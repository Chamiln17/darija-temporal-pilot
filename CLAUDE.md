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
- [x] Chamel scored the outputs on 22 October 2026; `results/metrics.json` recomputed from his verdicts (34/40; French 19/20, Darija–French 15/20; F4 order French 4/4, Darija 0/4). F1 contrast: both NOT_ACTIVE and INSUFFICIENT_EVIDENCE accepted (gold ambiguous).
- [x] Glossary check run (F4 Darija with glossary: 0/4, `results_glossary/`). README questions 1 and 3 written by Chamel (Claude: spelling/grammar and factual sections only); provenance updated.
- [x] Chamel published the public Bucket on 22 October 2026 (00:41 UTC): https://huggingface.co/buckets/Chamiln17/darija-temporal-pilot, 24 files from commit 42184ea (CLAUDE.md left out); checked public and complete.
- [ ] Chamel pastes the link into the form and submits (deadline 22 October 2026, 12:59 Algiers).

## Layout

`data/cases.csv` cases · `notebooks/eval_qwen35_4b.ipynb` Colab run · `scripts/pilot.py` parsing and metrics · `results/` outputs · `README.md` the Bucket's front page · `provenance.md` who did what.
