"""Training loop: one pilot round on Modal: DPO with LoRA on Qwen/Qwen3.5-4B (TRL), then dev-set evaluation (15 Nov 2026).

Train: settings matched to Adaption v1 where possible: LoRA r16, alpha 32, dropout 0, q/k/v/o/gate/up/down projections of
the language model; lr 1e-5 cosine, beta 0.1 (sigmoid DPO loss), 1 epoch; effective batch 8 (4 x 2 accumulation);
bf16; max length 1,536 tokens. Prompts are rendered with the model's chat template, generation prompt on, thinking off
(the same rendering vLLM uses at eval). One L40S, hard timeout 2,400 s. The adapter is saved to the Modal volume
"loop-adapters" under the round name, with keys named as the Adaption adapter names them (model.language_model.layers).
Eval: the repo's vLLM path, copied from sprint-code/scored-run/modal_4b_scored.py: vLLM 0.32.0, transformers 5.19.0, L40S,
greedy temperature 0, thinking off, max 200 new tokens, seed 0, frozen alerted prompt (already inside packets_dev.jsonl).
Parse = the frozen first-JSON-object rule (sprint-code/pilot/run_pilot.parse, imported unchanged).

  CON_ARTIST_DIR=<repo>/sprint-code/preexisting/con-artist PYTHONUTF8=1 <python>/Scripts/modal.exe run loop/pilot_modal.py \
      --round r0 [--base] [--eval-only | --train-only]
Reads rounds/<round>/pairs.jsonl and dev/packets_dev.jsonl. Writes rounds/<round>/dev_outputs_<arm>.jsonl,
rounds/<round>/train_log.json and rounds/<round>/run_record.json; the adapter is downloaded to rounds/<round>/adapter/.
"""
import hashlib
import json
import os
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
BASE = "Qwen/Qwen3.5-4B"
TRAIN_TIMEOUT, EVAL_TIMEOUT = 2400, 1200

app = modal.App("epistemics-loop-pilot")
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
adapters = modal.Volume.from_name("loop-adapters", create_if_missing=True)
train_image = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
               .entrypoint([]).pip_install("torch==2.9.0", "transformers==5.19.0", "trl", "peft", "accelerate",
                                           "datasets", "flash-linear-attention")
               .env({"HF_HOME": "/hf-cache"}))
eval_image = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
              .entrypoint([]).pip_install("vllm==0.32.0", "transformers==5.19.0")
              .env({"HF_HOME": "/hf-cache"}))


@app.function(image=train_image, gpu="L40S", volumes={"/hf-cache": cache, "/adapters": adapters}, timeout=TRAIN_TIMEOUT)
def train(round_name, rows, seed=0):
    import importlib.metadata as md

    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from safetensors.torch import load_file, save_file
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOConfig, DPOTrainer

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)

    def render(p):
        return tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)

    ds = Dataset.from_list([{"prompt": render(r["prompt"]), "chosen": r["chosen"], "rejected": r["rejected"]}
                            for r in rows])
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16)
    lcfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                      exclude_modules=r".*visual.*")
    out = f"/adapters/{round_name}"
    cfg = DPOConfig(output_dir="/tmp/dpo", beta=0.1, learning_rate=1e-5, lr_scheduler_type="cosine", num_train_epochs=1,
                    per_device_train_batch_size=4, gradient_accumulation_steps=2, bf16=True, max_length=1536,
                    gradient_checkpointing=True, logging_steps=5, save_strategy="no", report_to="none", seed=seed)
    tr = DPOTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok, peft_config=lcfg)
    sample = tr.train_dataset[0]
    res = tr.train()
    tr.model.save_pretrained(out)
    # name keys as the Adaption adapter does, so vLLM loads it like the release adapter
    st = os.path.join(out, "adapter_model.safetensors")
    w = load_file(st)
    w2 = {k.replace("base_model.model.model.layers.", "base_model.model.model.language_model.layers."): v
          for k, v in w.items()}
    save_file(w2, st)
    adapters.commit()
    vers = {p: md.version(p) for p in ("torch", "transformers", "trl", "peft", "accelerate", "datasets")}
    return {"log_history": tr.state.log_history, "train_runtime_s": round(time.time() - t0, 1),
            "train_metrics": res.metrics, "versions": vers, "n_keys": len(w2), "keys_sample": sorted(w2)[:4],
            "sample_chosen_ids_tail": [int(x) for x in sample.get("chosen_input_ids", [])[-4:]],
            "eos_id": tok.eos_token_id}


