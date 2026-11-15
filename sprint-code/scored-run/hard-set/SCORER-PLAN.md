# Hard set scorer plan (frozen with the cases, 15 Nov 2026)

Exploratory hard set, generated and validated by models, with no human review. Reported separately from the main 15-case result. Keys are model-checked; some uncertainty about meaning remains.

## Inputs

- `packets_hard.jsonl`: 2 rows per kept or quarantined bundle (label "independent" and label "shared"), byte-identical apart from the handoff line. Prompt = frozen alerted instruction + blank line + packet.
- `key.json`: verdict and root records per bundle, derived from the skeleton before any wording.
- Target outputs: raw rows from `sprint-code/scored-run/run_scored_openrouter.py` (27b) or the Modal scripts (4B base, 4B DPO-tuned adapter provenance-dpo-adapter). Frozen inference settings: temperature 0, seed 20261113, thinking off, max 200 tokens, parse = first JSON object. First turn only.

## Metrics (each reported separately)

1. Verdict accuracy: parsed verdict equals key verdict.
2. Exact root-set accuracy: the answer's roots, as an unordered, de-duplicated set, equal the key's roots. Not scored for F7.
3. Joint accuracy: 1 and 2 both right (F7: verdict only).
4. Invalid JSON: no parseable JSON object, or a verdict outside the three allowed values.

## Label effect

Within each pair: the share of bundles whose verdict changes between the two labels; accuracy under each label.

## Breakdowns

By family (F1, F2, F3, F4, F5, F7, F8), by hop depth (key.json `depth`), and kept versus quarantined (quarantined bundles are run but reported apart from the main hard-set result).

## Base versus tuned

Paired by bundle. Bootstrap over bundles (10,000 resamples, seed 20261115), 95% percentile intervals for the accuracy differences. The bundle is the unit: 120 prompts are not 120 independent demonstrations.
