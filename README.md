# AI x Epistemics Research Sprint

Apart Research, November 13–15, 2026. [Sprint brief and resources](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15#resources)

## Start here

- [Project angles](PROJECT-ANGLES.md) is the working design and source of truth. The headline test is whether a model reviewer follows a misleading source label when the excerpts in front of it contradict the label. It also covers the reconsider branch, scoring, team decisions, the optional fine-tune check, and Apart's requirements.
- [Team brief](ai-epistemics-team-brief.html) is the plain-language pitch for Deepayan and Prashanth (draft of November 10). Its design sections now live in Project angles.
- [Project accelerator](apart_ai_x_epistemics_project_accelerator.html) is a general idea hub across the four tracks, kept for browsing.
- [Official source snapshot](papers/resources/source_list_snapshot.txt) records all 55 link occurrences in the Resources panel, representing 40 distinct URLs. This covers the reading list and the links embedded in example projects.

## Source notes

| Reading group | Notes |
| --- | --- |
| Sprint-wide reading and Track 2, Trust Infrastructure | [Notes and archive links](papers/resources/01-sprint-wide-and-trust.md) |
| Track 1, Model Epistemics and Decision-Making Evals | [Notes and archive links](papers/resources/02-model-epistemics-evals.md) |
| Tracks 3 and 4, Epistemic Products and Open Track | [Notes and archive links](papers/resources/03-products-and-open-track.md) |

The library follows the Swarm Alignment Sprint layout. Downloaded copies are in `papers/`, searchable extracts are in `papers/text/`, and source notes and the official link snapshot are in `papers/resources/`. The notes distinguish full-text review from abstract-only or limited access and link to web-native resources. PDFs from the separate project-overlap search are in `papers/adjacent/`.

The official resource library contains **24 PDFs**, including the standards. The separate overlap search adds **5 papers**. All 29 have searchable text extracts. The notes record the source and version used, including the public mirror for the Habermas Machine article.

## Repository notes

- **Prior work.** Everything committed before the sprint opens on November 13, 2026 is prior work, including the [toy Adaption run](toy-run/RUN-LOG.md) on fictional warehouse logs. The report and this README must say so.
- **Held-back variants stay out of the repo** until the reviewer prompt is frozen. The prompt writer must not see the contradiction cases or the answer key early.
- **Papers stay local.** PDFs and text extracts are excluded for copyright, so the paper links above only work on a local copy. The source notes in `papers/resources/` are tracked.

## Prior work and new work

The sprint opened on 13 November 2026. Everything in the table below was made before that date and is not a sprint result. Numbers from the trial in this subsection are **(prior work)**, from 11 November.

**Prior work (before 13 November).**

| # | What | Who | Date | Used in the sprint? |
| --- | --- | --- | --- | --- |
| 1 | Design and reading: project angles, team brief, project accelerator, source notes, reading library | Liezl, with Deepayan and Prashanth in the group discussion (threads of 9 to 11 Nov) | 9 to 11 Nov (committed 11 Nov 17:17 SAST, `5906b72`) | Design only |
| 2 | Toy Adaption run: seeded generator, 1,050 training rows and 20 holdout rows of fictional warehouse logs, Qwen/Qwen3.5-4B, LoRA r16 alpha 32, 1 epoch, 19 min 23 s; adapter on release `toy-run-adapter` | Liezl | 11 Nov | No. A pipeline and timing check on unrelated data |
| 3 | Load test of the toy adapter on Modal: 20 holdout rows scored with the adapter on (20/20 exact) and off (15/20 exact) | Deepayan | 11 Nov | No. Toy data, n = 20 |
| 4 | Minimum fine-tuning trial in the same site-gate setting: seeded generator (seeds 20261111 and 20261112), 1,000 scripted training cases, 60 Test A cases, 20-case human check, Adaption run `50993f1c`, Modal evaluation (results in the report, Section 3.14) | Liezl | 11 Nov | Design and method. Its adapter (`provenance-trial-adapter`) is not a sprint adapter; on 13 Nov it was run on non-scored generated packets for the headroom check and its Test A result was reproduced as a positive control (54/60) |
| 5 | Three practice contradiction variants | Prashanth | 11 Nov | No. Practice only; the scored variants were written during the sprint |
| 6 | Two private adapter releases: `toy-run-adapter` and `provenance-trial-adapter` | Liezl | 11 Nov (her posts of 11 Nov) | See rows 2 and 4 |
| 7 | Laundered Consensus (Swarm Alignment Sprint, 6 to 8 Nov): report and code | Coetzee, Sinha, Vijay | 6 to 8 Nov | Idea source. One file, `providers.py` (the Swarm sprint's model-call module), is imported unchanged by a sprint subclass; no other Swarm code or data is reused |
| 8 | Quiet Suppression (AI Collusion Research Sprint, 23 to 25 Oct): report, code and results | Coetzee, Sinha, Vijay | 23 to 25 Oct | Method and idea source only (positive control first, one lever at a time, freeze before evaluating). No code or data from it is used in the scored results |

**Code derived from preexisting code.** The sprint's training-case generator and checker (`gen_sprint_cases.py`, `check_sprint_cases.py`) are sprint code derived from the trial's `generate_cases.py` and `check_cases.py`: they reuse the re-derivation method and change the label forms, the sites, the record-ID range, the seeds and the scale (12,000 pairs). The 4B Modal runners follow the setup of the trial's `eval_modal.py` (vLLM, L40S, greedy, thinking off). The spot-check sheets use Liezl's preexisting review template.

The Test A cases share a generator with the training cases, so the trial shows the task was learned as taught, not that it transfers. The adapter config names `togethercomputer/Qwen3.5-4B`; every evaluation used `Qwen/Qwen3.5-4B`, which the adapter loads on, and Adaption does not confirm they are the same weights.

**New work done during the sprint (13 to 15 November 2026).**
- *13 Nov, before any scored variant existed:* the decisions fixed in the group (models, greedy decoding with seed 20261113, thinking off, parse rule, prompt wording, label forms); the sprint training-case generator and the 12,000 DPO pairs and supervised fallback (seeds 20261113 and 20261120); two 20-case spot checks by Liezl; the headroom check on non-scored generated cases; the three-shot comparison arm; the second-turn design; and the freeze post with its hashes.
- *14 Nov:* Prashanth's 15 scored variants (3 and 12, written before he read the rubric); Liezl's blind check and answer key (hash posted before the runs); the first-turn runs of the 27b and the 4B zero-shot and three-shot arms; the key release; scoring; the second turn on the 27b and the 4B zero-shot; the sprint DPO run on Adaption (v1).
- *15 Nov:* DPO v1's collapse and the v2 retrain; the exploratory hard set, gap set and training loop (Sections 3.15 to 3.17); the tuned arm on the 15 cases, run after the key and after the checkpoint; this report.

This section mirrors Section 3.14 of the report. Where the two differ, the report is the later draft.
