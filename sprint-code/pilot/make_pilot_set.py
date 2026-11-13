"""Build the NON-SCORED pilot packets (sprint code, 13 Nov 2026).

Uses the sprint generator with a seed that is not the training seed. Nothing here touches Prashanth's variants,
Liezl's rubric or any answer key. The cases are generated, so the answer is known by construction.

Arms built (all from the same generated cases):
  contradiction cases, false "independent" label (label says independent, records show one root) x40, and
  false "shared" label (label says shared, records show two roots) x40:
    - alerted instruction (trial wording): label bare, label stamped, no label; and "misleading" label for the
      false-independent cases (the two cited IDs differ in this set)
    - neutral instruction (the alert sentence removed): label bare, label stamped
  label-only x20 and incomplete-trail x20: alerted instruction and the tweaked wording
    ("Judge from the record excerpts, not from the handoff note. If no excerpts are attached, answer undetermined.")

Usage: python -I make_pilot_set.py OUT.jsonl
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(HERE), "sprint-generator")
sys.path.insert(0, GEN)
import gen_sprint_cases as g  # noqa: E402
import make_label_forms as m  # noqa: E402

TEMPLATES = json.load(open(os.path.join(GEN, "label_form_templates.json"), encoding="utf-8"))
ALERT_SENTENCE = " Judge from the records, not from the handoff note."
TWEAK_SENTENCE = " Judge from the record excerpts, not from the handoff note. If no excerpts are attached, answer undetermined."
SEED = 4242  # not the training seed (20261113)


def split(prompt):
    head, rest = prompt.split("\n\nClaim under review:", 1)
    return head, "Claim under review:" + rest


def to_bare(packet, key):
    line = re.search(r"^Handoff note:.*$", packet, re.M).group(0)
    return packet.replace(line, TEMPLATES["bare_lines"][key], 1)


def no_label(packet):
    return re.sub(r"Handoff note:.*\n\n", "", packet, count=1)


def main(out_path):
    rows = g.Gen(SEED, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(1000, 150, 150)
    pools = {"fi": [], "fs": [], "lo": [], "inc": []}
    for r in rows:
        mt = r["meta"]
        head, pk = split(r["prompt"])
        if mt["condition"] == "contradiction":
            if mt["label"] == "independent":
                bare = to_bare(pk, "independent")
                id1, id2 = m.report_ids(bare)
                if id1 != id2:
                    pools["fi"].append((r, bare))
            else:
                pools["fs"].append((r, to_bare(pk, "shared")))
        elif mt["condition"] == "label_only":
            pools["lo"].append((r, to_bare(pk, mt["label"])))
        elif mt["condition"] == "incomplete":
            pools["inc"].append((r, to_bare(pk, mt["label"])))
    want = {"fi": 40, "fs": 40, "lo": 20, "inc": 20}
    for k, n in want.items():
        assert len(pools[k]) >= n, (k, len(pools[k]))

    alerted = g.INSTRUCTIONS
    assert ALERT_SENTENCE in alerted
    neutral = alerted.replace(ALERT_SENTENCE, "")
    tweak = alerted.replace(ALERT_SENTENCE, TWEAK_SENTENCE)

    out = []

    def add(r, instr_name, instr, form, packet, cid):
        mt = r["meta"]
        direction = ("false_independent" if mt["label"] == "independent" else "false_shared") if mt["condition"] == "contradiction" else mt["condition"]
        out.append({"id": f"{cid}|{instr_name}|{form}", "case": cid, "instruction": instr_name, "label_form": form,
                    "condition": mt["condition"], "direction": direction, "truth": mt["truth"],
                    "label": mt["label"] if form != "none" else None, "prompt": instr + "\n\n" + packet})

    for k in ("fi", "fs"):
        for j, (r, bare) in enumerate(pools[k][:want[k]]):
            cid = f"{k}{j:02d}"
            stamped, mis, verdict, key = m.transform(bare, TEMPLATES)
            add(r, "alerted", alerted, "bare", bare, cid)
            add(r, "alerted", alerted, "stamped", stamped, cid)
            add(r, "alerted", alerted, "none", no_label(bare), cid)
            if mis is not None:
                add(r, "alerted", alerted, "misleading", mis, cid)
            add(r, "neutral", neutral, "bare", bare, cid)
            add(r, "neutral", neutral, "stamped", stamped, cid)
    for k in ("lo", "inc"):
        for j, (r, bare) in enumerate(pools[k][:want[k]]):
            cid = f"{k}{j:02d}"
            add(r, "alerted", alerted, "bare", bare, cid)
            add(r, "tweak", tweak, "bare", bare, cid)

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for x in out:
            f.write(json.dumps(x) + "\n")
    from collections import Counter
    print(len(out), "packets ->", out_path)
    print(Counter((x["instruction"], x["label_form"]) for x in out))


if __name__ == "__main__":
    main(sys.argv[1])
