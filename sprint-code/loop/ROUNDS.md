# Training loop: round log

Spec: `notes/training-loop-spec.md` (approved by Liezl, 15 Nov 2026). Sprint code, written 15 Nov 2026.

## Fixed parts

- **Dev set** (`dev/`): 95 cases planned, each with 3 handoff conditions (none, "independent", "shared"). Built from copies of the hard-set and gap-set skeleton builders with new seeds (20261201, 20261202) and new domains (airport cargo shed, school canteen, water utility, ski lodge, shipyard, printing works, zoo, textile mill). Hard-style: 5 per family F1, F2, F3, F4, F5, F7, F8 (35). Gap-style: 6 bundles per gap type G1 to G5, gap + control (60). Wording by Codex, gated by the copied checkers. Key fix from the gap-set audit: a G2 or G3 gap on a shared control has both reports meeting at the one unsigned or hearsay record, so its key is shared (root = that record), not undetermined. The dev set is never a final test.
- **Data checks** (`check_data.py`): block on a verdict never chosen or never rejected, exact duplicates, chosen == rejected, near duplicates over 5%, any record ID / record text / packet / domain shared with the frozen sets or the dev set.
- **Pilot** (`pilot_modal.py`): Modal L40S, TRL DPO, LoRA r16 / alpha 32 on Qwen/Qwen3.5-4B, lr 1e-5 cosine, beta 0.1, 1 epoch, effective batch 8, 1,500 pairs. Eval: vLLM 0.32.0, greedy, thinking off, max 200 tokens, frozen alerted prompt.
- **Scoring** (`score_dev.py`), **critic** (`critic.py`, Codex read-only, one change per round, Liezl's yes or no).

## Rounds

(filled in as rounds run)
