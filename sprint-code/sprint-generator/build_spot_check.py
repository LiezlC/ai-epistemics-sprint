"""Build a 20-case spot-check sheet for the sprint training files (13 Nov 2026).

SPRINT CODE derived from the PREEXISTING `training-trial/build_review.py` and `review_template.html`
(Liezl, 11 Nov 2026). The HTML template is Liezl's; this script only fills it with new data and changes
the storage key, the download file name and the title so the two sheets do not clash.

Sample: stratified like the trial (3 consistent independent, 3 consistent shared, 3 false-shared-label
contradictions, 3 false-independent-label contradictions, 4 incomplete, 4 label-only), seed 20261113.
Each case also shows the label form and the REJECTED answer of its DPO pair after the packet.

Usage: python -I build_spot_check.py META_JSONL TEMPLATE_HTML OUT_HTML [KEY_SUFFIX]
KEY_SUFFIX (added 13 Nov after Liezl found the first two sheets shared a storage key and download name) gives each sheet its own
storage key and download file name; use a different suffix for every sheet, e.g. extra.
"""
import json
import random
import re
import sys

meta_path, tpl_path, out_path = sys.argv[1:4]
suffix = sys.argv[4] if len(sys.argv) > 4 else ""
rows = [json.loads(l) for l in open(meta_path, encoding="utf-8")]
r = random.Random(20261113)
want = [("consistent", "independent", 3), ("consistent", "shared", 3), ("contradiction", "independent", 3),
        ("contradiction", "shared", 3), ("incomplete", "undetermined", 4), ("label_only", "undetermined", 4)]
pick = []
for cond, truth, n in want:
    pool = [x for x in rows if x["meta"]["condition"] == cond and x["meta"]["truth"] == truth]
    pick += r.sample(pool, n)
r.shuffle(pick)

out = []
for k, x in enumerate(pick, 1):
    m = x["meta"]
    recs = {q["id"]: q for q in m["records"]}
    p = x["prompt"].split("\n\n", 1)[1]
    p += "\n\n(For the check only, not shown to the model) Rejected answer in the DPO pair: " + x["rejected"]
    trails = []
    for i, rep in enumerate(m["reports"], 1):
        cite = re.findall(r"([A-Z]-\d+)", rep)[-1]
        steps = [cite]
        c = cite
        while c in recs and not recs[c]["firsthand"] and recs[c]["cites"]:
            c = recs[c]["cites"]
            steps.append(c)
        end = "firsthand" if c in recs and recs[c]["firsthand"] else ("no excerpt shown" if not recs else "dead end: no source")
        trails.append({"report": i, "steps": steps, "end": end})
    out.append({"n": k, "train_idx": x["idx"], "packet": p, "answer": json.loads(x["chosen"]),
                "condition": m["condition"], "label": m["label"],
                "wording": f"{m['wording']}, label form {m['label_form']}", "overlap": m.get("overlap") or 0,
                "trails": trails})

tpl = open(tpl_path, encoding="utf-8").read()
data = ("window.REVIEW = " + json.dumps(out, indent=1) + ";").replace("</", "<" + chr(92) + "/")
html = tpl.replace('<script src="review_data.js"></script>', "<script>" + data + "</script>")
assert html != tpl, "template placeholder not found"
html = html.replace('KEY = "case-check-v1"', 'KEY = "case-check-sprint-v1' + ("-" + suffix if suffix else "") + '"')
html = html.replace('l.download = "case-check-results.json"', 'l.download = "sprint-case-check-results' + ("-" + suffix if suffix else "") + '.json"')
html = html.replace("<title>Case Check</title>", "<title>Sprint Case Check</title>")
html = html.replace("<!doctype html>", "<!doctype html>\n<!-- Sprint copy of the preexisting trial review template (Liezl, 11 Nov 2026); data and storage key changed 13 Nov 2026. -->", 1)
open(out_path, "w", encoding="utf-8", newline="\n").write(html)
print(len(out), "cases ->", out_path)
from collections import Counter
print(Counter((o["condition"], o["answer"]["verdict"]) for o in out))
