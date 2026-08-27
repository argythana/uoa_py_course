#!/usr/bin/env python3
"""Harvest the final-assignment GRADING corpus into a PII-free, aggregate JSON signal.

This is the deterministic front-end for the `evaluate-course-from-final-submissions`
skill. It reads the per-notebook grade-feedback files the
`uoa-py-course-final-assignment-grade` skill writes into each student's gitignored
folder, extracts the 13-criterion score table from each, deduplicates to ONE latest
grade run per student per notebook category, and emits aggregate counts of where
students lost points — grouped by criterion and by notebook category.

WHAT IT READS (gitignored student PII — local only):
    students_work/class_<YY>/*/final_assignment/<slug>_<category>_feedback_<TS>.md
    where <category> in {regression, clustering, classification} and
    <TS> = YYYY-MM-DD_HHMM (the grade run's timestamp).

    It deliberately does NOT read the formative feedback skill's
    `*_assignment_draft_feedback_*.md` files — those carry readiness flags
    (checkmarks), not numeric criterion scores.

WHAT IT EMITS (safe to commit / hand downstream): aggregate JSON on stdout with
NO student names, NO folder slugs, NO free-text prose, NO dataset details — only
criterion keys, caps, numeric point values (sorted, so no positional link back to a
student), and counts. This is the PII discipline the skill depends on: the input is
gitignored, the output is anonymous by construction.

Deterministic: same corpus in -> same JSON out (no wall-clock in the payload). Runs
on the Python 3.12 stdlib only; no third-party imports, no network.

Usage:
    python harvest_grade_corpus.py [--class 26] [--repo-root PATH] [--table]

    --class YY      class cohort under students_work/class_<YY>/  (default: 26)
    --repo-root P   repo root (default: auto-detected by walking up for .git)
    --table         also print a human-readable PII-free summary table to stderr
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# ----------------------------------------------------------------------------
# The 13 criteria: canonical key -> (display substring needle, expected cap).
# The needle is matched (case-insensitive substring) against the criterion cell
# of each grade table row. Needles are chosen to be mutually unambiguous.
# Caps are verbatim from final_assignment/submission_requirements.prompt.md.
# ----------------------------------------------------------------------------
CRITERIA = [
    ("executability",        "executab",             0.5),
    ("readability",          "readab",               0.5),
    ("imports",              "import",               0.5),
    ("dataset_selection",    "dataset select",       0.5),
    ("relative_paths",       "relative path",        0.5),
    ("data_presentation",    "data presentation",    0.5),
    ("eda",                  "eda",                  1.5),
    ("descriptive_stats",    "descriptive",          0.5),
    ("preprocessing",        "preprocess",           1.0),
    ("model_implementation", "model implementation", 2.0),
    ("model_evaluation",     "model evaluation",     1.0),
    ("model_selection",      "model selection",      0.5),
    ("model_validation",     "model validation",     0.5),
]
KEY_ORDER = [k for k, _, _ in CRITERIA]
CAP_BY_KEY = {k: cap for k, _, cap in CRITERIA}
CATEGORIES = ("regression", "clustering", "classification")

# A grade-table row looks like:
#   | EDA (1.5, strict) | 1.0 | notes... |
#   | Model implementation & fine-tuning (2.0) | 2.0 | ... |
# Capture: the criterion name (before the cap parens), the cap, and the points.
ROW_RE = re.compile(
    r"^\|\s*(?P<name>[^|]+?)\s*"
    r"\((?P<cap>\d+(?:\.\d+)?)(?:,\s*[^)]*)?\)\s*"   # (0.5)  or  (1.5, strict)
    r"\|\s*(?P<pts>\d+(?:\.\d+)?)\s*\|",
    re.IGNORECASE,
)

# Grade-feedback filenames: <slug>_<category>_feedback_<YYYY-MM-DD>_<HHMM>.md
FEEDBACK_RE = re.compile(
    r"^(?P<slug>.+)_(?P<category>regression|clustering|classification)"
    r"_feedback_(?P<ts>\d{4}-\d{2}-\d{2}_\d{4})\.md$"
)


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` until a directory containing .git is found."""
    cur = start.resolve()
    for cand in (cur, *cur.parents):
        if (cand / ".git").exists():
            return cand
    return cur


def key_for(name: str) -> str | None:
    """Map a criterion display name to its canonical key via substring needle."""
    low = name.lower()
    for key, needle, _cap in CRITERIA:
        if needle in low:
            return key
    return None


