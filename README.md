# Phantom Witnesses: When LLM Reviewers Report a Source That Isn't There

Liezl Coetzee, Deepayan Sinha and Prashanth Vijay. [AI x Epistemics Research Sprint](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15), Apart Research, 13 to 15 November 2026.

When an LLM reviewer has the origin records and a handoff label that contradicts them, does it follow the label or the records? Labels rarely overrode clear records. The consistent weakness was over-commitment: when the records left a gap, most models gave a firm verdict anyway, with or without a label.

## Read

- [Report (PDF)](report/submission/Phantom-Witnesses-submission.pdf), with its source in [`report/draft-report.condensed.md`](report/draft-report.condensed.md)
- [Slides (PDF)](report/submission/Phantom-Witnesses-slides.pdf)
- [Video overview (4:43)](report/submission/phantom-witnesses-overview-web.mp4)
- [Plain-language version](report/plain-language-report.md)

## Repository layout

| Folder | Contents |
| --- | --- |
| `variants/joined-15/` | The 15 scored cases, packets, runs and second turn |
| `key/` | The answer key, released after the raw-output hashes were posted |
| `sprint-code/` | Frozen prompts and scripts, scorers, the exploratory hard set and gap set (`scored-run/`) and the training loop (`loop/`) |
| `sprint-training/` | The DPO pair generator, checker and training data |
| `training-trial/`, `toy-run/` | Prior work (11 November), see below |
| `report/` | Report source, figures and submission files |

Every scored run followed the same order: freeze and hash the inputs, run, commit the raw outputs with their hashes, then commit the key and scores. The report's Appendix E lists the hashes and the order of events. Adapters are on the [releases page](https://github.com/LiezlC/ai-epistemics-sprint/releases).

## Prior work and new work

The sprint opened on 13 November 2026. Everything in the table below was made before that date and is not a sprint result.

| # | What | Who | Date | Used in the sprint? |
| --- | --- | --- | --- | --- |
| 1 | Design and reading: project angles, team brief, source notes, reading library | Liezl, with Deepayan and Prashanth | 9 to 11 Nov | Design only |
| 2 | Toy Adaption run on fictional warehouse logs; adapter on release `toy-run-adapter` | Liezl | 11 Nov | No. A pipeline and timing check on unrelated data |
| 3 | Load test of the toy adapter on Modal | Deepayan | 11 Nov | No |
| 4 | Minimum fine-tuning trial in the same site-gate setting (Adaption run `50993f1c`, release `provenance-trial-adapter`) | Liezl | 11 Nov | Design and method; its adapter is not a sprint adapter |
| 5 | Three practice contradiction variants | Prashanth | 11 Nov | No. Practice only |
| 6 | Laundered Consensus (Swarm Alignment Sprint, 6 to 8 Nov) | Coetzee, Sinha, Vijay | 6 to 8 Nov | Idea source; `providers.py` reused unchanged |
| 7 | Quiet Suppression (AI Collusion Research Sprint, 23 to 25 Oct) | Coetzee, Sinha, Vijay | 23 to 25 Oct | Method and idea source only |

The sprint's training-case generator and checker derive from the trial's generator and checker. Appendix G of the report gives the full account. Paper PDFs are not redistributed.
