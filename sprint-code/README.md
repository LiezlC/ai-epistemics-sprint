# Sprint code (written 13 Nov 2026 or later, after the AI x Epistemics sprint opened)

Everything here is sprint work unless it sits under `preexisting/`. The files listed with a hash in the freeze post of 13 Nov (11 files here, plus the two training files in `../sprint-training/`) are byte-exact: `.gitattributes` turns off line-ending conversion for this folder, so compare `sha256sum` against the post.

## Preexisting (marked, unchanged)
- `preexisting/con-artist/providers.py`: the Swarm Alignment Sprint's model-call module (6 Nov 2026), copied here byte-for-byte so the pilot can run. Not edited. The pilot imports it; set `CON_ARTIST_DIR=sprint-code/preexisting/con-artist`.
- Derived-from (not copied): `training-trial/generate_cases.py`, `check_cases.py`, `eval_modal.py` (Liezl, 11 Nov 2026) and its spot-check review template. The generator, checker, spot-check builder and `modal_4b_pilot.py` follow them; the headers say so.

## Sprint code
- `sprint-generator/`: training-case generator and checker, label-form script (stamped, literal-but-misleading, no-label), its templates and self-test, set combiner, spot-check sheet builder.
- `pilot/`: headroom pilot on non-scored generated packets: runner, scorer, Modal runners, packet builders, threshold applier, two generated packet files, results notes, `PROVENANCE.md`.
- `freeze-drafts/`: the frozen instruction and second-turn texts, and the label-form freeze record (hash history).

## Not here, on purpose
`train_meta.jsonl` (ground truth of the generated cases), run outputs, the trial adapter, scratch and cache folders. No keys: the OpenRouter key lives in a Modal secret.
