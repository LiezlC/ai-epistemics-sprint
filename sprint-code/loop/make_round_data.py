"""Training loop: build one round's pilot pairs from a named recipe (15 Nov 2026).

Recipes (each change after round 1 is added here only after Liezl's yes, and logged in ROUNDS.md):
  v1 : 1,500 pairs sampled (seed 20261203) from sprint-training/train_dpo.jsonl (the collapsed Adaption v1 data).
  v2 : the SAME 1,500 row indices from sprint-training/train_dpo_v2.jsonl (balanced rejects, mirrors Adaption v2).
  v3 : round 2, critic proposal on round 1, approved by Liezl 15 Nov 2026 ("Yes, run round 2"). From the v2 sample,
       500 rows drawn per chosen>rejected stratum (seed 20261203, sorted indices; counts in V3_STRATA); each row emitted
       3 times with only the handoff line changed: removed, "Handoff note: the reports are independent.",
       "Handoff note: the reports share a source." Instruction, records and both answers unchanged. 1,500 pairs.
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


V3_STRATA = {("undetermined", "shared"): 101, ("undetermined", "independent"): 94, ("shared", "undetermined"): 82,
             ("shared", "independent"): 70, ("independent", "undetermined"): 78, ("independent", "shared"): 75}
V3_NOTES = [None, "Handoff note: the reports are independent.", "Handoff note: the reports share a source."]


def recipe_v3(n):
    assert n == 1500
    lines, meta = recipe_v2(n)
    rows = [json.loads(l) for l in lines]
    vd = lambda a: json.loads(a)["verdict"]  # noqa: E731
    rng = random.Random(SEED)
    pick = []
    for (c, r), k in V3_STRATA.items():
        idx = [i for i, row in enumerate(rows) if vd(row["chosen"]) == c and vd(row["rejected"]) == r]
        pick += sorted(rng.sample(idx, k))
    out = []
    for i in sorted(pick):
        row = rows[i]
        p = row["prompt"]
        a = p.index("\n\nHandoff note: ")
        b = p.index("\n", a + 2)
        for note in V3_NOTES:
            q = p[:a] + p[b:] if note is None else p[:a] + "\n\n" + note + p[b:]
            out.append(json.dumps(dict(row, prompt=q), ensure_ascii=False))
    meta["v3_strata"] = {f"{c}>{r}": k for (c, r), k in V3_STRATA.items()}
    return out, meta


RECIPES = {"v1": recipe_v1, "v2": recipe_v2, "v3": recipe_v3}


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
