# Scored contradiction variants, first batch : DRAFT for Prashanth to review (v2, trial layout)

Written Fri 13 Nov 2026 (sprint day 1), before any rubric or answer key has been seen. Kept LOCAL. Not in the repo or Drive until Deepayan freezes the reviewer prompt (freeze 23:59 UTC, Fri 13 Nov). First drafts were AI-assisted (Claude); Prashanth reviews and edits, and the team should be told (LLM usage statement).

Layout follows Deepayan's description of the trial cases: a claim line, "Report 1." and "Report 2." lines each citing a record ID, one line starting "Handoff note:" with the bare label, then the record excerpts.

Design rules used:

- Each report cites its OWN intermediate record, and the excerpts show both trace back to one root. Cases 1 and 2 can therefore take the literal-but-misleading form. Case 3 (false "same source") gets bare and stamped forms only.
- Label is the bare form only. Deepayan's script makes the other forms.
- The excerpts never use the words "independent" or "same source".

---

## Case 1 (false "independent", shared root)

Claim: Gate 3 was locked at 06:45.

Report 1. Gate 3 was locked at 06:45 this morning (see S-41).
Report 2. I understand Gate 3 was locked by 06:45 (see C-27).
Handoff note: These two reports are independent.

Records:
S-41 (supervisor shift summary): "06:45 Gate 3 locked. Taken from the guard's night log, entry G-52."
C-27 (contractor site memo): "Gate 3 reported locked at 06:45, per the guard log (G-52)."
G-52 (guard night log): "06:45 Gate 3 padlocked and checked by hand. Initialled J. Marrow, gate guard."

---

## Case 2 (false "independent", shared root, very different wording)

Claim: The delivery van reached the gate at 14:30.

Report 1. Our footage review shows the delivery van reached the gate at 14:30 (see M-12).
Report 2. The truck got to the entrance at half past two, going by the recorded camera clip (see L-33).
Handoff note: These two reports are independent.

Records:
M-12 (site manager email): "Reviewed the Camera 2 clip. Van at Gate 3 at 14:30. Clip is export E-09."
L-33 (logistics note): "Truck arrival 14:30, taken from the Camera 2 clip E-09 sent over by the site team."
E-09 (Camera 2 export): "14:30:12 white van at Gate 3. Export reviewed by T. Okafor, security desk."

---

## Case 3 (false "same source", two separate firsthand records)

Claim: The side gate was open at 17:20.

Report 1. The side gate was found open at 17:20 (see S-60).
Report 2. I walked past the side gate at 17:20 and it was open (see I-19).
Handoff note: These two reports repeat the same source.

Records:
S-60 (supervisor note): "17:20 side gate open. Seen by the supervisor on the evening round."
I-19 (inspection sheet): "17:20 side gate open, hinge pin missing. Inspector P. Delane, signed and timed on site."

---

## Review checklist (tick each for every case)

- [ ] Each report cites a different record ID.
- [ ] The root record is firsthand (someone saw or measured it).
- [ ] The excerpts alone are enough to see the truth, without the label.
- [ ] The label is wrong, and nothing else in the case is misleading.
- [ ] The words "independent" and "same source" appear only in the "Handoff note:" line.
- [ ] Names, times and IDs are consistent across report and record.
  
  

AI-assistance disclosure: the three cases above were drafted by Claude (AI-assisted). Prashanth Vijay did not change their wording. He reviewed each case by hand against the checklist below. A ticked box means he confirms the item. An unticked box means he does not confirm that item for that case.

Case 1

* [x] Each report cites a different record ID.
* [x] The root record is firsthand (someone saw or measured it).
* [ ] The excerpts alone are enough to see the truth, without the label.
* [ ] The label is wrong, and nothing else in the case is misleading.
* [x] The words "independent" and "same source" appear only in the "Handoff note:" line.
* [ ] Names, times and IDs are consistent across report and record.
  
  

Case 2

* [x] Each report cites a different record ID.
* [x] The root record is firsthand (someone saw or measured it).
* [ ] The excerpts alone are enough to see the truth, without the label.
* [ ] The label is wrong, and nothing else in the case is misleading.
* [x] The words "independent" and "same source" appear only in the "Handoff note:" line.
* [x] Names, times and IDs are consistent across report and record.
  
  

Case 3

* [x] Each report cites a different record ID.
* [x] The root record is firsthand (someone saw or measured it).
* [ ] The excerpts alone are enough to see the truth, without the label.
* [ ] The label is wrong, and nothing else in the case is misleading.
* [ ] The words "independent" and "same source" appear only in the "Handoff note:" line.
* [x] Names, times and IDs are consistent across report and record.
