# Handover: AI x Epistemics sprint (written Sun 15 Nov, about 11:10 UTC)

For anyone, or anyone's Claude, picking up if Liezl's sessions stop. **Submission closes Mon 16 Nov, 11:59 UTC.** Tracker (Gantt): https://claude.ai/artifact/B6gjVd8q4tnEEpTDppS97x. Report draft: `report/draft-report.md`, with every open item marked `TBD`. The earlier lead-session handover from 12 Nov (team, tools, pre-sprint trial) replaced by this file is still in git: `git show 0f7917c:HANDOVER.md`.

## Rules we keep

1. **Order of events for any scored run:** freeze and hash inputs, commit and push before running. Run. Commit the raw outputs and their hashes before scoring. Then commit the cases, key and scripts. Then commit the scores. One commit per step, pushed as it happens.
2. **Hash the committed bytes:** `git show HEAD:path | sha256sum`. Liezl's Git converts line endings, and every scored folder has `.gitattributes` `* -text`.
3. **Frozen sets are never edited or tuned against.** They are the main 15 cases (`variants/joined-15/`), the hard set (`sprint-code/scored-run/hard-set/`) and the gap set (`sprint-code/scored-run/gap-set/`). Only final candidates are scored on them. The loop uses its own development set.
4. **GPU work on Modal only.** Adaption runs spend Liezl's credits; never launch one without her yes.
5. **Report the hard set, gap set and loop as exploratory and model-built, apart from the main result.** Disclose every deviation; the report already lists them.

## Where things stand

| Piece | State | Commits |
|---|---|---|
| Main 15 cases, first turn (27b, 4B zero-shot, 4B three-shot) | Scored | ea01cc8 (key released), 5423a99, 02600bc |
| Second turn (27b, 4B untuned) | Scored. Caveat: the "new inspection" branch arguably isn't firsthand; see report 4.5 | a6073ef, 170b4aa |
| DPO v1 (Adaption 72134b60) | Collapsed to "undetermined" (never rejected in train_dpo.jsonl) | release provenance-dpo-adapter |
| DPO v2 (Adaption 8a22454b) | Fixes the collapse. Hard set verdict 86% (untuned 66%), roots 90% (65%) | c70ffa7, release provenance-dpo-adapter-v2 |
| Hard set (55 kept of 60 paired bundles) | Scored: 27b, 4B untuned, v1, v2 | 73a387c, 35ba2b8, ea1c614, 8482533, 98beb35, d4ff28a |
| Gap set (40 gaps + 40 controls × 3 notes) | Scored, 6 arms + v2. Labels don't fill gaps; models over-commit. 10 bundles mis-keyed (Liezl's audit); the report gives the 30-bundle analysis | ff19e0e, fe16ef7, 30aff8f, ab0ed67, 8c58bc6, 4d33ca5, 25aa21d |
| Training loop (`sprint-code/loop/`, log in ROUNDS.md) | Rounds 0 to 2 done. Round 3 (wrong-note verdict as rejected) training on Modal | 05b3fa7 … df71dc8 |

## What's left, by owner

**Deepayan**
- Run the 4B tuned arm on the main 15 cases with **v2** (`provenance-dpo-adapter-v2`, on `Qwen/Qwen3.5-4B`). Run v1 too if there's time, as the documented failure.
- Same frozen prompt and settings as the other 4B arms; outputs hash committed before scoring.
- Fill report Tables 3 to 6 (sections 4.1 to 4.5) and Appendix B from the committed scores.

**Whoever continues the loop** (Modal; scripts in `sprint-code/loop/`)
- When round 3 finishes, record it in ROUNDS.md and report Table 11.
- Further rounds need a person's yes on each critic change (`critic.py <round> --prev <round> --run` runs Codex). Liezl approves if she's around; otherwise, stop at round 3. Don't approve changes on her behalf.
- **Pick a final candidate:** the best round on the dev set, judged on verdict, roots, gap abstention and label flip together. Score its pilot adapter once on the hard and gap sets with the frozen scorers, following rule 1.
- A 12,000-pair Adaption run of the best recipe needs Liezl's yes; skip it if she's unavailable.
- **Finding so far:** every round that improved record tracing also raised label sensitivity (flip rate 8.4% untuned, 13.6% round 1, 16.8% round 2).

**Report (anyone)**
- Fill every `TBD` in `report/draft-report.md`: abstract, introduction headline, sections 4.1 to 4.5, exact control accuracies in Table 10, loop round 3, discussion bullets, conclusion, references, Appendix B run record and Appendix C tables.
- Renumber tables in order of appearance.
- Liezl's voice rules apply to all prose: no em dashes, no "not X but Y" constructions, no lists of three for rhythm.
- Final read, PDF, and repo tidy by Monday 10:00 UTC. Liezl decides on making the repo public.

## Key facts for the write-up

- **Main 15 cases:** 27b right on all 99 rows. 4B zero-shot verdict 97/99 (two label-follows under the neutral instruction), roots 66/99 (76/99 with duplicates removed). 4B three-shot 52/54 and 49/54. The extra-hop cases v004, v007 and v011 trip the 4B on roots.
- **Hard set, kept bundles:**

  | Model | Verdict | Roots | Label flips (of 55 pairs) |
  |---|---|---|---|
  | 27b | 99/110 | 99/102 | 3 |
  | 4B untuned | 73/110 | 66/102 | 3 |
  | v1 | 10/110 | 2/102 | 0 |
  | v2 | 94/110 | 92/102 | 4 |

  27b and v2 both score 0/8 on broken chains.
- **Gap set:**
  - Undetermined on gaps with no note: 27b 0%, 4B 3%, DeepSeek 3%, GLM 18%, Kimi 70%, v2 20%.
  - Label pull on gaps is no larger than on controls for any model.
- **Checks lesson (report discussion):**
  - Item-level human checks found little.
  - Liezl's gap audit found the key flaw.
  - The v1 flaw was only visible in file totals.
  - Model validators share blind spots.

## Update, Sun 15 Nov about 14:50 UTC (Liezl's sessions pausing for a usage reset)

- **Working report is now `report/draft-report.condensed.md`** (Deepayan's condensed version, about 5,200 words; detail in Appendices E to J). `report/draft-report.md` stays as the full record. Edit only the condensed file from here.
- **Fixed:** of five untuned models, four rarely or never said undetermined on the gap set, and only Kimi tracked gaps (the old "five of six" wording was wrong). Round 3 rows now in counts.
- **Headline:** labels rarely override clear records; the consistent weakness is over-commitment. Round 3's label pull on gaps (+0.10 [0.01, 0.19]) is an exploratory lead only.
- **Prashanth:** trim the abstract to 250 words, paste into the Google Docs template, measure pages, cut to 8 if needed. Branch, then push, target 21:00 UTC.
- **Liezl's calls still open:** author order (earlier reports listed Liezl first), Table P1 row 1 dates, public repo or access link, Adaption credits figure.
- **Slides (`slidevid/slides/`, local only):** Liezl is applying text fixes in Canva. Charts for slides 8 and 10 need redrawing with real numbers (slide 8: one "firm verdict 97 to 100%" bar, not two; slide 10: label flip 8.4 untuned, 13.6, 16.8, 14.0, 25.3 against roots 39, 58, 59, 58, 63).
- **Video (`slidevid/vidoverview/`, local only):** a Claude session is building the animated overview with HyperFrames. The voiceover fix clip `Delilah-editline-11614436.mp3` replaces the scene 6 sentence; the output is `label-or-record-overview.mp4`.
