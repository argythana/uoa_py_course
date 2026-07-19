#!/usr/bin/env python3
"""
record_grade.py — record one student's AI-suggested final-assignment grade in
the eClass mirror DB (source of truth) and regenerate the instructor's ODS
ledger from it (derived export; both live under gitignored admin_docs/).

Usage:
    record_grade.py --year 2026 <slug> <grade> [--ods PATH] [--db PATH]

Behaviour (fully deterministic, no LLM, no network):

  - Resolves the student (user_id, full name, "Αριθμός Μητρώου"/AM) from the
    eClass mirror DB (admin_docs/eclass_data/eclass.db) by matching the given
    ``lastname_t`` slug against ``roster_slugs.slugify(full_name)`` over the
    roster. A student missing from the mirror is an error — refresh the mirror
    with automation_infrastructure/eclass/refresh_db.py first.
  - Upserts a ``grades`` row keyed on (user_id, grade_item) with
    ``grade_item = final_assignment_<year>_ai_suggested`` and ``max_score = 10``
    — the distinct label keeps AI-suggested grades from ever masquerading as
    scraped official gradebook entries. Re-recording a student replaces the
    score. ``assignment_id`` is linked when a single assignment matches the year.
  - Regenerates the ODS ledger from the DB (creating it if missing):
    ``admin_docs/student_lists_grades/year=<year>/final_assignment_grades_<year>.ods``,
    one sheet ``final_assignment_<year>``, columns
    Ονοματεπώνυμο | Αριθμός Μητρώου | Βαθμός, rows sorted by name, numeric
    grade cells. The ODS is a **view of the DB** — do not hand-edit it; it is
    rebuilt on every recording.

Prints a small JSON status to stdout (paths + action, never the student's name).
Exit codes: 0 ok · 2 student not found / ambiguous · 1 error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableCell, TableRow
from odf.text import P

HEADERS = ["Ονοματεπώνυμο", "Αριθμός Μητρώου", "Βαθμός"]


def _find_repo_root(start: Path) -> Path:
    # Same strategy as the pipeline's locate_student_submission.py: the skill
    # may live outside the repo (symlinked), so fall back to walking up from cwd.
    for origin in (start, Path.cwd()):
        for p in [origin, *origin.parents]:
            if (p / "automation_infrastructure").is_dir() or (p / ".git").exists():
                return p
    return start


def _write_ods(ods_path: Path, sheet_name: str, rows: list[tuple[str, str, float]]) -> None:
    doc = OpenDocumentSpreadsheet()
    sheet = Table(name=sheet_name)
    header = TableRow()
    for text in HEADERS:
        cell = TableCell(valuetype="string")
        cell.addElement(P(text=text))
        header.addElement(cell)
    sheet.addElement(header)
    for name, am, score in rows:
        tr = TableRow()
        for cell in (TableCell(valuetype="string"),
                     TableCell(valuetype="string"),
                     TableCell(valuetype="float", value=float(score))):
            tr.addElement(cell)
        for cell, text in zip(tr.getElementsByType(TableCell), (name, am, score)):
            cell.addElement(P(text=str(text)))
        sheet.addElement(tr)
    doc.spreadsheet.addElement(sheet)
    ods_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(ods_path))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="student slug, e.g. argyriou_t")
    ap.add_argument("grade", type=float, help="suggested total assignment grade, e.g. 8.5")
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--ods", type=Path, default=None,
                    help="ledger path (default: admin_docs/student_lists_grades/"
                         "year=<year>/final_assignment_grades_<year>.ods)")
    ap.add_argument("--db", type=Path, default=None,
                    help="eClass mirror DB (default: admin_docs/eclass_data/eclass.db)")
    args = ap.parse_args(argv)

    repo_root = _find_repo_root(Path(__file__).resolve())
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from automation_infrastructure.eclass.db import open_db, upsert_grade
    from automation_infrastructure.roster_slugs import slugify

    db_path = args.db or (repo_root / "admin_docs" / "eclass_data" / "eclass.db")
    if not db_path.exists():
        print(json.dumps({"error": f"DB not found: {db_path}"}), file=sys.stderr)
        return 1
    ods_path = args.ods or (repo_root / "admin_docs" / "student_lists_grades"
                            / f"year={args.year}"
                            / f"final_assignment_grades_{args.year}.ods")
    sheet_name = f"final_assignment_{args.year}"
    grade_item = f"final_assignment_{args.year}_ai_suggested"

    conn = open_db(db_path)
    try:
        users = conn.execute(
            "SELECT user_id, full_name FROM users ORDER BY full_name").fetchall()
        matches = [u for u in users if slugify(u[1]) == args.slug]
        if len(matches) != 1:
            print(json.dumps({
                "error": f"{len(matches)} roster users slugify to {args.slug!r}."
                         " Refresh the mirror (automation_infrastructure/eclass/"
                         "refresh_db.py) if the student is missing.",
            }), file=sys.stderr)
            return 2
        user_id = matches[0][0]

        assignment_ids = [r[0] for r in conn.execute(
            "SELECT assignment_id FROM assignments WHERE title LIKE ?",
            (f"%{args.year}%",)).fetchall()]
        assignment_id = assignment_ids[0] if len(assignment_ids) == 1 else None

        existed = conn.execute(
            "SELECT 1 FROM grades WHERE user_id = ? AND grade_item = ?",
            (user_id, grade_item)).fetchone() is not None
        upsert_grade(conn, user_id=user_id, grade_item=grade_item,
                     score=args.grade, max_score=10.0, assignment_id=assignment_id)
        conn.commit()

        ods_created = not ods_path.exists()
        rows = conn.execute(
            """
            SELECT u.full_name, COALESCE(u.am, ''), g.score
            FROM grades g JOIN users u ON u.user_id = g.user_id
            WHERE g.grade_item = ?
            ORDER BY u.full_name
            """,
            (grade_item,)).fetchall()
    finally:
        conn.close()

    _write_ods(ods_path, sheet_name, rows)
    print(json.dumps({
        "db": str(db_path), "grade_item": grade_item,
        "db_action": "updated" if existed else "inserted",
        "ods": str(ods_path), "sheet": sheet_name,
        "ods_action": "created" if ods_created else "regenerated",
        "slug": args.slug, "grade": args.grade, "rows": len(rows),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
