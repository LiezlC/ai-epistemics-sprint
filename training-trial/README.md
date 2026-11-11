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

## Human check, v1 (November 11)

Liezl checked 20 stratified v1 cases (`review/case-check-results-2026-11-11.json`, sheet in `review/review-v1.html`, data in `data/v1/`). All 20 verdicts and root IDs correct, all marked fit to train on. Notes led to three generator fixes in v2:

- **Wording was labeled, not measured.** In v1, "varied" only meant two templates were drawn at random, often the same one: median content-word overlap was 47%, with some at 100%. v2 measures overlap (content-word Jaccard, record IDs and role prefixes removed) and only accepts **near identical at 80% or more** and **varied at 35% or less**. v2 adds four report templates and three paraphrases per claim. Measured: near identical pairs all 100%, varied pairs 4–33%. The score is stored per case as `overlap`.
- **Name collisions suggested links that were not there** (case 6). v2 never reuses a person's name within a case.
- **Dead-end notes could read as firsthand** (case 14). v2 dead ends say the writer was not on site and gives no source.

Verdict logic is unchanged, and the independent re-derivation still matches all 1,060 v2 answers. Near-identical wording now also appears on shared-source cases (25%), so wording cannot be used as a shortcut in either direction.

## Deviation from the team plan

The team agreed on November 11 that no case files exist before Friday and that Deepayan writes training cases. This trial generates training cases now, from a script in the gate-and-log setting. Test B, the rubric and the answer key are untouched: they are still written during the sprint. Confirm in the group before step 2.
