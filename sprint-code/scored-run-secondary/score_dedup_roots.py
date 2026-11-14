"""SECONDARY analysis, not the primary figure: score with duplicate root ids removed (sprint code, 14 Nov 2026).

Why: some 4B outputs list the same root record twice (for example ["G-52", "G-52"]). The frozen scorer
(score_scored.py, 13 Nov) compares sorted root lists without removing duplicates, so such a row cannot count as
"verdict and roots right" even if the root is correct. The primary result is the frozen scorer as it is.
This script only removes repeated ids inside each row's "roots" list (keeping order), writes the changed rows to a
new file next to the output you name, and then calls the frozen scorer's main() on that file. It never edits the
raw outputs and does not change the scorer.

Usage: python -I score_dedup_roots.py --key KEY.json --results RESULTS.jsonl [--results MORE.jsonl ...] --label NAME --out DIR
Reads no key until you run it; do not run it before the key is released. Report its table as "secondary: duplicate roots removed".
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = os.path.join(HERE, "..", "scored-run", "score_scored.py")


def dedupe(roots):
    seen, out = set(), []
    for r in roots or []:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--results", action="append", required=True)
    ap.add_argument("--label", default="run")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    spec = importlib.util.spec_from_file_location("score_scored", SCORER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    new_paths, changed, total = [], 0, 0
    for p in a.results:
        dst = os.path.join(a.out, "dedup_" + os.path.basename(p))
        with open(p, encoding="utf-8") as f, open(dst, "w", encoding="utf-8", newline="\n") as g:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                total += 1
                if r.get("roots"):
                    d = dedupe(r["roots"])
                    if d != r["roots"]:
                        changed += 1
                        r["roots"] = d
                g.write(json.dumps(r, ensure_ascii=False) + "\n")
        new_paths.append(dst)
    print("SECONDARY: duplicate roots removed |", changed, "of", total, "rows changed")
    argv = ["--key", a.key, "--label", a.label + " (secondary, duplicate roots removed)"]
    for p in new_paths:
        argv += ["--results", p]
    mod.main(argv)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        assert dedupe(["G-52", "G-52"]) == ["G-52"]
        assert dedupe(["A-1", "B-2", "A-1"]) == ["A-1", "B-2"]
        assert dedupe([]) == [] and dedupe(None) == []
        print("selftest ok")
    else:
        main()
