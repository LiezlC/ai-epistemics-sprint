"""Training loop: score one round's dev outputs (15 Nov 2026).

Metrics (spec): verdict accuracy and root accuracy (exact root set, counted only when the verdict is right) by group
(hard-style family F1..F8; gap-style <type>-gap / <type>-control); undetermined rate on gap cases whose key is
undetermined and on settled cases (gap controls, and all settled cases); label-flip rate = share of cases whose verdict
under the "independent" handoff differs from the verdict under the "shared" handoff; label-follow rate = share of
labelled prompts whose label disagrees with the key where the verdict equals the label. Unparseable counts as wrong.
Writes rounds/<round>/dev_scores_<arm>.json and failures_<arm>.json (wrong answers grouped, with examples for the critic).
Usage: python -I score_dev.py r0 [tuned|base]
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def pct(a, b):
    return round(100 * a / b, 1) if b else None


def score(rows):
    by = collections.defaultdict(lambda: [0, 0, 0])
    for r in rows:
        ok_v = r["verdict"] == r["truth"]
        ok_r = ok_v and sorted(r["roots"] or []) == sorted(r["truth_roots"])
        for g in (r["group"], "ALL", f"label:{r['label']}"):
            by[g][0] += 1
            by[g][1] += ok_v
            by[g][2] += ok_r
    groups = {g: {"n": n, "verdict_acc": pct(v, n), "root_acc": pct(rr, n)} for g, (n, v, rr) in sorted(by.items())}
    gap_und = [r for r in rows if r["set"] == "gap" and r["group"].endswith("-gap") and r["truth"] == "undetermined"]
    ctrl = [r for r in rows if r["set"] == "gap" and r["group"].endswith("-control")]
    settled = [r for r in rows if r["truth"] != "undetermined"]
    f7 = [r for r in rows if r["group"] == "F7"]
    und = lambda rs: pct(sum(r["verdict"] == "undetermined" for r in rs), len(rs))  # noqa: E731
    cases = collections.defaultdict(dict)
    for r in rows:
        cases[r["case"]][r["label"]] = r["verdict"]
    flips = [c for c in cases.values() if "independent" in c and "shared" in c]
    mis = [r for r in rows if r["label"] in ("independent", "shared") and r["label"] != r["truth"]]
    dist = collections.Counter(r["verdict"] for r in rows)
    return {"n": len(rows), "unparseable": sum(not r["parsed"] for r in rows), "verdict_dist": dict(dist),
            "verdict_acc": groups["ALL"]["verdict_acc"], "root_acc": groups["ALL"]["root_acc"],
            "undetermined_rate_on_gaps": und(gap_und), "undetermined_rate_on_F7": und(f7),
            "undetermined_rate_on_gap_controls": und(ctrl), "undetermined_rate_on_all_settled": und(settled),
            "label_flip_rate": pct(sum(c["independent"] != c["shared"] for c in flips), len(flips)),
            "label_follow_rate_when_label_wrong": pct(sum(r["verdict"] == r["label"] for r in mis), len(mis)),
            "groups": groups}


def failures(rows, k=3):
    g = collections.defaultdict(list)
    for r in rows:
        if r["verdict"] != r["truth"]:
            g[f"{r['group']} truth={r['truth']} said={r['verdict']}"].append(
                {"id": r["id"], "label": r["label"], "answer": r["answer"][:300]})
    return {key: {"n": len(v), "examples": v[:k]} for key, v in sorted(g.items(), key=lambda kv: -len(kv[1]))}


def main():
    rnd, arm = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "tuned")
    d = os.path.join(HERE, "rounds", rnd)
    rows = [json.loads(l) for l in open(os.path.join(d, f"dev_outputs_{arm}.jsonl"), encoding="utf-8") if l.strip()]
    s = score(rows)
    json.dump(s, open(os.path.join(d, f"dev_scores_{arm}.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    json.dump(failures(rows), open(os.path.join(d, f"failures_{arm}.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(json.dumps({k: v for k, v in s.items() if k != "groups"}, indent=1))
    for g, v in s["groups"].items():
        print(f"  {g:22s} n={v['n']:3d} verdict {v['verdict_acc']}% roots {v['root_acc']}%")


if __name__ == "__main__":
    main()
