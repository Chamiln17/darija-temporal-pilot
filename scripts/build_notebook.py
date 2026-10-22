"""Write notebooks/eval_qwen35_4b.ipynb with pilot.py embedded. Run after editing pilot.py."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = open(os.path.join(ROOT, "scripts", "pilot.py"), encoding="utf-8").read()


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n")}


cells = [
    md("""
# Darija–French temporal pilot: Qwen3.5-4B

1. Runtime → Change runtime type → **T4 GPU**.
2. Upload `cases.csv` (from `data/`) to the Files pane on the left.
3. Run the cells in order. Generation is resumable: if Colab disconnects, re-run from the top and finished items are skipped.
4. Download `results.zip`, fill `manual_verdict` / `error_type` / `my_notes` in `scoring_sheet.csv`, upload it back, run the metrics cell.
"""),
    code("""
!pip install -q -U "transformers>=5.0" accelerate torchvision pillow
"""),
    code("""
MODEL_ID = "Qwen/Qwen3.5-4B"
REVISION = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"  # main on 2026-10-21; pinned for reproducibility
CASES_PATH = "cases.csv"
OUT_DIR = "results"
FORMATS = ["A", "B"]
MAX_NEW_TOKENS = 384          # non-thinking answers are short; truncation is flagged per item
THINKING_MAX_NEW_TOKENS = 4096
"""),
    code("# --- scripts/pilot.py, embedded by scripts/build_notebook.py ---\n" + PILOT),
    code("""
import os, sys, json, time, platform, datetime
import torch, transformers
os.makedirs(OUT_DIR, exist_ok=True)
gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
assert gpu, "No GPU: Runtime -> Change runtime type -> T4 GPU"
# T4 (compute 7.5) has no native bf16; use float16 there.
DTYPE = torch.bfloat16 if torch.cuda.get_device_capability(0)[0] >= 8 else torch.float16
run_config = {
    "model_id": MODEL_ID, "revision": REVISION, "gpu": gpu, "dtype": str(DTYPE),
    "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
    "decoding": {"do_sample": False, "num_beams": 1, "max_new_tokens": MAX_NEW_TOKENS},
    "prompt_formats": PROMPT_FORMATS, "answer_instructions": ANSWER_INSTRUCTIONS,
    "started_utc": datetime.datetime.utcnow().isoformat(timespec="seconds"),
}
json.dump(run_config, open(f"{OUT_DIR}/run_config.json", "w"), indent=2, ensure_ascii=False)
print(json.dumps(run_config, indent=2, ensure_ascii=False))
"""),
    code("""
cases = load_cases(CASES_PATH)  # only APPROVED / EDITED rows
print(len(cases), "approved cases")
from collections import Counter
print(Counter((c["language"], c["task_type"], c["variant_id"]) for c in cases))
"""),
    code("""
from transformers import AutoProcessor, AutoModelForImageTextToText
processor = AutoProcessor.from_pretrained(MODEL_ID, revision=REVISION)
model = AutoModelForImageTextToText.from_pretrained(MODEL_ID, revision=REVISION, dtype=DTYPE, device_map="auto")
model.eval()

def render(prompt, thinking):
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    return processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False,
                                         enable_thinking=thinking)

def generate(prompt, thinking=False, max_new_tokens=MAX_NEW_TOKENS):
    text = render(prompt, thinking)
    inputs = processor(text=[text], return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, do_sample=False, num_beams=1, max_new_tokens=max_new_tokens)
    new = out[0][inputs["input_ids"].shape[1]:]
    return processor.decode(new, skip_special_tokens=True), len(new)

# Check the chat template really switched thinking off: the prompt should end with an empty think block.
sample = render(build_prompt(cases[0], "A"), thinking=False)
print(sample[-300:])
assert "</think>" in sample[-60:], "enable_thinking=False did not reach the chat template; stop and check"
"""),
    code("""
