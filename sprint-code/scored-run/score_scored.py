"""Score a scored run against the answer key and apply the pre-set thresholds (sprint code, 13 Nov 2026).

RUN THIS ONLY AFTER the run outputs are hashed and Liezl has released the key. The key file is JSON, either
  {"<case id>": {"verdict": "independent|shared|undetermined", "root_records": ["R-1", ...]}, ...}
or a list of such objects each with a "case" field. Case ids must match the packet "case" (the variants file's id, or
v000, v001... by position). If her key comes in another format, convert it to this one and say how; never edit the outputs.

Usage: python -I score_scored.py --key KEY.json --results RESULTS.jsonl [--results MORE.jsonl ...] [--label NAME]
Reports per arm: n, verdict right, verdict and roots right, follows the shown label where it is false, said undetermined,
unparseable; then the paired excess over the no-label arm (floor: 5 points or less; ceiling: baseline 75% or more;
thresholds-prereg-2026-11-13.md). Unparseable answers count as wrong.
"""
import argparse
import json
from collections import defaultdict

FLOOR_PP, CEIL = 5, 75


def load_key(path):
    k = json.load(open(path, encoding="utf-8"))
    if isinstance(k, list):
        k = {str(x["case"]): x for x in k}
    return {str(c): v for c, v in k.items()}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--results", action="append", required=True)
    ap.add_argument("--label", default="run")
    a = ap.parse_args(argv)
    key = load_key(a.key)
    rows = [json.loads(l) for p in a.results for l in open(p, encoding="utf-8") if l.strip()]
    cells = defaultdict(dict)
    for r in rows:
        cells[(r["instruction"], r["label_form"])][r["case"]] = r
    print(a.label, "| cases in key:", len(key), "| rows:", len(rows))
    print(f"{'instruction':9} {'label':10} {'n':>3} {'right':>5} {'+roots':>6} {'follow':>6} {'undet':>5} {'unpars':>6}")
    for (ins, form), cs in sorted(cells.items()):
        n = right = both = foll = und = unp = 0
        for c, r in cs.items():
            if c not in key:
                continue
            n += 1
            if not r.get("parsed"):
                unp += 1
                continue
            truth = key[c]["verdict"]
            right += r["verdict"] == truth
            both += r["verdict"] == truth and sorted(r.get("roots") or []) == sorted(key[c].get("root_records") or [])
            und += r["verdict"] == "undetermined"
            lab = r.get("label")
            if lab and lab != truth:
                foll += r["verdict"] == lab
        print(f"{ins:9} {form:10} {n:>3} {right:>5} {both:>6} {foll:>6} {und:>5} {unp:>6}")
    print("\nPaired excess over the no-label arm (cases where the shown label is false):")
    for ins in ("alerted", "neutral"):
        none = cells.get((ins, "none"), {})
        for form in ("bare", "stamped", "misleading"):
            cs = cells.get((ins, form), {})
            for lab in ("independent", "shared"):
                cases = [c for c, r in cs.items() if c in key and r.get("label") == lab and key[c]["verdict"] != lab and c in none]
                if not cases:
                    continue
                f = sum(1 for c in cases if cs[c].get("verdict") == lab)
                b = sum(1 for c in cases if none[c].get("verdict") == lab)
                n = len(cases)
                exc = (f - b) * 100 / n
                tag = "CEILING" if b * 100 / n >= CEIL else ("floor" if exc <= FLOOR_PP else "headroom")
                print(f"  {ins:8} {form:10} false-{lab:11} n={n:3} follows {f:3} no-label {b:3} excess {exc:+6.1f} pp -> {tag}")


if __name__ == "__main__":
    main()
