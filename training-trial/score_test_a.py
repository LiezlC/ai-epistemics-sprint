"""Score results/test_a_outputs.jsonl against the frozen generator answers.

Usage: python -I score_test_a.py TRIAL_DIR
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict

D = sys.argv[1]
rows = [json.loads(l) for l in open(f"{D}/results/test_a_outputs.jsonl", encoding="utf-8")]
meta = [json.loads(l)["meta"] for l in open(f"{D}/data/test_a_meta.jsonl", encoding="utf-8")]
ARMS = ["base_zero", "base_3shot", "tuned_zero"]


def parse(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        return {"verdict": str(d.get("verdict", "")).strip().lower(), "roots": sorted(d.get("root_records") or [])}
    except Exception:
        return None


def exact_mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


res = {a: [] for a in ARMS}
for r, m in zip(rows, meta):
    gold = r["gold"]
    for a in ARMS:
        p = parse(r[a])
        res[a].append({
            "parsed": p is not None,
            "verdict": p["verdict"] if p else None,
            "v_ok": bool(p) and p["verdict"] == gold["verdict"],
            "roots_ok": bool(p) and p["verdict"] == gold["verdict"] and p["roots"] == sorted(gold["root_records"]),
            "gold": gold["verdict"], "cond": m["condition"], "wording": m["wording"],
        })

lines = ["# Test A results", "", f"{len(rows)} cases. Greedy decoding, thinking off.", "",
         "| Arm | Parsed | Verdict right | Verdict + roots right | False independent | False shared | Said undetermined |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
for a in ARMS:
    x = res[a]; n = len(x)
    fi = sum(1 for y in x if y["verdict"] == "independent" and y["gold"] != "independent")
    fs = sum(1 for y in x if y["verdict"] == "shared" and y["gold"] != "shared")
    un = sum(1 for y in x if y["verdict"] == "undetermined")
    lines.append(f"| {a} | {sum(y['parsed'] for y in x)}/{n} | {sum(y['v_ok'] for y in x)}/{n} | "
                 f"{sum(y['roots_ok'] for y in x)}/{n} | {fi} | {fs} | {un} |")

lines += ["", "## Verdict right, by condition", "", "| Condition | n | " + " | ".join(ARMS) + " |",
          "| --- | --- | " + " | ".join("---" for _ in ARMS) + " |"]
for cond in ["consistent", "contradiction", "incomplete", "label_only"]:
    idx = [i for i, m in enumerate(meta) if m["condition"] == cond]
    lines.append(f"| {cond} | {len(idx)} | " + " | ".join(f"{sum(res[a][i]['v_ok'] for i in idx)}" for a in ARMS) + " |")

lines += ["", "## Paired comparison with the tuned model (verdict right)", ""]
for a in ["base_zero", "base_3shot"]:
    b = sum(1 for i in range(len(rows)) if res["tuned_zero"][i]["v_ok"] and not res[a][i]["v_ok"])
    c = sum(1 for i in range(len(rows)) if res[a][i]["v_ok"] and not res["tuned_zero"][i]["v_ok"])
    lines.append(f"- tuned vs {a}: tuned fixes {b}, tuned breaks {c}, exact McNemar p = {exact_mcnemar(b, c):.4g}")

lines += ["", "## Verdict confusion (gold → said)", ""]
for a in ARMS:
    c = Counter((y["gold"], y["verdict"]) for y in res[a])
    lines.append(f"- {a}: " + ", ".join(f"{g}→{s}: {k}" for (g, s), k in sorted(c.items(), key=lambda t: (str(t[0][0]), str(t[0][1])))))

open(f"{D}/results/test_a_results.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
