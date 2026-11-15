"""Gap set: mechanical solver (exploratory, 15 Nov 2026). Adapted from hard-set/solver.py (same layout and parse).

Reads a finished packet TEXT plus the case's list of person names, and re-derives the answer:
- edges: each report cites the IDs in its "(see X)" part; every ID named inside a record's text is an edge;
- an end record (names no other ID) counts as a FIRSTHAND ROOT only if its text names exactly one listed person and
  carries no hearsay or relay marker (HEARSAY below). Any other end record leaves that path unsettled;
- if any path from either report reaches an ID that is not supplied, or an end record that is not a firsthand root,
  the records cannot settle the question: undetermined, roots [];
- otherwise shared if the two reports' root sets meet, else independent (roots = the union).
"""
import re

ID_RE = re.compile(r"\b[A-Z]{1,4}-\d+\b")
REC_RE = re.compile(r'^([A-Z]{1,4}-\d+) \(([^)]*)\): "(.*)"$')
HEARSAY = re.compile(r"\b(told|heard|hearsay|passed on|according to|relayed|copied|taken from|word came|reportedly)\b", re.I)


def parse(packet):
    out = {"claim": None, "reports": {}, "label": None, "records": {}, "bad_lines": []}
    in_recs = False
    for ln in packet.split("\n"):
        if ln.startswith("Claim under review: "):
            out["claim"] = ln[len("Claim under review: "):]
        elif ln.startswith("Report 1. ") or ln.startswith("Report 2. "):
            out["reports"][ln[7]] = ln[10:]
        elif ln.startswith("Handoff note: "):
            out["label"] = ln[len("Handoff note: "):]
        elif ln == "Records:":
            in_recs = True
        elif in_recs and ln.strip():
            m = REC_RE.match(ln)
            if not m:
                out["bad_lines"].append(ln)
                continue
            out["records"][m.group(1)] = {"type": m.group(2), "text": m.group(3)}
    return out


def edges(p):
    e = {rid: sorted(set(ID_RE.findall(r["text"])) - {rid}) for rid, r in p["records"].items()}
    rep = {}
    for k, t in p["reports"].items():
        m = re.search(r"\(see ([^)]*)\)\.?$", t)
        rep[k] = sorted(set(ID_RE.findall(m.group(1)))) if m else []
    return rep, e


def firsthand(rec, names):
    t = rec["type"] + " " + rec["text"]
    return sum(n in t for n in names) == 1 and not HEARSAY.search(t)


def solve(packet, names):
    p = parse(packet)
    rep, e = edges(p)

    def roots_of(start):
        seen, roots, broken, stack = set(), set(), False, list(start)
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            if x not in p["records"]:
                broken = True
                continue
            if not e[x]:
                if firsthand(p["records"][x], names):
                    roots.add(x)
                else:
                    broken = True
            stack.extend(e[x])
        return roots, broken, seen

    r1, b1, s1 = roots_of(rep.get("1", []))
    r2, b2, s2 = roots_of(rep.get("2", []))
    if b1 or b2 or not r1 or not r2:
        ans = {"verdict": "undetermined", "root_records": []}
    elif r1 & r2:
        ans = {"verdict": "shared", "root_records": sorted(r1 | r2)}
    else:
        ans = {"verdict": "independent", "root_records": sorted(r1 | r2)}
    return ans, {"parsed": p, "report_cites": rep, "edges": e, "reached": sorted(s1 | s2)}
