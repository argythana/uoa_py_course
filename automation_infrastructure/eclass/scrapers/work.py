"""Read the eClass 'work' (Εργασίες) module: list assignments, download submissions.

The work module lists a course's assignments at
``/modules/work/index.php?course=<CODE>``. Each assignment has an internal
numeric id and, for a teacher account, two download affordances:

- **all submissions as one ZIP**: ``?course=<CODE>&download=<assignment_id>``
  (Content-Type ``application/zip``, filename ``<CODE>_work_<id>.zip``). The
  archive holds one file per student submission — usually the ``.zip`` the
  student uploaded.
- **one submission**: ``?course=<CODE>&get=<submission_id>``.

This module is import-safe: the functions return data / write files and never
print. Run ``download_submissions`` (the sibling CLI) to drive it end-to-end.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from ..session import BASE
from ...roster_slugs import transliterate

# Local ZIP signature — the first bytes of every well-formed zip.
ZIP_MAGIC = b"PK\x03\x04"

# GET params that mark a work-module link as an *action* on an assignment
# rather than a link to the assignment's own page.
_ACTION_PARAMS = (
    "choice", "get", "download", "as_id", "disp_results", "disp_non_submitted",
)


@dataclass
class Assignment:
    """One row of the work-module assignment list."""

    assignment_id: int
    title: str
    submitted: int | None      # count of submissions, as shown in the list
    deadline_text: str | None  # human Greek deadline string, verbatim


@dataclass
class Submission:
    """One student's submission to an assignment (teacher view of the page)."""

    submission_id: int          # the ?get=<id> download id
    student_name: str | None    # eClass display name (Greek); None if unparsed
    profile_id: int | None      # ?id=<id> on display_profile.php
    filename_hint: str | None   # filename as shown in the table — MAY BE TRUNCATED
    submitted_at: str | None = None  # raw submission-time text from the file cell
    # (e.g. "Δευτέρα 25 Μαΐου 2026 - 11:55 π.μ."); opaque — used only to detect a
    # resubmission (a changed timestamp), not parsed into a datetime.


def slugify_title(title: str) -> str:
    """Assignment title → filesystem-safe slug, keeping digits (years).

    Latin tokens are lowercased and stripped to ``[a-z0-9]``; Greek tokens are
    transliterated (see :func:`automation_infrastructure.roster_slugs.transliterate`).
    e.g. ``"Final Assignment Python 2026"`` → ``"final_assignment_python_2026"``;
    ``"Τελική εργασία python 2025"`` → ``"teliki_ergasia_python_2025"``.
    """
    parts: list[str] = []
    for token in title.split():
        if token.isascii():
            cleaned = re.sub(r"[^a-z0-9]+", "", token.lower())
        else:
            cleaned = transliterate(token)  # Greek letters → Latin; non-letters dropped
        if cleaned:
            parts.append(cleaned)
    return re.sub(r"_+", "_", "_".join(parts)).strip("_")


def list_assignments(session: requests.Session, course_code: str) -> list[Assignment]:
    """Return every assignment defined under the course's work module."""
    url = f"{BASE}/modules/work/index.php?course={course_code}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    found: dict[int, Assignment] = {}
    for a in soup.find_all("a", href=True):
        p = urlparse(a["href"])
        if not p.path.endswith("/modules/work/index.php"):
            continue
        q = parse_qs(p.query)
        if "id" not in q or "course" not in q:
            continue
        if any(k in q for k in _ACTION_PARAMS):
            continue
        aid_str = q["id"][0]
        if not aid_str.isdigit():
            continue
        aid = int(aid_str)
        title = " ".join(a.get_text().split())
        if not title or aid in found:
            continue

        # The enclosing <tr> carries the count + deadline columns. Layout
        # (May 2026): [title+meta, submitted, total, deadline, actions].
        submitted: int | None = None
        deadline: str | None = None
        tr = a.find_parent("tr")
        if tr is not None:
            cells = [" ".join(td.get_text().split()) for td in tr.find_all("td")]
            if len(cells) >= 2 and cells[1].isdigit():
                submitted = int(cells[1])
            if len(cells) >= 4 and cells[3]:
                deadline = cells[3]
        found[aid] = Assignment(aid, title, submitted, deadline)
    return list(found.values())


def find_assignment_for_year(
    session: requests.Session, course_code: str, year: int
) -> Assignment:
    """Pick the assignment for ``year`` — the one whose title contains the year.

    If several titles contain the year, prefer those that look like a final
    assignment ("final" / "τελικ"). Raises ``LookupError`` on zero or an
    unresolved tie (caller should fall back to an explicit assignment id).
    """
    assignments = list_assignments(session, course_code)
    needle = str(year)
    matches = [a for a in assignments if needle in a.title]
    if not matches:
        raise LookupError(
            f"no {course_code} assignment title contains {year}; "
            f"pass an explicit --assignment-id"
        )
    if len(matches) > 1:
        preferred = [a for a in matches if re.search(r"final|τελικ", a.title, re.I)]
        matches = preferred or matches
    if len(matches) > 1:
        listing = ", ".join(f"{a.assignment_id}={a.title!r}" for a in matches)
        raise LookupError(
            f"ambiguous {year} assignment in {course_code}: {listing}; "
            f"pass an explicit --assignment-id"
        )
    return matches[0]


