"""Delete named files from an eClass course's Έγγραφα (document module).

The uploader (``upload_documents``) never deletes; it reports files that are on
eClass but no longer in the source. This tool removes exactly the files you
name, by their visible path, the way the uploader prints them:

    # Preview: logs in, finds each file, deletes nothing.
    python -m automation_infrastructure.eclass.delete_documents --course ECON875 \\
        lecture_01_ollama_models_prompts_langchain/reading_material/old_name.ipynb

    # Delete.
    python -m automation_infrastructure.eclass.delete_documents --course ECON875 --yes \\
        lecture_01_ollama_models_prompts_langchain/reading_material/old_name.ipynb

Safety, by design:

- **Exact paths only.** No wildcards, no patterns: each argument must name one
  file, character for character.
- **Files only.** A path that names a folder is refused, since deleting a folder
  deletes everything inside it. Remove folders in the browser.
- **All or nothing.** Every path is looked up before anything is deleted; one
  that is missing or a folder stops the run with nothing deleted.
- **``--yes`` to act.** Without it the run is a preview.

Each deletion is confirmed by listing the folder again, and the file's row in
the uploader's ledger (``document_uploads``) is dropped, so a file that comes
back to the source is uploaded again. The login is a single CAS attempt (see
:mod:`session`).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import requests

from .db import REPO_ROOT, delete_document_upload, open_db
from .scrapers.documents import DocumentError, Entry, delete_entry, list_dir
from .session import LoginError, login, logout


@dataclass
class Target:
    """One requested path, resolved on eClass."""

    path: str            # visible path, as given
    folder: str          # internal path of the folder that holds it
    entry: Entry | None  # None when not found
    problem: str = ""    # why it cannot be deleted; '' when it can


def normalise(path: str) -> str:
    """Strip surrounding slashes; reject empty, '.' and '..' components."""
    clean = path.strip().strip("/")
    parts = clean.split("/")
    if not clean or any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"not a plain path: {path!r}")
    return clean


def resolve(session: requests.Session, course: str, path: str) -> Target:
    """Walk the folders of ``path`` one listing at a time and find its last part."""
    *folders, name = path.split("/")
    internal = ""
    for depth, folder in enumerate(folders):
        entry = list_dir(session, course, internal).find(folder, is_dir=True)
        if entry is None:
            missing = "/".join(folders[: depth + 1])
            return Target(path, internal, None, f"folder {missing!r} not found")
        internal = entry.path
    listing = list_dir(session, course, internal)
    entry = listing.find(name, is_dir=False)
    if entry is None:
        if listing.find(name, is_dir=True) is not None:
            return Target(path, internal, None, "is a folder; this tool deletes files only")
        return Target(path, internal, None, "not found")
    if not entry.code:
        return Target(path, internal, entry, "no delete action listed for it")
    return Target(path, internal, entry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete named files from an eClass course's Έγγραφα, by exact visible path."
    )
    parser.add_argument("--course", required=True, help="eClass course code, e.g. ECON875.")
    parser.add_argument("paths", nargs="+", metavar="PATH",
                        help="Visible path of a file, e.g. lecture_01_x/reading_material/a.ipynb")
    parser.add_argument("--yes", action="store_true",
                        help="Delete. Without it, only show what would be deleted.")
    args = parser.parse_args(argv)

    try:
        paths = list(dict.fromkeys(normalise(p) for p in args.paths))
    except ValueError as exc:
        parser.error(str(exc))

    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass  # rely on env vars already being set

    print(f"target: eClass {args.course} → Έγγραφα{'' if args.yes else '  [preview]'}\n")
    try:
        session = login(next_path=f"/modules/document/index.php?course={args.course}")
    except LoginError as exc:
        print(f"login failed: {exc}", file=sys.stderr)
        return 1

    deleted = failed = 0
    try:
        targets = [resolve(session, args.course, p) for p in paths]
        blocked = [t for t in targets if t.problem]
        for t in targets:
            if t.problem:
                print(f"  {'REFUSED':>14}  {t.path}: {t.problem}", file=sys.stderr)
            else:
                label = "will delete" if args.yes else "would delete"
                print(f"  {label:>14}  {t.path}  ({t.entry.size_text})")
        if blocked:
            print(f"\nnothing deleted: {len(blocked)} path(s) refused.", file=sys.stderr)
            return 1
        if not args.yes:
            print(f"\npreview only: pass --yes to delete {len(targets)} file(s).")
            return 0

        conn = None
        try:
            conn = open_db()
        except Exception as exc:
            print(f"warning: mirror db unavailable ({exc}); the ledger is not updated",
                  file=sys.stderr)
        try:
            print()
            for t in targets:
                token = list_dir(session, args.course, t.folder).token
                try:
                    delete_entry(session, args.course, t.entry, token)
                except (DocumentError, requests.RequestException) as exc:
                    print(f"  {'FAILED':>14}  {t.path}: {exc}", file=sys.stderr)
                    failed += 1
                    continue
                if list_dir(session, args.course, t.folder).find(t.entry.name,
                                                                  is_dir=False):
                    print(f"  {'FAILED':>14}  {t.path}: still listed after the delete",
                          file=sys.stderr)
                    failed += 1
                    continue
                if conn is not None:
                    delete_document_upload(conn, args.course, t.path)
                    conn.commit()
                print(f"  {'deleted':>14}  {t.path}")
                deleted += 1
        finally:
            if conn is not None:
                conn.close()
    finally:
        logout(session)

    print(f"\ndeleted {deleted}, failed {failed}.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
