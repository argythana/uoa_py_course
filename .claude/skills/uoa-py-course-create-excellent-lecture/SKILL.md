---
name: uoa-py-course-create-excellent-lecture
description: Use this skill to drive a single lecture in this course repo from its current state (whatever tier) up to composite `strong` on the 9-category rubric used by `uoa-py-course-lecture-eval`, OR to apply a targeted update / modification to an already-`solid`-or-`strong` lecture (add a section, retire content, rescope, lift content between lectures). Trigger on requests like "improve lecture NN", "bring lecture NN to strong", "fix every gap in lecture NN", "refactor lecture NN to the Lecture 09 template", "make lecture NN as good as lecture 09", "update lecture NN to add X", "lift section X from lecture NN to lecture MM", or when the user supplies an eval report and asks for the fixes to land. Do NOT use it to: evaluate or score a lecture (use `uoa-py-course-lecture-eval`); plan a lecture from scratch without any existing material (use `uoa-py-course-lecture-outline` first, then this skill once the outline is approved); grade student work (use `final_assignment/grade_feedback.prompt.md`); rewrite arbitrary files outside `lectures_*/`; or edit `docs/Lectures_outline.md` directly (the skill emits a suggested patch instead). If the lecture is missing both an eval report and an outline, this skill runs them first; if the user has not yet decided on destructive moves (deletions, renames), this skill asks before touching the lecture folder.
---

# Create excellent lecture

You are taking **one** lecture folder from wherever it is on the rubric (often `gap`) up to composite `strong`. The output is a refactored lecture that re-runs cleanly through `uoa-py-course-lecture-eval` and earns the `strong` tier on every applicable category. The point of the skill is to ship the lecture, not to write a report.

The skill is interactive at the maintainer-decision points (destructive moves, industry-use selection, dataset choices) and autonomous everywhere else. It uses subagents heavily for content authoring (notebooks, the AI-fluency reading) and edits existing notebooks surgically itself.

## Calibration: what "strong" means here

Calibration is delegated. Read `.claude/skills/uoa-py-course-lecture-eval/SKILL.md` §"What a strong lecture looks like" and §"Structural model of a course lecture" before doing anything else. The 9-category rubric there is the contract this skill writes against. If the eval skill's rubric changes, this skill follows.

The benchmark for a refactored lecture is `lectures_07_13_pandas_plots_scikit/lecture_09_clustering_deploy_hf_app/`. Its archetype:

- 3 mandatory notebooks: `lec_NNa` (core walkthrough + cat-7 content), `lec_NNb` (assumptions/limitations), `lec_NNc` (intuition/visualisation OR deploy).
- 2 optional notebooks: `lec_NNd` (parameter tuning), `lec_NNe` (alternatives / forward references).
- 1 AI-fluency reading: `read_agents_<topic>_workflows.md`.
- 2 exercise files: `practice_exercises/lec_NN_exercises.ipynb` + `_solutions.ipynb`.

Most lectures will land near this shape. The maintainer overrides per topic.

## Modes — create vs. update

The skill operates in one of two modes, chosen by the lecture's starting tier and the maintainer's intent:

| Mode | Triggered when | Phases that run | Typical duration |
| --- | --- | --- | --- |
| **Create / refactor** | Composite is `gap` / `needs work` / `solid` and the maintainer wants to bring it up to `strong`. | All phases 0–7. | One session, ~1–2 h with subagents in parallel. |
| **Update** | Composite is already `solid`/`strong` and the maintainer asks for a *specific* change — add a section, lift content between lectures, retire a notebook, rescope an existing notebook. | Phase 0 (lightweight), Phase 2 (scoped questions), Phase 4 (only the affected files), Phase 5–6 (re-execute + re-eval the *affected* notebooks, then a full eval to confirm). | One session, ~15–60 min. |

The two modes share Phases 4–7 but differ in scope. In **update mode** do not re-run the full demolition / refactor — only touch the files the change actually requires, and rely on the final eval (Phase 6) to surface any side-effects (cat 8 falling because a notebook became two-topic, cat 4 falling because a goal lost its exercise, etc.). Side-effects are routine and expected; the eval catches them and iteration handles them.

When in doubt about which mode applies: if the eval composite is already `strong` and the maintainer's request is a discrete change rather than "fix everything", use update mode.

## Inputs

Accept any of:

- A path: `lectures_07_13_pandas_plots_scikit/lecture_10_knn_classifier/`.
- A lecture number: `10`. Resolve by globbing `lectures_*/lecture_NN_*/`.

If the lecture has not been evaluated yet, **run `uoa-py-course-lecture-eval` first** and read its report. If it has not been outlined yet, **run `uoa-py-course-lecture-outline` first** and read both `goals_<NN>.md` and `outline_<NN>.md`.

If the eval composite is already `strong` **and** the maintainer has not asked for a specific change, exit early — the lecture is done. If the maintainer wants polishing (`solid` → `strong`), iterate on the single bottleneck category and re-evaluate; don't run the full refactor pipeline. If the maintainer asks for a *named* change (add a section, retire a notebook, lift content between lectures), enter **update mode** (see §"Modes") regardless of the current tier.

## Boundaries