def parse_feedback_file(path: Path) -> dict[str, float]:
    """Return {criterion_key: points} for the 13-criterion table in one file.

    First occurrence of each criterion wins (guards against a stray second table).
    """
    scores: dict[str, float] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return scores
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        key = key_for(m.group("name"))
        if key is None or key in scores:
            continue
        scores[key] = float(m.group("pts"))
    return scores


def collect_latest(class_dir: Path) -> tuple[dict, list[str]]:
    """Deduplicate to the latest grade run per (student, category).

    Returns ({(student_dir, category): (ts, path)}, notes). The student_dir is used
    ONLY as an in-memory dedup key and is never emitted.
    """
    latest: dict[tuple[Path, str], tuple[str, Path]] = {}
    notes: list[str] = []
    for path in sorted(class_dir.rglob("*_feedback_*.md")):
        m = FEEDBACK_RE.match(path.name)
        if not m:
            continue  # e.g. *_assignment_draft_feedback_*.md — not a grade run
        student_dir = path.parent  # .../final_assignment/
        category = m.group("category")
        ts = m.group("ts")
        dkey = (student_dir, category)
        if dkey not in latest or ts > latest[dkey][0]:
            latest[dkey] = (ts, path)
    return latest, notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--class", dest="klass", default="26",
                    help="class cohort under students_work/class_<YY>/ (default 26)")
    ap.add_argument("--repo-root", default=None, help="repo root (default: auto)")
    ap.add_argument("--table", action="store_true",
                    help="also print a PII-free summary table to stderr")
    args = ap.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else find_repo_root(Path.cwd())
    class_dir = repo_root / "students_work" / f"class_{args.klass}"
    if not class_dir.is_dir():
        print(json.dumps({"error": f"no such class dir: {class_dir}"}), file=sys.stdout)
        return 2

    latest, notes = collect_latest(class_dir)

    # student_dir -> set of categories present (to count distinct submissions)
    students: dict[Path, set[str]] = defaultdict(set)
    # (category, key) -> list of points
    points: dict[tuple[str, str], list[float]] = defaultdict(list)
    parsed_files = 0
    files_missing_criteria: int = 0

    for (student_dir, category), (_ts, path) in latest.items():
        scores = parse_feedback_file(path)
        if not scores:
            notes.append(f"unparseable-table:{category}")
            continue
        parsed_files += 1
        students[student_dir].add(category)
        if len(scores) < 13:
            files_missing_criteria += 1
        for key, pts in scores.items():
            points[(category, key)].append(pts)

    def stats(vals: list[float], cap: float) -> dict:
        n = len(vals)
        below = sum(1 for v in vals if v < cap)
        zero = sum(1 for v in vals if v == 0.0)
        full = sum(1 for v in vals if v >= cap)
        total = sum(vals)
        return {
            "n": n,
            "below_cap": below,
            "below_cap_pct": round(100.0 * below / n, 1) if n else 0.0,
            "zero": zero,
            "full": full,
            "mean_points": round(total / n, 3) if n else 0.0,
            "mean_fraction_of_cap": round((total / n) / cap, 3) if n and cap else 0.0,
            # sorted -> the value list carries no positional link to any student
            "points_sorted": sorted(vals),
        }

    criteria_out: dict[str, dict] = {}
    for key in KEY_ORDER:
        cap = CAP_BY_KEY[key]
        per_cat = {}
        all_vals: list[float] = []
        for cat in CATEGORIES:
            vals = points.get((cat, key), [])
            if vals:
                per_cat[cat] = stats(vals, cap)
                all_vals.extend(vals)
        criteria_out[key] = {
            "cap": cap,
            "overall": stats(all_vals, cap),
            "by_category": per_cat,
        }

    by_category_counts = {
        cat: sum(1 for cats in students.values() if cat in cats) for cat in CATEGORIES
    }

    payload = {
        "class": args.klass,
        "submissions_scanned": len(students),
        "notebooks_scored": parsed_files,
        "by_category_submission_counts": by_category_counts,
        "files_with_incomplete_tables": files_missing_criteria,
        "criteria": criteria_out,
        "notes": sorted(set(notes)),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))

    if args.table:
        print("\nPII-free criterion deduction summary (class %s, %d submissions)"
              % (args.klass, len(students)), file=sys.stderr)
        print("%-22s %4s %8s %6s %6s %8s" %
              ("criterion", "cap", "n", "below", "zero", "mean%cap"), file=sys.stderr)
        for key in KEY_ORDER:
            o = criteria_out[key]["overall"]
            print("%-22s %4.1f %8d %6d %6d %8.2f" % (
                key, CAP_BY_KEY[key], o["n"], o["below_cap"], o["zero"],
                o["mean_fraction_of_cap"]), file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
