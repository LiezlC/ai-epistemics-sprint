"""Re-derive every answer from the visible packet text alone and compare to the stored answer."""
import json, re, sys
bad = 0
for path in sys.argv[1:]:
    for line in open(path, encoding="utf-8"):
        row = json.loads(line); p = row["prompt"]; ans = json.loads(row["completion"])
        recs = {}
        for m in re.finditer(r"^\[([A-Z]-\d+)\] ([^.]+)\. (.*)$", p, re.M):
            rid, typ, text = m.groups()
            first = rid[0] in "GCISM"
            cite = re.search(r"(?:per|in|Minutes by [^:]+: )\s*([A-Z]-\d+)", text)
            cites = re.findall(r"\b([A-Z]-\d+)\b", text)
            recs[rid] = (first, cites[0] if cites and not first else None)
        reps = [re.findall(r"\b([A-Z]-\d+)\b", line)[0] for line in re.findall(r"^Report \d\. .*$", p, re.M)]
        if "No record excerpts" in p:
            exp = ("undetermined", [])
        else:
            roots = []
            for c in reps:
                seen = 0
                while c in recs and not recs[c][0] and recs[c][1] and seen < 5:
                    c = recs[c][1]; seen += 1
                roots.append(c if c in recs and recs[c][0] else None)
            if None in roots: exp = ("undetermined", [])
            elif roots[0] == roots[1]: exp = ("shared", [roots[0]])
            else: exp = ("independent", sorted(roots))
        got = (ans["verdict"], sorted(ans["root_records"]))
        if got != exp:
            bad += 1
            if bad <= 3: print("MISMATCH", path.split("/")[-1], got, exp, reps)
    print(path.split("/")[-1], "checked")
print("mismatches:", bad)
