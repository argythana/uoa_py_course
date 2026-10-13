---
name: uoa-py-course-create-excellent-lecture
description: >
  Use this skill to drive a single lecture in this course repo from its current
  state up to composite `strong` on the 9-category rubric used by
  `uoa-py-course-lecture-eval`, or to apply a targeted update to an already
  solid-or-strong lecture (add a section, retire content, rescope, lift content
  between lectures). Trigger on "improve lecture NN", "bring lecture NN to
  strong", "fix every gap in lecture NN", "refactor lecture NN to the Lecture 09
  template", "update lecture NN to add X", "lift section X from lecture NN to
  lecture MM", or when the user supplies an eval report and asks for the fixes
  to land. Do NOT use it to evaluate or score a lecture
  (`uoa-py-course-lecture-eval`), plan a lecture with no existing material
  (`uoa-py-course-lecture-outline` first), grade student work, rewrite files
  outside `lectures_*/`, or edit `docs/Lectures_outline.md` directly (it emits a
  suggested patch). It runs a missing eval or outline first and asks before
  destructive moves such as deletions or renames.
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
6. **Term inventory.** Before writing any prose, list the vocabulary this lecture inherits and the vocabulary it must define, with the eval skill's scan script `.claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py`. The rules it applies (P1, P2, 1–11) are in §"Pattern: scannable markdown style".
   - **Inherited terms.** Run `--terms` over every earlier lecture; for lecture 11: `for MM in $(seq -f %02g 1 10); do python3 .claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py --terms --lecture "$MM"; done`. A term defined there is reused with a `term (lec_MMx)` pointer, never defined again. Lectures written before the prose rules carry few definition bullets: a term they teach in another form still counts as taught, and its old form is a note for the maintainer, not an edit (this skill touches one lecture only).
   - **This lecture's candidates.** Run `python3 .claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py --inventory --lecture NN` for each candidate term's first use, later uses and proposal (definition bullet or inline gloss). Confirm each proposal with the course-vocabulary test (habit 4 of the pattern).
   - **Definition order.** For each new term, write down the terms its definition needs; add any missing one first (rule 10) and order the bullets so each builds on those above (rule 9). Assign every bullet to the first notebook that uses the term, mandatory before optional, above the first code cell that uses it.

   The output is a short table (term | defined in | status: inherited / new here / inline gloss) that feeds Phase 1 and every Phase 4 subagent prompt. In update mode, build it only for the terms the change introduces.
7. Sanity-check: the eval's must-fix findings should align with the outline's create-improve commitments (in create mode), or the maintainer's stated change (in update mode). If the eval and the maintainer's intent diverge significantly, flag it and pause for direction.

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
- Any concept the change introduces or removes — cross-check against `docs/Lectures_outline.md` (Phase 0 step 5) and the term inventory (Phase 0 step 6). If the change uses a concept not yet taught, surface it: the maintainer either teaches it here (adds material + goal) or avoids it.

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

**Every subagent prompt carries the term inventory and the prose rules.** Paste the Phase 0 step 6 term inventory (inherited terms with their `lec_MMx` home, the terms this file defines and in what order, the terms a sibling notebook defines first) and the rules table from §"Pattern: scannable markdown style". A subagent that has not seen the rules writes inline definitions and bold emphasis; one that has not seen the inventory redefines terms an earlier lecture owns. A notebook subagent runs `python3 .claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py <its notebook>` alongside the execution check and fixes the hits before returning PASS.

**Foreground tasks** (surgical, sequential, by main agent):

