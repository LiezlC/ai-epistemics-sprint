"""Qwen3.5-4B positive control and pilot on Modal (sprint code, written 13 Nov 2026). Run on 13 Nov: positive control reproduced and pilots done.

PREEXISTING CODE REUSED: the model, the vLLM setup, the Modal image and the arm definitions follow
`training-trial/eval_modal.py` (Liezl, 11 Nov 2026; vLLM 0.32.0, transformers 5.19.0, L40S, greedy, thinking off,
base `Qwen/Qwen3.5-4B`, LoRA rank 16). Her file is read, not edited. The trial's scorer `score_test_a.py` can be run
unchanged on the Test A outputs this script writes (same row format). What is new here: the pilot packets are run
through the same two arms, and everything happens in one container so the model loads once.

ONE container, ONE function call, hard timeout 1,800 s: the cost cap is that timeout (an L40S for at most 30 minutes;
Modal's per-second price is not checked here). No metering of the account balance is available.

Run (after the adapter has been downloaded and checked; see the session):
  ADAPTER_DIR=<folder with adapter_model.safetensors and adapter_config.json> PYTHONUTF8=1 .venv/Scripts/modal run \
      "plans/Epistemics Sprint/pilot/modal_4b_pilot.py" --out "plans/Epistemics Sprint/pilot/runs/4b"
Outputs: test_a_outputs.jsonl (positive control, trial row format), pilot_outputs.jsonl, summary_4b.txt.
"""
import json
import os
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
TRIAL_DATA = HERE.parent / "ai-epistemics-sprint" / "training-trial" / "data"
ADAPTER_DIR = os.environ.get("ADAPTER_DIR", ".")
BASE = "Qwen/Qwen3.5-4B"

app = modal.App("epistemics-4b-pilot")
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
image = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
         .entrypoint([]).pip_install("vllm==0.32.0", "transformers==5.19.0")
         .env({"HF_HOME": "/hf-cache"})
         .add_local_dir(ADAPTER_DIR, "/adapter", ignore=["*.zst", "*.tar*"]))


@app.function(image=image, gpu="L40S", volumes={"/hf-cache": cache}, timeout=1800)
def run(control_cases, shots, pilot_packets):
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    llm = LLM(model=BASE, enable_lora=True, max_lora_rank=16, max_model_len=8192, seed=0)
    sp = SamplingParams(temperature=0, max_tokens=200)
    kw = {"chat_template_kwargs": {"enable_thinking": False}}
    lora = LoRARequest("trial", 1, "/adapter")
    few = []
    for s in shots:
        few += [{"role": "user", "content": s["prompt"]}, {"role": "assistant", "content": s["completion"]}]

    def gen(convs, tuned):
        res = llm.chat(convs, sp, lora_request=lora if tuned else None, **kw)
        return [r.outputs[0].text for r in res]

    out = {"control": {}, "pilot": {}}
    if control_cases:  # skipped in the v2 re-run (the positive control was reproduced in the first run)
        zero = [[{"role": "user", "content": c["prompt"]}] for c in control_cases]
        out["control"]["base_zero"] = gen(zero, False)
        out["control"]["base_3shot"] = gen([few + z for z in zero], False)
        out["control"]["tuned_zero"] = gen(zero, True)
    pz = [[{"role": "user", "content": p["prompt"]}] for p in pilot_packets]
    out["pilot"]["base_zero"] = gen(pz, False)
    out["pilot"]["tuned_zero"] = gen(pz, True)
    return out


@app.local_entrypoint()
def main(out: str, packets_file: str = "pilot_packets.jsonl", skip_control: bool = False):
    import sys
    sys.path.insert(0, str(HERE))
    from run_pilot import parse, summarise  # sprint code; imports the preexisting providers.py unchanged

    cases = [json.loads(l) for l in open(TRIAL_DATA / "test_a.jsonl", encoding="utf-8")]
    meta = [json.loads(l) for l in open(TRIAL_DATA / "train_meta.jsonl", encoding="utf-8")]
    shots = []
    for want in ("independent", "shared", "undetermined"):  # as in the trial: one per verdict, from training, never Test A
        m = next(x for x in meta if x["meta"]["truth"] == want and x["meta"]["condition"] != "label_only")
        shots.append({"prompt": m["prompt"], "completion": m["completion"]})
    packets = [json.loads(l) for l in open(HERE / packets_file, encoding="utf-8")]
    if skip_control:
        cases, shots = [], []

    res = run.remote(cases, shots, packets)

    od = pathlib.Path(out)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "test_a_outputs.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for i, c in enumerate(cases):
            f.write(json.dumps({"idx": i, "gold": json.loads(c["completion"]),
                                **{k: v[i] for k, v in res["control"].items()}}) + "\n")
    lines = []
    for arm in ("base_zero", "tuned_zero"):
        rows = []
        for p, text in zip(packets, res["pilot"][arm]):
            parsed = parse(text)
            r = {k: p[k] for k in p if k != "prompt"}
            r.update({"arm": arm, "answer": text, "parsed": parsed is not None,
                      "verdict": parsed[0] if parsed else None, "roots": parsed[1] if parsed else None})
            rows.append(r)
        with open(od / f"pilot_outputs_{arm}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        g = summarise(rows)
        lines.append(f"== {arm} ({len(rows)} packets)")
        lines.append(f"{'instruction':9} {'condition/direction':18} {'label':10} {'n':>3} {'right':>5} {'follow':>6} {'undet':>5} {'unpars':>6}")
        for k, v in sorted(g.items()):
            lines.append(f"{k[0]:9} {k[1]:18} {k[2]:10} {v['n']:>3} {v.get('correct', 0):>5} {v.get('follows_label', 0):>6} "
                         f"{v.get('undetermined', 0):>5} {v.get('unparseable', 0):>6}")
    (od / "summary_4b.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("wrote", od)