RAW = f"{OUT_DIR}/raw_outputs.jsonl"
done = {(r["case_id"], r["prompt_format"]) for r in read_jsonl(RAW)}
todo = [(c, f) for f in FORMATS for c in cases if (c["case_id"], f) not in done]
print(f"{len(done)} done, {len(todo)} to run")
t0 = time.time()
for k, (c, fmt) in enumerate(todo, 1):
    prompt = build_prompt(c, fmt)
    t = time.time()
    raw, n_tokens = generate(prompt)
    parsed, status = parse_answer(raw, c["task_type"])
    append_jsonl(RAW, {"case_id": c["case_id"], "prompt_format": fmt, "thinking": False, "prompt": prompt,
                       "raw_output": raw, "new_tokens": n_tokens, "truncated": n_tokens >= MAX_NEW_TOKENS,
                       "parsed_answer": parsed, "parse_status": status, "seconds": round(time.time() - t, 1)})
    print(f"[{k}/{len(todo)}] {c['case_id']} fmt={fmt} -> {parsed or status} ({time.time() - t:.0f}s, elapsed {time.time() - t0:.0f}s)")
"""),
    code("""
import csv
by_case = {c["case_id"]: c for c in cases}
rows = []
for r in read_jsonl(RAW):
    c = by_case.get(r["case_id"])
    if not c or r["thinking"]:
        continue
    rows.append({**{k: c[k] for k in ("case_id", "family_id", "variant_id", "language", "task_type", "question", "gold_answer")},
                 "prompt_format": r["prompt_format"], "parsed_answer": r["parsed_answer"], "parse_status": r["parse_status"],
                 "truncated": r["truncated"], "auto_correct": auto_score(c, r["parsed_answer"], r["parse_status"]),
                 "manual_verdict": "", "error_type": "", "my_notes": ""})
