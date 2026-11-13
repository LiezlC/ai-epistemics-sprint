# Freeze record: label-form templates (13 Nov 2026)

Frozen at 2026-11-13 14:36 UTC on the user's instruction ("Template wordings look good - freeze it"). This freezes the label-form TEMPLATES only. The prompt text, the other scripts, the second-turn wording and the training files are not frozen yet.

| File (in `plans/Epistemics Sprint/sprint-generator/`) | sha256 | Status |
|---|---|---|
| `label_form_templates.json` | `14572f3244ccbeb91c3a1fad61d5627ab264a521a30909286c6df59222c7992d` | **FROZEN** 14:36 UTC |
| `make_label_forms.py` | `82e234ddcb9a758448d661e45f89ba2b7675f0540b6385404a3b152eaa39bdff` | as of 14:36 UTC; not frozen (reads the templates, not part of the wording) |
| `test_make_label_forms.py` | `51d2afdf13411df8edd4218e3833223a5025431f695ed2e5615f322dd071ef42` | as of 14:36 UTC |
| `gen_sprint_cases.py` | `33d914c24cceb5d5ddf139f105a9f00311be54a389f01b3a2dac375fd579b167` | as of 14:36 UTC; will change if the instruction text changes |
| `check_sprint_cases.py` | `64a97bca30b0242e5e2042b0cd1210d4d33b1a016465dd484f58790bf8edfda5` | as of 14:36 UTC |

Update, 15:09 UTC: `make_label_forms.py` and its test were changed after Prashanth said his records are listed as `ID (type): "text"` (the script first assumed the trial layout `[ID] Type. text`, and would have silently skipped the misleading form on his packets). It now reads both layouts, derives the root by his rule (the record the others cite that cites none), and classifies a hand-written bare label by words when clear. The templates file is unchanged (same sha256, still frozen). New hashes: `make_label_forms.py` `7ff4a2ff061c8d2c308ba0a4ebab35cfde2b405354dcfbc8a8cf0077ae93a9e5`, `test_make_label_forms.py` `52abbf1e35d46852de38fae105928b97cff947f23d21ccafdaff1931b5a19878`. Tests pass on generated cases in both layouts. Prashanth's variants not opened.

Notes
- Hashes are of the file bytes on this machine. The templates file has Windows (CRLF) line endings here; a copy with different line endings hashes differently, so verify with `sha256sum` on the same file and re-hash if it is ever copied or committed through a tool that rewrites line endings.
- The frozen wordings: stamped "Handoff note: verified independent by audit. These two reports come from independent sources." (shared counterpart in the file); misleading "Handoff note: Report 1 cites {id1}, Report 2 cites {id2}.", used only where the bare label says independent and the records show a shared root with two different cited IDs.
- Prashanth's variants had not been opened when this was frozen (he had written 3 and said he would post "variants done" with a sha256 later). The script has been run only on generated cases.
- To be posted in the group with the prompt hash before 23:59 UTC, before his variants go into the repo and before Liezl releases the rubric. Not posted yet.

## Update 13 Nov 2026 (after the headroom re-run): no-label arm added to the script
`make_label_forms.py` now also writes a `none` form (the handoff line removed, one adjacent blank line with it), the no-label arm the headroom re-run showed is needed to separate label pull from baseline error. The templates file is unchanged (sha256 `14572f3244ccbeb91c3a1fad61d5627ab264a521a30909286c6df59222c7992d`). Tests pass (trial layout: all packets, nothing else changed; the `none` form is not yet tested on Prashanth's layout, only the stamped and misleading forms are). New hashes, replacing those of 15:09 UTC:
- `make_label_forms.py`: `bc930226c028fa6dcf1e41f2be6c6ab4db7f61b9368687c56021b4a99900d3a2`
- `test_make_label_forms.py`: `5dc367d81677d9af211886bc48c8c716740665b4a0146f6568a9dc95cb8b3ea2`
Post these (not the earlier two) with the freeze note.
