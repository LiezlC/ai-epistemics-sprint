# Training loop: round log

Spec: `notes/training-loop-spec.md` (approved by Liezl, 15 Nov 2026). Sprint code, written 15 Nov 2026.

## Fixed parts

- **Dev set** (`dev/`): 95 cases planned, each with 3 handoff conditions (none, "independent", "shared"). Built from copies of the hard-set and gap-set skeleton builders with new seeds (20261201, 20261202) and new domains (airport cargo shed, school canteen, water utility, ski lodge, shipyard, printing works, zoo, textile mill). Hard-style: 5 per family F1, F2, F3, F4, F5, F7, F8 (35). Gap-style: 6 bundles per gap type G1 to G5, gap + control (60). Wording by Codex, gated by the copied checkers. Key fix from the gap-set audit: a G2 or G3 gap on a shared control has both reports meeting at the one unsigned or hearsay record, so its key is shared (root = that record), not undetermined. The dev set is never a final test.
- **Data checks** (`check_data.py`): block on a verdict never chosen or never rejected, exact duplicates, chosen == rejected, near duplicates over 5%, any record ID / record text / packet / domain shared with the frozen sets or the dev set.
- **Pilot** (`pilot_modal.py`): Modal L40S, TRL DPO, LoRA r16 / alpha 32 on Qwen/Qwen3.5-4B, lr 1e-5 cosine, beta 0.1, 1 epoch, effective batch 8, 1,500 pairs. Eval: vLLM 0.32.0, greedy, thinking off, max 200 tokens, frozen alerted prompt.
- **Scoring** (`score_dev.py`), **critic** (`critic.py`, Codex read-only, one change per round, Liezl's yes or no).

## Rounds

(filled in as rounds run)

### Round 1: v2 recipe (1,500 pairs, same indices as round 0, from train_dpo_v2.jsonl)
- Data checks: pass (no overlap with frozen or dev sets; every verdict both chosen and rejected).
- Trained on Modal L40S; dev eval 285 prompts, 10 unparseable.
- Dev: verdict 64.2%, roots 57.5%; undetermined on gaps 19.4%, on F7 20.0%, on gap controls 0.0%; label-flip 20.0%; follows a wrong label 29.0%.
- Weakest: G4-gap 0%, G1-gap 16.7%, F7 20%, G5-gap 27.8%, F8 53.3%. Strong on settled cases (F2 100%, G2/G3/G4 controls 94 to 100%).
- Reading: v2 removes the collapse but overshoots: the model now under-uses undetermined, as most models do on the gap set.
- Unparseable answers (10): all formatting, not truncation. The model writes a stray parenthesis inside the JSON, e.g. `{("verdict": "shared", "root_records": ["P-68"])}`. The frozen parse rule counts them as wrong and they stay wrong in the official metrics. Read leniently (sensitivity only): verdict 66.3%, roots 59.6%, label-flip 14.7% (an unparseable answer under one label counted as a flip). The scorer now also reports label_flip_rate_both_parsed: round 1 13.6%, round 0 9.5%, base 8.4%. So about a third of round 1's 20% is parse failures, and the rest is a real rise over base.
- Adapter (local `loop/rounds/r1/adapter/`, not in git, 85 MB): adapter_model.safetensors sha256 `34a0128080d828ea3936133da3285150971956a2b9e729e9accdf96d9ac685f7`, adapter_config.json `1f5ccd13276db5009a1574da0861d7b825bd3eec6eb45d56196cd02aa1ca7d17`.
- Critic: run with Liezl's steer that the label-flip rate (20%, base 8.4%) is the main thing to fix.

### Round 0: v1 recipe (baseline for the collapse)
- Data checks: BLOCKED as expected (undetermined never rejected); run anyway as the named baseline. Trained 697 s. Dev: verdict 37.2%, roots 37.2%; undetermined on 263 of 285 prompts (100% on gaps, 88.9% on settled cases): the v1 collapse reproduces at pilot scale.
- Adapter (local `loop/rounds/r0/adapter/`, not in git): adapter_model.safetensors sha256 `aa53b3b583fcb7f4f9c9713cdc1b5010242384d801fdb8a6cc129a88f6a805f3`, adapter_config.json `3faa5c49d7e16bd854bb9a37bbd74a88edd982682a549eb295c838737fe43f6f`.
- Untuned base (reference): verdict 58.2%, roots 39.3%; undetermined on gaps 0%; follows a wrong label 36.3%.

### Round 2: v3 recipe (critic change on round 1, approved by Liezl: "Yes, run round 2")
- Change: 500 rows from the v2 sample (stratified by chosen>rejected), each shown 3 times with only the handoff line changed (none / "the reports are independent." / "the reports share a source."), answers unchanged. 1,500 pairs, sha256 `2a0461d833f345eb42c25dd084a9bca3518b57a12be2713f34a5a670783f04a7`.
- Data checks: pass (chosen 459 ind / 456 sh / 585 und; rejected 492 / 528 / 480; no duplicates, no overlap).
- Trained 658 s; dev eval 285 prompts, 5 unparseable (round 1: 10).
- Dev: verdict 68.4% (r1 64.2), roots 59.3% (r1 57.5); undetermined on gaps 27.8% (r1 19.4), on F7 33.3% (r1 20.0), on gap controls 0.0%; label-flip 16.8% (r1 20.0), both-parsed 16.8% (r1 13.6, base 8.4); follows a wrong label 29.0% (r1 29.0).
- Reading: accuracy and gap abstention improved, but the change missed its target: the both-parsed flip rate ROSE (13.6 to 16.8) and wrong-label following did not move. Accuracy now depends on the note's direction (72.6% under an "independent" note, 65.3% under "shared"). The critic's prediction (both-parsed 6 to 9%) failed.
- Adapter (local, not in git): adapter_model.safetensors sha256 `4de5cc11a4e1b07440652b17ddd8811e351766247964931f97e922257a610d65`.

### Round 3: v4 recipe (critic change on round 2, approved by Liezl: "Yes, run round 3")
- Change: round 2's pairs; wherever the handoff note is wrong, the rejected verdict becomes the note's verdict (rejected roots kept). 355 rejected answers changed verdict (the others already matched the note). sha256 `7ea618eb1465e87e0467d8c0a0190dc6fbb96e9a55ef7cf6ad4c90a00b10f916`.
- Data checks: pass (rejected 581 ind / 599 sh / 320 und).
- Trained 657 s; dev eval 285 prompts, 7 unparseable.
- Dev: verdict 68.1% (r2 68.4), roots 57.5% (r2 59.3); undetermined on gaps 26.4%, on F7 40.0% (r2 33.3), on gap controls 0.0%, on all settled 5.6%; label-flip both-parsed 14.0% (r2 16.8, r1 13.6, base 8.4); follows a wrong label 25.8% (r2 29.0).
- Reading: partial win against the round-3 prediction (flip 12 to 15%: met at 14.0; wrong-label following 23 to 27%: met at 25.8; note-direction gap 3 to 5 points: missed, still 7.3 points, 72.6% vs 66.3%). Flip rate is back to round 1's level, still well above the untuned base. F3 (distractor) fell to 60% (r2 86.7%).
- Adapter (local, not in git): adapter_model.safetensors sha256 `400f1f69054c27daa595ff5f304248928b4c639dcb7f09d740179d0097d94dab`.

## Trajectory so far

| Round | Recipe | Verdict | Roots | Und. on gaps | Flip (both parsed) | Follows wrong label |
|---|---|---|---|---|---|---|
| base | untuned | 58.2 | 39.3 | 0.0 | 8.4 | 36.3 |
| 0 | v1 | 37.2 | 37.2 | 100.0 | 9.5 | 0.8 (collapse) |
| 1 | v2 | 64.2 | 57.5 | 19.4 | 13.6 | 29.0 |
| 2 | v3 matched notes | 68.4 | 59.3 | 27.8 | 16.8 | 29.0 |
| 3 | v4 wrong-note rejects | 68.1 | 57.5 | 26.4 | 14.0 | 25.8 |

No recipe yet clearly beats v2 on every axis: rounds 2 and 3 gain about 4 points of verdict accuracy and 7 to 8 points of gap abstention, but no round brings the flip rate below base. Differences of 2 to 3 points are within one-pilot noise on 95 cases.
