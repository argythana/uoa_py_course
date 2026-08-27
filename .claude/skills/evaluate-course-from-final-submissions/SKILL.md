---
name: evaluate-course-from-final-submissions
description: Use this skill to turn the ACCUMULATED final-assignment GRADING OUTPUT (many students, already graded) into COURSE-IMPROVEMENT signal — a prioritized, aggregate, PII-free report of where the delivered material has holes, keyed by lecture number. Trigger on requests like "what do the final submissions say about the course", "find course gaps from the graded assignments", "which lectures need work based on student mistakes", "summarize the cohort's recurring weaknesses", "aggregate the grading results into lecture improvements", "where is the material under-teaching students", or when a lecture-improvement skill invokes it for input. It reads the grade skill's cumulative AUTOIMPROVE log and the per-student grade-summary + criterion-feedback files under gitignored `students_work/`, harvests the 13 criterion scores into a deterministic PII-free JSON (`scripts/harvest_grade_corpus.py`), groups recurring criterion-level weaknesses with counts (N of M submissions), then for EACH theme LOCATES where it is taught (`goals_NN.md`) and where the assignment asks for it (`submission_requirements.prompt.md`) and TRIAGES it as a MATERIAL gap (under-taught), an ASSIGNMENT-FRAMING gap (unclear ask), or STUDENT-EXECUTION (taught + asked clearly, still missed). Output is one aggregate report (`admin_docs/course_eval/course_gap_report_<YY>_<TS>.md`) with per-lecture improvement briefs the lecture skills can consume. Do NOT use it to: GRADE a student or score a submission (use `uoa-py-course-final-assignment-grade`); give FORMATIVE feedback on a draft (use `uoa-py-course-final-assignment-feedback`); evaluate or score ONE lecture against the rubric (use `uoa-py-course-lecture-eval`); rewrite / improve / add content to a lecture (use `uoa-py-course-create-excellent-lecture`); apply post-teaching corrections to a lecture (use `uoa-py-course-update-lecture-post-teaching`); plan a lecture from scratch (use `uoa-py-course-lecture-outline`); or assess a postgrad dissertation (use `assess_postgrad_dissertation`). This skill only produces the cross-submission gap analysis — it never touches student notebooks or lecture files. It could be called BY the lecture-improvement skills to source their evidence.
---

# Evaluate the course from its final submissions

You are turning **many graded final assignments** into a single, prioritized picture of
**where the delivered course material is failing students** — not to re-grade anyone, but
to find the holes the aggregate exposes and hand concrete, lecture-keyed improvements to
the skills that fix lectures.

The unit of analysis is the **cohort**, never the student. The upstream grade skill
(`uoa-py-course-final-assignment-grade`) already produced, per student, a defensible
13-criterion score panel and a written feedback file. This skill mines the *accumulation*
of those: it asks "across everyone who submitted, which criteria did the class miss, why,
and whose problem is it — the material's, the assignment's, or the students'?"

The output is **one aggregate, PII-free Markdown report** with per-lecture improvement
briefs. That report is the whole deliverable. This skill does not edit a single notebook,
lecture file, or student submission.

## The core verb: triage, don't just tally

Counting deductions is the easy half. The value is the **triage** — for every recurring
weakness, deciding which of three things is true:

- **MATERIAL gap** — the owning lecture under-teaches the skill or (very common here)
  teaches the *mechanic* without modelling the *write-up*. Students copy what the lecture
  models; if `lec_08` shows plots with no written takeaway, students ship plots with no
  written takeaway. → routes to the lecture-improvement skills.
- **ASSIGNMENT-FRAMING gap** — the material is fine; the *ask* is vague, misreadable, or
  silent on the edge case students tripped on. → routes to `final_assignment/*.prompt.md`,
  the maintainer's call.
- **STUDENT-EXECUTION** — taught clearly, asked clearly, still missed. The fix is emphasis
  (a class-wide reminder, a pre-submission checklist), not a content change.

A theme can carry two triages; name the dominant one so the downstream skill knows whether
it owns the fix. **Getting the triage right is the point** — mis-labelling an execution
problem as a material gap sends a lecture skill to rewrite content that was never broken.

## Authoritative sources (read these at runtime)

1. `references/criterion_lecture_map.md` — **this skill's** verified map of each of the 13
   criteria to the lecture that teaches it, plus the class-26 seed patterns with their prior
   triage. Read it first; it saves re-deriving the routing every run.
2. `references/course_gap_report_template.md` — the report structure, naming, PII rules, and
   the hand-off contract to the lecture skills.
3. `final_assignment/submission_requirements.prompt.md` — the 13 weighted criteria, caps,
   and the naming / single-zip gates. **Source of truth for what is asked.**
