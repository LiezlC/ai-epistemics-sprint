# Review check sheet: report at 32cfb32 (sha256 baaaab88…bd60)

Reviewers so far: Codex and Fable. Kimi K3.1 Pro is still running and will be added. Tick what I should fix. Unticked items stay as they are.

## Both reviewers flagged these (strongest)

- [ ] **1. Round 3's "+0.10 [0.01, 0.19]" is in the wrong column.** In Table 12 and Table 10, that column is "gaps minus controls" for each arm. The round 3 number compares round 3 with other arms. Fix: give round 3's own gaps-minus-controls value in the column, and state the +0.10 comparison in a sentence that names the arms it is against.
- [ ] **2. "In no arm is label pull larger on gaps… every interval includes zero"** says the opposite of the round 3 row. Fix: "For the seven arms outside the loop, every gaps-minus-controls interval includes zero."
- [ ] **3. "Exclude a large label pull but not a modest one" is too strong.** Cells hold 4 to 9 cases, so upper bounds reach 30 to 70%. The "0 of 99 rows" count also uses the wrong denominator: only 61 rows carry a false label. Fix: "Label-following was rare, but with 4 to 9 cases per cell, only a near-universal pull is excluded." The 27b followed "none of 61 false labels".
- [ ] **4. Loop trade-off: "every gain in tracing came with more label sensitivity"** (Abstract, 5, 6). Round 3 has fewer flips than round 2. Every round flips more than the untuned model. Fix: "On the development set, every pilot round (one seed each, no intervals) beat the untuned model on roots and also flipped with the label more often (13.6 to 25.3% against 8.4%)."
- [ ] **5. Round 3 "the only tuned arm to abstain on broken chains / most on gaps"** ignores v1, which abstained everywhere. Fix: "the only tuned arm except the collapsed v1". Also write 0.38 as "3 of 8".
- [ ] **6. Gap-set headline uses all 40 bundles**, including the 10 mis-keyed ones where "shared" is right. Fix: lead with the 30-bundle numbers, or add "(on the 30 bundles kept after the audit: …)" in the Abstract and 4.4. 5.1 also says the audit "found 10 mis-keyed". It found 2 directly and the other 8 by the same pattern. Fix that wording.
- [ ] **7. Leftover placeholders:**
  - the E.8 `TBD` on key format conversion. I need your answer, or I delete the sentence.
  - Appendix I `[Proposed reading:]` and `[One short paragraph…]` markers.
  - H.6 "Reading so far".
  - "(Liezl's statement; Appendix)" with no letter.
  - Fix: delete the markers and keep the text.
- [ ] **8. Stale H.4 text:** "the label fills the gap. This is the pattern the study was designed to find" contradicts 4.4. "Deep chains… all score perfectly" is wrong (F2 is 13/14). Fix both, and write "v1" where "tuned" means v1.
- [ ] **9. Broken section references** to old numbers:
  - Appendix A "3.15" goes to H.1.
  - H.5 "4.8" goes to H.6.
  - Appendix C "4.3" goes to E.11 or I.3.
  - H.1 "5.1" goes to 5.2.
  - Table 7 "3.11/3.12" goes to F/E.11.
  - I.5 points to second-turn output that is not in Appendix C.
- [ ] **10. "66 of 99 roots right"** is the joint verdict-plus-roots score (Codex). Fix: call it "verdict and roots both right" wherever it appears. Also drop "right by luck, as in a Gettier case" (both reviewers).

## One reviewer only

- [ ] **11. (Fable) Authorship is inconsistent across sections.**
  - 3.4 says "Liezl wrote the answer key".
  - Appendix G says "Prashanth's 15 variants… written".
  - Appendix A says the variants were blind-checked by Liezl; you checked the key.
  - Fix: use one wording everywhere.
- [ ] **12. (Fable) Abstract's last sentence states the design advice as a result.** Fix: "We suggest, untested here, that handoff labels point to records."
- [ ] **13. (Fable) Related Work says "replicates and extends Hu"**, but our arm showed no authority effect. Fix: "adapts Hu's manipulation".
- [ ] **14. (Fable) Abstract "only 34 of 54"** should add "(42 of 54 once repeated record IDs are removed)".
- [ ] **15. (Fable) Jargon a cold reader meets undefined:** DPO, LoRA, "11:59 checkpoint", "key release", "kept/quarantined". Fix: one short gloss each at first use.
- [ ] **16. (Fable) Table 11 round 4 shows 25.3% in two adjacent columns.** Possibly a copy error; I'll check against ROUNDS.md.
- [ ] **17. (Codex) "All cases share one fictional setting (site gate, guard log)"**, but v004 is about pallet loading. Fix: "fictional operational-record packets with one shared structure".
- [ ] **18. (Codex) Second turn: "Sound verdict: revise"** treats the disputed new-inspection key as correct. Fix: "keyed response".
- [ ] **19. (Codex) E.11 "No frozen file was edited"** sits beside a patched `build_second_turn.py`. Fix: state which builder version made the scored rows, and count the patch as a deviation.
- [ ] **20. (Codex) "p > 0.05 suggestive" rule** reads as treating a null result as evidence. Fix: delete the blanket rule.

## Not for me to decide alone

- Items 3, 4 and 6 change the Abstract, which is at 250 words. Each fix swaps wording and adds none, but Prashanth and Deepayan should see the new Abstract.
- The 8-page check is still with Deepayan.
