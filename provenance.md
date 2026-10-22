# Provenance

The Fatima form asks applicants to do this analysis themselves. This file records who did what.

## Mine (Chamel)

- The research idea and motivation, from my own CNAS → CASNOS Chifa experience.
- The half-page proposal in `docs/proposal.md`.
- Reviewing every case in `data/cases.csv` and editing the Darija–French text; the glossary in `data/glossary.txt`.
- Reviewing and approving or editing every gold label (gold labels and rationales were first drafted by Claude).
- Reading the outputs and the manual verdicts and notes in `results/scoring_sheet.csv` (error types chosen by me from options Claude proposed).
- The README answers to questions 1 and 3 and the conclusions, written by me; Claude fixed spelling and grammar only and filled the factual sections (results tables, quoted outputs, repository table).

## AI-assisted (Claude)

- The tokenizer check cited in question 3 (how `Qwen/Qwen3.5-4B`'s tokenizer at the pinned revision splits *après* vs *ba3d*), run at my request.
- `results/review_pack.md`: a script-generated list of the outputs that did not match the gold label, quoted verbatim, to speed up my reading. It contains no verdicts.

- Summaries of methodology papers I read for preparation (CheckList, contrast sets, prompt sensitivity, and others listed in the README).
- Planning documents I used while forming the proposal; they are not part of this repository.
- The notebook, `scripts/pilot.py` (prompt building, answer parsing, metrics) and its self-check, and the repository layout. These are infrastructure: they do not choose cases, labels or conclusions.
- First drafts of all 20 case rows in `data/cases.csv` (`written_by = ai_draft`): rules, French and Darija–French narratives, questions and gold labels. The Darija drafts follow my own romanized account of the Chifa story; the public corpora `awras/lahja-dataset-v1` and `algerian-nlp/algerian-darja-corpus` (CC-BY-4.0) were looked at for vocabulary only, and no text was copied from them. The `review_status` column records my review of each row: APPROVED (kept as drafted) or EDITED (I rewrote part of it).
