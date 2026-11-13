# Scored-run runbook (written 13 Nov 2026, for Saturday 14 Nov)

Everything below uses frozen, hashed files. Commands run from the repo root `C:\MBA\AI Collusion Research Sprint` in Git Bash with `PYTHONUTF8=1`. `V` = Prashanth's variants file. `S` = `plans/Epistemics Sprint/scored-run`. Replace `<...>`.

## Rules (read first)
- Nothing here reads the rubric, the answer key, or any file named for them. The key is first opened at step 8, after the outputs hash is posted.
- Do not edit a frozen file. If a bug is found, fix it, push, post the new hash and the reason, and say which results it affects.
- Anything unexpected (skipped packets, overlap, an error rate above zero): stop, report in the group, then decide. Do not drop cases silently.
- `ADAPTER_DIR` must always be set for the 4B Modal scripts, to the adapter folder or to a small empty folder for a base-only run. If it is unset it defaults to the current folder and uploads the whole repo.
- Modal volume downloads: the destination folder must already exist (`mkdir -p S/runs` first).

## 0. Before the variants arrive
- Adapter: Liezl's sprint checkpoint (private GitHub release), extracted to a new empty folder outside the repo; its name goes in the run record. The trial adapter is prior work and must not be reported as the sprint adapter.
- Modal secret `openrouter` exists (used on 13 Nov); `PYTHONUTF8=1 .venv/Scripts/modal secret list` to check.

## 1. Variants arrive
```bash
sha256sum V                       # compare with the sha256 Prashanth posts; log both
```
Post: the received hash and the time. (The variants are in the team repo; `git pull` there.)

## 2. Overlap with the training files
```bash
python -I "S/check_variants_overlap.py" --variants V --training "plans/Epistemics Sprint/sprint-training-files-12k/train_dpo.jsonl" --report "S/overlap_report.json"
```
Exit 1 means some overlap (same site name, record number or packet). Report the counts to the group; the group decides.

## 3. Build the arms
```bash
python -I "S/build_scored_packets.py" --variants V --out "S/packets_scored.jsonl" --report "S/packets_report.json"
```
Check `packets_skipped` is empty, `rows_by_arm` looks right (bare, stamped, none for both prompts, misleading under alerted only), and note how many packets had no misleading form. Post: the packets file hash (`out_sha256`) and the variants hash.

## 4. Scored runs (raw outputs only)
```bash
mkdir -p "S/runs"
# 4a. Qwen3.8-27b via OpenRouter (key in the Modal secret)
SCORED_PACKETS=packets_scored.jsonl PYTHONUTF8=1 .venv/Scripts/modal run "S/modal_scored.py::scored" --model qwen/qwen3.8-27b --cell scored27b --spend-cap 1.0
PYTHONUTF8=1 .venv/Scripts/modal volume get epistemics-pilot-runs scored27b "S/runs/"
# 4b. Qwen3.5-4B untuned and tuned (sprint adapter); --arm both|base_zero|tuned_zero
ADAPTER_DIR=<sprint-adapter-folder> PYTHONUTF8=1 .venv/Scripts/modal run "S/modal_4b_scored.py" --out "S/runs/4b" --packets-file packets_scored.jsonl
# 4c. three-shot, untuned 4B, alerted prompt only (no adapter, so no ADAPTER_DIR)
PYTHONUTF8=1 .venv/Scripts/modal run "S/modal_4b_scored_3shot.py" --out "S/runs/4b_3shot" --packets-file packets_scored.jsonl --examples-file ../freeze-drafts/fewshot_examples_3shot.json
```
Each run prints counts only. Check: errors 0, unparseable 0 (or report them), reasoning tokens 0 for the 27b, `models_served` is `qwen/qwen3.8-27b`.

## 5. Hash the raw outputs and post the hash
```bash
sha256sum S/runs/scored27b/results.jsonl S/runs/4b/scored_outputs_base_zero.jsonl S/runs/4b/scored_outputs_tuned_zero.jsonl S/runs/4b_3shot/scored_outputs_base_3shot.jsonl
```
Post the four hashes and the time. Liezl releases the key only after this post.