- **One lecture per invocation.** No batch refactors.
- **Read-only against everything outside the target lecture folder**, except: `.claude/uoa-py-course-lecture-eval-reports/` (writes the new eval report), `.claude/uoa-py-course-lecture-outlines/` (reads outlines), and `course_venv/` (executes notebooks). The skill **never** edits `docs/Lectures_outline.md`, `README.md`, or `CLAUDE.md` — it emits suggested patches inline in chat for the maintainer to apply.
- **Never delete a file without explicit maintainer confirmation** at Phase 2. The skill always asks before destructive moves. Once approved, use `git rm` / `git mv` so history is preserved.
- **Never invent industry-use names, dataset choices, or career-framing sentences** without asking the maintainer. The eval skill's cat-7 rule applies: identify *what is missing*, then ask the maintainer for the named example. Default suggestions (drawn from the lecture's `outline_<NN>.md` if available) are fine; the maintainer confirms.
- **Use `course_venv/` for all execution.** From the repo root: `course_venv/bin/python` and `.../course_venv/bin/jupyter`. Never install packages, never modify the venv, never use a different interpreter.
- **Subagents must verify their own notebooks** via `jupyter nbconvert --to notebook --execute --output /tmp/...` before returning. The subagent's PASS is what the skill trusts; if a subagent reports BLOCKED execution, re-run the verification yourself.
- **No content invention in `read_agents_*.md` or notebooks** beyond what the topic supports. Follow the outline's plan; if the outline is silent on a section, ask the maintainer instead of fabricating.
- **Preserve hand-built draft intent — never overwrite silently.** Any pre-existing notebook in the lecture folder represents pedagogical work the maintainer has done by hand. The skill must not replace its content silently — *especially* not via a `git mv` of a `*_draft*.ipynb` onto a skill-generated file of the same final name, which loses the draft's history in the rename. Concrete signals that a notebook is hand-built (and not a previous skill output to be replaced): (a) the filename contains `draft`, `WIP`, `notes`, or a year suffix; (b) markdown cells contain first-person teacher voice ("Best model I managed to find", "I prefer", "On my PC, not yours"); (c) the notebook uses a library combination the rest of the lecture does not (e.g., statsmodels + pingouin + sklearn side by side when the rest of the lecture is sklearn-only); (d) the notebook walks a worked methodology that is not in the eval-rubric checklist (manual subset iteration with metric comparison, hand-tuned hyperparameter sweep, an econometrics-style summary readout). Before treating any such file as renamed / replaced / retired, surface its **distinctive intent** to the maintainer in ≤2 lines and ask whether to (a) preserve the file as-is, (b) preserve a named subset of cells inside the replacement notebook, or (c) explicitly retire with the rationale captured in the Phase 1 synthesis. This is the failure that produced the Lecture-11 statsmodels feature-selection regression: the `lec_11b_multiple_lin_regr_draft.ipynb` was renamed onto the new `lec_11c_multiple_linear_regression.ipynb` and the draft's hand-built backward-elimination workflow (statsmodels summary table → iterate subsets → "best model I managed to find") was dropped without surfacing. The fix had to be applied in a post-teaching update; the prevention is this rule.
- **Example discipline — match examples to the lecture's exact mode.** A classification lecture's hook + industry-use examples must be classification-flavoured: pre-defined labels, labelled training set, new observations need predictions. Examples that read as clustering ("find similar customers and describe their type") or pure similarity-retrieval ("find K most similar embeddings") add to the very confusion the lecture is trying to remove. The `lec_10a` initial trail-running-shoes hook and the recsys / embedding-retrieval / "similarity baselines" industry-use trio were both rejected on this exact ground — every one of them was algorithmically *KNN* but pedagogically *not classification*. Pick examples where (a) the label set is pre-defined, (b) labels are known for the training population, and (c) the new observation genuinely needs a prediction. If the lecture is a regression lecture, examples need continuous targets; if it is supervised classification, examples need discrete pre-defined classes; if it is unsupervised, examples need an *absence* of labels.
- **Scope discipline — do not jump ahead.** Before any new notebook uses a concept, verify that concept was taught in this lecture or an earlier one (or is an explicit prerequisite from the previous lecture's `goals_<NN-1>.md`). Two specific failure modes from past iterations:
  - *Using future-lecture concepts.* The initial `lec_10e` fitted logistic regression / decision trees / SVM with worked code, even though lectures 11 and 12 had not introduced those classifiers yet. That worked content had to be moved to lecture 13. A theory-only forward-reference notebook (à la `lec_09f`) is the right shape for "alternatives" content in a teaching lecture — name the algorithms, give one-line "when to prefer" guidance, link to scikit-learn docs, defer the worked code to the lecture that owns it.
  - *Using prerequisites without teaching them.* The initial `lec_10a` did `fit/predict` while calling `train_test_split` only in a stubbed cell — the train/test concept was used implicitly but never taught. The fix was to retrofit an extensive `§B1.3` section that introduces the split as a first-class concept (with worked code, with the two-way / three-way split contrast, with the leakage pitfall, with the lazy-vs-evaluation argument). The rule: if a concept appears as `fit(X_train, ...)` in any cell of a notebook in this lecture, the concept must be *introduced* somewhere upstream of that cell — either in an earlier lecture's `goals_<NN-1>.md` or in this lecture's text.
- **Cross-check against `docs/Lectures_outline.md`.** That file is the course's index. Read it during Phase 0. If a concept this lecture wants to use is already owned by another lecture per the outline, defer to a forward-reference. If a concept this lecture wants to teach overlaps with another lecture's listed scope, flag the conflict to the maintainer before authoring. The outline is the anchor for "what's taught where"; this skill cross-checks against it but does not edit it.

## Refactor-state awareness

Lectures arrive in three states. The skill adapts:

| State | What to do |
| --- | --- |
| **Refactored, `gap`/`needs-work`/`solid`** | Skip Phase 3 (folder split already exists). Go straight to Phase 4 (content). |
| **Not refactored** (lectures 10–13, 14–16) | Run all phases. Phase 3 creates `reading_material/` + `practice_exercises/` and uses `git mv` to move surviving files. |
| **Refactored, already `strong`** | Exit early. The skill has nothing to do. |

## Procedure

### Phase 0 — Pre-flight

1. Resolve the target lecture folder. Determine the mode: **create / refactor** vs **update** (see §"Modes").
2. Check whether an eval report exists at `.claude/uoa-py-course-lecture-eval-reports/<lecture_folder_name>_<today>.md`. If absent, **run `uoa-py-course-lecture-eval`** (see its SKILL.md) and read the report. If the eval composite is already `strong` *and* the maintainer has not asked for a specific change, exit.
3. Check whether an outline exists at `.claude/uoa-py-course-lecture-outlines/lecture_<NN>_*/`. If absent in create mode, **run `uoa-py-course-lecture-outline`** and read both `goals_<NN>.md` (the student-facing draft) and `outline_<NN>.md` (the design doc). In update mode, the outline is helpful but not required — the existing `goals_<NN>.md` in the lecture's `reading_material/` is the authoritative goal list to update against.
4. **Hand-built content inventory.** List every notebook in the lecture folder (recursively, including the root and any `reading_material/` subdir if already refactored). For each, classify it:
   - **Skill-generated** — produced by a previous run of this skill; safe to replace if the eval/outline demands.
   - **Hand-built** — authored by the maintainer outside the skill. Signals: `draft` / `WIP` / `notes` / year in the filename; first-person teacher voice in markdown cells; library combinations the rest of the lecture does not use; a worked methodology not in the eval-rubric checklist.
   For every **hand-built** notebook, do a fast extraction (`jupyter nbconvert --to markdown --stdout <file> | head -300` and a `python -c "import json; ..."` cell-by-cell outline) and summarise its **distinctive intent** in ≤2 lines: the scientific method it teaches, the workflow it walks, the library choices it makes. This summary is an *input* to Phase 2's destructive-moves decision — every hand-built notebook gets its own preserve / partial-preserve / retire question, regardless of what the eval says about its rubric performance. The eval scores against the rubric; the maintainer's hand-built intent is not always rubric-legible (statsmodels feature selection scores poorly on cat-7 "industry uses" while being central to the lecture's intent). The rubric is necessary, not sufficient.
5. **Read `docs/Lectures_outline.md`.** That file is the course's index. Note:
   - The target lecture's row (often a one-line stub in the "pending refactor" block — that is expected; the outline grows as lectures land).
   - The previous lecture's (`NN-1`) row — what concepts can this lecture assume as already taught.
   - The next lecture's (`NN+1`) row — what concepts must this lecture *not* pre-empt.
   - The AI-Agents table at the top — what `read_agents_*.md` files have already been declared.
   Use this index throughout the rest of the procedure: any time the new content uses a concept, decide whether the concept is taught earlier (assume it, reference it), taught here (own it, add it to goals), or taught later (forward-reference it, do not duplicate the worked example).
6. Sanity-check: the eval's must-fix findings should align with the outline's create-improve commitments (in create mode), or the maintainer's stated change (in update mode). If the eval and the maintainer's intent diverge significantly, flag it and pause for direction.

### Phase 1 — Gap synthesis (or delta synthesis in update mode)

In **create mode**, read both artefacts and present the maintainer with a single synthesised view:

- Current composite tier and per-category tier breakdown (from the eval).
- Target floor and what the outline locks in structurally.
- **The path** from current → strong, as a sequenced list of concrete sub-tasks. Mirror the structure used in the Lecture 10 reference: demolition → structural refactor → goals rewrite → content additions to existing notebooks → new notebooks → AI-fluency reading → exercises + solutions → optional notebooks → re-evaluation.
- Estimate which sub-tasks need maintainer input (destructive moves, dataset selection, industry-use names) vs. which the skill can do autonomously.

In **update mode**, the synthesis is a *delta*, not a gap:

- What the maintainer asked to change (one sentence).
- Which files are affected (typically 1–3, including `goals_<NN>.md`).
- Predicted side-effects on the rubric — e.g. "adding a new optional notebook bumps optional load by ~0.3 h; declaring a new goal will fail cat 4 unless we also add a tied exercise; renaming a notebook means cross-references in other notebooks need updating."
- Any concept the change introduces or removes — cross-check against `docs/Lectures_outline.md` (Phase 0 step 4). If the change uses a concept not yet taught, surface it: the maintainer either teaches it here (adds material + goal) or avoids it.

Output is a short summary in chat (≤30 lines). Do not write this synthesis to disk — it is conversational, not an artefact.

### Phase 2 — Maintainer decisions (interactive)

Before touching the lecture folder, ask the maintainer the load-bearing decisions. Use **AskUserQuestion** with concrete options. Typical decisions:

1. **Destructive moves.** List every file the eval/outline recommends deleting or merging. For each: name the file, name the reason (duplicate / stale / replaced by new file X), and ask for confirmation. *Do not bundle multiple unrelated deletions into one question* — each deletion is a separate decision unless they share a single rationale.
2. **Hand-built draft disposition.** For every notebook classified **hand-built** in Phase 0 step 4, ask a *separate* question with three options: (a) **Preserve as-is** (keep the file under its current name; the skill works around it). (b) **Preserve a named subset of cells inside the replacement notebook** (the skill quotes the distinctive cells and asks the maintainer to confirm which ones must survive into the new file; common when the hand-built file walks a methodology that should become a new `§F` / `§G` section in the refactored notebook). (c) **Retire with rationale** (the maintainer is happy to drop the content; the rationale is captured in the Phase 1 synthesis so future skill runs can see why). The default suggestion is (b) when the hand-built file's distinctive intent maps to a goal in `goals_<NN>.md`; otherwise (a). Never default to (c).
3. **Notebook bucket boundary.** If the outline flagged a notebook as borderline (mandatory vs optional), surface it. Demoting a notebook to optional drops the mandatory load and the presentation time; demoting too much breaks cat 9 from the other side.
4. **Dataset choices for new content.** If new notebooks introduce a dataset that isn't already in the repo, surface the candidates. Defaults from the outline are fine starting points. Prefer datasets the course already uses (continuity) over novel ones (over-engineering).
5. **Industry-use trio for the cat-7 hook.** The eval rubric requires ≥3 named industry uses in `lec_NNa`. Suggest three drawn from the outline's recommendations; let the maintainer override. **Apply the example-discipline boundary** (§"Boundaries"): every example must match the lecture's exact mode (classification → predefined-label classification examples; clustering → unlabelled grouping examples; regression → continuous-target examples). If a candidate example reads as the wrong mode, replace it with a maintainer-confirmed alternative. Show the maintainer the explicit test for an example: *(a) are the labels pre-defined?* *(b) are labels known for the training population?* *(c) does the new observation genuinely need a prediction?* All three must be yes for a classification example.
6. **Checkpoint cadence.** Ask whether the maintainer wants to review after each content piece, after the mandatory core, or push through to the end. The default is "push through, eval at end" — fastest path. For high-stakes lectures (e.g., final assignment-adjacent) the safer "review each piece" cadence is reasonable.
7. **Scope cross-check** (driven by Phase 0 step 5). If the planned content uses any concept that is NOT taught in this lecture or upstream, surface it as a question: "*The plan uses `train_test_split` / `GridSearchCV` / cross-validation / etc. Lecture <NN> does not currently teach this. Three options: (a) teach the concept here (add a section + a goal); (b) defer the use to the lecture that owns the concept; (c) drop the affected content.*" Default to (a) when the concept is foundational (the train/test split is one such case); default to (b) when the concept is downstream-owned (e.g., cross-validation belongs to lecture 13).

Record the answers. They drive every subsequent phase.

### Phase 3 — Mechanical refactor

Only runs if the lecture is not yet refactored. All operations are reversible via git.

1. **Create subfolders.** `mkdir -p reading_material/ practice_exercises/` inside the lecture folder.
2. **Destructive moves (now authorised).** For each confirmed deletion, `git rm <path>`. For each rename, `git mv <old> <new>`. Never use plain `rm` — history matters.
3. **Move surviving notebooks** into `reading_material/` using `git mv`. If the outline proposed a renaming (e.g., `lec_10a_knn.ipynb` → `lec_10a_knn_classification.ipynb` to match the `lec_NNx_topic_action.ipynb` convention), apply the rename in the same `git mv`.
4. **Promote `goals_<NN>.md`** from `.claude/uoa-py-course-lecture-outlines/lecture_<NN>_*/goals_<NN>.md` into `reading_material/goals_<NN>.md`. Use `Write` (this is a fresh file inside the lecture folder, not a git move).

No content authoring happens in this phase. Just structure.

### Phase 4 — Content authoring (parallel)

This is the bulk of the work. Independent pieces run as concurrent subagents in the background; surgical edits to existing notebooks happen in the foreground.

**Parallelisable subagent tasks** (launch all at once with `run_in_background=true`):

- **New notebook from scratch** — `lec_NNb_<topic>_assumptions_caveats.ipynb` (mandatory limitations beat). Subagent reads the lec_09 equivalent as a template, writes a new notebook covering the failure modes named in `goals_<NN>.md`'s G4/G5 (or topic equivalents), verifies execution under `course_venv`, returns PASS.
- **New notebook from scratch** — `lec_NNd_<topic>_other_parameters.ipynb` (optional bucket).
- **New notebook from scratch** — `lec_NNe_<topic>_vs_other_<things>.ipynb` (optional reference notebook with forward-references).
- **`read_agents_<topic>_workflows.md`** — the AI-fluency reading. Subagent uses the 4Ds framework (Delegation / Description / Discernment / Diligence), targets ≥1500 words for `strong` tier, references current models (Claude / Copilot / ChatGPT family names from CLAUDE.md's "currentDate" frame), includes 3 concrete "try this with an assistant" tasks (one per AI-fluency goal A1, A2, A3).

**Foreground tasks** (surgical, sequential, by main agent):

- **Edit `lec_NNa` for cat-7 + cat-3 fixes.** Dump cell-level structure with `python -c "import json; ..."`. Plan a single Python script that does **all** edits atomically: cell-0 replacement (hook + 3 industry uses + lecture map + forward refs to later notebooks); imports cell adjustments; train/test split implementation if the original was data-leaking; downstream cell updates for the split; deletion of any in-class exercise cells (moved to `practice_exercises/`); appended closing markdown (limitations forwarding to `lec_NNb` + career framing closing the cat-7 arc). Apply the script. Run `jupyter nbconvert --execute` to verify PASS.
- **Build out `lec_NNc`** if the existing version is thin (zero markdown, etc.). Use a Python script to write a fresh notebook with full narrative arc: title + intro, helper function, weights/parameter contrast, K-effect sweep, recap.
- **`lec_NN_exercises.ipynb` + `_solutions.ipynb`** (in `practice_exercises/`). One required exercise per declared required goal G1..Gn (mapped 1:1). One stretch exercise per optional goal O1..On. The exercises notebook uses placeholder code (`# Your code here` comments + no-op executable cells so the notebook runs as a template); the solutions notebook has runnable answers. Both must PASS nbconvert. Author both via a single Python script for consistency.

**Hard authoring rules for any new notebook**:

- Single imports cell at top; one constant `RANDOM_STATE = 42`; seed every `train_test_split`, `make_classification`, `KMeans`, etc. **Do not** add `random_state=42` to estimators that don't have one — `KNeighborsClassifier` and `StandardScaler` have no internal randomness and will raise `TypeError` if given a `random_state`. (This is one of the classic AI-assistant hallucinations flagged in `read_agents_knn_workflows.md` §3.)
- One concept per code cell. Explicit variable names (`X_train_scaled`, not `Xs`).
- Markdown cells short (~150 words max each). Beginner-friendly tone. No emojis (project style).
- **Scannable markdown — bullets and hard line breaks over dense prose.** Beginners and teachers both skim markdown cells in a notebook; a wall of prose is the dominant cause of "I scrolled past the explanation and went straight to the code". The default for any markdown cell longer than ~3 sentences is bullets, not paragraphs. The full rule is documented under the §"Scannable markdown style" pattern below; the short version is: (a) any enumeration of three or more items goes to a bulleted or numbered list (industry-use trio, model-output components, API quirks, "what this notebook covers"); (b) any sentence longer than ~25 words gets broken across visual lines with two trailing spaces + `\n` (markdown's hard-line-break syntax), so each clause renders on its own line; (c) trim ruthlessly — if a paragraph repeats the previous one's point with different wording, delete one of them. The reference example is `lec_11a` cells 0, 4, 7 (the lecture-11 intro and §§1–2). Use that file as the visual template when writing any new markdown cell.
- No in-notebook exercises — they live in `practice_exercises/`.
- All notebooks must pass `nbconvert --execute` under `course_venv` at the 120-s default timeout.
- **Forward-reference, never pre-teach.** If a new notebook needs to point at content that belongs to a later lecture (alternative algorithms, advanced techniques), use a *theory-only* reference structure (à la `lec_09f_other_clustering_algos.ipynb`): minimal or zero worked code, one-paragraph descriptions, "when to prefer over <this lecture's algo>" bullets, scikit-learn doc links, and an explicit "the full worked treatment lives in lecture <MM>" pointer. Worked code that depends on an unknown classifier/regressor is the most reliable way to confuse a beginner — keep it out.

**Pause-point annotations** (cat 9 strong-tier requirement). After the mandatory notebooks are content-complete, identify **2–3 deepening cells per mandatory notebook** — cells whose removal does not break a downstream beat — and prepend a markdown callout cell of the form:

> ⏱ **Skip if running long.** <one-line description of what's below>. <one-line description of where the concept reappears or why it's safe to skip>.

Insert these as new markdown cells before the affected section, not as modifications to existing cells. The callouts give a teacher running over a one-pass way to compress; without them cat 9 stays at `solid` even when the volume budget is in band.

**Normalisation pass after authoring**: run `nbformat.validator.normalize()` on every notebook to set cell IDs and silence the `MissingIDFieldWarning`. Cosmetic but tidy.

### Phase 5 — Execution verification

For each notebook in `reading_material/` and each `_solutions.{py,ipynb}` in `practice_exercises/`:

```
course_venv/bin/jupyter nbconvert \
  --to notebook --execute <notebook> \
  --output /tmp/<basename>_executed.ipynb \
  --ExecutePreprocessor.timeout=180 2>&1 | tail -3
```

Iterate until every notebook returns `Writing X bytes to /tmp/...` (no errors). Common bugs to fix:

- **`NameError` on previously-implicit imports** — the surgical refactor trimmed an unused-looking import (`from matplotlib import style`) but a later cell still references it. Re-add the import.
- **`NameError` on a renamed variable** — the refactor introduced `train_accuracy` / `test_accuracy` but a downstream cell still calls plain `accuracy`. Update every downstream reference.
- **`CellTimeoutError`** at 120 s — usually a `SequentialFeatureSelector` or similar exhaustive search wrapping a slow estimator. Either delete the cell (if the lecture doesn't need it), constrain the search (`n_features_to_select=5`, `n_jobs=-1`), or use a faster surrogate (`SelectKBest`).

Do not skip execution — a notebook that does not execute fails cat 5 regardless of how good the content reads.

### Phase 5.5 — Consistency sweep (before re-evaluating)

Before running the eval, do a one-pass consistency check. The eval catches most of these, but pre-flighting them saves an iteration:

1. **Title alignment.** Lecture title in `goals_<NN>.md` line 1 matches the title in `lec_<NN>a` cell 0. Title in `docs/Lectures_outline.md` (the suggested patch you will emit in Phase 7) matches both.
2. **Goal ↔ content trace.** Every goal in `goals_<NN>.md` has an inline `*(file §section)*` citation, and that section actually exists in the cited notebook. Use `grep` on the goals file to list citations; `grep -n` on each notebook's markdown cells to verify each section heading.
3. **File-description accuracy.** Every entry in `goals_<NN>.md`'s Files section accurately describes the current state of the corresponding notebook. After content edits, file descriptions drift quickly — the most common drift is "industry uses (recsys / retrieval / baseline)" pointing at content that has been replaced. The eval flags this as a should-fix; fixing it before the eval saves a round trip.
4. **Exercise ↔ goal map.** Every required goal G1..Gn has at least one required exercise tagged `[Gx]`. Every optional goal O1..On has at least one stretch exercise tagged `[Ox]`. Adding a new goal without a tied exercise drops cat 4 from `strong` to `solid`.
5. **Cross-notebook references.** Each "see `lec_NNx` for …" pointer in any notebook resolves to a section that actually exists in the named file. After a refactor / rename / lift, these are easy to break.
6. **Outline doc patch preview.** Mentally diff the current lecture state against `docs/Lectures_outline.md`. The patch you will emit in Phase 7 should accurately describe the lecture as it stands now — not as it was before this iteration.
7. **Index integrity.** Any concept the lecture now uses or teaches should be representable in `docs/Lectures_outline.md`. If the lecture now teaches a concept the outline does not list (e.g., the train/test split moving from lecture 11 to lecture 10), the Phase 7 patch must include the relevant edit to the other lecture's row too.
8. **Duplication sweep.** Run a quick scan for two failure modes the eval skill's cat-8 sub-check formally catches but you can pre-flight in ~2 minutes:
   - **Across notebooks**: `grep -F` a distinctive ~10-line signature from each notebook against every other notebook in the lecture folder. Typical false-finding source: a content lift between files (e.g., we moved `lec_10d` §7 into `lec_10f` but forgot to delete the source) leaves near-duplicate cells in both places. A real positive is two notebooks both containing the same `make_classification(...)` boilerplate verbatim, the same intro paragraph, or the same helper function.
   - **Within a single notebook**: scan for two code cells that produce the same output (same DataFrame head, same plot title), and for markdown cells that restate the same definition in similar language more than twice.
   - **Apply the cat-3 reinforcement carve-out.** Deliberate "explain three times" repetition at different abstraction levels is the point of cat 3 strong tier. Mechanical copy-paste is the failure mode. The test: *does the second occurrence add value the first did not?* If yes, leave it. If no, consolidate or cite-and-defer.

This sweep is conversational and takes ~5 minutes. It is not a deliverable; it is a pre-flight before the eval.

### Phase 6 — Re-evaluate

Run `uoa-py-course-lecture-eval` again. The eval skill is the only source of truth for whether the work is done.

- **If composite = `strong`**: stop. Tell the maintainer the composite tier, the per-category tiers, and that the lecture is shippable.
- **If composite = `solid`**: read the eval's single must-fix or should-fix bottleneck. Fix it (often a typo, a stale reference, or a small content gap). Re-run the eval. Iterate until `strong`.
- **If composite < `solid`**: a content phase did not deliver. Identify which category is dragging, return to Phase 4 for that specific gap, fix it, re-run the eval. Do not start over from Phase 1.

There is no maximum iteration count, but iteration count is a quality signal — if you are on iteration 3 and still not at `strong`, the issue is probably in the plan (Phase 1 synthesis) or the maintainer decisions (Phase 2), not the execution.

**Be strict on the composite calculation.** The composite tier is the **lowest tier across applicable categories**, full stop. A breakdown of `[strong × 7, solid × 1, solid × 1]` is composite `solid`, not `strong`. Do not round up. If a subagent's eval report claims a composite that is higher than its lowest-category tier, the subagent has made an arithmetic error — the lowest-tier rule wins, and the maintainer should be told the truthful composite. The Lecture-10 history has at least one example of this: a subagent reported "composite strong" while the per-category breakdown showed `8 solid, 9 solid`. Calling that out honestly is part of the skill's job.

### Phase 7 — Closing notes

Emit (in chat, not as a written file):

- The eval composite tier and per-category tiers.
- Files added, modified, deleted (one-line summary each).
- The suggested patch to `docs/Lectures_outline.md` from the outline's `outline_<NN>.md` `## Suggested patch to docs/Lectures_outline.md` section, **verbatim**, for the maintainer to apply manually.
- Open decisions that the skill deferred to the maintainer (e.g., "industry-use trio uses outline defaults — confirm these match your teaching voice before next semester").
- A single "next steps" sentence: typically "commit and push" or "review notebooks in JupyterLab once before next class".

The skill does not auto-commit. Git operations beyond `git rm` / `git mv` in Phase 3 are the maintainer's call.

## Implementation patterns (proven in Lecture 10)

These patterns were validated when this skill produced its first composite-`strong` lecture (Lecture 10, 2026-05-12). Reuse them.

### Pattern: surgical notebook edits via a single Python script

Editing a 100+ cell notebook via dozens of `NotebookEdit` calls is error-prone (index drift after deletions, easy to miss a downstream reference). Instead, write a single Python script that:

1. Loads the notebook JSON.
2. Applies every replacement in one pass using **original** 0-based indices.
3. Applies all deletions sorted **high-to-low** so earlier indices are preserved.
4. Appends new closing cells at the end.
5. Runs `nbformat.validator.normalize()` to add cell IDs.
6. Writes the result back.

Save the script to `/tmp/refactor_lec_<NN>a.py` so the maintainer can inspect it if needed. The script is regenerable and read-once.

### Pattern: launch new-content subagents in parallel, foreground subagents that re-author from scratch

For each **new** notebook (`lec_NNb`, `lec_NNd`, `lec_NNe`) and for `read_agents_*.md`, launch a subagent with `run_in_background=true` and a fully self-contained prompt:

- Point at the lec_09 equivalent as the template.
- Point at the new `goals_<NN>.md` for the goal mapping.
- Specify the size target (cells, words) from the outline's Phase 5 estimates.
- Require execution verification via `jupyter nbconvert --execute` before returning.
- Explicitly forbid in-notebook exercises (those live in `practice_exercises/`).

The four-subagents-in-parallel pattern cut Lecture 10's authoring time roughly 4× vs. doing them sequentially.

Foreground (main-agent) work in parallel: the surgical edits to existing notebooks (`lec_NNa`, `lec_NNc`) and the exercises notebooks. The main agent has the most context and can react to subagent results as they return.

### Pattern: ask for industry-use trio + checkpoint cadence + destructive moves in one batch

Three load-bearing questions, distinct headers, all asked together at the start of Phase 2 via a single `AskUserQuestion` call with three questions. Avoids round-tripping the maintainer once per phase. The answers feed Phase 3 (destructive moves) and Phase 4 (industry-use names land in `lec_NNa` cell 0).

### Pattern: cell-ID normalisation in the same Python script that writes a notebook

`MissingIDFieldWarning` will become a hard error in a future nbformat version. Every script that writes a notebook should end with:

```python
import nbformat
nb_obj = nbformat.from_dict(nb)
nbformat.validator.normalize(nb_obj)
PATH.write_text(nbformat.writes(nb_obj) + "\n")
```

Don't ship raw-JSON-`dumps` notebooks. They work today but the warning is loud and future-fragile.

### Pattern: never silence stale outputs

When a refactor changes a cell's source, the cached `outputs` and `execution_count` from a previous run are stale. **Do not** delete them — `nbconvert --execute` will regenerate them on the next run, and the eval skill re-executes anyway. Leaving the old outputs in the committed file is the jupyter convention and keeps `git diff` readable.

### Pattern: example-mode test before authoring any hook or industry-use bullet

For every example you draft for the cat-7 hook or the "industry uses" bullets, run this three-question test before committing it to the notebook:

- *Are the labels pre-defined?* (yes → classification or regression candidate; no → unsupervised / clustering — wrong mode for a classification lecture)
- *Are labels known for the training population?* (yes → supervised; no → unsupervised)
- *Does the new observation genuinely need a prediction?* (yes → the example illustrates what the algorithm does; no → the example is descriptive, wrong mode)

Examples that score 3/3 yes match a classification lecture. Examples that score 2/3 (e.g., "embedding retrieval for RAG" — yes labels exist for past queries, yes for the training set, but the *new query does not need a label* — it needs the nearest neighbours, which is retrieval, not classification) belong in a similarity-search or retrieval lecture, not here.

The Lecture-10 initial hook ("trail-running shoes — five most similar buyers all bought trail-running shoes, so we send the trail-running promo") failed this test on question 1 (the customer's "type" was being *discovered*, not assigned from a pre-defined set), and the recsys / embedding-retrieval / similarity-baselines industry-use trio failed it on question 3 (retrieval, not classification). Both were replaced with examples that pass cleanly (medical triage / few-shot classification on embeddings / honest baseline before a deep model).

### Pattern: forward-reference, never pre-teach

A "what else exists" reference notebook (`lec_NNe_<topic>_vs_other_<things>.ipynb`) is the canonical place to acknowledge that other algorithms exist for the same problem. Keep it theory-only:

- One paragraph per alternative algorithm.
- "When to prefer over <this lecture's algo>" bullets (3–4).
- "Watch out for" paragraph.
- A scikit-learn docs link.
- An explicit "the full worked treatment is in lecture <MM>" pointer.

Do **not** fit / score / compare those alternative algorithms in worked code in this lecture. Beginners pattern-match unfamiliar API surface (`LogisticRegression`, `DecisionTreeClassifier`, `SVC(kernel='rbf')`) and treat each one as a new concept that needs to land before they can read the rest of the notebook. Worked code that depends on un-taught algorithms is the dominant cause of "I gave up halfway through this notebook" complaints.

The Lecture-10 initial `lec_10e` violated this — it fitted KNN / LogReg / DecisionTree / SVC side-by-side with coefficient tables, support-vector counts, and a bar chart. The worked content was lifted into lecture 13 (`lec_13/lec_10e_REFACTOR_to_comparing_classifiers.ipynb`), and `lec_10e` was downsized to 5 markdown cells matching the `lec_09f` template. The downsize alone bumped the optional load below the 1 h floor (a separate fix added `lec_10f_knn_regression_teaser.ipynb` to restore it), but the right shape for the reference notebook was clear once the constraint was respected.

### Pattern: scannable markdown style (the Lecture-11 readability lesson)

A notebook's markdown cells are where the *teaching* happens — the code cells are the *evidence*. If the teaching cell is a 200-word unbroken paragraph, beginners scroll past it and teachers cannot find a clean place to pause. The fix is structural, not stylistic: bullets instead of prose where possible, and visual line breaks inside long sentences so the eye can find the parts.

The Lecture-11 origin: the maintainer reviewed all six notebooks in `lectures_07_13_pandas_plots_scikit/lecture_11_regression_linear_polynomial/` after the first composite-`strong` pass and reported them as "too verbose" — every section had a 150–250-word prose paragraph where a bulleted list would have read in half the time. The reference fix that established this pattern is the rewrite of `lec_11a` cells 0, 4, and 7 (intro, §1 Load the data, §2 Visualise first) — open those three cells side-by-side with any other notebook in the lecture for the visual contrast.

**The three rules**:

1. **Bullets over prose whenever you are enumerating.** Three or more items of the same kind — three industry uses, four summary-table columns, three API quirks, five "what this notebook covers" sub-points — go into a bulleted or numbered list, never into a sentence joined by commas and "and". Each bullet starts with the named item in bold or backticks: `- **R-squared** — fraction of variance...`, not `- The R-squared column reports the fraction of variance...`. The bold/code prefix gives the eye an anchor.

2. **Hard line breaks for long sentences.** Markdown collapses adjacent lines into one paragraph unless the previous line ends in **two trailing spaces** before the newline. Use that to break any sentence longer than ~25 words into one clause per visual line. The literal source looks like:

   ```markdown
   We predict a continuous number from **one** input feature using the most-used model in applied statistics:  
   Ordinary Least Squares (OLS).  

   The mathematics is one library-independent thing; the Python ecosystem offers **three** popular APIs for it, each with its own usability.
   ```

   The two spaces at the end of `applied statistics:` and after `(OLS).` force a `<br>` in the rendered output. Without them, the three lines render as one run-on sentence. (A blank line between paragraphs is *also* a paragraph break, but it gives more vertical space than the hard line break — use blank lines between *thoughts*, two-trailing-spaces between *clauses of the same thought*.)

3. **Trim ruthlessly.** If two consecutive sentences make the same point in different words, delete one. If a list of bullets has an "obvious" entry the rest of the list implies, delete it. If a parenthetical aside ("note that...", "you might wonder...") restates what the previous sentence already said, delete it. The target for a teaching markdown cell is ≤150 words of *new* information; 200+ words is a smell, 300+ words is a refactor.

**Concrete before/after**:

> *Before* — one 70-word prose paragraph, no visual structure:
> `statsmodels is the Python home of formal regression statistics. Its OLS output is a multi-section .summary() table that reads like the appendix of an econometrics paper: R², coefficients with standard errors, t-statistics, p-values, F-statistic, AIC/BIC, and residual diagnostics. If your job is to write a statistics report, this is the library.`

> *After* — sentence framing, then a bulleted enumeration of the table's components, then the punchline. Same content, ~half the scan time:
> ```markdown
> `statsmodels` is the Python home of formal regression statistics:
> - OLS,
> - GLMs,
> - time-series models,
> - hypothesis tests.  
>
> Its OLS output is a multi-section `.summary()` table that reads like the appendix of an econometrics paper:
> - R²,
> - coefficients with standard errors,
> - t-statistics,
> - p-values,
> - F-statistic,
> - AIC/BIC,
> - residual diagnostics.  
>
> If your job is to *write a statistics report*, this is the library.
> ```

**When prose IS the right answer**: definitions, single-sentence aphorisms ("**The math is identical, so pick by ergonomics.**"), call-out callouts (`⏱ Skip if running long.`), and section transitions of ≤2 sentences. The rule is not "ban prose" — it is "use prose for one-sentence thoughts and lists for enumerations". A bulleted list of two items is usually worse than a single sentence; a paragraph that enumerates five items is always worse than the same five as bullets.

**Apply this when authoring any new notebook, and when editing an existing one.** Pre-flight the cells in Phase 5.5 by running a one-line scan: `python -c "import json; nb=json.load(open(F)); [print(i, len(''.join(c['source']).split())) for i,c in enumerate(nb['cells']) if c['cell_type']=='markdown']"` — every cell over 200 words is a refactor candidate, every cell over 300 words is a should-fix on the readability sub-check that `uoa-py-course-lecture-eval` cat 3 now carries.

### Pattern: no preview sections that duplicate the next notebook (the Lecture-11 §9 lesson)

A "brief preview" section at the end of notebook N that walks the diagnostic / workflow / concept that notebook N+1 covers formally is **mechanical duplication, not reinforcement**. The cat-3 strong tier wants concepts revisited *at a different abstraction level or with new value added* (see the eval skill's cat-3 reinforcement carve-out). A preview that runs the same diagnostic on the same data and forwards students to the next notebook for "the formal treatment" is value-equivalent at best, and is more likely to crowd out time / class-pacing budget than to deepen understanding.

The bright-line signal to refuse the preview: **if you can write a "⏱ Skip if running long — nothing downstream depends on it" callout above the section, the section is mechanical duplication, not reinforcement.** That callout is the maintainer telling themselves the section is dispensable. The honest move is to delete the section, not to wrap it in a skip-callout and hope the teacher remembers.

The canonical case is **Lecture 11, `lec_11a` §9** (Residuals — a brief assumption check), which existed at first composite-strong landing. The section:

- ran a residuals-vs-fitted plot + QQ plot on the temp-to-coffee fit,
- was prefaced by an explicit *"⏱ Skip if running long. … point students at lec_11b and skip §9 — they will not lose anything they need for lec_11c"* callout (the smoking gun),
- duplicated content fully covered in `lec_11b §E` (homoscedasticity), `§F` (normality), and `§G` (both checks applied to `grades_factors`),
- forced an extra `from scipy import stats` import into `lec_11a`'s clean three-API setup just for that diagnostic, blurring the notebook's "API tour" identity.

It was removed in the post-teaching update (3 cells deleted, recap rewritten to add an explicit `lec_11b` forward pointer, scipy import dropped, `goals_11.md` description corrected). Net win: tighter `lec_11a` ("the API tour, nothing else"), cleaner handoff to `lec_11b` ("the assumptions notebook owns residuals"), one less import for students to parse.

**Apply this rule in Phase 1 and Phase 5.5.**

- **Phase 1 synthesis** — when planning a notebook, refuse any "preview / teaser / brief look at" section whose content is fully owned by a downstream notebook in the same lecture. If the maintainer asks for one, push back: the forward-pointer in the recap is the right tool, not a duplicated worked example.
- **Phase 5.5 consistency sweep** — scan every notebook for sections wrapped in a `⏱ Skip if running long` callout. For each: read the callout's own claim ("nothing downstream needs this" / "the formal treatment is in lec_NNx"). If both clauses appear, the section is a duplication candidate — surface to the maintainer with the offer to delete.

**Carve-out: legitimate skip-callouts.** Not every `⏱ Skip if running long` callout flags a duplication. The rubric's cat-9 strong tier explicitly wants pause-points — a callout above a deepening sub-section (a second worked example at a higher difficulty, an aside on a related-but-tangential topic, an optional algorithm comparison) is the right shape. The duplication test is **content provenance**, not callout presence: does the callout's content already live in another notebook in this lecture? If yes → duplication. If no → legitimate pause-point.

### Pattern: side-effect awareness on goal / file additions

Adding content has rubric side-effects the maintainer rarely anticipates. Surface them at Phase 1 / Phase 2 time, not after the eval is done:

- **Declaring a new goal without an exercise** → cat 4 drops one tier (was `strong`, becomes `solid`). Fix: pair every new goal with at least one exercise in the same change.
- **Adding a section that introduces a new concept** → cat 1 needs the section's section heading cited in `goals_<NN>.md`; cat 9 absorbs the new reading time into the mandatory load.
- **Lifting content into its own notebook** → cat 8 (decomposition) stays strong; cat 9 optional load shifts (content moved, not added — net zero); cat 2 needs the new file declared in `goals_<NN>.md`'s Optional Files section.
- **Removing a notebook from the optional bucket** → cat 9 optional load drops. If the drop pushes optional load below 1 h, cat 9 falls to `needs work`. (See Lecture-10's `lec_10e` downsize for the canonical example.)
- **Renaming a notebook** → every cross-reference to the old name in other notebooks becomes a broken link. `grep -r "<old-name>"` across the lecture folder before committing.

The pattern: every additive or subtractive change to the lecture should be reasoned about against the 9-category rubric *before* re-running the eval. The eval catches everything eventually, but anticipating side-effects cuts iterations.

### Pattern: respect the maintainer's pushback

The maintainer can be wrong about the data. When the maintainer proposes a rewording, a content change, or a "I think this is actually true" framing, **run the experiment before implementing**. The Lecture-10 `lec_10d` §2 history is the canonical case: the maintainer proposed reframing "uniform and distance are essentially tied on iris" as "distance performs much better than uniform — here's why iris is special." The data did not support that framing — distance edged out uniform on most K values but only by 1–2 misclassified flowers, and the picture flipped at `random_state=123`. The skill pushed back with the seed-stability evidence, presented three honest wording options, and the maintainer picked the honest one. The point of the skill is to produce a defensible lecture, not to ratify maintainer intuition uncritically — but the pushback must be backed by numbers, not by stubbornness.

### Pattern: update mode preserves the "single Python script" discipline

In update mode the skill still benefits from atomic Python scripts. Even a small edit (rewrite cell 0, replace section 3 with a new K-sweep, lift §7 into a new file) should go through one script that:
1. Loads the affected notebook(s).
2. Applies every change in one pass.
3. Runs `nbformat.normalize()`.
4. Writes the result.
5. Triggers `nbconvert --execute` immediately after.

This keeps the edits inspectable (one `/tmp/<name>.py` per change), makes them undoable (revert the script, regenerate the notebook), and avoids the "I edited cell 38 and forgot the downstream reference at cell 91" failure mode. The Lecture-10 history has at least four examples: `refactor_lec_10a.py`, `build_lec_10c.py`, `build_exercises.py`, `downsize_lec_10e.py`, `add_split_section.py`, `final_strong_push.py` — every substantive change had a script behind it.

### Pattern: intent-preservation pass for hand-built drafts (the Lecture-11 lesson)

When the lecture folder contains a hand-built notebook — a `*_draft*.ipynb`, a `*_notes*.ipynb`, a file with first-person teacher voice — that notebook represents the maintainer's pedagogical intent expressed in code, before the rubric got involved. The rubric does not see this intent unless the skill makes it visible.

The canonical failure is **Lecture 11, 2026-05-19**. The lecture folder had `lec_11b_multiple_lin_regr_draft.ipynb` containing a hand-built workflow: fit OLS with `statsmodels`, read the summary table (R², adj-R², F-statistic, p-values, AIC, BIC), then **iterate feature subsets** by hand — drop the highest-p feature, refit, compare metrics, settle on the model labelled `### Best model I managed to find`. That iteration *was* the scientific feature-selection lesson the lecture existed to teach.

The skill ran in create/refactor mode and `git mv`'d the draft onto a new `lec_11c_multiple_linear_regression.ipynb`. The new file's content was sklearn-only, with statsmodels reduced to a one-sentence footnote: *"sklearn deliberately does not print standard errors, p-values, F-statistics, or AIC. (...) The course does not pretend sklearn provides what statsmodels provides; it pretends you do not need inference output for the prediction workflow that follows."* The draft's distinctive intent was silently dropped.

The students felt it during the live lecture. The fix was a post-teaching `§F` insert — refit with statsmodels, walk the backward-elimination loop, then verify with sklearn-native `SequentialFeatureSelector` + `RFE` — and a corresponding new goal G4 in `goals_11.md`. That fix is correct content, but the root cause was a skill behaviour, not a content gap.

The defences that go into this skill:

1. **Phase 0 step 4 ("Hand-built content inventory")** classifies every notebook as skill-generated vs hand-built and summarises each hand-built file's distinctive intent in ≤2 lines.
2. **Phase 2 question 2 ("Hand-built draft disposition")** asks a per-file preserve / partial-preserve / retire question. The default is **never** retire; it is preserve-cells-into-replacement when the intent maps to a goal, and preserve-as-is otherwise.
3. **The boundary rule "Preserve hand-built draft intent — never overwrite silently"** holds the line if Phase 0/2 are skipped: a `git mv` of a hand-built draft onto a skill-generated final filename is forbidden unless the disposition question has been answered.

The test the skill must always pass: after a refactor, if the maintainer opens the original draft side-by-side with the final notebook, every methodological idea the draft taught should be either (a) still present in the new file, (b) explicitly retired in the Phase 1 synthesis with a one-line rationale, or (c) preserved in the original file living alongside. None of those three was true for Lecture 11; that is the failure to prevent.

## Stopping conditions

Stop when **any** of these is true:

1. **`uoa-py-course-lecture-eval` returns composite `strong`.** This is the canonical success.
2. **Composite is `solid` and every remaining finding is a polish-tier item** (typos, anchor-text quality, a single non-blocking `(c) needs-verification` link). The composite-`strong` tier is reachable if the maintainer wants it, but is not the same as "lecture is shippable". Surface the remaining items in Phase 7 and let the maintainer decide whether to ship at `solid` or push for `strong`.
3. **The maintainer signals stop.** Whatever state the lecture is in, write Phase 7's closing notes and end the session.

Do not run additional refactor passes once a stopping condition fires. Repeated full-refactor passes on a `strong` lecture tend to over-fit to the rubric and dilute the maintainer's voice.

## Tone

Direct, concrete, no flattery. Every action surfaced to the maintainer should be specific enough that they could ask another engineer to do it instead. The lecture-eval skill is the judge; this skill is the implementer. When in doubt about whether a change is needed, re-read the eval report rather than guessing.

If the eval and the outline disagree on something material (e.g., the eval says "lec_NNc should be optional" but the outline says "lec_NNc should be mandatory"), surface the disagreement to the maintainer rather than picking one. Both skills are calibrated against the same rubric but they look at different evidence (eval = current state; outline = target state), so honest disagreement is information.
