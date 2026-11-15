# Label or Record? The plain version

*Draft for tone calibration and the video voiceover. Numbers marked [TBD] wait on the last runs.*

## The question

When an AI reviews evidence, it rarely starts cold. Someone has usually passed it a summary first. In a grievance file, that summary might be a handoff note saying “these two reports are independent,” which means two people saw the same thing separately. Two independent witnesses make a claim stronger. Two reports copied from one logbook entry make it just as strong as that one entry, however many times it gets repeated.

We wanted to know whether AI reviewers believe the note or check the records. Each test case gives the reviewer a claim, two reports, a handoff note and the records behind the reports. A careful reviewer follows each report back through the paper trail to the person who saw the event, then says whether the two reports share a source or stand on separate ones. Where the records are too incomplete to tell, the right answer is “undetermined.”

## Keeping ourselves honest

Before running anything, we locked the test cases and the answer key with a digital fingerprint (a hash) and posted it to the team. Every model’s answers got fingerprinted and saved before anyone scored them. That way the test cannot drift to fit the results, whoever is tempted.

## Fifteen easy cases

A teammate wrote fifteen cases by hand, with AI help, and checked each one. Claude drafted the answer key, and Liezl checked it blind, without seeing the draft first. They agreed on all fifteen.

The larger model, Qwen at 27 billion parameters, got every case right. The small one, at 4 billion, got the verdicts right almost every time but often stopped one step short on longer paper trails, naming a middle record as the source. The handoff note hardly moved either model. The cases were too easy to show much, so we built harder ones.

## Harder cases

Sixty new cases, each run twice with the note flipped and everything else identical. They carried traps: longer trails, records with look-alike numbers, a late inspection that copied the original, and a record that falsely claimed to be “independently confirmed.” AI models built the cases from a fixed blueprint, so the right answer existed before any wording did, and three other models checked them.

The big model walked past almost every trap. Flipping the note changed its answer in only 3 of 55 pairs. It failed in one place. When a record in the chain was missing, it never said “undetermined.” It picked an answer anyway, and in two of four cases the note picked it.

## The gap test

That hinted at a sharper idea: maybe notes only matter when the records leave a hole. So we built forty cases where the records could not settle the question (a missing record, an unsigned one, a hearsay one, an unclear one), each with a twin where the hole was filled, and ran each with no note and with each kind of note.

The idea did not survive. Notes did not fill the holes. The models filled them on their own, mostly by guessing “shared,” with or without any note to lean on. Of six models, only one (Kimi) said “I can’t tell” at a useful rate.

Liezl checked ten of these cases by hand and found a flaw in our key. In ten cases, both reports led back to the same unsigned record, and the fair answer there is “shared,” whatever that record’s origin. We reported the results with and without those cases. The finding held either way.

## Teaching a small model

We also tried to teach the 4-billion model to trace sources, using a method called DPO. It learns from pairs: a better answer and a worse one for the same case.

The first attempt failed in an instructive way. The tuned model answered “undetermined” to nearly everything. The cause sat in the training file. “Undetermined” appeared thousands of times as the better answer and never once as the worse one, so the model found the one reply that never got marked down and gave it every time.

The second attempt balanced the file, and the small model jumped from 66 to 86 percent correct on the hard cases, close to a model seven times its size. It still never said “undetermined” on a broken chain. It had swung from always abstaining to never abstaining.

## A faster loop

Big training runs take hours and only show their flaws at the end. So we switched to small, quick rounds: count the training file first, train a small version in about twelve minutes for about a dollar, test it on practice cases kept apart from the real tests, and have another AI propose one change, which Liezl approved or rejected.

The count caught the first attempt’s flaw before training even started. Four rounds later, a pattern held steady. Every change that taught the model to trace sources better also made it more swayed by the note. Teaching the skill and teaching indifference to the label pulled against each other. The best round, scored on the real tests: [TBD].

## What it adds up to

Handoff notes sway these models less than we expected, on easy cases and hard ones alike. The bigger weakness is overconfidence. Most models give a firm answer when the evidence has a hole in it, and they will do it with no note at all.

Teaching a model to say “I can’t tell” is harder than it looks. Get the training data slightly lopsided and it says it about everything. Fix the balance and it stops saying it where it should.

The checks taught us something too. Counting the totals in a file and chasing odd results caught more than case-by-case review. Three agreeing models are not three independent opinions, which is this study’s own point turned on its makers. One careful human look found the flaw that the automated pipeline passed.

A reviewer that never says “I can’t tell” will sooner or later tell you about a source that was never there.
