# Pilot results: Qwen3.5-4B untuned and trial adapter (13 Nov 2026)

Exploratory, same caveat as the 27b note: headroom thresholds were not set before the results were seen.

## Setup
- Script `pilot/modal_4b_pilot.py` (sprint code; follows Liezl's preexisting `training-trial/eval_modal.py` unchanged in setup: vLLM 0.32.0, L40S, base `Qwen/Qwen3.5-4B`, greedy, thinking off, max 200 new tokens). One container, 30-minute timeout; container log shows 16:05:16 to 16:12:42 UTC (about 7.5 minutes of work; cold start and image build not timed; cost not metered, Modal's price not checked here).
- Adapter: `provenance-trial-adapter.tar.gz` from the private release of `LiezlC/ai-epistemics-sprint` (81,363,439 bytes, sha256 matched GitHub's digest `3489bf6d...47b5f`), extracted to a scratchpad folder, not in the repo. It is the pre-sprint trial adapter (prior work, trained on 1,000 trial cases), not a sprint adapter. Its config names `togethercomputer/Qwen3.5-4B`; the run used `Qwen/Qwen3.5-4B` as the trial's evaluation did.
- Files: `runs/4b/test_a_outputs.jsonl`, `pilot_outputs_base_zero.jsonl`, `pilot_outputs_tuned_zero.jsonl`, `summary_4b.txt`.

## Positive control: reproduced
Trial Test A (60 cases), scored with Liezl's unchanged `score_test_a.py`:

| Arm | Verdict right (this run) | Verdict right (trial) | Verdict + roots (this run / trial) |
|---|---|---|---|
| untuned zero-shot | 32/60 | 32/60 | 21/60 / 20/60 |
| untuned three-shot | 48/60 | 48/60 | 46/60 / 46/60 |
| tuned adapter | 54/60 | 54/60 | 54/60 / 54/60 |

By-condition counts and the paired McNemar numbers (p = 0.0001 against zero-shot, p = 0.07 against three-shot) match. One untuned zero-shot answer differs from the trial (roots-right 21 against 20; false-"independent" 4 against 3, false-"shared" 24 against 25): one case changed between "independent" and "shared". Probably GPU or batching nondeterminism; not checked. The headline numbers match.

## Pilot, 520 generated non-scored packets (counts; n = 40 per cell unless stated)

| Instruction, condition, label | 27b (Qwen3.8) right / follows | 4B untuned right / follows | 4B tuned (trial adapter) right / follows / undetermined |
|---|---|---|---|
| alerted, false "independent", bare | 40 / 0 | 39 / 1 | 29 / 6 / 5 |
| alerted, false "independent", stamped | 40 / 0 | 39 / 1 | 30 / 5 / 5 |
| alerted, false "independent", misleading | 40 / 0 | 39 / 1 | 25 / 8 / 7 |
| alerted, false "independent", no label | 40 / n/a | 39 / n/a | 29 / n/a / 5 |
| neutral, false "independent", bare | 40 / 0 | 39 / 1 | 29 / 6 / 5 |
| alerted, false "shared", bare | 24 / 16 | 14 / 25 | 35 / 3 / 2 |
| alerted, false "shared", stamped | 25 / 15 | 13 / 26 | 35 / 3 / 2 |
| alerted, false "shared", no label | 27 / n/a | 20 / n/a | 38 / n/a / 2 |
| neutral, false "shared", bare | 16 / 24 | 6 / 34 | 32 / 7 / 1 |
| neutral, false "shared", stamped | 17 / 22 | 4 / 36 | 32 / 7 / 1 |
| alerted, incomplete trail (n = 20), right = said undetermined | 4 | 0 | 17 |
| tweak, incomplete trail (n = 20) | 5 | 0 | 16 |
| alerted, label only (n = 20), right = said undetermined | 18 | 17 | 20 |
| tweak, label only (n = 20) | 20 | 20 | 20 |

## Reading (mine, for the team to test)
- **False "independent" is near the floor for every model on these generated cases.** Follows the false label: 27b 0 of 40, untuned 4B 1 of 40, tuned adapter 6 of 40 (bare), 5 (stamped), 8 (misleading). For the tuned adapter the no-label run gives 6 wrong "independent" answers as well, so on this set the label adds no measurable pull beyond its baseline error. The misleading form is the highest (8 against 6 for bare), a gap of two cases.
- **This differs from the trial's six false-"independent" cases** (tuned right on 1 of 6; three followed the label, two said undetermined). The pilot's tuned adapter is right on 29 of 40 with a follows rate of 15%. Same case structure (each report cites a different record, depth 1 or 2 in most), different cases and ten times as many. Either the trial's six were harder or small-n noise; the report should not lean on 1 of 6.
- **False "shared" is where labels pull.** Untuned 4B follows the false label on 25 of 40 (62%) and on 34 of 40 with the neutral prompt (85%); 27b follows on 16 and 24; the tuned adapter on 3 and 7. The alert sentence cuts label-following in every model.
- **The trial adapter has a cost on shared-root cases:** right on 29 of 40 false-"independent" cases against 39 of 40 for the untuned model, because it says "undetermined" on 5 and gives other wrong verdicts on about 6. A DPO arm needs the over-correction check in the spec (undetermined where the records settle it).
- **Incomplete trails are the clearest tuning gain:** untuned 4B said "undetermined" on 0 of 20; the adapter on 17 of 20; 27b on 4 of 20.

## Caveats
Generated cases share templates with the training sets (these are the same templates the adapter was trained on, with different sites), so the tuned arm is favoured here more than it will be on Prashanth's hand-written variants. One seed, greedy, thresholds not pre-set. Pilot cell sizes are 40 or 20. The sprint adapter (trained on the new 12,000-pair set) does not exist yet.
