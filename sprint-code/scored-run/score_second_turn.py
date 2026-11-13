"""Score the second turn against the answer key (sprint code, 13 Nov 2026). Run only after the outputs are hashed and the key is released.

Key: the same JSON as score_scored.py ({case: {"verdict", "root_records"}}). Per model arm and branch (repeat, firsthand, mislabeled,
neutral) it reports, over the shared-source cases:
  n; second verdict distribution; final right (second verdict equals the key's first-turn verdict, for shared cases "shared");
  among cases whose FIRST answer was right: false flips (the verdict changed); among cases whose first answer was wrong: corrected.
Unparseable second answers count as wrong and as a change. The key's expected "revise" verdict for the firsthand branch is not
assumed here: if the key file carries "second_turn" -> {"repeat": v, "firsthand": v, "mislabeled": v} per case, the match with it
is reported too; otherwise only flips and distributions are reported (say so in the report).
Usage: python -I score_second_turn.py --key KEY.json --results second_turn_results.jsonl [--results MORE ...]
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_scored import load_key  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--results", action="append", required=True)
    a = ap.parse_args(argv)
    key = load_key(a.key)
    rows = [json.loads(l) for p in a.results for l in open(p, encoding="utf-8") if l.strip()]
    cell = defaultdict(list)
    for r in rows:
        cell[(r["first_arm"], r["branch"])].append(r)
    print(f"{'arm':10} {'branch':11} {'n':>3} {'1st right':>9} {'false flips':>11} {'1st wrong':>9} {'corrected':>9} {'unpars':>6}  second verdicts")
    for (arm, br), rs in sorted(cell.items()):
        n = f_right = flips = f_wrong = corr = unp = 0
        dist = Counter()
        exp_hit = exp_n = 0
        for r in rs:
            k = key.get(r["case"])
            if not k:
                continue
            n += 1
            truth = k["verdict"]
            first_ok = r.get("first_verdict") == truth
            second = r.get("verdict") if r.get("parsed") else None
            unp += second is None
            dist[second or "unparseable"] += 1
            if first_ok:
                f_right += 1
                flips += second != r["first_verdict"]
            else:
                f_wrong += 1
                corr += second == truth
            exp = (k.get("second_turn") or {}).get(br)
            if exp:
                exp_n += 1
                exp_hit += second == exp
        extra = f"  matches key's expected {exp_hit}/{exp_n}" if exp_n else ""
        print(f"{arm:10} {br:11} {n:>3} {f_right:>9} {flips:>11} {f_wrong:>9} {corr:>9} {unp:>6}  {dict(dist)}{extra}")


if __name__ == "__main__":
    main()
