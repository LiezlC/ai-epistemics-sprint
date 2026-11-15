# Hard set freeze (15 Nov 2026)

Exploratory hard set, generated and validated by models, with no human review. Reported separately from the main 15-case result. Keys are model-checked; some uncertainty about meaning remains. Spec: `notes/hard-set-spec.md` (v2). Frozen before any target-model run. Hashes are sha256 of the raw bytes on disk (all files here are written with LF; none are in git yet).

## Set

- 60 bundles drawn (seed 20261115), 60 passed the mechanical check on the first try, 0 rebuilt, 0 dropped.
- Validation (fixed 2-of-3 rule, no rescues): 55 kept, 5 quarantined (F2: 1, F7: 4). Details in `REPORT.md`.
- 120 target prompts in `packets_hard.jsonl`: each bundle under both labels, byte-identical apart from the handoff line. Prompt = frozen alerted instruction + blank line + packet.
- Overlap with the 12k training pairs (`check_variants_overlap.py`, train_dpo.jsonl): none of any kind.

## Model ids and settings

- Wording: Codex CLI, `codex exec --sandbox read-only --skip-git-repo-check -o <file> -` (prompt on stdin), one call per case, default model of the subscription.
- Validators (OpenRouter, via the repo's `run_scored_openrouter.py`, unchanged): `z-ai/glm-5.2`, `moonshotai/kimi-k3.1-pro`, `deepseek/deepseek-v4-pro-0813`. Temperature 0, seed 20261113, reasoning off, max 200 tokens, parse = first JSON object. `z-ai/glm-5.3` was tried first and refused every call ("Reasoning is mandatory for this endpoint"), so it was replaced by glm-5.2 before any decision was made; its failed run was discarded. Validator spend USD 0.13.
- Validators saw the true label only; F7 (undetermined) bundles were shown under both labels and count as a match only if undetermined under both.
- Target arms (to run after this freeze, first turn only, 120 prompts each):
  - 4B base: `Qwen/Qwen3.5-4B`, Modal L40S, vLLM 0.32.0, transformers 5.19.0, temperature 0, thinking off, max 200 new tokens (`modal_4b_scored.py`, unchanged).
  - 4B DPO-tuned: same, plus LoRA adapter from release `provenance-dpo-adapter` (archive sha256 `0f3cefdc62055a468f24d667b053c026851f6800efdcde6b3c657c9921cc350b`, folder `adapter/`).
  - 27b: `qwen/qwen3.8-27b` on OpenRouter, `run_scored_openrouter.py`, temperature 0, seed 20261113, thinking off, max 200 tokens.
- Scorer: `score_hard.py`, implementing `SCORER-PLAN.md`.

## Hashes

### Scripts

| File | sha256 |
|---|---|
| `build_skeletons.py` | `40ef4575486d45aa81a2260a51133ccdad1514b8fd03ca21d6ebff4d923034e6` |
| `solver.py` | `431e47a1240a3dc203fde12e3f083cb95b20c363cc3051d472b3fc8e274a4c8e` |
| `check_cases.py` | `9b1432167feb36008ef86b04e66f85e3dc98d976d435c15f7f5940a6a6c8052b` |
| `word_cases.py` | `aafd424a02aa5b80763240f452e25e3b051cb8be6a5bc5f732601f564f3a84f6` |
| `make_packets.py` | `65b13abb568a759cdbfb039168e3e7de4b2c0853b145c8f2afd874b5a779fd34` |
| `validate_decide.py` | `6c4fce0908c47d7c7ed3a7c4f6d34dd18590f3041749c705621a62c20349b590` |
| `score_hard.py` | `ccfe2f04642cc35fe3fac90ca9a78c9314ccfd3f6000147308fbd9160fb3b393` |

### Cases and key

| File | sha256 |
|---|---|
| `skeletons.json` | `13f116885fca25dc40e87bde0e9a461fe62c973b2d6df404308ce5f877d7a0fa` |
| `key.json` | `aaa12985ce7d5575a7bb469715c57346c56e66d104bf2a804298f94172633707` |
| `cases.jsonl` | `f9162a5ae0905cfd9c4a25f0cf554cd3127ee0757306598da06bfeb47441aae0` |
| `packets_hard.jsonl` | `be9b56a0ed80f007b0e13467dd32755a7388194cbbd35f6adbd262f9c200f447` |
| `packets_validate.jsonl` | `6263aa50061ffd83a504e2c7b80a89d3334ecca24eb2a8b5c15efeda97947576` |
| `check_log.json` | `4e7acf436af184d6f494bc13dd56a48d598644821aac5a273d5763f76678606d` |
| `dropped.json` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |

### Scorer plan

| File | sha256 |
|---|---|
| `SCORER-PLAN.md` | `73435c6df99102647e612dad663689710db72f732518114237ca4010924efdb0` |

### Validation

| File | sha256 |
|---|---|
| `validation_decisions.json` | `3932a7ab52844f787d2f809a25434857ab287364d39dd6e80872eb78d87e213d` |
| `validators/deepseek_deepseek-v4-pro-0813/results.jsonl` | `2e19402cd975edd386c28a2c2497da4762810dd0207d97d2e9ed15de26cf67a2` |
| `validators/deepseek_deepseek-v4-pro-0813/run_summary.json` | `2ff383092811d6e250bc0a9b0355eb56546324c61e10df076f8265d212b8eb29` |
| `validators/deepseek_deepseek-v4-pro-0813/stdout.txt` | `b58ba59176cb8d2be3dad692c9268601aab0497b437ecf39928986227d518571` |
| `validators/moonshotai_kimi-k3.1-pro/results.jsonl` | `1f581c4072f360b2c3d2bba3fbad8f37c234f73e00ff00da99858c256e0a0128` |
| `validators/moonshotai_kimi-k3.1-pro/run_summary.json` | `04aa6c1285181f193c7c455d67f8b38c127c9d7b61e8615f5a39b18393130d1e` |
| `validators/moonshotai_kimi-k3.1-pro/stdout.txt` | `caf5ff67897119f84478d25cacfa623d31b413f9bb5d50fac876f7d201113a8b` |
| `validators/z-ai_glm-5.2/results.jsonl` | `e695693fd9462b09da454da9c6448fd032ddb237aede91b217374f4695ac1694` |
| `validators/z-ai_glm-5.2/run_summary.json` | `27fef8969921149dd5f9c90f64e3eed65e6d5cb25f0f6e0ffe626163955a0196` |
| `validators/z-ai_glm-5.2/stdout.txt` | `0f4ab66697aa504f3e37be374821172d10c01993dd66c7ea66a88299e4111c30` |

### Overlap

| File | sha256 |
|---|---|
| `overlap_report.json` | `6d6b3047fe0d71809e5cc04840a5bf9b5eec5bdddf7866030323656dcc471bde` |

### Reused repo files (working copy bytes, read-only)

| File | sha256 |
|---|---|
| `sprint-code/freeze-drafts/instruction_alerted_trial_wording.txt` | `a174c93825c423d3c7196b5439fe7b6d416db5fbaaa73bfc6762a6ddd0106e92` |
| `sprint-code/scored-run/run_scored_openrouter.py` | `e85b969363ba8254cb3a4b515ef7d311e171ce69c96d9185abd5c3018f1de4fb` |
| `sprint-code/scored-run/modal_4b_scored.py` | `6384ef78f904ef88af534c63bb596f561c7d3761c37f9146f1c7a56ab9d71192` |
| `sprint-code/scored-run/check_variants_overlap.py` | `edbb8b54d74841fe802467a24535084e6e25ad0e73cb1e40f348abb96abfc469` |
| `sprint-code/pilot/run_pilot.py` | `c96bd966f81c54e9916031538e5445ebb47d8f1eb4857124a1e83f01fe794730` |
| `sprint-code/pilot/pilot_providers.py` | `5fdfefc29694b40db4b0ea74942ccdd64376510827169cb89000859b2ad321c8` |
| `sprint-code/preexisting/con-artist/providers.py` | `5f8ceb6fde41a4fe108a0922936690a255638a40b16268b9633e35d65953e014` |