- **Edit `lec_NNa` for cat-7 + cat-3 fixes.** Dump cell-level structure with `python -c "import json; ..."`. Plan a single Python script that does **all** edits atomically: cell-0 replacement (hook + 3 industry uses + lecture map + forward refs to later notebooks); imports cell adjustments; train/test split implementation if the original was data-leaking; downstream cell updates for the split; deletion of any in-class exercise cells (moved to `practice_exercises/`); appended closing markdown (limitations forwarding to `lec_NNb` + career framing closing the cat-7 arc). Apply the script. Run `jupyter nbconvert --execute` to verify PASS.
- **Build out `lec_NNc`** if the existing version is thin (zero markdown, etc.). Use a Python script to write a fresh notebook with full narrative arc: title + intro, helper function, weights/parameter contrast, K-effect sweep, recap.
- **`lec_NN_exercises.ipynb` + `_solutions.ipynb`** (in `practice_exercises/`). One required exercise per declared required goal G1..Gn (mapped 1:1). One stretch exercise per optional goal O1..On. The exercises notebook uses placeholder code (`# Your code here` comments + no-op executable cells so the notebook runs as a template); the solutions notebook has runnable answers. Both must PASS nbconvert. Author both via a single Python script for consistency. Exercises define nothing: a term an exercise needs points to its definition bullet in the notebook (`term (lec_NNx)`).
- **Edits to existing notebooks follow the same prose rules.** Every cell the script writes or rewrites meets the hard authoring rules below and the term inventory: an inline definition in a rewritten cell becomes a definition bullet, and a term an earlier lecture defines becomes a `term (lec_MMx)` pointer. In create mode, also convert the lecture's remaining old-form definitions (the eval's cat-3 Terminology sub-check scores the whole lecture). In update mode, touch only the cells the change needs and list the other hits for the maintainer in Phase 7.

**Hard authoring rules for any new notebook**:

- Single imports cell at top; one constant `RANDOM_STATE = 42`; seed every `train_test_split`, `make_classification`, `KMeans`, etc. **Do not** add `random_state=42` to estimators that don't have one — `KNeighborsClassifier` and `StandardScaler` have no internal randomness and will raise `TypeError` if given a `random_state`. (This is one of the classic AI-assistant hallucinations flagged in `read_agents_knn_workflows.md` §3.)
- One concept per code cell. Explicit variable names (`X_train_scaled`, not `Xs`).
- Markdown cells short (~150 words max each). Beginner-friendly tone. No emojis (project style).
- **Scannable markdown — bullets, short paragraphs and definition bullets over dense prose.** Beginners and teachers both skim markdown cells in a notebook; a wall of prose is the dominant cause of "I scrolled past the explanation and went straight to the code". The full rules, with their shared numbers and scan check IDs, are under §"Pattern: scannable markdown style" below; the short version:
  - **P1, rule 7**: one idea per paragraph, with a blank line where its job changes; at most 3 sentences and ~60 words; a long sentence becomes two sentences, never a trailing-space line break.
  - **Rule 8**: three or more items of one kind go to a list (industry-use trio, model-output components, API quirks, "what this notebook covers"), each bullet opening `- **Item**: …`; a one-item list only for a defined term or a command to remember. Trim ruthlessly: if a paragraph repeats the previous one's point in other words, delete one of them.
  - **P2, rules 1–4**: every course term gets one definition bullet, `- [A/An/The] **term** is/are <kind of thing> that <what sets it apart>.`, with one term per bullet, readable on its own, saying what the thing *is*; no inline definitions, no term tables.
  - **Rules 9–11**: definitions in prerequisite order with a complete chain (add a missing definition first) and one meaning per word; a term an earlier notebook defines gets a `term (lec_NNx)` pointer, not a second definition (Phase 0 step 6 builds the term inventory).
  - **Rules 5–6**: bold only for vocabulary, list anchors, opening labels and callouts, emphasis in *italics*; list continuation lines indented and one blank line between blocks.

  The visual template for bullets and trimming is `lec_11a` cells 0, 4, 7 (the lecture-11 intro and §§1–2); the template for paragraphs and definitions is `teach-llm-system`'s `lec_01a`, quoted in the pattern.
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
9. **Prose and terminology sweep.** The eval runs the same scan script for its cat-3 Markdown readability and Terminology sub-checks and its "Prose and terminology" table, so fix its hits first:

   ```
   python3 .claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py --lecture NN
   ```

   - **Read the report.** Each line is `short_name cell N  check-id  excerpt`; the check IDs map to the rules table in §"Pattern: scannable markdown style". After fixing one class of hit, re-run just that class with `--only` (e.g. `--only def-form,def-multi-term`).
   - **The non-rule IDs.** `wall-of-prose`, `oversize-cell` and `cell-words` call for bullets, a split or trimming. `def-duplicate` and `used-before-defined` call for one definition in the first notebook that uses the term, mandatory before optional. `def-in-exercises` moves the definition into the notebook.
   - **False positives and scope.** Leave a false positive (an opening label caught by `bold-emphasis`) and say why in Phase 7. In update mode, fix the hits in the cells the change touched and list the rest for the maintainer.

   Then do the editorial read the script cannot. Run the script with `--terms --lecture NN` and read every definition bullet with its `uses:` line:
   - **Rule 2**: does the bullet read alone, with no pronoun pointing outside it?
   - **Rule 3**: does it say what the thing *is*, or only what it does and why it matters?
   - **Rule 10**: is every technical word it relies on defined, above it or in an earlier lecture, and does each `term (lec_NNx)` pointer lead to the defining notebook?
   - **Rule 11**: does any defined term take a second meaning elsewhere in the lecture?
   - **P1**: in each cell you wrote or rewrote, does every paragraph do one job?

