# Label or Record? Video voiceover (draft)

About 3 minutes at a calm reading pace. Each scene is one visual beat. The spoken text follows the plain-language report; the numbers match `report/draft-report.md`.

---

**Scene 1. A file and a sticky note** *(visual: a grievance file, a handoff note on top reading “these two reports are independent”)*

When an AI reviews evidence, someone has usually handed it a summary first. Two witnesses who saw something separately make a claim stronger. Two reports copied from one logbook entry make it just as strong as that entry. We asked whether AI reviewers believe the note or check the records.

**Scene 2. Following the trail** *(visual: two reports, arrows back through records to one root, or to two)*

Each test gives a claim, two reports, a note and the records behind them. A careful reviewer follows each report back to the person who saw the event. Same source, or separate sources. And where the records run out, the honest answer is “I can’t tell.”

**Scene 3. Locking the test** *(visual: a padlock, a hash string, a timestamped commit)*

Before running anything, we fingerprinted the cases and the answer key and posted the fingerprints to the team. Answers were saved before anyone scored them, so the test could not bend to fit the results.

**Scene 4. Easy cases, then traps** *(visual: a scoreboard near the ceiling, then a maze of records)*

Fifteen hand-written cases proved too easy. So we built sixty harder ones, full of traps. The big model walked past nearly all of them, and flipping the note changed its answer in 3 of 55 pairs. It stumbled in one place. When a record in the chain was missing, it never said “I can’t tell.”

**Scene 5. Holes in the evidence** *(visual: records with a torn-out page, an unsigned note, a hearsay line)*

So we built cases with holes in them, and twins with the holes filled. The notes did not fill the holes. The models did, by guessing, with or without a note. Of six models, one said “I can’t tell” at a useful rate.

**Scene 6. Teaching a small model** *(visual: a small model, pairs of answers marked better and worse)*

We trained a small model on pairs of better and worse answers. The first attempt learned to say “I can’t tell” to everything, because that answer was never once marked as the worse one. Balancing the file fixed it, and the small model jumped from 66 to 86 percent on the hard cases, close to a model seven times its size.

**Scene 7. A faster loop** *(visual: a circular arrow: count, train, test, revise)*

Then we switched to quick rounds: count the training file, train for twelve minutes, test on practice cases, change one thing. A pattern held. Each change that sharpened source tracing also made the model easier to sway with a note.

**Scene 8. The finding** *(visual: a hole in the records, a note sliding in to fill it)*

The best of those rounds learned to say “I can’t tell” far more often than any other trained model. And in that model, the note started to matter. Handed a “same source” note, it gave up on “I can’t tell” and took the note’s word: 23 percent of gap cases against 40 percent with no note. Models that never saw the holes left nothing for a note to fill. Labels can only fill gaps a reviewer can see.

**Scene 9. Close** *(visual: the file closes; one line on screen)*

So the lesson for anyone building AI reviewers is to teach honesty about gaps and resistance to labels together, and to point handoff notes at records instead of conclusions. A reviewer that never says “I can’t tell” will sooner or later tell you about a source that was never there.
