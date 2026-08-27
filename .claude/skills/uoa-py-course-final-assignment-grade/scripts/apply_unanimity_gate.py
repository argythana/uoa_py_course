#!/usr/bin/env python3
"""
apply_unanimity_gate.py — no grade penalty without a UNANIMOUSLY AFFIRMED issue.

This script is the ONLY sanctioned way to decide which findings may cost a student
points or appear as a criticism in their feedback. Do not hand-assemble the surviving
set; run this.

THE RULE (instructor mandate, 2026-07-29)
-----------------------------------------
Unanimity is required on **the ISSUE that causes the penalty**, not on the number.
Graders may legitimately differ on whether a confirmed weakness costs 0.25 or 0.5 —
that is rubric calibration, and the arbiter settles it against the ladder. They may
NOT differ on whether the weakness *is there*. A penalty resting on a premise that
not every examiner affirms is a false positive, and at this level a false positive
is unacceptable: it lowers a real student's grade and states a criticism of their
work on a premise that may simply be untrue.

    A finding may cost points / enter the feedback prose only if, in a single
    deliberation round, EVERY voter of that round independently AFFIRMED it,
    the round included the arbiter, and the round had at least MIN_VOTERS voters.

Missing a real weakness is an acceptable cost. Inventing one is not. So an issue that
cannot reach unanimity within MAX_ROUNDS (3) rounds is STRUCK — the penalty is refunded
and the remark is deleted, not softened.

Failure modes this exists to prevent (all three observed in real panels)
-----------------------------------------------------------------------
1.  A finding raised by ONE grader is folded into the arbiter's prose because the
    arbiter believes it. One voice, not unanimity. Struck unless it survives a round.
2.  A finding is re-worded ("narrowed") after a round, given a fresh affirmation by
    the arbiter alone, and never re-voted by the other examiners. Struck: a re-worded
    finding is a NEW finding and needs its own unanimous round.
3.  A criterion is scored below cap while every finding behind it was struck — the
    number keeps the penalty after the premise died. Reported as a BREACH.

Inputs (a panel directory, typically $WORK/panel/)
--------------------------------------------------
  findings.json      canonical, de-duplicated list of every penalty-bearing issue
                     proposed by ANY voice (the arbiter merges the graders' pooled
                     findings into this list; semantic merging is judgement, the
                     vote arithmetic below is not):
                       [{"id": "F1", "notebook": "regression", "criterion": "eda",
                         "statement": "...", "anchor": "cell 7", "raised_by": ["1"]}]

  round<N>_<voter>.json   one file per voter per round; voter id must contain
                     "arbiter" for the arbiter's own vote:
                       {"voter": "e1", "round": 1,
                        "votes": [{"finding_id": "F1", "vote": "AFFIRM",
                                   "reason": "cell 7 shows ..."}]}
                     Vote values: AFFIRM | REFUTE | UNSURE. Anything that is not a
                     literal AFFIRM counts against unanimity — including UNSURE and
                     a missing vote. Silence is never assent.

  final_scores.json  (optional, via --check-final) the arbiter's proposed final
                     scores, shaped for compute_grade.py, where every criterion below
                     its cap carries the finding ids that justify it:
                       {"notebooks": {"regression": {"criteria": {"eda": 1.0},
                                       "justified_by": {"eda": ["F1"]}}}}

Usage:
    apply_unanimity_gate.py <panel_dir> [--check-final final_scores.json] [--write]

Exit status:
    0  every finding resolved and (if checked) no score rests on a struck premise
    1  unreadable / malformed input
    3  BREACH — a criterion is below cap with no surviving finding behind it, or a
       struck finding is still cited. The grade must not be shipped until fixed.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

AFFIRM = "AFFIRM"
REFUTE = "REFUTE"

MAX_ROUNDS = 3          # instructor mandate: deliberate up to 3 rounds, then let it go
MIN_VOTERS = 3          # a deciding round needs >= 2 fresh examiners + the arbiter
EPS = 1e-9

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

ROUND_FILE = re.compile(r"round(\d+)_(.+)\.json$")


def load_json(path: str | Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def collect_rounds(panel_dir: str) -> dict[int, dict[str, dict[str, str]]]:
    """round number -> voter id -> finding_id -> vote.

    Every `round<N>_<voter>.json` in the directory is read. The round number comes
    from the filename, never from the file body, so a mislabelled body cannot smuggle
    a vote into a round it was not cast in.
    """
    rounds: dict[int, dict[str, dict[str, str]]] = {}
    for path in sorted(glob.glob(os.path.join(panel_dir, "round*_*.json"))):
        m = ROUND_FILE.search(os.path.basename(path))
        if not m:
            continue
        rnum, voter = int(m.group(1)), m.group(2)
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  ! could not read {os.path.basename(path)}: {exc}", file=sys.stderr)
            continue
        cast = rounds.setdefault(rnum, {}).setdefault(voter, {})
        for vote in data.get("votes", []):
            fid = vote.get("finding_id") or vote.get("id")
            if fid is not None:
                cast[str(fid)] = str(vote.get("vote", "")).strip().upper()
    return rounds


def settle(fid: str, rounds: dict[int, dict[str, dict[str, str]]],
           blind_unanimous: bool = False) -> dict:
    """Walk rounds 1..MAX_ROUNDS; the first round that is unanimous AFFIRM settles it.

    `blind_unanimous` (instructor policy, 2026-07-29): a finding that ALL THREE blind
    graders raised independently, in substantially the same words, and that no grader
    contradicted, is treated as already unanimously affirmed and needs no deliberation
    round. The instructor accepted the residual risk this carries — a real panel saw a
    claim raised by all three graders still get unanimously REFUTED once examined,
    because agreeing that something is wrong is not the same as having verified the
    exact wording. The mitigation is at the MERGE step, not here: a blind-unanimous
    finding must carry the most conservative grader's wording VERBATIM, never a
    coordinator-written summary, because coordinator-introduced quantifiers ("only",
    "never", "no…at all") are what defeated every struck claim in that panel.

    Otherwise a round decides only if it is quorate (>= MIN_VOTERS voters, arbiter
    among them) and EVERY voter in it recorded a literal AFFIRM for this finding. A
    voter who did not vote on this finding breaks unanimity — silence is not assent.
    """
    if blind_unanimous:
        return {"survives": True, "resolution": "unanimous_blind_affirm_no_round",
                "settled_round": 0, "trail": []}

    trail = []
    for rnum in range(1, MAX_ROUNDS + 1):
        voters = rounds.get(rnum, {})
        if not voters:
            continue
        cast = {v: votes.get(fid) for v, votes in voters.items()}
        present = {v: val for v, val in cast.items() if val}
        # A finding that was not on THIS round's ballot simply was not deliberated
        # here. Skip the round entirely: with no votes cast, `all(...)` over an empty
        # set is vacuously true, which would otherwise report a finding nobody voted
        # on as "unanimously refuted" in a round it never appeared in — and would
        # strike a narrowed finding introduced later on the strength of an earlier
        # round that predates it.
        if not present:
            continue
        has_arbiter = any("arbiter" in v.lower() for v in voters)
        quorate = len(voters) >= MIN_VOTERS and has_arbiter
        # Every voter of the round must have voted, and all the same way.
        complete = len(present) == len(voters)
        unanimous_affirm = complete and all(val == AFFIRM for val in present.values())
        unanimous_refute = complete and all(val == REFUTE for val in present.values())
        trail.append({
            "round": rnum, "voters": len(voters), "quorate": quorate,
            "votes": cast, "unanimous_affirm": unanimous_affirm,
        })
        if quorate and unanimous_affirm:
            return {"survives": True, "resolution": f"unanimous_affirm_round_{rnum}",
                    "settled_round": rnum, "trail": trail}
        if quorate and unanimous_refute:
            return {"survives": False, "resolution": f"unanimously_refuted_round_{rnum}",
                    "settled_round": rnum, "trail": trail}
    if not trail:
        return {"survives": False, "resolution": "never_deliberated",
                "settled_round": None, "trail": trail}
    return {"survives": False, "resolution": f"no_unanimity_after_{MAX_ROUNDS}_rounds",
            "settled_round": None, "trail": trail}


def check_final(final: dict, surviving: set[str], struck: set[str]) -> list[dict]:
    """Every criterion below its cap must cite >= 1 SURVIVING finding."""
    breaches = []
    for cat, spec in (final.get("notebooks") or {}).items():
        if not spec.get("criteria"):
            continue
        # `justified_by` is the canonical key; `cites` is accepted as a synonym so a
        # reconciliation written against either spelling is checked rather than being
        # silently reported as an unpremised penalty on every below-cap criterion.
        justified = spec.get("justified_by") or spec.get("cites") or {}
        for crit, score in spec["criteria"].items():
            cap = CRITERIA_MAX.get(crit)
            if cap is None or float(score) >= cap - EPS:
                continue
            cited = [str(x) for x in (justified.get(crit) or [])]
            alive = [c for c in cited if c in surviving]
            if not cited:
                breaches.append({
                    "key": f"{cat}.{crit}", "score": score, "cap": cap,
                    "reason": "scored below cap but cites NO finding — penalty with no premise",
                    "remedy_score": cap,
                })
            elif not alive:
                breaches.append({
                    "key": f"{cat}.{crit}", "score": score, "cap": cap,
                    "cited": cited,
                    "struck_cited": [c for c in cited if c in struck],
                    "reason": "every finding behind this penalty was STRUCK by the gate",
                    "remedy_score": cap,
                })
            elif len(alive) < len(cited):
                breaches.append({
                    "key": f"{cat}.{crit}", "score": score, "cap": cap,
                    "cited": cited, "surviving_cited": alive,
                    "struck_cited": [c for c in cited if c not in surviving],
                    "reason": ("penalty partly rests on struck findings — re-score using "
                               "ONLY the surviving ones"),
                    "remedy_score": None,
                })
    return breaches


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("panel_dir", help="directory holding findings.json + round*_*.json")
    ap.add_argument("--check-final", help="the arbiter's proposed final scores JSON")
    ap.add_argument("--write", action="store_true",
                    help="write gate_report.json / surviving_findings.json / struck_findings.json")
    args = ap.parse_args()

    findings_path = os.path.join(args.panel_dir, "findings.json")
    try:
        findings = load_json(findings_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"cannot read findings.json: {exc}"}), file=sys.stderr)
        return 1

    rounds = collect_rounds(args.panel_dir)
    surviving, struck = [], []
    for f in findings:
        fid = str(f.get("id"))
        verdict = settle(fid, rounds, blind_unanimous=bool(f.get("blind_unanimous")))
        rec = {**{k: f.get(k) for k in
                  ("id", "notebook", "criterion", "statement", "anchor", "raised_by")},
               **verdict}
        (surviving if verdict["survives"] else struck).append(rec)

    surviving_ids = {r["id"] for r in surviving}
    struck_ids = {r["id"] for r in struck}

    report = {
        "panel_dir": args.panel_dir,
        "max_rounds": MAX_ROUNDS,
        "min_voters_per_deciding_round": MIN_VOTERS,
        "rounds_held": sorted(rounds),
        "voters_per_round": {str(r): sorted(v) for r, v in sorted(rounds.items())},
        "counts": {"findings": len(findings),
                   "surviving": len(surviving), "struck": len(struck),
                   "settled_blind_unanimous": sum(
                       1 for r in surviving
                       if r["resolution"] == "unanimous_blind_affirm_no_round"),
                   "settled_by_deliberation": sum(
                       1 for r in surviving
                       if r["resolution"].startswith("unanimous_affirm_round_"))},
        "surviving": surviving,
        "struck": struck,
        "breaches": [],
        "_rule": ("A finding costs points only on unanimous AFFIRM by every voter of a "
                  "quorate round that includes the arbiter. Anything else is struck: "
                  "the penalty is refunded and the remark deleted, not softened."),
    }

    if args.check_final:
        try:
            report["breaches"] = check_final(load_json(args.check_final),
                                             surviving_ids, struck_ids)
        except (OSError, json.JSONDecodeError) as exc:
            print(json.dumps({"error": f"cannot read final scores: {exc}"}), file=sys.stderr)
            return 1

    print(f"{args.panel_dir}")
    print(f"  findings {len(findings)}   survive {len(surviving)}   struck {len(struck)}")
    for r in struck:
        print(f"  STRUCK {r['id']} [{r['notebook']}.{r['criterion']}] {r['resolution']}")
    for b in report["breaches"]:
        print(f"  BREACH {b['key']}: {b['reason']}")

    if args.write:
        out = Path(args.panel_dir)
        (out / "gate_report.json").write_text(
            json.dumps(report, indent=1, ensure_ascii=False) + "\n", "utf-8")
        (out / "surviving_findings.json").write_text(
            json.dumps(surviving, indent=1, ensure_ascii=False) + "\n", "utf-8")
        (out / "struck_findings.json").write_text(
            json.dumps(struck, indent=1, ensure_ascii=False) + "\n", "utf-8")
        print("  written")

    return 3 if report["breaches"] else 0


if __name__ == "__main__":
    sys.exit(main())
