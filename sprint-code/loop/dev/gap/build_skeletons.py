"""LOOP DEV SET (copy of gap-set/build_skeletons.py; new seed 20261202, new domains, 6 bundles per gap type; KEY FIX: a G2/G3 gap whose control is shared has both reports meeting at the one unsigned or hearsay record, so its key is shared with that record as root, not undetermined). Gap set, step 1: draw the 40 bundle skeletons (gap + matched control) and derive the key (exploratory, 15 Nov 2026).

Spec: notes/gap-set-spec.md. The key comes from the skeleton only. Deterministic: seed 20261116.
Each bundle has a CONTROL version (records settle it: shared or independent) and a GAP version (one change, so at least
one report has no complete path to a firsthand root; key undetermined, roots []). The gap side is always the chain
that ends at rootA via relay R1 ("gap report"); which display slot (Report 1 or 2) carries it is random.
  G1 missing cited record : R1 -> M -> rootA; gap drops record M (still cited by R1).
  G2 unattributed root    : gap rewrites rootA with no maker and no sign of firsthand observation.
  G3 hearsay root         : gap rewrites rootA so its author says they were told by someone unnamed.
  G4 ambiguous sameness   : control independent; gap rewrites rootB so it names both observers and leaves open
                            whether it is the same observation as rootA or a second one.
  G5 sourceless relay     : gap rewrites R1 so it names no source record at all.
Controls: G4 all independent; G1, G2, G3, G5 five shared and three independent each (20 shared, 20 independent).
Writes skeletons.json and key.json (cases gNNN = gap, gNNNc = control).
Usage: python -I build_skeletons.py
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261202
DOMAINS = ["airport cargo shed", "school canteen", "water utility", "ski lodge", "shipyard", "printing works", "zoo", "textile mill"]
TYPES = [("G1", ["shared"] * 3 + ["independent"] * 3), ("G2", ["shared"] * 3 + ["independent"] * 3),
         ("G3", ["shared"] * 3 + ["independent"] * 3), ("G4", ["independent"] * 6),
         ("G5", ["shared"] * 3 + ["independent"] * 3)]
LETTERS = "ABCDEFGHJKLMNPRSTVWXZ"
SURNAMES = ["Okafor", "Lindqvist", "Marrow", "Haddad", "Petrov", "Achebe", "Quinlan", "Tanaka", "Ferreira", "Novak",
            "Brennan", "Ibarra", "Kowalczyk", "Mensah", "Albrecht", "Delacroix", "Varga", "Oduya", "Strand", "Castillo",
            "Mbeki", "Nakamura", "Rossi", "Halvorsen", "Szabo", "Duarte", "Kariuki", "Whitlock", "Esposito", "Lund"]
INITIALS = "ABCDEGHJKLMNPRST"


class IdPool:
    def __init__(self, rng):
        self.rng, self.used, self.nums = rng, set(), set()

    def new(self):
        while True:
            pre = self.rng.choice(LETTERS) + (self.rng.choice(LETTERS) if self.rng.random() < 0.35 else "")
            num = self.rng.randint(10, 99) if self.rng.random() < 0.7 else self.rng.randint(100, 899)
            if num in self.nums or num % 10 == 0:
                continue
            i = f"{pre}-{num}"
            if i not in self.used:
                self.used.add(i)
                self.nums.add(num)
                return i


def skeleton(b, gtype, truth, domain, rng):
    pool = IdPool(rng)
    names = rng.sample(SURNAMES, 2)
    nA, nB = f"{rng.choice(INITIALS)}. {names[0]}", f"{rng.choice(INITIALS)}. {names[1]}"
    recs = []
    rootA = pool.new()
    recs.append({"id": rootA, "role": "root", "cites": [], "observer": nA})
    end2 = rootA
    if truth == "independent":
        rootB = pool.new()
        recs.append({"id": rootB, "role": "root", "cites": [], "observer": nB})
        end2 = rootB
    # gap-side chain
    if gtype == "G1":
        m = pool.new()
        recs.append({"id": m, "role": "relay", "cites": [rootA]})
        r1 = pool.new()
        recs.append({"id": r1, "role": "relay", "cites": [m]})
    else:
        r1 = pool.new()
        recs.append({"id": r1, "role": "relay", "cites": [rootA]})
    # other chain: 1 or 2 relays
    nxt = end2
    for _ in range(rng.choice([1, 2])):
        rid = pool.new()
        recs.append({"id": rid, "role": "relay", "cites": [nxt]})
        nxt = rid
    c_gap, c_other = r1, nxt
    if gtype == "G1":
        target = m
    elif gtype in ("G2", "G3"):
        target = rootA
    elif gtype == "G4":
        target = rootB
    else:
        target = r1
    gap_slot = rng.choice(["1", "2"])
    c1, c2 = (c_gap, c_other) if gap_slot == "1" else (c_other, c_gap)
    rng.shuffle(recs)
    roots = [rootA] if truth == "shared" else sorted([rootA, rootB])
    return {"bundle": b, "gap_type": gtype, "control_truth": truth, "domain": domain, "gap_slot": gap_slot,
            "names": [nA, nB] if truth == "independent" or gtype == "G4" else [nA],
            "report1_cites": c1, "report2_cites": c2, "records": recs, "target": target,
            "key_control": {"verdict": truth, "root_records": roots},
            "key_gap": {"verdict": "undetermined", "root_records": []}}


def main():
    rng = random.Random(SEED)
    sk, n = [], 0
    for gt, truths in TYPES:
        for t in truths:
            sk.append(skeleton(f"dg{n:03d}", gt, t, DOMAINS[n % len(DOMAINS)], rng))
            n += 1
    key = {}
    for s in sk:
        kg = s["key_gap"]
        if s["gap_type"] in ("G2", "G3") and s["control_truth"] == "shared":  # dev key fix (audit)
            kg = {"verdict": "shared", "root_records": s["key_control"]["root_records"]}
        key[s["bundle"]] = dict(kg, bundle=s["bundle"], version="gap", gap_type=s["gap_type"])
        key[s["bundle"] + "c"] = dict(s["key_control"], bundle=s["bundle"], version="control", gap_type=s["gap_type"])
    with open(os.path.join(HERE, "skeletons.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(sk, f, indent=1)
    with open(os.path.join(HERE, "key.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(key, f, indent=1)
    print(len(sk), "bundles,", len(key), "cases")


if __name__ == "__main__":
    main()
