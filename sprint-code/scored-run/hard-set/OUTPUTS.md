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