def download_all_submissions(
    session: requests.Session,
    course_code: str,
    assignment_id: int,
    dest_zip: Path,
    *,
    chunk_size: int = 1 << 20,
    progress: Callable[[int, int], None] | None = None,
) -> Path:
    """Stream the all-submissions ZIP for one assignment to ``dest_zip``.

    Writes to a ``.part`` sidecar and renames on success, so an interrupted
    download never leaves a truncated file at the final path. ``progress`` (if
    given) is called as ``progress(bytes_so_far, total_bytes)`` per chunk;
    ``total_bytes`` is 0 when the server omits Content-Length.

    Raises ``RuntimeError`` if the response isn't a zip — which is how eClass
    signals "no submissions" (it serves the HTML page instead of an archive).
    """
    url = f"{BASE}/modules/work/index.php?course={course_code}&download={assignment_id}"
    with session.get(url, stream=True, timeout=(30, 120)) as r:
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "")
        if "zip" not in ctype.lower():
            raise RuntimeError(
                f"expected a zip from download={assignment_id}, got "
                f"Content-Type={ctype!r} — the assignment id may be wrong or it "
                f"has no submissions yet."
            )
        total = int(r.headers.get("Content-Length") or 0)
        dest_zip.parent.mkdir(parents=True, exist_ok=True)
        part = dest_zip.with_name(dest_zip.name + ".part")

        got = 0
        first = True
        with open(part, "wb") as fh:
            for block in r.iter_content(chunk_size):
                if not block:
                    continue
                if first:
                    if not block.startswith(ZIP_MAGIC):
                        fh.close()
                        part.unlink(missing_ok=True)
                        raise RuntimeError(
                            "download did not start with ZIP magic (PK\\x03\\x04)"
                        )
                    first = False
                fh.write(block)
                got += len(block)
                if progress is not None:
                    progress(got, total)

    part.replace(dest_zip)
    return dest_zip


def list_submissions(
    session: requests.Session, course_code: str, assignment_id: int
) -> list[Submission]:
    """Parse the assignment page (teacher view) into one row per submission.

    Each row carries the ``?get=<id>`` download id, the submitting student, and
    the filename as shown — which the page often **truncates**, so use the
    download's Content-Disposition header for the real name, not ``filename_hint``.
    """
    url = f"{BASE}/modules/work/index.php?course={course_code}&id={assignment_id}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    found: dict[int, Submission] = {}
    for a in soup.find_all("a", href=True):
        q = parse_qs(urlparse(a["href"]).query)
        sid_list = q.get("get")
        if not sid_list or not sid_list[0].isdigit():
            continue
        sid = int(sid_list[0])
        if sid in found:
            continue

        hint = (a.get("title") or " ".join(a.get_text().split())) or None
        student_name: str | None = None
        profile_id: int | None = None
        tr = a.find_parent("tr")
        if tr is not None:
            prof = tr.find("a", href=lambda h: h and "display_profile.php" in h)
            if prof is not None:
                student_name = " ".join(prof.get_text().split()) or None
                pq = parse_qs(urlparse(prof["href"]).query)
                pid = pq.get("id", [None])[0]
                profile_id = int(pid) if pid and pid.isdigit() else None

        # The submission time sits in a <div> right after the file link, in the
        # same cell (e.g. "Δευτέρα 25 Μαΐου 2026 - 11:55 π.μ."). It's the only
        # signal that a student has *resubmitted* since a previous download.
        submitted_at: str | None = None
        file_td = a.find_parent("td")
        if file_td is not None:
            ts_div = file_td.find("div")
            if ts_div is not None:
                submitted_at = " ".join(ts_div.get_text().split()) or None

        found[sid] = Submission(sid, student_name, profile_id, hint, submitted_at)
    return list(found.values())


def _filename_from_disposition(content_disposition: str) -> str | None:
    """Pull the filename out of a Content-Disposition header.

    Prefers RFC 5987 ``filename*=UTF-8''...`` (eClass uses this for Greek
    names), falling back to a plain ``filename="..."``.
    """
    if not content_disposition:
        return None
    m = re.search(r"filename\*\s*=\s*[^']*''([^;]+)", content_disposition, re.I)
    if m:
        return unquote(m.group(1)).strip().strip('"')
    m = re.search(r'filename\s*=\s*"?([^";]+)"?', content_disposition, re.I)
    if m:
        return m.group(1).strip()
    return None


def sanitize_filename(name: str, fallback: str = "submission") -> str:
    """Reduce a server-supplied filename to a safe basename."""
    name = name.replace("\\", "/").split("/")[-1]
    name = re.sub(r"\s+", " ", name).strip().strip(".")
    return name or fallback


def download_submission(
    session: requests.Session,
    course_code: str,
    submission_id: int,
    dest_dir: Path,
    *,
    filename: str | None = None,
    chunk_size: int = 1 << 20,
    progress: Callable[[int, int], None] | None = None,
) -> Path:
    """Stream one submission (``?get=<id>``) into ``dest_dir``.

    The saved filename comes from the response's Content-Disposition header
    (the page's own text is often truncated) unless ``filename`` is given.
    Writes to a ``.part`` sidecar and renames on success. ``progress`` is called
    as ``progress(bytes_so_far, total_bytes)`` per chunk.
    """
    url = f"{BASE}/modules/work/index.php?course={course_code}&get={submission_id}"
    with session.get(url, stream=True, timeout=(30, 120)) as r:
        r.raise_for_status()
        if "text/html" in r.headers.get("Content-Type", "").lower():
            raise RuntimeError(
                f"get={submission_id} returned HTML, not a file "
                f"(permissions, or the submission was withdrawn)"
            )
        name = filename or _filename_from_disposition(
            r.headers.get("Content-Disposition", "")
        ) or f"submission_{submission_id}"
        name = sanitize_filename(name)
        total = int(r.headers.get("Content-Length") or 0)

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / name
        part = dest.with_name(dest.name + ".part")
        got = 0
        with open(part, "wb") as fh:
            for block in r.iter_content(chunk_size):
                if not block:
                    continue
                fh.write(block)
                got += len(block)
                if progress is not None:
                    progress(got, total)

    part.replace(dest)
    return dest
