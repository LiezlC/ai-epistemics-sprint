"""Fresh headroom-check set (sprint code, 13 Nov 2026). Seed 7777; 100 false-independent + 100 false-shared cases.

Reuses helpers from make_pilot_set.py (unchanged). Arms: alerted x bare/stamped/none(/misleading for false-independent),
neutral x bare/stamped/none. Thresholds are in thresholds-prereg-2026-11-13.md (written before this was run).
Usage: python -I make_pilot_set_v2.py OUT.jsonl
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_pilot_set as base  # noqa: E402
g, m = base.g, base.m

SEED = 7777
N = 100


def main(out_path):
    rows = g.Gen(SEED, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(1500, 250, 250)
    pools = {"fi": [], "fs": []}
    for r in rows:
        mt = r["meta"]
        if mt["condition"] != "contradiction":
            continue
        head, pk = base.split(r["prompt"])
        if mt["label"] == "independent":
            bare = base.to_bare(pk, "independent")
            a, b = m.report_ids(bare)
            if a != b:
                pools["fi"].append((r, bare))
        else:
            pools["fs"].append((r, base.to_bare(pk, "shared")))
    for k in pools:
        assert len(pools[k]) >= N, (k, len(pools[k]))
    alerted = g.INSTRUCTIONS
    neutral = alerted.replace(base.ALERT_SENTENCE, "")
    out = []

    def add(r, iname, instr, form, packet, cid):
        mt = r["meta"]
        d = "false_independent" if mt["label"] == "independent" else "false_shared"
        out.append({"id": f"{cid}|{iname}|{form}", "case": cid, "instruction": iname, "label_form": form,
                    "condition": mt["condition"], "direction": d, "truth": mt["truth"],
                    "label": mt["label"] if form != "none" else None, "prompt": instr + "\n\n" + packet})

    for k in ("fi", "fs"):
        for j, (r, bare) in enumerate(pools[k][:N]):
            cid = f"v2{k}{j:03d}"
            stamped, mis, _v, _k = m.transform(bare, base.TEMPLATES)
            for iname, instr in (("alerted", alerted), ("neutral", neutral)):
                add(r, iname, instr, "bare", bare, cid)
                add(r, iname, instr, "stamped", stamped, cid)
                add(r, iname, instr, "none", base.no_label(bare), cid)
            if mis is not None:
                add(r, "alerted", alerted, "misleading", mis, cid)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for x in out:
            f.write(json.dumps(x) + "\n")
    print(len(out), "packets ->", out_path)
    print(Counter((x["direction"], x["instruction"], x["label_form"]) for x in out))


if __name__ == "__main__":
    main(sys.argv[1])
