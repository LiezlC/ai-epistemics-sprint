"""Loop dev set: write the dev prompts and the merged dev key (15 Nov 2026).

The dev set is for the training loop only; it is never a final test. Built from copies of the hard-set and gap-set
pipelines (dev/hard, dev/gap) with new seeds and new domains, wording by Codex, gated by the copied checkers.
Prompt = frozen alerted instruction (sprint-code/freeze-drafts/instruction_alerted_trial_wording.txt, read as the frozen
sets read it) + blank line + packet. 3 rows per case: no handoff line (frozen make_label_forms.no_label), bare
"independent" label, bare "shared" label. Byte-identical apart from the handoff line.
Key: dev/hard/key.json and dev/gap/key.json (gap key carries the audit fix: G2/G3 gaps on a shared control are shared).
Writes packets_dev.jsonl and key_dev.json.
Usage: python -I make_dev_packets.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FREEZE = os.path.join(REPO, "sprint-code", "freeze-drafts")
sys.path.insert(0, os.path.join(REPO, "sprint-code", "sprint-generator"))
import make_label_forms as m  # noqa: E402  (frozen, unchanged)

LABELS = {"independent": "These two reports are independent.", "shared": "These two reports repeat the same source."}


def instruction():
    t = open(os.path.join(FREEZE, "instruction_alerted_trial_wording.txt"), encoding="utf-8", newline="").read()
    return t.replace("\r\n", "\n").rstrip("\n")


def packet(pk, lab):
    if lab == "none":
        out = m.no_label(pk)
        assert "Handoff note:" not in out
        return out
    out = pk.replace("Handoff note: " + LABELS["independent"], "Handoff note: " + LABELS[lab])
    assert out.count("Handoff note: " + LABELS[lab]) == 1
    return out


def main():
    instr = instruction()
    key, rows = {}, []
    for sub in ("hard", "gap"):
        k = json.load(open(os.path.join(HERE, sub, "key.json"), encoding="utf-8"))
        for l in open(os.path.join(HERE, sub, "cases.jsonl"), encoding="utf-8"):
            if not l.strip():
                continue
            c = json.loads(l)
            kk = k[c["case"]]
            group = kk["family"] if sub == "hard" else f"{kk['gap_type']}-{kk['version']}"
            key[c["case"]] = {"set": sub, "group": group, "verdict": kk["verdict"], "root_records": kk["root_records"]}
            for lab in ("none", "independent", "shared"):
                rows.append({"id": f"{c['case']}|{lab}", "case": c["case"], "set": sub, "group": group, "label": lab,
                             "truth": kk["verdict"], "truth_roots": kk["root_records"],
                             "prompt": instr + "\n\n" + packet(c["packet"], lab)})
    rows.sort(key=lambda r: r["id"])
    with open(os.path.join(HERE, "packets_dev.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "key_dev.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(key, f, indent=1, sort_keys=True)
    print(len(key), "cases;", len(rows), "rows")


if __name__ == "__main__":
    main()
