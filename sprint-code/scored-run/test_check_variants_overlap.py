"""Test for check_variants_overlap.py on GENERATED data only (sprint code, 13 Nov 2026). Usage: python -I test_check_variants_overlap.py"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "sprint-generator"))
import gen_sprint_cases as g  # noqa: E402

fails = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


tmp = tempfile.mkdtemp()
train = g.Gen(901, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(200, 20, 20)
tp = os.path.join(tmp, "train.jsonl")
with open(tp, "w", encoding="utf-8", newline="\n") as f:
    for r in train:
        f.write(json.dumps({"prompt": r["prompt"]}) + "\n")


def run(variants):
    vp = os.path.join(tmp, "v.jsonl")
    with open(vp, "w", encoding="utf-8", newline="\n") as f:
        for p in variants:
            f.write(json.dumps({"prompt": p}) + "\n")
    rp = os.path.join(tmp, "rep.json")
    res = subprocess.run([sys.executable, "-I", os.path.join(HERE, "check_variants_overlap.py"), "--variants", vp, "--training", tp, "--report", rp],
                         capture_output=True, text=True)
    return res, json.load(open(rp))


# 1. packets from the same site list and ID range: must be flagged
same = [r["prompt"].split("\n\n", 1)[1] for r in g.Gen(902, g.SITES, g.ID_LO, g.ID_HI, g.INSTRUCTIONS).batch(30, 5, 5)]
res, rep = run(same)
check(res.returncode == 1 and rep["packets_with_a_training_site_name"] == 30, f"same sites flagged on all 30 packets ({rep['packets_with_a_training_site_name']})")
check(rep["packets_with_ids_in_the_training_range_10000_14999"] == 30, "IDs in the training range are listed")
check(rep["packets_sharing_only_a_record_number"] + rep["packets_sharing_an_exact_record_id"] > 0, "some record numbers coincide with the training files")

# 2. an exact training packet is flagged as identical
dup = [train[0]["prompt"].split("\n\n", 1)[1]]
res, rep = run(dup)
check(rep["packets_identical_to_a_training_packet"] == 1, "an exact copy of a training packet is flagged")

# 3. different sites and a different ID range: no overlap
other_sites = [s + " Annexe" if False else s for s in g.SITES]
alt_sites = ["Harbour Light Station", "Ironbark Cold Store", "Saltpan Weighbridge", "Kestrel Ridge Clinic", "Marula Bend Depot", "Tidewater Substation",
             "Bluegum Yard", "Ashfall Quarry", "Lantern Hill School", "Pelican Flats Pumphouse", "Granite Cross Hub", "Driftwood Dairy"]
ok_rows = g.Gen(903, alt_sites, 30000, 34999, g.INSTRUCTIONS).batch(30, 5, 5)
clean = [r["prompt"].split("\n\n", 1)[1] for r in ok_rows]
res, rep = run(clean)
check(res.returncode == 0 and "no overlap of any kind" in res.stdout, f"different sites and ID range: no overlap (exit {res.returncode})")
print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(0 if not fails else 1)
