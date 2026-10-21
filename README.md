# Temporal reasoning in Algerian Darija–French code-switched narratives

Pilot evaluation of `Qwen/Qwen3.5-4B` for the Fatima Fellowship technical challenge (Fall 2026).

> TODO (Chamel): everything under "Question 1" and "Question 3" is yours to write, in your own words. The rest of this file describes the repository and can be trimmed.

## Question 1 — The blind spot

TODO (Chamel): your motivation (the Chifa / CNAS → CASNOS story), the blind spot in one sentence, why standard benchmarks miss it.

## What I built

TODO (Chamel): number of scenario families, base/contrast pairs, languages (French, Romanized Darija–French), task types (status, event order, extraction), the two prompt formats.

## Results

TODO (Chamel): fill only from `results/metrics.json` and your own review. Show counts as numerator/denominator. Pick 2–3 raw outputs that show what happened.

| Measure | French | Darija–French |
|---|---|---|
| Accuracy | TODO | TODO |
| Contrast consistency (base and contrast both right) | TODO | TODO |

Cross-language: same answer on TODO pairs; both correct on TODO pairs.

## Question 3 — Path forward

TODO (Chamel): what the errors suggest, and the fix you propose (event extraction → timeline → answer prompting, or fine-tuning on validated Darija–French timelines), tied to the error types you saw.

## Limitations

TODO (Chamel): one model, small pilot, fictional rules, one annotator.

## Repository

| Path | Content |
|---|---|
| `data/cases.csv` | Evaluation cases: rule, narrative, question, gold answer, review status |
| `notebooks/eval_qwen35_4b.ipynb` | Colab notebook: load model, run cases in two prompt formats, parse answers, score |
| `results/raw_outputs.jsonl` | Every prompt and untouched model output |
| `results/scoring_sheet.csv` | Automatic score plus my manual verdict and error type for each output |
| `results/metrics.json` | Grouped counts |
| `results/run_config.json` | Model revision, library versions, GPU, decoding settings |
| `provenance.md` | What I did and what was AI-assisted |

Model: `Qwen/Qwen3.5-4B`, revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, non-thinking mode, greedy decoding. Weights are linked, not copied.

To re-run: open the notebook in Colab with a T4 GPU, upload `data/cases.csv`, run all cells.
