# Test A results

60 cases. Greedy decoding, thinking off.

| Arm | Parsed | Verdict right | Verdict + roots right | False independent | False shared | Said undetermined |
| --- | --- | --- | --- | --- | --- | --- |
| base_zero | 60/60 | 32/60 | 20/60 | 3 | 25 | 9 |
| base_3shot | 60/60 | 48/60 | 46/60 | 11 | 1 | 17 |
| tuned_zero | 60/60 | 54/60 | 54/60 | 4 | 0 | 25 |

## Verdict right, by condition

| Condition | n | base_zero | base_3shot | tuned_zero |
| --- | --- | --- | --- | --- |
| consistent | 24 | 17 | 23 | 24 |
| contradiction | 12 | 6 | 8 | 7 |
| incomplete | 12 | 0 | 5 | 11 |
| label_only | 12 | 9 | 12 | 12 |

## Paired comparison with the tuned model (verdict right)

- tuned vs base_zero: tuned fixes 27, tuned breaks 5, exact McNemar p = 0.0001131
- tuned vs base_3shot: tuned fixes 7, tuned breaks 1, exact McNemar p = 0.07031

## Verdict confusion (gold → said)

- base_zero: independent→independent: 5, independent→shared: 13, shared→shared: 18, undetermined→independent: 3, undetermined→shared: 12, undetermined→undetermined: 9
- base_3shot: independent→independent: 17, independent→shared: 1, shared→independent: 4, shared→shared: 14, undetermined→independent: 7, undetermined→undetermined: 17
- tuned_zero: independent→independent: 18, shared→independent: 3, shared→shared: 13, shared→undetermined: 2, undetermined→independent: 1, undetermined→undetermined: 23

## Reading

- **Training helped.** Against the untuned model with no examples, the tuned model fixes 27 cases and breaks 5 (p = 0.0001). Against the fairer control, the untuned model with three worked examples, it fixes 7 and breaks 1 (p = 0.07): 48/60 to 54/60, suggestive at this size and not settled.
- **Where the gain came from:** incomplete trails (5/12 to 11/12). The tuned model learned to say undetermined when a trail stops at an unsourced note. The 3-shot model mostly called those independent.
- **What training did not fix:** a false "independent" label on reports that share one source. All 5 of the tuned model's contradiction errors are this case type (1 of 6 right; 2 of 6 for 3-shot). The reverse, a false "same source" label on independent reports, was 6 of 6 for both. The misleading label persuades in one direction only, which is the sprint's headline question.
- **Caveats:** Test A comes from the same generator as training, so this measures learning the task as taught. Transfer needs Test B (hand-written sprint cases). Small n: 6 cases per contradiction direction.
