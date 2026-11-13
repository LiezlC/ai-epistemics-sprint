"""Overlap check between Prashanth's variants and the sprint training files (sprint code, 13 Nov 2026). No key, no rubric.

Same idea as the trial's measured-overlap check (training-trial/check_cases.py, Liezl, 11 Nov 2026), written for hand-written variants:
it reports (a) which of the training files' site names appear anywhere in a variant, (b) record-ID numbers that also occur in the training
files (same number, any letter, and same exact ID), (c) packets that equal a training packet exactly. Overlap is reported, not judged:
hand-written variants may legitimately reuse a site name; the group decides what to do. The record-number range of the sprint training
files is 10000 to 14999, so variant IDs in that range are listed separately.

Usage: python -I check_variants_overlap.py --variants FILE --training train_dpo.jsonl [--report overlap_report.json]
  FILE: .jsonl (key "prompt") or .txt/.md (packets start at each "Claim under review:" line)
  --training: the training DPO or SFT jsonl (key "prompt"; the instruction block is ignored)
Exit code 0 when there is no overlap of any kind, 1 otherwise (so a script can stop and ask).
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sprint-generator"))
import make_label_forms as m  # noqa: E402  (frozen, unchanged)
import gen_sprint_cases as g  # noqa: E402  (frozen, unchanged: the site list)

ID_LO, ID_HI = g.ID_LO, g.ID_HI


def packet_of(prompt):
    i = prompt.find("Claim under review:")
    return prompt[i:] if i >= 0 else prompt


def ids_of(text):
    return re.findall(m.ID, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--training", required=True)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()

    _, container, packets = m.read_packets(a.variants)
    train_packets, train_nums, train_ids = set(), set(), set()
    for l in open(a.training, encoding="utf-8"):
        if not l.strip():
            continue
        p = packet_of(json.loads(l)["prompt"])
        train_packets.add(hashlib.sha256(p.encode()).hexdigest())
        for i in ids_of(p):
            train_ids.add(i)
            train_nums.add(i.split("-")[1])

    site_hits, id_hits, num_hits, in_range, dup = [], [], [], [], []
    for k, p in enumerate(packets):
        txt = p if isinstance(p, str) else str(p)
        sites = [s for s in g.SITES if s.lower() in txt.lower()]
        if sites:
            site_hits.append({"index": k, "sites": sites})
        ids = sorted(set(ids_of(txt)))
        same_id = [i for i in ids if i in train_ids]
        same_num = [i for i in ids if i.split("-")[1] in train_nums and i not in same_id]
        rng = [i for i in ids if i.split("-")[1].isdigit() and ID_LO <= int(i.split("-")[1]) <= ID_HI]
        if same_id:
            id_hits.append({"index": k, "ids": same_id})
        if same_num:
            num_hits.append({"index": k, "ids": same_num})
        if rng:
            in_range.append({"index": k, "ids": rng})
        if hashlib.sha256(packet_of(txt).encode()).hexdigest() in train_packets:
            dup.append(k)
    rep = {"variants_sha256": hashlib.sha256(open(a.variants, "rb").read()).hexdigest(),
           "training_sha256": hashlib.sha256(open(a.training, "rb").read()).hexdigest(),
           "packets_checked": len(packets), "training_site_names_checked": len(g.SITES),
           "packets_with_a_training_site_name": len(site_hits), "sites_detail": site_hits,
           "packets_sharing_an_exact_record_id": len(id_hits), "exact_id_detail": id_hits,
           "packets_sharing_only_a_record_number": len(num_hits), "number_detail": num_hits,
           "packets_with_ids_in_the_training_range_10000_14999": len(in_range), "range_detail": in_range,
           "packets_identical_to_a_training_packet": len(dup), "identical_detail": dup}
    if a.report:
        json.dump(rep, open(a.report, "w", encoding="utf-8"), indent=1)
    for k in ("packets_checked", "packets_with_a_training_site_name", "packets_sharing_an_exact_record_id",
              "packets_sharing_only_a_record_number", "packets_with_ids_in_the_training_range_10000_14999",
              "packets_identical_to_a_training_packet"):
        print(f"{k:55} {rep[k]}")
    overlap = any(rep[k] for k in ("packets_with_a_training_site_name", "packets_sharing_an_exact_record_id",
                                   "packets_sharing_only_a_record_number", "packets_identical_to_a_training_packet"))
    print("OVERLAP FOUND (report it to the group; do not drop anything silently)" if overlap else "no overlap of any kind")
    sys.exit(1 if overlap else 0)


if __name__ == "__main__":
    main()
