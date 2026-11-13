# Sprint training files (13 Nov 2026, AI x Epistemics sprint)

SPRINT CODE and data, written 13 Nov 2026 (after the sprint opened). Derived from the PREEXISTING trial generator `training-trial/generate_cases.py` (Liezl, 11 Nov 2026).

| File | Rows | sha256 |
|---|---|---|
| `train_dpo.jsonl` (prompt, chosen, rejected) | 12,000 | `0f830ea2eb709651934ddd3de67200d23b18ace89d6feddf78c083d5f369fba1` |
| `train_sft.jsonl` (prompt, completion), supervised fallback | 12,000 | `7412b87dc3914be3d837e1ab35ac80b60b4683694f80ecc46b7092312e0b687c` |

- Block 1: the first 1,000 cases (seed 20261113), spot-checked by Liezl: 20 of 20, no flags (her statement; result file read by Deepayan).
- Block 2: 11,000 more cases (seed 20261120), same generator, 20 of 20 on a separate spot check.
- Every row passes the generator's checker (answer re-derived from the records; rejected answer differs from chosen on every pair; no duplicate prompts; no site or record number shared with the trial files).
- Mix: 3,600 independent, 3,600 shared, 4,800 undetermined. Bare and authority-stamped labels only; the literal-but-misleading form is not in training.
- Known limit: volume, not variety (12 sites, fixed templates). Report it.
- `train_meta.jsonl` (ground-truth record structure) is deliberately not in the repo.
