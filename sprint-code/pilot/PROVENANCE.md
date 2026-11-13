# Pilot code: what is preexisting, what is new (13 Nov 2026)

Use this to fill the README and report prior-work tables (the T01 proposal's Swarm-reuse cell said "[confirm: Deepayan]"; this settles it for this code).

## Preexisting code reused (Swarm Alignment Sprint, 6 Nov 2026; written before the Epistemics sprint opened)
| File | How it is used | Changed? |
|---|---|---|
| `con-artist/providers.py` | Imported by `pilot_providers.py` and shipped to Modal as a file: the call interface, retry and back-off, concurrency limits, spend cap, key scrubbing, the `Result` record | **No. Not edited, not copied.** |
| `con-artist/modal_app.py` | Pattern followed (Secret by name, Volume for outputs, `local_entrypoint`); not imported or copied | Not used as code |
| `training-trial/generate_cases.py` and `check_cases.py` (Liezl, 11 Nov 2026) | Basis of the sprint generator and checker; the generator header says so | Derived into new files, originals untouched |

## What is new, and why the preexisting route was not enough
The preexisting OpenRouter route calls the Responses endpoint and sends **no temperature and no seed**, so runs are not greedy or seeded, and it has no thinking-off switch. The sprint protocol needs greedy, seeded, thinking off. Change, kept outside the preexisting file:
- `pilot_providers.py`: a subclass `SprintProviders` that adds the route `openrouter_chat` (POST `/chat/completions`) with `temperature`, `seed`, `reasoning: {"enabled": false}` and `usage: {"include": true}` (to get the cost). Everything else is delegated to the preexisting class.

## New files (sprint code, 13 Nov 2026), all in `plans/Epistemics Sprint/pilot/`
`pilot_providers.py`, `make_pilot_set.py` (builds 520 non-scored packets from the sprint generator, seed 4242), `run_pilot.py` (runs a model, parses, scores, summarises), `fake_model.py` (test double), `modal_pilot.py` (Modal entry points, not yet run), `pilot_packets.jsonl` (generated data), this file.

## Status (updated 13 Nov, later)
- Tested first with the fake model, then run for real: smoke tests on both Qwen3.8 variants (five calls each) and the full 520-call pilot on `qwen/qwen3.8-27b` (run `q27b1`, USD 0.042, 0 errors). Results: `pilot-results-q27b1-2026-11-13.md`.
- The OpenRouter fields worked on the 27b route: `reasoning: {"enabled": false}` was accepted and honoured (0 reasoning tokens), `usage: {"include": true}` returned the cost (`cost_source` "reported" on all 520 calls). `qwen/qwen3.8-max-0902` rejects `reasoning.enabled=false` ("Reasoning is mandatory for this endpoint and cannot be disabled").
- One change after the first Modal run: `modal_pilot.py` guarded `HERE.parents[2]` so it imports inside the container (sprint code only; the preexisting `providers.py` is still untouched).
- Spend so far: about USD 0.043 on OpenRouter. No GPU spend yet.
