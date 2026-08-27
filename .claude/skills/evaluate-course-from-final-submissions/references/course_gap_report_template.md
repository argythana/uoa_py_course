# Course-gap report — structure, naming, and the hand-off contract

The `evaluate-course-from-final-submissions` skill writes **one** aggregate report per
run. It is the skill's only deliverable. This file is its template and naming rule.

## Location & naming

```
admin_docs/course_eval/course_gap_report_<YY>_<TS>.md
```

- `<YY>` — the class cohort (e.g. `26`).  `<TS>` — `date +%Y-%m-%d_%H%M`.
- `admin_docs/` is **gitignored**. The report is PII-free *by construction* (no names,
  no slugs, no prose lifted from a single student), but it is **derived from**
  gitignored student work, so it defaults to a gitignored home. Once the maintainer
  has reviewed it, it is safe to copy anywhere — including handing it verbatim to the
  lecture-improvement skills — precisely because it is anonymous and aggregate.
- **Never overwrite.** The `<TS>` stamp gives every run its own dated file, so the
  cohort's gap history accumulates (this run's report vs last month's is a signal of
  whether a lecture fix landed).

## PII rules for the report body (load-bearing)

- No student names, no folder slugs, no submission filenames.
- Counts and percentages only ("N of M submissions"), never per-student rows.
- No verbatim prose from any single feedback file (a dataset name or a cell hash can
  identify a person). Describe themes in the skill's own words.
- In committed skill text / examples, the placeholder slug is `argyriou_t` — never a
  real student.

## Template

