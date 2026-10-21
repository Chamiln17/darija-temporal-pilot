"""Case loading, prompt building, answer parsing and metrics for the pilot.

The notebook embeds this file's source in one cell (scripts/build_notebook.py), so
Colab needs no repo clone. Model loading and generation live in the notebook.
"""
import csv
import json
import re
from collections import defaultdict

STATUS_LABELS = ("CONFIRMED_ACTIVE", "CONFIRMED_NOT_ACTIVE", "INSUFFICIENT_EVIDENCE")
TASK_TYPES = ("status", "order", "extract")
LANGUAGES = ("fr", "darija_fr")
CASE_COLUMNS = (
    "family_id", "variant_id", "language", "task_type", "fictional_rule", "narrative",
    "question", "gold_answer", "gold_rationale", "changed_feature", "same_answer_as_base",
    "written_by", "review_status", "notes",
)

ANSWER_INSTRUCTIONS = {
    "status": "End your reply with one line: ANSWER: CONFIRMED_ACTIVE, ANSWER: CONFIRMED_NOT_ACTIVE or ANSWER: INSUFFICIENT_EVIDENCE.",
    "order": "End your reply with one line: ANSWER: followed by the event IDs in chronological order, comma-separated (for example ANSWER: E2, E1, E3).",
    "extract": "End your reply with one line: ANSWER: followed by your short answer.",
}

# Two fixed layouts with identical content; only formatting differs (prompt-format check).
PROMPT_FORMATS = {
    "A": "Rule: {rule}\n\nStory: {narrative}\n\nQuestion: {question}\n\n{instruction}",
    "B": "### RULE\n{rule}\n### STORY\n{narrative}\n### QUESTION\n{question}\n### FORMAT\n{instruction}",
}


def case_id(case):
    return f"{case['family_id']}-{case['variant_id']}-{case['language']}"


def load_cases(path, approved_only=True):
    """Read the review sheet CSV; keep APPROVED/EDITED rows unless approved_only is False."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in CASE_COLUMNS if rows and c not in rows[0]]
    if missing:
        raise ValueError(f"cases file is missing columns: {missing}")
    cases, problems = [], []
    for n, row in enumerate(rows, start=2):
        row = {k: (v or "").strip() for k, v in row.items() if k}
        if not row.get("family_id"):
            continue
        if approved_only and row["review_status"].upper() not in ("APPROVED", "EDITED"):
            continue
        if row["task_type"] not in TASK_TYPES:
            problems.append(f"line {n}: task_type {row['task_type']!r} not in {TASK_TYPES}")
        if row["language"] not in LANGUAGES:
            problems.append(f"line {n}: language {row['language']!r} not in {LANGUAGES}")
        if row["task_type"] == "status" and row["gold_answer"] not in STATUS_LABELS:
            problems.append(f"line {n}: status gold {row['gold_answer']!r} not in {STATUS_LABELS}")
        row["case_id"] = case_id(row)
        cases.append(row)
    ids = [c["case_id"] for c in cases]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append(f"duplicate case ids: {dupes}")
    if problems:
        raise ValueError("cases file problems:\n" + "\n".join(problems))
    return cases


def build_prompt(case, fmt):
    return PROMPT_FORMATS[fmt].format(
        rule=case["fictional_rule"], narrative=case["narrative"], question=case["question"],
        instruction=ANSWER_INSTRUCTIONS[case["task_type"]],
    )


def final_text(raw):
    """Drop any thinking block; only the text after </think> is scored."""
    return raw.rsplit("</think>", 1)[-1].strip()


def parse_answer(raw, task_type):
    """Return (parsed_answer, parse_status). parse_status: ok | no_answer_line | invalid."""
    text = final_text(raw)
    lines = [l for l in text.splitlines() if re.match(r"\s*\**\s*ANSWER\s*\**\s*:", l, re.I)]
    if not lines:
        return "", "no_answer_line"
    value = lines[-1].split(":", 1)[1].strip().strip("*").strip()
    if task_type == "status":
        found = [lab for lab in STATUS_LABELS if re.search(rf"\b{lab}\b", value.upper())]
        return (found[0], "ok") if len(found) == 1 else (value, "invalid")
    if task_type == "order":
        ids = re.findall(r"\bE\d+\b", value.upper())
        return (", ".join(ids), "ok") if ids else (value, "invalid")
    return value, "ok"


def normalise_order(s):
    return [x for x in re.findall(r"E\d+", s.upper())]


def auto_score(case, parsed, parse_status):
    """True/False when checkable automatically, None when a human must judge (extract tasks)."""
    if parse_status != "ok":
        return False
    if case["task_type"] == "status":
        return parsed == case["gold_answer"]
    if case["task_type"] == "order":
        return normalise_order(parsed) == normalise_order(case["gold_answer"])
    return None


def final_correct(row):
    """The human verdict wins over the automatic score."""
    manual = (row.get("manual_verdict") or "").strip().upper()
    if manual in ("CORRECT", "WRONG"):
        return manual == "CORRECT"
    auto = row.get("auto_correct")
    if auto in (True, False):
        return auto
    if isinstance(auto, str) and auto in ("True", "False"):
        return auto == "True"
    return None


def _ratio(rows):
    judged = [r for r in rows if final_correct(r) is not None]
    return f"{sum(final_correct(r) for r in judged)}/{len(judged)}"


def metrics(rows):
    """Counts as numerator/denominator strings; unjudged rows are left out of each ratio."""
    out = {"overall": _ratio(rows), "unjudged": sum(final_correct(r) is None for r in rows)}
    for key in ("language", "prompt_format", "task_type", "variant_id"):
        groups = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        out[f"by_{key}"] = {k: _ratio(v) for k, v in sorted(groups.items())}
    out["parse_failures"] = sum(r["parse_status"] != "ok" for r in rows)

    by_id = {(r["family_id"], r["variant_id"], r["language"], r["prompt_format"]): r for r in rows}
    # Cross-language consistency: same case and format, French vs Darija-French.
    same, both_right, pairs = 0, 0, 0
    for (fam, var, lang, fmt), r in by_id.items():
        other = by_id.get((fam, var, "darija_fr", fmt)) if lang == "fr" else None
        if not other:
            continue
        a, b = final_correct(r), final_correct(other)
        if a is None or b is None:
            continue
        pairs += 1
        same += (r["parsed_answer"].upper() == other["parsed_answer"].upper())
        both_right += a and b
    out["cross_language_same_answer"] = f"{same}/{pairs}"
    out["cross_language_both_correct"] = f"{both_right}/{pairs}"

    # Contrast consistency: base and contrast both correct, per family, language and format.
    groups, ok = 0, 0
    for (fam, var, lang, fmt), r in by_id.items():
        if var != "base":
            continue
        twin = by_id.get((fam, "contrast", lang, fmt))
        if not twin or final_correct(r) is None or final_correct(twin) is None:
            continue
        groups += 1
        ok += final_correct(r) and final_correct(twin)
    out["contrast_consistency"] = f"{ok}/{groups}"
    return out


def append_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except FileNotFoundError:
        return []