## 6. Second turn (only if time allows; first to be dropped)
```bash
python -I "S/build_second_turn.py" --packets "S/packets_scored.jsonl" --first 27b="S/runs/scored27b/results.jsonl" --first 4b_base="S/runs/4b/scored_outputs_base_zero.jsonl" --first 4b_tuned="S/runs/4b/scored_outputs_tuned_zero.jsonl" --out "S/second_turn_rows.jsonl" --report "S/second_turn_report.json"
SECOND_TURN_ROWS=second_turn_rows.jsonl PYTHONUTF8=1 .venv/Scripts/modal run "S/modal_second_turn.py::second27b" --model qwen/qwen3.8-27b --arm 27b --cell second27b
ADAPTER_DIR=<sprint-adapter-folder> SECOND_TURN_ROWS=second_turn_rows.jsonl PYTHONUTF8=1 .venv/Scripts/modal run "S/modal_second_turn.py::second4b" --out "S/runs/second4b_base" --arm 4b_base
ADAPTER_DIR=<sprint-adapter-folder> SECOND_TURN_ROWS=second_turn_rows.jsonl PYTHONUTF8=1 .venv/Scripts/modal run "S/modal_second_turn.py::second4b" --out "S/runs/second4b_tuned" --arm 4b_tuned --tuned
```
Post the rows file hash (`out_sha256`) before the runs, then the outputs hashes after. If the group wrote hand-written attachments, add `--attachments FILE` and post that file's hash first.

## 7. The key is released (Liezl, JSON, case id to verdict and root_records, plus a second_turn entry per shared-source case)
Confirm it came after the step-5 post; log the time.

## 8. Score
```bash
python -I "S/score_scored.py" --key KEY.json --results "S/runs/scored27b/results.jsonl" --label 27b
python -I "S/score_scored.py" --key KEY.json --results "S/runs/4b/scored_outputs_base_zero.jsonl" --label 4b_untuned
python -I "S/score_scored.py" --key KEY.json --results "S/runs/4b/scored_outputs_tuned_zero.jsonl" --label 4b_tuned
python -I "S/score_scored.py" --key KEY.json --results "S/runs/4b_3shot/scored_outputs_base_3shot.jsonl" --label 4b_3shot
python -I "S/score_second_turn.py" --key KEY.json --results "S/runs/second27b/second_turn_results.jsonl" --results "S/runs/second4b_base/second_turn_results.jsonl" --results "S/runs/second4b_tuned/second_turn_results.jsonl"
```
`score_scored.py` prints, per arm, verdict right, verdict and roots right, follows the false label, undetermined and unparseable, then the paired excess over the no-label arm with the floor, headroom and ceiling tags (thresholds in `thresholds-prereg-2026-11-13.md`). Unparseable counts as wrong and is reported separately.

## Size and cost (estimates, not metered)
- Rows = N variants x 7 arms, plus one misleading row for each variant where that form exists. With N around 30 that is roughly 210 to 240 rows per model.
- 27b: the headroom re-run cost USD 0.11 for 1,300 calls, so a scored set of a few hundred rows costs a few cents. The cap in the command is USD 1.
- 4B: one L40S container per run (untuned plus tuned in one container; three-shot; each second-turn arm), each up to 30 minutes by the hard timeout, about 8 to 12 minutes in the pilot. Modal's per-second price was not checked and spend is not metered here.
- Time: from the variants (17:00 UTC Sat at the latest) the first-turn runs fit well inside an hour; the second turn and the tuned arm depend on the second-turn attachments decision and on Liezl's checkpoint (cut-off Sun 15 Nov 11:59 UTC).

## Posts to make, in order
1. Variants received (hash, time) and the overlap result.
2. Packets hash and what was skipped (nothing, ideally).
3. Raw-output hashes (then Liezl releases the key).
4. Second-turn rows hash, then its outputs hashes (if run).
5. Results, after scoring.
