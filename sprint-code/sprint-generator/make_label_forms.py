"""Make the other label forms from packets that carry the BARE label (option (a), agreed 13 Nov 2026).

SPRINT CODE (written 13 Nov 2026). The answer re-derivation reuses the logic of the preexisting
`training-trial/check_cases.py` (Liezl, 11 Nov 2026).

Input: packets in the trial layout: a line "Claim under review: ...", lines "Report 1. ..." and
"Report 2. ..." each citing exactly one record ID, ONE line starting "Handoff note:" with a bare label,
and "Record excerpts:" with lines "[ID] Type. text".
  - .jsonl: one JSON object per line with a "prompt" key (other keys are kept)
  - .txt / .md: packets start at each "Claim under review:" line

Output (in --out-dir), one file per form:
  bare      the input, unchanged
  stamped   the handoff line replaced by the stamped template (every packet with a bare label)
  misleading  the handoff line replaced by "Report 1 cites X, Report 2 cites Y" ONLY where the bare label
              says independent and the records show a shared root (the literally true but misleading form)
  none      the handoff line removed (no-label arm, added 13 Nov after the headroom re-run), every packet
A packet the script cannot parse is NOT guessed: it is listed in report.json under "skipped" with the reason.
Templates come from label_form_templates.json; its sha256 is printed so it can be frozen.

Usage: python -I make_label_forms.py --in FILE --out-dir DIR [--templates label_form_templates.json]
"""
import argparse
import hashlib
import json
import os
import re
import sys


ID = r"[A-Z]{1,3}-\d+"
REC_TRIAL = re.compile(rf"^\[({ID})\] ([^.]+)\. (.*)$", re.M)          # [R-12] Shift summary. text
REC_PV = re.compile(rf'^({ID}) \(([^)]*)\):\s*"?(.*?)"?\s*$', re.M)    # R-12 (Shift summary): "text"  (Prashanth's layout, 13 Nov)


def parse_records(prompt):
    """Return {id: (is_firsthand, cited_id_or_None)} for either record layout.
    Trial layout: firsthand = the ID letter is one of G, C, I, S, M (as in check_cases.py).
    Prashanth's layout: no letters are assumed; a record that cites no other record is the root (his rule, 13 Nov).
    Caveat for his layout: a dead-end note that cites nothing would also count as a root."""
    recs = {}
    for m in REC_TRIAL.finditer(prompt):
        rid, _, text = m.groups()
        first = rid[0] in "GCISM"
        cites = [c for c in re.findall(rf"\b({ID})\b", text) if c != rid]
        recs[rid] = (first, cites[0] if cites and not first else None)
    if not recs:
        for m in REC_PV.finditer(prompt):
            rid, _, text = m.groups()
            cites = [c for c in re.findall(rf"\b({ID})\b", text) if c != rid]
            recs[rid] = (not cites, cites[0] if cites else None)
    return recs


def derive(prompt):
    """Re-derive (verdict, roots) from the visible packet text alone (as in check_cases.py, extended to both layouts)."""
    recs = parse_records(prompt)
    reps = report_ids(prompt)
    if "No record excerpts" in prompt:
        return ("undetermined", [])
    roots = []
    for c in reps:
        seen = 0
        while c in recs and not recs[c][0] and recs[c][1] and seen < 5:
            c = recs[c][1]
            seen += 1
        roots.append(c if c in recs and recs[c][0] else None)
    if None in roots:
        return ("undetermined", [])
    if roots[0] == roots[1]:
        return ("shared", [roots[0]])
    return ("independent", sorted(roots))


def report_ids(prompt):
    out = []
    for n in (1, 2):
        m = re.search(rf"^Report {n}\. (.*)$", prompt, re.M)
        if not m:
            raise ValueError(f"no 'Report {n}.' line")
        ids = re.findall(rf"\b({ID})\b", m.group(1))
        if len(ids) != 1:
            raise ValueError(f"Report {n} cites {len(ids)} record IDs (need exactly 1)")
        out.append(ids[0])
    return out


def handoff_line(prompt, templates):
    lines = re.findall(r"^Handoff note:.*$", prompt, re.M)
    if len(lines) != 1:
        raise ValueError(f"{len(lines)} 'Handoff note:' lines (need exactly 1)")
    line = lines[0].rstrip()
    for key, text in templates["bare_lines"].items():
        if line == text:
            return line, key
    # Not one of the bare templates exactly (the variants are written by hand). Classify by words, but only
    # when it is unambiguous; otherwise skip the packet and say why.
    low = line.lower()
    says_ind = "independent" in low and "not independent" not in low and "non-independent" not in low
    says_sh = bool(re.search(r"same source|common source|single source|one source|shared", low))
    if says_ind != says_sh:
        return line, ("independent" if says_ind else "shared")
    raise ValueError("handoff line is not a bare template and cannot be classified: " + line[:80])


