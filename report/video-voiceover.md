# Label or Record? Video voiceover (draft 2)

Target 4 minutes at a calm reading pace, about 690 words. Each scene is one visual beat. The spoken text follows the plain-language report; the numbers match `report/draft-report.md`.

---

**Scene 1. Why sources matter** *(visual: two witnesses at a gate, then one logbook with two arrows copying from it)*

Suppose two people tell you the gate was locked at a quarter to seven. If each of them saw it with their own eyes, you have two witnesses, and the claim gets stronger. If both read it from the same line in the guard’s logbook, you have one witness repeated twice. The claim is as strong as that one line, no matter how many people pass it on. Telling these apart is a basic part of weighing evidence, in courtrooms and newsrooms alike.

**Scene 2. The AI reviewer and the sticky note** *(visual: an AI reading a file; a sticky note on top saying “these two reports are independent”)*

AI systems are starting to do this kind of reviewing. They rarely start cold. Someone, often another AI, has usually passed the file along with a note on top, saying something like “these two reports are independent.” Our question was simple. Does the AI reviewer take the note’s word for it, or does it check the records underneath?

**Scene 3. How a test case works** *(visual: two reports, arrows back through records, ending at one root or two)*

Each test case gives the reviewer a claim, two reports, a note and the records behind the reports. A careful reviewer follows each report back, record by record, to the person who saw the event. Then it answers: same source, or separate sources. And where the paper trail runs out, it should say so. “I can’t tell” is a correct answer when the records leave a hole.

**Scene 4. Locking the test** *(visual: a padlock on a folder, a string of characters, a timestamp)*

Before running anything, we gave the test cases and the answer key a digital fingerprint and posted it to the team. If anyone changed a single character afterwards, the fingerprint would no longer match. Every model’s answers got the same treatment before scoring, so the test could not shift to suit the results.

**Scene 5. Easy cases, then traps** *(visual: a scoreboard near full marks, then a maze of records)*

We tested two open models from the same family: a large one, and a small one about a seventh of its size. On fifteen hand-written cases, both did well, so we built sixty harder ones, full of traps: longer paper trails, look-alike record numbers, a late inspection that copied the original, and a record falsely claiming to be “independently confirmed.” The large model walked past nearly all of them. Flipping the note changed its answer in only 3 cases out of 55. It stumbled in one place. When a record in the chain was missing, it never said “I can’t tell.” It picked an answer anyway.

**Scene 6. Holes in the evidence** *(visual: a torn-out page, an unsigned note, a line reading “I was told”)*

That gave us a sharper question. Maybe notes only matter when the records leave a hole. So we built forty cases with holes in them (a missing page, an unsigned record, secondhand hearsay, a record that names no source) and a twin for each with the hole filled. We ran six different AI models on them, with and without notes. The notes did not fill the holes. The models did, on their own, by guessing. Five of the six almost never said “I can’t tell.”

**Scene 7. Teaching the small model** *(visual: pairs of answers, one marked better, one marked worse)*

Next we tried to train the small model to trace sources, by showing it thousands of pairs: a better answer and a worse one for the same case. The first attempt backfired. The model learned to say “I can’t tell” to everything. The reason was in the training file. “I can’t tell” appeared thousands of times as the better answer and never once as the worse one, so the model found the one reply that never got marked down. Once we balanced the file, the small model jumped from 66 to 86 percent correct on the hard cases, close to the large model.

**Scene 8. A faster loop** *(visual: a circle of arrows: count, train, test, revise)*

Big training runs take hours and reveal their flaws only at the end. So we switched to quick rounds: check the training file, train a small version in twelve minutes for about a dollar, test it on practice cases, and change one thing at a time. A simple count of the file caught that first mistake before any training started. Four rounds in, a pattern held. Every change that sharpened source tracing also made the model easier to sway with a note.

**Scene 9. Where it leaves us** *(visual: a hole in the records; a sticky note hovering beside it)*

The best of those rounds learned to say “I can’t tell” far more often than any other trained model, and it caught some broken chains that even the large model missed. It also gave us a hint worth chasing. With no note, it said “I can’t tell” on 40 percent of the cases with holes. Handed a note saying “same source,” that fell to 23 percent. Perhaps a note can only fill a hole the reviewer has noticed. We treat that as a lead and nothing more: it comes from one small model, picked after many comparisons. What holds across every model we tested is simpler. Labels rarely overrode clear records, and most models guessed when the records ran out.

**Scene 10. What follows** *(visual: the file closes; one line on screen)*

So anyone building AI reviewers should test them on cases where the right answer is “I can’t tell,” and should expect honesty about gaps and resistance to labels to need training together. Handoff notes should point to records and leave the conclusion to the reviewer. A reviewer that never says “I can’t tell” will sooner or later tell you about a source that was never there.
