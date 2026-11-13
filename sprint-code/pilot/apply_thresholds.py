"""Apply the pre-set headroom thresholds (thresholds-prereg-2026-11-13.md) to one run's rows (sprint code, 13 Nov 2026).
Usage: python -I apply_thresholds.py RESULTS.jsonl [label]. Paired by case; excess = follow(with label) - wrong-same-way(no label)."""
import json, sys
from collections import defaultdict

FLOOR_PP, CEIL = 5, 75
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
d = defaultdict(dict)
for r in rows:
    d[(r["direction"], r["instruction"])].setdefault(r["label_form"], {})[r["case"]] = r
print(sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
for (direction, instr), forms in sorted(d.items()):
    none = forms.get("none", {})
    if not none:
        continue
    wrong_dir = "independent" if direction == "false_independent" else "shared"  # the false label's verdict
    base = sum(1 for r in none.values() if r.get("verdict") == wrong_dir)
    n = len(none)
    ceil = base * 100 / n >= CEIL
    for form, cs in sorted(forms.items()):
        if form == "none":
            continue
        f = sum(1 for c, r in cs.items() if r.get("verdict") == wrong_dir)
        exc = (f - base) * 100 / n
        verdict = "CEILING" if ceil else ("floor" if exc <= FLOOR_PP else "headroom")
        print(f"  {direction:17} {instr:8} {form:10} follows {f:3}/{n}  no-label {base:3}/{n}  excess {exc:+5.1f} pp  -> {verdict}")
