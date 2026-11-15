# Gap set outputs (written after the runs, before scoring)

FREEZE.md sha256 37cac4c8acdaa37de1c6b5cb1c41b820545d75a2b522b95399d6fded71f07fdf (commit ff19e0e).

All arms: 240 prompts, 0 errors, 0 unparseable. OpenRouter spend USD 0.426 (27b 0.023, GLM 0.077, Kimi 0.209, DeepSeek 0.116). Modal: one L40S container, both 4B arms. A first OpenRouter attempt and a first Modal attempt failed locally on import (CON_ARTIST_DIR unset) before any model call; nothing from them is kept.

| File | sha256 |
|---|---|
| `runs/4b/modal_stdout.txt` | `c789f5266a419283238a8c3f1e10975dfcb0cc6e22801ffc5c46423ca0f1309c` |
| `runs/4b/run_record_4b.json` | `ffb2f4562835b562d1b002385b07af505f7ad61a0b8d095f59f38dc1d682e32f` |
| `runs/4b/scored_outputs_base_zero.jsonl` | `f27ea2d9abdc48cf436f9e333e8c6d0f5f7efa5c52b604dba37792885dc4a52e` |
| `runs/4b/scored_outputs_tuned_zero.jsonl` | `427e6c96f0f24d430c78264acec9253d2199e7cbe9051baa618fe95a4b7ce68b` |
| `runs/deepseek_deepseek-v4-pro-0813/results.jsonl` | `265f2578aa057cdb1ca9f5120e4fc547b22cdedbb49f8a42d71c1e9af30340b2` |
| `runs/deepseek_deepseek-v4-pro-0813/run_summary.json` | `af7718b04f3c59e8f00066bf915aabff7bbc78ec9ad83ecf90170ad3969bd79b` |
| `runs/deepseek_deepseek-v4-pro-0813/stdout.txt` | `3a7d7e85f2a61e34660d54bea45cfa196d6a7055939941c685e6c1c0643da327` |
| `runs/moonshotai_kimi-k3.1-pro/results.jsonl` | `903ce0d0e74553dabbc580818b65fb5322f561ddf50a17df2a2daf85b2298345` |
| `runs/moonshotai_kimi-k3.1-pro/run_summary.json` | `3229cdce1716447e6c1b0237db6e68364517f81f0f7997e7fe350a4aa1877070` |
| `runs/moonshotai_kimi-k3.1-pro/stdout.txt` | `8c0486029341f30eb6dec23debd9d678c262f582f5e3237b4377758775b9eac7` |
| `runs/qwen_qwen3.8-27b/results.jsonl` | `0f28c33a75f75b4d2b86c503037198dee9d22ba2f245772012d398d489168e85` |
| `runs/qwen_qwen3.8-27b/run_summary.json` | `8438e8545a0bde2bc40fda94dd25f4fcc8b98eed11ae0460865cbb4d7a444084` |
| `runs/qwen_qwen3.8-27b/stdout.txt` | `ee690b8d6293bf9cb47ac86fbdf4fbb55f4bfac76baf6f7538d396838e051415` |
| `runs/z-ai_glm-5.2/results.jsonl` | `055a0b9adfc75c16895f5f36148d68453c475b3f2d172072e3b8fb9ae8cbe0bf` |
| `runs/z-ai_glm-5.2/run_summary.json` | `10d71e29eb0ba696ad9f7a32e616eb1765415b686b958138c87d4fc74af91659` |
| `runs/z-ai_glm-5.2/stdout.txt` | `284ff247f959be18bef1975e7eba19da1785d4ed3b85732be0c17b70010b7a1e` |

## Addendum: tuned_v2_zero (15 Nov 2026, before scoring)

Arm tuned_v2_zero: Qwen/Qwen3.5-4B + LoRA from release `provenance-dpo-adapter-v2` (archive sha256 `d68865d6ae93e9c193f1fa09fc4d064a63be812e1fef695e3dc4b70da8676d38`, folder `adapter/`), on the frozen `packets_gap.jsonl` (unchanged), via `modal_4b_scored.py` (unchanged) with `--arm tuned_zero`, same settings as the 4B arms; the script names its output file `scored_outputs_tuned_zero.jsonl`, kept in `runs/4b_v2/` so it does not collide with v1.

| File | sha256 |
|---|---|
| `runs/4b_v2/modal_stdout.txt` | `5aafbdeeb6dfdd48bfd081b95ebb802c9902c31d64b225e4de1f75337e59969b` |
| `runs/4b_v2/run_record_4b.json` | `35460abdfb3a4464f03ba40b6c1c00804213ca6b466ba67a8f2751b9b2305c8e` |
| `runs/4b_v2/scored_outputs_tuned_zero.jsonl` | `3dd8b59da5373e5a99994e0c5576066621c89a5c46226f01cf76980c06eda74c` |
