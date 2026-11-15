"""Write per-item, text-free observations for the 15-case first-turn runs (15 Nov 2026).
One row per model and prompt: case id, arm, label form, label shown, the key's verdict, the model's verdict and cited roots,
whether each is right, and the sha256 of the exact prompt sent. No packet text is written.
Reads the released key, the four first-turn output files and the frozen packets file; writes variants/joined-15/observations.csv.
Usage: python -I make_observations.py
"""
import csv
import hashlib
import json
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
J = os.path.join(BASE, "variants", "joined-15")
KEY = json.load(open(os.path.join(BASE, "key", "answer-key.json"), encoding="utf-8"))
RUNS = {
    "27b": os.path.join(J, "runs", "scored27b", "results.jsonl"),
    "4B zero-shot": os.path.join(J, "runs", "4b_untuned", "scored_outputs_base_zero.jsonl"),
    "4B three-shot": os.path.join(J, "runs", "4b_3shot", "scored_outputs_base_3shot.jsonl"),
    "4B tuned (v2)": os.path.join(J, "runs", "4b_tuned_v2", "scored_outputs_tuned_zero.jsonl"),
}
PK = {}
for line in open(os.path.join(J, "packets_scored.jsonl"), encoding="utf-8"):
    if line.strip():
        p = json.loads(line)
        PK[p["id"]] = hashlib.sha256(p["prompt"].encode("utf-8")).hexdigest()
out = os.path.join(J, "observations.csv")
n = 0
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["model", "row_id", "case", "instruction", "label_form", "label_shown", "key_verdict", "verdict",
                "roots_cited", "verdict_right", "roots_right_exact", "verdict_and_roots_right", "parsed", "prompt_sha256"])
    for model, path in RUNS.items():
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            k = KEY[r["case"]]
            roots = r.get("roots") or []
            w.writerow([model, r["id"], r["case"], r["instruction"], r["label_form"], r.get("label") or "",
                        k["verdict"], r.get("verdict") or "", ";".join(roots),
                        int(r.get("verdict") == k["verdict"]),
                        int(sorted(roots) == sorted(k["root_records"])),
                        int(r.get("verdict") == k["verdict"] and sorted(roots) == sorted(k["root_records"])), int(bool(r.get("parsed"))),
                        PK.get(r["id"], "")])
            n += 1
print("wrote", out, n, "rows")
