"""Pick a stratified 20-case sample from train and write review data for review.html."""
import json, random, sys, os
D = sys.argv[1]
rows = [json.loads(l) for l in open(os.path.join(D, "data", "train_meta.jsonl"), encoding="utf-8")]
r = random.Random(7)
want = [("consistent","independent",3),("consistent","shared",3),("contradiction","independent",3),
        ("contradiction","shared",3),("incomplete","undetermined",4),("label_only","undetermined",4)]
pick = []
for cond, truth, n in want:
    pool = [x for x in rows if x["meta"]["condition"] == cond and x["meta"]["truth"] == truth]
    pick += r.sample(pool, n)
r.shuffle(pick)
out = []
for k, x in enumerate(pick, 1):
    m = x["meta"]; recs = {q["id"]: q for q in m["records"]}
    p = x["prompt"].split("\n\n", 1)[1]
    import re
    trails = []
    for i, rep in enumerate(m["reports"], 1):
        cite = re.findall(r"([A-Z]-\d+)", rep)[-1]
        steps = [cite]; c = cite
        while c in recs and not recs[c]["firsthand"] and recs[c]["cites"]:
            c = recs[c]["cites"]; steps.append(c)
        end = "firsthand" if c in recs and recs[c]["firsthand"] else ("no excerpt shown" if not recs else "dead end: no source")
        trails.append({"report": i, "steps": steps, "end": end})
    out.append({"n": k, "train_idx": x["idx"], "packet": p, "answer": json.loads(x["completion"]),
                "condition": m["condition"], "label": m["label"], "wording": m["wording"], "overlap": m.get("overlap"), "trails": trails})
open(os.path.join(D, "review_data.js"), "w", encoding="utf-8").write("window.REVIEW = " + json.dumps(out, indent=1) + ";\n")
print(len(out), "cases")
tpl = open(os.path.join(D, "review_template.html"), encoding="utf-8").read()
data = open(os.path.join(D, "review_data.js"), encoding="utf-8").read().replace("</", "<" + chr(92) + "/")
open(os.path.join(D, "review.html"), "w", encoding="utf-8").write(tpl.replace('<script src="review_data.js"></script>', "<script>" + data + "</script>"))
os.remove(os.path.join(D, "review_data.js"))
print("wrote review.html")