SHEET = f"{OUT_DIR}/scoring_sheet.csv"
with open(SHEET, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print("wrote", SHEET, len(rows), "rows")
print(json.dumps(metrics(rows), indent=2))
import pandas as pd
df = pd.DataFrame(rows)
df[df["auto_correct"] != True][["case_id", "prompt_format", "gold_answer", "parsed_answer", "parse_status", "truncated"]]
"""),
    md("""
**Your review.** Read every raw output in `raw_outputs.jsonl` (not only the parsed label). In `scoring_sheet.csv` set `manual_verdict` to CORRECT or WRONG where you disagree with `auto_correct` or where it is empty (extract tasks), and `error_type` to one of: `language` (misread Darija/French), `ordering`, `inference` (facts right, conclusion wrong), `format`, `other`. Upload the edited sheet back as `results/scoring_sheet.csv`, then run the next cell.
"""),
    code("""
with open(f"{OUT_DIR}/scoring_sheet.csv", encoding="utf-8-sig", newline="") as f:
    reviewed = list(csv.DictReader(f))
m = metrics(reviewed)
m["error_types"] = dict(Counter(r["error_type"] for r in reviewed if r["error_type"]))
json.dump(m, open(f"{OUT_DIR}/metrics.json", "w"), indent=2, ensure_ascii=False)
print(json.dumps(m, indent=2, ensure_ascii=False))
"""),
    md("""
**Optional: thinking-mode rerun of failures.** Slow on a T4 (long reasoning). Greedy here; Qwen recommends sampling for thinking mode, so report this as a diagnostic, not as the model's tuned performance.
"""),
    code("""
RAW_T = f"{OUT_DIR}/raw_outputs_thinking.jsonl"
failed = sorted({(r["case_id"], r["prompt_format"]) for r in reviewed if final_correct(r) is False})
done_t = {(r["case_id"], r["prompt_format"]) for r in read_jsonl(RAW_T)}
todo_t = [x for x in failed if x not in done_t]
print(len(failed), "failures,", len(todo_t), "to rerun with thinking")
for k, (cid, fmt) in enumerate(todo_t, 1):
    c = by_case[cid]; prompt = build_prompt(c, fmt); t = time.time()
    raw, n_tokens = generate(prompt, thinking=True, max_new_tokens=THINKING_MAX_NEW_TOKENS)
    parsed, status = parse_answer(raw, c["task_type"])
    append_jsonl(RAW_T, {"case_id": cid, "prompt_format": fmt, "thinking": True, "prompt": prompt, "raw_output": raw,
                         "new_tokens": n_tokens, "truncated": n_tokens >= THINKING_MAX_NEW_TOKENS,
                         "parsed_answer": parsed, "parse_status": status,
                         "auto_correct": auto_score(c, parsed, status), "seconds": round(time.time() - t, 1)})
    print(f"[{k}/{len(todo_t)}] {cid} fmt={fmt} -> {parsed or status} ({time.time() - t:.0f}s)")
"""),
    code("""
import shutil
shutil.copy(CASES_PATH, f"{OUT_DIR}/cases_used.csv")
shutil.make_archive("results", "zip", OUT_DIR)
from google.colab import files
files.download("results.zip")
"""),
]



def write(cells, name):
    nb = {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
                                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    for i, c in enumerate(nb["cells"]):
        c["id"] = f"cell-{i}"
    path = os.path.join(ROOT, "notebooks", name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("wrote", path)


write(cells, "eval_qwen35_4b.ipynb")

# Diagnostic: rerun the F4 Darija cases with Chamel's connector glossary in the prompt (non-thinking).
# Shares the install, config, pilot.py, environment and model-loading cells with the main notebook.
glossary_cells = [
    md("""
# Glossary check: F4 Darija–French with a connector glossary (non-thinking)

Reruns the F4 Darija–French cases (base and contrast, formats A and B) with your glossary of Darija time connectors added just before the story. Same model, revision, decoding and answer parsing as the main run; only the glossary is new.

1. Runtime → **T4 GPU**. 2. Upload `cases.csv` and `glossary.txt` (both from `data/`). 3. Run all. 4. Download `glossary_results.zip`.
"""),
    cells[1], cells[2],
    code('OUT_DIR = "results_glossary"  # separate folder: never overwrite the main run results'),
    cells[3], cells[4],
    code("""
GLOSSARY = load_glossary("glossary.txt")
print(GLOSSARY)
cases = [c for c in load_cases(CASES_PATH) if c["family_id"] == "F4" and c["language"] == "darija_fr"]
print(len(cases), "F4 Darija cases")
"""),
    cells[6],
    code("""
RAW_G = f"{OUT_DIR}/raw_outputs_glossary.jsonl"
json.dump({**run_config, "glossary": GLOSSARY, "cases": [c["case_id"] for c in cases]},
          open(f"{OUT_DIR}/run_config_glossary.json", "w"), indent=2, ensure_ascii=False)
done = {(r["case_id"], r["prompt_format"]) for r in read_jsonl(RAW_G)}
todo = [(c, f) for f in FORMATS for c in cases if (c["case_id"], f) not in done]
print(f"{len(done)} done, {len(todo)} to run")
for k, (c, fmt) in enumerate(todo, 1):
    prompt = build_prompt(c, fmt, glossary=GLOSSARY)
    t = time.time()
    raw, n_tokens = generate(prompt)
    parsed, status = parse_answer(raw, c["task_type"])
    append_jsonl(RAW_G, {"case_id": c["case_id"], "prompt_format": fmt, "thinking": False, "glossary": True,
                         "prompt": prompt, "raw_output": raw, "new_tokens": n_tokens,
                         "truncated": n_tokens >= MAX_NEW_TOKENS, "parsed_answer": parsed, "parse_status": status,
                         "auto_correct": auto_score(c, parsed, status), "seconds": round(time.time() - t, 1)})
    print(f"[{k}/{len(todo)}] {c['case_id']} fmt={fmt} -> {parsed or status} gold={c['gold_answer']} ({time.time() - t:.0f}s)")
"""),
    code("""
res = read_jsonl(RAW_G)
print(f"with glossary: {sum(r['auto_correct'] is True for r in res)}/{len(res)} correct (without glossary: 0/4 in the main run)")
for r in res:
    print("=====", r["case_id"], r["prompt_format"], "->", r["parsed_answer"])
    print(r["raw_output"][:1200])
"""),
    code("""
import shutil
shutil.copy("glossary.txt", f"{OUT_DIR}/glossary_used.txt")
shutil.make_archive("glossary_results", "zip", OUT_DIR)
from google.colab import files
files.download("glossary_results.zip")
"""),
]
write(glossary_cells, "glossary_check_f4.ipynb")
