#!/usr/bin/env python3
"""
audit_grades_recorded.py — verify the recording invariant:

    A student is "graded" ONLY when the AI-suggested grade is present in BOTH
    the eClass mirror DB (grades table) AND the derived ODS ledger.

A student can have written feedback/grade-summary files on disk yet never have
been passed through ``record_grade.py`` (e.g. graded by an earlier skill version
before recording existed). Those students look done but are invisible to the
instructor's ledger — this script catches exactly that gap.

Usage:
    audit_grades_recorded.py --year 2026 [--db PATH] [--ods PATH]

What it does (deterministic, no LLM, no network):
  - "Graded on disk"  = a student folder under students_work/class_<YY>/<slug>/
    contains at least one ``*_assignment_grade_summary_*.md`` file.
  - "In DB"           = a grades row exists with
    grade_item = final_assignment_<year>_ai_suggested, mapped to the student via
    roster_slugs.slugify(full_name) == <slug>.
  - "In ODS"          = the ledger sheet final_assignment_<year> has a data row
    for that student (ODS is regenerated from the DB, so this should mirror DB;
    checked independently so a corrupt/stale ODS is still caught).

Reports three sets:
  - MISSING   : graded on disk but NOT recorded (the invariant violation) → these
                are "not really graded". Fix by re-running the grade cycle or, if
                the grade is trusted, ``record_grade.py --year <Y> <slug> <grade>``.
  - RECORDED  : graded on disk AND in both DB + ODS (the healthy state).
  - ORPHANS   : recorded in DB/ODS but no grade-summary file on disk (informational
                — e.g. files cleaned up, or recorded by hand).

Exit codes: 0 all graded-on-disk students are recorded · 3 one or more MISSING ·
2 DB/ODS not found · 1 error. Prints a human table to stderr and a JSON summary
to stdout. Never prints anything beyond slugs (no names, no PII) unless --names.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for origin in (start, Path.cwd()):
        for p in [origin, *origin.parents]:
            if (p / "automation_infrastructure").is_dir() or (p / ".git").exists():
                return p
    return start


def _graded_on_disk(class_dir: Path) -> set[str]:
    """Slugs whose folder holds at least one *_assignment_grade_summary_*.md."""
    graded: set[str] = set()
    if not class_dir.is_dir():
        return graded
    for student_dir in sorted(class_dir.iterdir()):
        if not student_dir.is_dir():
            continue
        hits = list(student_dir.glob("**/*_assignment_grade_summary_*.md"))
        if hits:
            graded.add(student_dir.name)
    return graded


def _ods_slugs(ods_path: Path, sheet_name: str, slugify) -> set[str]:
    """Slugs present as data rows in the ODS ledger sheet (mapped from name)."""
    if not ods_path.exists():
        return set()
    from odf.opendocument import load
    from odf.table import Table, TableRow, TableCell
    from odf.text import P

    doc = load(str(ods_path))
    slugs: set[str] = set()
    for tbl in doc.spreadsheet.getElementsByType(Table):
        if tbl.getAttribute("name") != sheet_name:
            continue
        for i, tr in enumerate(tbl.getElementsByType(TableRow)):
            if i == 0:  # header
                continue
            cells = tr.getElementsByType(TableCell)
            if not cells:
                continue
            name = "".join(str(p) for p in cells[0].getElementsByType(P)).strip()
            if name:
                slugs.add(slugify(name))
    return slugs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--db", type=Path, default=None)
    ap.add_argument("--ods", type=Path, default=None)
    ap.add_argument("--names", action="store_true",
                    help="also print full names (PII) — off by default")
    args = ap.parse_args(argv)

    repo_root = _find_repo_root(Path(__file__).resolve())
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from automation_infrastructure.eclass.db import open_db
    from automation_infrastructure.roster_slugs import slugify

    yy = args.year % 100
    class_dir = repo_root / "students_work" / f"class_{yy}"
    db_path = args.db or (repo_root / "admin_docs" / "eclass_data" / "eclass.db")
    ods_path = args.ods or (repo_root / "admin_docs" / "student_lists_grades"
                            / f"year={args.year}"
                            / f"final_assignment_grades_{args.year}.ods")
    sheet_name = f"final_assignment_{args.year}"
    grade_item = f"final_assignment_{args.year}_ai_suggested"

    if not db_path.exists():
        print(json.dumps({"error": f"DB not found: {db_path}"}), file=sys.stderr)
        return 2

    graded = _graded_on_disk(class_dir)

    conn = open_db(db_path)
    try:
        users = conn.execute("SELECT user_id, full_name FROM users").fetchall()
        uid_to_slug = {u[0]: slugify(u[1]) for u in users}
        uid_to_name = {u[0]: u[1] for u in users}
        db_rows = conn.execute(
            "SELECT user_id, score FROM grades WHERE grade_item = ?",
            (grade_item,)).fetchall()
    finally:
        conn.close()

    db_slug_to_score = {}
    for uid, score in db_rows:
        slug = uid_to_slug.get(uid)
        if slug:
            db_slug_to_score[slug] = score
    db_slugs = set(db_slug_to_score)
    ods_slugs = _ods_slugs(ods_path, sheet_name, slugify)

    recorded = sorted(s for s in graded if s in db_slugs and s in ods_slugs)
    missing = sorted(graded - db_slugs)             # graded on disk, not in DB
    in_db_not_ods = sorted(db_slugs - ods_slugs)    # DB/ODS drift (should be empty)
    orphans = sorted(db_slugs - graded)             # recorded but no summary file

    def line(slug: str) -> str:
        if not args.names:
            return slug
        uid = next((u for u, s in uid_to_slug.items() if s == slug), None)
        return f"{slug}  ({uid_to_name.get(uid, '?')})"

    out = sys.stderr
    print(f"\n=== Grade-recording audit — final_assignment {args.year} ===", file=out)
    print(f"graded on disk: {len(graded)} · in DB: {len(db_slugs)} · "
          f"in ODS: {len(ods_slugs)}", file=out)
    print(f"\nRECORDED (disk + DB + ODS): {len(recorded)}", file=out)
    for s in recorded:
        print(f"  ok   {line(s)}  = {db_slug_to_score.get(s)}", file=out)
    if missing:
        print(f"\nMISSING (graded on disk, NOT recorded — not really graded): "
              f"{len(missing)}", file=out)
        for s in missing:
            print(f"  !!   {line(s)}", file=out)
    if in_db_not_ods:
        print(f"\nDB/ODS DRIFT (in DB, not in ODS — regenerate ledger): "
              f"{len(in_db_not_ods)}", file=out)
        for s in in_db_not_ods:
            print(f"  !!   {line(s)}", file=out)
    if orphans:
        print(f"\nORPHANS (recorded, no summary file on disk — informational): "
              f"{len(orphans)}", file=out)
        for s in orphans:
            print(f"  ?    {line(s)}  = {db_slug_to_score.get(s)}", file=out)
    print("", file=out)

    print(json.dumps({
        "year": args.year, "grade_item": grade_item,
        "graded_on_disk": len(graded), "in_db": len(db_slugs), "in_ods": len(ods_slugs),
        "recorded": recorded, "missing": missing,
        "db_ods_drift": in_db_not_ods, "orphans": orphans,
        "all_graded_recorded": not missing and not in_db_not_ods,
    }, ensure_ascii=False))
    return 3 if (missing or in_db_not_ods) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