4. `final_assignment/grade_feedback.prompt.md` — the grading orientation (accuracy mandate).
5. The upstream grade skill's `AUTOIMPROVE.md`
   (`.claude/skills/uoa-py-course-final-assignment-grade/AUTOIMPROVE.md`) — one PII-free entry
   per graded student; it *already* names recurring cohort patterns (timestamps, no names).
   Your richest qualitative input.
6. The per-lecture `goals_NN.md` files — where each criterion is actually taught. Confirm a
   MATERIAL triage against these before asserting it.

If (3) or (4) change, this skill stays correct because it reads them live.

## Boundaries & safety

- **Cohort-level, aggregate output only.** Never a per-student verdict. If asked to grade or
  to coach one student, stop and route to the grade / feedback skill.
- **Read-only against everything.** The skill reads the grading corpus, the specs, the
  goals files, and the lecture folders (to confirm a triage). It **writes only** the one
  report. It never edits student work, lecture material, `docs/Lectures_outline.md`,
  `README.md`, `CLAUDE.md`, or the prompt files.
- **PII discipline (load-bearing — `.claude/skills/` is committed / open-sourced).**
  `students_work/` is gitignored student PII. The skill *reads* it but its **report and
  every line it prints to chat must be aggregate and PII-free**: no student names, no folder
  slugs, no submission filenames, no verbatim prose lifted from a single feedback file
  (a dataset name or a cell hash can identify a person), counts / percentages / criterion
  themes only. `scripts/harvest_grade_corpus.py` enforces this at the data layer — its stdout
  is anonymous by construction (sorted point lists, no student mapping). The **report defaults
  to gitignored `admin_docs/course_eval/`** because it is *derived from* gitignored work;
  it is safe to hand to the lecture skills precisely because it is anonymous and aggregate.
  In committed skill text use the placeholder slug `argyriou_t`, never a real student.
- **Interpreter.** Use the course venv for the harvester: `course_venv/bin/python`. No
  installs, no network. The script is Python 3.12 stdlib only.
- **Never invent a finding.** Every theme cites the criterion, the count (N of M), and the
  lecture/goal + spec section it was triaged against. A criterion the cohort *aced* (e.g.
  `dataset_selection` at full marks) is reported as a non-finding — evidence the material
  and the ask are working, not something to pad.
- **Small-N honesty.** A cohort of M < ~15 makes any single criterion's rate noisy. Label
  weak-evidence themes (1–2 students) as hypotheses to watch, not mandates.
- **Transient files go to `/tmp`, never a tracked path.** The harvester's JSON and any
  scratch are corpus-derived; keep them out of the repo tree even though they are PII-free.

## Procedure

### Phase 0 — Scope

1. Determine the cohort: default `class_26`; the user may name another (e.g. `class_25`).
2. Confirm the corpus exists: `students_work/class_<YY>/*/final_assignment/` with
   `*_<category>_feedback_<TS>.md` grade files. If none, say so and stop — there is nothing
   to aggregate yet (the grade skill has to run first).

### Phase 1 — Harvest the quantitative signal (deterministic)

```bash
REPO=$(git rev-parse --show-toplevel)
PY=$REPO/course_venv/bin/python
SKILL=$REPO/.claude/skills/evaluate-course-from-final-submissions
WORK=$(mktemp -d)   # scratch in /tmp — corpus-derived, never a tracked path
$PY "$SKILL/scripts/harvest_grade_corpus.py" --class <YY> --table > "$WORK/corpus.json"
```

The harvester walks every `*_<category>_feedback_<TS>.md` file, extracts the 13-criterion
score table, **deduplicates to the latest grade run per student per notebook category**
(a re-graded student counts once), and emits PII-free JSON: per criterion and per category,
the count scored below cap, the zeros, and the mean fraction of cap earned. `--table` also
prints a human-readable summary to stderr.

- It **excludes** the formative feedback skill's `*_assignment_draft_feedback_*.md` files
  (those carry readiness checkmarks, not numeric scores) — verified.
- Output is deterministic: same corpus → same JSON.
- Keep `$WORK` in `/tmp`; do not write the JSON into the repo tree (it is PII-free but
  corpus-derived — keep the discipline). Self-clean `$WORK` at the end.

Read the JSON. The worst criteria (highest below-cap rate, most zeros, lowest mean %cap)
are your candidate themes.

### Phase 2 — Fold in the qualitative signal

The numbers say *which* criteria; the AUTOIMPROVE log says *what shape* the miss takes.
Read `.claude/skills/uoa-py-course-final-assignment-grade/AUTOIMPROVE.md` end to end. It
already records cohort patterns in prose (e.g. "model_validation = 0.0 in all three
notebooks — promised a new-observation prediction but only ever calls `.predict(X_test)`";
"5th of 9 graded missing a required algo"). Match each AUTOIMPROVE pattern to a harvested
criterion; the log turns "23/30 below cap on `model_validation`" into a *diagnosable* theme
("built-but-uninterpreted / reused-test-row / never-built").

