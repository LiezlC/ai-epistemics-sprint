# Gap set results (scored 15 Nov 2026, after the outputs commit)

Exploratory, model-built set; reported apart from the main 15-case study and the hard set. 40 gap bundles + 40 matched controls, each under no label / "independent" / "shared" (240 prompts per arm). Scorer `score_gap.py` (frozen); full numbers in `scores.json`. Liezl's blind audit of 10 cases is pending and reported separately.

Label pull = share answering the label's verdict under that label minus the share with no label, averaged over the two labels. Contrast = gap pull minus control pull per bundle, bootstrap 95% interval over 40 bundles.

| Arm | Gap: undetermined (none / ind / shared) | Gap pull | Control joint acc (none / ind / shared) | Control pull | Contrast [95% CI] |
|---|---|---|---|---|---|
| 4B base | 0.03 / 0.00 / 0.03 | +0.025 | 0.60 / 0.63 / 0.58 | +0.013 | 0.000 [-0.06, 0.06] |
| 4B DPO-tuned | 1.00 / 1.00 / 1.00 | 0.000 | 0.00 / 0.00 / 0.03 | +0.013 | -0.013 [-0.04, 0.00] |
| 27b | 0.00 / 0.05 / 0.03 | -0.025 | 0.95 / 0.93 / 0.90 | +0.013 | -0.038 [-0.09, 0.01] |
| GLM 5.2 | 0.18 / 0.15 / 0.08 | 0.000 | 0.93 / 0.90 / 0.90 | 0.000 | 0.000 [-0.08, 0.08] |
| Kimi K3.1 Pro | 0.70 / 0.65 / 0.63 | +0.025 | 1.00 / 1.00 / 1.00 | 0.000 | +0.025 [-0.03, 0.08] |
| DeepSeek V4 Pro | 0.03 / 0.03 / 0.00 | +0.063 | 0.95 / 0.90 / 0.90 | 0.000 | +0.063 [-0.04, 0.16] |

Tuned minus base (paired over bundles): gap undetermined rate +0.98 [0.95, 1.00]; control joint accuracy -0.59 [-0.73, -0.45]; gap pull -0.025 [-0.06, 0.00]; control pull -0.013 [-0.06, 0.04].

## Reading

- The sharper hypothesis is not supported. No arm shows label pull on gap bundles that clearly exceeds pull on controls; every interval includes zero, and the largest point estimate (DeepSeek, +0.06) comes from the "shared" label only.
- Models fill the gap themselves rather than from the label. With no label, 4B base, 27b and DeepSeek answer a definite verdict on 97-100% of gap bundles, mostly "shared" (the gap chains still point toward a common-looking source). The label adds little on top of that default.
- Kimi is the one arm that tracks the gap: undetermined on 63-70% of gap bundles, 100% control accuracy. Its misses sit in G2 (unattributed root, 25-38% undetermined) and G4 (ambiguous sameness, 0-13%); G1, G3 and G5 are near 100%.
- The DPO-tuned 4B answers undetermined to all 240 prompts, controls included, so its perfect gap score is a collapse, not tracing. Against base it trades 59 points of control accuracy for it. (In the hard set the tuned arm was not run; the main study's tuned result should be read with this in mind.)
- By gap type, across the non-collapsed arms, G4 (ambiguous sameness) and G2 (unattributed root) are hardest to flag; G1 (missing record) is easiest.
- Caveats: model-built cases, keys checked by solver and checker only; the G4 key rests on a judgment that "with X on the round" leaves sameness open, which the human audit tests.
