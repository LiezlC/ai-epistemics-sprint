"""Concatenate the original 1,000-case sprint set and an extra batch into one larger set (sprint code, 13 Nov 2026).

The first block is kept byte-for-byte (it is the set Liezl is spot-checking); the extra batch is appended. The meta
file is re-indexed so idx runs 0..N-1. Nothing is shuffled or edited.

Usage: python -I combine_sets.py FIRST_DIR EXTRA_DIR OUT_DIR
Each directory holds train_dpo.jsonl, train_sft.jsonl, train_meta.jsonl (from gen_sprint_cases.py).
"""
import json
import os
import sys

first, extra, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
for name in ("train_dpo.jsonl", "train_sft.jsonl"):
    with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
        for d in (first, extra):
            for line in open(os.path.join(d, name), encoding="utf-8"):
                f.write(line if line.endswith("\n") else line + "\n")
n = 0
with open(os.path.join(out, "train_meta.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    for d in (first, extra):
        for line in open(os.path.join(d, "train_meta.jsonl"), encoding="utf-8"):
            row = json.loads(line)
            row["idx"] = n
            f.write(json.dumps(row) + "\n")
            n += 1
print("combined rows:", n)
