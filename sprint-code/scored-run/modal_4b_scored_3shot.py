"""Qwen3.5-4B UNTUNED, three-shot comparison arm, scored packets, on Modal (sprint code, 13 Nov 2026). Raw outputs only.

Same setup as modal_4b_scored.py (itself following the preexisting training-trial/eval_modal.py): vLLM 0.32.0, L40S, base
Qwen/Qwen3.5-4B, greedy, thinking off, max 200 new tokens, one container, hard timeout 1,800 s. The three worked examples come
from the frozen examples file (make_fewshot_examples.py) and are sent as earlier chat turns, as the trial did. They carry the
ALERTED instruction text, so only alerted-instruction packets are run (the neutral rows are skipped and counted).
No adapter: this is an untuned arm.

  PYTHONUTF8=1 .venv/Scripts/modal run "plans/Epistemics Sprint/scored-run/modal_4b_scored_3shot.py" \
      --out "plans/Epistemics Sprint/scored-run/runs/4b_3shot" --packets-file packets_scored.jsonl \
      --examples-file ../freeze-drafts/fewshot_examples_3shot.json [--limit N]
Outputs: scored_outputs_base_3shot.jsonl and run_record_4b_3shot.json.
"""
import hashlib
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
PILOT = HERE.parent / "pilot"
BASE = "Qwen/Qwen3.5-4B"

app = modal.App("epistemics-4b-3shot")
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
image = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
         .entrypoint([]).pip_install("vllm==0.32.0", "transformers==5.19.0")
         .env({"HF_HOME": "/hf-cache"}))


def build_convs(shots, prompts):
    """Each conversation = the worked examples as user/assistant turns, then the packet prompt as the last user turn."""
    few = []
    for s in shots:
        few += [{"role": "user", "content": s["prompt"]}, {"role": "assistant", "content": s["completion"]}]
    return [few + [{"role": "user", "content": p}] for p in prompts]


@app.function(image=image, gpu="L40S", volumes={"/hf-cache": cache}, timeout=1800)
def run(shots, prompts):
    from vllm import LLM, SamplingParams

    llm = LLM(model=BASE, max_model_len=8192, seed=0)
    sp = SamplingParams(temperature=0, max_tokens=200)
    res = llm.chat(build_convs(shots, prompts), sp, chat_template_kwargs={"enable_thinking": False})
    return [r.outputs[0].text for r in res]


@app.local_entrypoint()
def main(out: str, packets_file: str = "packets_scored.jsonl", examples_file: str = "../freeze-drafts/fewshot_examples_3shot.json",
         limit: int = 0):
    import sys
    sys.path.insert(0, str(PILOT))
    from run_pilot import parse  # frozen parse rule, unchanged

    path = HERE / packets_file
    ex_path = (HERE / examples_file).resolve()
    shots = json.load(open(ex_path, encoding="utf-8"))["shots"]
    packets = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    skipped = sum(1 for p in packets if p["instruction"] != "alerted")
    packets = [p for p in packets if p["instruction"] == "alerted"]
    if limit:
        packets = packets[:limit]
    texts = run.remote(shots, [p["prompt"] for p in packets])
    od = pathlib.Path(out)
    od.mkdir(parents=True, exist_ok=True)
    n_unp = 0
    with open(od / "scored_outputs_base_3shot.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for p, text in zip(packets, texts):
            parsed = parse(text)
            n_unp += parsed is None
            r = {k: p[k] for k in p if k != "prompt"}
            r.update({"arm": "base_3shot", "answer": text, "parsed": parsed is not None,
                      "verdict": parsed[0] if parsed else None, "roots": parsed[1] if parsed else None})
            f.write(json.dumps(r) + "\n")
    rec = {"base": BASE, "arm": "base_3shot", "packets_file": packets_file, "packets_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
           "examples_sha256": hashlib.sha256(open(ex_path, "rb").read()).hexdigest(), "examples_train_rows": [s["train_row"] for s in shots],
           "rows_run": len(packets), "neutral_rows_skipped": skipped, "limit": limit,
           "decoding": "greedy temperature 0, thinking off, max 200 new tokens, vLLM 0.32.0, L40S, seed 0"}
    (od / "run_record_4b_3shot.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("base_3shot", len(packets), "packets,", n_unp, "unparseable;", skipped, "neutral rows skipped; wrote", od)
