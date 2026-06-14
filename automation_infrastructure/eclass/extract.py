"""Safe, modular archive extraction for the eClass download pipeline.

Student submissions arrive as ``.zip`` files — both the per-submission eClass
download (``?get=<id>``) and the all-in-one combined download (``?download=<id>``).
This module turns a downloaded archive into an extracted folder, safely:

- it **refuses path-traversal members** (a ``../`` or absolute entry cannot
  escape the destination),
- it **skips macOS resource forks** (``__MACOSX/``, ``._*``) and other OS junk,
- it **leaves non-zip archives** (``.rar`` / ``.7z`` / ``.tar`` / ...) untouched
  with a clear warning, because the standard library can't open them, and
- it **never raises on a corrupt zip or a single bad entry** — it collects
  warnings and carries on, so one malformed submission can't abort a batch run.

Like the rest of the ``eclass`` package, this module is import-safe: functions
take paths, write files, and return a typed :class:`ExtractResult`; they never
print. The CLI (:mod:`download_submissions`) owns all user-facing output.
"""

from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

__all__ = ["ExtractKind", "ExtractResult", "safe_extract_zip", "extract_archive"]

ZIP_SUFFIX = ".zip"
# Archives the standard library cannot open: we leave them in place and warn.
UNSUPPORTED_ARCHIVE_SUFFIXES = frozenset(
    {".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz"}
)

ExtractKind = Literal["zip", "unsupported", "not-archive"]


def _is_os_junk(name: str) -> bool:
    """True for macOS resource forks / OS metadata that should not be extracted."""
    parts = Path(name).parts
    if any(seg == "__MACOSX" for seg in parts):
        return True
    base = parts[-1] if parts else name
    return base.startswith("._") or base in {".DS_Store", "Thumbs.db"}


@dataclass
class ExtractResult:
    """Outcome of attempting to extract one archive.

    ``kind`` is ``"zip"`` when a zip was processed (see :attr:`extracted` for
    whether it actually yielded files), ``"unsupported"`` for a ``.rar`` / ``.7z``
    / etc. left in place, and ``"not-archive"`` for a plain file (e.g. a single
    ``.ipynb`` a student uploaded without zipping).
    """

    archive: Path
    kind: ExtractKind
    extracted_to: Path | None = None
    member_count: int = 0
    skipped_members: list[str] = field(default_factory=list)
    removed_archive: bool = False
    warnings: list[str] = field(default_factory=list)

    @property
    def extracted(self) -> bool:
        """True iff a zip was opened and at least its tree was written out."""
        return self.kind == "zip" and self.extracted_to is not None


def safe_extract_zip(
    zip_path: Path,
    dest: Path,
    *,
    drop_os_junk: bool = True,
) -> ExtractResult:
    """Extract ``zip_path`` into ``dest``, refusing path-traversal members.

    Every member's resolved target must stay within ``dest``; an entry that tries
    to escape (``../`` or an absolute path) is skipped and recorded in
    :attr:`ExtractResult.skipped_members`. Directories are created on demand and
    macOS junk is dropped when ``drop_os_junk`` is set. ``dest`` is created if it
    does not exist.

    Raises :class:`zipfile.BadZipFile` if ``zip_path`` is not a readable zip —
    callers that drive a batch should prefer :func:`extract_archive`, which
    captures that as a warning instead.
    """
    dest.mkdir(parents=True, exist_ok=True)
    dest_root = dest.resolve()
    result = ExtractResult(archive=zip_path, kind="zip", extracted_to=dest)

    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            name = member.filename
            if drop_os_junk and _is_os_junk(name):
                continue
            target = (dest / name).resolve()
            try:
                target.relative_to(dest_root)  # must stay inside dest
            except ValueError:
                result.skipped_members.append(name)
                result.warnings.append(f"refused path-traversal entry: {name!r}")
                continue
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
            result.member_count += 1

    return result


def extract_archive(
    archive: Path,
    dest: Path | None = None,
    *,
    keep_archive: bool = True,
    drop_os_junk: bool = True,
) -> ExtractResult:
    """Extract a downloaded ``archive`` into ``dest`` (default: its own folder).

    Dispatches on the suffix so the caller can pass anything a student uploaded:

    - ``.zip``  → extract into ``dest`` (defaults to ``archive.parent``); when
      ``keep_archive`` is false the original ``.zip`` is removed after a
      successful extract.
    - ``.rar`` / ``.7z`` / ``.tar`` / ...  → left in place; ``kind="unsupported"``
      with a warning (the stdlib can't open these — extract them manually).
    - anything else (a plain ``.ipynb`` / ``.pdf``)  → left in place;
      ``kind="not-archive"`` (nothing to do).

    Never raises on a corrupt zip: a :class:`zipfile.BadZipFile` is captured as a
    warning and returned, so a single bad submission can't abort a batch.
    """
    suffix = archive.suffix.lower()

    if suffix != ZIP_SUFFIX:
        kind: ExtractKind = (
            "unsupported" if suffix in UNSUPPORTED_ARCHIVE_SUFFIXES else "not-archive"
        )
        warnings = (
            [f"{archive.name}: {suffix} archives are not auto-extractable here; "
             "extract it manually and re-run."]
            if kind == "unsupported"
            else []
        )
        return ExtractResult(archive=archive, kind=kind, warnings=warnings)

    dest = dest if dest is not None else archive.parent
    try:
        result = safe_extract_zip(archive, dest, drop_os_junk=drop_os_junk)
    except zipfile.BadZipFile as exc:
        return ExtractResult(
            archive=archive,
            kind="zip",
            extracted_to=None,
            warnings=[f"{archive.name}: not a valid zip ({exc})"],
        )

    if not keep_archive and result.extracted:
        archive.unlink()
        result.removed_archive = True

    return result
