#!/usr/bin/env python3
"""
compute_grade.py — turn per-criterion scores into the authoritative assignment grade.

This is the deterministic arithmetic layer of the grading skill. The LLM graders
decide *what each of the 13 criteria deserves* (substance); this script does *all*
the summation, rounding, and weighting (arithmetic), so three independent graders
can never disagree on the maths — only on judgement, which is the point.

Usage:
    compute_grade.py <scores.json>          # read a scores file
    compute_grade.py -                      # read scores JSON from stdin

Input JSON shape:

    {
      "prefix": "argyriou_t",                # optional, echoed back
      "rejection_flags": ["..."],            # optional, assignment-level (surfaced, not auto-applied)
      "notebooks": {
        "regression":     {"filename": "...", "criteria": {"executability": 0.5, ...}},
        "clustering":     {"submitted": false},
        "classification": {"filename": "...", "criteria": {"executability": 0.5, ...}}
      }
    }

Each submitted notebook's `criteria` must use exactly the 13 canonical keys below.
A notebook with "submitted": false (or omitted) scores 0 but its weight still counts
toward the total, per submission_requirements.prompt.md.

Output JSON on stdout: per-notebook raw sum + rounded grade + weighted contribution,
the raw weighted total, and the final suggested grade (rounded to the nearest 0.5).
Validation problems (bad keys, out-of-range scores, criteria not summing to a max of
10) are reported in `validation` — never raised, so the caller always gets a number
plus a clear flag if a grader mis-scored.

No LLM, no network. Pure arithmetic.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# The 13 within-notebook criteria and their maxima (sum to 10.0), verbatim from
# final_assignment/submission_requirements.prompt.md → "weights for a perfect 10".
CRITERIA_MAX: dict[str, float] = {
    "executability": 0.5,        # Overall notebook executability
    "readability": 0.5,          # Notebook Readability (markdown cells for headers/conclusions)
    "imports": 0.5,              # Proper python imports
    "dataset_selection": 0.5,    # Appropriate dataset selection
    "relative_paths": 0.5,       # Use working relative paths to read data
    "data_presentation": 0.5,    # Data Presentation
    "eda": 1.5,                  # Proper Exploratory Data Analysis (strict)
    "descriptive_stats": 0.5,    # Descriptive Statistics
    "preprocessing": 1.0,        # Data Preprocessing
    "model_implementation": 2.0, # Model Implementation, Testing, Finetuning
    "model_evaluation": 1.0,     # Model evaluation with proper metrics
    "model_selection": 0.5,      # Model's Comparison and model Selection
    "model_validation": 0.5,     # Model Validation with new data
}

# Notebook weights on a scale of 10 (regression 2.5 / clustering 2.5 / classification 5.0
# → multipliers 0.25 / 0.25 / 0.50). A missing notebook still counts its weight.
WEIGHTS: dict[str, float] = {
    "regression": 0.25,
    "clustering": 0.25,
    "classification": 0.50,
}

# Reported grades live on a 0.5 grid; the prompt's "acceptable" passing band is 5..10.
ACCEPTABLE_MIN = 5.0
ACCEPTABLE_MAX = 10.0


def round_half_to_0_5(x: float) -> float:
    """Round to the nearest 0.5, half **up** (8.25 -> 8.5), matching how a human
    grader rounds. A tiny epsilon absorbs float noise (e.g. a sum of .1s landing
    at 8.4999999 instead of 8.5)."""
    return math.floor(round(x, 6) * 2 + 0.5 + 1e-9) / 2


def grade_one_notebook(category: str, spec: dict) -> dict:
    """Score a single notebook from its criteria. Returns the per-notebook record."""
    weight = WEIGHTS[category]
    submitted = bool(spec.get("submitted", True)) and "criteria" in spec
    problems: list[str] = []

    if not submitted:
        return {
            "category": category,
            "submitted": False,
            "filename": spec.get("filename"),
            "raw_sum": 0.0,
            "grade": 0.0,
            "weight": weight,
            "weighted_contribution": 0.0,
            "problems": ["Notebook not submitted — scores 0; its weight still counts."],
        }

    criteria = spec.get("criteria", {})
    unknown = sorted(set(criteria) - set(CRITERIA_MAX))
    missing = sorted(set(CRITERIA_MAX) - set(criteria))
    if unknown:
        problems.append(f"Unknown criterion keys (ignored): {', '.join(unknown)}")
    if missing:
        problems.append(f"Missing criterion keys (treated as 0): {', '.join(missing)}")

    raw_sum = 0.0
    clamped: dict[str, float] = {}
    for key, cap in CRITERIA_MAX.items():
        raw = float(criteria.get(key, 0.0) or 0.0)
        val = max(0.0, min(raw, cap))
        if raw != val:
            problems.append(f"{key}={raw} out of range [0, {cap}] — clamped to {val}.")
        clamped[key] = val
        raw_sum += val

    grade = round_half_to_0_5(raw_sum)
    return {
        "category": category,
        "submitted": True,
        "filename": spec.get("filename"),
        "criteria": clamped,
        "raw_sum": round(raw_sum, 4),
        "grade": grade,
        "weight": weight,
        "weighted_contribution": round(grade * weight, 4),
        "problems": problems,
    }


def compute(payload: dict) -> dict:
    notebooks_in = payload.get("notebooks", {})
    unknown_cats = sorted(set(notebooks_in) - set(WEIGHTS))
    validation: list[str] = []
    if unknown_cats:
        validation.append(f"Unknown notebook categories (ignored): {', '.join(unknown_cats)}")
    if abs(sum(CRITERIA_MAX.values()) - 10.0) > 1e-9:
        validation.append("CRITERIA_MAX no longer sums to 10 — script needs review.")

    per_notebook = {}
    raw_total = 0.0
    for category in ("regression", "clustering", "classification"):
        spec = notebooks_in.get(category, {"submitted": False})
        rec = grade_one_notebook(category, spec)
        per_notebook[category] = rec
        raw_total += rec["weighted_contribution"]
        validation.extend(f"[{category}] {p}" for p in rec.get("problems", []))

    suggested = round_half_to_0_5(raw_total)
    return {
        "prefix": payload.get("prefix"),
        "notebooks": per_notebook,
        "raw_total": round(raw_total, 4),
        "suggested_grade": suggested,
        "in_acceptable_band": ACCEPTABLE_MIN <= suggested <= ACCEPTABLE_MAX,
        "below_pass_band": suggested < ACCEPTABLE_MIN,
        "weights": WEIGHTS,
        "rejection_flags": payload.get("rejection_flags", []),
        "validation": validation,
        "_note": ("suggested_grade is AI-suggested, not final; the instructor and tutor "
                  "may adjust it. Rejection flags are surfaced, never auto-applied."),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores", help="Path to a scores JSON file, or '-' for stdin.")
    args = ap.parse_args(argv)

    try:
        raw = sys.stdin.read() if args.scores == "-" else Path(args.scores).read_text("utf-8")
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"{e.__class__.__name__}: {e}"}), file=sys.stderr)
        return 1

    print(json.dumps(compute(payload), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
