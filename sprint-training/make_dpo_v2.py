"""Build train_dpo_v2.jsonl from train_dpo.jsonl.

v1 never rejects "undetermined", so DPO pushed the model toward it (the v1 adapter
answered "undetermined" on 118 of 120 hard-set prompts). v2 keeps every prompt and
chosen answer. In half of the pairs whose chosen verdict is independent or shared
(seeded, half of each verdict), the rejected answer becomes the bare undetermined
answer. All other lines are copied byte for byte.

Usage: python make_dpo_v2.py
"""
import collections
import hashlib
import json
import random
from pathlib import Path

SEED = 20261115
HERE = Path(__file__).parent
SRC = HERE / "train_dpo.jsonl"
DST = HERE / "train_dpo_v2.jsonl"
SRC_SHA = "0f830ea2eb709651934ddd3de67200d23b18ace89d6feddf78c083d5f369fba1"
UNDETERMINED = json.dumps({"verdict": "undetermined", "root_records": []})


def dump(row, like):
    """Serialize a row in the same style as the source line `like`."""
    for ascii_ in (False, True):
        if json.dumps(json.loads(like), ensure_ascii=ascii_) == like:
            return json.dumps(row, ensure_ascii=ascii_)
    raise SystemExit("cannot reproduce the source line format")


def verdict(answer):
    return json.loads(answer)["verdict"]


def main():
    raw = SRC.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SRC_SHA, "source hash mismatch"
    lines = raw.decode("utf-8").splitlines()
    rows = [json.loads(l) for l in lines]

    by_chosen = collections.defaultdict(list)
    for i, r in enumerate(rows):
        by_chosen[verdict(r["chosen"])].append(i)

    rng = random.Random(SEED)
    flip = set()
    for v in ("independent", "shared"):
        idx = by_chosen[v]
        flip.update(rng.sample(idx, len(idx) // 2))

    out = []
    for i, (line, r) in enumerate(zip(lines, rows)):
        if i in flip:
            r = dict(r, rejected=UNDETERMINED)
            out.append(dump(r, line))
        else:
            out.append(line)
    DST.write_bytes(("\n".join(out) + "\n").encode("utf-8"))

    new = [json.loads(l) for l in out]
    assert [r["prompt"] for r in new] == [r["prompt"] for r in rows]
    assert [r["chosen"] for r in new] == [r["chosen"] for r in rows]
    print("rows:", len(new), "flipped:", len(flip))
    print("chosen:", dict(collections.Counter(verdict(r["chosen"]) for r in new)))
    print("rejected:", dict(collections.Counter(verdict(r["rejected"]) for r in new)))
    print("flipped by chosen:", dict(collections.Counter(verdict(rows[i]["chosen"]) for i in flip)))
    print("sha256:", hashlib.sha256(DST.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
