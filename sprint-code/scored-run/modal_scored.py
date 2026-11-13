"""Modal entry point: scored run on an OpenRouter model, key kept in the Modal secret `openrouter` (sprint code, 13 Nov 2026).

Pattern follows the headroom pilot's modal_pilot.py (itself following the preexisting con-artist/modal_app.py). The preexisting
con-artist/providers.py is shipped UNCHANGED. Raw outputs only; no scoring. Outputs go to the Volume `epistemics-pilot-runs`.

  SCORED_PACKETS=packets_scored.jsonl PYTHONUTF8=1 .venv/Scripts/modal run \
      "plans/Epistemics Sprint/scored-run/modal_scored.py::scored" --model qwen/qwen3.8-27b --cell scored27b --spend-cap 1.0
  PYTHONUTF8=1 .venv/Scripts/modal volume get epistemics-pilot-runs scored27b "plans/Epistemics Sprint/scored-run/runs/"
SCORED_PACKETS is a file name inside this folder (default packets_scored.jsonl). Add --limit N for a small test.
"""
from __future__ import annotations

import os
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent / "pilot"
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE  # repo root on the laptop; inside the container this is not used
PROVIDERS = ROOT / "con-artist" / "providers.py"
if not PROVIDERS.exists():  # team-repo layout: sprint-code/scored-run -> sprint-code/preexisting/con-artist
    PROVIDERS = HERE.parent / "preexisting" / "con-artist" / "providers.py"

app = modal.App("epistemics-scored")
vol = modal.Volume.from_name("epistemics-pilot-runs", create_if_missing=True)
image = (modal.Image.debian_slim(python_version="3.12").pip_install("httpx==0.28.1")
         .add_local_file(str(PROVIDERS), "/root/con-artist/providers.py")  # preexisting, unchanged
         .add_local_file(str(PILOT / "pilot_providers.py"), "/root/pilot/pilot_providers.py")
         .add_local_file(str(PILOT / "run_pilot.py"), "/root/pilot/run_pilot.py")
         .add_local_file(str(HERE / "run_scored_openrouter.py"), "/root/scored-run/run_scored_openrouter.py")
         .add_local_file(str(HERE / os.environ.get("SCORED_PACKETS", "packets_scored.jsonl")), "/root/scored-run/packets_scored.jsonl"))


@app.function(image=image, secrets=[modal.Secret.from_name("openrouter")], volumes={"/runs": vol}, timeout=60 * 60)
def run(model: str, cell: str, spend_cap: float, limit: int = 0, thinking: str = "off") -> int:
    import sys

    os.environ["CON_ARTIST_DIR"] = "/root/con-artist"
    sys.path.insert(0, "/root/scored-run")
    import run_scored_openrouter as r

    argv = ["--packets", "/root/scored-run/packets_scored.jsonl", "--model", model, "--out", f"/runs/{cell}",
            "--spend-cap", str(spend_cap), "--thinking", thinking]
    if limit:
        argv += ["--limit", str(limit)]
    r.main(argv)
    vol.commit()
    return 0


@app.local_entrypoint()
def scored(model: str, cell: str, spend_cap: float = 1.0, limit: int = 0, thinking: str = "off"):
    run.remote(model, cell, spend_cap, limit, thinking)
