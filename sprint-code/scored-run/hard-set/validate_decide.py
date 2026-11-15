"""Hard set: apply the fixed 2-of-3 keep/quarantine rule (15 Nov 2026). No discretionary rescues.

Reads the three validator run folders (raw outputs written by sprint-code/scored-run/run_scored_openrouter.py) and key.json.
A validator matches a bundle when its parsed verdict equals the key verdict (verdict only; roots logged, not used).
F7 (undetermined) was shown under both labels; a validator matches only if it says undetermined under both.
Errors and unparseable answers count as no match.
Keep the bundle if at least 2 of 3 validators match; otherwise quarantine.
Usage: python -I validate_decide.py RUN_DIR_GLM RUN_DIR_KIMI RUN_DIR_DEEPSEEK
Writes validation_decisions.json.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def load_run(d):
    rows = []
    for p in glob.glob(os.path.join(d, "*.jsonl")):
        rows += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return rows


def main():
    key = json.load(open(os.path.join(HERE, "key.json"), encoding="utf-8"))
    dirs = sys.argv[1:4]
    per = defaultdict(dict)  # case -> model -> {label: verdict}
    roots = defaultdict(dict)
    models = []
    for d in dirs:
        summ = json.load(open(os.path.join(d, "run_summary.json"), encoding="utf-8"))
        models.append(summ["model"])
        for r in load_run(d):
            if "case" not in r:
                continue
            per[r["case"]].setdefault(summ["model"], {})[r["label"]] = r.get("verdict")
            roots[r["case"]].setdefault(summ["model"], {})[r["label"]] = r.get("roots")
    out, counts = {}, defaultdict(Counter)
    for case in sorted(per):
        k = key[case]["verdict"]
        match = {}
        for m in models:
            v = per[case].get(m, {})
            match[m] = bool(v) and all(x == k for x in v.values()) and (k != "undetermined" or len(v) == 2)
        dec = "keep" if sum(match.values()) >= 2 else "quarantine"
        out[case] = {"family": key[case]["family"], "key_verdict": k, "verdicts": per[case], "roots": roots[case],
                     "match": match, "decision": dec}
        counts[key[case]["family"]][dec] += 1
    res = {"models": models, "rule": "keep if >=2 of 3 validators match the key verdict; F7 must be undetermined under both labels",
           "by_family": {f: dict(c) for f, c in sorted(counts.items())}, "cases": out}
    json.dump(res, open(os.path.join(HERE, "validation_decisions.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(json.dumps(res["by_family"], indent=1))
    print({m: sum(o["match"][m] for o in out.values()) for m in models})


if __name__ == "__main__":
    main()
