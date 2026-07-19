#!/usr/bin/env python3
"""
inspect_datasets.py — check the datasets in a submission against the course's
data-selection guidelines (see references/dataset_rules.md).

Usage:
    inspect_datasets.py <data_file_or_dir> [<more> ...]

For each .csv / .tsv / .xlsx / .xls it loads the table with pandas and reports:
  - shape (rows, cols) and a numeric/categorical column tally
  - size_ok      : rows >= 300 (soft window 270-300)
  - shape_ok     : cols >= 7  (>= 6 features + target)
  - ratio_ok     : rows >= 10 * cols
  - forbidden    : match against course/tutorial datasets, by filename AND by
                   column signature (catches renamed files)
  - possible_timeseries / possible_text : out-of-scope data-type hints

Output is JSON on stdout. No LLM, no network. Load errors are reported, not raised.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TABLE_EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".parquet"}

# Directory names that mark dependency/IDE/VCS trees (most often a bundled
# virtualenv) a student may have zipped by accident — never scan inside them.
ENV_DIR_NAMES = {
    "site-packages", "node_modules", "__pycache__", ".ipynb_checkpoints",
    "__MACOSX", ".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache", ".tox",
    ".eggs", ".idea", ".vscode",
}


def _in_env_dir(p: Path) -> bool:
    """True if any path segment names a venv / dependency / tooling dir."""
    for seg in p.parts:
        s = seg.lower()
        if s in ENV_DIR_NAMES or s in {"venv", ".venv", "env", ".env"}:
            return True
        if s.endswith("venv") or s.endswith(".dist-info") or s.endswith(".egg-info"):
            return True
    return False

# (dataset, filename substrings, column-signature substrings, min signature hits)
FORBIDDEN = [
    ("Iris", ["iris"], ["sepal", "petal", "species"], 2),
    ("Wine", ["wine"], ["alcohol", "malic", "flavanoid", "proline",
                        "od280", "ash"], 3),
    ("Breast Cancer", ["breast", "cancer", "wdbc"],
        ["radius_mean", "texture_mean", "concavity", "diagnosis", "perimeter_mean"], 2),
    ("Boston Housing", ["boston"],
        ["crim", "zn", "indus", "nox", "rm", "medv", "lstat", "ptratio"], 4),
    ("Diabetes (Pima)", ["diabetes", "pima"],
        ["pregnancies", "glucose", "bloodpressure", "skinthickness",
         "insulin", "bmi", "diabetespedigree", "outcome"], 4),
    ("MNIST / digits", ["mnist", "digits"], ["pixel"], 1),
    ("Mall customers", ["mall"],
        ["customerid", "annual income", "spending score", "annual_income",
         "spending_score"], 2),
    ("Heart Disease", ["heart"],
        ["cp", "trestbps", "thalach", "oldpeak", "chol", "thal", "exang",
         "restecg", " caa", "num"], 4),
]

# Only genuine date-like column names. A plain integer "Year"/"Runtime" column is an
# ordinary feature, not a time index — including those produced false positives.
TIME_HINT_COLS = ["date", "datetime", "timestamp"]

# Above this size, a CSV/TSV is analysed from a sample (bounded memory + time)
# instead of a full load — the row count is taken cheaply by streaming lines, so
# the size/shape checks stay correct without pulling a multi-GB file into RAM.
LARGE_FILE_BYTES = 50 * 1024 * 1024  # 50 MB
SAMPLE_ROWS = 100_000


def load_table(path: Path, nrows: int | None = None):
    """Best-effort load; return (df, error). ``nrows`` caps rows for big files."""
    ext = path.suffix.lower()
    try:
        import pandas as pd
        if ext in {".xlsx", ".xls"}:
            return pd.read_excel(path, nrows=nrows), None
        if ext == ".parquet":
            return pd.read_parquet(path), None  # columnar; no cheap nrows cap
        sep = "\t" if ext == ".tsv" else None
        try:
            return pd.read_csv(path, sep=sep, engine="python", nrows=nrows), None
        except UnicodeDecodeError:
            return pd.read_csv(path, sep=sep, engine="python", nrows=nrows,
                               encoding="latin-1"), None
    except Exception as e:  # noqa: BLE001 - report, never raise
        return None, f"{e.__class__.__name__}: {e}"


def count_data_rows(path: Path) -> int | None:
    """Cheap, constant-memory data-row count (lines minus header) for a text table.
    Approximate if fields contain embedded newlines — fine for the size check."""
    try:
        with open(path, "rb", buffering=1024 * 1024) as fh:
            lines = sum(buf.count(b"\n") for buf in iter(lambda: fh.read(1024 * 1024), b""))
        return max(lines - 1, 0)
    except OSError:
        return None


def match_forbidden(path: Path, columns: list[str]) -> dict | None:
    fname = path.name.lower()
    cols = [str(c).lower() for c in columns]
    cols_joined = " ".join(cols)
    for name, fhints, sighints, min_hits in FORBIDDEN:
        by_filename = any(h in fname for h in fhints)
        if name.startswith("MNIST"):
            # The MNIST/digits signal is MANY pixel columns (pixel0..pixel783),
            # not a single column that merely contains "pixel" — e.g. Steel
            # Plates' "Pixels_Areas" must NOT trip this.
            pixel_cols = sum(1 for c in cols if "pixel" in c)
            by_columns = pixel_cols >= 10
            sig_hits = [f"{pixel_cols} pixel-named columns"] if by_columns else []
        else:
            sig_hits = [s for s in sighints
                        if any(s in c for c in cols) or s in cols_joined]
            by_columns = len(sig_hits) >= min_hits
        if by_filename or by_columns:
            if name.startswith("MNIST"):
                non_matching = [c for c in cols if "pixel" not in c]
            else:
                non_matching = [c for c in cols
                                if not any(s in c for s in sighints)]
            return {
                "dataset": name,
                "by_filename": by_filename,
                "by_columns": by_columns,
                "matched_signature_cols": sig_hits,
                "renamed_suspect": by_columns and not by_filename,
                "columns_not_matching_signature": non_matching,
                # A signature match can be a same-schema VARIANT (synthetic /
                # augmented Kaggle copy), not the course's actual data. The
                # signature hints are partial, so the new-feature ratio must be
                # judged against the dataset's true original schema.
                "verification_required": True,
                "note": ("Hint, not a verdict: before ruling forbidden, verify "
                         "against the course's actual file (column names + "
                         "row-level overlap). Variant rule in dataset_rules.md: "
                         "class-2026 same-schema variants are grandfathered; "
                         "from 2027 a variant needs >=50% genuinely new "
                         "features."),
            }
    return None


def inspect_one(path: Path) -> dict:
    size_bytes = path.stat().st_size if path.exists() else 0
    is_text_table = path.suffix.lower() in {".csv", ".tsv"}
    sampled = is_text_table and size_bytes > LARGE_FILE_BYTES

    df, err = load_table(path, nrows=SAMPLE_ROWS if sampled else None)
    if err is not None:
        return {"path": str(path), "load_error": err}

    import pandas as pd
    # On a sampled big file, df holds only the first SAMPLE_ROWS rows — take the
    # true row count cheaply from the file so the size checks stay correct.
    if sampled:
        true_rows = count_data_rows(path)
        rows = true_rows if true_rows is not None else int(df.shape[0])
    else:
        rows = int(df.shape[0])
    cols = int(df.shape[1])
    numeric = int(df.select_dtypes(include="number").shape[1])
    non_numeric = cols - numeric

    # possible text: an object column whose values are long on average
    possible_text = False
    for c in df.select_dtypes(include="object").columns:
        try:
            avg_len = df[c].dropna().astype(str).str.len().mean()
            if avg_len and avg_len > 50:
                possible_text = True
                break
        except Exception:
            continue

    # possible time series: a date-like column name, a NON-numeric dtype (so an
    # integer year/runtime feature doesn't trigger), that actually parses as dates.
    possible_timeseries = False
    for c in df.columns:
        cl = str(c).lower()
        if any(h in cl for h in TIME_HINT_COLS):
            col = df[c]
            if pd.api.types.is_numeric_dtype(col):
                continue
            try:
                parsed = pd.to_datetime(col, errors="coerce")
                if parsed.notna().mean() > 0.8:
                    possible_timeseries = True
                    break
            except Exception:
                continue

    return {
        "path": str(path),
        "rows": rows,
        "cols": cols,
        "numeric_cols": numeric,
        "categorical_cols": non_numeric,
        "column_names": [str(c) for c in df.columns][:60],
        "size_ok": rows >= 300,
        "size_soft": 270 <= rows < 300,
        "shape_ok": cols >= 7,
        "ratio_ok": rows >= 10 * cols,
        "size_mb": round(size_bytes / (1024 * 1024), 1),
        "very_large": sampled,  # bigger than LARGE_FILE_BYTES; analysed from a sample
        "sampled_rows": int(df.shape[0]) if sampled else None,
        "possible_text": possible_text,
        "possible_timeseries": possible_timeseries,
        "forbidden": match_forbidden(path, list(df.columns)),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", type=Path, nargs="+")
    args = ap.parse_args(argv)

    files: list[Path] = []
    for p in args.paths:
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*")
                                if f.suffix.lower() in TABLE_EXTS
                                and not _in_env_dir(f)))
        elif p.suffix.lower() in TABLE_EXTS:
            files.append(p)

    results = [inspect_one(f) for f in files]
    print(json.dumps({"datasets": results, "count": len(results)},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
