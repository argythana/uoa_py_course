"""Publish a course repository's material to an eClass course's Έγγραφα (document module).

Mirrors the files of a git repository **as committed at HEAD** — the same tree
GitHub shows — into the course's document module, folder for folder, and
gathers generated PDF handouts (gitignored, so absent from GitHub) into one
extra top-level folder:

    Έγγραφα/                                   (eClass course ECON875)
      lecture_01_.../infra_tools/01a_git_uv.md
      lecture_01_.../reading_material/lec_01a_....ipynb
      ...
      README.md
      Instructions/01a_git_uv.pdf              (built by tools/build_guide_pdfs.py)

Uploading HEAD rather than the working tree keeps eClass identical to GitHub:
uncommitted edits are listed as a warning and left out, and so is a commit that
has not been pushed yet (warned, but uploaded).

Re-running is cheap and safe. Each uploaded file is recorded in the mirror DB
(``document_uploads`` in ``admin_docs/eclass_data/eclass.db``) with its sha256 and
eClass-internal path; a file whose content is unchanged and still listed on
eClass is skipped, a changed one replaces the eClass copy in place, and a new one
is uploaded. Nothing is ever deleted on eClass: files that are on eClass but no
longer in the source are reported as orphans; remove them by hand or with
``delete_documents``.

    # Preview: logs in, compares with eClass, changes nothing.
    python -m automation_infrastructure.eclass.upload_documents --profile teach-llm-system --dry-run

    # Upload new and changed files.
    python -m automation_infrastructure.eclass.upload_documents --profile teach-llm-system

    # Any repo / course, without a profile.
    python -m automation_infrastructure.eclass.upload_documents --course ECONxxx \\
        --repo ../some-repo --include 'lecture_*' --include README.md

PDFs older than the Markdown guide next to them abort the run (rebuild them
first, or pass ``--allow-stale-pdfs``). The login is a single CAS attempt
(see :mod:`session`); uploads are visible to students as soon as they land.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import shutil
import sqlite3
import subprocess  # nosec B404 - runs git with a fixed argument list
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import requests

from .db import REPO_ROOT, get_document_upload, open_db, upsert_document_upload
from .scrapers.documents import DocumentError, Listing, create_dir, list_dir, upload_file
from .session import LoginError, login, logout


@dataclass(frozen=True)
class Profile:
    """A named upload target: which repo files go to which course."""

    course: str
    repo: Path
    include: tuple[str, ...]        # top-level names / globs taken from git HEAD
    pdf_glob: str | None = None     # PDFs (working tree) gathered into pdf_folder
    pdf_folder: str | None = None


PROFILES = {
    # The LLM-systems course (github.com/argythana/teach-llm-system).
    "teach-llm-system": Profile(
        course="ECON875",
        repo=REPO_ROOT.parent / "teach-llm-system",
        include=("lecture_*", "README.md", "troubleshooting.md"),
        pdf_glob="lecture_*/infra_tools/*.pdf",
        pdf_folder="Instructions",
    ),
}


@dataclass
class SourceFile:
    """One file to publish: where it goes on eClass and its bytes."""

    remote_path: PurePosixPath     # folder names + filename as students see them
    content: bytes
    source: str                    # provenance for the ledger, e.g. "teach-llm-system@59641e8"
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        self.sha256 = hashlib.sha256(self.content).hexdigest()


# -- Collecting the source files ---------------------------------------------

GIT = shutil.which("git") or "git"


def _git(repo: Path, *args: str) -> bytes:
    # No shell; the arguments are this module's own, plus paths from git itself.
    return subprocess.run([GIT, "-C", str(repo), *args], check=True,  # nosec B603
                          capture_output=True).stdout


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    top = path.split("/", 1)[0]
    return any(fnmatch.fnmatchcase(top, p) or fnmatch.fnmatchcase(path, p) for p in patterns)


def collect_git_files(repo: Path, include: tuple[str, ...]) -> list[SourceFile]:
    """Every regular file committed at HEAD whose top-level name matches ``include``."""
    short_sha = _git(repo, "rev-parse", "--short", "HEAD").decode().strip()
    source = f"{repo.name}@{short_sha}"
    files: list[SourceFile] = []
    for record in _git(repo, "ls-tree", "-r", "-z", "HEAD").split(b"\0"):
        if not record:
            continue
        meta, path = record.decode("utf-8").split("\t", 1)
        mode, kind, blob = meta.split()
        if kind != "blob" or mode == "120000" or not _matches(path, include):
            continue  # submodules, symlinks, files outside the selection
        files.append(SourceFile(PurePosixPath(path), _git(repo, "cat-file", "blob", blob), source))
    return files


def collect_pdfs(repo: Path, pdf_glob: str, folder: str) -> tuple[list[SourceFile], list[str]]:
    """The generated PDFs, flattened into ``folder``; plus the names of stale ones.

    A PDF is stale when the Markdown file it was built from (same name, same
    folder) was modified after it.
    """
    files: list[SourceFile] = []
    stale: list[str] = []
    seen: dict[str, Path] = {}
    for pdf in sorted(repo.glob(pdf_glob)):
        if pdf.name in seen:
            raise SystemExit(f"error: two PDFs would both land in {folder}/{pdf.name}: "
                             f"{seen[pdf.name]} and {pdf}")
        seen[pdf.name] = pdf
        markdown = pdf.with_suffix(".md")
        if markdown.exists() and markdown.stat().st_mtime > pdf.stat().st_mtime:
            stale.append(str(pdf.relative_to(repo)))
        files.append(SourceFile(PurePosixPath(folder, pdf.name), pdf.read_bytes(),
                                f"{repo.name} working tree"))
    return files, stale


def git_warnings(repo: Path, include: tuple[str, ...]) -> list[str]:
    """Ways in which HEAD differs from what the instructor may expect to publish."""
    warnings: list[str] = []
    status = _git(repo, "status", "--porcelain", "--", *include).decode().splitlines()
    if status:
        warnings.append(f"{len(status)} uncommitted change(s) are NOT uploaded (HEAD is):\n"
                        + "\n".join(f"      {line}" for line in status))
    try:
        ahead = int(_git(repo, "rev-list", "--count", "@{u}..HEAD").decode().strip())
    except subprocess.CalledProcessError:
        warnings.append("no upstream branch: cannot tell whether HEAD is on GitHub")
    else:
        if ahead:
            warnings.append(f"HEAD is {ahead} commit(s) ahead of its upstream: "
                            "eClass will show material GitHub does not have yet (git push)")
    return warnings


# -- The eClass side ---------------------------------------------------------

class RemoteTree:
    """Lazily resolved view of a course's document folders, by visible path.

    Folder listings are cached; any write invalidates the listing it touched.
    In dry-run mode missing folders are not created and resolve to None.
    """

    def __init__(self, session: requests.Session, course: str, *, dry_run: bool) -> None:
        self.session = session
        self.course = course
        self.dry_run = dry_run
        self._listings: dict[str, Listing] = {}
        self.dirs: dict[str, str | None] = {"": ""}   # visible path -> internal path
        self.created: list[str] = []

    def listing(self, internal_path: str) -> Listing:
        if internal_path not in self._listings:
            self._listings[internal_path] = list_dir(self.session, self.course, internal_path)
        return self._listings[internal_path]

    def forget(self, internal_path: str) -> None:
        self._listings.pop(internal_path, None)

    @property
    def token(self) -> str:
        return self.listing("").token

    def resolve_dir(self, visible: str) -> str | None:
        """Internal path of the folder at ``visible``, creating it if missing."""
        if visible in self.dirs:
            return self.dirs[visible]
        parent_visible, _, name = visible.rpartition("/")
        parent = self.resolve_dir(parent_visible)
        existing = None
        if parent is not None:
            existing = self.listing(parent).find(name, is_dir=True)
        if existing is not None:
            internal: str | None = existing.path
        else:
            internal = None
            if not self.dry_run:
                internal = create_dir(self.session, self.course, parent, name, self.token).path
                self.forget(parent)
            self.created.append(visible)
        self.dirs[visible] = internal
        return internal


def _human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def publish(remote: RemoteTree, files: list[SourceFile], conn: sqlite3.Connection | None,
            *, force: bool) -> dict[str, int]:
    """Upload new/changed files; print one line per file; return counts by outcome."""
    counts = {"uploaded": 0, "replaced": 0, "unchanged": 0, "failed": 0}
    course = remote.course
    for f in files:
        visible_dir = str(f.remote_path.parent) if str(f.remote_path.parent) != "." else ""
        name = f.remote_path.name
        dir_internal = remote.resolve_dir(visible_dir)
        existing = (remote.listing(dir_internal).find(name, is_dir=False)
                    if dir_internal is not None else None)
        row = get_document_upload(conn, course, str(f.remote_path)) if conn is not None else None
        if (existing is not None and not force and row is not None
                and row["file_sha256"] == f.sha256 and row["eclass_path"] == existing.path):
            counts["unchanged"] += 1
            continue
        outcome = "replaced" if existing is not None else "uploaded"
        verb = {"uploaded": "upload", "replaced": "replace"}[outcome]
        label = f"{'would ' + verb if remote.dry_run else outcome:>14}"
        if remote.dry_run:
            print(f"  {label}  {f.remote_path}  ({_human_bytes(len(f.content))})")
            counts[outcome] += 1
            continue
        try:
            upload_file(remote.session, course, dir_internal, name, f.content, remote.token,
                        replace=existing is not None)
        except (DocumentError, requests.RequestException) as exc:
            print(f"  {'FAILED':>14}  {f.remote_path}: {exc}", file=sys.stderr)
            counts["failed"] += 1
            continue
        remote.forget(dir_internal)
        landed = remote.listing(dir_internal).find(name, is_dir=False)
        if landed is None:
            print(f"  {'FAILED':>14}  {f.remote_path}: accepted but not listed afterwards",
                  file=sys.stderr)
            counts["failed"] += 1
            continue
        if conn is not None:
            upsert_document_upload(conn, course_code=course, remote_path=str(f.remote_path),
                                   eclass_path=landed.path, file_sha256=f.sha256,
                                   size_bytes=len(f.content), source=f.source)
            conn.commit()
        print(f"  {label}  {f.remote_path}  ({_human_bytes(len(f.content))})")
        counts[outcome] += 1
    return counts


def orphans(remote: RemoteTree, files: list[SourceFile]) -> list[str]:
    """Entries inside the folders we manage that the source no longer has.

    The course root is not checked: it also holds material that never came from
    the repository.
    """
    wanted: set[str] = set()
    for f in files:
        wanted.add(str(f.remote_path))
        wanted.update(str(p) for p in f.remote_path.parents if str(p) != ".")
    found: list[str] = []
    for visible, internal in sorted(remote.dirs.items()):
        if not visible or internal is None:
            continue
        for entry in remote.listing(internal).entries:
            path = f"{visible}/{entry.name}"
            if path not in wanted:
                found.append(path + ("/" if entry.is_dir else ""))
    return found


# -- CLI ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish a repository's committed material to an eClass course's Έγγραφα."
    )
    parser.add_argument("--profile", choices=sorted(PROFILES),
                        help="Named target; the options below override its fields.")
    parser.add_argument("--course", help="eClass course code, e.g. ECON875.")
    parser.add_argument("--repo", type=Path, help="Git repository whose HEAD is published.")
    parser.add_argument("--include", action="append",
                        help="Top-level name or glob to publish (repeatable).")
    parser.add_argument("--pdf-glob", help="Glob (relative to the repo) of PDFs to gather.")
    parser.add_argument("--pdf-folder", help="eClass folder the PDFs are gathered into.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log in and compare with eClass, but upload and create nothing.")
    parser.add_argument("--force", action="store_true",
                        help="Re-upload every file even if the ledger says it is unchanged.")
    parser.add_argument("--allow-stale-pdfs", action="store_true",
                        help="Upload PDFs even if their Markdown source is newer.")
    args = parser.parse_args(argv)

    base = PROFILES[args.profile] if args.profile else None
    course = args.course or (base.course if base else None)
    repo = args.repo or (base.repo if base else None)
    include = tuple(args.include) if args.include else (base.include if base else ())
    pdf_glob = args.pdf_glob or (base.pdf_glob if base else None)
    pdf_folder = args.pdf_folder or (base.pdf_folder if base else None)
    if not course or not repo or not include:
        parser.error("give --profile, or --course, --repo and at least one --include")
    if bool(pdf_glob) != bool(pdf_folder):
        parser.error("--pdf-glob and --pdf-folder go together")
    repo = repo.resolve()

    files = collect_git_files(repo, include)
    if pdf_glob:
        pdfs, stale = collect_pdfs(repo, pdf_glob, pdf_folder)
        if stale and not args.allow_stale_pdfs:
            print("error: these PDFs are older than their Markdown guide — rebuild them "
                  "(e.g. uv run python tools/build_guide_pdfs.py) or pass --allow-stale-pdfs:\n"
                  + "\n".join(f"  {p}" for p in stale), file=sys.stderr)
            return 1
        files += pdfs
    if not files:
        print(f"error: nothing in {repo} matches {include}", file=sys.stderr)
        return 1

    print(f"source: {repo}  ({len(files)} files, "
          f"{_human_bytes(sum(len(f.content) for f in files))})")
    print(f"target: eClass {course} → Έγγραφα{'  [dry run]' if args.dry_run else ''}")
    for warning in git_warnings(repo, include):
        print(f"  ⚠ {warning}", file=sys.stderr)
    print()

    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass  # rely on env vars already being set

    try:
        session = login(next_path=f"/modules/document/index.php?course={course}")
    except LoginError as exc:
        print(f"login failed: {exc}", file=sys.stderr)
        return 1

    # The ledger only saves work; without it every existing file is replaced.
    conn = None
    try:
        conn = open_db()
    except Exception as exc:
        print(f"warning: mirror db unavailable ({exc}); every existing file will be replaced",
              file=sys.stderr)

    try:
        remote = RemoteTree(session, course, dry_run=args.dry_run)
        counts = publish(remote, files, conn, force=args.force)
        left_over = orphans(remote, files)
    finally:
        if conn is not None:
            conn.close()
        logout(session)

    verb = "would create" if args.dry_run else "created"
    if remote.created:
        print(f"\n{verb} {len(remote.created)} folder(s): {', '.join(remote.created)}")
    if left_over:
        print("\non eClass but not in the source (left in place; remove with delete_documents if unwanted):\n"
              + "\n".join(f"  {p}" for p in left_over))
    prefix = "would have " if args.dry_run else ""
    print(f"\n{prefix}uploaded {counts['uploaded']}, {prefix}replaced {counts['replaced']}, "
          f"unchanged {counts['unchanged']}, failed {counts['failed']}.")
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
