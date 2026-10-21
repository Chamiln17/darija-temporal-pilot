# Claude entry point

Fatima Fellowship (Fall 2026) technical challenge: a pilot evaluation of `Qwen/Qwen3.5-4B` on administrative timelines told in French vs Romanized Algerian Darija–French. The application is tracked in the separate repo `E:\programming\PhD\academic-applications` (`applications/2026/fatima-fellowship/`).

**Deadline: 21 October 2026 AoE = 22 October 2026, 12:59 Algiers time.** The form needs the link to a public Hugging Face Bucket.

## Rules for the agent

The form says: "conduct the analysis yourself rather than asking an AI agent … we will reject applications that rely on generic AI-generated answers." So:

- Chamel owns the idea, the case review, reading the model outputs, the manual verdicts, and every word of the README answers to questions 1 and 3. Do not write those, do not fill `manual_verdict` / `error_type` / `my_notes`, and do not invent results.
- The agent may: fix the notebook and scripts, explain errors, help with Colab and Hugging Face upload, check facts, and keep `provenance.md` accurate about what was AI-assisted.
- Never mark rows APPROVED/EDITED in `data/cases.csv`; only Chamel does.
- Never create or upload the Hugging Face Bucket; give Chamel the commands (`docs/publish.md`).

## State (update this when a step finishes)

- [x] Proposal written by Chamel (`docs/proposal.md`).
- [x] Notebook, `scripts/pilot.py` and its self-check (`python scripts/test_pilot.py`). The notebook embeds `pilot.py`; after editing `pilot.py`, run `python scripts/build_notebook.py`.
- [x] 20 cases drafted (AI) and reviewed by Chamel on 21 October 2026: 4 families (base + contrast, French + Darija–French) and 2 sanity checks; all APPROVED or EDITED.
- [x] Notebook run on Colab T4 on 21 October 2026 (started 22:46 UTC): 40 non-thinking runs plus 9 thinking-mode reruns of failures. `results/cases_used.csv` is identical to `data/cases.csv`.
- [x] `results/` copied into the repo; `results/review_pack.md` (AI-generated, verbatim quotes only) lists the 9 mismatches and 8 extract answers to judge.
- [ ] Chamel reads the outputs and fills the scoring sheet; run the metrics cell.
- [ ] Chamel writes README questions 1 and 3 and the results section; complete `provenance.md` TODOs.
- [ ] Chamel publishes the public Bucket (`docs/publish.md`) and pastes the link into the form.

## Layout

`data/cases.csv` cases · `notebooks/eval_qwen35_4b.ipynb` Colab run · `scripts/pilot.py` parsing and metrics · `results/` outputs · `README.md` the Bucket's front page · `provenance.md` who did what.
