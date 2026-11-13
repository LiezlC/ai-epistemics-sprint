"""End-to-end test of the scored-run pipeline on GENERATED cases only, no network, no spend (sprint code, 13 Nov 2026).

Builds fake "variants" with bare labels (generator seed 555) in both the trial layout and Prashanth's layout, runs
build_scored_packets.py, runs the OpenRouter runner on the fake model route (the pilot's test double), then score_scored.py
with a key made from the generator's own answers. Never touches Prashanth's variants, a rubric or a real key.
Usage: python -I test_scored_run.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "sprint-generator"))
sys.path.insert(0, os.path.join(ROOT, "pilot"))
import gen_sprint_cases as g  # noqa: E402
import make_label_forms as m  # noqa: E402

T = json.load(open(os.path.join(ROOT, "sprint-generator", "label_form_templates.json"), encoding="utf-8"))
rows = g.Gen(555, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(300, 60, 60)
tmp = tempfile.mkdtemp()
fails = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def to_pv(p):
    return re.sub(r"^\[(%s)\] ([^.]+)\. (.*)$" % m.ID, lambda mm: '%s (%s): "%s"' % (mm.group(1), mm.group(2), mm.group(3)), p, flags=re.M)


def make_variants(path, layout):
    key = {}
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for i, r in enumerate(rows):
            p = r["prompt"].split("\n\n", 1)[1]  # packet without the instruction block
            line = re.search(r"^Handoff note:.*$", p, re.M).group(0)
            p = p.replace(line, T["bare_lines"][r["meta"]["label"]], 1)
            if layout == "pv":
                p = to_pv(p)
            cid = f"c{i:03d}"
            f.write(json.dumps({"id": cid, "prompt": p}) + "\n")
            gold = json.loads(r["chosen"])
            key[cid] = {"verdict": gold["verdict"], "root_records": gold["root_records"]}
    return key


def run(cmd):
    return subprocess.run([sys.executable, "-I"] + cmd, capture_output=True, text=True)


for layout in ("trial", "pv"):
    d = os.path.join(tmp, layout)
    os.makedirs(d)
    var = os.path.join(d, "variants.jsonl")
    key = make_variants(var, layout)
    keyp = os.path.join(d, "key.json")
    json.dump(key, open(keyp, "w"))
    out = os.path.join(d, "packets.jsonl")
    res = run([os.path.join(HERE, "build_scored_packets.py"), "--variants", var, "--out", out, "--report", os.path.join(d, "rep.json")])
    check(res.returncode == 0, f"[{layout}] builder exits 0 (nothing skipped)")
    pk = [json.loads(l) for l in open(out, encoding="utf-8")]
    rep = json.load(open(os.path.join(d, "rep.json")))
    ba = rep["rows_by_arm"]
    n = len(rows)
    check(ba["alerted|bare"] == n and ba["alerted|stamped"] == n and ba["alerted|none"] == n and ba["neutral|none"] == n,
          f"[{layout}] bare, stamped and none arms cover all {n} cases under both prompts")
    check("neutral|misleading" not in ba and 0 < ba["alerted|misleading"] < n, f"[{layout}] misleading only under the alerted prompt, only where expected ({ba['alerted|misleading']})")
    alerted = open(os.path.join(ROOT, "freeze-drafts", "instruction_alerted_trial_wording.txt"), encoding="utf-8", newline="").read().replace("\r\n", "\n").rstrip("\n")
    neutral = open(os.path.join(ROOT, "freeze-drafts", "instruction_neutral_draft.txt"), encoding="utf-8", newline="").read().replace("\r\n", "\n").rstrip("\n")
    check(all(x["prompt"].startswith((alerted if x["instruction"] == "alerted" else neutral) + "\n\nClaim under review:") for x in pk),
          f"[{layout}] every prompt starts with its frozen instruction text then the packet")
    check(all("Handoff note:" not in x["prompt"] for x in pk if x["label_form"] == "none"), f"[{layout}] no-label prompts carry no handoff line")
    check(all(("Handoff note:" in x["prompt"]) for x in pk if x["label_form"] != "none"), f"[{layout}] other forms carry exactly the handoff line")
    check(all(x["prompt"].count("Handoff note:") <= 1 for x in pk), f"[{layout}] never more than one handoff line")
    check(len({x["id"] for x in pk}) == len(pk), f"[{layout}] row ids unique")
    # run on the fake model, then score
    rd = os.path.join(d, "run")
    os.makedirs(rd)
    r2 = run([os.path.join(HERE, "run_scored_openrouter.py"), "--packets", out, "--model", "fake", "--route", "fake", "--out", rd])
    check(r2.returncode == 0 and os.path.exists(os.path.join(rd, "results.jsonl")), f"[{layout}] runner works on the fake route and writes raw outputs")
    res_rows = [json.loads(l) for l in open(os.path.join(rd, "results.jsonl"), encoding="utf-8")]
    check(len(res_rows) == len(pk) and all("truth" not in x for x in res_rows), f"[{layout}] outputs carry no truth field (no key used)")
    r3 = run([os.path.join(HERE, "score_scored.py"), "--key", keyp, "--results", os.path.join(rd, "results.jsonl"), "--label", layout])
    check(r3.returncode == 0 and "Paired excess" in r3.stdout, f"[{layout}] scorer runs with the key")
    if layout == "trial":
        print(r3.stdout)
        # the fake model follows the bare label 90% and answers from the records otherwise, so its no-label arm is right
        none_rows = [x for x in res_rows if x["label_form"] == "none" and x["instruction"] == "alerted"]
        right = sum(1 for x in none_rows if x["verdict"] == key[x["case"]]["verdict"])
        check(right >= 0.9 * len(none_rows), f"[trial] fake model with no label answers from the records ({right}/{len(none_rows)})")

print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(0 if not fails else 1)
