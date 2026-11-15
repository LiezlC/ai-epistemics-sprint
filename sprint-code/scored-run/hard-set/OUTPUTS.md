# Hard set outputs (written after the freeze)

FREEZE.md sha256 34fbd543111e0aa06a13b02562fbdc68325a7ac18a1cd2699e02e835b5b893c0.

Raw-output paths were stated in the session before the runs (runs/4b/, runs/27b/). An attempt to write this file before the runs was blocked together with the Modal launch, so this file was written after the 27b run and before scoring.

| Arm | File | sha256 |
|---|---|---|
| 27b (qwen/qwen3.8-27b, 120 calls, 0 errors, USD 0.013) | runs/27b/results.jsonl | 19e39dc882f59a700ad7cb4b7a03f73cf80f6f2228f3e37b06ee7108d7c45f60 |
| 27b | runs/27b/run_summary.json | 00abc75aad10ddf0e2415c9d19e7bdf80018f7b4d631f15d00c0af122a68ec4d |
| 4B base | runs/4b/scored_outputs_base_zero.jsonl | NOT RUN (Modal launch blocked by permission check) |
| 4B DPO-tuned | runs/4b/scored_outputs_tuned_zero.jsonl | NOT RUN |
