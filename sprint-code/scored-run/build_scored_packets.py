"""Build the SCORED run's prompts from Prashanth's variants (sprint code, 13 Nov 2026).

Needs NO answer key and NO rubric: it only reads the variants (bare handoff label, as he writes them) and the frozen
files. Uses the frozen label-form script UNCHANGED (imported from ../sprint-generator) for the stamped, literal-but-
misleading and no-label forms.

Arms (same design as the headroom pilot): alerted instruction x bare / stamped / none / misleading, neutral instruction
x bare / stamped / none. The misleading form exists only where the bare label says independent, the records show a
shared root and the two reports cite different IDs (the frozen script's rule).
Prompt = instruction text + blank line + packet. The instruction text is the frozen file with line endings normalised
to LF and trailing newlines removed (the generator text equals it exactly: checked 13 Nov).

Usage: python -I build_scored_packets.py --variants FILE --out packets_scored.jsonl [--report report.json]
  FILE: .jsonl (key "prompt", optional "id") or .txt/.md (packets start at each "Claim under review:" line)
Output rows: id, case, instruction, label_form, label (what the shown label says; none for the no-label arm),
bare_label (the bare label read from the packet), derived (the verdict the records imply by the frozen derivation; NOT the
answer key), prompt. Unparseable packets are listed in the report, never guessed.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(HERE), "sprint-generator")
FREEZE = os.path.join(os.path.dirname(HERE), "freeze-drafts")
sys.path.insert(0, GEN)
import make_label_forms as m  # noqa: E402  (frozen script, unchanged)


def read_instruction(name):
    t = open(os.path.join(FREEZE, name), encoding="utf-8", newline="").read().replace("\r\n", "\n")
    return t.rstrip("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", default=None)
    ap.add_argument("--templates", default=os.path.join(GEN, "label_form_templates.json"))
    a = ap.parse_args()
    templates = json.load(open(a.templates, encoding="utf-8"))
    alerted = read_instruction("instruction_alerted_trial_wording.txt")
    neutral = read_instruction("instruction_neutral_draft.txt")

    kind, container, packets = m.read_packets(a.variants)
    ids = [r.get("id") for r in container] if kind == "jsonl" else [None] * len(packets)
    rows, skipped, counts = [], [], {}
    for i, p in enumerate(packets):
        cid = str(ids[i]) if ids[i] is not None else f"v{i:03d}"
        try:
            stamped, mis, derived, key = m.transform(p, templates)
            none = m.no_label(p)
        except ValueError as e:
            skipped.append({"index": i, "case": cid, "reason": str(e)})
            continue
        forms = {"bare": p, "stamped": stamped, "none": none, "misleading": mis}
        for instr_name, instr, wanted in (("alerted", alerted, ("bare", "stamped", "none", "misleading")),
                                          ("neutral", neutral, ("bare", "stamped", "none"))):
            for form in wanted:
                text = forms[form]
                if text is None:
                    continue
                shown = None if form == "none" else ("independent" if form == "misleading" else key)
                rows.append({"id": f"{cid}|{instr_name}|{form}", "case": cid, "instruction": instr_name,
                             "label_form": form, "label": shown, "bare_label": key, "derived": derived,
                             "prompt": instr + "\n\n" + text})
                counts[(instr_name, form)] = counts.get((instr_name, form), 0) + 1
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    rep = {"variants": os.path.abspath(a.variants), "variants_sha256": hashlib.sha256(open(a.variants, "rb").read()).hexdigest(),
           "templates_sha256": hashlib.sha256(open(a.templates, "rb").read()).hexdigest(),
           "out_sha256": hashlib.sha256(open(a.out, "rb").read()).hexdigest(),
           "packets_read": len(packets), "packets_skipped": skipped, "rows": len(rows),
           "rows_by_arm": {f"{k[0]}|{k[1]}": v for k, v in sorted(counts.items())}}
    if a.report:
        json.dump(rep, open(a.report, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "variants"}, indent=1))
    sys.exit(1 if skipped else 0)


if __name__ == "__main__":
    main()