```markdown
# Course-gap report — class <YY> final assignments

**Date:** <YYYY-MM-DD>
**Cohort:** class_<YY>  ·  **Submissions analysed:** <M>  (<n_reg> regression / <n_clu> clustering / <n_cls> classification notebooks scored)
**Corpus:** <M> latest per-student grade runs + the grade skill's AUTOIMPROVE log
**Author:** Claude Code (skill: evaluate-course-from-final-submissions)
**Scope:** aggregate, PII-free. Turns graded-assignment output into course-improvement signal. Does NOT grade students, evaluate a single lecture, or rewrite lectures.

## Headline

- The <k> criteria where the cohort most under-delivered (by below-cap rate and zeros):
  1. **<criterion>** — <N>/<M> below cap, <z> zeros (<pct>% of cap on average) → **<TRIAGE>**, lecture <NN>.
  2. ...
- Single most actionable course change: <one sentence naming the lecture + the change>.

## Criterion signal table (from `harvest_grade_corpus.py`)

Deterministic, PII-free. `below` = notebooks scoring under the criterion cap; `zeros`
= complete misses; `mean %cap` = average fraction of the cap earned.

| Criterion (cap) | n | below | zeros | mean %cap | Owning lecture(s) | Triage |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| model_validation (0.5) | <n> | <b> | <z> | <p> | L09 / L10 / L13 | <MATERIAL/FRAMING/EXECUTION> |
| eda (1.5) | ... | | | | L08 | ... |
| ... | | | | | | |

(One row per criterion, ordered worst-first by below-cap rate. Owning lecture from
`criterion_lecture_map.md`.)

## Recurring themes (grouped, assessed, triaged)

For each recurring weakness — grouped from the criterion signal + the AUTOIMPROVE log
+ a read of the grade-summary reconciliation notes:

### Theme <k>: <short name>

- **What students did (aggregate):** <the pattern, in counts — "23 of 30 notebooks …">.
- **Evidence strength:** strong (whole cohort / unanimous) | moderate (several) | weak (1–2).
- **Where it is taught:** lecture <NN>, `goals_<NN>.md` <goal id>, `lec_<NN>x §<sec>`. What the lecture currently does / does not model.
- **Where the assignment asks for it:** `submission_requirements.prompt.md` <section/line>. Clear ask or vague?
- **Triage:** **<MATERIAL | ASSIGNMENT-FRAMING | STUDENT-EXECUTION>** (+ secondary if any). One sentence of *why*.

Repeat per theme, worst-first.

## Per-lecture improvement briefs (the hand-off — see below)

Grouped by lecture number so the lecture-improvement skills can consume directly.
Only lectures with a MATERIAL (or MATERIAL-leaning) finding appear here; FRAMING and
EXECUTION findings go to the two sections after.

### Lecture <NN> — <topic>

- **Gap:** <what the delivered material is missing / under-models>, from theme(s) <k>.
- **Evidence:** <N>/<M> submissions; criterion(s) <keys>; strength <strong/moderate/weak>.
- **Suggested change (minimal):** <one concrete, actionable edit a lecture skill can land — e.g. "in lec_08d, add a one-line written takeaway under each EDA plot so students have an exemplar to copy">.
- **Which skill:** `uoa-py-course-create-excellent-lecture` (new/expanded content) or `uoa-py-course-update-lecture-post-teaching` (if it is a taught-and-observed regression).
- **Predicted rubric side-effect:** <e.g. "adds ~0.1 h mandatory load; new goal needs a tied exercise (cat 4)"> — so the lecture skill plans for it.

Repeat per affected lecture, ordered by evidence strength × criterion weight.

## Assignment-framing findings (route to `final_assignment/*.prompt.md`)

Not a lecture problem — the *ask* is unclear or silent. The maintainer owns these.

- **<theme>** — <what to clarify in the instructions>. Evidence: <counts>.

## Student-execution findings (route to class-wide reminders / checklist)

Taught clearly, asked clearly, still missed. Fix is emphasis, not content.

- **<theme>** — <the class-wide note / pre-submission checklist item to add>. Evidence: <counts>.

## Method & caveats

- Corpus: <M> latest-per-student grade runs under `students_work/class_<YY>/`, harvested by `scripts/harvest_grade_corpus.py` (deterministic, PII-free), plus the AUTOIMPROVE log read for qualitative themes.
- Deductions are the panel's reconciled scores — a *suggested*-grade signal, not ground truth; small-N cohorts (M < ~15) make any single criterion's rate noisy. Treat weak-evidence themes as hypotheses to watch, not mandates.
- A criterion at full marks across the cohort (e.g. `dataset_selection`) is reported as a *non-finding* — evidence the material + ask are working.
```

## Hand-off contract to the lecture-improvement skills

The "Per-lecture improvement briefs" section is the machine-facing interface. It is
keyed by **lecture number** and each brief carries exactly what a downstream skill
needs to act without re-reading the corpus:

| Field | Consumed by | Why the downstream skill needs it |
| --- | --- | --- |
| **Lecture number + topic** | `uoa-py-course-create-excellent-lecture`, `uoa-py-course-update-lecture-post-teaching`, `uoa-py-course-lecture-outline` | Resolves the target folder (`lectures_*/lecture_NN_*/`). One brief = one lecture, matching those skills' "one lecture per invocation" rule. |
| **Gap** (what's missing/under-modelled) | create / update | The delta to close — states the *what*, not a rewrite. |
| **Evidence** (counts + strength) | create / update | Lets the maintainer prioritise; weak-evidence briefs are optional. |
| **Suggested change (minimal)** | create (update mode) / update-post-teaching | A concrete, ≤1-hour, single-section edit — the shape those skills' update mode wants. |
| **Which skill** | router | MATERIAL-new-content → `create-excellent-lecture`; taught-but-regressed-in-practice → `update-lecture-post-teaching`. |
| **Predicted rubric side-effect** | create / update | Those skills reason about cat-4/cat-9 side-effects before re-evaluating; naming them here saves an iteration. |

A downstream skill reads its lecture's brief, treats **Suggested change** as the
change brief, and runs its own procedure (eval → plan → author → re-eval). This skill
never edits lecture material — it only produces the brief.