def transform(prompt, templates):
    """Return (stamped_prompt, misleading_prompt_or_None, derived_verdict, bare_key)."""
    line, key = handoff_line(prompt, templates)
    id1, id2 = report_ids(prompt)
    verdict, _ = derive(prompt)
    stamped = prompt.replace(line, templates["stamped_lines"][key], 1)
    mis = None
    # The literal form lists the two cited IDs. If both reports cite the same ID the sentence would
    # not mislead, so no misleading form is made for that packet (main() reports it).
    if key == "independent" and verdict == "shared" and id1 != id2:
        mis = prompt.replace(line, templates["misleading_line"].format(id1=id1, id2=id2), 1)
    return stamped, mis, verdict, key


def no_label(prompt):
    """The packet with the handoff line removed (one adjacent blank line goes with it, so no double gap is left)."""
    lines = prompt.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("Handoff note:")]
    if len(idx) != 1:
        raise ValueError(f"{len(idx)} 'Handoff note:' lines (need exactly 1)")
    i = idx[0]
    del lines[i]
    if i < len(lines) and lines[i] == "" and (i == 0 or lines[i - 1] == ""):
        del lines[i]
    return "\n".join(lines)


def read_packets(path):
    if path.endswith(".jsonl"):
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        return "jsonl", rows, [r["prompt"] for r in rows]
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"(?m)^(?=Claim under review:)", text)
    head = parts[0] if parts and not parts[0].startswith("Claim under review:") else ""
    packets = [p for p in parts if p.startswith("Claim under review:")]
    return "text", head, packets


def write_forms(kind, container, packets, outputs, out_dir, stem):
    """outputs: dict form -> list of packet text or None (skipped)."""
    for form, items in outputs.items():
        path = os.path.join(out_dir, f"{stem}.{form}" + (".jsonl" if kind == "jsonl" else ".txt"))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            if kind == "jsonl":
                for row, new in zip(container, items):
                    if new is None:
                        continue
                    r = dict(row)
                    r["prompt"] = new
                    r["label_form"] = form
                    f.write(json.dumps(r) + "\n")
            else:
                f.write(container)
                for new in items:
                    if new is not None:
                        f.write(new if new.endswith("\n") else new + "\n")
                        if not new.endswith("\n\n"):
                            f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--templates", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_form_templates.json"))
    a = ap.parse_args()

    tpath = a.templates
    templates = json.load(open(tpath, encoding="utf-8"))
    print("templates", tpath, "sha256", hashlib.sha256(open(tpath, "rb").read()).hexdigest())
    os.makedirs(a.out_dir, exist_ok=True)
    kind, container, packets = read_packets(a.inp)

    out = {"bare": [], "stamped": [], "misleading": [], "none": []}
    skipped, n_mis, same_id = [], 0, []
    for i, p in enumerate(packets):
        try:
            stamped, mis, verdict, key = transform(p, templates)
            nolabel = no_label(p)
        except ValueError as e:
            skipped.append({"index": i, "reason": str(e)})
            for k in out:
                out[k].append(None)
            continue
        if key == "independent" and verdict == "shared" and mis is None:
            same_id.append(i)
        out["bare"].append(p)
        out["stamped"].append(stamped)
        out["misleading"].append(mis)
        out["none"].append(nolabel)
        n_mis += mis is not None

    stem = os.path.splitext(os.path.basename(a.inp))[0]
    write_forms(kind, container, packets, out, a.out_dir, stem)
    report = {
        "input": os.path.abspath(a.inp),
        "input_sha256": hashlib.sha256(open(a.inp, "rb").read()).hexdigest(),
        "templates_sha256": hashlib.sha256(open(tpath, "rb").read()).hexdigest(),
        "packets": len(packets), "bare": sum(x is not None for x in out["bare"]),
        "stamped": sum(x is not None for x in out["stamped"]), "misleading": n_mis,
        "none": sum(x is not None for x in out["none"]),
        "shared_root_but_both_reports_cite_the_same_id_no_misleading_form": same_id,
        "skipped": skipped,
    }
    json.dump(report, open(os.path.join(a.out_dir, "report.json"), "w", encoding="utf-8"), indent=2)
    print(json.dumps({k: v for k, v in report.items() if k != "input"}, indent=2))
    sys.exit(1 if skipped else 0)


if __name__ == "__main__":
    main()
