"""Training loop: build one round's pilot pairs from a named recipe (15 Nov 2026).

Recipes (each change after round 1 is added here only after Liezl's yes, and logged in ROUNDS.md):
  v1 : 1,500 pairs sampled (seed 20261203) from sprint-training/train_dpo.jsonl (the collapsed Adaption v1 data).
  v2 : the SAME 1,500 row indices from sprint-training/train_dpo_v2.jsonl (balanced rejects, mirrors Adaption v2).
Both source files are checked against their sha256 first.
Usage: python -I make_round_data.py --recipe v1 --out rounds/r0/pairs.jsonl [--n 1500]
"""
import argparse
import hashlib
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(os.path.dirname(HERE), "sprint-training")
SEED = 20261203
SOURCES = {
    "v1": ("train_dpo.jsonl", "0f830ea2eb709651934ddd3de67200d23b18ace89d6feddf78c083d5f369fba1"),
    "v2": ("train_dpo_v2.jsonl", None),  # hash printed and logged; make_dpo_v2.py is deterministic
}


def load(name, sha):
    raw = open(os.path.join(TRAIN, name), "rb").read()
    h = hashlib.sha256(raw).hexdigest()
    if sha:
        assert h == sha, f"{name} hash mismatch"
    return raw.decode("utf-8").splitlines(), h


def indices(n_total, n):
    return sorted(random.Random(SEED).sample(range(n_total), n))


def recipe_v1(n):
    lines, h = load(*SOURCES["v1"])
    return [lines[i] for i in indices(len(lines), n)], {"source": SOURCES["v1"][0], "source_sha256": h}


def recipe_v2(n):
    lines, h = load(*SOURCES["v2"])
    return [lines[i] for i in indices(len(lines), n)], {"source": SOURCES["v2"][0], "source_sha256": h}


RECIPES = {"v1": recipe_v1, "v2": recipe_v2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe", required=True, choices=sorted(RECIPES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=1500)
    a = ap.parse_args()
    lines, meta = RECIPES[a.recipe](a.n)
    out = a.out if os.path.isabs(a.out) else os.path.join(HERE, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    data = ("\n".join(lines) + "\n").encode("utf-8")
    open(out, "wb").write(data)
    meta.update({"recipe": a.recipe, "n": len(lines), "seed": SEED, "pairs_sha256": hashlib.sha256(data).hexdigest()})
    json.dump(meta, open(out.replace(".jsonl", ".meta.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
