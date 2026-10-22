# Temporal Reasoning in Algerian Darija–French Code-Switched Narratives

Pilot evaluation of `Qwen/Qwen3.5-4B` for the Fatima Fellowship technical challenge (Fall 2026).

## Question 1 — The blind spot

As an Algerian, I often communicate using a mixture of Algerian Darija and French, especially when discussing administrative procedures. When I tried to switch my Chifa card from CNAS to CASNOS after getting my auto-entrepreneur status, I was sent between offices and eventually had to travel around 500 km to Algiers without knowing which documents to bring. CASNOS later told me everything was good, yet my card still did not appear on Damancom even though I could use it normally at pharmacies. This made me wonder whether an AI model could understand the story as I would naturally tell it.

Most benchmarks are in Modern Standard Arabic or English, not Darija the way we actually write it. The model reads Darija facts fine but fails on time connectors. My Chifa case passed, but the failure was in event order.

## What I built

- 4 scenario families with fictional institutions and an explicit rule each, so every gold answer can be checked from the text alone. Each family has a base story and a contrast story where one fact or connector changes the answer.
- Every story in two meaning-matched versions: standard French and Romanized Algerian Darija–French.
- Three task types: status inference (`CONFIRMED_ACTIVE` / `CONFIRMED_NOT_ACTIVE` / `INSUFFICIENT_EVIDENCE`), event ordering, and simple reading checks.
- Every case run in two prompt formats (plain and `###`-sectioned) with the same content: 20 cases × 2 formats = 40 outputs.
- Qwen3.5-4B, non-thinking mode, greedy decoding, on a free Colab T4. Failures were rerun once with thinking mode on, as a diagnostic.
- I read every output and judged it by hand (`results/scoring_sheet.csv`).

## Results

| Family | What it tests | French | Darija–French |
|---|---|---|---|
| F1 | File accepted vs rights started | 4/4* | 4/4* |
| F2 | Online portal vs pharmacy use (my Chifa story) | 4/4 | 4/4 |
| F3 | Certificate issue date vs printed end date | 3/4 | 3/4 |
| **F4** | **Events told out of order** | **4/4** | **0/4** |
| S1, S2 | Reading checks | 4/4 | 4/4 |
| **All** | | **19/20** | **15/20** |

\* F1 contrast: after reading the outputs I accepted both `CONFIRMED_NOT_ACTIVE` and `INSUFFICIENT_EVIDENCE` (see Limitations).

Overall 34/40. Prompt format A 18/20, B 16/20. Base and contrast both correct: 12/16. Errors I labelled: language 4, inference 1, format 1 (`results/metrics.json`).

Thinking-mode reruns of the failures (diagnostic, not counted above): F3 contrast fixed in both languages; F1 contrast unchanged; all 4 F4 Darija–French reruns used the full 4,096-token budget without reaching an answer.

F4 Darija–French rerun with my glossary of time connectors in the prompt (`data/glossary.txt`, non-thinking, same settings): 0/4 correct (without it: 0/4); 2 of the 4 outputs were cut off at 384 tokens without an answer; in one output (base, format B) the Tlemcen visit and the trip are now in the right order but the download and the diploma copy are still swapped (`results_glossary/`).

The glossary alone isn't enough; it copies my words literally.

### One story, two languages

Same facts, same question (F4 base, format A). Gold order: E2, E1, E4, E3.

French, correct:

```text
1.  The narrator states they went to the Tlemcen office first ("l'agence de Tlemcen, où j'étais allé en premier"). This corresponds to **E2**.
...
3.  Finally, they downloaded the certificate from the website "three hours after" handing in the copy. This corresponds to **E3**.

ANSWER: E2, E1, E4, E3
```

Darija–French, wrong:

```text
3.  **"ba3d ma meditlhom la copie ta3 le diplôme f l'agence ta3 Alger"**: After downloading, they handed in the diploma copy at the Algiers office. This corresponds to **E4**.
4.  **"Tl3t l Alger psk l'agence ta3 Tlemcen"**: Later, the narrator went to the Tlemcen office. This corresponds to **E2**.

ANSWER: E1, E3, E4, E2
```

From the thinking-mode rerun of the same case (format B):

```text
Wait, one detail: "3 sway3 men ba3d ma". "3 sway3" means "3 times". "men ba3d ma" means "after".
```

Thinking more doesn't help when it doesn't know the word.

## Question 3 — Path forward

I added a glossary to Qwen's prompt because it failed all the connector cases. It didn't work: Qwen copied my words literally. The model didn't fix its errors with thinking because it doesn't know the words, maybe because the tokenizer doesn't have them as single tokens, so their meaning isn't stored in the embedding space. For example, *après* is one token, while *ba3d* is split into `ba`, `3`, `d`. Next, I would fine-tune the model after curating a better, large-scale dataset that matches what I wrote myself.

## Limitations

- One model (Qwen3.5-4B), greedy decoding; Qwen recommends sampling for thinking mode, so the thinking reruns are a diagnostic only.
- Small pilot: the F4 result rests on one family, 4 outputs per language.
- The cases were drafted with AI help and then reviewed and edited by me, including all Darija text (`provenance.md`).
- Romanized Darija has no standard spelling; mine is one convention.
- F1 contrast: my rule did not separate "not yet active" from "unknown", and I accepted both labels after seeing the outputs.

## Repository

| Path | Content |
|---|---|
| `data/cases.csv` | The 20 cases: rule, story, question, gold answer, review status |
| `data/glossary.txt` | My glossary of Darija time connectors |
| `notebooks/eval_qwen35_4b.ipynb` | Main run: load model, run both formats, parse, score |
| `notebooks/glossary_check_f4.ipynb` | F4 Darija–French rerun with the glossary in the prompt |
| `results/raw_outputs.jsonl`, `results/raw_outputs_thinking.jsonl` | Every prompt and untouched output |
| `results/scoring_sheet.csv` | Automatic score plus my verdict, error type and notes |
| `results/metrics.json` | Grouped counts |
| `results/run_config.json` | Model revision, library versions, GPU, decoding |
| `provenance.md` | What I did and what was AI-assisted |

Model: `Qwen/Qwen3.5-4B`, revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` (weights linked, not copied). To re-run: open the notebook in Colab on a T4 GPU, upload `data/cases.csv`, run all.
