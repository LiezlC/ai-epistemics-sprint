"""Gap set: write the target prompts (15 Nov 2026). Adapted from hard-set/make_packets.py.

Prompt = frozen alerted instruction (sprint-code/freeze-drafts/instruction_alerted_trial_wording.txt, LF, trailing newlines
removed) + blank line + packet. 3 rows per case (80 cases = 40 gap + 40 controls, 240 rows):
- label "none": handoff line dropped with the repo's frozen no-label function (sprint-generator/make_label_forms.no_label,
  imported unchanged), as in the main study's no-label arm;
- label "independent" / "shared": the bare handoff line. All three byte-identical apart from the handoff line.
Usage: python -I make_packets.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FREEZE = os.path.join(ROOT, "sprint-code", "freeze-drafts")
sys.path.insert(0, os.path.join(ROOT, "sprint-code", "sprint-generator"))
import make_label_forms as m  # noqa: E402  (frozen, unchanged)

LABELS = {"independent": "These two reports are independent.", "shared": "These two reports repeat the same source."}


def instruction():
    t = open(os.path.join(FREEZE, "instruction_alerted_trial_wording.txt"), encoding="utf-8", newline="").read()
    return t.replace("\r\n", "\n").rstrip("\n")


def row(c, lab, instr):
    if lab == "none":
        pk = m.no_label(c["packet"])
        assert "Handoff note:" not in pk
    else:
        pk = c["packet"].replace("Handoff note: " + LABELS["independent"], "Handoff note: " + LABELS[lab])
        assert pk.count("Handoff note: " + LABELS[lab]) == 1
    return {"id": f"{c['case']}|alerted|{lab}", "case": c["case"], "bundle": c["bundle"], "version": c["version"],
            "gap_type": c["gap_type"], "instruction": "alerted", "label_form": "none" if lab == "none" else "bare",
            "label": lab, "bare_label": None if lab == "none" else lab, "derived": None, "prompt": instr + "\n\n" + pk}


def main():
    instr = instruction()
    cases = [json.loads(l) for l in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8") if l.strip()]
    cases.sort(key=lambda c: c["case"])
    n = 0
    with open(os.path.join(HERE, "packets_gap.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for c in cases:
            for lab in ("none", "independent", "shared"):
                f.write(json.dumps(row(c, lab, instr), ensure_ascii=False) + "\n")
                n += 1
    print(len(cases), "cases;", n, "rows")


if __name__ == "__main__":
    main()
