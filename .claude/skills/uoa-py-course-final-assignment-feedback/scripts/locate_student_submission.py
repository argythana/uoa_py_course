#!/usr/bin/env python3
"""
locate_student_submission.py — find one student's final-assignment draft under the
unified per-student layout.

Both the eClass download automation and emailed/manual drafts now land in the SAME place:

    students_work/class_<YY>/<lastname_t>/final_assignment/

Inside `final_assignment/` the download carries a **download-date suffix** (the
automation downloads + extracts there, tagging the artifact with its date). The exact
shape may be a dated extracted subfolder, a dated .zip, or the notebooks placed directly
— this resolver handles all of them and picks the LATEST dated artifact.

Given a student query and a class year, it resolves:
  - the student's folder (matched by `lastname_t` slug / surname / substring),
  - the submission to feed the inventory step (preferring an already-extracted folder;
    a .zip is flagged `needs_extract` so the inventory step unpacks it),
  - the feedback directory (always the student's `final_assignment/`).

Usage:
    locate_student_submission.py [student] [--year 2026] [--root students_work] [--class-dir DIR]

Output is JSON on stdout. No network, no LLM.
Exit codes: 0 resolved a submission · 2 ambiguous / none given / nothing downloaded yet
            · 1 class folder not found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz"}
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
# Matches both the per-submission `downloaded_<date>/` folder and the combined
# `<title>__downloaded_<date>` artifact — "downloaded" preceded by start or `_`.
DOWNLOADED_DATE_RE = re.compile(r"(?:^|_)downloaded_(\d{4}-\d{2}-\d{2})")


def _has_notebooks(folder: Path) -> bool:
    """True if the folder contains a real .ipynb (ignoring checkpoints / OS junk)."""
    for p in folder.rglob("*.ipynb"):
        parts = p.parts
        if ".ipynb_checkpoints" in parts or "__MACOSX" in parts:
            continue
        if p.name.startswith("._"):
            continue
        return True
    return False


def _inspect_dated_dir(chosen: Path) -> dict:
    """Decide what to feed the inventory step for a dated download *folder*.

    The per-submission download saves a raw `.zip` into `downloaded_<date>/`
    (and, since the extraction fix, may also extract it there). So a dated folder
    can be: already-extracted (has notebooks), or zip-only (needs extracting), or
    a non-zip archive that needs manual extraction.
    """
    date = _parsed_date(chosen.name)
    if _has_notebooks(chosen):
        return {"submission_path": str(chosen), "submission_kind": "dated_folder",
                "is_extracted": True, "needs_extract": False, "download_date": date}

    # No notebooks yet — look for an archive sitting directly inside the folder.
    archives = sorted((c for c in chosen.iterdir()
                       if c.is_file() and c.suffix.lower() in ARCHIVE_EXTS),
                      key=lambda c: c.stat().st_mtime)
    zips = [a for a in archives if a.suffix.lower() == ".zip"]
    if zips:
        inner = zips[-1]
        return {"submission_path": str(inner), "submission_kind": "dated_zip_in_folder",
                "is_extracted": False, "needs_extract": True, "download_date": date,
                "note": ("Dated download folder holds an un-extracted .zip — the "
                         "inventory step will unpack it.")}
    if archives:
        inner = archives[-1]
        return {"submission_path": str(inner), "submission_kind": "dated_archive_in_folder",
                "is_extracted": False, "needs_extract": False, "download_date": date,
                "note": f"Archive is {inner.suffix} — extract it manually first."}
    return {"submission_path": None, "submission_kind": "dated_folder_empty",
            "download_date": date,
            "note": "Dated download folder has no notebooks and no archive."}


def _find_repo_root(start: Path) -> Path:
    # The skill may live outside the repo (e.g. ~/.local/share/skillden/) and be
    # reached via a symlink, so walking up from __file__ can escape the repo —
    # fall back to walking up from the cwd (the skill runs from the repo root).
    for origin in (start, Path.cwd()):
        for p in [origin, *origin.parents]:
            if (p / "automation_infrastructure").is_dir() or (p / ".git").exists():
                return p
    return start


def _load_slugify():
    """Reuse roster_slugs.slugify (canonical name→lastname_t). Fall back to ASCII."""
    repo_root = _find_repo_root(Path(__file__).resolve())
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from automation_infrastructure.roster_slugs import slugify  # type: ignore
        return slugify
    except Exception:
        def _fallback(full_name: str) -> str:
            toks = [re.sub(r"[^a-z0-9]+", "", t.lower()) for t in full_name.split()]
            toks = [t for t in toks if t]
            if not toks:
                return ""
            initials = "_".join(t[0] for t in toks[1:]) if len(toks) > 1 else ""
            return f"{toks[0]}_{initials}".strip("_")
        return _fallback


def _date_key(name: str):
    """Sort key for 'latest dated artifact': prefer __downloaded_<date>, else any date."""
    m = DOWNLOADED_DATE_RE.search(name) or DATE_RE.search(name)
    return (m.group(1) if m else "", name)


def _parsed_date(name: str) -> str | None:
    m = DOWNLOADED_DATE_RE.search(name) or DATE_RE.search(name)
    return m.group(1) if m else None


def resolve_class_dir(root: Path, year: int, class_dir: Path | None) -> Path | None:
    if class_dir is not None:
        return class_dir if class_dir.is_dir() else None
    for cand in (root / f"class_{year % 100:02d}", root / f"class_{year}"):
        if cand.is_dir():
            return cand
    return None


def match_students(class_dir: Path, query: str, slugify) -> list[Path]:
    dirs = [d for d in sorted(class_dir.iterdir())
            if d.is_dir() and not d.name.startswith(".")]
    q = query.strip().lower()
    qslug = (slugify(q) or "").lower()
    qsurname = qslug.split("_")[0] if qslug else ""
    out = []
    for d in dirs:
        name = d.name.lower()
        if (name == q or (qslug and name == qslug) or q in name
                or (qsurname and name.startswith(qsurname))):
            out.append(d)
    return out


def pick_submission(fa: Path) -> dict:
    """Choose what to feed the inventory step from a final_assignment/ folder."""
    if not fa.is_dir():
        return {"submission_path": None, "submission_kind": "no_final_assignment_dir"}

    children = [c for c in fa.iterdir()
                if not c.name.startswith(".") and c.name != "__MACOSX"]
    if not children:
        return {"submission_path": None, "submission_kind": "empty"}

    dated_dirs = sorted((c for c in children if c.is_dir() and _parsed_date(c.name)),
                        key=lambda c: _date_key(c.name))
    dated_zips = sorted((c for c in children if c.is_file()
                         and c.suffix.lower() == ".zip" and _parsed_date(c.name)),
                        key=lambda c: _date_key(c.name))
    notebooks_direct = any(p.suffix.lower() == ".ipynb"
                           for p in fa.rglob("*")
                           if ".ipynb_checkpoints" not in p.parts)
    plain_zips = [c for c in children
                  if c.is_file() and c.suffix.lower() in ARCHIVE_EXTS]

    if dated_dirs:
        return _inspect_dated_dir(dated_dirs[-1])
    if dated_zips:
        chosen = dated_zips[-1]
        return {"submission_path": str(chosen), "submission_kind": "dated_zip",
                "is_extracted": False, "needs_extract": chosen.suffix.lower() == ".zip",
                "download_date": _parsed_date(chosen.name)}
    if notebooks_direct:
        return {"submission_path": str(fa), "submission_kind": "notebooks_in_place",
                "is_extracted": True, "needs_extract": False, "download_date": None}
    if plain_zips:
        chosen = sorted(plain_zips, key=lambda c: c.stat().st_mtime)[-1]
        return {"submission_path": str(chosen), "submission_kind": "archive",
                "is_extracted": False,
                "needs_extract": chosen.suffix.lower() == ".zip",
                "download_date": None,
                "note": (None if chosen.suffix.lower() == ".zip"
                         else "Archive is .rar/.7z — extract it manually first.")}
    return {"submission_path": None, "submission_kind": "unrecognised",
            "contents": [c.name for c in children]}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("student", nargs="?", default=None,
                    help="Student query: lastname_t slug, surname, or substring.")
    ap.add_argument("--year", type=int, default=date.today().year)
    ap.add_argument("--root", type=Path, default=None,
                    help="students_work root (default: <repo>/students_work).")
    ap.add_argument("--class-dir", type=Path, default=None,
                    help="Explicit class folder (overrides --year/--root).")
    args = ap.parse_args(argv)

    repo_root = _find_repo_root(Path(__file__).resolve())
    root = args.root or (repo_root / "students_work")
    slugify = _load_slugify()

    class_dir = resolve_class_dir(root, args.year, args.class_dir)
    if class_dir is None:
        print(json.dumps({
            "error": "Class folder not found.",
            "looked_for": [str(root / f"class_{args.year % 100:02d}"),
                           str(root / f"class_{args.year}")],
        }, ensure_ascii=False), file=sys.stderr)
        return 1

    base = {"class_dir": str(class_dir), "year": args.year}

    if args.student is None:
        roster = []
        for d in sorted(class_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            fa = d / "final_assignment"
            sub = pick_submission(fa)
            roster.append({"slug": d.name,
                           "has_submission": bool(sub.get("submission_path")),
                           "submission_kind": sub["submission_kind"]})
        base["students"] = roster
        base["note"] = "No student given — pick a slug with has_submission=true."
        print(json.dumps(base, indent=2, ensure_ascii=False))
        return 2

    matches = match_students(class_dir, args.student, slugify)
    base["query"] = args.student
    if len(matches) != 1:
        base["matches"] = [d.name for d in matches]
        base["note"] = ("No student folder matched — check the slug/spelling."
                        if not matches else "Multiple matches — narrow the query.")
        print(json.dumps(base, indent=2, ensure_ascii=False))
        return 2

    student_dir = matches[0]
    fa = student_dir / "final_assignment"
    sub = pick_submission(fa)
    base.update({
        "slug": student_dir.name,
        "student_dir": str(student_dir),
        "final_assignment_dir": str(fa),
        "feedback_dir": str(fa),  # feedback is written here, alongside the submission
        **sub,
    })
    if not sub.get("submission_path"):
        base["note"] = ("No submission found in final_assignment/ yet "
                        f"({sub['submission_kind']}). It may not be downloaded.")
        print(json.dumps(base, indent=2, ensure_ascii=False))
        return 2

    print(json.dumps(base, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
