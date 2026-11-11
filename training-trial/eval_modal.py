"""Test A comparison on Modal: untuned Qwen3.5-4B (zero-shot and 3-shot) vs the trial LoRA (zero-shot).

Run:  python -m modal run eval_modal.py
Writes results/test_a_outputs.jsonl next to this file. Greedy decoding, thinking off.
"""
import json
import pathlib
import modal

HERE = pathlib.Path(__file__).parent
BASE = "Qwen/Qwen3.5-4B"

app = modal.App("epistemics-trial-eval")
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
image = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
         .entrypoint([]).pip_install("vllm==0.32.0", "transformers==5.19.0")
         .env({"HF_HOME": "/hf-cache"})
         .add_local_dir(str(HERE / "checkpoint"), "/adapter", ignore=["*.zst"]))


@app.function(image=image, gpu="L40S", volumes={"/hf-cache": cache}, timeout=3600)
def run(cases, shots):
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    llm = LLM(model=BASE, enable_lora=True, max_lora_rank=16, max_model_len=8192, seed=0)
    sp = SamplingParams(temperature=0, max_tokens=200)
    kw = {"chat_template_kwargs": {"enable_thinking": False}}
    few = []
    for s in shots:
        few += [{"role": "user", "content": s["prompt"]}, {"role": "assistant", "content": s["completion"]}]
    convs = {
        "base_zero": [[{"role": "user", "content": c["prompt"]}] for c in cases],
        "base_3shot": [few + [{"role": "user", "content": c["prompt"]}] for c in cases],
        "tuned_zero": [[{"role": "user", "content": c["prompt"]}] for c in cases],
    }
    lora = LoRARequest("trial", 1, "/adapter")
    out = {}
    for name, cv in convs.items():
        res = llm.chat(cv, sp, lora_request=lora if name.startswith("tuned") else None, **kw)
        out[name] = [r.outputs[0].text for r in res]
    return out


@app.local_entrypoint()
def main():
    data = HERE / "data"
    cases = [json.loads(l) for l in open(data / "test_a.jsonl", encoding="utf-8")]
    meta = [json.loads(l) for l in open(data / "train_meta.jsonl", encoding="utf-8")]
    # One worked example per verdict, from training cases (never from Test A).
    shots = []
    for want in ("independent", "shared", "undetermined"):
        m = next(x for x in meta if x["meta"]["truth"] == want and x["meta"]["condition"] != "label_only")
        shots.append({"prompt": m["prompt"], "completion": m["completion"]})
    out = run.remote(cases, shots)
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "test_a_outputs.jsonl", "w", encoding="utf-8") as f:
        for i, c in enumerate(cases):
            f.write(json.dumps({"idx": i, "gold": json.loads(c["completion"]),
                                **{k: v[i] for k, v in out.items()}}) + "\n")
    print("wrote", len(cases), "rows")
