# Sprint talks: insights for the report

From the sprint talks and their slides, plus the papers two speakers cited. Each entry gives the point, how it bears on our results, and where it might go in the report. All are optional; the first four are the strongest fits. Quotes are paraphrased from the transcripts, so cite the talks as talks (speaker, AI x Epistemics Research Sprint, 13 to 15 Nov 2026) and the papers as papers.

## 1. Response pressure explains over-commitment (Orestis Palermos, “Artificial Knowing”)

Palermos argues that a language model taken on its own is reliable but cannot be epistemically responsible. It checks its output for internal coherence but has no way to detect when the grounding is missing. He names the cause **response pressure**: models are optimized to answer rather than fall silent, so when no candidate answer is well supported, the model still picks the most probable one and states it fluently. In his words, fluent generation is not truth tracking.

**Bearing on us:** this is our gap-set result, stated as a mechanism. On cases where the records cannot settle the question, four of five untuned models gave a firm verdict almost every time, with or without a label. Our study gives response pressure a measurement in one setting. His “responsibility” condition is the ability to detect defeaters: a broken chain is a defeater the models failed to register.

**Where:** Section 1 or 5, one or two sentences framing over-commitment as response pressure, citing the talk. He also argues that grounding comes from the wider socio-technical system (feedback, evaluators), which supports our design recommendation: the pipeline, not the model alone, should make the gap visible, by having labels point to records.

## 2. Right verdict, wrong root is a Gettier case (Joel Suro, “Knowledge definitions and safety alignment”)

Suro walked through Gettier cases: a belief that is true and justified but true by luck, like reading the right time off a stopped clock. A lucky guess on an exam earns full marks without being knowledge.

**Bearing on us:** the untuned 4B on the main set is right on the verdict in 97 of 99 rows but names the right root in only 66. Where it names the middle record as the root and still says “shared”, it reaches the right verdict through a wrong chain, which is the Gettier pattern. This is the epistemic case for scoring roots separately from verdicts, and for reading v2’s gain (roots 66 to 96 of 99, verdicts unchanged) as a gain in knowledge, not in accuracy alone.

**Where:** Section 3 (why roots are scored) or 4.2 (the roots result). One sentence.

## 3. Acknowledging uncertainty is not detecting error (Keivan Navaie, “Epistemic norms for AI safety and alignment research”, *Artificial Intelligence Review*, 2026, doi:10.1007/s10462-026-11666-8)

Navaie lists five places where evidence for a safety claim can fail: target, visibility, verification, unknowns and culture. In a small pilot, 9 of 10 papers discussed limitations but none of the 10 had independent verification. His line: acknowledging uncertainty is not the same as engineering a process that can detect error. His framework (ECAISA) asks for inspectable evidence, claims proportionate to evidence, attempts to break the claim, and a clean separation of evidence from conjecture. He presents it as an auditable research record, not a certificate.

**Bearing on us:** our protocol already does much of this: hashes before runs, raw outputs committed before scoring, frozen scorers, a blind key check, round 3 demoted to a lead. It also names our weak spot. The exploratory sets were checked by models, and model validators are not independent verification: they share habits, which is our own finding. And the two process lessons in our discussion (the v1 flaw visible only in file totals, the key flaw found by one human audit) are examples of a process built to detect error.

**Where:** Section 5, the “checks” paragraph. Cite the paper; it gives our process lesson a published frame.

## 4. Read the traces, and newer models are not always better judges (Owen Cotton-Barratt)

Cotton-Barratt’s advice for AI-for-epistemics builders: when a pipeline of model calls gives a weak result, read the intermediate traces and ask whether each step was sensible. Hold outputs to a high standard instead of accepting “in the vicinity”. His group’s Judgment Bench, which tests how well models judge other models’ answers, found that newer models are not always better at it.

**Bearing on us:** our v1 collapse surfaced only when someone opened the training file behind an odd result. And our design used models as validators (the hard set) and as a critic (the training loop), and Codex’s predictions in the loop missed twice. That is consistent with his point that model judgment needs checking.

**Where:** Section 5 or Appendix J, a clause in the checks paragraph. Optional.

## 5. Labels are context we put in (Dean Issacharoff, VSIN visual investigations)

Issacharoff builds AI tools that describe large media archives for investigators. Two points carry over. The descriptions a model writes depend on the context it is given, so investigators must watch the biases they put in, as well as those inside the model. And model confidence scores are hard to read (“what does 42 percent mean?”).

**Bearing on us:** a handoff label is that kind of injected context, and our real-world motivation is pipelines where one AI step hands a summary to the next. His setting, AI-generated descriptions feeding human investigators, is a live example of the pipelines our introduction describes. The confidence point supports asking for an explicit “undetermined” instead of reading confidence.

**Where:** Section 1, one example of where handoff labels arise. Optional.

## 6. Trusted sources and feedback loops (Jonathan Stray; Stray et al., “Political Neutrality as Balanced Approval”, arXiv:2605.28911)

Stray models conflict escalation as a feedback loop with bad information, inside an epistemic system of humans and machines. Societies need some sources that people who disagree both trust. The paper defines AI neutrality as responses that win approval across opposing groups, tested with 7,434 participants.

**Bearing on us:** this is a weak fit. If AI reviewers become sources that many people rely on, a reviewer that launders one record into two witnesses inflates apparent consensus, which is the mechanism by which bad information feeds a loop. Possible single line in the dual-use or motivation text; skip if pressed for words.

## 7. Adaption’s win rate is its own judge (Bargav Jagatha, Adaption)

Jagatha explained that AutoScientist scores runs with a stack of LLM judges and reports a win rate. This confirms what the report already says: the 0.42 (v1) and 0.47 (v2) “gain” figures are Adaption’s judge win rates on its own data, not our metric. He also said Adaption’s dataset generator can build eval sets. Not needed for the report.

## Suggested minimum

If word budget allows only a little: one sentence on response pressure in the discussion (Palermos), one sentence on Gettier in the roots paragraph (Suro), and the Navaie citation in the checks paragraph. Together these add about 80 words and three references.
