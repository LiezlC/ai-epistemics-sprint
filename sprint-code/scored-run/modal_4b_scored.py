"""Qwen3.5-4B untuned and tuned, scored packets, on Modal (sprint code, 13 Nov 2026). Raw outputs only; no scoring.

Setup copied from the headroom pilot's modal_4b_pilot.py, which follows the preexisting training-trial/eval_modal.py (Liezl,
11 Nov 2026): vLLM 0.32.0, transformers 5.19.0, L40S, base Qwen/Qwen3.5-4B, greedy (temperature 0), thinking off, max 200 new
tokens, LoRA rank 16. Zero-shot for both arms. ONE container, hard timeout 1,800 s (the cost cap).

  ADAPTER_DIR=<folder with adapter_model.safetensors and adapter_config.json> PYTHONUTF8=1 .venv/Scripts/modal run \
      "plans/Epistemics Sprint/scored-run/modal_4b_scored.py" --out "plans/Epistemics Sprint/scored-run/runs/4b" \
      --packets-file packets_scored.jsonl [--limit N] [--arm both|base_zero|tuned_zero]
Use the SPRINT adapter (Liezl's checkpoint) for the tuned arm and name it in the run record; the trial adapter is prior work.
Outputs: scored_outputs_<arm>.jsonl (packet fields, raw answer, parsed verdict and roots) and run_record_4b.json.
"""
import hashlib
import json
import os
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
PILOT = HERE.parent / "pilot"
ADAPTER_DIR = os.environ.get("ADAPTER_DIR", ".")
BASE = "Qwen/Qwen3.5-4B"

app = modal.App("epistemics-4b-scored")
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
image = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
         .entrypoint([]).pip_install("vllm==0.32.0", "transformers==5.19.0")
         .env({"HF_HOME": "/hf-cache"})
         .add_local_dir(ADAPTER_DIR, "/adapter", ignore=["*.zst", "*.tar*"]))


@app.function(image=image, gpu="L40S", volumes={"/hf-cache": cache}, timeout=1800)
def run(prompts, arms):
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    llm = LLM(model=BASE, enable_lora=True, max_lora_rank=16, max_model_len=8192, seed=0)
    sp = SamplingParams(temperature=0, max_tokens=200)
    kw = {"chat_template_kwargs": {"enable_thinking": False}}
    lora = LoRARequest("sprint", 1, "/adapter")
    convs = [[{"role": "user", "content": p}] for p in prompts]
    out = {}
    for arm in arms:
        res = llm.chat(convs, sp, lora_request=lora if arm == "tuned_zero" else None, **kw)
        out[arm] = [r.outputs[0].text for r in res]
    return out


@app.local_entrypoint()
def main(out: str, packets_file: str = "packets_scored.jsonl", limit: int = 0, arm: str = "both"):
    import sys
    sys.path.insert(0, str(PILOT))
    from run_pilot import parse  # frozen parse rule, unchanged

    path = HERE / packets_file
    packets = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if limit:
        packets = packets[:limit]
    arms = ["base_zero", "tuned_zero"] if arm == "both" else [arm]
    res = run.remote([p["prompt"] for p in packets], arms)
    od = pathlib.Path(out)
    od.mkdir(parents=True, exist_ok=True)
    for a in arms:
        n_unp = 0
        with open(od / f"scored_outputs_{a}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for p, text in zip(packets, res[a]):
                parsed = parse(text)
                n_unp += parsed is None
                r = {k: p[k] for k in p if k != "prompt"}
                r.update({"arm": a, "answer": text, "parsed": parsed is not None,
                          "verdict": parsed[0] if parsed else None, "roots": parsed[1] if parsed else None})
                f.write(json.dumps(r) + "\n")
        print(a, len(packets), "packets,", n_unp, "unparseable")
    rec = {"base": BASE, "adapter_dir_name": os.path.basename(ADAPTER_DIR.rstrip("/\\")), "arms": arms, "packets_file": packets_file,
           "packets_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(), "limit": limit,
           "decoding": "greedy temperature 0, thinking off, max 200 new tokens, vLLM 0.32.0, L40S, seed 0"}
    (od / "run_record_4b.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("wrote", od)