@app.function(image=eval_image, gpu="L40S", volumes={"/hf-cache": cache, "/adapters": adapters}, timeout=EVAL_TIMEOUT)
def evaluate(round_name, prompts, arms):
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    adapters.reload()
    llm = LLM(model=BASE, enable_lora=True, max_lora_rank=16, max_model_len=8192, seed=0)
    sp = SamplingParams(temperature=0, max_tokens=200)
    kw = {"chat_template_kwargs": {"enable_thinking": False}}
    convs = [[{"role": "user", "content": p}] for p in prompts]
    out = {}
    for arm in arms:
        lora = LoRARequest(round_name, 1, f"/adapters/{round_name}") if arm == "tuned" else None
        res = llm.chat(convs, sp, lora_request=lora, **kw)
        out[arm] = [r.outputs[0].text for r in res]
    return out


@app.function(image=eval_image, volumes={"/adapters": adapters}, timeout=300)
def fetch(round_name):
    d = pathlib.Path(f"/adapters/{round_name}")
    return {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()}


@app.local_entrypoint()
def main(round: str, base: bool = False, eval_only: bool = False, train_only: bool = False):
    import sys
    sys.path.insert(0, str(REPO / "sprint-code" / "pilot"))
    from run_pilot import parse  # frozen parse rule, unchanged

    rd = HERE / "rounds" / round
    pairs_path, dev_path = rd / "pairs.jsonl", HERE / "dev" / "packets_dev.jsonl"
    rows = [json.loads(l) for l in open(pairs_path, encoding="utf-8") if l.strip()]
    rp = rd / "run_record.json"
    rec = json.loads(rp.read_text(encoding="utf-8")) if eval_only and rp.exists() else {}
    rec.update({"round": round, "base": BASE, "pairs_sha256": hashlib.sha256(pairs_path.read_bytes()).hexdigest(),
                "n_pairs": len(rows)})
    if not eval_only:
        t = time.time()
        tl = train.remote(round, rows)
        rec["train_wall_s"] = round_s = round_(time.time() - t)
        (rd / "train_log.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
        rec.update({"train_runtime_s": tl["train_runtime_s"], "versions": tl["versions"]})
        print("trained in", round_s, "s")
        files = fetch.remote(round)
        (rd / "adapter").mkdir(exist_ok=True)
        for n, b in files.items():
            (rd / "adapter" / n).write_bytes(b)
        rec["adapter_sha256"] = {n: hashlib.sha256(b).hexdigest() for n, b in sorted(files.items())}
    if train_only:
        rp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print("train only; wrote", rp)
        return
    packets = [json.loads(l) for l in open(dev_path, encoding="utf-8") if l.strip()]
    rec.update({"dev_sha256": hashlib.sha256(dev_path.read_bytes()).hexdigest(), "n_dev_prompts": len(packets)})
    arms = (["base"] if base else []) + ["tuned"]
    t = time.time()
    res = evaluate.remote(round, [p["prompt"] for p in packets], arms)
    rec["eval_wall_s"] = round_(time.time() - t)
    for a in arms:
        n_unp = 0
        with open(rd / f"dev_outputs_{a}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for p, text in zip(packets, res[a]):
                parsed = parse(text)
                n_unp += parsed is None
                r = {k: p[k] for k in p if k != "prompt"}
                r.update({"arm": a, "answer": text, "parsed": parsed is not None,
                          "verdict": parsed[0] if parsed else None, "roots": parsed[1] if parsed else None})
                f.write(json.dumps(r) + "\n")
        print(a, len(packets), "prompts,", n_unp, "unparseable")
    rec["decoding"] = "greedy temperature 0, thinking off, max 200 new tokens, vLLM 0.32.0, L40S, seed 0"
    rp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("wrote", rd)


def round_(x):
    return round(x, 1) if isinstance(x, float) else x
