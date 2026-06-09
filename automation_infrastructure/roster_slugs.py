"""Derive `students_work/` folder slugs from the eClass roster.

The course's per-student work folders follow a fixed convention, e.g.
`ΠΑΠΑΔΟΠΟΥΛΟΥ ΜΑΡΙΑ`            -> ``papadopoulou_m``
`ΓΕΩΡΓΙΟΥ ΑΝΝΑ-ΜΑΡΙΑ`-> ``georgiou_a_m``

i.e. ``<transliterated-surname>_<first-initial>[_<second-initial>...]`` in
lowercase ASCII. Surnames are transliterated Greek→Latin; the first name
contributes one initial per part (parts split on whitespace and hyphen).

This module is the single source of truth for that mapping. It reads the
roster from the local eClass mirror (`admin_docs/eclass_data/eclass.db`,
gitignored — see ``automation_infrastructure/eclass/``) and prints one slug
per line. The companion ``scaffold_student_dirs.sh`` consumes that output to
create the folders.

Usage (from the repo root)::

    python -m automation_infrastructure.roster_slugs --year 2026
    python -m automation_infrastructure.roster_slugs --year 2026 --with-email

Transliteration is deterministic but cannot capture every name the way its
owner would spell it (e.g. ``ΜΠ`` word-initially, hyphenated surnames). For
those, drop a tab-separated override file at
``admin_docs/student_lists_grades/year=<YEAR>/slug_overrides.tsv`` with lines
``<email><TAB><desired_slug>`` (``#`` comments allowed); it wins over the
computed slug.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

# eClass reports the student role with this exact Greek label.
ROLE_STUDENT = "Εκπαιδευόμενος"
DEFAULT_COURSE = "ECON537"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "admin_docs" / "eclass_data" / "eclass.db"


def _overrides_path(year: int) -> Path:
    return (
        REPO_ROOT
        / "admin_docs"
        / "student_lists_grades"
        / f"year={year}"
        / "slug_overrides.tsv"
    )


# --- Greek → Latin transliteration ------------------------------------------

# Single-letter map (lowercase, accents already stripped). Digraphs (ου, αυ,
# ευ, ηυ) are handled in the scan below, before these are consulted.
_MONO = {
    "α": "a", "β": "v", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "i",
    "θ": "th", "ι": "i", "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ξ": "x",
    "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "y",
    "φ": "f", "χ": "ch", "ψ": "ps", "ω": "o",
}

# Followers that voice an αυ/ευ/ηυ diphthong to "v" (vowels + voiced
# consonants); anything else (or end of word) makes it "f".
_VOICED_FOLLOWERS = set("αεηιουω" + "βγδζλμνρ")
_DIPHTHONG_BASE = {"αυ": "a", "ευ": "e", "ηυ": "i"}


def _strip_accents(text: str) -> str:
    return "".join(
        ch
        for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )


def transliterate(greek: str) -> str:
    """Greek → lowercase-ASCII, handling the ου / αυ / ευ / ηυ digraphs."""
    s = _strip_accents(greek).lower()
    out: list[str] = []
    i = 0
    while i < len(s):
        pair = s[i : i + 2]
        if pair in _DIPHTHONG_BASE:
            nxt = s[i + 2] if i + 2 < len(s) else ""
            voiced = nxt in _VOICED_FOLLOWERS
            out.append(_DIPHTHONG_BASE[pair] + ("v" if voiced else "f"))
            i += 2
            continue
        if pair == "ου":
            out.append("ou")
            i += 2
            continue
        ch = s[i]
        if ch in _MONO:
            out.append(_MONO[ch])
        elif ch.isascii() and ch.isalpha():
            out.append(ch)  # already-Latin character, keep as-is
        # everything else (spaces, punctuation, stray marks) is dropped
        i += 1
    return "".join(out)


def slugify(full_name: str) -> str:
    """``"ΠΑΠΑΔΟΠΟΥΛΟΥ ΜΑΡΙΑ"`` → ``"papadopoulou_m"``.

    First whitespace-token is the surname; remaining tokens are the given
    name(s). Each given-name part (split further on hyphens) contributes one
    transliterated initial.
    """
    tokens = full_name.strip().split()
    if not tokens:
        return ""
    surname = transliterate(tokens[0])
    initials: list[str] = []
    for token in tokens[1:]:
        for part in re.split(r"[-‐-―]", token):
            latin = transliterate(part)
            if latin:
                initials.append(latin[0])
    return surname + ("_" + "_".join(initials) if initials else "")


# --- Roster access ----------------------------------------------------------


def load_overrides(year: int) -> dict[str, str]:
    """Read ``<email> -> <slug>`` overrides for the year, if the file exists."""
    path = _overrides_path(year)
    overrides: dict[str, str] = {}
    if not path.exists():
        return overrides
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        email, _, slug = line.partition("\t")
        email, slug = email.strip().lower(), slug.strip()
        if email and slug:
            overrides[email] = slug
    return overrides


def roster_slugs(
    year: int, course: str = DEFAULT_COURSE, db_path: Path = DEFAULT_DB
) -> list[tuple[str, str]]:
    """Return ``[(slug, email), ...]`` for the year's students, slug-sorted.

    "The year's students" = course members with the student role whose
    eClass registration date falls within the calendar year. Overrides (by
    email) replace the computed slug. Collisions are disambiguated with a
    numeric suffix and reported to stderr so they can be fixed via overrides.
    """
    if not db_path.exists():
        raise FileNotFoundError(
            f"eClass mirror not found at {db_path}. Populate it first:\n"
            f"  python -m automation_infrastructure.eclass.refresh_db {course}"
        )

    overrides = load_overrides(year)
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            """
            SELECT full_name, email
            FROM users
            WHERE course_code = ?
              AND role = ?
              AND registration_date >= ?
              AND registration_date < ?
            ORDER BY full_name
            """,
            (course, ROLE_STUDENT, f"{year}-01-01", f"{year + 1}-01-01"),
        ).fetchall()
    finally:
        conn.close()

    result: list[tuple[str, str]] = []
    seen: dict[str, int] = {}
    for full_name, email in rows:
        key = (email or "").strip().lower()
        slug = overrides.get(key) or slugify(full_name)
        if slug in seen:
            seen[slug] += 1
            disambiguated = f"{slug}_{seen[slug]}"
            print(
                f"warning: slug collision on '{slug}' -> using "
                f"'{disambiguated}' (add an override to fix)",
                file=sys.stderr,
            )
            slug = disambiguated
        else:
            seen[slug] = 1
        result.append((slug, key))

    result.sort(key=lambda pair: pair[0])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print students_work folder slugs for a year's roster."
    )
    parser.add_argument(
        "--year", type=int, required=True, help="Calendar year, e.g. 2026."
    )
    parser.add_argument("--course", default=DEFAULT_COURSE, help="eClass course code.")
    parser.add_argument(
        "--db", type=Path, default=DEFAULT_DB, help="Path to eclass.db."
    )
    parser.add_argument(
        "--with-email",
        action="store_true",
        help="Emit '<slug>\\t<email>' instead of just the slug.",
    )
    args = parser.parse_args(argv)

    try:
        pairs = roster_slugs(args.year, args.course, args.db)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    if not pairs:
        print(
            f"warning: no {args.course} students found for {args.year}",
            file=sys.stderr,
        )
    for slug, email in pairs:
        print(f"{slug}\t{email}" if args.with_email else slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
