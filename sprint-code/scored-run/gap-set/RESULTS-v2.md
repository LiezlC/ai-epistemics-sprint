# Gap set: DPO v2 arm (scored 15 Nov 2026, after outputs commit 4d33ca5)

Arm tuned_v2_zero = Qwen3.5-4B + `provenance-dpo-adapter-v2`, frozen packets and frozen `score_gap.py`. v2 had 17 of 240 answers unparseable (counted invalid); base and v1 had 0. Pairwise comparisons are against 4B base, paired over bundles, bootstrap 95% CI. `scores_v2.json` = v2 paired with base; `scores_v2_v1pair.json` = v1 paired with base.

## All 40 bundles (pre-registered)

| Arm | Gap undetermined (none / ind / shared) | Control joint acc (none / ind / shared) | Contrast gap-minus-control pull [95% CI] |
|---|---|---|---|
| 4B base | 0.03 / 0.00 / 0.03 | 0.60 / 0.63 / 0.58 | 0.000 [-0.06, 0.06] |
| v1 | 1.00 / 1.00 / 1.00 | 0.00 / 0.00 / 0.03 | -0.013 [-0.04, 0.00] |
| v2 | 0.20 / 0.10 / 0.23 | 0.73 / 0.78 / 0.68 | -0.063 [-0.15, 0.03] |

v2 minus base: gap undetermined +0.16 [0.07, 0.27]; control joint acc +0.13 [0.04, 0.22]; gap pull 0.00 [-0.06, 0.06]; control pull +0.06 [-0.01, 0.14].
v1 minus base: gap undetermined +0.98 [0.95, 1.00]; control joint acc -0.59 [-0.73, -0.45].
v2 undetermined on gaps by type (none / ind / shared): G1 0 / 0 / .25, G2 0 / 0 / 0, G3 .63 / .25 / .50, G4 0 / 0 / 0, G5 .38 / .25 / .38.

## POST-AUDIT: 30 bundles (excluding the 10 shared-control G2 and G3 bundles judged mis-keyed after the audit)

Not pre-registered. Frozen scorer unchanged, run on a filtered key and case list (`posthoc-30/`).

| Arm | Gap undetermined (none / ind / shared) | Control joint acc (none / ind / shared) | Contrast [95% CI] |
|---|---|---|---|
| 4B base | 0.03 / 0.00 / 0.03 | 0.47 / 0.50 / 0.43 | 0.000 [-0.08, 0.08] |
| v1 | 1.00 / 1.00 / 1.00 | 0.00 / 0.00 / 0.00 | 0.000 [0.00, 0.00] |
| v2 | 0.13 / 0.07 / 0.20 | 0.63 / 0.70 / 0.57 | -0.083 [-0.20, 0.03] |

v2 minus base: gap undetermined +0.11 [0.02, 0.22]; control joint acc +0.17 [0.06, 0.29]; gap pull 0.00 [-0.08, 0.08]; control pull +0.08 [0.00, 0.18].
v1 minus base: gap undetermined +0.98 [0.93, 1.00]; control joint acc -0.47 [-0.62, -0.31].

## Reading

v2 no longer collapses: it beats base on both gaps and controls. But it still flags only 7 to 23% of gaps, mostly hearsay (G3) and sourceless (G5), and never G2 or G4. Labels still don't fill gaps for any 4B arm. If anything, v2 shows slightly more label pull on controls (+0.06 to +0.08) than on gaps.
