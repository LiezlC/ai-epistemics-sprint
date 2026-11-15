"""Hard set: write the prompt files (15 Nov 2026).

Prompt = frozen alerted instruction (sprint-code/freeze-drafts/instruction_alerted_trial_wording.txt, LF, trailing newlines
removed, read exactly as build_scored_packets.py reads it) + blank line + packet. Same row layout as packets_scored.jsonl.
- packets_hard.jsonl: 2 rows per kept case (label "independent" and label "shared"), byte-identical except the handoff line.
- packets_validate.jsonl: what the validators see: the true label only ("shared" or "independent");
  F7 (undetermined) gets both labels.
Usage: python -I make_packets.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FREEZE = os.path.join(os.path.dirname(HERE), "sprint-code", "freeze-drafts")
LABELS = {"independent": "These two reports are independent.", "shared": "These two reports repeat the same source."}


def instruction():
    t = open(os.path.join(FREEZE, "instruction_alerted_trial_wording.txt"), encoding="utf-8", newline="").read()
    return t.replace("\r\n", "\n").rstrip("\n")


def row(c, lab, instr):
    pk = c["packet"].replace("Handoff note: " + LABELS["independent"], "Handoff note: " + LABELS[lab])
    assert pk.count("Handoff note: " + LABELS[lab]) == 1
    return {"id": f"{c['case']}|alerted|{lab}", "case": c["case"], "family": c["family"], "instruction": "alerted",
            "label_form": "bare", "label": lab, "bare_label": lab, "derived": None, "prompt": instr + "\n\n" + pk}


def main():
    instr = instruction()
    cases = [json.loads(l) for l in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8") if l.strip()]
    key = json.load(open(os.path.join(HERE, "key.json"), encoding="utf-8"))
    cases.sort(key=lambda c: c["case"])
    with open(os.path.join(HERE, "packets_hard.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for c in cases:
            for lab in ("independent", "shared"):
                f.write(json.dumps(row(c, lab, instr), ensure_ascii=False) + "\n")
    n = 0
    with open(os.path.join(HERE, "packets_validate.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for c in cases:
            v = key[c["case"]]["verdict"]
            for lab in (("independent", "shared") if v == "undetermined" else (v,)):
                f.write(json.dumps(row(c, lab, instr), ensure_ascii=False) + "\n")
                n += 1
    print(len(cases), "cases;", 2 * len(cases), "hard rows;", n, "validator rows")


if __name__ == "__main__":
    main()
