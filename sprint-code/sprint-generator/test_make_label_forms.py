"""Self-test for make_label_forms.py on GENERATED cases only (never on Prashanth's variants).

Usage: python -I test_make_label_forms.py
Builds 1,000 sprint training-style cases, swaps every handoff line to the bare form, runs the
transformation, and checks the outputs. Sprint code, written 13 Nov 2026.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_sprint_cases as g
import make_label_forms as m

templates = json.load(open(os.path.join(HERE, "label_form_templates.json"), encoding="utf-8"))
rows = g.Gen(777, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(1000, 100, 100)

tmp = tempfile.mkdtemp()
src = os.path.join(tmp, "bare_cases.jsonl")
expect_mis = 0
with open(src, "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        meta = r["meta"]
        p = r["prompt"]
        line = re.search(r"^Handoff note:.*$", p, re.M).group(0)
        bare = templates["bare_lines"][meta["label"]]
        p = p.replace(line, bare, 1)
        if (meta["label"] == "independent" and meta["underlying"] == "shared" and meta["condition"] != "label_only"
                and m.report_ids(p)[0] != m.report_ids(p)[1]):
            expect_mis += 1
        f.write(json.dumps({"prompt": p, "idx": meta["claim"]}) + "\n")

out = os.path.join(tmp, "out")
res = subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_label_forms.py"), "--in", src, "--out-dir", out],
                     capture_output=True, text=True)
print(res.stdout)
fails = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


check(res.returncode == 0, "script exits 0 (nothing skipped)")
bare = [json.loads(l) for l in open(os.path.join(out, "bare_cases.bare.jsonl"), encoding="utf-8")]
stamped = [json.loads(l) for l in open(os.path.join(out, "bare_cases.stamped.jsonl"), encoding="utf-8")]
mis = [json.loads(l) for l in open(os.path.join(out, "bare_cases.misleading.jsonl"), encoding="utf-8")]
check(len(bare) == len(stamped) == 1000, f"bare and stamped cover all 1000 packets ({len(bare)}, {len(stamped)})")
none = [json.loads(l) for l in open(os.path.join(out, "bare_cases.none.jsonl"), encoding="utf-8")]
check(len(none) == 1000 and all("Handoff note:" not in x["prompt"] for x in none), "no-label form: every packet, handoff line gone")
def squash(p):
    return re.sub(r"\n{2,}", "\n\n", re.sub(r"^Handoff note:.*$", "", p, flags=re.M))
check(all(squash(b["prompt"]) == squash(n["prompt"]) and "\n\n\n" not in n["prompt"] for b, n in zip(bare, none)),
      "no-label form: nothing else changed, no triple newline left")
check(all(x["label_form"] == "none" for x in none), "no-label rows are tagged label_form=none")
check(len(mis) == expect_mis, f"misleading made exactly where expected: {len(mis)} vs {expect_mis}")

# Only the handoff line changes
def mask(p):
    return re.sub(r"^Handoff note:.*$", "H", p, flags=re.M)

same_other = all(mask(b["prompt"]) == mask(s["prompt"]) for b, s in zip(bare, stamped))
check(same_other, "stamped packets differ from bare only in the handoff line")
ok_stamp = all(re.search(r"^Handoff note:.*$", s["prompt"], re.M).group(0) in templates["stamped_lines"].values() for s in stamped)
check(ok_stamp, "every stamped line equals a stamped template")

# Misleading lists the right IDs and the packet is a shared-root packet
bad = 0
for r in mis:
    p = r["prompt"]
    line = re.search(r"^Handoff note:.*$", p, re.M).group(0)
    id1, id2 = m.report_ids(p)
    if line != templates["misleading_line"].format(id1=id1, id2=id2) or id1 == id2:
        bad += 1
    if m.derive(p)[0] != "shared":
        bad += 1
check(bad == 0, f"misleading lines list each report's own cited ID and sit on shared-root packets: {bad} bad")
check(all(r["label_form"] == "misleading" for r in mis), "misleading rows are tagged label_form=misleading")

# Prashanth's record layout (13 Nov): "ID (type): "text"" instead of "[ID] Type. text"
def to_pv(p):
    return re.sub(r"^\[(%s)\] ([^.]+)\. (.*)$" % m.ID, lambda mm: f'{mm.group(1)} ({mm.group(2)}): "{mm.group(3)}"', p, flags=re.M)

pv_src = os.path.join(tmp, "pv_cases.jsonl")
with open(pv_src, "w", encoding="utf-8", newline="\n") as f:
    for row in bare:
        f.write(json.dumps({"prompt": to_pv(row["prompt"])}) + "\n")
res_pv = subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_label_forms.py"), "--in", pv_src, "--out-dir", os.path.join(tmp, "pv_out")],
                        capture_output=True, text=True)
check(res_pv.returncode == 0, "his layout: script exits 0 (nothing skipped)")
pv_mis = [json.loads(l) for l in open(os.path.join(tmp, "pv_out", "pv_cases.misleading.jsonl"), encoding="utf-8")]
check(len(pv_mis) == expect_mis, f"his layout: misleading made exactly where expected: {len(pv_mis)} vs {expect_mis}")
check(all("(" in x["prompt"] and "[" not in re.search(r"Record excerpts:\n(.*)", x["prompt"]).group(1)[:1] for x in pv_mis),
      "his layout: the record lines keep his format in the output")

# A hand-written bare label that is not one of the templates is classified by words, or skipped when unclear
alt = bare[0]["prompt"]
line0 = re.search(r"^Handoff note:.*$", alt, re.M).group(0)
variants = {"Handoff note: these two reports are independent sources.": "classified",
            "Handoff note: both reports come from the same source.": "classified",
            "Handoff note: something unclear here.": "skipped"}
okv = True
for text, want in variants.items():
    t = alt.replace(line0, text, 1)
    try:
        m.handoff_line(t, templates)
        got = "classified"
    except ValueError:
        got = "skipped"
    okv &= got == want
check(okv, "hand-written bare labels: classified when clear, skipped when unclear")

# A packet it cannot parse is skipped, not guessed
broken = os.path.join(tmp, "broken.jsonl")
with open(broken, "w", encoding="utf-8") as f:
    f.write(json.dumps({"prompt": "Claim under review: At X, a thing.\n\nReport 1. cites nothing\nReport 2. A-1\n\nHandoff note: odd.\n"}) + "\n")
r2 = subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_label_forms.py"), "--in", broken, "--out-dir", os.path.join(tmp, "o2")],
                    capture_output=True, text=True)
check(r2.returncode == 1 and "skipped" in r2.stdout and '"index": 0' in r2.stdout, "an unparseable packet is skipped and reported, not guessed")

print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(0 if not fails else 1)
