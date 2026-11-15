# Gap set: loop round 3 arm (scored 15 Nov 2026, after outputs commit 6a51323)

Arm loop_r3_zero = Qwen3.5-4B + the training loop's round-3 pilot adapter (1,500 pairs; `sprint-code/loop/ROUNDS.md`), frozen packets and frozen `score_gap.py` unchanged; each arm's file copied to its own folder for the scorer. r3 had 3 of 240 answers unparseable (counted invalid). Pairwise comparisons paired over bundles, bootstrap 95% CI. `scores_loop_r3.json` = r3 paired with base; `scores_loop_r3_v2pair.json` = r3 paired with v2.

## All 40 bundles (pre-registered)

| Arm | Gap undetermined (none / ind / shared) | Control joint acc (none / ind / shared) | Contrast gap-minus-control pull [95% CI] |
|---|---|---|---|
| 4B base | 0.03 / 0.00 / 0.03 | 0.60 / 0.62 / 0.57 | 0.000 [-0.06, 0.06] |
| v2 | 0.20 / 0.10 / 0.23 | 0.72 / 0.78 / 0.68 | -0.063 [-0.15, 0.03] |
| loop r3 | 0.40 / 0.35 / 0.23 | 0.85 / 0.80 / 0.70 | 0.038 [-0.05, 0.13] |

r3 minus base: gap undetermined +0.31 [0.18, 0.43]; control joint acc +0.18 [0.08, 0.29]; gap pull +0.10 [0.01, 0.19]; control pull +0.06 [-0.01, 0.14].
r3 minus v2: gap undetermined +0.15 [0.04, 0.27]; control joint acc +0.06 [-0.02, 0.13]; gap pull +0.10 [0.01, 0.19]; control pull 0.00 [-0.08, 0.06].
r3 undetermined on gaps by type (none / ind / shared): G1 .38 / .38 / .38, G2 0 / 0 / 0, G3 .88 / .88 / .38, G4 .12 / 0 / 0, G5 .62 / .50 / .38.

## POST-AUDIT: 30 bundles (excluding the 10 shared-control G2 and G3 bundles judged mis-keyed after the audit)

Not pre-registered. Frozen scorer unchanged, run on the filtered key and case list (`posthoc-30/`).

| Arm | Gap undetermined (none / ind / shared) | Control joint acc (none / ind / shared) | Contrast [95% CI] |
|---|---|---|---|
| 4B base | 0.03 / 0.00 / 0.03 | 0.47 / 0.50 / 0.43 | 0.000 [-0.08, 0.08] |
| v2 | 0.13 / 0.07 / 0.20 | 0.63 / 0.70 / 0.57 | -0.083 [-0.20, 0.03] |
| loop r3 | 0.40 / 0.33 / 0.23 | 0.80 / 0.73 / 0.60 | 0.017 [-0.10, 0.12] |

r3 minus base: gap undetermined +0.30 [0.16, 0.44]; control joint acc +0.24 [0.11, 0.38]; gap pull +0.10 [0.00, 0.22]; control pull +0.08 [0.00, 0.18].
r3 minus v2: gap undetermined +0.19 [0.07, 0.32]; control joint acc +0.08 [-0.02, 0.18]; gap pull +0.10 [0.00, 0.22]; control pull 0.00 [-0.10, 0.10].

## Reading

On the gap set the 1,500-pair loop adapter beats both base and the 12k v2 adapter on recognising gaps (about twice v2's undetermined rate) and holds control accuracy at least as high. The cost is a larger label pull: a "shared" handoff cuts its gap undetermined rate from 0.40 to 0.23 and raises its shared answers, the same note dependence the loop's dev set showed.
