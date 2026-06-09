#!/usr/bin/env bash
#
# scaffold_student_dirs.sh — create per-student work folders for a year's class.
#
# For every registered student of the given year it ensures
#
#   students_work/class_<YY>/<slug>/practice_exercises
#   students_work/class_<YY>/<slug>/final_assignment
#
# exist, where <slug> comes from the eClass roster via
# `automation_infrastructure.roster_slugs` (e.g. ΠΑΠΑΔΟΠΟΥΛΟΥ ΜΑΡΙΑ ->
# papadopoulou_m). The operation is idempotent: existing folders are left
# untouched, only missing ones are created.
#
# students_work/ is gitignored (student PII); this script writes there but is
# itself committed.
#
# Usage:
#   automation_infrastructure/scaffold_student_dirs.sh [options]
#
# Options:
#   --year YYYY     Class year (default: current year).
#   --course CODE   eClass course code (default: ECON537).
#   --db PATH       Path to eclass.db (default: admin_docs/eclass_data/eclass.db).
#   --dry-run       Show what would be created; make no changes.
#   -h, --help      Show this help and exit.
#
set -euo pipefail

SUBDIRS=(practice_exercises final_assignment)

YEAR="$(date +%Y)"
COURSE="ECON537"
DB_ARG=""
DRY_RUN=0

usage() { sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --year)   YEAR="${2:?--year needs a value}"; shift 2 ;;
        --course) COURSE="${2:?--course needs a value}"; shift 2 ;;
        --db)     DB_ARG="${2:?--db needs a value}"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

# --- locate repo root and interpreter ---------------------------------------

if REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)"; then
    :
else
    REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi
cd "$REPO_ROOT"

if [[ -x course_venv/bin/python ]]; then
    PY=course_venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    echo "error: no python interpreter found (course_venv/bin/python or python3)" >&2
    exit 1
fi

YY="$(printf '%02d' "$((YEAR % 100))")"
CLASS_DIR="students_work/class_${YY}"

# --- fetch the roster slugs --------------------------------------------------

ROSTER_ARGS=(--year "$YEAR" --course "$COURSE")
[[ -n "$DB_ARG" ]] && ROSTER_ARGS+=(--db "$DB_ARG")

# Read slugs into an array; the helper prints one per line and exits non-zero
# (with a message on stderr) if the DB is missing.
mapfile -t SLUGS < <("$PY" -m automation_infrastructure.roster_slugs "${ROSTER_ARGS[@]}")
if [[ ${#SLUGS[@]} -eq 0 ]]; then
    echo "error: roster query returned no students for ${COURSE} ${YEAR}." >&2
    echo "       (is admin_docs/eclass_data/eclass.db populated?)" >&2
    exit 1
fi

echo "Scaffolding ${#SLUGS[@]} student folders for ${COURSE} ${YEAR} under ${CLASS_DIR}/"
[[ $DRY_RUN -eq 1 ]] && echo "(dry run — no changes will be made)"
echo

# --- create folders ----------------------------------------------------------

created=0
existing=0
for slug in "${SLUGS[@]}"; do
    student_dir="${CLASS_DIR}/${slug}"
    for sub in "${SUBDIRS[@]}"; do
        target="${student_dir}/${sub}"
        if [[ -d "$target" ]]; then
            existing=$((existing + 1))
        elif [[ $DRY_RUN -eq 1 ]]; then
            echo "  would create  ${target}"
            created=$((created + 1))
        else
            mkdir -p "$target"
            echo "  created       ${target}"
            created=$((created + 1))
        fi
    done
done

# --- verify ------------------------------------------------------------------

echo
missing=0
for slug in "${SLUGS[@]}"; do
    for sub in "${SUBDIRS[@]}"; do
        target="${CLASS_DIR}/${slug}/${sub}"
        if [[ ! -d "$target" && $DRY_RUN -eq 0 ]]; then
            echo "  MISSING       ${target}" >&2
            missing=$((missing + 1))
        fi
    done
done

# --- flag orphan folders (present on disk but not in this year's roster) -----

orphans=()
if [[ -d "$CLASS_DIR" ]]; then
    while IFS= read -r dir; do
        name="$(basename "$dir")"
        found=0
        for slug in "${SLUGS[@]}"; do
            [[ "$slug" == "$name" ]] && { found=1; break; }
        done
        [[ $found -eq 0 ]] && orphans+=("$name")
    done < <(find "$CLASS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name '.*' | sort)
fi

# --- summary -----------------------------------------------------------------

echo "Summary:"
echo "  students in roster : ${#SLUGS[@]}"
if [[ $DRY_RUN -eq 1 ]]; then
    echo "  subfolders to create: ${created}"
else
    echo "  subfolders created : ${created}"
    echo "  subfolders existing: ${existing}"
fi
if [[ ${#orphans[@]} -gt 0 ]]; then
    echo "  orphan folders (not in ${YEAR} roster, left untouched): ${#orphans[@]}"
    for name in "${orphans[@]}"; do
        echo "      - ${CLASS_DIR}/${name}"
    done
fi

if [[ $missing -gt 0 ]]; then
    echo
    echo "error: ${missing} expected subfolder(s) missing after run." >&2
    exit 1
fi

if [[ $DRY_RUN -eq 0 ]]; then
    echo "  all ${#SLUGS[@]} students have practice_exercises + final_assignment ✓"
fi
exit 0
