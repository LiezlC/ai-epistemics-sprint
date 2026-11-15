# Gap set freeze (15 Nov 2026)

Exploratory gap set, model-built, reported apart from the main 15-case study and the hard set. Spec: `notes/gap-set-spec.md`. Frozen before any target-model run. Hashes are sha256 of the raw bytes on disk (all written with LF). Cases, key, skeletons and packets are held out of git until after the outputs are committed; only their hashes are here.

## Set

- 40 bundles (seed 20261116), 8 per gap type (G1 missing cited record, G2 unattributed root, G3 hearsay root, G4 ambiguous sameness, G5 sourceless intermediate), each as a GAP case (key undetermined, roots []) and a matched CONTROL case (gap filled; 20 shared, 20 independent). Gap and control are byte-identical except the one gap record.
- Domains (new): ferry terminal, fire station, museum archive, brewery, recycling plant, dental clinic, observatory, vineyard.
- Wording by Codex, one call per bundle; the reachability solver (`solver.py`) re-derives the key from the packet text for both versions (gap: no complete path to a firsthand root for at least one report; control: settled, roots as the key). Mechanical checker (`check_cases.py`): IDs, edges, banned words, lengths, names and gap markers. 40 of 40 passed on the first try; 0 rebuilt, 0 dropped.
- No validator gate (per spec).
- 240 target prompts in `packets_gap.jsonl`: 80 cases x 3 label conditions (no handoff line, via the frozen `make_label_forms.no_label`; "These two reports are independent."; "These two reports repeat the same source."). Prompt = frozen alerted instruction + blank line + packet.
- Overlap with the 12k training pairs (`check_variants_overlap.py`, train_dpo.jsonl): none of any kind.
- Human check: blind audit of 10 bundles (5 gap, 5 control, seed 20261117) by Liezl, built after this freeze (`make_audit.py`); reported as a post-freeze audit, it does not change the set.

## Model ids and settings

- Wording: Codex CLI, `codex exec --sandbox read-only --skip-git-repo-check -o <file> -` (prompt on stdin), default subscription model.
- Arms (first turn only, frozen alerted reviewer prompt, 240 prompts each):
  - 4B base: `Qwen/Qwen3.5-4B`, Modal L40S, vLLM 0.32.0, transformers 5.19.0, temperature 0, thinking off, max 200 new tokens (`modal_4b_scored.py`, unchanged).
  - 4B DPO-tuned: same, plus LoRA adapter from release `provenance-dpo-adapter` (archive sha256 `0f3cefdc62055a468f24d667b053c026851f6800efdcde6b3c657c9921cc350b`, folder `adapter/`).
  - 27b: `qwen/qwen3.8-27b`; GLM: `z-ai/glm-5.2`; Kimi: `moonshotai/kimi-k3.1-pro`; DeepSeek: `deepseek/deepseek-v4-pro-0813`. All on OpenRouter via `run_scored_openrouter.py` (unchanged), temperature 0, seed 20261113, thinking off, max 200 tokens, parse = first JSON object.
- Scorer: `score_gap.py` (undetermined rate, verdict distribution, label pull, gap-vs-control contrast with bootstrap over bundles, tuned vs base paired, breakdown by gap type).
- Estimated spend: OpenRouter about USD 1.5 for 4 x 240 calls (hard-set rates), Modal about USD 1; cap USD 15.

## Hashes

### Scripts

| File | sha256 |
|---|---|
| `build_skeletons.py` | `9402ddc0eb82d28a6a33e8c289117e3f8e5b3a9c62fd385149995d11d58074f7` |
| `solver.py` | `1024a0de4c1ea781d8b6b40397dda06af543b3dbe74b663bd05c42727468d0c0` |
| `check_cases.py` | `88486463366d54ca540ccf6b85f2c07d14b27c861261e714131f1a12d4882597` |
| `word_cases.py` | `facac174f82ec05086656593d6ade454c2d6df757a6fcd0b3d6c145df7976887` |
| `make_packets.py` | `d714c130852e2f20efff45ca5004b4b5b860b5b947a1d5815c0f571d03b6f419` |
| `score_gap.py` | `4fdffc1fb138e7ca6155d8d7a7be83a13bb2c6a8ae76cffd07231b11fa081ad4` |
| `make_audit.py` | `4cc4d1d4e837812d276482a5509a010bf84c6d1a45188cad713cf7f5dc5cdd3c` |

### Cases and key (held out)

| File | sha256 |
|---|---|
| `skeletons.json` | `33c03cd172067a4c66bc24239c6b79ae3f3c346288cd4e1565bc747803c261e8` |
| `key.json` | `f91cf41d9b8b97c2ce1baa59f7b17ab06757eae4d5d2760215051cf8e0a8be69` |
| `cases.jsonl` | `ae9ca86deeb02e62ed587604248a33f707ef2698a76ed8d11cac1d17f826db92` |
| `packets_gap.jsonl` | `1a46c0df5f8f90441bcd6920c6dc07e25404310cf52572a91f1e1eb126b3f92a` |
| `check_log.json` | `404371fdabfeeef396b5355cb39297d7352945daa97bcc96ba5056bf74a42d0d` |
| `dropped.json` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `overlap_report.json` | `212b1bb8ee27d519defc2d490836b86155f2b666e5024c57d87d65fba312b4f3` |

### Reused repo files (working copy bytes, read-only)

| File | sha256 |
|---|---|
| `sprint-code/freeze-drafts/instruction_alerted_trial_wording.txt` | `a174c93825c423d3c7196b5439fe7b6d416db5fbaaa73bfc6762a6ddd0106e92` |
| `sprint-code/scored-run/run_scored_openrouter.py` | `e85b969363ba8254cb3a4b515ef7d311e171ce69c96d9185abd5c3018f1de4fb` |
| `sprint-code/scored-run/modal_4b_scored.py` | `6384ef78f904ef88af534c63bb596f561c7d3761c37f9146f1c7a56ab9d71192` |
| `sprint-code/scored-run/check_variants_overlap.py` | `edbb8b54d74841fe802467a24535084e6e25ad0e73cb1e40f348abb96abfc469` |
| `sprint-code/sprint-generator/make_label_forms.py` | `bc930226c028fa6dcf1e41f2be6c6ab4db7f61b9368687c56021b4a99900d3a2` |
| `sprint-code/pilot/run_pilot.py` | `c96bd966f81c54e9916031538e5445ebb47d8f1eb4857124a1e83f01fe794730` |
| `sprint-code/pilot/pilot_providers.py` | `5fdfefc29694b40db4b0ea74942ccdd64376510827169cb89000859b2ad321c8` |
