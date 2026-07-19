"""Download student submissions for a course's final assignment.

Logs into eClass once (CAS SSO), finds the current year's assignment in the
``work`` module, and downloads each student's submission straight into the
per-student folder that ``scaffold_student_dirs.sh`` created, under a subfolder
named with the **download date** — so each run is a dated snapshot sitting right
next to the rest of that student's work. Each downloaded ``.zip`` is then
**extracted in place** (see :mod:`extract`), so the dated folder holds a
ready-to-read submission (the original ``.zip`` is kept alongside by default):

    students_work/class_26/
      papadopoulou_m/final_assignment/downloaded_2026-06-09/
        papadopoulou_m_assignment.zip          # original (kept unless --no-keep-zip)
        papadopoulou_m_assignment/...           # extracted notebooks + data/
      georgiou_a_m/final_assignment/downloaded_2026-06-09/
        final_assignment_georgiou.zip
        final_assignment_georgiou/...

Extraction is path-traversal-safe and skips macOS junk; a non-zip upload (a
loose ``.ipynb``, or a ``.rar``/``.7z`` the stdlib can't open) is left in place
with a note. Pass ``--no-extract`` to keep only the raw ``.zip``.

The per-student slug is derived with the same
:func:`automation_infrastructure.roster_slugs.slugify` used to create those
folders, so submissions land in the right place. ``students_work/`` is
gitignored (student PII). A submitter who has no folder yet (e.g. not in the
roster snapshot) gets one created.

By default submissions are fetched **one at a time** (``?get=<id>``): streaming
starts immediately, each file is resumable, and progress is per student. The
alternative ``--combined`` mode pulls eClass's single all-in-one ZIP
(``?download=<id>``) into one dated folder at the class root — simpler, but it
stalls upfront while the server builds the whole archive.

**Dedup is driven by the eClass mirror DB** (``admin_docs/eclass_data/eclass.db``,
gitignored). Each downloaded submission is recorded in its ``submissions`` table
(submission_id, submitted_at, local file_path); a later run skips any submission
whose submission_id + submitted_at is already on record — one indexed lookup,
not a walk over every student's folder. A **resubmission** (a newer
``submitted_at`` for the same submission_id) re-downloads and updates the row;
``--force`` re-fetches regardless. Submissions downloaded before this ledger
existed are matched on disk once (via their ``.submission_meta.json`` sidecar,
still written alongside each file) and **backfilled** into the DB, so the first
run under this scheme indexes them instead of re-fetching. If the DB can't be
opened the run degrades to the on-disk dedup.

The assignment is discovered by year (the work entry whose title contains the
year, e.g. "Final Assignment Python 2026"); pass ``--assignment-id`` to override.

Usage (from the repo root)::

    python -m automation_infrastructure.eclass.download_submissions
    python -m automation_infrastructure.eclass.download_submissions --year 2026
    python -m automation_infrastructure.eclass.download_submissions --assignment-id 78801
    python -m automation_infrastructure.eclass.download_submissions --combined

Single-attempt login (see ``session.py``): a wrong password is NOT retried,
because repeated CAS failures can lock the UoA account.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

from ..roster_slugs import slugify as student_slug
from .db import (
    get_submission,
    known_user_ids,
    open_db,
    upsert_assignment,
    upsert_submission,
)
from .extract import ExtractResult, extract_archive
from .scrapers.work import (
    Assignment,
    Submission,
    download_all_submissions,
    download_submission,
    find_assignment_for_year,
    list_assignments,
    list_submissions,
    sanitize_filename,
    slugify_title,
)
from .session import LoginError, login, logout

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STUDENTS_ROOT = REPO_ROOT / "students_work"
DEFAULT_COURSE = "ECON537"
FINAL_ASSIGNMENT_SUBDIR = "final_assignment"
# Sidecar dropped next to each downloaded submission so later runs can tell
# "already have this exact submission" from "the student resubmitted".
SUBMISSION_META = ".submission_meta.json"


def _human_bytes(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _make_progress(label: str):
    """A throttled stderr progress printer for one streamed file."""
    state = {"last": -1}

    def progress(got: int, total: int) -> None:
        if total:
            pct = int(got * 100 / total)
            if pct == state["last"]:
                return
            state["last"] = pct
            line = f"\r  {label:24} {pct:3d}%  ({_human_bytes(got)} / {_human_bytes(total)})"
        else:
            mb = got >> 20
            if mb == state["last"]:
                return
            state["last"] = mb
            line = f"\r  {label:24} {_human_bytes(got)}"
        print(line, end="", file=sys.stderr, flush=True)

    return progress


def _resolve_assignment(session, course: str, year: int, assignment_id: int | None) -> Assignment:
    """Return the Assignment to download — by explicit id or by year discovery."""
    if assignment_id is None:
        return find_assignment_for_year(session, course, year)
    for asg in list_assignments(session, course):
        if asg.assignment_id == assignment_id:
            return asg
    return Assignment(assignment_id, f"{course}_work_{assignment_id}", None, None)


def _describe_extract(result: ExtractResult) -> str:
    """A short, human-readable suffix for the per-student completion line."""
    if result.kind == "not-archive":
        return ""  # a loose .ipynb/.pdf — nothing to extract
    if result.kind == "unsupported":
        return f"  (⚠ {result.archive.suffix} not auto-extracted)"
    if not result.extracted:
        return "  (⚠ extract failed)"
    suffix = f"  → extracted {result.member_count} file(s)"
    if result.skipped_env_member_count:
        suffix += f", {result.skipped_env_member_count} bundled venv file(s) skipped"
    if result.removed_archive:
        suffix += ", zip removed"
    return suffix


_GREEK_MONTHS = {
    "ιανουαριου": 1, "φεβρουαριου": 2, "μαρτιου": 3, "απριλιου": 4,
    "μαιου": 5, "ιουνιου": 6, "ιουλιου": 7, "αυγουστου": 8,
    "σεπτεμβριου": 9, "οκτωβριου": 10, "νοεμβριου": 11, "δεκεμβριου": 12,
}


def _parse_greek_dt(text: str | None) -> datetime | None:
    """Parse an eClass submission-time string into a ``datetime`` (None if it can't).

    Format: ``"Δευτέρα 25 Μαΐου 2026 - 11:55 π.μ."`` — day name, day, genitive
    Greek month, year, time, and ``π.μ.``/``μ.μ.`` (AM/PM). Accents are stripped
    before matching so ``Μαΐου`` → ``μαιου``. Used only to tell whether a student
    resubmitted *after* we last downloaded their file.
    """
    if not text:
        return None
    norm = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    ).lower()
    m = re.search(
        r"(\d{1,2})\s+([α-ω]+)\s+(\d{4})\s*-\s*(\d{1,2}):(\d{2})\s*([πμ])\.?\s*μ\.?",
        norm,
    )
    if not m:
        return None
    day, month_word, year, hour, minute, meridiem = m.groups()
    month = _GREEK_MONTHS.get(month_word)
    if month is None:
        return None
    hour = int(hour)
    if meridiem == "μ" and hour != 12:      # μ.μ. = PM
        hour += 12
    elif meridiem == "π" and hour == 12:    # 12 π.μ. = midnight
        hour = 0
    try:
        return datetime(int(year), month, int(day), hour, int(minute))
    except ValueError:
        return None


def _hint_matches(on_disk_name: str, filename_hint: str) -> bool:
    """True if a downloaded file matches a submission's (possibly truncated) hint.

    eClass truncates long names in the link ``title`` with a *middle* ellipsis
    (``"final_assignment_python_the...ka.zip"``), while the file on disk carries
    the full name from Content-Disposition. So match prefix+suffix around the
    ellipsis; with no ellipsis, require an exact match.
    """
    hint = sanitize_filename(filename_hint)
    for ellipsis in ("...", "…"):
        if ellipsis in hint:
            prefix, _, suffix = hint.partition(ellipsis)
            return on_disk_name.startswith(prefix) and on_disk_name.endswith(suffix)
    return on_disk_name == hint


def _write_submission_meta(meta_path: Path, course: str, assignment_id: int,
                           sub: Submission, filename: str) -> None:
    """Record what submission a dated folder holds, so later runs can dedup it."""
    meta = {
        "course": course,
        "assignment_id": assignment_id,
        "submission_id": sub.submission_id,
        "submitted_at": sub.submitted_at,
        "student_name": sub.student_name,
        "filename": filename,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _find_existing_download(student_dir: Path, sub: Submission,
                            course: str, assignment_id: int) -> Path | None:
    """Return a prior dated folder already holding *this* submission, else None.

    A submission is "the same" when a previous download has the same
    ``submission_id`` **and** the same ``submitted_at`` timestamp — so a genuine
    resubmission (new timestamp) is *not* matched and gets re-fetched.

    Folders downloaded before this dedup existed carry no sidecar; for those we
    fall back to matching the submitted filename and **backfill** a sidecar, so
    the first run under the new logic registers existing downloads instead of
    re-fetching them. (Blind spot: a resubmission with an identical filename made
    between that old download and this run is matched by name and skipped; use
    ``--force`` to override.)
    """
    fa = student_dir / FINAL_ASSIGNMENT_SUBDIR
    if not fa.exists():
        return None
    sub_dt = _parse_greek_dt(sub.submitted_at)
    for folder in sorted(fa.glob("downloaded_*")):
        meta_path = folder / SUBMISSION_META
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if (meta.get("submission_id") == sub.submission_id
                    and meta.get("submitted_at") == sub.submitted_at):
                return folder
            continue  # sidecar present but for a different/older submission
        # No sidecar (pre-dedup download): match the submitted filename, then
        # confirm via the timestamp that the student hasn't resubmitted since.
        if not sub.filename_hint:
            continue
        match = next(
            (f for f in folder.iterdir()
             if f.is_file() and f.name != SUBMISSION_META
             and _hint_matches(f.name, sub.filename_hint)),
            None,
        )
        if match is None:
            continue
        # If the live submission time is later than when we downloaded this file,
        # the student resubmitted — keep looking (and ultimately re-download).
        if sub_dt is not None and sub_dt > datetime.fromtimestamp(match.stat().st_mtime):
            continue
        _write_submission_meta(meta_path, course, assignment_id, sub, match.name)
        return folder
    return None


def _repo_relative(path: Path) -> str:
    """``path`` as a repo-root-relative string, or absolute if it lies outside."""
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _file_in_prior_folder(folder: Path) -> Path | None:
    """The submitted file inside a prior dated folder, per its sidecar.

    ``_find_existing_download`` guarantees a sidecar in ``folder`` (it backfills
    one when matching by filename), so the ``filename`` it records points at the
    submitted file we want to register in the DB ledger.
    """
    try:
        meta = json.loads((folder / SUBMISSION_META).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    name = meta.get("filename")
    return folder / name if name else None


def _record_submission(conn, sub: Submission, user_id: int | None,
                       assignment_id: int, file_path: Path | None,
                       warnings: list[str], slug: str) -> None:
    """Upsert one submission into the mirror DB ledger; never abort on failure.

    A failed ledger write is non-fatal — the file is already on disk, and the
    next run's on-disk fallback will re-index it — so it degrades to a warning.
    """
    try:
        upsert_submission(
            conn,
            submission_id=sub.submission_id,
            user_id=user_id,
            assignment_id=assignment_id,
            submitted_at=sub.submitted_at,
            file_path=_repo_relative(file_path) if file_path else None,
        )
        conn.commit()
    except sqlite3.Error as exc:
        warnings.append(f"{slug}: could not record submission in db ({exc})")


def _download_per_submission(session, course, asg, class_dir, date_str, force,
                             conn=None, extract=True, keep_zip=True):
    """Download each submission into <class_dir>/<slug>/final_assignment/downloaded_<date>/.

    Dedup is driven by the eClass mirror DB (``conn``): every downloaded
    submission is recorded in the ``submissions`` table, and a later run skips
    any submission whose ``submission_id`` + ``submitted_at`` is already on
    record — one indexed lookup, no walking each student's folder. A submission
    not yet in the DB falls back to the on-disk check once and is **backfilled**
    into the ledger, so the first run under this scheme indexes pre-existing
    downloads instead of re-fetching them. With ``conn=None`` (DB unavailable)
    the behaviour degrades to the on-disk-only dedup.

    Each downloaded ``.zip`` is then extracted in place (unless ``extract`` is
    false); the raw ``.zip`` is kept alongside the extracted tree unless
    ``keep_zip`` is false.

    Returns (downloaded, skipped, bytes, new_student_folders, warnings).
    """
    subs = list_submissions(session, course, asg.assignment_id)
    print(f"{len(subs)} submission(s) found.")
    downloaded = skipped = total_bytes = 0
    new_folders: list[str] = []
    warnings: list[str] = []
    known = known_user_ids(conn) if conn is not None else set()

    for sub in subs:
        slug = student_slug(sub.student_name) if sub.student_name else f"submission_{sub.submission_id}"
        student_dir = class_dir / slug
        if not student_dir.exists():
            new_folders.append(slug)  # submitter not in the scaffolded roster

        # The submission's eClass user_id (== profile_id) — stored only when it
        # resolves to a roster row, else NULL (a submitter outside the snapshot).
        user_id = sub.profile_id if sub.profile_id in known else None

        # 1) DB fast path: do we already hold this exact submission? A matching
        #    submitted_at means "downloaded"; a changed one means "resubmitted".
        if conn is not None and not force:
            row = get_submission(conn, sub.submission_id)
            if row is not None and row["submitted_at"] == sub.submitted_at:
                print(f"  {slug:24} already downloaded (db) — skipping")
                skipped += 1
                continue

        # 2) On-disk fallback / one-time backfill: a copy already on disk for
        #    this exact submission (downloaded before the ledger existed, or a
        #    rebuilt DB)? Index it so the DB fast path catches it next time.
        if not force:
            prior = _find_existing_download(student_dir, sub, course, asg.assignment_id)
            if prior is not None:
                if conn is not None:
                    _record_submission(conn, sub, user_id, asg.assignment_id,
                                       _file_in_prior_folder(prior), warnings, slug)
                tag = "indexed" if conn is not None else "on disk"
                print(f"  {slug:24} already downloaded ({prior.name}) — {tag}, skipping")
                skipped += 1
                continue

        dest = student_dir / FINAL_ASSIGNMENT_SUBDIR / f"downloaded_{date_str}"

        if dest.exists() and any(dest.iterdir()) and not force:
            print(f"  {slug:24} already present today — skipping")
            skipped += 1
            continue

        try:
            saved = download_submission(
                session, course, sub.submission_id, dest, progress=_make_progress(slug),
            )
        except Exception as exc:
            # A single stalled/oversized upload (e.g. a multi-hundred-MB file that
            # times out mid-stream) must not abort the whole batch; record it and
            # move on so the remaining submitters still get fetched.
            print(f"\r  {slug:24} ⚠ download failed: {exc}", file=sys.stderr)
            warnings.append(f"{slug}: download failed ({exc}) — re-run to retry")
            skipped += 1
            continue
        size = saved.stat().st_size
        total_bytes += size
        downloaded += 1
        _write_submission_meta(
            dest / SUBMISSION_META, course, asg.assignment_id, sub, saved.name,
        )
        if conn is not None:
            _record_submission(conn, sub, user_id, asg.assignment_id, saved, warnings, slug)

        extract_note = ""
        if extract:
            result = extract_archive(saved, keep_archive=keep_zip)
            extract_note = _describe_extract(result)
            warnings.extend(f"{slug}: {w}" for w in result.warnings)

        # overwrite the in-place progress line with a clean completion line
        print(f"\r  {slug:24} {_human_bytes(size):>10}  ✓ {saved.name}{extract_note}",
              file=sys.stderr)

    return downloaded, skipped, total_bytes, new_folders, warnings


def _download_combined(session, course, asg, class_dir, date_str, extract, keep_zip, force):
    """Download the all-in-one ZIP into one dated folder at the class root."""
    stem = f"{slugify_title(asg.title)}__downloaded_{date_str}"
    zip_path = class_dir / f"{stem}.zip"
    folder = class_dir / stem
    if (folder.exists() if extract else zip_path.exists()) and not force:
        print(f"already downloaded today: {folder if extract else zip_path}\n(use --force)")
        return
    download_all_submissions(
        session, course, asg.assignment_id, zip_path, progress=_make_progress("(combined zip)"),
    )
    print(file=sys.stderr)
    print(f"downloaded: {zip_path}  ({_human_bytes(zip_path.stat().st_size)})")
    if extract:
        if folder.exists():
            shutil.rmtree(folder)  # a fresh extract must not mix with a stale one
        result = extract_archive(zip_path, folder, keep_archive=keep_zip)
        for warning in result.warnings:
            print(f"  ⚠ {warning}", file=sys.stderr)
        if result.extracted:
            print(f"extracted: {result.member_count} file(s) → {folder}")
            if result.removed_archive:
                print(f"removed intermediate zip: {zip_path.name}")


def main(argv: list[str] | None = None) -> int:
    today = date.today()
    parser = argparse.ArgumentParser(
        description="Download a course's final-assignment submissions into students_work."
    )
    parser.add_argument("--year", type=int, default=today.year,
                        help="Class year: picks the assignment and class_<YY> folder (default: current).")
    parser.add_argument("--course", default=DEFAULT_COURSE, help="eClass course code.")
    parser.add_argument("--assignment-id", type=int, default=None,
                        help="Target a specific work-module assignment id (skips year discovery).")
    parser.add_argument("--students-root", type=Path, default=None,
                        help="Root holding class_<YY>/ (default: students_work/).")
    parser.add_argument("--combined", action="store_true",
                        help="Use eClass's single all-in-one ZIP instead of per-submission downloads.")
    parser.add_argument("--no-extract", action="store_true",
                        help="Keep only the downloaded .zip(s); do not extract them.")
    parser.add_argument("--no-keep-zip", action="store_true",
                        help="Delete each .zip after a successful extract.")
    parser.add_argument("--force", action="store_true",
                        help="Re-download even if this submission was already downloaded "
                             "(bypass the submitted_at dedup check).")
    args = parser.parse_args(argv)

    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass  # rely on env vars already being set

    students_root = args.students_root or DEFAULT_STUDENTS_ROOT
    class_dir = students_root / f"class_{args.year % 100:02d}"
    date_str = today.isoformat()

    try:
        session = login(next_path=f"/modules/work/index.php?course={args.course}")
    except LoginError as exc:
        print(f"login failed: {exc}", file=sys.stderr)
        return 1

    # The mirror DB is the dedup ledger: which submissions we already hold and at
    # what submitted_at. It's a convenience index, not a hard dependency — if it
    # can't be opened we fall back to the on-disk dedup (conn=None) rather than fail.
    conn = None
    try:
        conn = open_db()
    except Exception as exc:
        print(f"warning: mirror db unavailable ({exc}); using on-disk dedup only",
              file=sys.stderr)

    new_folders: list[str] = []
    try:
        try:
            asg = _resolve_assignment(session, args.course, args.year, args.assignment_id)
        except LookupError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        print(
            f"assignment: id={asg.assignment_id}  title={asg.title!r}"
            + (f"  submitted={asg.submitted}" if asg.submitted is not None else "")
        )
        print(f"target: {class_dir}/<slug>/{FINAL_ASSIGNMENT_SUBDIR}/downloaded_{date_str}/\n")

        # Record the assignment we're targeting (both modes) so submissions have
        # a parent row to FK against and the mirror knows this assignment exists.
        if conn is not None:
            try:
                upsert_assignment(conn, assignment_id=asg.assignment_id,
                                  course_code=args.course, title=asg.title,
                                  deadline=asg.deadline_text)
                conn.commit()
            except sqlite3.Error as exc:
                print(f"warning: could not record assignment in db ({exc})", file=sys.stderr)

        if args.combined:
            _download_combined(
                session, args.course, asg, class_dir, date_str,
                extract=not args.no_extract, keep_zip=not args.no_keep_zip, force=args.force,
            )
        else:
            downloaded, skipped, total, new_folders, warnings = _download_per_submission(
                session, args.course, asg, class_dir, date_str, args.force,
                conn=conn, extract=not args.no_extract, keep_zip=not args.no_keep_zip,
            )
            print(f"\ndownloaded {downloaded} file(s), skipped {skipped} "
                  f"({_human_bytes(total)}) → {class_dir}")
            for warning in warnings:
                print(f"  ⚠ {warning}", file=sys.stderr)
    finally:
        if conn is not None:
            conn.close()
        logout(session)

    if new_folders:
        print(f"note: created folders for {len(new_folders)} submitter(s) not in the "
              f"scaffolded roster: {', '.join(new_folders)}")

    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
