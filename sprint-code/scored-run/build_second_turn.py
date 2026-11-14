"""Build the SECOND-TURN conversations (sprint code, 13 Nov 2026). Needs NO answer key and NO rubric.

Design (PROJECT-ANGLES.md, "Second turn: a request to reconsider"; Liezl's key on 13 Nov: repeat -> hold, new firsthand inspection ->
revise, mislabeled repeat -> hold, neutral recheck as control; Prashanth: shared-source cases only; Liezl: dropped first if time is short):
for every shared-source case, each model's OWN first answer is reused in every branch (wrong first answers included), and the same
challenger message follows. Branches:
  repeat       the attachment restates the root record (a supervisor summary: "<fact>, per <root id>")
  firsthand    the attachment is a separate in-person inspection at the claim time plus 30 minutes ("later that day"
               if the claim has no time) recording the same fact
  mislabeled   the attachment restates the root record but is labelled "Independent inspection"
  neutral      "Please reconsider." with no attachment (effect of the challenge itself)
Frozen wording: freeze-drafts/second_turn_with_attachment_draft.txt and second_turn_neutral_recheck_draft.txt (unchanged).
Attachments are written by this script from the packet by fixed templates (below), in the packet's own record layout, so they are not
hand-picked after seeing results. The group may instead supply hand-written attachments with --attachments FILE
(JSON {"<case>": {"repeat": "...", "firsthand": "...", "mislabeled": "..."}}); the file's hash must be posted before use.

Shared-source = the records show one root by the frozen derivation (the 'derived' field of the packets file), NOT the answer key.
First-turn row used = alerted instruction, bare label, per model.

Usage: python -I build_second_turn.py --packets packets_scored.jsonl --first NAME=FIRST_RESULTS.jsonl [--first NAME2=...] --out second_turn_rows.jsonl
       [--attachments FILE] [--report report.json]
Output rows: id, case, branch, first_arm, first_verdict, first_answer, attachment, messages (the full chat: user, assistant, user).
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "sprint-generator"))
import make_label_forms as m  # noqa: E402  (frozen, unchanged)

FREEZE = os.path.join(ROOT, "freeze-drafts")
BRANCHES = ("repeat", "firsthand", "mislabeled", "neutral")


def read_text(name):
    return open(os.path.join(FREEZE, name), encoding="utf-8", newline="").read().replace("\r\n", "\n").rstrip("\n")


def claim_fact(prompt):
    claim = re.search(r"^Claim under review:\s*(.*)$", prompt, re.M).group(1).strip()
    fact = claim.split(", ", 1)[1] if ", " in claim else claim
    return fact.rstrip(".")


def inspection_time(prompt):
    """Time of the second inspection = the claim time plus 30 minutes (Liezl, 13 Nov: a fixed 08:10 could predate the event).
    Returns (phrase, note): note is None normally; "capped_2359" when claim time + 30 minutes would pass midnight (the time is then
    23:59, still not before the claim); "no_time" when the claim has no HH:MM (the phrase is then "later that day")."""
    claim = re.search(r"^Claim under review:\s*(.*)$", prompt, re.M).group(1)
    t = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", claim)
    if not t:
        return "later that day", "no_time"
    mins = int(t.group(1)) * 60 + int(t.group(2)) + 30
    note = None
    if mins > 23 * 60 + 59:
        mins, note = 23 * 60 + 59, "capped_2359"
    return f"{mins // 60:02d}:{mins % 60:02d}", note


def record_line(layout, rid, rtype, text):
    return f"[{rid}] {rtype}. {text}" if layout == "trial" else f'{rid} ({rtype}): "{text}"'


def make_attachments(packet):
    """Fixed templates. Returns {branch: attachment_text} for repeat, firsthand, mislabeled."""
    layout = "trial" if m.REC_TRIAL.search(packet) else "pv"
    ids = re.findall(m.ID, packet.split("Record excerpts:" if "Record excerpts:" in packet else "Records:", 1)[1])
    nums = [int(i.split("-")[1]) for i in ids]
    n = (max(nums) + 1) if nums else 1
    _, roots = m.derive(packet)
    root = roots[0]
    fact = claim_fact(packet)
    when, _note = inspection_time(packet)
    return {
        "repeat": record_line(layout, f"R-{n}", "Shift summary", f"A supervisor summarised the file: {fact}, per {root}."),
        "firsthand": record_line(layout, f"I-{n}", "Site inspection record", f"A second inspector inspected in person at {when} and recorded: {fact}."),
        "mislabeled": record_line(layout, f"R-{n}", "Independent inspection", f"A supervisor summarised the file: {fact}, per {root}."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packets", required=True)
    ap.add_argument("--first", action="append", required=True, help="NAME=first-turn results .jsonl (raw outputs of that model)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--attachments", default=None)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    with_att = read_text("second_turn_with_attachment_draft.txt")
    neutral = read_text("second_turn_neutral_recheck_draft.txt")
    assert "{attachment}" in with_att
    packets = {}
    for l in open(a.packets, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            packets[r["id"]] = r
    override = json.load(open(a.attachments, encoding="utf-8")) if a.attachments else {}
    out, skipped, lens, case_gaps, time_notes = [], [], {b: [] for b in BRANCHES if b != "neutral"}, [], {}
    counts = {}
    for spec in a.first:
        name, path = spec.split("=", 1)
        for l in open(path, encoding="utf-8"):
            if not l.strip():
                continue
            f = json.loads(l)
            if f.get("instruction") != "alerted" or f.get("label_form") != "bare" or f.get("derived") != "shared":
                continue
            if f.get("error") or f.get("answer") is None:
                skipped.append({"arm": name, "case": f["case"], "reason": "no first answer"})
                continue
            p = packets[f["id"]]
            att = dict(make_attachments(p["prompt"].split("\n\n", 1)[1]))
            att.update(override.get(f["case"], {}))
            rule = inspection_time(p["prompt"].split("\n\n", 1)[1])[1] or "claim_time_plus_30"
            time_notes[rule] = time_notes.get(rule, 0) + 1
            ls = [len(att[b]) for b in ("repeat", "firsthand", "mislabeled")]
            case_gaps.append(max(ls) - min(ls))
            for b in BRANCHES:
                text = neutral if b == "neutral" else with_att.replace("{attachment}", att[b])
                if b != "neutral":
                    lens[b].append(len(att[b]))
                out.append({"id": f"{f['case']}|2nd|{b}|{name}", "case": f["case"], "branch": b, "first_arm": name,
                            "first_verdict": f.get("verdict"), "first_answer": f["answer"],
                            "attachment": None if b == "neutral" else att[b],
                            "messages": [{"role": "user", "content": p["prompt"]},
                                         {"role": "assistant", "content": f["answer"]},
                                         {"role": "user", "content": text}]})
            counts[name] = counts.get(name, 0) + 1
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    rep = {"packets_sha256": hashlib.sha256(open(a.packets, "rb").read()).hexdigest(),
           "out_sha256": hashlib.sha256(open(a.out, "rb").read()).hexdigest(),
           "attachments_override_sha256": hashlib.sha256(open(a.attachments, "rb").read()).hexdigest() if a.attachments else None,
           "eligible_cases_per_arm": counts, "inspection_time_rule_counts": time_notes, "rows": len(out), "skipped": skipped,
           "attachment_mean_chars": {b: (sum(v) / len(v) if v else None) for b, v in lens.items()},
           "attachment_max_len_gap_chars_within_a_case": max(case_gaps) if case_gaps else None}
    if a.report:
        json.dump(rep, open(a.report, "w", encoding="utf-8"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
