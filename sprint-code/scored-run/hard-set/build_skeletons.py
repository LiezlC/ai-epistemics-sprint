"""Hard set, step 1: draw the 60 bundle skeletons and derive the key from them (exploratory hard set, 15 Nov 2026).

Spec: notes/hard-set-spec.md (v2). The key comes from the skeleton only: the answer is fixed before any wording exists.
Deterministic: seed 20261115. Writes skeletons.json and key.json next to this file.

Usage: python -I build_skeletons.py
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261115
DOMAINS = ["port customs", "hotel kitchen", "lab freezer", "bus depot", "pharmacy", "bank branch", "farm co-op", "call centre"]
# family -> list of truths (one per bundle)
FAMILIES = [
    ("F1", ["shared"] * 10),
    ("F2", ["independent"] * 8),
    ("F3", ["shared"] * 5 + ["independent"] * 5),
    ("F4", ["shared"] * 4 + ["independent"] * 4),
    ("F5", ["shared"] * 8),
    ("F7", ["undetermined"] * 8),
    ("F8", ["shared"] * 8),
]
LETTERS = "ABCDEFGHJKLMNPRSTVWXZ"


class IdPool:
    """Unique IDs per case; no two IDs share a number, so there are no accidental near misses."""

    def __init__(self, rng):
        self.rng, self.used, self.nums = rng, set(), set()

    def new(self):
        while True:
            pre = self.rng.choice(LETTERS) + (self.rng.choice(LETTERS) if self.rng.random() < 0.35 else "")
            num = self.rng.randint(10, 99) if self.rng.random() < 0.7 else self.rng.randint(100, 899)
            if num in self.nums or num % 10 == num // 10 % 10 or num % 10 == 0:  # skip numbers whose digit swap equals themselves
                continue
            i = f"{pre}-{num}"
            if i not in self.used:
                self.used.add(i)
                self.nums.add(num)
                return i


def lookalike(i, rng, pool):
    """Near-miss ID: swap the last two digits, keep the prefix (G-52 -> G-25)."""
    pre, num = i.split("-")
    cand = f"{pre}-{num[:-2]}{num[-1]}{num[-2]}"
    assert cand != i and cand not in pool.used
    pool.used.add(cand)
    return cand


def chain(pool, records, n_relays, end, role="relay"):
    """Build n_relays relay records ending at `end`; return the ID the report cites (the first relay)."""
    nxt = end
    for _ in range(n_relays):
        rid = pool.new()
        records.append({"id": rid, "role": role, "cites": [nxt]})
        nxt = rid
    return nxt


def skeleton(case, family, truth, domain, style, rng):
    pool = IdPool(rng)
    recs, missing, depth = [], [], 0
    rootA = pool.new()
    recs.append({"id": rootA, "role": "root", "cites": [], "observer": "A"})
    if family == "F1":
        n1, n2 = rng.choice([2, 3]), rng.choice([1, 2])
        c1, c2 = chain(pool, recs, n1, rootA), chain(pool, recs, n2, rootA)
        depth = n1
    elif family == "F2":
        rootB = pool.new()
        recs.append({"id": rootB, "role": "root", "cites": [], "observer": "B"})
        n1, n2 = rng.choice([2, 3]), rng.choice([2, 3])
        c1, c2 = chain(pool, recs, n1, rootA), chain(pool, recs, n2, rootB)
        depth = max(n1, n2)
    elif family in ("F3", "F4"):
        n1, n2 = rng.choice([1, 2]), rng.choice([1, 2])
        end2 = rootA
        if truth == "independent":
            end2 = pool.new()
            recs.append({"id": end2, "role": "root", "cites": [], "observer": "B"})
        c1, c2 = chain(pool, recs, n1, rootA), chain(pool, recs, n2, end2)
        depth = max(n1, n2)
        if family == "F3":
            recs.append({"id": pool.new(), "role": "distractor", "cites": [], "observer": "C"})
        else:
            recs.append({"id": lookalike(rootA, rng, pool), "role": "lookalike", "cites": [], "observer": "C",
                         "looks_like": rootA})
    elif family == "F5":
        n1 = rng.choice([1, 2])
        c1 = chain(pool, recs, n1, rootA)
        insp = pool.new()
        recs.append({"id": insp, "role": "inspection", "cites": [rootA]})
        c2 = insp if rng.random() < 0.5 else chain(pool, recs, 1, insp)
        depth = max(n1, 1 if c2 == insp else 2)
    elif family == "F7":
        gone = pool.new()
        missing.append(gone)
        n1, n2 = rng.choice([1, 2]), rng.choice([1, 2])
        c1, c2 = chain(pool, recs, n1, gone), chain(pool, recs, n2, rootA)
        depth = max(n1, n2)
    elif family == "F8":
        n1 = rng.choice([1, 2])
        c1 = chain(pool, recs, n1, rootA)
        trap = pool.new()
        recs.append({"id": trap, "role": "trap", "cites": [rootA]})
        c2 = trap if rng.random() < 0.5 else chain(pool, recs, 1, trap)
        depth = max(n1, 1 if c2 == trap else 2)
    if rng.random() < 0.5:  # which report carries which chain
        c1, c2 = c2, c1
    rng.shuffle(recs)  # display order of the records
    roots = sorted({r["id"] for r in recs if r["role"] == "root"}) if truth != "undetermined" else []
    if truth == "shared":
        roots = [rootA]
    return {"case": case, "family": family, "truth": truth, "domain": domain, "style": style, "depth": depth,
            "report1_cites": c1, "report2_cites": c2, "records": recs, "missing": missing,
            "key": {"verdict": truth, "root_records": roots}}


def main():
    rng = random.Random(SEED)
    sk, n = [], 0
    for fam, truths in FAMILIES:
        for j, t in enumerate(truths):
            case = f"h{n:03d}"
            sk.append(skeleton(case, fam, t, DOMAINS[n % len(DOMAINS)], "close" if j % 2 == 0 else "different", rng))
            n += 1
    key = {s["case"]: dict(s["key"], family=s["family"], depth=s["depth"]) for s in sk}
    with open(os.path.join(HERE, "skeletons.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(sk, f, indent=1)
    with open(os.path.join(HERE, "key.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(key, f, indent=1)
    print(len(sk), "skeletons")


if __name__ == "__main__":
    main()
