---
name: uoa-py-course-lecture-outline
description: Use this skill to produce a structural outline for one lecture in this course repo — a draft `goals_NN.md` plus an internal design doc that pre-conforms to the 9-category rubric used by `uoa-py-course-lecture-eval`. Trigger on requests like "outline lecture NN", "plan a lecture on X", "design lecture NN before writing it", "draft goals_NN.md for X", "plan the refactor of lecture NN", or "scaffold the outline for the regression lecture". Do NOT use it to: generate lecture content (no code, no datasets, no specific industry uses — that work belongs to the future `create-improve-lecture` skill); evaluate an existing lecture (use `uoa-py-course-lecture-eval`); grade student submissions; rewrite `docs/Lectures_outline.md` directly (the skill emits a suggested patch instead). If the lecture number or topic is ambiguous, ask before proceeding.
---

# Lecture outline

You are producing a **structural outline** for one lecture. The output is two Markdown files; the maintainer will read them, edit, and feed them into the future `create-improve-lecture` skill. The point of this skill is to lock in the structural commitments — goals, files, exercises, time budget, AI-fluency plan — so that when content is written, it slots into a shape that will pass the rubric used by `uoa-py-course-lecture-eval`.

This is a planning skill. It does not invent content. It declares slots and contracts.

## What strong looks like (calibration)

Calibration is delegated. Read `.claude/skills/uoa-py-course-lecture-eval/SKILL.md` §"What a strong lecture looks like" and §"Structural model of a course lecture" before producing an outline. The rubric there is the contract this skill writes against — do not duplicate it here, do not contradict it. If the eval skill's rubric changes, this skill follows.

The benchmark for a refactored lecture is `lectures_07_13_pandas_plots_scikit/lecture_09_clustering_deploy_hf_app/`. Its 6-notebook decomposition (core walkthrough → assumptions/limitations → practical/deploy → optional alternatives → optional parameters → optional intuition) is the **default** archetype this skill proposes. Most lectures will not need all six slots; the maintainer overrides per topic.

## Structural model

The structural model is also delegated to the eval skill (§"Structural model of a course lecture"). In short: every refactored lecture has three buckets — **mandatory**, **optional / career-track**, **AI fluency** — and `goals_NN.md` surfaces the split in two places: under Learning Goals and under Files. The outline this skill produces enforces that split from day one.

## Inputs

Accept any of:

- A topic name in free text: `"KNN classification"`, `"regression with train/test split"`, `"ensemble methods"`.
- A lecture number with topic: `"lecture 11 — regression and train/test split"`.
- A path to an existing lecture to refactor: `"lectures_07_13_pandas_plots_scikit/lecture_11_regression_train_test_split/"`.
- A lecture number alone (`"11"`) only if it resolves to a pending-refactor lecture in `docs/Lectures_outline.md` — read the outline doc to recover the topic.

If the lecture number is missing and not derivable, ask the maintainer to pick one. If the number could collide with an existing refactored lecture, ask whether the request is a re-outline (replace) or a fresh slot (new number). Never guess slot numbers.

Optional maintainer seeds the skill will use if provided (and only if provided):

- Prerequisites from prior lectures (concept names) — used in Phase 1 to verify the dependency chain.
- Industry-use *domains* (e.g., "retail", "ops"). The skill records the domain as a slot but does not invent a named example.
- A target presentation length when the maintainer wants something other than 2–2.5 h.

## Boundaries