Steps 1–8 are conversational and take ~5 minutes; step 9 takes longer on a lecture written before the prose rules. None of it is a deliverable; it is a pre-flight before the eval.

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
- Include the Phase 0 term inventory and the rules table from §"Pattern: scannable markdown style", and require a clean `scan_notebook_prose.py` report on the new notebook alongside the execution check.
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

A notebook's markdown cells are where the *teaching* happens — the code cells are the *evidence*. If the teaching cell is a 200-word unbroken paragraph, beginners scroll past it and teachers cannot find a clean place to pause. The fix is structural, not stylistic: bullets instead of prose where possible, short paragraphs that each do one job, and one definition bullet per course term so a student can find what a word means.

The Lecture-11 origin: the maintainer reviewed all six notebooks in `lectures_07_13_pandas_plots_scikit/lecture_11_regression_linear_polynomial/` after the first composite-`strong` pass and reported them as "too verbose" — every section had a 150–250-word prose paragraph where a bulleted list would have read in half the time. The reference fix that established this pattern is the rewrite of `lec_11a` cells 0, 4, and 7 (intro, §1 Load the data, §2 Visualise first) — open those three cells side-by-side with any other notebook in the lecture for the visual contrast. Those cells predate the paragraph and definition rules below: cells 4 and 7 still break sentences with trailing spaces, and cell 0 still bolds emphasis and leaves list continuation lines unindented. Copy their bullets and their trimming, not their line breaks.

