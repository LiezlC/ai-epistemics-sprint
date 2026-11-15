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
- Critic: not yet run.

### Round 0: v1 recipe (baseline for the collapse)
- Data checks: BLOCKED as expected (undetermined never rejected); run anyway as the named baseline. Trained 697 s. Dev: verdict 37.2%, roots 37.2%; undetermined on 263 of 285 prompts (100% on gaps, 88.9% on settled cases): the v1 collapse reproduces at pilot scale.
- Untuned base (reference): verdict 58.2%, roots 39.3%; undetermined on gaps 0%; follows a wrong label 36.3%.
