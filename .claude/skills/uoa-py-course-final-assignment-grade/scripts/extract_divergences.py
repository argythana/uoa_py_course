#!/usr/bin/env python3
"""
extract_divergences.py — deterministic census of what the blind panel penalised.

**What unanimity is about.** The panel does NOT need to converge on an identical
number. It needs unanimity on **the ISSUE that causes a grade penalty** — the
factual premise ("Naive Bayes is imported at cell 3 but never fitted"). The number
is calibration and is settled by the rubric ladder; the *premise* is fact, and a
penalty resting on a premise that not every examiner affirms is a false positive
that harms a student. Those are forbidden.

This script computes, by arithmetic rather than by an LLM eyeballing three tables:

1.  `criteria_needing_findings` — every (notebook, criterion) that ANY blind grader
    scored below its rubric cap. Each one is a proposed penalty, so each one MUST be
    justified by at least one canonical finding that passes the unanimity gate. A
    criterion that appears here and ends up below cap in the final scores with no
    surviving finding behind it is a breach (`apply_unanimity_gate.py` catches it).
2.  `raised_findings` — the findings the graders actually stated, pooled and grouped
    by (notebook, criterion), with how many graders raised something there. A
    criterion penalised by a grader who stated no finding for it is flagged
    (`penalty_without_stated_finding`): the penalty has no premise on record.
3.  `score_spread` — a diagnostic only. Divergent numbers are NOT themselves the
    thing to reconcile; they are a signal that the underlying premises differ.

Usage:
    extract_divergences.py <g1.json> <g2.json> <g3.json> [--out DIR]

Each input is one grader's Phase-G1 return:

    {"grader": "1",
     "notebooks": {"regression": {"filename": "...",
                                  "criteria": {"eda": 1.0, ...},
                                  "findings": [{"criterion": "eda",
                                                "statement": "...",
                                                "anchor": "cell 7",
                                                "evidence": "..."}]},
                   "clustering": {...}, "classification": {...}}}

Exit 0 always (a fully clean panel is a valid outcome). Exit 1 on unreadable input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Caps must mirror compute_grade.py::CRITERIA_MAX — a penalty is "score < cap".
CRITERIA_MAX: dict[str, float] = {
    "executability": 0.5,
    "readability": 0.5,
    "imports": 0.5,
    "dataset_selection": 0.5,
    "relative_paths": 0.5,
    "data_presentation": 0.5,
    "eda": 1.5,
    "descriptive_stats": 0.5,
    "preprocessing": 1.0,
    "model_implementation": 2.0,
    "model_evaluation": 1.0,
    "model_selection": 0.5,
    "model_validation": 0.5,
}
CATEGORIES = ["regression", "clustering", "classification"]
EPS = 1e-9


def load(path: str) -> dict:
    return json.loads(Path(path).read_text("utf-8"))


def grader_id(payload: dict, fallback: str) -> str:
    return str(payload.get("grader") or payload.get("id") or fallback)


def census(returns: list[dict]) -> dict:
    ids = [grader_id(r, str(i + 1)) for i, r in enumerate(returns)]
    notebooks: dict[str, dict] = {}
    needing: list[dict] = []
    problems: list[str] = []

    for cat in CATEGORIES:
        specs = [r.get("notebooks", {}).get(cat) or {} for r in returns]
        submitted = [bool(s.get("criteria")) for s in specs]
        if not any(submitted):
            continue
        if not all(submitted):
            problems.append(
                f"[{cat}] graders disagree on whether the notebook was submitted: "
                + json.dumps(dict(zip(ids, submitted)))
            )

        # Pool every stated finding for this notebook, keyed by criterion.
        findings_by_crit: dict[str, list[dict]] = {}
        for gid, spec in zip(ids, specs):
            for f in spec.get("findings") or []:
                crit = f.get("criterion")
                rec = dict(f)
                rec["raised_by"] = gid
                findings_by_crit.setdefault(crit, []).append(rec)

        spread: dict[str, dict] = {}
        for crit, cap in CRITERIA_MAX.items():
            scores = {}
            for gid, spec in zip(ids, specs):
                crits = spec.get("criteria") or {}
                if crit in crits:
                    scores[gid] = float(crits[crit])
            if not scores:
                continue

            penalisers = {g: s for g, s in scores.items() if s < cap - EPS}
            if len(set(scores.values())) > 1:
                spread[crit] = {
                    "scores": scores,
                    "min": min(scores.values()),
                    "max": max(scores.values()),
                    "spread": round(max(scores.values()) - min(scores.values()), 4),
                }

            if penalisers:
                stated = findings_by_crit.get(crit, [])
                raisers = sorted({f["raised_by"] for f in stated})
                entry = {
                    "key": f"{cat}.{crit}",
                    "notebook": cat,
                    "criterion": crit,
                    "cap": cap,
                    "scores": scores,
                    "penalised_by": sorted(penalisers),
                    "lowest_proposed": min(scores.values()),
                    "most_favourable": max(scores.values()),
                    "unanimously_penalised": len(penalisers) == len(ids),
                    "findings_stated_by": raisers,
                    "stated_findings": stated,
                }
                silent = sorted(set(penalisers) - set(raisers))
                if silent:
                    entry["penalty_without_stated_finding"] = silent
                    problems.append(
                        f"[{cat}.{crit}] grader(s) {', '.join(silent)} scored below cap "
                        "but stated no finding — a penalty with no premise on record."
                    )
                needing.append(entry)

        notebooks[cat] = {
            "filename": next((s.get("filename") for s in specs if s.get("filename")), None),
            "score_spread": spread,
            "findings_by_criterion": findings_by_crit,
        }

    return {
        "graders": ids,
        "notebooks": notebooks,
        "criteria_needing_findings": needing,
        "keys_needing_findings": [e["key"] for e in needing],
        "counts": {
            "criteria_with_a_proposed_penalty": len(needing),
            "unanimously_penalised": sum(1 for e in needing if e["unanimously_penalised"]),
            "penalty_proposed_by_some_only": sum(
                1 for e in needing if not e["unanimously_penalised"]
            ),
            "total_findings_stated": sum(
                len(f) for nb in notebooks.values()
                for f in nb["findings_by_criterion"].values()
            ),
        },
        "problems": problems,
        "_note": (
            "Unanimity is required on the ISSUE, not on the number. Every criterion "
            "listed in criteria_needing_findings must, in the final scores, either sit "
            "at its cap or cite at least one finding that the deliberation rounds "
            "AFFIRMED unanimously. apply_unanimity_gate.py enforces this."
        ),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("returns", nargs=3, help="the three blind graders' G1 return JSON files")
    ap.add_argument("--out", help="directory to also write divergences.json into")
    args = ap.parse_args(argv)

    try:
        payloads = [load(p) for p in args.returns]
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"{e.__class__.__name__}: {e}"}), file=sys.stderr)
        return 1

    result = census(payloads)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / "divergences.json").write_text(text + "\n", "utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