The paragraph and definition rules come from the sibling course [`teach-llm-system`](https://github.com/argythana/teach-llm-system), where the maintainer first applied them to `lec_01a_first_call_tokens_context.ipynb`. The before/after pairs under habit 4 quote that notebook (its prose is CC BY 4.0).

**The rules.** Their numbers (P1, P2, 1–11) are shared with `uoa-py-course-lecture-eval` (the cat-3 Terminology sub-check and the "Prose and terminology" table of its report) and with the check IDs of its scan script, `scripts/scan_notebook_prose.py`. "Rule N" anywhere in this skill means this table.

| # | Rule | Scan check ID |
| --- | --- | --- |
| P1 | One idea per paragraph: a blank line where a paragraph's job changes (main point, mechanism, lesson, instruction, pointer); a cause and its effect stay together. | editorial; length via `para-long` |
| P2 | Definition bullets for course terms, strict form `- [A/An/The] **term** is/are <kind of thing> that <what sets it apart>.` List bullets keep `- **Item**: …`, so "is/are" marks a definition. | `def-form` |
| 1 | One term per definition bullet (one bold span). | `def-multi-term` |
| 2 | Self-contained: no pronoun pointing to text outside the bullet, so it can be copied into a glossary. | `def-pronoun` + editorial |
| 3 | Define, don't describe: say what the thing *is*; why it matters goes in the next sentence. | editorial with `--terms` |
| 4 | One form for every course term: no inline "**X**, a …" definitions, no `\| Term \| Meaning \|` tables. | `def-inline`, `term-table`, `term-undefined` |
| 5 | Bold means vocabulary: bold only for a term in its definition bullet, a list-bullet or table-row anchor, a defined term in a recap or "What this notebook covers" list, an opening label, and callouts. Emphasis uses italics. | `bold-emphasis` |
| 6 | Source matches render: list continuation lines indented; one blank line between blocks; a sentence between a definition group and another list, because two lists separated only by a blank line render as one. | `lazy-continuation`, `blank-lines`, `list-merge` |
| 7 | Paragraph limit: at most 3 sentences and about 60 words; a long sentence becomes two sentences. Trailing-two-space hard line breaks are deprecated (invisible in the source, stripped by editors and formatters). | `para-long` |
| 8 | A one-item list only for a defined term or a backticked command/API to remember. | `single-bullet` |
| 9 | Prerequisite order: a definition uses only everyday words, words from earlier lectures, and terms defined before it; within a group each bullet builds on those above; parts before the whole (node, edge → graph); related definitions form one tight list. | `def-order` |
| 10 | Complete chain: every technical word a definition relies on has its own earlier definition; add a missing one first (request and response before server and client); a "term (`lec_NNx`)" pointer leads to the notebook that defines the term. | `backref-mismatch` + editorial |
| 11 | One word, one meaning: a defined term keeps one meaning; a second sense gets its own name or other words (the server sends a response, the model writes an answer). | editorial |

The script also reports `wall-of-prose` (>200 words, no list, an unbroken prose run of ≥6 lines), `oversize-cell` (>300 words), `cell-words` (>160 words), `def-duplicate`, `used-before-defined` and `def-in-exercises`.

**The six habits** (each groups the rules named in its title):

1. **Bullets over prose whenever you are enumerating** (rule 8). Three or more items of the same kind — three industry uses, four summary-table columns, three API quirks, five "what this notebook covers" sub-points — go into a bulleted or numbered list, never into a sentence joined by commas and "and". A bullet that explains its item starts with the item in bold or backticks and a colon: `- **Real-estate price from one feature**: a first-pass valuation from square metres alone`, not `- One use is valuing an apartment from its square metres`. The bold/code prefix gives the eye an anchor, and the colon keeps a list bullet apart from a definition bullet, whose verb is "is". A one-item list is only for a defined term or a backticked command or API worth remembering; anything else is a sentence.

2. **One idea per paragraph, at most three sentences** (P1, rule 7). Leave a blank line wherever the paragraph's job changes: the main point, how it works, the lesson, an instruction, a pointer. Keep a cause and its effect in one paragraph. A paragraph holds at most 3 sentences and about 60 words, and a sentence longer than ~25 words becomes two sentences. Do not use trailing-space hard line breaks (two spaces before a newline), which earlier versions of this skill recommended: they are invisible in the source, and editors and formatters strip them silently, so the layout breaks without a visible diff. `lec_11a` cell 7 needs exactly this fix: its four trailing-space lines become two paragraphs, first the instruction with its reason (plot the data first, because the eye spots curves faster than any test statistic), then how to read the plot (a clean line versus a U-shape).

3. **Trim ruthlessly.** If two consecutive sentences make the same point in different words, delete one. If a list of bullets has an "obvious" entry the rest of the list implies, delete it. If a parenthetical aside ("note that...", "you might wonder...") restates what the previous sentence already said, delete it. The target for a teaching markdown cell is ≤150 words of *new* information; 200+ words is a smell, 300+ words is a refactor.

4. **Definition bullets for course terms** (P2, rules 1–4, 9–11). A course term is defined once, in one form:

   ```markdown
   - [A/An/The] **term** is/are <kind of thing> that <what sets it apart>.
   ```

   - **One term per bullet** (rule 1): one bold span. A bullet that bolds four terms defines none of them well.
   - **Self-contained** (rule 2): no "it", "this" or "them" pointing outside the bullet; the bullet reads correctly when copied into a glossary.
   - **Define, don't describe** (rule 3): the bullet says what the thing *is*; why it matters goes in the next sentence, outside the bullet.
   - **One form only** (rule 4): no inline "**X**, a …" definitions and no `| Term | Meaning |` tables.
   - **Course-vocabulary test**: a term gets a bullet when it comes back later (a later section or notebook, `goals_<NN>.md`, the recap, the exercises) or is industry vocabulary. A one-off word gets a short inline gloss, without bold.
   - **Define once**: in the first notebook that uses the term in teaching order, before any code cell uses it. A forward mention is a plain-text gloss ("a word piece, section 3"). A mandatory notebook never relies on a definition in an optional one, and exercises define nothing. A later notebook or lecture points back with `term (lec_NNx)`.
   - **Prerequisite order** (rule 9): a definition uses only everyday words, words from earlier lectures and terms defined above it. Within a group each bullet builds on the ones above, parts come before the whole (node and edge before graph), and related definitions form one tight list.
   - **Complete chain** (rule 10): every technical word a definition relies on has its own earlier definition; if one is missing, add it first. In lecture 11, a bullet saying OLS "minimises the squared residuals" needs a definition of residual above it.
   - **One word, one meaning** (rule 11): a defined term keeps one meaning across the course; a second sense gets its own name or other words.

   **Before/after, section 2 "Your first call" of `teach-llm-system`'s `lec_01a`** (P2, rules 4, 9, 10). Before, three inline definitions, one of them resting on "special token", which nothing had defined yet:

   > An LLM does one thing: given text, it predicts the next **token** (a word piece, section 3), appends it, and repeats until it emits a **stop token**, a special token that means "done".
   >
   > Everything else, chat, coding, summarising, is that loop with a clever **prompt**, the text you send.

   After, the main point, then one tight group in prerequisite order (prompt → answer → token → stop token); "special token" gets its own bullet later in the section, where the prompt's extra tokens first need it:

   ```markdown
   An LLM does one thing: given text, it predicts the next token, appends it, and repeats until it writes a stop token.

   - A **prompt** is the text you send to a model.
   - An **answer** is the text a model writes back for a prompt.
   - A **token** is the unit of text a model reads and writes: a word, a word piece or a punctuation mark. Section 3 looks inside.
   - A **stop token** is a token that a model writes to end its answer.

   Everything else, chat, coding, summarising, is that loop with a clever prompt.
   ```

   **Before/after, section 1's server group** (rules 9, 10, 11). Before, four bold terms inline; "request" and "response" carry the definitions without being defined, and the server "answers", a word the model's answer needs:

   > [**Ollama**](https://docs.ollama.com/) does this as a **server**: a program that runs in the background, keeps the model in memory, and answers requests at the address in `OLLAMA_HOST`.
   >
   > Your code is the **client**: it sends a request to the server and gets a response back. Guide `01c_ollama` explains the address, its port, and the **API**, the set of requests the server understands.

   After, the parts first (request, response), then the roles and the API built on them, then the instance (Ollama); the server now *handles* requests:

   ```markdown
   - A **request** is what one program sends to another program to ask for one thing.
   - A **response** is what the program sends back for one request: the result, or an error.
   - A **server** is a program that runs in the background and handles requests at an address.
   - A **client** is the code that sends requests to a server and reads its responses.
   - An **API** is the set of requests a server understands, with the shape of each request and of its response.
   - **Ollama** is a [local model server](https://docs.ollama.com/): it keeps a model in memory and handles requests at the address in `OLLAMA_HOST`.

   Your code is the client. Guide `01c_ollama` explains Ollama's address, its port, and its API.
   ```

   Two smaller pairs from the same notebook:

   - **One term per bullet, parts first** (rules 1, 6, 9): section 3 "Tokens" had one bullet holding four bold terms, the whole first, with an unindented continuation line: "A **tokenizer** cuts text into **tokens**, … and replaces each with its **token ID**, its position in the **vocabulary**: the fixed list of every token the model knows". The rewrite is three bullets, parts first: vocabulary (the fixed list of every token a model knows), token ID (the number that stands for one token: its position in the vocabulary), tokenizer (the program that cuts text into tokens and replaces each with its token ID). Token itself was defined in section 2.
   - **Self-contained** (rule 2): section 5's "**Temperature** reshapes them before the draw" points "them" at the paragraph above; the rewrite reads alone: "**Temperature** is a setting that reshapes the token probabilities before the draw".

5. **Bold means vocabulary** (rule 5). Bold marks only a term in its definition bullet, the anchor at the start of a list bullet or table row, a defined term in a recap or "What this notebook covers" list, a label that opens a paragraph (`**Status: …**`, `**Next: …**`), and the callouts (`⏱ **Skip if running long.**`). Emphasis uses *italics*. `lec_11a` cell 0's "from **one** input feature" and cell 4's "**Always do this**" are emphasis, so they become *one* and *Always do this*; `lec_01a` made the same change ("You edit **one line**" became "You edit *one line*"). Once bold marks only vocabulary, a student skimming a notebook for bold finds the words to learn.

6. **Source matches render** (rule 6). Indent a list item's continuation lines under the item: `lec_11a` cell 0 puts "A first-pass valuation …" flush left under `1. **Real-estate price from one feature.**`, so the source suggests a new paragraph while the render runs label and explanation together inside the item. Leave one blank line between blocks (paragraph, list, heading, table, code fence), so a list never sits glued to the sentence above it. This repo has no markdown formatter hook (in `teach-llm-system` a wrap hook does both), so the script that writes the cell must do it.

**Concrete before/after** (habits 1, 2, 4 and 6):

> *Before* — one 51-word paragraph: a description where a definition belongs, and a seven-item enumeration buried in a sentence:
> `statsmodels is the Python home of formal regression statistics. Its OLS output is a multi-section .summary() table that reads like the appendix of an econometrics paper: R², coefficients with standard errors, t-statistics, p-values, F-statistic, AIC/BIC, and residual diagnostics. If your job is to write a statistics report, this is the library.`

> *After* — a definition bullet, the framing sentence, the enumeration as a list, then the punchline: one job per block, one blank line between blocks, no trailing punctuation on the list items. Same facts, ~half the scan time:
> ```markdown
> - **`statsmodels`** is a Python library for statistical modelling that reports the uncertainty of every fitted coefficient.
>
> `statsmodels` prints its OLS output as a multi-section `.summary()` table that reads like the appendix of an econometrics paper:
>
> - R²
> - coefficients with standard errors
> - t-statistics
> - p-values
> - F-statistic
> - AIC/BIC
> - residual diagnostics
>
> If your job is to *write a statistics report*, this is the library.
> ```

**When prose IS the right answer**: single-sentence aphorisms ("*The math is identical, so pick by ergonomics.*"), call-out callouts (`⏱ Skip if running long.`), and section transitions of ≤2 sentences. The rule is not "ban prose" — it is "use prose for one-sentence thoughts and lists for enumerations". A bulleted list of two items is usually worse than a single sentence; a paragraph that enumerates five items is always worse than the same five as bullets.

**Apply this when authoring any new notebook, and when editing an existing one.** Pre-flight the cells in Phase 5.5 with the eval skill's scan script: `python3 .claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py --report --lecture NN`. Each hit reads `short_name cell N  check-id  excerpt`. `uoa-py-course-lecture-eval` reads the same report: `wall-of-prose` and `oversize-cell` feed its cat-3 Markdown readability sub-check, and the rule IDs feed its cat-3 Terminology sub-check.

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
