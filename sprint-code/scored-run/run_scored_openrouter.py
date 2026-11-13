"""Run the scored packets on one OpenRouter model (sprint code, 13 Nov 2026). Writes raw outputs only: NO scoring here.

Reuses run_pilot.run (frozen, imported unchanged) and the preexisting providers.py through pilot_providers.
Settings are the frozen ones: temperature 0, seed 20261113, thinking off, max 200 tokens, parse = first JSON object.
Local run:  python -I run_scored_openrouter.py --packets packets_scored.jsonl --model qwen/qwen3.8-27b --out RUN_DIR
The key comes from OPENROUTER_API_KEY (use modal_scored.py to keep it in the Modal secret instead).
Prints only counts: the verdict distribution per arm and the cost. Scoring needs the answer key: score_scored.py.
"""
import argparse
import asyncio
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pilot"))
import run_pilot as rp  # noqa: E402  (frozen, unchanged)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--packets", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--route", default="openrouter_chat")
    ap.add_argument("--spend-cap", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--thinking", default="off", choices=["off", "default"])
    ap.add_argument("--seed", type=int, default=20261113)
    a = ap.parse_args(argv)
    packets = [json.loads(l) for l in open(a.packets, encoding="utf-8") if l.strip()]
    if a.limit:
        packets = packets[:a.limit]
    prov, results = asyncio.run(rp.run(a, packets))
    summary = {"model": a.model, "route": a.route, "thinking": a.thinking, "seed": a.seed, "temperature": 0,
               "packets_sha256": hashlib.sha256(open(a.packets, "rb").read()).hexdigest(),
               "calls": prov.calls, "spend_usd": round(prov.spend, 5),
               "errors": sum(1 for x in results if x.get("error")),
               "unparseable": sum(1 for x in results if not x.get("error") and not x.get("parsed")),
               "reasoning_tokens_total": sum(x.get("reasoning_tokens") or 0 for x in results),
               "models_served": sorted({x["model_served"] for x in results if x.get("model_served")})}
    json.dump(summary, open(os.path.join(a.out, "run_summary.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary, indent=1))
    dist = {}
    for x in results:
        dist.setdefault((x["instruction"], x["label_form"]), Counter())[x.get("verdict") or "unparseable_or_error"] += 1
    for k, v in sorted(dist.items()):
        print(f"{k[0]:8} {k[1]:10} {dict(v)}")


if __name__ == "__main__":
    main()
