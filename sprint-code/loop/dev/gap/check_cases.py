"""Gap set: mechanical checker (exploratory, 15 Nov 2026). Adapted from hard-set/check_cases.py.

check(packet, sk, version) -> list of failures (empty = pass); version is "control" or "gap". Checks:
- solver answer from the text equals the key (control: verdict and roots; gap: undetermined);
- supplied record IDs and citation edges equal the skeleton's (gap G1: record M absent but still cited; gap G5: R1 cites
  nothing), report citations included;
- banned words ("independ", "same source", "separate", "corroborat") nowhere except the Handoff note;
- reports under 30 words (without the "(see X)." tail), record texts under 40 words, layout parses;
- names: claim, reports and relays name no listed person; each control root names its own observer only, with no
  hearsay marker; the gap record carries its gap: G2 no listed person; G3 "told" plus its observer only; G4 both
  observers and no hearsay marker; G5 "passed on", no listed person, no ID.
Usage: python -I check_cases.py   (checks cases.jsonl against skeletons.json)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solver  # noqa: E402

BANNED = re.compile(r"independ|same source|separate|corroborat", re.I)


def words(t):
    return len(t.split())


def expected(sk, version):
    recs = {r["id"]: sorted(r["cites"]) for r in sk["records"]}
    if version == "gap":
        if sk["gap_type"] == "G1":
            del recs[sk["target"]]
        if sk["gap_type"] == "G5":
            recs[sk["target"]] = []
    return recs


def check(packet, sk, version):
    fails = []
    names = sk["names"]
    ans, info = solver.solve(packet, names)
    p = info["parsed"]
    if p["bad_lines"]:
        fails.append(f"unparsed record lines: {p['bad_lines']}")
    if not p["claim"] or set(p["reports"]) != {"1", "2"} or p["label"] is None:
        fails.append("layout: claim, two reports and handoff note required")
    key = sk["key_control"] if version == "control" else sk["key_gap"]
    if ans["verdict"] != key["verdict"] or sorted(ans["root_records"]) != sorted(key["root_records"]):
        fails.append(f"{version}: solver {ans} != key {key}")
    want = expected(sk, version)
    if set(p["records"]) != set(want):
        fails.append(f"{version}: record IDs differ: missing {sorted(set(want) - set(p['records']))}, "
                     f"extra {sorted(set(p['records']) - set(want))}")
    for rid, e in info["edges"].items():
        if rid in want and e != want[rid]:
            fails.append(f"{version}: edges of {rid}: text {e} != skeleton {want[rid]}")
    rc = info["report_cites"]
    if rc.get("1") != [sk["report1_cites"]] or rc.get("2") != [sk["report2_cites"]]:
        fails.append(f"report cites {rc} != skeleton")
    for k, t in p["reports"].items():
        body = re.sub(r"\s*\(see [^)]*\)\.?$", "", t)
        if solver.ID_RE.search(body):
            fails.append(f"report {k} names an ID outside its (see) part")
        if words(body) >= 30:
            fails.append(f"report {k} has {words(body)} words")
        if BANNED.search(t):
            fails.append(f"banned word in report {k}")
        if any(n in t for n in names):
            fails.append(f"report {k} names a listed person")
    if BANNED.search(p["claim"] or "") or any(n in (p["claim"] or "") for n in names):
        fails.append("banned word or listed person in claim")
    roles = {r["id"]: r for r in sk["records"]}
    for rid, r in p["records"].items():
        full = r["type"] + " " + r["text"]
        if words(r["text"]) >= 40:
            fails.append(f"record {rid} has {words(r['text'])} words")
        if BANNED.search(full):
            fails.append(f"banned word in record {rid}")
        if rid not in roles:
            continue
        has = [n for n in names if n in full]
        is_gap = version == "gap" and rid == sk["target"]
        if is_gap:
            gt = sk["gap_type"]
            obs = roles[rid].get("observer")
            if gt == "G2" and has:
                fails.append(f"G2 gap record {rid} names {has}")
            if gt == "G3" and (not re.search(r"\btold\b", full, re.I) or has != [obs]):
                fails.append(f"G3 gap record {rid} needs 'told' and only {obs} (has {has})")
            if gt == "G4" and (sorted(has) != sorted(names) or solver.HEARSAY.search(full)):
                fails.append(f"G4 gap record {rid} must name both observers, no hearsay marker (has {has})")
            if gt == "G5" and (not re.search(r"passed on", full, re.I) or has or solver.ID_RE.search(r["text"])):
                fails.append(f"G5 gap record {rid} needs 'passed on', no listed person, no ID")
        elif roles[rid]["role"] == "root":
            if has != [roles[rid]["observer"]] or solver.HEARSAY.search(full):
                fails.append(f"root {rid} must name only {roles[rid]['observer']} with no hearsay marker (has {has})")
        elif has:
            fails.append(f"relay {rid} names a listed person {has}")
    return fails


def main():
    sk = {s["bundle"]: s for s in json.load(open(os.path.join(HERE, "skeletons.json"), encoding="utf-8"))}
    rows = [json.loads(l) for l in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8") if l.strip()]
    bad = 0
    for r in rows:
        f = check(r["packet"], sk[r["bundle"]], r["version"])
        if f:
            bad += 1
            print(r["case"], f)
    print(f"{len(rows)} cases, {bad} failing")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
