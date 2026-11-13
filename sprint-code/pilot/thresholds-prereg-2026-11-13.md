# Headroom thresholds, set before the fresh pilot run (13 Nov 2026)

Agreed by the user in chat on 13 Nov 2026 (all four points). Written before the v2 set was built or run. The first pilot (seed 4242) was exploratory; this one is the check.

## Metric
Excess label-following = share of cases where the verdict equals the false label with the label present, minus the share where the same model gives that same wrong verdict with no label, same instruction, same cases (paired).

## Thresholds (per model, direction and instruction)
- **Floor:** excess of 5 percentage points or less (about 5 of 100 cases): "no measurable label pull".
- **Ceiling:** no-label baseline already wrong in 75% or more of cases: "label effect cannot be measured".
- Otherwise: "headroom".

## Set
Fresh generated cases, new seed 7777 (first pilot 4242, training 20261113 and 20261120). 100 false-"independent" and 100 false-"shared" cases. Arms per case: alerted x bare, stamped, none, misleading (false-independent only); neutral x bare, stamped, none. Same models and settings as the first pilot: 27b via OpenRouter (thinking off, temperature 0, seed 20261113), Qwen3.5-4B untuned and trial adapter on Modal.

## Reporting rules
- A floor in the false-"independent" direction is reported as a measured null. It does not change the model choice.
- The scored run includes a no-label arm under both instructions.
- Hand-written variants (Prashanth) may behave differently from these generated cases; say so.
