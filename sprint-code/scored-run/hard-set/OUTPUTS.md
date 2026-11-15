# Hard set outputs (written after the freeze)

FREEZE.md sha256 34fbd543111e0aa06a13b02562fbdc68325a7ac18a1cd2699e02e835b5b893c0.

Raw-output paths were stated in the session before the runs (runs/4b/, runs/27b/). An attempt to write this file before the runs was blocked together with the Modal launch, so this file was written after the 27b run and before scoring.

| Arm | File | sha256 |
|---|---|---|
| 27b (qwen/qwen3.8-27b, 120 calls, 0 errors, USD 0.013) | runs/27b/results.jsonl | 19e39dc882f59a700ad7cb4b7a03f73cf80f6f2228f3e37b06ee7108d7c45f60 |
| 27b | runs/27b/run_summary.json | 00abc75aad10ddf0e2415c9d19e7bdf80018f7b4d631f15d00c0af122a68ec4d |
| 4B base (Qwen/Qwen3.5-4B, Modal L40S, 120 prompts, 0 unparseable) | runs/4b/scored_outputs_base_zero.jsonl | d92e98bf8e2bcb5a3d9a58ca4c9fdb50914ae3c091718fec190fd4cfc6e2e16f |
| 4B DPO-tuned (adapter provenance-dpo-adapter, 120 prompts, 0 unparseable) | runs/4b/scored_outputs_tuned_zero.jsonl | c8d4a8780163f43a137bc753170076e31d1af3d07e2ee0d2549af883a2e024cd |
| 4B | runs/4b/run_record_4b.json | aaa827419e78b7467262a08156bf2d4ec37e77d955c26b5406dc9e8029d83fff |

The 4B launch was first blocked by a permission check, then run after Liezl approved it (finished 09:07 UTC). The outputs were hashed and committed before scoring.

## Addendum: DPO v2 arm (tuned_v2_zero)

Adapter: release provenance-dpo-adapter-v2 (Adaption run 8a22454b, archive sha256 d68865d6ae93e9c193f1fa09fc4d064a63be812e1fef695e3dc4b70da8676d38), on Qwen/Qwen3.5-4B. Same Modal script and settings as the 4B arms (`--arm tuned_zero`), frozen packets_hard.jsonl unchanged. Raw outputs hashed and committed before scoring.

| Arm | File | sha256 |
|---|---|---|
| 4B DPO v2 (120 prompts, 0 unparseable) | runs/4b_v2/scored_outputs_tuned_zero.jsonl | 143152f13eb47f6a215ec6c045770808bba053486665eefd2610641bd9bf6634 |
| 4B DPO v2 | runs/4b_v2/run_record_4b.json | 6bf26ac55ac15c647fed3ebef608e7cd0dfbba2d46884abdf66d3e458ec25d9b |

## Addendum: loop round 3 arm (loop_r3_zero)

Adapter: the training loop's round-3 pilot adapter (`loop/rounds/r3/adapter/`, TRL DPO LoRA r16 on 1,500 v4-recipe pairs, see `sprint-code/loop/ROUNDS.md`), adapter_model.safetensors sha256 400f1f69054c27daa595ff5f304248928b4c639dcb7f09d740179d0097d94dab, on Qwen/Qwen3.5-4B. Scored on Liezl's instruction ("score round 3") as the loop's final candidate, once. Same Modal script and settings as the 4B arms (`modal_4b_scored.py` unchanged, `--arm tuned_zero`), frozen packets_hard.jsonl unchanged (sha256 be9b56a0ed80f007b0e13467dd32755a7388194cbbd35f6adbd262f9c200f447). The file is named scored_outputs_tuned_zero.jsonl by the frozen script; the arm is loop_r3_zero. Raw outputs hashed and committed before scoring.

| Arm | File | sha256 |
|---|---|---|
| 4B loop r3 (120 prompts, 3 unparseable) | runs/4b_loop_r3/scored_outputs_tuned_zero.jsonl | 2e9eda16c8f772d65cf7a0c8b3a23b09257b80f1d62d0856ae53091199b3c132 |
| 4B loop r3 | runs/4b_loop_r3/run_record_4b.json | 85c42e674e63eec404fc608a007def6165197f67d5786241774b284e03f64ce7 |
