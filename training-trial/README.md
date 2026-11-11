# Minimum fine-tuning trial

Pre-sprint work, started November 11, 2026. Disclose as prior work.

## Question

Does fine-tuning make a small reviewer model better at telling shared-source corroboration from independent corroboration, and did it learn anything at all?

## Design

- **Model:** Qwen/Qwen3.5-4B, untuned versus LoRA-tuned on Adaption (same settings as the toy run).
- **Training set:** `data/train.jsonl`, 1,000 generated cases. Verdicts: 300 independent, 300 shared, 400 undetermined. Conditions: 400 consistent label, 200 label contradicts the records, 200 incomplete trail, 200 label only (no excerpts).
- **Test A:** `data/test_a.jsonl`, 60 cases from the same generator with disjoint sites and record-number ranges. Shows whether the model learned the task as taught.
- **Test B:** the hand-written sprint cases (written during the sprint, frozen before scoring). Shows whether the skill transfers. This is the result that counts.
- **Format control:** the untuned model gets three worked examples in its prompt, so any gain beyond that is skill, not answer format.
- **Scoring:** verdict accuracy, false "independent" and false "shared" counted separately, "undetermined" rate, root-record IDs checked separately, paired comparison on the same cases.

## Files

- `generate_cases.py`: seeded generator (train seed 20261111, Test A seed 20261112). `*_meta.jsonl` hold the full trail for each case.
- `check_cases.py`: re-derives every answer from the visible packet text alone. All 1,060 match.
- `build_review.py` + `review_template.html` → `review.html`: 20-case stratified human check of the training set.

## Steps

1. **Human check (Liezl):** open `review.html` in a browser, mark 20 cases, download the results JSON into this folder. Gate: no wrong verdicts. Any wrong verdict means fixing the generator first.
2. Upload `train.jsonl` as a private Hugging Face dataset and import through the Adaption connector.
3. One AutoScientist run, Qwen3.5-4B, LoRA, one iteration.
4. Run untuned (with three examples) and tuned on Test A now and on Test B in the sprint. Score with the frozen key.

## Deviation from the team plan

The team agreed on November 11 that no case files exist before Friday and that Deepayan writes training cases. This trial generates training cases now, from a script in the gate-and-log setting. Test B, the rubric and the answer key are untouched: they are still written during the sprint. Confirm in the group before step 2.