- **Read-only against `lectures_*/`.** The skill does not edit any lecture material. It does not create the lecture folder or empty notebook stubs — that belongs to `create-improve-lecture`.
- **Writes only to** `.claude/uoa-py-course-lecture-outlines/`. Create the directory if missing. Never write inside the lecture folder, never write inside `docs/`.
- **No content.** No code snippets, no specific datasets, no named companies, no concrete industry-use sentences, no example exercise prompts. The outline declares *slots* and *commitments*; `create-improve-lecture` fills them. Violating this rule produces plausible-but-shallow material that looks finished and never gets revisited — the dominant failure mode of LLM-generated curricula.
- **References the rubric, never duplicates it.** When the outline needs to make a tier claim, cite the eval skill's rubric category by number and let the eval verify it.
- **Suggests, never modifies, `docs/Lectures_outline.md`.** Emit the proposed update inline in `outline_NN.md` as a markdown patch the maintainer can apply manually.
- **One lecture per invocation.** For a multi-lecture refactor, run the skill once per lecture.
- **Use `course_venv/` for any execution** (currently only the time-budget heuristics, which require nothing beyond the standard library).
- **Never invent prerequisites.** If a goal references prior content, the prior content must exist (verify against the prior lecture's `goals_NN.md`) or be flagged as a Phase 1 finding.

## Procedure

### Phase 1 — Locate & contextualise

1. Resolve the slot:
   - If an existing lecture path was given, walk it; record refactor state (refactored / partial / not refactored).
   - If only a topic + number, locate the parent section (`lectures_01_06_*`, `lectures_07_13_*`, `lectures_14_16_*`) using `docs/Lectures_outline.md`.
2. Read for context, in this order, and note what they say about the topic:
   - `README.md` §"Course structure and pace" and §"Course Outline".
   - `docs/Lectures_outline.md` for the lecture's existing row (if any) and its neighbours.
   - The previous lecture's `goals_NN.md` — record the **prerequisites** the new lecture can assume.
   - The next lecture's `goals_NN.md` if it exists — record the **downstream concepts** the new lecture must hand off to (do not over-cover; that is a category 9 risk).
3. If refactoring an existing lecture, also walk its `reading_material/` and `practice_exercises/` and skim file headings. Do not read full notebook content — the skill is structural.
4. Surface anything found: missing prior-lecture prerequisites, downstream conflicts, unfilled rows in `Lectures_outline.md`.

### Phase 2 — Topic decomposition

Propose a notebook breakdown. Use the Lecture-09 archetype as the **default starting pattern**, then prune:

| Slot | Letter | Bucket (default) | Always required? |
| --- | --- | --- | --- |
| Core walkthrough | `lec_NNa` | mandatory | yes |
| Assumptions / limitations | `lec_NNb` | mandatory | yes — the "honest limitations" beat is mandatory per the rubric §calibration |
| Practical / deploy | `lec_NNc` | mandatory | only if topic has a deployable artefact (a model, an API, a dashboard) |
| Alternatives / awareness | `lec_NNd` | optional | no |
| Parameter tuning / advanced config | `lec_NNe` | optional | no |
| Intuition / visualisation | `lec_NNf` | optional | no |

Smaller-scope lectures often land on 2–3 notebooks (core + limitations + one optional). Larger lectures may need a 4th mandatory notebook before any optional content. The skill proposes; the maintainer decides.

For each proposed notebook, record:

- **File name** following the convention `lec_NNx_<short_slug>.ipynb`.
- **One-line purpose** (≤120 chars). No content prose.
- **Bucket**: mandatory | optional | (AI fluency lives in its own file, not a notebook).
- **Goals it covers** (placeholder — Phase 3 fills the IDs).
- **Dependency**: which prior notebook (in this lecture or a prior lecture) it builds on.

### Phase 3 — Goals & exercises (UbD Stage 1 + 2 first)

Backwards-design order: goals → assessment → content. Phase 2's notebook list is provisional until this phase; if a goal has no exercise and no notebook, it is not a goal yet — it is a wish.

**Required goals.** At least 5. Each one must:

- Use a **student-action verb**: `implement`, `compute`, `compare`, `interpret`, `refactor`, `debug`, `predict`, `name`, `build`, `deploy`, `tune`, `select`, `evaluate`, `visualise`. Bloom-revised, observable.
- Forbid aspirational verbs in the required block: `understand`, `know`, `appreciate`, `be familiar with`, `be aware of`, `learn about`. The rule of thumb: *"If a TA can't tell from the notebook whether the student did it, the verb is wrong."*
- Map to one or more files in Phase 2's list.
- Get a stable id (`G1`, `G2`, …) for the back-reference table.

**Optional / career-track goals.** Aspirational verbs are tolerated here; the bar is "the student has a pointer for further reading", not "the student can do X". Each one maps to an optional file or to an optional/stretch exercise.

**AI fluency goals.** Listed separately under an "AI Fluency" sub-heading (eval Phase 1 looks for this). They map to the planned `read_agents_<topic>.md`.

**Exercise plan.** The output must include an `exercise → goal_id` back-reference table. Constraints:

- Every required goal has at least one required exercise. No exception. The eval skill scores this directly under category 4.
- Optional/stretch exercises map to optional goals.
- Exercises must use only concepts the lecture's planned mandatory notebooks teach. If an exercise depends on `lec_NNd` and `lec_NNd` is in the optional bucket, the exercise must be tagged stretch — otherwise it is the lecture-09 cat-4 trap (Exercise 4.2 needed DBSCAN that `lec_09d` did not teach).
- Note difficulty: `trivial` (≤15 min), `realistic` (≤45 min), `stretch` (≤90 min). Defaults to realistic if unmarked.

### Phase 4 — AI fluency reading plan

Plan a `read_agents_<topic>.md` file. The skill outlines its structure only; `create-improve-lecture` writes the prose.

Use Anthropic's 4Ds framework (Delegation / Description / Discernment / Diligence) as the backbone — it is explicitly cited by `README.md` and the AI Fluency for Educators course. For each D, list the **topic-specific failure modes** an assistant exhibits when applied to this lecture's content. Examples of the *kind* of failure mode (not concrete examples — those belong to `create-improve-lecture`):

- *Delegation* — what the student should and should not hand off to an assistant on this topic.
- *Description* — what context the assistant needs to give a useful answer for this topic (data shape? domain constraints? model assumptions?).
- *Discernment* — what an assistant typically gets wrong on this topic and how to spot it.
- *Diligence* — what the student must verify by hand, every time.

The output records 3–6 bullets per D, all topic-tagged. The actual examples are filled in later. Target length once filled: ≥200 words (the eval skill's threshold for a non-stub).

### Phase 5 — Time budget

Reuse the heuristics from `uoa-py-course-lecture-eval` §Phase 2c — same numbers, same caveats. Apply them per *planned* notebook (no content yet, so the inputs are estimates):

- Reading time (fresh cost): planned word-count estimate ÷ 150 wpm. Use 800–1500 words per notebook unless the maintainer says otherwise.
- Code walk-through (fresh cost): planned cell count × per-cell time. Estimate 8–15 trivial + 8–15 non-trivial cells per mandatory notebook. Trivial = 90 sec, non-trivial = 180 sec.
- Exercises (fresh cost): count × difficulty band (trivial 15 min / realistic 45 min / stretch 90 min). Tag each exercise as *required* (G1–Gn) or *stretch* (O1–On or explicitly stretch).

Compute the four budget lines using the **fixed eval-skill formulas** (post-rubric-update; the eval skill is authoritative):

- **Mandatory student load (at-home, after class)** = mandatory reading + (mandatory walk-through × 0.4). The × 0.4 models at-home re-walk after the student has seen the cells in class (complement of presentation × 0.6). Practice exercises are **not** in this sum — see below.
- **Optional student load** = optional reading + optional walk-through (no multiplier — students hit optional content cold, no in-class preview). Only optional-bucket notebooks declared in `goals_NN.md`'s Optional Files section. Practice exercises are **not** in this sum either.
- **Practice exercise budget** = (count × difficulty band) over all exercises in `practice_exercises/`. Reported as two sub-totals: required exercises (tied to G1–Gn) and stretch exercises (tied to O1–On). **Reported only**, not tier-determining for cat 9, since per the README practice exercises are bonus work ("*Mid-course assignments and practice exercises are optional and are graded only positively*").
- **Presentation time** ≈ **mandatory walk-through (fresh) × 0.6**. Computed strictly over the mandatory bucket. It **excludes** optional notebooks (never walked through in class), AI fluency readings (companion at-home reading), practice exercises (bonus at-home work, never class time), and mandatory markdown reading (read at home; already in *Mandatory student load*). If a particular lecture's teacher walks through markdown or optional content in class, flag it explicitly in the design doc; do not silently inflate the formula.
- **AI Fluency reading time** = reading over `ai-fluency`-bucket files. Reported separately; not in any total.

Compare against targets:

- Presentation: 2–2.5 h (needs work 2.5–3 h, gap >3 h).
- Mandatory student load (lecture content only — readings + at-home walk × 0.4): **1.5–3 h** (needs work 1–1.5 h or 3–4 h, gap >4 h or <1 h).
- Optional / advanced student load (optional notebooks only): **1–3 h** (needs work <1 h or 3–4 h, gap 0 h or >4 h).
- Practice exercise budget: reported only. A reasonable spread is ~2–6 h required + ~0.5–3 h stretch — outside that range is a should-fix on cat 4 (overload or thin coverage), not a cat 9 finding.

If a budget is over, propose **specific** moves to optional in the design doc (e.g., "move planned `lec_NNe` to optional; mandatory drops from 3.4 h → 2.6 h"). Do not silently absorb the overrun.

### Phase 6 — Eval-criteria pre-check

For each of the 9 rubric categories in `uoa-py-course-lecture-eval`, declare:

- **Target tier** the outline can guarantee at the structural level (typically `solid`; rare to claim `strong` from an outline alone).
- **Outline guarantees** — what the outline itself locks in (e.g., "Required+Optional split present"; "every file mapped to a goal"; "exercise→goal back-reference table").
- **Create-improve commitments** — what the next skill must deliver to land the tier (e.g., "lec_NNa cell 0 includes a 1-paragraph hook"; "≥3 industry uses named in lec_NNa cell 0"; "read_agents_<topic>.md ≥200 words").

Categories 5 and 7 are content-bound — outline cannot guarantee them, only reserve the slots and record the commitments. Category 6 is partially structural (file declared in goals; ≥200 words target) and partially content (currency, specificity).

### Phase 7 — Write outputs

Both files go to `.claude/uoa-py-course-lecture-outlines/lecture_<NN>_<short_slug>/`. Create the directory if missing.

- `goals_<NN>.md` — student-facing draft. Structural skeleton only. The maintainer copies it into the lecture folder when promoting.
- `outline_<NN>.md` — internal design doc. Stays in `.claude/`.

Print both paths and a one-line summary ("composite outline tier-floor: solid; bottlenecks at create-improve time: cat 5, cat 7, cat 6 currency") to the user.

If a file with the same name already exists at the target path, overwrite it after Read'ing it (do not silently append). The outline is regenerable.

## Output templates

### Template — `goals_<NN>.md` (student-facing draft)

```markdown
# Lecture <NN>: <Topic title>

## Learning Goals

### Required

- <action verb> <observable behaviour> <on what>.   <!-- G1 -->
- <action verb> <observable behaviour> <on what>.   <!-- G2 -->
- ...
- <action verb> <observable behaviour> <on what>.   <!-- G5 (minimum) -->

### Optional / Career track

- <aspirational or extension goal>.                  <!-- O1 -->
- ...

### AI Fluency

- <action verb> tied to using an AI assistant on this topic.   <!-- A1 -->
- ...

## Files

### Required

- `lec_<NN>a_<slug>.ipynb` — <one-line purpose, ≤120 chars>.
- `lec_<NN>b_<slug>.ipynb` — <one-line purpose>.
- ...

### Optional / Further reading

- `lec_<NN>x_<slug>.ipynb` — <one-line purpose; one phrase on why it is optional>.
- ...

### AI Fluency

- `read_agents_<topic_slug>.md` — using AI assistants for <one-phrase scope: e.g. picking K, debugging a pipeline, deploying>.

## Practice

- `practice_exercises/lec_<NN>_exercises.ipynb` — covers required goals G1–Gn with realistic exercises, plus stretch exercises tied to optional goals.
- `practice_exercises/lec_<NN>_exercises_solutions.ipynb` — runnable solutions for all required exercises; partial for stretch.
```

The HTML-comment goal IDs (`<!-- G1 -->`) are intentional: they survive in raw markdown without rendering, and `create-improve-lecture` and `uoa-py-course-lecture-eval` can grep them to verify the back-reference table is still in sync after edits.

### Template — `outline_<NN>.md` (internal design doc)

```markdown
# Lecture <NN> outline — <Topic title>

**Date:** <YYYY-MM-DD>
**Slot:** <parent section>, lecture <NN>
**Refactor state:** new | refactor of `<existing path>`
**Status:** draft
**Author:** Claude Code (skill: uoa-py-course-lecture-outline)

## Context

- Prior lecture (<NN-1>): <topic> — prerequisites this lecture assumes: <bullet list>.
- Next lecture (<NN+1>): <topic, if known> — downstream concepts this lecture must hand off cleanly to: <bullet list>.
- Existing row in `docs/Lectures_outline.md`: <quote, or "none yet">.

## Goals

### Required

| ID | Goal (action verb) | Covered by |
| --- | --- | --- |
| G1 | <verb + observable> | lec_<NN>a |
| G2 | ... | ... |

### Optional / Career track

| ID | Goal | Covered by |
| --- | --- | --- |
| O1 | ... | lec_<NN>d |

### AI Fluency

| ID | Goal | Covered by |
| --- | --- | --- |
| A1 | ... | read_agents_<topic>.md |

## Non-goals

(≤3 bullets — what this lecture deliberately does not cover. Forces explicit scope. Example: "deep dive into Lloyd's algorithm proof — covered in optional reading only, no exercise".)

- ...

## Notebook decomposition

| File | Bucket | Purpose | Goals covered | Builds on |
| --- | --- | --- | --- | --- |
| `lec_<NN>a_<slug>.ipynb` | mandatory | <one-line> | G1, G2 | prior lecture <NN-1> |
| `lec_<NN>b_<slug>.ipynb` | mandatory | <one-line> | G3 | lec_<NN>a |
| ... | ... | ... | ... | ... |

## Exercise plan

| Exercise | Tier | Maps to goal | Concepts taught in |
| --- | --- | --- | --- |
| 1.1 | required, trivial | G1 | lec_<NN>a |
| 1.2 | required, realistic | G1, G2 | lec_<NN>a, lec_<NN>b |
| 4.1 | stretch | O1 | lec_<NN>d (optional) |
| ... | ... | ... | ... |

Constraint check: every required goal has ≥1 required exercise; no required exercise depends on an optional notebook. <state OK or list violations>.

## AI fluency reading plan (`read_agents_<topic>.md`)

Backbone: Anthropic 4Ds. Each D gets 3–6 bullets pointing at topic-specific failure modes; the actual prose lands in `create-improve-lecture`.

- **Delegation** — what to hand off to the assistant on <topic>: <bullet, bullet>.
- **Description** — what context the assistant needs: <bullet, bullet>.
- **Discernment** — typical assistant errors on <topic>: <bullet, bullet>.
- **Diligence** — what the student verifies by hand every time: <bullet, bullet>.

Target length once filled: ≥200 words. Concrete tasks ("try this with an assistant: …") count toward the rubric §6 strong tier.

## Time budget

| Component | Mandatory | Optional | AI Fluency |
| --- | --- | --- | --- |
| Reading time | <N.N> h | <N.N> h | <N.N> h |
| Code walk-through (fresh) | <N.N> h | <N.N> h | — |
| Code walk-through (at-home, × 0.4) | <N.N> h | (no multiplier — students hit optional cold) | — |
| **Total student load (at-home)** | **<N.N> h** (target 1.5–3 h, gap >4 h or <1 h) | **<N.N> h** (target 1–3 h, gap if 0 or >4 h) | <N.N> h (reported only) |

Estimated presentation time: <N.N> h (target 2–2.5 h, needs work 2.5–3 h, gap >3 h). **Mandatory walk-through (fresh) × 0.6**. Excludes optional-bucket notebooks, AI fluency readings, practice exercises, and markdown reading in mandatory notebooks (read at home). If the teacher plans to walk through any of these in class, flag the under-estimate explicitly.

**Practice exercise budget** (reported only; not tier-determining for cat 9 — exercises are bonus work per the README):

- Required exercises (tied to G1–Gn): <N> exercises, ~<N.N> h.
- Stretch exercises (tied to O1–On or marked stretch): <N> exercises, ~<N.N> h.
- Total: ~<N.N> h.

If over budget: <list specific moves; expected post-move totals>.

## Eval-criteria pre-check

| # | Category (cf. `uoa-py-course-lecture-eval`) | Target tier | Outline guarantees | `create-improve-lecture` commitments |
| - | --- | --- | --- | --- |
| 1 | Learning goals | solid | Required + Optional split; ≥5 required goals with action verbs; goal IDs assigned | Aspirational verbs stay out of the required block when content lands |
| 2 | Coverage | solid | Files split (Required + Optional + AI Fluency); every planned file mapped to ≥1 goal; no unaccounted file | Every file written matches the planned slot; nothing extra |
| 3 | Pedagogical scaffolding | (deferred) | Notebook order respects dependency table | Each new concept introduced via worked example before reuse |
| 4 | Exercises | solid | Exercise→goal back-reference table; every required goal covered; no required exercise depends on optional content | Solutions notebook runs cleanly under `requirements.txt` |
| 5 | Code, data & references | (deferred) | — | All notebooks execute under `course_venv`; 0 broken hyperlinks (parser-extracted, GET-with-UA verified) |
| 6 | AI-fluency thread | partial | `read_agents_<topic>.md` declared in goals; 4D structure planned | Prose ≥200 words; topic-specific examples; concrete "try this" tasks |
| 7 | Real-world relevance | (deferred) | Hook / industry-uses / limitations / career-framing slots reserved in lec_<NN>a | Maintainer fills the slots; ≥3 named industry uses; ≥1 career framing |
| 8 | Decomposition | solid | One topic per notebook; letter ordering reflects dependency | No notebook accumulates a second topic during writing |
| 9 | Volume & time budget | solid | Mandatory (lecture content only, reading + walk × 0.4) 1.5–3 h, optional notebooks 1–3 h, presentation (mandatory walk × 0.6) 2–2.5 h per Phase 5. Practice exercise budget reported only. | Walk-through pace at write-time matches the budget; teacher does not silently extend in-class time over markdown or optional content |

Floor at content time: composite **solid**. Reaching `strong` requires the create-improve commitments to land cleanly.

## Suggested patch to `docs/Lectures_outline.md`

(Markdown patch the maintainer can apply manually. The skill does not edit `docs/`.)

> Replace the existing row for Lecture <NN> with:
>
> ```markdown
> - **Lecture <NN> — <Topic title>.** <One-paragraph summary mirroring the per-section style of `Lectures_outline.md` — list the required notebooks by name with a phrase each; flag the optional bucket; close with the AI fluency file name.>
> ```

If the lecture's row in the AI-Agents table at the top of `Lectures_outline.md` is empty, also propose:

> Add row for Lecture <NN>: `read_agents_<topic_slug>.md` covering <one phrase>.

## Open decisions for the maintainer

(Things the skill could not resolve without judgement. Listed so they don't get lost.)

- ...
```

## Tone

Direct, concrete, no flattery. The outline is a planning artefact, not a pitch document. If the skill cannot produce a defensible answer for a section (e.g., the topic is too vague to bucket goals), say so in that section's body rather than padding with generic placeholders. The maintainer would rather see one honest "needs maintainer input" than three plausible-but-shallow bullets.
