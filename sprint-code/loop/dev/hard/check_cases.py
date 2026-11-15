"""Hard set: mechanical checker (exploratory hard set, 15 Nov 2026).

check(packet, skeleton) -> list of failure strings (empty = pass). Checks, per notes/hard-set-spec.md:
- the solver's answer from the packet text equals the skeleton key (F7: verdict only, since its key has no roots);
- every skeleton ID appears as a supplied record, missing IDs are named but not supplied, no extra records;
- the citation edges in the text equal the skeleton's edges exactly (no extra, none missing), reports included;
- banned words ("independ", "same source", "separate", "corroborat") appear only in the Handoff note, except that in F8
  the trap record (and only it) must contain "independently";
- reports under 30 words each (without the "(see X)." tail), record texts under 40 words;
- the packet layout parses (every record line matches  ID (type): "text").
Usage as a script: python -I check_cases.py  (checks cases.jsonl against skeletons.json, prints a summary)
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


def check(packet, sk):
    fails = []
    ans, info = solver.solve(packet)
    p = info["parsed"]
    if p["bad_lines"]:
        fails.append(f"unparsed record lines: {p['bad_lines']}")
    if not p["claim"] or set(p["reports"]) != {"1", "2"} or p["label"] is None:
        fails.append("layout: claim, two reports and handoff note required")
    key = sk["key"]
    if ans["verdict"] != key["verdict"]:
        fails.append(f"solver verdict {ans['verdict']} != key {key['verdict']}")
    elif sk["family"] != "F7" and sorted(ans["root_records"]) != sorted(key["root_records"]):
        fails.append(f"solver roots {ans['root_records']} != key {key['root_records']}")
    want_ids = {r["id"] for r in sk["records"]}
    got_ids = set(p["records"])
    if got_ids != want_ids:
        fails.append(f"record IDs differ: missing {sorted(want_ids - got_ids)}, extra {sorted(got_ids - want_ids)}")
    want_edges = {r["id"]: sorted(r["cites"]) for r in sk["records"]}
    for rid, e in info["edges"].items():
        if rid in want_edges and e != want_edges[rid]:
            fails.append(f"edges of {rid}: text {e} != skeleton {want_edges[rid]}")
    rc = info["report_cites"]
    if rc.get("1") != [sk["report1_cites"]] or rc.get("2") != [sk["report2_cites"]]:
        fails.append(f"report cites {rc} != skeleton {sk['report1_cites']}, {sk['report2_cites']}")
    for k, t in p["reports"].items():
        body = re.sub(r"\s*\(see [^)]*\)\.?$", "", t)
        if solver.ID_RE.search(body):
            fails.append(f"report {k} names an ID outside its (see) part")
        if words(body) >= 30:
            fails.append(f"report {k} has {words(body)} words")
        if BANNED.search(t):
            fails.append(f"banned word in report {k}")
    if BANNED.search(p["claim"] or ""):
        fails.append("banned word in claim")
    trap = {r["id"] for r in sk["records"] if r["role"] == "trap"}
    for rid, r in p["records"].items():
        if words(r["text"]) >= 40:
            fails.append(f"record {rid} has {words(r['text'])} words")
        hits = BANNED.findall(r["text"]) + BANNED.findall(r["type"])
        if rid in trap:
            if "independently" not in r["text"].lower():
                fails.append(f"F8 trap record {rid} lacks 'independently'")
            if [h for h in hits if h.lower() != "independ"] or BANNED.search(r["type"]):
                fails.append(f"banned word beyond the trap in {rid}")
        elif hits:
            fails.append(f"banned word in record {rid}: {hits}")
    return fails


def main():
    sk = {s["case"]: s for s in json.load(open(os.path.join(HERE, "skeletons.json"), encoding="utf-8"))}
    rows = [json.loads(l) for l in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8") if l.strip()]
    bad = 0
    for r in rows:
        f = check(r["packet"], sk[r["case"]])
        if f:
            bad += 1
            print(r["case"], f)
    print(f"{len(rows)} cases, {bad} failing")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
