---
name: uoa-py-course-update-lecture-post-teaching
description: Use this skill to apply post-teaching corrections to a lecture in this course repo after the maintainer has actually taught it and observed failures, missed beats, student confusion, or pedagogical intent that did not survive an earlier `uoa-py-course-create-excellent-lecture` run. The trigger is *class-observed pain points*, not rubric gaps. Trigger on requests like "update lecture NN after teaching it", "lecture NN missed the intent of the draft, fix it", "students got stuck on X in lecture NN, add a section", "the original draft for lecture NN had Y workflow and the refactored version dropped it — restore it", "the live class showed Z is broken in lecture NN", or when the maintainer supplies live-teaching notes / a list of student questions / an overlooked design artefact and asks for the fixes to land. Workflow: (1) recover the original intent from outline, `goals_<NN>.md`, and any `*_draft*.ipynb` or hand-built notebook in the lecture folder; (2) diff intent vs as-shipped lecture; (3) propose a minimal-surgery fix; (4) delegate the content edits to `uoa-py-course-create-excellent-lecture` in **update mode**; (5) re-run `uoa-py-course-lecture-eval` to confirm no regression; (6) patch the lessons learned back into `uoa-py-course-create-excellent-lecture` so the same failure does not repeat. Do NOT use it to: improve a lecture against the eval rubric without a class-observed failure (use `uoa-py-course-create-excellent-lecture` directly); plan a lecture from scratch (use `uoa-py-course-lecture-outline`); evaluate or score a lecture (use `uoa-py-course-lecture-eval`); grade student work; or apply a maintainer-named change that does not stem from teaching observations (use `uoa-py-course-create-excellent-lecture`'s update mode directly — this skill exists specifically for the *diagnostic* step of figuring out what the failure was, before that named change can be formulated). If the maintainer already knows exactly which section to add and why, route to `uoa-py-course-create-excellent-lecture` instead.
---

# Update lecture post-teaching

You are taking a lecture that has already been taught at least once, where the live class surfaced failures the eval rubric did not catch, and producing a minimal-surgery fix that (a) restores any lost pedagogical intent, (b) closes any concrete pain points the maintainer observed, and (c) feeds the failure mode back into `uoa-py-course-create-excellent-lecture` so the next lecture does not repeat it.

The skill is **diagnostic-heavy and implementation-light**. Most of the implementation is delegated to `uoa-py-course-create-excellent-lecture`'s update mode. What this skill owns is:

1. Recovering the **original intent** — what the lecture was *meant* to teach, from artefacts older than the as-shipped notebooks.
2. Building an **intent / as-shipped diff** the maintainer can read in one sitting.
3. Deciding the **minimal-surgery fix** — which sections to add, which goals to renumber, which retirements need a written rationale.
4. Closing the **feedback loop** into the generator skill so the failure does not repeat.

## Boundaries

- **Only invoke after the lecture has been taught at least once.** If the maintainer is asking for changes pre-teaching, route to `uoa-py-course-create-excellent-lecture` directly. The whole value of this skill is the post-teaching feedback signal — without it there is no diagnostic step to do.
- **One lecture per invocation.** No batch updates across lectures.
- **Never auto-edit the lecture folder.** Every content change is delegated to `uoa-py-course-create-excellent-lecture` in update mode with a precise change brief; this skill does not perform notebook surgery itself.
- **Capture the lesson before exiting.** Phase 6 patches `uoa-py-course-create-excellent-lecture`'s `SKILL.md` with a new boundary rule, a new procedural step, or a new Pattern that would have caught this failure. Without this step the same failure recurs on the next lecture. **The patch is non-negotiable** — if the maintainer says "the failure mode is too one-off to codify", capture it as a Pattern entry with that caveat rather than skipping the patch entirely.
- **Read-only against `docs/Lectures_outline.md`, `README.md`, `CLAUDE.md`.** Emit suggested patches inline; never edit those files directly. (Same boundary as the create skill.)
- **Use `course_venv/` for any execution.** Same repo-root-relative interpreter paths as the create skill: `course_venv/bin/python` and `.../course_venv/bin/jupyter`.

## Inputs

Accept any combination of:

- **A path / lecture number** (required). The lecture to update.
- **Pain points** (required, free-form). The maintainer's observations from teaching: what didn't land, where students got stuck, what they expected to teach but the as-shipped lecture didn't deliver.
- **Overlooked design artefacts** (optional but common). A `*_draft*.ipynb` still sitting in the lecture folder, an outline note, a paragraph from `docs/Lectures_outline.md`, a Slack message, a paper PDF — anything that captures intent older than the as-shipped notebooks.

If the maintainer's request is one-line ("update lecture 11"), ask for at least the pain-points input before doing any work. Without it, the skill is operating blind.

## Procedure

### Phase 0 — Intake

1. Resolve the lecture folder (same convention as the create skill: path or `NN` → glob `lectures_*/lecture_NN_*/`).
2. Capture the maintainer's pain points verbatim (1–5 sentences). Number them P1, P2, … so subsequent phases can reference them directly.
3. Inventory the lecture folder. Specifically:
   - Every `*_draft*.ipynb` or hand-built notebook at the lecture root (i.e., **not** moved into `reading_material/` yet — these are the strongest "older intent" signals).
   - Every notebook inside `reading_material/` — these are the as-shipped artefacts.
   - The current `reading_material/goals_<NN>.md`.
   - Any outline document at `.claude/uoa-py-course-lecture-outlines/lecture_<NN>_*/`.
4. Surface a one-line summary of each artefact to the maintainer so they can confirm the inventory is complete (sometimes there is a `notes.md` in a sibling directory the skill would not find on its own).

### Phase 1 — Intent recovery

For each hand-built artefact (especially `*_draft*.ipynb`), extract the **distinctive intent** — the methodology, library choices, worked progression, or scientific method that artefact uniquely carries. The extraction technique is:

1. Convert the notebook to markdown for fast reading: `jupyter nbconvert --to markdown --stdout <file> | head -800`. For very long notebooks, also dump a cell outline (`python -c "import json; for i, c in enumerate(json.load(open(...))['cells']): print(i, c['cell_type'], (...))"`).
2. Identify the file's **distinctive contribution** — the *one thing* it taught that the rest of the lecture does not. Examples:
   - "Hand-built backward elimination using statsmodels OLS summary table — drop highest-p feature, refit, iterate."
   - "Three-API comparison (statsmodels / pingouin / sklearn) on the same dataset with a 'when to reach for which' table."
   - "Worked progression from underfit → just-right → overfit on a 1D polynomial with annotated visual."
3. Map each distinctive contribution to a goal in the current `goals_<NN>.md`. If no goal covers it, the contribution was dropped — that is the intent-loss to recover.

In parallel, read the outline (if present) and `docs/Lectures_outline.md`'s row for this lecture. Note any commitment in either document that the as-shipped lecture does not satisfy.

### Phase 2 — Intent / as-shipped diff

Produce a single-page synthesis the maintainer can read in two minutes. Format:

| Item | Origin | Status in as-shipped lecture | Decision |
| --- | --- | --- | --- |
| (e.g.) Backward feature elimination via statsmodels OLS metrics | `lec_11b_multiple_lin_regr_draft.ipynb` §"Remove non statistically significant factors" | **Missing** — statsmodels reduced to a one-sentence footnote in `lec_11c §E`. | Restore as a new `§F` in `lec_11c` + add new goal G4. |
| (e.g.) sklearn-native feature selection | (none — the maintainer's pain point P2 requested this) | **Missing** — never planned. | Add inside the same new `§F` (`SequentialFeatureSelector` + `RFE`). |
| (e.g.) Coefficient interpretation pitfalls | `lec_11d_advanced_linear_model_coeff_interpretation.ipynb` | **Present** — goal G6 cites it. | No action. |

The diff is conversational, not a deliverable. Keep it to ≤30 lines.

### Phase 3 — Minimal-surgery plan

Translate the diff into a change brief the create skill can act on. The brief must specify:

- **Affected files** — one or two notebooks, plus `goals_<NN>.md`. Update mode tolerates 1–3 files; if your brief touches more, the plan is too big — split it.
- **Section-level edits** — name the new section (e.g., "§F. Choosing features scientifically"), name the cells to add, name the cells to retire or rewrite.
- **Goal changes** — which goals to add, which to renumber, which file descriptions in `goals_<NN>.md` to update.
- **Predicted rubric side-effects** — adding a new goal needs a tied exercise (cat 4); adding a new section bumps mandatory load (cat 9); renaming a notebook breaks cross-references (cat 1). The create skill's "side-effect awareness" pattern lists these; surface the relevant ones here so the create skill can plan around them.

Ask the maintainer for explicit go-ahead before delegating. If the maintainer wants to adjust the brief (split into smaller passes, swap a "restore" for a "retire with rationale", change a goal label), incorporate the changes and re-confirm.

### Phase 4 — Delegate to `uoa-py-course-create-excellent-lecture` in update mode

Invoke the create skill with the approved change brief. Conventions:

- Pass the change brief verbatim — do not paraphrase. The create skill is the implementer; ambiguity in the brief produces drift in the implementation.
- Specify **update mode** (the create skill auto-detects, but be explicit: "this is an update, the lecture's composite is already strong, only the named files should change").
- If the brief touches a notebook whose history matters (e.g., the renamed-from-`*_draft*.ipynb` file), tell the create skill that history must be preserved — content edits via `NotebookEdit` or a single Python script, **never** a `git mv` of a different file onto the existing path.

Wait for the create skill's Phase 7 closing notes. If it returns composite-`strong`, advance. If it returns composite-`solid` with a polish-tier remainder, decide with the maintainer whether to push for `strong` or ship at `solid`. If it returns < `solid`, the brief was wrong — return to Phase 3, refine, re-delegate.

### Phase 5 — Re-evaluate

Run `uoa-py-course-lecture-eval` against the updated lecture. The eval is the canonical proof that the update did not regress any rubric category. Two specific things to check beyond the composite tier:

1. **Cat 4 (exercises ↔ goals).** A new goal without a tied exercise drops cat 4. Confirm the create skill landed both halves.
2. **Cat 1 (goals ↔ content).** Every goal's `*(file §section)*` citation resolves to a real section in the named notebook. After cell-index drift from inserts, citations sometimes point at the wrong heading.

If the eval surfaces a regression, return to Phase 4 with a tightened brief. Do not re-run the full update from Phase 0.

### Phase 6 — Feedback loop into the generator skill

This is the step that distinguishes this skill from `uoa-py-course-create-excellent-lecture`'s update mode. **Do not skip it.**

Ask the question: *would the create skill, run today against the original input, have made the same mistake?* If yes, the create skill needs a defence. The defence takes one of three shapes:

1. **A new boundary rule.** Added to the Boundaries section of `uoa-py-course-create-excellent-lecture/SKILL.md`. Used when the failure was a hard rule the create skill violated (e.g., "preserve hand-built draft intent — never overwrite silently").
2. **A new procedural step.** Added to Phase 0 / Phase 2 / Phase 4 of the create skill. Used when the failure was a step the create skill skipped (e.g., "Hand-built content inventory" as a new Phase 0 step).
3. **A new Pattern.** Added to the "Implementation patterns" section. Used when the failure is best taught by example — quote the broken artefact, quote the fixed artefact, explain the test the skill should have applied (e.g., "Pattern: intent-preservation pass for hand-built drafts").

Write the patch directly into `uoa-py-course-create-excellent-lecture/SKILL.md`. Use the same voice as the existing skill (direct, concrete, named historical incidents). Reference the lecture and date of the failure so future readers can trace it.

If the maintainer pushes back ("this failure is too one-off to codify"), still write a Pattern entry — that one-off observation is exactly what Patterns are for. The bar for skipping the patch entirely is the maintainer being able to articulate *why* the failure is unrepeatable; "I don't think it'll happen again" is not sufficient.

### Phase 7 — Closing notes

Emit (in chat, not as a written file):

- The pain points addressed (P1, P2, …), each marked **resolved** / **partial** / **deferred** with one-line rationale for non-resolved items.
- Files modified (one-line summary each). The brief in Phase 3 should already list these; re-confirm against the actual diff.
- The eval composite tier from Phase 5.
- The lesson captured in Phase 6, named as `[boundary | procedural step | pattern]` and quoted in 2–3 lines.
- A single next-step sentence: typically "commit lecture <NN> + the skill patches together so the diff tells the whole story".

## Implementation patterns

### Pattern: surface every hand-built artefact in Phase 0, even if it looks superseded

When `git status` shows a file like `lec_11b_multiple_lin_regr_draft.ipynb` as untracked at the lecture root *after* a refactor moved a same-name file into `reading_material/`, that orphan draft is a strong signal of intent-loss. The refactor's `git mv` carried the *filename* into `reading_material/`, but the original file content stayed behind and was replaced by skill-generated content under the new name. The maintainer kept the orphan because they could already feel the intent was lost; they had not yet articulated it.

This is the Lecture-11 case verbatim. The defence: in Phase 0 step 3, treat any orphan `*_draft*` at the lecture root as a *required* input to intent recovery, not an optional one.

### Pattern: a maintainer pain point may not name the intent it is trying to recover

Maintainers often describe failures concretely ("students didn't understand why we kept act_math when its p-value was 0.4") without naming the underlying methodology that would have prevented the confusion ("the draft taught backward elimination by p-value; the as-shipped lecture skipped that workflow"). The diagnostic step in Phase 1 is to *map* the concrete pain point to the missing methodology — sometimes the maintainer cannot name it themselves until the diff is on the page.

Do not require the maintainer to articulate the methodology before invoking this skill. The diagnostic is the skill's job.

### Pattern: deliver the fix and the lesson together

The temptation after Phase 5 confirms the fix is to ship and move on. Don't. Phase 6's patch into the generator skill is what makes this skill compounding rather than one-shot. Without it the next lecture has the same probability of the same failure; with it the probability falls.

When pushing the lecture commit and the skill patch, push them together. The git history then tells the whole story: "lecture 11 needed X, the create skill is now defended against the failure that produced the gap."

## Stopping conditions

Stop when **all** of:

1. The pain points listed in Phase 0 are each resolved, partial, or deferred (with rationale).
2. The eval composite tier in Phase 5 is at least `solid` and ideally `strong`.
3. The Phase 6 patch into `uoa-py-course-create-excellent-lecture/SKILL.md` is written.

If any of those is open and the maintainer signals stop, write the Phase 7 closing notes with the open items called out explicitly so the next session can pick up.

## Tone

Direct, concrete, no flattery. The maintainer has just taught the lecture; they know what failed better than the skill does. The skill's job is to listen carefully, recover the intent that was lost, plan the minimum surgery to restore it, and codify the lesson — not to redesign the lecture on the rubric's terms again.

The eval is still the judge. The maintainer's pain points are the prompt. The intent of the original design artefacts is the anchor. The patch into the generator skill is the dividend.
