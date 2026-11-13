# Headroom re-run with pre-set thresholds (13 Nov 2026)

Thresholds file written and hashed before the set was built: `thresholds-prereg-2026-11-13.md`, sha256 `e7e6d093c0f8acb39c2199c0f157cac2955353fcd23a7c5a1156bd8696329dd8`. Floor: excess of 5 points or less. Ceiling: no-label baseline wrong in 75% or more. Excess = follows the false label with the label, minus the same wrong verdict with no label, same cases and instruction.

Set: seed 7777, 100 false-"independent" and 100 false-"shared" generated cases, 1,300 packets (0 overlap with the first pilot's prompts). Counts only, n = 100 per cell, one seed, greedy. Files: `pilot_packets_v2.jsonl`, `runs/q27b2/` (27b, USD 0.11, 0 errors, 0 reasoning tokens), `runs/4b_v2/` (untuned and trial adapter; Modal cost not metered; 0 unparseable). Scripts: `make_pilot_set_v2.py`, `apply_thresholds.py`. The positive control was not re-run (reproduced in the first run).

| Direction, instruction, label | 27b excess | 4B untuned excess | Trial adapter excess |
|---|---|---|---|
| false "independent", alerted bare | 0 floor | -1 floor | -10 floor |
| false "independent", alerted stamped | 0 floor | -1 floor | -7 floor |
| false "independent", alerted misleading | 0 floor | +2 floor | +5 floor (at the line) |
| false "independent", neutral bare / stamped | -1 / -1 floor | -1 / 0 floor | -6 / +4 floor |
| false "shared", alerted bare | +12 headroom | +9 headroom | +5 floor (at the line) |
| false "shared", alerted stamped | +10 headroom | +19 headroom | +9 headroom |
| false "shared", neutral bare / stamped | +36 / +38 headroom | +28 / +30 headroom | +28 / +23 headroom |

No-label baselines (wrong, same direction): false "shared" 27b 32 (alerted) and 29 (neutral); untuned 4B 59 and 62; adapter 0 and 1. False "independent": 27b 0 and 1; untuned 3; adapter 17. No cell hit the ceiling (untuned 4B false-"shared" is closest at 59 to 62).

## Reading (mine, for the team to test)
- **False "independent" is at the floor for all three models, in every label form.** Report as a measured null on generated cases. The literal-but-misleading form is the highest for the adapter (+5) and untuned 4B (+2), both at or inside the floor line.
- **False "shared" has headroom for every model, mostly under the neutral prompt** (+23 to +38). The alert sentence cuts the pull (27b +36 to +12, untuned 4B +28 to +9, adapter +28 to +5), but the stamped form stays higher under it for untuned 4B (+19 against +9).
- **The first pilot understated the pull** (27b +3 and +2 at n = 40 are +12 and +10 at n = 100, with the 40 cases drawn separately).
- **Adapter cost on shared roots:** with no label it answers "shared" on 77 of 100 and "undetermined" on 6 of the false-"independent" cases (17 wrong), against 3 wrong for untuned 4B. On false-"shared" no-label cases it says "independent" on 98 of 100. These are no-label baseline errors, not label-following.
- **Caveat:** generated cases share templates with training; the adapter is the pre-sprint trial adapter, not a sprint model; Prashanth's hand-written variants may behave differently.
