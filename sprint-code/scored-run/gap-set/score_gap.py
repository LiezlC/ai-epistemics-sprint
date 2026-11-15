"""Gap set scorer (frozen with the cases, 15 Nov 2026). Implements the Scoring section of notes/gap-set-spec.md.

Usage: python -I score_gap.py --arm NAME=PATH [--arm ...] [--base NAME --tuned NAME] --out scores.json
PATH is a results .jsonl file or a folder of them (rows with case, label, verdict, roots, error).
Per arm:
- gap cases, per label condition (none / independent / shared): undetermined rate and verdict distribution
  (invalid = error, unparseable or not one of the three verdicts);
- controls, per label condition: verdict, root and joint accuracy, and verdict distribution;
- label pull, gap and control: pull_ind = share "independent" under the independent label minus share "independent" with
  no label; pull_sh = the same for "shared"; pull = their mean;
- main contrast: per bundle, pull(gap) - pull(control) with pull per bundle = (1[ind|ind] - 1[ind|none] + 1[sh|sh] -
  1[sh|none]) / 2; mean with a bootstrap 95% interval over bundles (10,000 resamples, seed 20261116);
- breakdown by gap type (gap and control).
Tuned against base (paired over bundles, bootstrap): gap undetermined rate, control joint accuracy, gap pull, control pull.
"""
import argparse
import glob
import json
import os
import random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
VALID = {"independent", "shared", "undetermined"}
LABS = ("none", "independent", "shared")
SEED, NB = 20261116, 10000


def load(path):
    files = [path] if os.path.isfile(path) else glob.glob(os.path.join(path, "*.jsonl"))
    rows = []
    for p in files:
        rows += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return {(r["case"], r["label"]): r for r in rows if "case" in r}


def verdict(r):
    v = None if (r is None or r.get("error")) else r.get("verdict")
    return v if v in VALID else "invalid"


def roots_ok(r, k):
    roots = r.get("roots") if r and isinstance(r.get("roots"), list) else []
    return {str(x).strip() for x in roots} == set(k["root_records"])


def mean(x):
    return sum(x) / len(x) if x else None


def r4(x):
    return None if x is None else round(x, 4)


def boot(d):
    d = [x for x in d if x is not None]
    if not d:
        return None
    rng = random.Random(SEED)
    ms = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(NB))
    return {"mean": r4(mean(d)), "ci95": [r4(ms[int(0.025 * NB)]), r4(ms[int(0.975 * NB) - 1])], "bundles": len(d)}


def bundle_pull(V, case):
    v = {l: V[(case, l)] for l in LABS}
    pi = (v["independent"] == "independent") - (v["none"] == "independent")
    ps = (v["shared"] == "shared") - (v["none"] == "shared")
    return (pi + ps) / 2, pi, ps


def summarise(V, R, key, cases, version):
    out = {"cases": len(cases), "by_label": {}}
    for l in LABS:
        vs = [V[(c, l)] for c in cases]
        d = {"n": len(vs), "dist": dict(Counter(vs)), "undetermined_rate": r4(mean([v == "undetermined" for v in vs])),
             "invalid_rate": r4(mean([v == "invalid" for v in vs]))}
        if version == "control":
            d["verdict_acc"] = r4(mean([V[(c, l)] == key[c]["verdict"] for c in cases]))
            d["joint_acc"] = r4(mean([V[(c, l)] == key[c]["verdict"] and roots_ok(R[(c, l)], key[c]) for c in cases]))
        else:
            d["verdict_acc"] = d["undetermined_rate"]
        out["by_label"][l] = d
    share = lambda l, v: mean([V[(c, l)] == v for c in cases])  # noqa: E731
    if cases:
        pi = share("independent", "independent") - share("none", "independent")
        ps = share("shared", "shared") - share("none", "shared")
        out["label_pull"] = {"pull_ind": r4(pi), "pull_sh": r4(ps), "pull": r4((pi + ps) / 2)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", required=True)
    ap.add_argument("--base")
    ap.add_argument("--tuned")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    key = json.load(open(os.path.join(HERE, "key.json"), encoding="utf-8"))
    cases_in = {json.loads(l)["case"] for l in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8") if l.strip()}
    key = {c: k for c, k in key.items() if c in cases_in}
    bundles = sorted({k["bundle"] for k in key.values() if k["version"] == "gap" and k["bundle"] + "c" in key})
    gap = [b for b in bundles]
    ctl = [b + "c" for b in bundles]
    res, per = {"bundles": len(bundles), "arms": {}}, {}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        rows = load(path)
        V = {(c, l): verdict(rows.get((c, l))) for c in key for l in LABS}
        R = {(c, l): rows.get((c, l)) for c in key for l in LABS}
        missing = sum((c, l) not in rows for c in key for l in LABS)
        pb = {b: {"gap": bundle_pull(V, b), "ctl": bundle_pull(V, b + "c"),
                  "und": mean([V[(b, l)] == "undetermined" for l in LABS]),
                  "cjoint": mean([V[(b + "c", l)] == key[b + "c"]["verdict"] and roots_ok(R[(b + "c", l)], key[b + "c"])
                                  for l in LABS])} for b in bundles}
        per[name] = pb
        by_type = defaultdict(list)
        for b in bundles:
            by_type[key[b]["gap_type"]].append(b)
        res["arms"][name] = {
            "missing_rows": missing,
            "gap": summarise(V, R, key, gap, "gap"),
            "control": summarise(V, R, key, ctl, "control"),
            "contrast_gap_minus_control": {
                "pull": boot([pb[b]["gap"][0] - pb[b]["ctl"][0] for b in bundles]),
                "pull_ind": boot([pb[b]["gap"][1] - pb[b]["ctl"][1] for b in bundles]),
                "pull_sh": boot([pb[b]["gap"][2] - pb[b]["ctl"][2] for b in bundles])},
            "by_gap_type": {t: {"gap": summarise(V, R, key, bs, "gap"),
                                "control": summarise(V, R, key, [b + "c" for b in bs], "control")}
                            for t, bs in sorted(by_type.items())}}
    if a.base and a.tuned:
        B, T = per[a.base], per[a.tuned]
        res["tuned_vs_base"] = {
            "gap_undetermined_rate": boot([T[b]["und"] - B[b]["und"] for b in bundles]),
            "control_joint_acc": boot([T[b]["cjoint"] - B[b]["cjoint"] for b in bundles]),
            "gap_pull": boot([T[b]["gap"][0] - B[b]["gap"][0] for b in bundles]),
            "control_pull": boot([T[b]["ctl"][0] - B[b]["ctl"][0] for b in bundles])}
    json.dump(res, open(a.out, "w", encoding="utf-8", newline="\n"), indent=1)
    for n, x in res["arms"].items():
        g, c = x["gap"], x["control"]
        print(f"{n:10} gap und none/ind/sh {[g['by_label'][l]['undetermined_rate'] for l in LABS]} pull {g['label_pull']['pull']}"
              f" | ctl acc {[c['by_label'][l]['joint_acc'] for l in LABS]} pull {c['label_pull']['pull']}"
              f" | contrast {x['contrast_gap_minus_control']['pull']}")
    if "tuned_vs_base" in res:
        print(json.dumps(res["tuned_vs_base"]))


if __name__ == "__main__":
    main()
