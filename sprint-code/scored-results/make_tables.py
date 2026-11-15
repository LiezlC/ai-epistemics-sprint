"""Rebuild the numbers for report Tables 3, 4, 5 and C1 from the released key and the four first-turn output files (repo layout, 15 Nov 2026).
Reads the released key and the raw outputs; writes nothing but prints. Primary = frozen scorer's rule (verdict and sorted roots exact).
Usage: python -I make_tables.py
"""
import json
import math
import os
from collections import defaultdict

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
KEY = json.load(open(os.path.join(BASE, "key", "answer-key.json"), encoding="utf-8"))
RUNS = {
    "27b": os.path.join(BASE, "variants", "joined-15", "runs", "scored27b", "results.jsonl"),
    "4B zero-shot": os.path.join(BASE, "variants", "joined-15", "runs", "4b_untuned", "scored_outputs_base_zero.jsonl"),
    "4B three-shot": os.path.join(BASE, "variants", "joined-15", "runs", "4b_3shot", "scored_outputs_base_3shot.jsonl"),
    "4B tuned (v2)": os.path.join(BASE, "variants", "joined-15", "runs", "4b_tuned_v2", "scored_outputs_tuned_zero.jsonl"),
}
FORMS = [("bare", "bare"), ("stamped", "authority-stamped"), ("misleading", "literal-misleading")]
rows = {m: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] for m, p in RUNS.items()}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({lo:.0f}-{hi:.0f}%)"


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def cell(model, ins, form):
    return {r["case"]: r for r in rows[model] if r["instruction"] == ins and r["label_form"] == form}


def table3(ins, models):
    print(f"\n== Label pull, {ins} instruction ==")
    print("model | form | direction | follows (Wilson) | same verdict no-label | pull pp | tag")
    for m in models:
        none = cell(m, ins, "none")
        for form, fname in FORMS:
            cs = cell(m, ins, form)
            for lab in ("independent", "shared"):
                cases = [c for c, r in cs.items() if r.get("label") == lab and KEY[c]["verdict"] != lab and c in none]
                if not cases:
                    continue
                f = sum(cs[c]["verdict"] == lab for c in cases)
                b = sum(none[c]["verdict"] == lab for c in cases)
                n = len(cases)
                exc = (f - b) * 100 / n
                tag = "ceiling" if b * 100 / n >= 75 else ("floor" if exc <= 5 else "headroom")
                print(f"{m} | {fname} | false-{lab} | {pct(f, n)} | {pct(b, n)} | {exc:+.1f} | {tag}")


def table4():
    print("\n== Label-following errors on false-independent cases (alerted): traced vs never traced ==")
    print("model | form | errors/n | traced root, followed label | never traced root")
    for m in RUNS:
        for form, fname in FORMS:
            cs = cell(m, "alerted", form)
            cases = [c for c, r in cs.items() if r.get("label") == "independent" and KEY[c]["verdict"] == "shared"]
            errs = [c for c in cases if cs[c]["verdict"] == "independent"]
            traced = [c for c in errs if set(KEY[c]["root_records"]) <= set(cs[c].get("roots") or [])]
            print(f"{m} | {fname} | {len(errs)}/{len(cases)} | {len(traced)} | {len(errs) - len(traced)}   errors at: {errs}")


def table5():
    print("\n== 4B arms on the same alerted rows (54 each) ==")
    print("arm | verdict right | verdict+roots right (primary) | roots right, repeats removed (secondary) | follows false label | undetermined | unparseable")
    sel = {}
    for m in ("4B zero-shot", "4B three-shot", "4B tuned (v2)"):
        rs = [r for r in rows[m] if r["instruction"] == "alerted"]
        sel[m] = {r["id"]: r for r in rs}
        n = len(rs)
        vr = sum(r["verdict"] == KEY[r["case"]]["verdict"] for r in rs)
        both = sum(r["verdict"] == KEY[r["case"]]["verdict"] and sorted(r["roots"] or []) == sorted(KEY[r["case"]]["root_records"]) for r in rs)
        bothd = sum(r["verdict"] == KEY[r["case"]]["verdict"] and sorted(set(r["roots"] or [])) == sorted(KEY[r["case"]]["root_records"]) for r in rs)
        fr = [r for r in rs if r.get("label") and r["label"] != KEY[r["case"]]["verdict"]]
        foll = sum(r["verdict"] == r["label"] for r in fr)
        und = sum(r["verdict"] == "undetermined" for r in rs)
        unp = sum(not r.get("parsed") for r in rs)
        print(f"{m} | {vr}/{n} | {both}/{n} | {bothd}/{n} | {foll}/{len(fr)} | {und} | {unp}")
    z, t = sel["4B zero-shot"], sel["4B three-shot"]
    ids = sorted(set(z) & set(t))
    ok = lambda r: r["verdict"] == KEY[r["case"]]["verdict"]
    fixes = sum(ok(t[i]) and not ok(z[i]) for i in ids)
    breaks = sum(ok(z[i]) and not ok(t[i]) for i in ids)
    print(f"paired verdict right, three-shot vs zero-shot: fixes {fixes}, breaks {breaks}, exact McNemar p = {mcnemar_exact(fixes, breaks):.2f}")
    mz = [i for i in ids if z[i]["label_form"] == "misleading"]
    print("literal-misleading rows: zero-shot right", sum(ok(z[i]) for i in mz), "/", len(mz), "; three-shot right", sum(ok(t[i]) for i in mz), "/", len(mz))


def verdict_summary():
    print("\n== Verdict right / verdict+roots right, all rows ==")
    for m, rs in rows.items():
        n = len(rs)
        vr = sum(r["verdict"] == KEY[r["case"]]["verdict"] for r in rs)
        both = sum(r["verdict"] == KEY[r["case"]]["verdict"] and sorted(r["roots"] or []) == sorted(KEY[r["case"]]["root_records"]) for r in rs)
        print(m, vr, "/", n, "|", both, "/", n)


def case_mix():
    lab = defaultdict(set)
    for r in rows["27b"]:
        lab[r["case"]].add(r.get("label"))
    fi = sum(1 for c in KEY if KEY[c]["verdict"] == "shared" and "independent" in lab[c])
    fs = sum(1 for c in KEY if KEY[c]["verdict"] == "independent" and "shared" in lab[c])
    print("\ncases:", len(KEY), "key shared", sum(KEY[c]["verdict"] == "shared" for c in KEY), "independent", sum(KEY[c]["verdict"] == "independent" for c in KEY), "| false-independent", fi, "false-shared", fs)


case_mix()
table3("alerted", list(RUNS))
table3("neutral", ["27b", "4B zero-shot", "4B tuned (v2)"])
table4()
table5()
verdict_summary()
