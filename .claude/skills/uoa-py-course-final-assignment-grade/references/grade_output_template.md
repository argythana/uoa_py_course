# Grade output — file naming, structure, and the mandatory disclaimers

The grading skill writes its output into the **same** per-student folder the submission
lives in (the locator's `feedback_dir` = `students_work/class_<YY>/<lastname_t>/final_assignment/`).
That tree is **gitignored PII** — never echo its contents to the chat (print only paths +
one-line status), never commit it.

**Never overwrite.** A student folder may already hold an earlier grade run *and* the
formative feedback skill's `<prefix>_assignment_draft_feedback_<date>.md`. Every grade file
this skill writes carries a **runtime timestamp** so nothing is ever clobbered — each run
leaves a fresh, dated trail. Generate the stamp once per run:

```bash
TS=$(date +%Y-%m-%d_%H%M)   # e.g. 2026-06-14_1637  (date + time to the minute)
```

Two kinds of file (both stamped with the same `TS`):

1. **One feedback file per submitted notebook** — the artefact `grade_feedback.prompt.md`
   asks for, named with the submission convention, the constant suffix `_feedback`, and `TS`:

   ```
   <prefix>_<category>_feedback_<TS>.md
   ```
   e.g. `argyriou_t_classification_feedback_2026-06-14_1637.md`.

2. **One assignment-level grade summary** (instructor-facing) — the total, the weighting,
   the rejection gates, and the **three-grader reconciliation** so the instructor sees how
   the panel agreed/diverged:

   ```
   <prefix>_assignment_grade_summary_<TS>.md
   ```

> These names are distinct from the **formative** feedback skill's
> `<prefix>_assignment_draft_feedback_<date>.md`, so the grading and feedback outputs never
> collide in the same folder. **Before writing, confirm no file of the same name exists** (the
> minute-level stamp makes this near-certain, but check — if it does, bump `TS` to `_%H%M%S`).

## Mandatory disclaimers (from grade_feedback.prompt.md — verbatim intent)

Every per-notebook feedback file **must** state, near the top:

- The suggested assignment grade is **AI-generated, not final**; the instructor may increase
  or decrease it.
- Each notebook is **also examined by the tutor**.
- The **total course grade** = the final-assignment grade **plus** practice-exercise
  submissions **plus** in-class participation.

## Per-notebook feedback file template

```markdown
# Final-assignment grade & feedback — <prefix> · <Category>

> **AI-suggested grade — not final.** This grade is AI-generated; the instructor may raise or
> lower it, and each notebook is also examined by the tutor. Your total course grade is the
> final-assignment grade **plus** your practice-exercise submissions **plus** class participation.

**Notebook:** `<filename>`  ·  **Suggested grade for this notebook: <grade>/10**
**Run-all (`course_venv`):** <runs clean / breaks at cell N: one-line reason / skipped: reason>

## What this notebook does well
- <name a genuinely strong section and why — the prompt asks to point out awesome work>

## Criterion-by-criterion
Each line: the criterion, the suggested points (out of its cap), and the reason. Where points
are lost, name the **exact** criterion and the cell/section, per the requirements.

| Criterion (cap) | Points | Notes |
| --- | --- | --- |
| Executability (0.5) | <n> | <reason> |
| Readability (0.5) | <n> | <reason> |
| Imports (0.5) | <n> | <reason> |
| Dataset selection (0.5) | <n> | <reason> |
| Relative paths (0.5) | <n> | <reason> |
| Data presentation (0.5) | <n> | <reason> |
| EDA (1.5, strict) | <n> | <reason> |
| Descriptive statistics (0.5) | <n> | <reason> |
| Preprocessing (1.0) | <n> | <reason> |
| Model implementation & fine-tuning (2.0) | <n> | <reason> |
| Model evaluation (1.0) | <n> | <reason> |
| Model selection / comparison (0.5) | <n> | <reason> |
| Model validation on new data (0.5) | <n> | <reason> |

## What's missing or costs points (explicit)
- <criterion> — <what is missing / wrong, and the cell/section>. <points impact>
- ...

## To reach full marks
- <concrete next step> ...
```

Notes:
- The per-notebook **grade in the header comes from `compute_grade.py`** (the rounded
  notebook grade), not from re-summing by hand. The per-criterion points in the table are the
  final reconciled scores fed to that script.
- For **classification**, the model-implementation and selection rows must address **KNN,
  Naive Bayes, and Logistic Regression** explicitly (which are present, which are missing, the
  comparison of all three).
- Omit nothing from the 13-row table even when a criterion is 0 — a 0 with a reason is the
  most useful feedback.

## Assignment grade summary template (instructor-facing)

```markdown
# Assignment grade summary — <prefix>

> AI-suggested, not final. Instructor + tutor review and may adjust. Total course grade also
> includes practice exercises and class participation.

**Suggested total assignment grade: <total>/10**  <"(below the 5–10 pass band)" if applicable>

| Notebook | Weight | Suggested grade | Weighted |
| --- | --- | --- | --- |
| Regression | 0.25 | <g>/10 | <w> |
| Clustering | 0.25 | <g>/10 | <w> |
| Classification | 0.50 | <g>/10 | <w> |
| **Total** | | | **<total>/10** |

**Submission gates (instructor's call — flagged, not auto-applied):**
- File naming (`lastname_t_<category>.ipynb`, snake_case): <OK / which files violate it>
- Single `.zip` containing notebooks + data: <OK / issue>
- Work-data alternative declared: <no / yes — basis for grading adjusted>

## Panel reconciliation (how the three graders compared)
A short, instructor-only note: where Grader 1, Grader 2, and the arbiter's own independent
pass **agreed**, and where they **diverged** (which criteria, the spread, and how the arbiter
resolved it). This is the audit trail for "no misjudgments or unfavourable treatment".

| Notebook | Grader 1 | Grader 2 | Arbiter (independent) | Final |
| --- | --- | --- | --- | --- |
| Regression | <g1> | <g2> | <g3> | <final> |
| Clustering | <g1> | <g2> | <g3> | <final> |
| Classification | <g1> | <g2> | <g3> | <final> |

- **Notable divergences:** <criterion-level disagreements > ~0.5 and how they were resolved>
- **Resolution basis:** <what evidence in the notebook settled each contested criterion>
- **Draft-feedback cross-reference** (only if a prior `*_assignment_draft_feedback_*.md` existed):
  <what the earlier draft feedback corroborated; what it caught that both live graders missed;
  which of its flags were stale because the student already fixed them in the final submission>.
  Omit this line entirely if no draft feedback was available.

---
*Generated by the `uoa-py-course-final-assignment-grade` skill to assist the instructor's
grading. The grade is a suggestion; always apply your own judgement.*
```
