"""Hard set scorer (frozen with the cases, 15 Nov 2026). Implements SCORER-PLAN.md.

Usage: python -I score_hard.py --arm NAME=RUN_DIR [--arm ...] [--base NAME --tuned NAME] --out scores.json
RUN_DIR holds results.jsonl (raw rows with case, label, verdict, roots, parsed, error).
Status (kept/quarantined) comes from validation_decisions.json; the headline is kept bundles, quarantined reported apart.
"""
import argparse
import glob
import json
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
VALID = {"independent", "shared", "undetermined"}


def load(d):
    rows = []
    for p in glob.glob(os.path.join(d, "*.jsonl")):
        rows += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return {(r["case"], r["label"]): r for r in rows if "case" in r}


def row_scores(r, k):
    v = r.get("verdict") if not r.get("error") else None
    invalid = v not in VALID
    vok = (not invalid) and v == k["verdict"]
    if k["verdict"] == "undetermined":
        rok = None
        jok = vok
    else:
        roots = r.get("roots") if isinstance(r.get("roots"), list) else []
        rok = (not invalid) and {str(x).strip() for x in roots} == set(k["root_records"])
        jok = vok and rok
    return {"verdict": v, "invalid": invalid, "v": vok, "r": rok, "j": jok}


def per_bundle(rows, key):
    out = {}
    for case, k in key.items():
        s = {lab: row_scores(rows.get((case, lab), {"error": "missing"}), k) for lab in ("independent", "shared")}
        out[case] = s
    return out


def agg(b, cases):
    n = 2 * len(cases)
    if not cases:
        return {"bundles": 0}
    v = sum(b[c][l]["v"] for c in cases for l in b[c]) / n
    rr = [b[c][l]["r"] for c in cases for l in b[c] if b[c][l]["r"] is not None]
    j = sum(b[c][l]["j"] for c in cases for l in b[c]) / n
    inv = sum(b[c][l]["invalid"] for c in cases for l in b[c]) / n
    flip = sum(b[c]["independent"]["verdict"] != b[c]["shared"]["verdict"] for c in cases) / len(cases)
    by_label = {l: sum(b[c][l]["v"] for c in cases) / len(cases) for l in ("independent", "shared")}
    return {"bundles": len(cases), "prompts": n, "verdict_acc": round(v, 4),
            "root_acc": round(sum(rr) / len(rr), 4) if rr else None, "joint_acc": round(j, 4),
            "invalid_json": round(inv, 4), "label_flip_rate": round(flip, 4),
            "verdict_acc_by_label": {k: round(x, 4) for k, x in by_label.items()}}


def bundle_metric(b, c, m):
    vals = [b[c][l][m] for l in b[c] if b[c][l][m] is not None]
    return sum(vals) / len(vals) if vals else None


def boot(bb, bt, cases, m, n=10000, seed=20261115):
    cs = [c for c in cases if bundle_metric(bb, c, m) is not None]
    d = [bundle_metric(bt, c, m) - bundle_metric(bb, c, m) for c in cs]
    if not d:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(n))
    return {"diff_tuned_minus_base": round(sum(d) / len(d), 4), "ci95": [round(means[int(0.025 * n)], 4),
            round(means[int(0.975 * n) - 1], 4)], "bundles": len(d)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", required=True)
    ap.add_argument("--base")
    ap.add_argument("--tuned")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    key = json.load(open(os.path.join(HERE, "key.json"), encoding="utf-8"))
    dec = json.load(open(os.path.join(HERE, "validation_decisions.json"), encoding="utf-8"))["cases"]
    cases_in = sorted(c for c in key if c in dec)
    key = {c: key[c] for c in cases_in}
    kept = [c for c in cases_in if dec[c]["decision"] == "keep"]
    quar = [c for c in cases_in if dec[c]["decision"] != "keep"]
    res, bund = {"arms": {}}, {}
    for spec in a.arm:
        name, d = spec.split("=", 1)
        b = per_bundle(load(d), key)
        bund[name] = b
        fam = defaultdict(list)
        dep = defaultdict(list)
        for c in kept:
            fam[key[c]["family"]].append(c)
            dep[key[c]["depth"]].append(c)
        res["arms"][name] = {"kept": agg(b, kept), "quarantined": agg(b, quar), "all": agg(b, cases_in),
                             "by_family_kept": {f: agg(b, cs) for f, cs in sorted(fam.items())},
                             "by_depth_kept": {str(k): agg(b, cs) for k, cs in sorted(dep.items())}}
    if a.base and a.tuned:
        res["tuned_vs_base_kept"] = {m: boot(bund[a.base], bund[a.tuned], kept, m) for m in ("v", "r", "j")}
    json.dump(res, open(a.out, "w", encoding="utf-8", newline="\n"), indent=1)
    print(json.dumps({n: x["kept"] for n, x in res["arms"].items()}, indent=1))
    if "tuned_vs_base_kept" in res:
        print(json.dumps(res["tuned_vs_base_kept"], indent=1))


if __name__ == "__main__":
    main()
