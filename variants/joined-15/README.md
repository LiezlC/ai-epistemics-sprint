# Joined variants (15 cases): converter, joined file, packets and first-turn outputs (14 Nov 2026)

Sprint work (written after the 13 Nov freeze). Check any file here with `git show HEAD:<path> | sha256sum`, not the working copy (`variants/** -text` is set).

Inputs are the two files already in `variants/`: `PV-scored-variants-DRAFT-2026-11-13 - Final.md` (3 cases, sha256 35db56b139e56760dc5eeda042fddbae1e33d192c876a63d9e579a534f6b3d45) and `PV-new-variants-2026-11-14.md` (12 cases, sha256 a86231b4aab18ed0834d76672154861ea1060bb3319204da76dbbf1ae76a4518).

| File | What it is |
|---|---|
| derive_joined_variants.py | converter; stops if an input hash differs; joins the first file's 3 cases then the new file's 12 |
| variants15.jsonl | 15 cases, ids v000 to v014 (first file v000 to v002, new file v003 to v014) |
| packets_scored.jsonl | output of the frozen `sprint-code/scored-run/build_scored_packets.py` on variants15.jsonl |
| runs/scored27b/ | Qwen3.8-27b via OpenRouter, raw outputs and run summary |
| runs/4b_3shot/ | Qwen3.5-4B untuned, three-shot, alerted prompt only, raw outputs and run record |

Command: `python -I derive_joined_variants.py <first file> <new file> variants15.jsonl`

The key and the rubric were not opened by the lead. Outputs were produced before the key was released.