Optionally skim a few grade-summary reconciliation notes for texture — but never quote them
verbatim into the report, and never record which student they came from.

### Phase 3 — Group into themes

Cluster the signal into a handful of recurring themes (aim for the 5–8 that matter, not one
per criterion). Each theme gets: the pattern in counts, an evidence-strength label
(strong = whole-cohort / unanimous; moderate = several; weak = 1–2), and the criterion(s) it
spans. Order worst-first by below-cap rate × criterion weight.

### Phase 4 — Locate & triage each theme

For every theme, run the **triage decision rule** from `criterion_lecture_map.md`:

1. **Locate the teaching.** Open the owning lecture's `goals_NN.md` and the cited notebook
   section (`lec_NNx §<sec>`). Does the lecture teach the skill to the depth the criterion
   demands, *and model the write-up* (interpretation, not just the mechanic)?
2. **Locate the ask.** Open `submission_requirements.prompt.md`. Is the requirement stated
   unambiguously, in words a first-year MSc student maps to an action?
3. **Decide** MATERIAL / ASSIGNMENT-FRAMING / STUDENT-EXECUTION (record a secondary triage
   if real; name the dominant one).

Use the map's seed-pattern table as your **prior**, but confirm it against the *current*
corpus and the *current* lecture files — a lecture may have been improved since the seed was
recorded, flipping a MATERIAL finding to EXECUTION. Do not hard-code the seed conclusions.

### Phase 5 — Write the report

Write to `admin_docs/course_eval/course_gap_report_<YY>_<TS>.md`
(`TS=$(date +%Y-%m-%d_%H%M)`; `mkdir -p` the dir; never overwrite a prior report). Follow
`references/course_gap_report_template.md` exactly. The load-bearing section is
**"Per-lecture improvement briefs"** — grouped by lecture number, each a self-contained
change brief a lecture skill can act on (gap · evidence · minimal suggested change · which
skill · predicted rubric side-effect). Assignment-framing and student-execution findings go
to their own sections (they do not route to the lecture skills).

Print to chat **only**: the report path, the top 3 themes with their triage and lecture
number, and the single most actionable change. No student PII, no per-student rows.

## Hand-off to the lecture-improvement skills

This skill's report is the **evidence source** for the skills that change lectures. The
"Per-lecture improvement briefs" section is the interface: keyed by lecture number (so each
brief maps to exactly one `lectures_*/lecture_NN_*/` folder, matching those skills'
one-lecture-per-invocation rule), and each brief carries what the downstream skill needs to
act without re-reading the corpus — the **gap**, the **evidence** (counts + strength), a
**minimal suggested change**, **which skill** should own it, and the **predicted rubric
side-effect**. The full field-by-field contract is in
`references/course_gap_report_template.md` §"Hand-off contract".

Routing of a per-lecture brief:

- **MATERIAL gap, new or expanded content** → `uoa-py-course-create-excellent-lecture`
  (its update mode takes a change brief and re-evaluates against the 9-category rubric). The
  brief's "Suggested change" is its change brief.
- **MATERIAL gap that is a taught-but-observed regression** (the intent was there, the
  as-shipped lecture lost it) → `uoa-py-course-update-lecture-post-teaching`, feeding the
  cohort evidence as the "pain point".
- **A lecture that needs re-planning from the gap** → `uoa-py-course-lecture-outline` first,
  then the create skill.

This skill **could be called by** those skills to source their evidence (a create/update run
that wants to know what the cohort actually got wrong), or run standalone by the maintainer
after a grading batch. Either way it only produces the analysis — the lecture skills own the
edits, `uoa-py-course-lecture-eval` remains the judge of whether a fix landed.

## Quality bar

- Every theme names the criterion, the count (N of M), the owning lecture + goal, the spec
  section, and an explicit triage. No un-triaged themes.
- Per-lecture briefs are concrete enough to act on in ≤1 hour each — a named section and a
  named change, not "improve the EDA lecture".
- The report is aggregate and PII-free; the harvester JSON it is built on is reproducible.
- Aced criteria are reported as non-findings, not omitted (absence of a gap is a result).
- The report distinguishes the three triages cleanly — a lecture skill reading it never has
  to guess whether a finding is theirs to fix.

## Tone

Direct, concrete, no flattery. The maintainer wants to know which lecture to open next and
why, backed by counts. If the evidence is thin, say "hypothesis to watch (2 students)"
rather than dressing it up. A single honest "the material is fine here, this is an execution
problem" is worth more than three plausible-but-unfounded lecture rewrites.
