# Handover: AI x Epistemics sprint, lead session

Written November 12, 2026, for the next Claude session that works with Liezl on this sprint. Treat that session as the **lead**: Liezl talks to it directly, and it hands self-contained tasks to sub-sessions (case generation, Modal runs, Adaption jobs, scoring, report sections) and checks what comes back.

## 1. Where the history is

- **Previous session ID:** `45c42833-7b2e-400d-aea0-39ab63c7f4db`
- **Full transcript, including everything before its compaction:** `C:\Users\Liezl\.claude\projects\C--Users-Liezl-Documents-Obsidian-06-Strategy-competitions\45c42833-7b2e-400d-aea0-39ab63c7f4db.jsonl`. It is large; grep it for a keyword (`Grep` on the file, e.g. "togethercomputer", "McNemar", "WhatsApp") instead of reading it whole.
- **Memory index:** `C:\Users\Liezl\.claude\projects\C--Users-Liezl-Documents-Obsidian-06-Strategy-competitions\memory\MEMORY.md` (repo rules, secrets location, "just do the obvious next step").

Read in this order, then stop reading and ask Liezl what she wants first:

1. [PROJECT-ANGLES.md](./PROJECT-ANGLES.md): the design, trial results, the November 12 proposals, and every team decision. Source of truth; where the brief differs, this wins.
2. [fable.txt](./fable.txt): the Fable pass that produced the November 12 proposals (summarised below).
3. [training-trial/README.md](./training-trial/README.md) and [results](./training-trial/results/test_a_results.md): the pre-sprint trial.
4. [toy-run/RUN-LOG.md](./toy-run/RUN-LOG.md): the toy run and Deepayan's load test.
5. [README.md](./README.md) and the [team brief](./ai-epistemics-team-brief.html), if needed.

## 2. What exists

- **Repo:** this folder is git repo `LiezlC/ai-epistemics-sprint` (private, `main`). Deepayan and Prashanth are collaborators. Papers (`papers/*.pdf`, `papers/adjacent/`, `papers/text/`) and checkpoints stay out of git. Held-back variants and the answer key never go in before the prompt freeze.
- **Team:** Liezl (rubric, answer key, launches Adaption jobs), Deepayan Sinha (owns the run: prompts, models, scoring; writes any fine-tune training cases), Prashanth Vijay (held-back contradiction variants, answer-key check, Zhou/Bara novelty line). Team chat is WhatsApp; Liezl pastes it in. Shared Drive folder: https://drive.google.com/drive/folders/1KU111BqP6CiYEKcQtC8zCouDVh5ilSyO
- **Sprint:** Apart AI x Epistemics, November 13–15, 2026. Submission closes November 16, 1:59 p.m. SAST. Requirements are in PROJECT-ANGLES.
- **Pre-sprint trial (prior work):**
  - `training-trial/generate_cases.py` makes scripted cases; `check_cases.py` re-derives every answer from the packet text (0 mismatches); `build_review.py` makes the 20-case human check (Liezl passed all 20).
  - Adaption run `50993f1c`, Qwen3.5-4B LoRA r16/alpha32, 1 epoch, lr 5e-5, one iteration, 32 minutes, no credits charged. Adapter at GitHub release `provenance-trial-adapter`; toy adapter at `toy-run-adapter`.
  - `eval_modal.py` runs three arms on Modal (L40S, vLLM 0.32.0, greedy, thinking off): untuned zero-shot 32/60, untuned three-shot 48/60, tuned 54/60. Tuned vs three-shot: 7 fixed, 1 broken, p = 0.07 (suggestive). `score_test_a.py` scores it.
  - Headline: a false "independent" label fools both models (tuned 1/6, three-shot 2/6); a false "same source" label fools neither (6/6).
- **Tools and keys:** Adaption via MCP connector or REST (`https://api.prod.adaptionlabs.ai/api/v1`, key in `C:/Users/Liezl/tools/.secrets/adaption.env`); Hugging Face account `khayali` (private datasets import through Adaption's connected account); Modal CLI configured; `gh` logged in as LiezlC. Run GPU work on Modal, never on Liezl's local GPU. Never print secrets.

## 3. The Fable inputs

Fable read the raw Test A outputs and found that in 3 of the tuned model's 5 failures on a false "independent" label, it cites the one shared root record and still answers "independent". So the model traces the trail and then defers to the label. Its four proposals, now in PROJECT-ANGLES as "Proposed additions (November 12)":

1. **Split the headline rate:** traced the right root and followed the label anyway, versus never traced it (the MASK knows-versus-says split). Two cheap arms: no label; roots asked for before the label is shown.
2. **Three label forms:** bare ("independent"), authority-stamped ("verified independent by audit"), literally true but misleading ("Report 1 cites R-6353, Report 2 cites G-7611"). Track 2 payoff: provenance labels as an attack surface; labels should point to records, never state conclusions.
3. **Training signal:** supervised tuning left the failure in place; try Adaption preference pairs (DPO) and reasoning traces, then check for over-correction on label-only packets.
4. **Shared conduit, separate observations:** separate witnesses relayed through one scribe or interpreter in near-identical wording; the error that erases complainants.

Lead's view: 1 and 2 are cheap and give the report its spine; Deepayan backs both. 3 depends on Friday's fine-tune decision and the case budget. 4 only if time allows. One caution for 2: if Deepayan's training cases include all three label forms, the fine-tune result says nothing about whether the literal-but-misleading form transfers untaught. Consider holding that form out of training so it tests transfer. Also still unread: arXiv 2606.09005 (retrieved text impersonating provenance signals); someone should read it before the report claims novelty.

## 4. Open items, as of the evening of November 12

- Prashanth: pick option (a) or (b) for the label forms; send the Zhou/Bara novelty line.
- Friday decisions are listed at the end of PROJECT-ANGLES "Decisions".
- Deepayan writes training cases Friday morning, freezes the prompt end of day Friday.
- Test B cases are written during the sprint; reuse `eval_modal.py` and `score_test_a.py` with a new data path.

## 5. Working rules with Liezl

- Read `C:/Users/Liezl/.agents/LIEZL.md`, `SOUL.md`, and `VOICE.md` first. Anything going out in her name (WhatsApp, report) follows VOICE.md: no em dashes, no "not X but Y", no triplets.
- Do obvious next steps without asking. Check `tools/.secrets` before saying a key is missing.
- Never `cd` in Bash. Links use `./` paths relative to the session's launch folder, `%20` for spaces.
- Push only to `LiezlC/ai-epistemics-sprint`; commit messages end with the attribution line the app supplies.
