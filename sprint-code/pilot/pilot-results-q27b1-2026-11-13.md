# Pilot results: qwen/qwen3.8-27b, run q27b1 (13 Nov 2026)

Exploratory. The user approved the run but had not yet set the floor and ceiling thresholds for the headroom check, and the table printed when the run finished, so no threshold was fixed before the results were seen. Read this as a pilot, not as a pre-registered check.

- **Setup:** 520 non-scored generated packets (`make_pilot_set.py`, seed 4242), OpenRouter route `qwen/qwen3.8-27b` via Modal secret `openrouter`, temperature 0, seed 20261113, thinking off, lenient first-JSON parse. Preexisting `con-artist/providers.py` reused unchanged (see `PROVENANCE.md`).
- **Operations:** 520 calls, 0 errors, 0 unparseable, 0 reasoning tokens (thinking off honoured), mean 389 tokens in and 29 out, cost reported by the API USD 0.042 in total. Files: `runs/q27b1/results.jsonl`, `summary.json`.
- **Cases:** 40 false-"independent" label (records show one root), 40 false-"shared" label (records show two roots), 20 label-only, 20 incomplete trail; each in the forms below. Cells are small (n = 40 or 20); counts only, no significance claims.

| Instruction | Condition or direction | Label form | n | Right | Follows label | Said undetermined |
|---|---|---|---|---|---|---|
| alerted (trial wording) | false "independent" | bare | 40 | 40 | 0 | 0 |
| alerted | false "independent" | stamped | 40 | 40 | 0 | 0 |
| alerted | false "independent" | no label | 40 | 40 | n/a | 0 |
| alerted | false "independent" | misleading (cites two IDs) | 40 | 40 | 0 | 0 |
| neutral | false "independent" | bare | 40 | 40 | 0 | 0 |
| neutral | false "independent" | stamped | 40 | 40 | 0 | 0 |
| alerted | false "shared" | bare | 40 | 24 | 16 | 0 |
| alerted | false "shared" | stamped | 40 | 25 | 15 | 0 |
| alerted | false "shared" | no label | 40 | 27 | n/a | 0 |
| neutral | false "shared" | bare | 40 | 16 | 24 | 0 |
| neutral | false "shared" | stamped | 40 | 17 | 22 | 1 |
| alerted | label only | bare | 20 | 18 | 1 | 18 |
| tweak | label only | bare | 20 | 20 | 0 | 20 |
| alerted | incomplete trail | bare | 20 | 4 | 8 | 4 |
| tweak | incomplete trail | bare | 20 | 5 | 8 | 5 |

## What it shows (counts, my reading)
- **False "independent" is at the floor for this model.** 0 of 40 followed the false label in every form, including the literally-true-but-misleading form and the neutral prompt. This is the direction where the tuned 4B model failed in the trial (1 of 6 right), so a model this strong gives no effect to measure there.
- **False "shared" has movement.** With no label the model was right on 27 of 40 (13 wrong, all answering "shared"). With a false "shared" label it followed it on 16 (bare) and 15 (stamped). So part of the error is not the label.
- **The alert sentence matters here.** With the neutral prompt it followed the false "shared" label on 24 (bare) and 22 (stamped). Paired on the same 40 cases (bare), the alert fixed 8 and broke 0.
- **Label-only:** answered "undetermined" on 18 of 20 with the trial wording and 20 of 20 with the tweaked sentence.
- **Incomplete trails:** only 4 of 20 (trial wording) and 5 of 20 (tweak) said "undetermined"; with the trial wording 15 of 20 answered "shared". The trial's untuned models also missed these, and tuning fixed them (11 of 12), so the fine-tune arm has room to help here.

## Caveats
- Generated cases share templates with the training set, so this says how the model handles this synthetic format, not how it handles Prashanth's hand-written variants.
- The 13 wrong "shared" answers with no label show a baseline error that is not label-following; the report should separate the two.
- Greedy decoding, one seed, one model. The second Qwen3.8 variant (max-0902) cannot run with thinking off.
- Not run: Qwen3.5-4B untuned and tuned (needs Modal GPU spend), the positive control, the three-shot arm.
