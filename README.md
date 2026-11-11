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
