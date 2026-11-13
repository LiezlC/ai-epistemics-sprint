"""Checks for the sprint training files (written 13 Nov 2026). Sprint code; the answer re-derivation is
adapted from the preexisting `training-trial/check_cases.py` (Liezl, 11 Nov 2026).

Usage: python -I check_sprint_cases.py DIR [--trial-dir PATH_TO_training-trial/data]
Exit code 0 only if every hard check passes.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter

PEOPLE = ["T. Mokoena", "A. Pillay", "J. van Wyk", "S. Dlamini", "R. Naidoo", "P. Botha",
          "L. Khumalo", "M. Fourie", "N. Zulu", "K. Abrahams", "D. Sithole", "F. Jacobs",
          "B. Nkosi", "H. Petersen", "Z. Mahlangu", "E. Govender"]
NEAR_IDENTICAL, VARIED = 0.8, 0.35


def derive(prompt):
    """Re-derive (verdict, roots) from the visible packet text alone."""
    recs = {}
    for m in re.finditer(r"^\[([A-Z]-\d+)\] ([^.]+)\. (.*)$", prompt, re.M):
        rid, typ, text = m.groups()
        first = rid[0] in "GCISM"
        cites = re.findall(r"\b([A-Z]-\d+)\b", text)
        recs[rid] = (first, cites[0] if cites and not first else None)
    reps = [re.findall(r"\b([A-Z]-\d+)\b", line)[0] for line in re.findall(r"^Report \d\. .*$", prompt, re.M)]
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


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--trial-dir", default=None)
    a = ap.parse_args()
    d = a.dir
    fails = []

    def check(ok, msg):
        print(("PASS  " if ok else "FAIL  ") + msg)
        if not ok:
            fails.append(msg)

    dpo = [json.loads(l) for l in open(os.path.join(d, "train_dpo.jsonl"), encoding="utf-8")]
    sft = [json.loads(l) for l in open(os.path.join(d, "train_sft.jsonl"), encoding="utf-8")]
    meta = [json.loads(l) for l in open(os.path.join(d, "train_meta.jsonl"), encoding="utf-8")]
    check(len(dpo) == len(sft) == len(meta), f"row counts match: dpo {len(dpo)}, sft {len(sft)}, meta {len(meta)}")

    # 1. chosen re-derived from the packet text
    bad = 0
    for i, row in enumerate(dpo):
        ans = json.loads(row["chosen"])
        got = (ans["verdict"], sorted(ans["root_records"]))
        if got != derive(row["prompt"]):
            bad += 1
            if bad <= 3:
                print("   mismatch", i, got, derive(row["prompt"]))
    check(bad == 0, f"chosen answers re-derived from packet text: {bad} mismatches")

    # 2. pairs
    same, roots_diff, unparse = 0, 0, 0
    for row in dpo:
        try:
            c, r = json.loads(row["chosen"]), json.loads(row["rejected"])
            assert set(c) == {"verdict", "root_records"} and set(r) == {"verdict", "root_records"}
        except Exception:
            unparse += 1
            continue
        if row["chosen"] == row["rejected"] or c["verdict"] == r["verdict"]:
            same += 1
        if sorted(c["root_records"]) != sorted(r["root_records"]):
            roots_diff += 1
    check(unparse == 0, f"chosen and rejected are well-formed JSON with the two keys: {unparse} bad")
    check(same == 0, f"rejected differs from chosen in verdict on every pair: {same} violations")
    check(roots_diff == 0, f"rejected keeps the chosen root IDs on every pair: {roots_diff} violations")

    # 3. SFT rows equal the DPO chosen rows
    sft_ok = all(s["prompt"] == p["prompt"] and s["completion"] == p["chosen"] for s, p in zip(sft, dpo))
    check(sft_ok, "supervised file equals the DPO file's prompt and chosen, row by row")

    # 4. label forms
    lines = []
    for row in dpo:
        m = re.search(r"^(Handoff note:.*)$", row["prompt"], re.M)
        lines.append(m.group(1) if m else "")
    check(all(lines), "every packet has exactly one handoff note line")
    check(not any(re.search(r"\bcites?\b|Report \d", l) for l in lines),
          "no literal-but-misleading label form in training (no 'cites' or 'Report n' in any handoff note)")
    forms = Counter(m["meta"]["label_form"] for m in meta)
    print("   label forms:", dict(forms))
    check(set(forms) <= {"bare", "stamped"}, "label forms are only bare and stamped")

    # 5. mix
    print("   truth:", dict(Counter(m["meta"]["truth"] for m in meta)))
    print("   condition:", dict(Counter(m["meta"]["condition"] for m in meta)))
    print("   contradiction by label:", dict(Counter(m["meta"]["label"] for m in meta if m["meta"]["condition"] == "contradiction")))

    # 6. wording bands
    badw = sum(1 for m in meta if (m["meta"]["wording"] == "near_identical" and m["meta"]["overlap"] < NEAR_IDENTICAL)
               or (m["meta"]["wording"] == "varied" and m["meta"]["overlap"] > VARIED))
    check(badw == 0, f"wording overlap inside the target bands: {badw} outside")

    # 7. duplicates, names, instruction block
    check(len({r["prompt"] for r in dpo}) == len(dpo), "no duplicate prompts")
    name_bad = 0
    for row in dpo:
        texts = re.findall(r"^\[[A-Z]-\d+\] .*$", row["prompt"], re.M)
        for p in PEOPLE:
            if sum(1 for t in texts if p in t) > 1:
                name_bad += 1
    check(name_bad == 0, f"no person's name appears in two records of one case: {name_bad} violations")
    heads = {r["prompt"].split("\n\nClaim under review:")[0] for r in dpo}
    check(len(heads) == 1, "one identical instruction block across all rows")

    # 8. no overlap with the trial files
    if a.trial_dir:
        ids, sites = set(), set()
        for fn in ("train.jsonl", "test_a.jsonl"):
            p = os.path.join(a.trial_dir, fn)
            if os.path.exists(p):
                for l in open(p, encoding="utf-8"):
                    pr = json.loads(l)["prompt"]
                    ids |= set(re.findall(r"[A-Z]-(\d+)", pr))
                    sites |= set(re.findall(r"Claim under review: At (.*?), ", pr))
        mine_ids, mine_sites = set(), set()
        for row in dpo:
            mine_ids |= set(re.findall(r"[A-Z]-(\d+)", row["prompt"]))
            mine_sites |= set(re.findall(r"Claim under review: At (.*?), ", row["prompt"]))
        check(not (ids & mine_ids), f"no record number shared with the trial files ({len(ids)} trial numbers): {len(ids & mine_ids)} shared")
        check(not (sites & mine_sites), f"no site name shared with the trial files ({sorted(sites)}): {sorted(sites & mine_sites)} shared")
        print("   training sites used:", sorted(mine_sites))
        print("   record numbers used: min", min(map(int, mine_ids)), "max", max(map(int, mine_ids)))
    else:
        print("   (trial overlap check skipped: pass --trial-dir)")

    # 9. hashes
    for fn in ("train_dpo.jsonl", "train_sft.jsonl", "train_meta.jsonl"):
        p = os.path.join(d, fn)
        print(f"   {fn}: {sum(1 for _ in open(p, encoding='utf-8'))} rows, sha256 {sha(p)}")

    print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
