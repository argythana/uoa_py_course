#!/usr/bin/env python3
"""
check_notebook_static.py — mechanical static signals for one assignment notebook.

Usage:
    check_notebook_static.py <notebook.ipynb>

Emits JSON on stdout with deterministic signals the editorial pass uses (and must
verify against the real content — these are HINTS, not verdicts):

  - absolute_paths      : code cells that read data via an absolute machine path
  - pip_installs        : cells containing pip/conda install
  - imports_not_at_top  : import statements appearing after real code has started
  - unused_imports      : pyflakes "imported but unused" (best-effort; skipped if
                          pyflakes is unavailable)
  - headers_in_code     : code cells that are entirely comments (likely a section
                          header/conclusion that should be a markdown cell)
  - markdown_stats      : counts of markdown vs code cells
  - section_coverage    : per-section present/weak/absent heuristic for sections 1-9
  - classification_algos: which of KNN / Naive Bayes / Logistic Regression appear

No LLM, no network. Robust to malformed notebooks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --- absolute-path detection ------------------------------------------------
# The Windows-drive pattern requires the drive letter to NOT be preceded by an
# alphanumeric char, so it matches a real `"C:\..."` / `'D:/...'` but NOT the
# `s:\` inside an f-string like `f"Missing values:\n{...}"` (a common false
# positive) or a URL scheme like `http://`.
ABS_PATH_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"),   # C:\  or  C:/  (Windows drive)
    re.compile(r"\\\\[^\\]+\\"),                       # \\server\share (UNC)
    re.compile(r"['\"](/Users/|/home/|/mnt/|/content/drive/|/Volumes/)"),
]
READ_CALL_RE = re.compile(r"\b(read_csv|read_excel|read_table|read_parquet|read_json|open)\s*\(")

READ_CALLS = "read_csv|read_excel|read_table|read_parquet|read_json"

# First (positional) argument of a pandas read_* call. The alternation captures,
# in order: a balanced Path("…") literal, a quoted string literal, a *complete*
# bare variable name (not a dotted call like os.path.join), then anything else
# (a complex expression). We interpret the captured arg in _literal_from_arg.
# Each literal form is followed by (?=\s*[,)]) so it must be the WHOLE argument —
# a partial match like Path("data") in `Path("data") / "x.csv"` falls through to
# the complex-expression branch instead of being read as the "data" directory.
_ARG_FORMS = (
    r"(?:[A-Za-z_][\w.]*\.)?Path\(\s*[rfbuRFBU]{0,2}['\"][^'\"\n]+['\"]\s*\)(?=\s*[,)])"  # Path("…")
    r"|[rfbuRFBU]{0,2}['\"][^'\"\n]+['\"](?=\s*[,)])"                                      # "…"
    r"|[A-Za-z_]\w*(?=\s*[,)])"                                                            # bare name
    r"|[^,)]+"                                                                             # complex expr
)
READ_ARG_RE = re.compile(rf"\b({READ_CALLS})\s*\(\s*({_ARG_FORMS})")

# A quoted string literal:  "data/x.csv"  /  r'C:\x.xlsx'  /  f"data/{n}.csv"
STR_LITERAL_RE = re.compile(r"^[rfbuRFBU]{0,2}(['\"])(.+)\1$")
# A Path(...) literal:  Path("data/x.csv")  /  pathlib.Path('data/x.csv')
PATH_LITERAL_RE = re.compile(
    r"^(?:[A-Za-z_][\w.]*\.)?Path\(\s*[rfbuRFBU]{0,2}(['\"])([^'\"\n]+)\1\s*\)$"
)
BARE_NAME_RE = re.compile(r"^[A-Za-z_]\w*$")
# Assignment of a literal path to a variable, on its own line:
#   data_path = "data/x.csv"   /   data_path = Path("data/x.csv")
ASSIGN_PATH_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*=\s*(?:[A-Za-z_][\w.]*\.)?(?:Path\(\s*)?"
    r"[rfbuRFBU]{0,2}(['\"])([^'\"\n]+)\2"
)


def is_absolute_path(s: str) -> bool:
    return bool(
        s.startswith("/") or s.startswith("~")
        or re.match(r"[A-Za-z]:[\\/]", s) or s.startswith("\\\\")
    )


def _literal_from_arg(arg: str, assignments: dict[str, str]):
    """Resolve a read_* first-argument expression to (literal_path, source).

    Handles the three common student patterns; returns (None, "unknown-expr")
    for anything more complex (joins, f-string concatenation, os.path.join).
    """
    arg = arg.strip()
    m = STR_LITERAL_RE.match(arg)
    if m:
        return m.group(2), "literal"
    m = PATH_LITERAL_RE.match(arg)
    if m:
        return m.group(2), "Path-literal"
    if BARE_NAME_RE.match(arg) and arg in assignments:
        return assignments[arg], f"variable:{arg}"
    if BARE_NAME_RE.match(arg):
        return None, f"variable:{arg} (unresolved)"
    return None, "unknown-expr"


def _collect_path_assignments(code_cells) -> dict[str, str]:
    """Map variable name -> literal path string, scanning every code line first
    (a path variable is often defined in an earlier cell). Last write wins."""
    assignments: dict[str, str] = {}
    for _i, t in code_cells:
        for ln in t.splitlines():
            m = ASSIGN_PATH_RE.match(ln)
            if m:
                assignments[m.group(1)] = m.group(3)
    return assignments


def extract_data_reads(code_cells, notebook_dir: Path):
    """Find pandas read_* calls and check the path resolves on disk relative to the
    notebook's own directory (the executability / relative-path test).

    Resolves string literals, ``Path("…")`` literals, and bare variables assigned
    a literal path elsewhere in the notebook — so the common, *good* pattern
    ``data_path = Path("data/x.csv"); pd.read_csv(data_path)`` is checked, not missed.
    """
    assignments = _collect_path_assignments(code_cells)
    reads = []
    for i, t in code_cells:
        for m in READ_ARG_RE.finditer(t):
            call, arg = m.group(1), m.group(2)
            path, source = _literal_from_arg(arg, assignments)
            if path is None:
                reads.append({
                    "cell": i, "call": call, "path": None, "arg": arg.strip()[:80],
                    "is_absolute": False, "is_dynamic": True,
                    "resolved_from": source, "resolves_on_disk": None,
                })
                continue
            dynamic = "{" in path or "}" in path  # f-string interpolation
            absolute = is_absolute_path(path)
            if dynamic:
                exists = None
            elif absolute:
                exists = Path(path).expanduser().exists()
            else:
                exists = (notebook_dir / path).exists()
            reads.append({
                "cell": i,
                "call": call,
                "path": path,
                "is_absolute": absolute,
                "is_dynamic": dynamic,
                "resolved_from": source,
                "resolves_on_disk": exists,
            })
    return reads

PIP_RE = re.compile(r"(^|\s)(!pip|%pip|!conda|pip install|conda install)\b", re.MULTILINE)

IMPORT_RE = re.compile(r"^\s*(import\s+\w|from\s+[\w.]+\s+import\s)", re.MULTILINE)

# --- section-coverage signal keywords (lowercased substring match on code) ---
SECTION_CODE_SIGNALS = {
    "2_load_describe": ["read_csv", "read_excel", "read_table", ".head(", ".info(", ".dtypes"],
    "3_eda": ["plt.", "sns.", ".plot(", ".hist(", ".boxplot(", "seaborn", "matplotlib",
              ".barplot", "sns.heatmap", "scatter"],
    "4_descriptive_stats": [".describe(", ".corr(", "correlation", ".value_counts("],
    "5_preprocessing_split": ["train_test_split", "standardscaler", "minmaxscaler",
                              "labelencoder", "onehotencoder", "get_dummies", ".fillna(",
                              ".dropna(", "scaler"],
    "6_model_fit": [".fit("],
    "7_evaluation": ["accuracy_score", "confusion_matrix", "classification_report",
                     "mean_squared_error", "r2_score", "mean_absolute_error",
                     "silhouette_score", ".score(", "roc_auc", "f1_score"],
}
# Markdown-side signals (lowercased substring match on markdown text).
SECTION_MD_SIGNALS = {
    "2_load_describe": ["describe the data", "target variable", "feature", "data types",
                        "load the data"],
    "8_model_selection": ["best model", "winning model", "compare", "model selection",
                          "winner", "pick a winner"],
    "9_validation_new_obs": ["new observation", "hypothetical", "new data", "inference",
                             "predict for a new", "new sample"],
}

CLASSIFICATION_ALGOS = {
    "KNN": ["kneighborsclassifier", "knn"],
    "Naive Bayes": ["gaussiannb", "multinomialnb", "bernoullinb", "naive_bayes", "naive bayes"],
    "Logistic Regression": ["logisticregression", "logistic regression"],
}


def load_cells(nb_path: Path):
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="replace"))
    cells = []
    for i, cell in enumerate(nb.get("cells", [])):
        src = cell.get("source", "")
        text = "".join(src) if isinstance(src, list) else str(src)
        cells.append((i, cell.get("cell_type", "unknown"), text))
    return cells


def snippet(text: str, n: int = 100) -> str:
    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return (line[:n] + "…") if len(line) > n else line


def count_saved_outputs(nb_path: Path) -> dict:
    """Code cells with at least one saved output.

    A notebook submitted with ZERO saved outputs was never run-all'd before
    submission — a strong predictor of written conclusions that contradict the
    actual results (validated on real class-26 submissions).
    """
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="replace"))
    code = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
    with_out = sum(1 for c in code if c.get("outputs"))
    return {
        "code_cells": len(code),
        "code_cells_with_saved_outputs": with_out,
        "no_saved_outputs": bool(code) and with_out == 0,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebook", type=Path)
    args = ap.parse_args(argv)

    try:
        cells = load_cells(args.notebook)
    except (json.JSONDecodeError, OSError) as e:
        print(json.dumps({"error": str(e), "notebook": str(args.notebook)}),
              file=sys.stderr)
        return 1

    code_cells = [(i, t) for i, ct, t in cells if ct == "code"]
    md_cells = [(i, t) for i, ct, t in cells if ct == "markdown"]
    all_code = "\n".join(t for _, t in code_cells).lower()
    all_md = "\n".join(t for _, t in md_cells).lower()

    # absolute paths (only flag when the line also looks like a path/read)
    absolute_paths = []
    for i, t in code_cells:
        for ln in t.splitlines():
            if any(p.search(ln) for p in ABS_PATH_PATTERNS):
                absolute_paths.append({"cell": i, "snippet": snippet(ln)})
                break

    # relative read calls present at all?
    has_read_call = bool(READ_CALL_RE.search(all_code))

    # can the notebook actually find its data? (resolve read paths vs its own dir)
    data_reads = extract_data_reads(code_cells, args.notebook.resolve().parent)
    unresolved_reads = [r for r in data_reads
                        if r["resolves_on_disk"] is False]

    # pip installs
    pip_installs = [{"cell": i, "snippet": snippet(t)}
                    for i, t in code_cells if PIP_RE.search(t)]

    # imports not at top: once a code cell has non-import real code, later imports flag
    imports_not_at_top = []
    real_code_started = False
    for i, t in code_cells:
        stripped_lines = [ln for ln in t.splitlines()
                          if ln.strip() and not ln.strip().startswith("#")]
        has_import = bool(IMPORT_RE.search(t))
        has_nonimport = any(not IMPORT_RE.match(ln) for ln in stripped_lines) and bool(
            [ln for ln in stripped_lines if not re.match(r"^\s*(import |from )", ln)])
        if real_code_started and has_import:
            imports_not_at_top.append({"cell": i, "snippet": snippet(t)})
        if has_nonimport:
            real_code_started = True

    # headers in code: code cell that is entirely comments
    headers_in_code = []
    for i, t in code_cells:
        lines = [ln for ln in t.splitlines() if ln.strip()]
        if lines and all(ln.strip().startswith("#") for ln in lines):
            headers_in_code.append({"cell": i, "snippet": snippet(t)})

    # unused imports (best effort)
    unused_imports = None
    try:
        from pyflakes.api import check as pyflakes_check  # type: ignore
        from pyflakes.reporter import Reporter  # type: ignore
        import io
        out, err = io.StringIO(), io.StringIO()
        pyflakes_check("\n".join(t for _, t in code_cells), str(args.notebook),
                       Reporter(out, err))
        unused_imports = [ln for ln in out.getvalue().splitlines()
                          if "imported but unused" in ln]
    except Exception:
        unused_imports = None  # pyflakes unavailable / errored — skip silently

    # section coverage
    section_coverage = {}
    for sec, sigs in SECTION_CODE_SIGNALS.items():
        hits = [s for s in sigs if s in all_code]
        section_coverage[sec] = {"status": "present" if hits else "absent",
                                 "signals": hits}
    for sec, sigs in SECTION_MD_SIGNALS.items():
        hits = [s for s in sigs if s in all_md]
        prev = section_coverage.get(sec)
        status = "weak" if hits else "absent"
        # md-only sections (8, 9) and load-describe verbal part
        if prev is None:
            section_coverage[sec] = {"status": status, "signals": hits}
        else:
            if hits and prev["status"] == "absent":
                prev["status"] = "weak"
            prev["signals"] = sorted(set(prev["signals"]) | set(hits))
    # section 1 imports: present iff any import anywhere
    section_coverage["1_imports"] = {
        "status": "present" if IMPORT_RE.search(all_code) else "absent",
        "signals": ["import"] if IMPORT_RE.search(all_code) else [],
    }
    # fine-tuning signal for section 6: >=2 .fit calls OR a loop/param-grid
    n_fit = all_code.count(".fit(")
    finetune_signal = (n_fit >= 2 or "gridsearch" in all_code or "for " in all_code
                       and ("n_neighbors" in all_code or "n_clusters" in all_code
                            or "alpha" in all_code or "param" in all_code))
    section_coverage["6_model_fit"]["fit_calls"] = n_fit
    section_coverage["6_model_fit"]["finetuning_signal"] = bool(finetune_signal)

    classification_algos = {name: any(s in all_code for s in sigs)
                            for name, sigs in CLASSIFICATION_ALGOS.items()}

    result = {
        "notebook": str(args.notebook),
        "cell_counts": {"total": len(cells), "code": len(code_cells),
                        "markdown": len(md_cells)},
        "saved_outputs": count_saved_outputs(args.notebook),
        "absolute_paths": absolute_paths,
        "has_data_read_call": has_read_call,
        "data_reads": data_reads,
        "unresolved_data_reads": unresolved_reads,
        "pip_installs": pip_installs,
        "imports_not_at_top": imports_not_at_top,
        "unused_imports": unused_imports,
        "headers_in_code": headers_in_code,
        "markdown_stats": {
            "markdown_cells": len(md_cells),
            "code_cells": len(code_cells),
            "low_markdown": len(md_cells) < max(3, len(code_cells) // 4),
        },
        "section_coverage": section_coverage,
        "classification_algos": classification_algos,
        "_note": ("section_coverage and finetuning_signal are heuristic hints; the "
                  "editorial pass must confirm against the real notebook content."),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
