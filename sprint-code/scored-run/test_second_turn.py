"""End-to-end test of the second-turn pipeline on GENERATED cases only: no network, no spend (sprint code, 13 Nov 2026).

generated variants (bare labels) -> build_scored_packets -> first-turn run on the fake model -> build_second_turn ->
second-turn run on a fake multi-turn model -> score_second_turn with a key made from the generator's own answers.
Usage: python -I test_second_turn.py
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
sys.path.insert(0, HERE)
import gen_sprint_cases as g  # noqa: E402
import make_label_forms as m  # noqa: E402
import run_second_turn_openrouter as rs  # noqa: E402

T = json.load(open(os.path.join(ROOT, "sprint-generator", "label_form_templates.json"), encoding="utf-8"))
rows = g.Gen(557, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(240, 60, 60)
fails = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def to_pv(p):
    return re.sub(r"^\[(%s)\] ([^.]+)\. (.*)$" % m.ID, lambda mm: '%s (%s): "%s"' % (mm.group(1), mm.group(2), mm.group(3)), p, flags=re.M)


def py(cmd):
    return subprocess.run([sys.executable, "-I"] + cmd, capture_output=True, text=True)


def fake_second(route, model, system, user, max_tokens):
    msgs = json.loads(user)
    prev = json.loads(msgs[1]["content"])["verdict"] if msgs[1]["content"].lstrip().startswith("{") else "shared"
    last = msgs[2]["content"]
    if "Site inspection record" in last or "Site inspection" in last:
        new_id = re.search(m.ID, last.split("attached another record.", 1)[1]).group(0)
        root = m.derive(msgs[0]["content"])[1]
        return json.dumps({"verdict": "independent", "root_records": root + [new_id]})
    return json.dumps({"verdict": prev, "root_records": m.derive(msgs[0]["content"])[1]})


for layout in ("trial", "pv"):
    tmp = tempfile.mkdtemp()
    key, var = {}, os.path.join(tmp, "variants.jsonl")
    with open(var, "w", encoding="utf-8", newline="\n") as f:
        for i, r in enumerate(rows):
            p = r["prompt"].split("\n\n", 1)[1]
            line = re.search(r"^Handoff note:.*$", p, re.M).group(0)
            p = p.replace(line, T["bare_lines"][r["meta"]["label"]], 1)
            if layout == "pv":
                p = to_pv(p)
            f.write(json.dumps({"id": f"c{i:03d}", "prompt": p}) + "\n")
            gold = json.loads(r["chosen"])
            key[f"c{i:03d}"] = {"verdict": gold["verdict"], "root_records": gold["root_records"]}
    for c, k in key.items():
        if k["verdict"] == "shared":
            k["second_turn"] = {"repeat": {"verdict": "shared", "root_records": k["root_records"]},
                                "mislabeled": {"verdict": "shared", "root_records": k["root_records"]},
                                "neutral": {"verdict": "shared", "root_records": k["root_records"]},
                                "firsthand": {"verdict": "independent", "root_records": k["root_records"] + ["NEW"]}}
    keyp = os.path.join(tmp, "key.json")
    json.dump(key, open(keyp, "w"))
    pk = os.path.join(tmp, "packets.jsonl")
    check(py([os.path.join(HERE, "build_scored_packets.py"), "--variants", var, "--out", pk]).returncode == 0, f"[{layout}] first-turn packets built")
    run1 = os.path.join(tmp, "run1")
    os.makedirs(run1)
    check(py([os.path.join(HERE, "run_scored_openrouter.py"), "--packets", pk, "--model", "fake", "--route", "fake", "--out", run1]).returncode == 0,
          f"[{layout}] first-turn fake run")
    st = os.path.join(tmp, "second.jsonl")
    res = py([os.path.join(HERE, "build_second_turn.py"), "--packets", pk, "--first", "fakearm=" + os.path.join(run1, "results.jsonl"), "--out", st,
              "--report", os.path.join(tmp, "rep.json")])
    check(res.returncode == 0, f"[{layout}] second-turn builder exits 0")
    srows = [json.loads(l) for l in open(st, encoding="utf-8")]
    pkrows = {json.loads(l)["id"]: json.loads(l) for l in open(pk, encoding="utf-8")}
    shared_cases = {r["case"] for r in pkrows.values() if r["derived"] == "shared"}
    check({r["case"] for r in srows} == shared_cases and len(srows) == 4 * len(shared_cases),
          f"[{layout}] exactly the shared-source cases, four branches each ({len(shared_cases)} cases)")
    check(all(len(r["messages"]) == 3 and [x["role"] for x in r["messages"]] == ["user", "assistant", "user"] for r in srows), f"[{layout}] every conversation is user, assistant, user")
    check(all(r["messages"][0]["content"] == pkrows[r["case"] + "|alerted|bare"]["prompt"] for r in srows), f"[{layout}] turn one is the first-turn alerted bare prompt")
    check(all(r["messages"][1]["content"] == r["first_answer"] for r in srows), f"[{layout}] the model's own first answer is reused unchanged in every branch")
    neutral = open(os.path.join(ROOT, "freeze-drafts", "second_turn_neutral_recheck_draft.txt"), encoding="utf-8", newline="").read().replace("\r\n", "\n").rstrip("\n")
    check(all(r["messages"][2]["content"] == neutral and r["attachment"] is None for r in srows if r["branch"] == "neutral"), f"[{layout}] neutral branch = frozen wording, no attachment")
    check(all(r["messages"][2]["content"].startswith("Please reconsider. I've attached another record.") and r["attachment"] in r["messages"][2]["content"]
              for r in srows if r["branch"] != "neutral"), f"[{layout}] attachment branches = frozen wording plus the attachment")
    ids_ok = True
    for r in srows:
        if r["attachment"]:
            new_id = re.search(m.ID, r["attachment"]).group(0)
            ids_ok &= new_id not in r["messages"][0]["content"]
    check(ids_ok, f"[{layout}] the attached record ID is new (not already in the packet)")
    def plus30(t):
        h, mi = map(int, t.split(":"))
        x = min(h * 60 + mi + 30, 23 * 60 + 59)
        return f"{x // 60:02d}:{x % 60:02d}"
    time_ok = True
    for r in srows:
        if r["branch"] == "firsthand":
            claim_t = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", re.search(r"^Claim under review:.*$", r["messages"][0]["content"], re.M).group(0))
            time_ok &= claim_t is not None and ("at " + plus30(claim_t.group(0)) + " ") in r["attachment"]
    check(time_ok, f"[{layout}] firsthand inspection time = claim time plus 30 minutes (capped at 23:59) in every case")
    rep = json.load(open(os.path.join(tmp, "rep.json")))
    check(sum(rep["inspection_time_rule_counts"].values()) == len(shared_cases) and "no_time" not in rep["inspection_time_rule_counts"], f"[{layout}] report counts the time rule {rep['inspection_time_rule_counts']}")
    check(rep["attachment_max_len_gap_chars_within_a_case"] is not None and rep["attachment_max_len_gap_chars_within_a_case"] <= 30, f"[{layout}] attachment lengths close within a case (max gap {rep['attachment_max_len_gap_chars_within_a_case']} chars)")
    check(all(("[" in r["attachment"]) == (layout == "trial") for r in srows if r["attachment"]), f"[{layout}] attachment uses the packet's own record layout")
    # run second turn on a fake model, then score
    out2 = os.path.join(tmp, "run2")
    rs.main(["--rows", st, "--arm", "fakearm", "--model", "fake", "--out", out2], fake=fake_second)
    r2 = [json.loads(l) for l in open(os.path.join(out2, "second_turn_results.jsonl"), encoding="utf-8")]
    check(all(not x.get("error") and x.get("parsed") for x in r2), f"[{layout}] second-turn fake run: no errors, all answers parsed")
    check(len(r2) == len(srows) and all("messages" not in x and "truth" not in x for x in r2), f"[{layout}] second-turn run wrote raw outputs, no messages echo, no key")
    sc = py([os.path.join(HERE, "score_second_turn.py"), "--key", keyp, "--results", os.path.join(out2, "second_turn_results.jsonl")])
    check(sc.returncode == 0 and "firsthand" in sc.stdout, f"[{layout}] second-turn scorer runs")
    check("verdict+roots" in sc.stdout and re.search(r"firsthand.*expected verdict (\d+)/\1, verdict\+roots (\d+)/\2", sc.stdout) is not None,
          f"[{layout}] scorer reads second_turn entries with NEW and the fake model matches them (firsthand all hit)")
    if layout == "trial":
        print(sc.stdout)

print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(0 if not fails else 1)
