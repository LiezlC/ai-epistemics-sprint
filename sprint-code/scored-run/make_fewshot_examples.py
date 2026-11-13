"""Make the three-shot examples file for the untuned 4B comparison arm (sprint code, 13 Nov 2026).

Rule = the trial's rule, unchanged (training-trial/eval_modal.py, Liezl, 11 Nov 2026): for each verdict in the order independent,
shared, undetermined, take the FIRST training case of the sprint training set whose condition is not label_only. The cases are
generated training cases, so none belongs to the scored set; the examples use the trial (alerted) instruction text and the trial
JSON answer. Label forms in the examples are the training set's own: bare and authority-stamped only.

Usage: python -I make_fewshot_examples.py TRAIN_META.jsonl OUT.json
The completion is the row's chosen answer (identical to the supervised completion). TRAIN_META.jsonl is the sprint training meta file (local only; it stays out of the team repo). The output carries the prompt and
completion of each example plus which training row it came from, so the choice can be checked against the training files.
"""
import hashlib
import json
import sys

meta_path, out_path = sys.argv[1:3]
meta = [json.loads(l) for l in open(meta_path, encoding="utf-8")]
shots = []
for want in ("independent", "shared", "undetermined"):
    x = next(m for m in meta if m["meta"]["truth"] == want and m["meta"]["condition"] != "label_only")
    mt = x["meta"]
    shots.append({"verdict": want, "train_row": x["idx"], "condition": mt["condition"], "label": mt["label"],
                  "label_form": mt["label_form"], "prompt": x["prompt"], "completion": x["chosen"]})
doc = {"rule": "first training case per verdict (independent, shared, undetermined), condition not label_only; trial rule unchanged",
       "source_meta_sha256": hashlib.sha256(open(meta_path, "rb").read()).hexdigest(),
       "applies_to": "alerted-instruction packets only (the examples carry the alerted instruction text)",
       "shots": shots}
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print(out_path, hashlib.sha256(open(out_path, "rb").read()).hexdigest())
for s in shots:
    print(s["verdict"], "row", s["train_row"], s["condition"], "label", s["label"], s["label_form"])
