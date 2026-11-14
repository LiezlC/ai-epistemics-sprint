"""Frozen converter: Prashanth's two variants files -> one joined .jsonl of 15 cases.

Usage:  python -I derive_joined_variants.py FIRST.md NEW.md OUT.jsonl

- Checks both inputs against the sha256 values below and stops if either differs.
- Takes each case from its 'Claim:' line to the end of its block (blocks are split at '---' lines),
  so headings, design notes, the checklist and the disclosure are dropped.
- Changes the leading 'Claim:' to 'Claim under review:'.
- Ids are v000, v001, ... in order: the first file's cases, then the new file's cases
  (the order Liezl's key uses: first file v000-v002, new file v003-v014).
- Reads no key and no rubric.
Written 14 Nov 2026 (sprint work, after the 13 Nov freeze).
"""
import hashlib
import json
import re
import sys

EXPECTED = {
    "first": "35db56b139e56760dc5eeda042fddbae1e33d192c876a63d9e579a534f6b3d45",
    "new": "a86231b4aab18ed0834d76672154861ea1060bb3319204da76dbbf1ae76a4518",
}


def cases_of(path, key):
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != EXPECTED[key]:
        sys.exit("hash mismatch for %s file: %s" % (key, got))
    text = raw.decode("utf-8")
    out = []
    for block in re.split(r"(?m)^---\s*$", text):
        m = re.search(r"(?m)^Claim:", block)
        if not m:
            continue
        body = block[m.start():].rstrip() + "\n"
        out.append(re.sub(r"^Claim:", "Claim under review:", body, count=1))
    return out


def main():
    first, new, out = sys.argv[1], sys.argv[2], sys.argv[3]
    cases = cases_of(first, "first") + cases_of(new, "new")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for i, c in enumerate(cases):
            f.write(json.dumps({"id": "v%03d" % i, "prompt": c}) + "\n")
    print("cases", len(cases))
    print("out_sha256", hashlib.sha256(open(out, "rb").read()).hexdigest())


main()
