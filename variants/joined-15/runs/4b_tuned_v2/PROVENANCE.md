# 4B tuned arm, DPO v2 adapter, 15 frozen cases (run here, 15 Nov 2026)

- Run time: 2026-11-15 12:27:48 to 12:34:05 UTC (shell clock). This is AFTER the Sun 15 Nov 11:59 UTC tuned-arm checkpoint set on 13 Nov; report it as a late run.
- Adapter: private release `provenance-dpo-adapter-v2` on LiezlC/ai-epistemics-sprint (Adaption run 8a22454b per Liezl; not checked here). Release asset `provenance-dpo-adapter-v2.tar.gz`, sha256 d68865d6ae93e9c193f1fa09fc4d064a63be812e1fef695e3dc4b70da8676d38 (equals the digest GitHub lists; computed here). Extracted `adapter/`: adapter_model.safetensors 31bdcdc2f980dcf1395d1bff390362d5c036053b69d5005a0ca2b294da5a1a3b, adapter_config.json 03eed2d91f4485d55cfbb5f88b96b26e9008d0c8d46aed1e49ad9de1ed2ae480 (config base_model_name_or_path: togethercomputer/Qwen3.5-4B; run loaded Qwen/Qwen3.5-4B).
- Script: modal_4b_scored.py --arm tuned_zero, frozen packets_scored.jsonl (sha256 96d555e2...61ddb, equals the frozen hash), greedy, thinking off, max 200 new tokens, vLLM 0.32.0, L40S, seed 0.
- Result: 99 packets, 0 unparseable, 0 empty answers.
- Outputs sha256: scored_outputs_tuned_zero.jsonl eb50e523d9a43849dc6260ce01b3e4ce936ef2758268e7b8b19490f1c91664b0; run_record_4b.json dd674cefc1484c5faeea239c25de9c3e7db56aebf300049a426660fadcade15a (its adapter_dir_name is "adapter"; this file is the record of which adapter).
- Hashed before scoring. Not yet committed or posted to the group at the time of writing. The key was already released (ea01cc8), so this arm was not blind to the key.
