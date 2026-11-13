"""Modal entry points for the SECOND TURN (sprint code, 13 Nov 2026). Raw outputs only; no scoring.

(1) 27b via OpenRouter, key in the Modal secret `openrouter`; the preexisting providers.py is shipped UNCHANGED.
  SECOND_TURN_ROWS=second_turn_rows.jsonl PYTHONUTF8=1 .venv/Scripts/modal run \
      "plans/Epistemics Sprint/scored-run/modal_second_turn.py::second27b" --model qwen/qwen3.8-27b --arm 27b --cell second27b
  PYTHONUTF8=1 .venv/Scripts/modal volume get epistemics-pilot-runs second27b "plans/Epistemics Sprint/scored-run/runs/"   (runs/ must exist)
(2) Qwen3.5-4B (untuned, or with the adapter) on one L40S container, hard timeout 1,800 s; same settings as modal_4b_scored.py:
  ADAPTER_DIR=<adapter folder> PYTHONUTF8=1 .venv/Scripts/modal run "plans/Epistemics Sprint/scored-run/modal_second_turn.py::second4b" \
      --out "plans/Epistemics Sprint/scored-run/runs/second4b" --arm 4b_base [--tuned]
Rows come from build_second_turn.py; each row carries its model's own first answer, so run each arm on its own rows.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

import modal

HERE = pathlib.Path(__file__).resolve().parent
PILOT = HERE.parent / "pilot"
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE
PROVIDERS = ROOT / "con-artist" / "providers.py"
if not PROVIDERS.exists():  # team-repo layout
    PROVIDERS = HERE.parent / "preexisting" / "con-artist" / "providers.py"
ROWS = os.environ.get("SECOND_TURN_ROWS", "second_turn_rows.jsonl")
ADAPTER_DIR = os.environ.get("ADAPTER_DIR", ".")
BASE = "Qwen/Qwen3.5-4B"

# ---- (1) 27b via OpenRouter
app = modal.App("epistemics-second-turn")
vol = modal.Volume.from_name("epistemics-pilot-runs", create_if_missing=True)
img27 = (modal.Image.debian_slim(python_version="3.12").pip_install("httpx==0.28.1")
         .add_local_file(str(PROVIDERS), "/root/con-artist/providers.py")  # preexisting, unchanged
         .add_local_file(str(PILOT / "pilot_providers.py"), "/root/pilot/pilot_providers.py")
         .add_local_file(str(PILOT / "run_pilot.py"), "/root/pilot/run_pilot.py")
         .add_local_file(str(HERE / "run_second_turn_openrouter.py"), "/root/scored-run/run_second_turn_openrouter.py")
         .add_local_file(str(HERE / ROWS), "/root/scored-run/second_turn_rows.jsonl"))


@app.function(image=img27, secrets=[modal.Secret.from_name("openrouter")], volumes={"/runs": vol}, timeout=60 * 60)
def run27(model: str, arm: str, cell: str, spend_cap: float) -> int:
    os.environ["CON_ARTIST_DIR"] = "/root/con-artist"
    sys.path.insert(0, "/root/scored-run")
    import run_second_turn_openrouter as r

    r.main(["--rows", "/root/scored-run/second_turn_rows.jsonl", "--arm", arm, "--model", model, "--out", f"/runs/{cell}",
            "--spend-cap", str(spend_cap)])
    vol.commit()
    return 0


@app.local_entrypoint()
def second27b(model: str, arm: str, cell: str, spend_cap: float = 1.0):
    run27.remote(model, arm, cell, spend_cap)


# ---- (2) Qwen3.5-4B on Modal
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
img4 = (modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
        .entrypoint([]).pip_install("vllm==0.32.0", "transformers==5.19.0").env({"HF_HOME": "/hf-cache"})
        .add_local_dir(ADAPTER_DIR, "/adapter", ignore=["*.zst", "*.tar*"]))
app4 = modal.App("epistemics-second-turn-4b")


@app4.function(image=img4, gpu="L40S", volumes={"/hf-cache": cache}, timeout=1800)
def run4(convs, tuned):
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    llm = LLM(model=BASE, enable_lora=True, max_lora_rank=16, max_model_len=8192, seed=0)
    sp = SamplingParams(temperature=0, max_tokens=200)
    res = llm.chat(convs, sp, lora_request=LoRARequest("sprint", 1, "/adapter") if tuned else None,
                   chat_template_kwargs={"enable_thinking": False})
    return [r.outputs[0].text for r in res]


@app4.local_entrypoint()
def second4b(out: str, arm: str, tuned: bool = False):
    sys.path.insert(0, str(PILOT))
    from run_pilot import parse  # frozen parse rule, unchanged

    path = HERE / ROWS
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r["first_arm"] == arm]
    texts = run4.remote([r["messages"] for r in rows], tuned)
    od = pathlib.Path(out)
    od.mkdir(parents=True, exist_ok=True)
    n_unp = 0
    with open(od / "second_turn_results.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r, t in zip(rows, texts):
            p = parse(t)
            n_unp += p is None
            meta = {k: r[k] for k in r if k != "messages"}
            meta.update({"answer2": t, "parsed": p is not None, "verdict": p[0] if p else None, "roots": p[1] if p else None})
            f.write(json.dumps(meta) + "\n")
    (od / "run_record_second_4b.json").write_text(json.dumps({
        "base": BASE, "arm": arm, "tuned": tuned, "adapter_dir_name": os.path.basename(ADAPTER_DIR.rstrip("/\\")),
        "rows_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(), "rows_run": len(rows),
        "decoding": "greedy temperature 0, thinking off, max 200 new tokens, vLLM 0.32.0, L40S, seed 0"}, indent=1), encoding="utf-8")
    print(arm, len(rows), "rows,", n_unp, "unparseable; wrote", od)
