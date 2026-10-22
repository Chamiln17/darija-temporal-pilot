"""Self-check for pilot.py without a GPU: python scripts/test_pilot.py"""
import csv
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import pilot as p

BASE = dict(fictional_rule="R", narrative="N", question="Q", gold_rationale="", changed_feature="",
            same_answer_as_base="", written_by="test", review_status="APPROVED", notes="")


def case(fam, var, lang, task, gold):
    return dict(BASE, family_id=fam, variant_id=var, language=lang, task_type=task, gold_answer=gold)


def write(rows):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=p.CASE_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return path


# parsing
assert p.parse_answer("<think>ANSWER: CONFIRMED_ACTIVE</think>\nok\nANSWER: INSUFFICIENT_EVIDENCE", "status") == ("INSUFFICIENT_EVIDENCE", "ok")
assert p.parse_answer("**ANSWER:** CONFIRMED_NOT_ACTIVE", "status") == ("CONFIRMED_NOT_ACTIVE", "ok")
# CONFIRMED_ACTIVE must not match inside CONFIRMED_NOT_ACTIVE
assert p.parse_answer("ANSWER: CONFIRMED_NOT_ACTIVE", "status")[0] == "CONFIRMED_NOT_ACTIVE"
assert p.parse_answer("no label here", "status") == ("", "no_answer_line")
assert p.parse_answer("ANSWER: maybe", "status") == ("maybe", "invalid")
assert p.parse_answer("ANSWER: e2, E1 ,E3", "order") == ("E2, E1, E3", "ok")

# loading: unapproved rows skipped, bad labels rejected
rows = [case("F1", "base", "fr", "status", "CONFIRMED_ACTIVE"),
        dict(case("F1", "base", "darija_fr", "status", "CONFIRMED_ACTIVE"), review_status="PENDING_HUMAN_REVIEW")]
assert [c["case_id"] for c in p.load_cases(write(rows))] == ["F1-base-fr"]
try:
    p.load_cases(write([case("F1", "base", "fr", "status", "ACTIVE")]))
    raise AssertionError("bad gold label accepted")
except ValueError:
    pass

# metrics: both languages of F1 base+contrast, format A
def row(fam, var, lang, task, gold, parsed, manual=""):
    c = case(fam, var, lang, task, gold)
    st = "ok"
    return dict(c, prompt_format="A", parsed_answer=parsed, parse_status=st,
                auto_correct=p.auto_score(c, parsed, st), manual_verdict=manual)

rs = [row("F1", "base", "fr", "status", "CONFIRMED_ACTIVE", "CONFIRMED_ACTIVE"),
      row("F1", "contrast", "fr", "status", "INSUFFICIENT_EVIDENCE", "INSUFFICIENT_EVIDENCE"),
      row("F1", "base", "darija_fr", "status", "CONFIRMED_ACTIVE", "CONFIRMED_ACTIVE"),
      row("F1", "contrast", "darija_fr", "status", "INSUFFICIENT_EVIDENCE", "CONFIRMED_ACTIVE"),
      row("S1", "sanity", "fr", "extract", "Tlemcen", "Tlemcen", manual="CORRECT"),
      row("S1", "sanity", "darija_fr", "extract", "Tlemcen", "Alger")]
m = p.metrics(rs)
assert m["overall"] == "4/5", m
assert m["unjudged"] == 1, m
assert m["by_language"] == {"darija_fr": "1/2", "fr": "3/3"}, m
assert m["contrast_consistency"] == "1/2", m
assert m["cross_language_both_correct"] == "1/2", m
assert m["cross_language_same_answer"] == "1/2", m
# glossary goes right before the story, once, in both formats; no glossary leaves the prompt unchanged
c = case("F4", "base", "darija_fr", "order", "E1, E2")
for fmt in ("A", "B"):
    g = p.build_prompt(c, fmt, glossary="psk = because")
    assert g.count("psk = because") == 1 and g.index("psk = because") < g.index("N"), (fmt, g)
    assert p.build_prompt(c, fmt) == p.build_prompt(c, fmt, glossary=None)
fd, gpath = tempfile.mkstemp(suffix=".txt"); os.close(fd)
open(gpath, "w", encoding="utf-8").write("# comment\npsk = TODO\n")
try:
    p.load_glossary(gpath)
    raise AssertionError("TODO glossary accepted")
except ValueError:
    pass
open(gpath, "w", encoding="utf-8").write("# comment\npsk = because\n9bel ma = before\n")
assert p.load_glossary(gpath) == "psk = because\n9bel ma = before"
print("all checks passed")
