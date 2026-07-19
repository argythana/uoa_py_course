#!/usr/bin/env python3
"""
inventory_submission.py — locate a (possibly partial) final-assignment draft and
inventory its notebooks and data files.

Usage:
    inventory_submission.py <input_path> <workdir>

<input_path> is one of:
    - a .zip file (typical email submission)
    - a directory (a student folder, or an already-extracted submission)
    - a single .ipynb file (a one-notebook draft)

The script materializes the submission into <workdir>/extracted (zip/dir) or uses
loose files in place, then:

  - finds every .ipynb and classifies each as regression / clustering /
    classification / unknown (by filename suffix first, then by code keywords),
  - lists data files (csv/xlsx/...),
  - derives the student prefix (lastname_t) from the notebook filenames, falling
    back to the folder name,
  - checks the snake_case `lastname_t_<category>.ipynb` naming convention and
    whether a data/ subfolder exists.

Output is JSON on stdout. Fully deterministic, no LLM, no network.

Exit codes: 0 ok · 2 needs-disambiguation (caller should ask the user) · 1 error.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

DATA_EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".json", ".jsonl"}
ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz"}

CATEGORY_FILENAME_HINTS = {
    "regression": ["regression", "regress", "linear_reg"],
    "clustering": ["clustering", "cluster", "kmeans", "k_means", "k-means"],
    "classification": ["classification", "classif", "classifier"],
}

# Code-keyword signals used only when the filename doesn't reveal the category.
CATEGORY_CODE_HINTS = {
    "clustering": ["kmeans", "k-means", "agglomerative", "dbscan", "silhouette",
                   "inertia", "n_clusters"],
    "classification": ["logisticregression", "kneighborsclassifier", "gaussiannb",
                       "multinomialnb", "bernoullinb", "confusion_matrix",
                       "classification_report", "accuracy_score", "svc("],
    "regression": ["linearregression", "ridge(", "lasso(", "elasticnet",
                   "mean_squared_error", "r2_score", "mean_absolute_error"],
}

PREFIX_RE = re.compile(r"^([a-z][a-z'-]*_[a-z])(?:[_-]|$)")
GOOD_NAME_RE = re.compile(
    r"^[a-z][a-z'-]*_[a-z]_(regression|clustering|classification)\.ipynb$"
)


def safe_extract_zip(zip_path: Path, dest: Path, warnings: list[str]) -> None:
    skipped_env = 0
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            # Never extract bundled venv / dependency / tooling trees — a student
            # sometimes zips their whole venv (hundreds of MB, never submission
            # content). Scanning already ignores these; skip them at extract time.
            if any(_is_env_segment(seg) for seg in Path(member.filename).parts):
                if not member.is_dir():
                    skipped_env += 1
                continue
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(dest.resolve())):
                warnings.append(f"Refused path-traversal entry: {member.filename!r}")
                continue
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    if skipped_env:
        warnings.append(
            f"Skipped {skipped_env} bundled venv/dependency file(s) at extract time."
        )


def materialize(input_path: Path, workdir: Path, warnings: list[str]) -> Path:
    """Return the root directory to scan for the submission."""
    if input_path.is_file() and input_path.suffix.lower() == ".zip":
        dest = workdir / "extracted"
        dest.mkdir(parents=True, exist_ok=True)
        safe_extract_zip(input_path, dest, warnings)
        return dest
    if input_path.is_file() and input_path.suffix.lower() in ARCHIVE_EXTS:
        raise RuntimeError(
            f"Archive type {input_path.suffix} is not auto-extractable here. "
            "Please extract it manually and re-run on the folder."
        )
    if input_path.is_file():
        # A single loose file (e.g. one .ipynb) — scan its parent but we only
        # report this one file as a notebook below by filtering on the input.
        return input_path.parent
    if input_path.is_dir():
        return input_path
    raise FileNotFoundError(f"Input path not found: {input_path}")


def read_notebook_code(nb_path: Path) -> str:
    """Concatenate all code-cell source from an ipynb. Robust to malformed cells."""
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return ""
    chunks: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = cell.get("source", "")
            chunks.append("".join(src) if isinstance(src, list) else str(src))
    return "\n".join(chunks).lower()


def classify_notebook(nb_path: Path) -> tuple[str, str]:
    """Return (category, classified_by)."""
    name = nb_path.name.lower()
    for category, hints in CATEGORY_FILENAME_HINTS.items():
        if any(h in name for h in hints):
            return category, "filename"
    code = read_notebook_code(nb_path)
    scores = {
        cat: sum(code.count(h) for h in hints)
        for cat, hints in CATEGORY_CODE_HINTS.items()
    }
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best, "content"
    return "unknown", "unknown"


# Directory names that mark dependency/IDE/VCS trees a student may have zipped by
# accident (most often a bundled virtualenv). Anything under these is NOT part of
# the submission — scanning it pollutes the data-file list with package fixtures.
ENV_DIR_NAMES = {
    "site-packages", "node_modules", "__pycache__", ".ipynb_checkpoints",
    "__MACOSX", ".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache", ".tox",
    ".eggs", ".idea", ".vscode",
}


def _is_env_segment(seg: str) -> bool:
    """True for a path segment that names a venv / dependency / tooling dir."""
    s = seg.lower()
    if s in ENV_DIR_NAMES or s in {"venv", ".venv", "env", ".env"}:
        return True
    return s.endswith("venv") or s.endswith(".dist-info") or s.endswith(".egg-info")


def is_hidden_or_junk(p: Path) -> bool:
    parts = p.parts
    if any(_is_env_segment(seg) for seg in parts):
        return True
    return p.name.startswith("._") or p.name in {".DS_Store", "Thumbs.db"}


def derive_prefix(notebooks: list[Path], scan_root: Path,
                  input_path: Path) -> tuple[str | None, str]:
    """Return (prefix, source). Prefer a consistent prefix across notebook names."""
    found: list[str] = []
    for nb in notebooks:
        m = PREFIX_RE.match(nb.name.lower())
        if m:
            found.append(m.group(1))
    if found and len(set(found)) == 1:
        return found[0], "notebook-filenames"
    if found:
        # Mixed prefixes — take the most common, flag via source.
        most = max(set(found), key=found.count)
        return most, "notebook-filenames (mixed — verify)"
    # Fall back to a folder name that looks like a student prefix.
    for cand in (scan_root.name, input_path.stem):
        m = PREFIX_RE.match(cand.lower())
        if m:
            return m.group(1), "folder-name"
    return None, "undetermined"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("workdir", type=Path)
    args = ap.parse_args(argv)

    warnings: list[str] = []
    args.workdir.mkdir(parents=True, exist_ok=True)

    try:
        scan_root = materialize(args.input, args.workdir, warnings)
    except (FileNotFoundError, RuntimeError, zipfile.BadZipFile) as e:
        print(json.dumps({"error": str(e), "kind": e.__class__.__name__}),
              file=sys.stderr)
        return 1

    single_file = args.input.is_file() and args.input.suffix.lower() == ".ipynb"

    # Always scan the submission tree (for a single notebook, scan_root is its parent)
    # so data files and a data/ subfolder are discovered — a draft must be checked
    # together with its ability to read its dataset.
    all_files = [p for p in scan_root.rglob("*")
                 if p.is_file() and not is_hidden_or_junk(p)]

    if single_file:
        # The user pointed at one notebook: review only that notebook, but inspect the
        # data sitting alongside it.
        notebooks = [args.input]
    else:
        notebooks = sorted(p for p in all_files if p.suffix.lower() == ".ipynb")
    data_files = sorted(p for p in all_files if p.suffix.lower() in DATA_EXTS)
    nested_archives = sorted(p for p in all_files
                             if p.suffix.lower() in ARCHIVE_EXTS)

    if not notebooks:
        print(json.dumps({
            "error": "No .ipynb notebooks found in the submission.",
            "scan_root": str(scan_root),
            "hint": ("If the submission is a .rar/.7z, extract it manually first. "
                     "Otherwise check the path."),
            "nested_archives": [str(a) for a in nested_archives],
        }, ensure_ascii=False), file=sys.stderr)
        return 2

    prefix, prefix_source = derive_prefix(notebooks, scan_root, args.input)

    nb_records = []
    seen_categories: dict[str, int] = {}
    for nb in notebooks:
        category, by = classify_notebook(nb)
        seen_categories[category] = seen_categories.get(category, 0) + 1
        name_ok = bool(GOOD_NAME_RE.match(nb.name.lower()))
        name_issue = None
        if not name_ok:
            expected = (f"{prefix}_{category}.ipynb"
                        if prefix and category != "unknown"
                        else "lastname_t_<category>.ipynb")
            name_issue = f"does not match snake_case convention; expected like `{expected}`"
        nb_records.append({
            "path": str(nb),
            "filename": nb.name,
            "category": category,
            "classified_by": by,
            "name_ok": name_ok,
            "name_issue": name_issue,
        })

    has_data_subfolder = any(
        p.is_dir() and p.name.lower() == "data" and not is_hidden_or_junk(p)
        for p in scan_root.rglob("*")
    )

    present = {r["category"] for r in nb_records if r["category"] != "unknown"}
    missing_categories = [c for c in ("regression", "clustering", "classification")
                          if c not in present]

    # Disambiguation: more than one notebook mapping to the same category, or any
    # unknown-category notebook, is worth a human glance but not fatal.
    duplicate_categories = {c: n for c, n in seen_categories.items()
                            if c != "unknown" and n > 1}

    result = {
        "input": str(args.input),
        "scan_root": str(scan_root),
        "single_file_mode": single_file,
        "prefix": prefix,
        "prefix_source": prefix_source,
        "notebooks": nb_records,
        "data_files": [str(p) for p in data_files],
        "nested_archives": [str(p) for p in nested_archives],
        "has_data_subfolder": has_data_subfolder,
        "categories_present": sorted(present),
        "missing_categories": missing_categories,
        "duplicate_categories": duplicate_categories,
        "unknown_category_count": seen_categories.get("unknown", 0),
        "naming_all_ok": all(r["name_ok"] for r in nb_records),
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
