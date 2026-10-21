# Provenance

The Fatima form asks applicants to do this analysis themselves. This file records who did what.

## Mine (Chamel)

- The research idea and motivation, from my own CNAS → CASNOS Chifa experience.
- The half-page proposal in `docs/proposal.md`.
- TODO: the evaluation cases in `data/cases.csv` (rows with `written_by = chamel`), including all Darija–French text.
- TODO: the gold labels and their rationale.
- TODO: reading every raw output, the manual verdicts and error types in `results/scoring_sheet.csv`.
- TODO: the README answers to questions 1 and 3, and the conclusions.

## AI-assisted (Claude)

- Summaries of methodology papers I read for preparation (CheckList, contrast sets, prompt sensitivity, and others listed in the README).
- Planning documents I used while forming the proposal; they are not part of this repository.
- The notebook, `scripts/pilot.py` (prompt building, answer parsing, metrics) and its self-check, and the repository layout. These are infrastructure: they do not choose cases, labels or conclusions.
- First drafts of all 20 case rows in `data/cases.csv` (`written_by = ai_draft`): rules, French and Darija–French narratives, questions and gold labels. The Darija drafts follow my own romanized account of the Chifa story; the public corpora `awras/lahja-dataset-v1` and `algerian-nlp/algerian-darja-corpus` (CC-BY-4.0) were looked at for vocabulary only, and no text was copied from them. TODO (Chamel): for each row, what I checked or rewrote (set `review_status` to APPROVED, EDITED or REJECTED).
