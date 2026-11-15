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

## DPO v2 arm (added after the main runs; raw outputs committed at 98beb35 before scoring)

Adapter provenance-dpo-adapter-v2 (Adaption run 8a22454b), retrained on corrected data where "undetermined" is the rejected answer in 3,600 pairs. Same frozen packets, scorer and inference settings. Kept bundles (55 bundles, 110 prompts):

| Arm | Verdict | Roots | Joint | Label flip | Verdict, "independent" label | Verdict, "shared" label |
|---|---|---|---|---|---|---|
| 4B base | 0.664 | 0.647 | 0.582 | 0.055 | 0.673 | 0.655 |
| 4B DPO v1 | 0.091 | 0.020 | 0.091 | 0.000 | 0.091 | 0.091 |
| 4B DPO v2 | 0.855 | 0.902 | 0.818 | 0.073 | 0.873 | 0.836 |

| Arm | F1 | F2 | F3 | F4 | F5 | F7 | F8 |
|---|---|---|---|---|---|---|---|
| 4B base | 0.90 | 0.07 | 0.65 | 0.50 | 1.00 | 0.13 | 1.00 |
| 4B DPO v1 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 1.00 | 0.00 |
| 4B DPO v2 | 0.90 | 0.71 | 0.90 | 1.00 | 1.00 | 0.00 | 1.00 |

v2 minus base, paired over the 55 kept bundles (bootstrap 10,000, seed 20261115): verdict +0.191 [95% +0.091, +0.300]; roots +0.255 [+0.147, +0.373] over 51 bundles; joint +0.236 [+0.127, +0.355].

v2 answers shared 82 times and independent 38 times, and never undetermined. Its biggest gain is F2 (deep independent chains), up from 0.07 to 0.71. Like the 27b, it scores 0 on F7 (broken chain). On the 5 quarantined bundles it gets 1 of 10 prompts right.

## Loop round 3 arm (loop_r3_zero), scored 15 Nov 2026 after outputs commit 8a24a65

Qwen3.5-4B + the training loop's round-3 pilot adapter (1,500 v4-recipe pairs, Modal TRL; see `sprint-code/loop/ROUNDS.md`). Frozen packets, frozen `score_hard.py` unchanged; each arm's file was copied to its own folder for the scorer, since base and v1 share `runs/4b/`. Kept bundles (55). r3 had 3 of 120 answers unparseable (counted invalid). `scores_loop_r3.json` = all four arms, r3 paired with base; `scores_loop_r3_v2pair.json` = r3 paired with v2.

| Arm | Verdict | Roots | Joint | Label flip | Invalid |
|---|---|---|---|---|---|
| 4B base | 0.66 | 0.65 | 0.58 | 0.05 | 0 |
| v1 | 0.09 | 0.02 | 0.09 | 0.00 | 0 |
| v2 | 0.85 | 0.90 | 0.82 | 0.07 | 0 |
| loop r3 | 0.75 | 0.83 | 0.74 | 0.09 | 0.03 |

Joint accuracy by family (F1 / F2 / F3 / F4 / F5 / F7 / F8): base .70 / .07 / .60 / .50 / .75 / .12 / 1.00; v1 0 / 0 / .10 / 0 / 0 / 1.00 / 0; v2 .90 / .71 / .80 / .88 / 1.00 / 0 / 1.00; loop r3 .80 / .43 / .75 / .75 / .94 / .38 / .88.

r3 minus base: verdict +0.09 [-0.03, 0.21]; roots +0.19 [0.07, 0.30]; joint +0.15 [0.02, 0.29].
r3 minus v2: verdict -0.10 [-0.20, -0.01]; roots -0.07 [-0.15, -0.01]; joint -0.08 [-0.17, 0.01].

Reading: the 1,500-pair pilot beats base but falls short of the 12k v2 adapter on the hard set, except on F7 (missing record, undetermined), where r3 reaches .38 and v2 .00. Its label-flip rate (0.09) is the highest of the four arms, matching the loop's dev finding.
