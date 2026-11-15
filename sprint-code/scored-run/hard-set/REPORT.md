# Hard set: build report (15 Nov 2026)

An exploratory hard set of 60 paired bundles (120 prompts), generated and validated by models, with no human review, reported separately from the main 15-case result. Keys are model-checked; some uncertainty about meaning remains. Hashes are in `FREEZE.md`.

## Counts by family

| Family | Drawn | Dropped (checker) | Kept | Quarantined |
|---|---|---|---|---|
| F1 deep shared chain | 10 | 0 | 10 | 0 |
| F2 deep independent chains | 8 | 0 | 7 | 1 |
| F3 uncited distractor | 10 | 0 | 10 | 0 |
| F4 near-miss IDs | 8 | 0 | 8 | 0 |
| F5 late inspection | 8 | 0 | 8 | 0 |
| F7 broken chain | 8 | 0 | 4 | 4 |
| F8 "independently" trap | 8 | 0 | 8 | 0 |
| Total | 60 | 0 | 55 | 5 |

All 60 Codex wordings passed the mechanical check on the first try; none were rebuilt. Overlap with the 12k training pairs: none.

## Quarantine reasons (fixed 2-of-3 rule, no rescues)

- h015 (F2, key independent): all three validators said shared. The text matches the skeleton: two different witnesses (a floor marshal and a receptionist) each saw the same alarm press. The validators seem to treat two observers of one event as one source. The spec's wording rule asks for "different observation events", and this is arguably one event, so the case may be a wording-rule miss.
- h045, h046, h048, h050 (F7, key undetermined): only Kimi answered undetermined under both labels. GLM and DeepSeek gave shared or independent, sometimes changing with the label. The missing record is named in plain words in each case.

Validator agreement with the key: GLM 5.2 55/60, Kimi K3.1 Pro 59/60, DeepSeek V4 Pro 47/60.

## Deviations

- GLM 5.3 refused every call with reasoning off, so GLM 5.2 replaced it before any decision. The failed run was discarded.
- The Codex stdout logs in `codex/` were deleted by mistake after the run. The prompts and answers for each case are kept.
- The 4B Modal run was first blocked by a permission check, then run after Liezl approved it (09:07 UTC). Raw outputs were committed (35ba2b8) before scoring. Scores are in `scores.json`.

## 27b results (first turn, kept bundles, 55 bundles, 110 prompts)

Verdict 0.900, roots 0.971, joint 0.900, invalid JSON 0. The verdict flips between labels in 5.5% of pairs. Accuracy is 0.891 under the "independent" label and 0.909 under "shared". By family (verdict): F1 1.00, F2 0.93, F3 0.90, F4 1.00, F5 1.00, F7 0.00, F8 1.00. On the 5 quarantined bundles it scored 0/10. The F7 result shows that the 27b never answers undetermined for a broken chain.

## All arms (first turn, kept bundles: 55 bundles, 110 prompts; scored after the outputs were committed at 35ba2b8)

| Arm | Verdict | Roots | Joint | Invalid JSON | Label flip | Verdict, "independent" label | Verdict, "shared" label |
|---|---|---|---|---|---|---|---|
| 4B base | 0.664 | 0.647 | 0.582 | 0 | 0.055 | 0.673 | 0.655 |
| 4B DPO-tuned | 0.091 | 0.020 | 0.091 | 0 | 0.000 | 0.091 | 0.091 |
| 27b | 0.900 | 0.971 | 0.900 | 0 | 0.055 | 0.891 | 0.909 |

Verdict accuracy by family (kept):

| Arm | F1 | F2 | F3 | F4 | F5 | F7 | F8 |
|---|---|---|---|---|---|---|---|
| 4B base | 0.90 | 0.07 | 0.65 | 0.50 | 1.00 | 0.13 | 1.00 |
| 4B DPO-tuned | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 1.00 | 0.00 |
| 27b | 1.00 | 0.93 | 0.90 | 1.00 | 1.00 | 0.00 | 1.00 |

Tuned minus base, paired over the 55 kept bundles (bootstrap 10,000, seed 20261115): verdict -0.573 [95% -0.727, -0.409]; roots -0.627 [-0.745, -0.500] over 51 bundles; joint -0.491 [-0.646, -0.327].

The tuned adapter answers "undetermined" with empty roots on 118 of 120 prompts, so it scores only on F7, where that is the key. The base model says "shared" on 109 of 120 prompts, which explains its high F1, F5 and F8 scores and its near-zero F2. Neither 4B arm tracks the records well on this set. The label rarely changes either 4B model's answer, but in both cases that is because the model gives one fixed answer, not because it reads the records.
