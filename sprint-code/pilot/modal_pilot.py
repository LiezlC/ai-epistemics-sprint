"""Modal entry points for the Epistemics pilot (sprint code, written 13 Nov 2026). NOT YET RUN: it spends money,
so it waits for the user's approval.

Pattern follows the preexisting `con-artist/modal_app.py` (Swarm sprint work, 6 Nov 2026): keys stay in the Modal
Secret `openrouter` referenced by name; run outputs go to a Volume; nothing is read from the laptop except the files
listed in the image below. The preexisting `con-artist/providers.py` is shipped UNCHANGED.

  PYTHONUTF8=1 .venv/Scripts/modal run "plans/Epistemics Sprint/pilot/modal_pilot.py::smoke" --model qwen/qwen3.8-max-0902
  PYTHONUTF8=1 .venv/Scripts/modal run "plans/Epistemics Sprint/pilot/modal_pilot.py::pilot" --model qwen/qwen3.8-max-0902 --cell max1 --spend-cap 1.5
  PYTHONUTF8=1 .venv/Scripts/modal volume get epistemics-pilot-runs max1 "plans/Epistemics Sprint/pilot/runs/"
"""
from __future__ import annotations

from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent          # plans/Epistemics Sprint/pilot
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE  # repo root (inside the container the file sits at /root, so fall back)
REMOTE = "/root/pilot"

app = modal.App("epistemics-pilot")
vol = modal.Volume.from_name("epistemics-pilot-runs", create_if_missing=True)
image = (modal.Image.debian_slim(python_version="3.12").pip_install("httpx==0.28.1")
         .add_local_file(str(ROOT / "con-artist/providers.py"), f"{REMOTE}/con-artist/providers.py")  # preexisting, unchanged
         .add_local_file(str(HERE / "pilot_providers.py"), f"{REMOTE}/pilot_providers.py")
         .add_local_file(str(HERE / "run_pilot.py"), f"{REMOTE}/run_pilot.py")
         # PILOT_PACKETS (env var, local side) picks the packets file; default is the first pilot's set (added for the v2 re-run)
         .add_local_file(str(HERE / __import__("os").environ.get("PILOT_PACKETS", "pilot_packets.jsonl")), f"{REMOTE}/pilot_packets.jsonl"))


@app.function(image=image, secrets=[modal.Secret.from_name("openrouter")], volumes={"/runs": vol}, timeout=60 * 60)
def run(model: str, cell: str, spend_cap: float, limit: int = 0, thinking: str = "off") -> int:
    import os
    import sys

    os.environ["CON_ARTIST_DIR"] = f"{REMOTE}/con-artist"
    sys.path.insert(0, REMOTE)
    import run_pilot

    argv = ["run_pilot.py", "--packets", f"{REMOTE}/pilot_packets.jsonl", "--model", model, "--out", f"/runs/{cell}",
            "--spend-cap", str(spend_cap), "--thinking", thinking]
    if limit:
        argv += ["--limit", str(limit)]
    sys.argv = argv
    run_pilot.main()
    vol.commit()
    return 0


@app.local_entrypoint()
def smoke(model: str):
    """Five real calls, hard cap USD 0.05: checks the key, the model id, thinking off and the parse."""
    run.remote(model, "smoke", 0.05, 5)


@app.local_entrypoint()
def pilot(model: str, cell: str, spend_cap: float = 1.0, thinking: str = "off"):
    run.remote(model, cell, spend_cap, 0, thinking)
