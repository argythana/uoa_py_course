---
name: uoa-py-course-lecture-eval
description: Use this skill to evaluate one lecture folder in this course repo against the 9-category pedagogical rubric (six internal + three external) and produce a Markdown report with a composite tier and prioritized fixes. Trigger on requests like "evaluate lecture NN", "audit lecture NN", "score lecture NN", "review the lecture material for NN", or when the user supplies a `lectures_*/` folder path and asks for a quality assessment. Do NOT use it to: improve, rewrite, or propose content for a lecture (that work belongs to the future `create-improve-lecture` skill — this skill flags absence only); evaluate non-lecture material such as `README.md`, `CLAUDE.md`, or arbitrary scripts; grade student submissions or final-assignment notebooks (use `final_assignment/grade_feedback.prompt.md` instead). If the lecture number or path doesn't resolve to exactly one folder, ask which folder before proceeding.
---

# Lecture evaluation

You are evaluating **one** lecture folder against the rubric below. The output is a Markdown report; the user will read it and act on it. The point of the skill is to surface every gap that prevents the lecture from being `strong` — ranking is incidental, fixing is the goal.

## What a strong lecture looks like (calibration source)

The rubric is calibrated against this template. When in doubt about a tier, ask whether the lecture meets the template.

> A strong lecture for this course is one a **working data scientist** would read on a flight and learn something from, AND a **first-year MSc student** can follow over a single week (~1.5–3 h of mandatory at-home review of the lecture content + 2–2.5 h of in-class presentation + ~1–3 h of optional/career-track notebooks on top) without external help, AND a **teacher** can present in class without skipping or overrunning. **Practice exercises are bonus work** (per the README's "*Mid-course assignments and practice exercises are optional and are graded only positively*") and are reported on a separate budget line; their time is not in the mandatory or optional sums.

Concretely, a strong lecture has these parts in roughly this order:

1. **A hook.** One paragraph or worked example: a real problem the technique solves.
2. **2–3 named industry uses.** Each is a single sentence: who, for what, what specifically the technique does there.
3. **The technique itself.** Split into logical notebooks — one concept per notebook. Letter ordering reflects dependency, not chronology.
4. **Honest limitations.** When NOT to use the technique. Failure modes a beginner will encounter.
5. **Hands-on practice.** Required exercises mapped to each declared *required* goal, plus optional/stretch exercises tied to optional goals.
6. **A "what would I do with this on the job" beat.** A closing connection back to the hook.
7. **Optional / advanced material for career-track students.** A clearly labelled section — separate notebooks, scripts, or `read_*.md` files — that goes deeper than the mandatory core, for students pursuing a career in Data Science / AI. Per the README, this is required structure, not a nice-to-have.
8. **AI Fluency complementary content.** A `read_agents_*.md` (or equivalent) file with current, specific guidance on using AI assistants for the lecture's topic. Per the README, every lecture carries this thread; it is not optional and not gated by the lecture range.

A lecture missing parts 1, 2, 4, or 6 is a tutorial, not a course lecture. A lecture missing part 7 or 8 violates the README's stated structure and should be flagged as a gap in the relevant category, not waved through.

## Structural model of a course lecture (mandatory vs. optional)

The README (lines 78–80) defines two distinct content tracks per lecture:

- **Mandatory track** — read before the next lecture, walked through in class. Targets: ~3–5 h student self-study + 2–2.5 h presentation.
- **Optional / advanced track** — for students who want to read more or pursue a career in Data Science / AI. Target: ~2 h additional self-study. Not walked through in class. Not required to pass.

Every refactored lecture's `goals_NN.md` is expected to surface this split in two places:

1. **Goals**: required goals listed first; an explicitly labelled "Optional" / "Advanced" / "Career track" sub-section listing the optional goals.
2. **Files**: same — a "Files" section for mandatory files + an "Optional / Further reading" section for the career-track files.

If `goals_NN.md` is a flat list with no separation, the lecture is structurally non-conforming and should be flagged. The skill does **not** infer which files are optional from filenames or content — that classification is a maintainer decision and must be declared in `goals_NN.md`. If absent, treat as a category 1 gap and, when computing volume (Phase 2c), bucket every pedagogical file as mandatory (not as a guess about which it "should" be).

`read_agents_*.md` (AI Fluency complementary content) is mandatory by the README's own framing and lives in its own bucket — neither inflating the mandatory load nor counting toward optional. It is scored under category 6.

## Inputs

Accept either:

- A path: `lectures_07_13_pandas_plots_scikit/lecture_09_clustering_deploy_hf_app/`
- A lecture number: `09`. Resolve it by globbing `lectures_*/lecture_NN_*/` (or `lectures_*/lecture_NN/` for unrefactored ones).

If multiple matches or no match, ask the user which folder.

## Boundaries

- One lecture per invocation. For multi-lecture audits, run the skill once per lecture.
- Read-only against the lecture folder. Do not edit lecture material.
- The skill **flags absence**; it does not propose specific industry examples or rewrites. Improvement work is the job of the future `create-improve-lecture` skill.
- Not for grading student work. Final-assignment grading lives at `final_assignment/grade_feedback.prompt.md` and uses different criteria.
- Not for non-lecture material. Only `lectures_*/` folders are in scope; do not evaluate `README.md`, `CLAUDE.md`, or scripts outside a lecture.
- Reports go to `.claude/uoa-py-course-lecture-eval-reports/<lecture-folder-name>_<YYYY-MM-DD>.md`. Create the directory if missing. Never write reports inside the lecture folder itself.
- Use `course_venv/` for any execution. Do not install packages, do not modify the venv.
- Never invent findings. Every finding cites a file path + cell index or line number.

## Refactor-state awareness

Some lectures (10–13, 14–16) haven't been refactored into `reading_material/` + `practice_exercises/` yet. Apply the same criteria, but do not penalise the structure:

- Treat missing `reading_material/practice_exercises/` split as one Should-fix recommendation, not a separate finding per category.
- Treat missing `goals_NN.md` as one Must-fix recommendation. Without it, categories 1 and 2 default to `gap` — say so explicitly and move on; don't multiply findings.
- Surface refactor-state at the top of the report so it's clear the bar is calibrated.

## Procedure

### Phase 1 — Inventory

1. Walk the folder. Record every file with its size and type.
2. Detect refactor state: presence of `reading_material/`, `practice_exercises/`, `goals_NN.md`.
3. Parse `goals_NN.md` if present. Extract, in this order:
   - **Required goals** — bullets under the main "Learning Goals" / "Goals" heading, *before* any "Optional" / "Advanced" / "Career track" / "Further reading" sub-heading.
   - **Optional / advanced goals** — bullets under a heading whose text matches `optional`, `advanced`, `career`, or `further reading` (case-insensitive). Record whether such a heading exists at all.
   - **Required files** — entries under the "Files" section (mandatory bucket).
   - **Optional files** — entries under an "Optional" / "Further reading" / "Advanced" Files sub-section. Record whether such a sub-section exists at all.
   - **AI Fluency files** — entries that point to a `read_agents_*.md` (or equivalent) under any AI Fluency / Agents sub-heading. Record whether such a file is declared and whether it actually exists on disk.
4. Cross-check filenames against the convention (`lec_NNx_*`, `goals_NN.md`, `read_*.md`, `lec_NN_exercises.md` + `_solutions.{py,ipynb}`).
5. **Bucket every pedagogical file** (notebooks, scripts, `read_*.md`, but not `requirements.txt`, datasets, cached HTML, build artefacts) into one of: `mandatory`, `optional`, `ai-fluency`, or `unaccounted` (file exists in the folder but isn't listed in any `goals_NN.md` section). Carry these buckets into Phase 2c.
6. **Structural-conformance flags** — record three booleans for use by the rubric:
   - `goals_split_present` — true iff `goals_NN.md` has both a required-goals block and an optional/advanced sub-heading.
   - `optional_files_section_present` — true iff `goals_NN.md` has a labelled "Optional" / "Further reading" Files sub-section.
   - `ai_fluency_file_present` — true iff a `read_agents_*.md` (or equivalent declared in goals) exists on disk and is non-trivial (>200 words).

### Phase 2 — Mechanical checks

These produce objective signals that feed the rubric.

**2a. Code execution.** For every `.ipynb` and `.py` in `reading_material/` (or the lecture root for unrefactored lectures), and for every `_solutions.{py,ipynb}` in `practice_exercises/`:

1. **Secret-gated detection.** Before executing, grep the source for: `os.environ`, `getenv`, `HF_TOKEN`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `load_dotenv`, `dotenv`, hard-coded `hf_*` / `sk-*` strings, `huggingface_hub.login`. If any match, skip execution, mark the file as `SKIP (needs secrets: <which>)`, and score it on static read only.
2. **Notebooks**: `jupyter nbconvert --to notebook --execute <file> --output /tmp/uoa-py-course-lecture-eval-<hash>.ipynb --ExecutePreprocessor.timeout=120 2>&1`. Don't write the executed notebook back to the lecture folder.
3. **Scripts**: `python <file>` from the lecture folder (so relative dataset paths resolve).
4. Use `course_venv`'s python from the repo root: `course_venv/bin/python` and `course_venv/bin/jupyter`.
5. Skip files that obviously launch interactive UIs (`streamlit run`, `app_*.py` for Gradio, `taipy run`) — note as `SKIP (interactive, not auto-runnable)`.
6. Record per file: `PASS` | `FAIL at cell N: <1–3 line excerpt>` | `SKIP <reason>`.

**2b. Hyperlink validation.** Three-step pipeline: extract → shape pre-flight → fetch & triage. Designed to avoid the false-positive trap where bot-walled HEAD requests look like real 404s and where a sloppy regex grabs `**` or nested `(http...)` into the URL string.

**Step 1 — Extract.** Use `markdown-it-py` (already in `course_venv`, v4.2+) to parse markdown content from every `.md` file and every markdown cell in every `.ipynb`. Walk the token stream and collect each `link_open` token's `href` attribute paired with its anchor text. **Do not use a regex.** Regex extraction grabs trailing `**`, lands inside nested `(...)`, and silently produces malformed URL strings that look like broken links but aren't — that mistake cost the maintainer real time on the 2026-05-10 Lecture 09 run. The parser is the source of truth for what URL the markdown actually points at.

**Anchor-text collection — include `code_inline` tokens, not just `text`.** When you walk the children of an inline-token group between `link_open` and `link_close`, collect the `.content` of *both* `text` tokens **and** `code_inline` tokens (the latter is what backtick-wrapped link anchors like `` [`huggingface_hub`](...) `` produce). Ignoring `code_inline` produces a false "empty anchor" finding on perfectly fine code-styled link text — that's a known earlier-version trap. Pseudo-code:

```python
for c in tok.children:
    if c.type == 'link_open':
        href = dict(c.attrs).get('href')
    elif c.type in ('text', 'code_inline') and href is not None:
        anchor += c.content
    elif c.type == 'link_close':
        if href: out.append((href, anchor))
        href = None; anchor = ''
```

**Step 2 — Shape pre-flight.** For each extracted URL, before fetching, sanity-check the string:
- Trailing `*`, `**`, `.`, `,`, or unbalanced `)` → strip and record the original-vs-cleaned pair as a **markdown source hygiene** finding under cat 5 (Should-fix, never a broken-link claim). Fetch the cleaned URL.
- URL contains `(http` or `)https` (impossible nesting) → flag as **markdown source hygiene**. Try to split at the first `(http` and fetch both halves; if neither resolves, only then mark as broken.
- URL longer than 500 chars → flag for human review.

These hygiene findings are real but cosmetic. They do **not** count as broken links and must not pull cat 5 toward `gap`.

**Step 3 — Fetch & triage.** For external URLs (`http://` / `https://`):

```
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -sL -A "$UA" -m 15 -o /dev/null -w "%{http_code}"
```

GET with redirect-follow, realistic browser UA, 15-s timeout. **Never use `-fsLI` (HEAD)** — Kaggle, Cloudflare-protected sites, and many CDNs return 404/403 to HEAD or to bot-shaped UAs while serving real content to a browser GET.

Triage the resulting status into three buckets:

| Status | Verdict | Bucket / surfaced as |
| --- | --- | --- |
| 200, 3xx | PASS | not surfaced |
| 401 | auth-gated, page exists | listed inline as a note — not a finding |
| 403, 429 | bot-walled / rate-limited | **(c) needs verification** — listed, does NOT pull tier |
| 404, 410 | confirmed broken | **(a) confirmed broken** — must-fix |
| 5xx | server error (likely transient) | **(c) needs verification** |
| timeout / connection refused | unreachable now | **(c) needs verification** |

For bucket (c), include a one-line "verify by opening in a browser" recommendation. Do not claim the link is broken on this evidence alone. If the maintainer wants a stronger verdict for stubborn (c) entries, escalate manually via the gstack `/browse` skill — but never block a report on it.

For internal links (relative paths like `../foo.md` or `./bar.ipynb`): resolve against the source file's directory and check the path exists on disk. Missing path → bucket (a) must-fix.

**Anchor text quality**: flag links whose anchor text is one of `click here`, `here`, `this`, `link`, `url`, or empty. Should-fix only — never a broken-link claim.

Record each finding with the source file, cell index (or line number), the original URL string, and the cleaned URL where applicable.

**2c. Volume estimation.** Heuristic — sanity check, not stopwatch. Compute per file, then bucket using the Phase 1 classification (`mandatory` / `optional` / `ai-fluency` / `unaccounted`):

- **Markdown reading time**: word count ÷ 150 wpm. Cover all `.md` files and all markdown cells in all `.ipynb` files.
- **Code walk-through time (fresh cost)**: count code cells and `.py` lines. Trivial cell (≤4 non-comment lines, no imports) = 90 sec; non-trivial = 180 sec. This is the cost of going through cells from scratch with no prior context — the *baseline*. Presentation time and at-home re-walk both derive from this number.
- **Exercise time**: scan `practice_exercises/` for exercise count. Default difficulty bands: trivial 15 min, realistic 45 min, stretch 90 min. If unclear, assume realistic. Tag each exercise as *required* (tied to a required goal G1–Gn) or *stretch* (tied to an optional goal O1–On, or explicitly marked stretch). The required/stretch split feeds the **Practice exercise budget** below — not the mandatory or optional totals.
- **Mandatory student load — TWO models, both required.** The skill computes and reports both, and cat-9 tiers on the **lower (more pessimistic) of the two verdicts**. One model alone is not enough — the previous version only reported the × 0.4 number and missed a 5-notebook / 84-mandatory-code-cell Lecture 11 as `solid`.
  - **(a) At-home, attended-class model** = reading + (mandatory walk-through × 0.4). The **× 0.4** models at-home re-walk after the student has already seen the cells in class — re-running, skimming, deepening understanding, not fresh exploration. It is the complement of the presentation rate (× 0.6); together they sum to 1.0 × fresh walk-through, so cells are counted exactly once across in-class and at-home time. *Useful for*: the average student who attended.
  - **(b) Fresh, no-prior-context model** = reading + (mandatory walk-through × 1.0). What it actually costs to follow the lecture from cold — the student who missed the class, the teacher who skipped fast over the difficult cells, or the maintainer who wants to know if the lecture is self-contained. The README's strong-lecture standard is explicit: a first-year MSc student can follow the material *"without external help"*; that's the fresh-cost regime, not the re-walk one. **Both buckets**: `mandatory` files + `unaccounted` (when in doubt, count as mandatory).

  Report both numbers in the volume table. **Cat-9 takes the worse of the two tiers** — the × 0.4 model can look comfortable while the × 1.0 model is already in needs-work or gap, and the lecture's true student burden is somewhere between.

  **Why exercises are not in either sum.** Per the README ("*Mid-course assignments and practice exercises are optional and are graded only positively*"), practice exercises are bonus work, not required student investment. Their time is reported separately as the *Practice exercise budget* below. The rubric's mandatory targets correspondingly reflect lecture-content review only.
- **Optional student load** = reading + walk-through, summed over `optional`-bucket *notebooks* declared in `goals_NN.md`'s Optional Files section. **No multiplier** here — students hit optional content cold with no in-class preview, so the at-home cost equals the fresh walk-through cost. Practice exercises (including stretch ones) are not included; see the Practice exercise budget below.
- **Practice exercise budget** = sum over all exercises in `practice_exercises/` of their difficulty-band time. Report two sub-totals: required exercises (tied to G1–Gn) and stretch exercises (tied to O1–On or explicitly stretch). This is **reported only**, not tier-determining for cat 9, since exercises are optional bonus work per the README. A reasonable spread for a refactored lecture is ~2–6 h required + ~0.5–3 h stretch — outside that range is a should-fix on cat 4 (overload) or cat 4 (thin coverage), not a cat 9 finding.
- **AI Fluency reading time** = same sum over `ai-fluency`-bucket files. Reported separately; not added to either total.
- **Presentation time** ≈ **mandatory walk-through (fresh) × 0.6**, where the multiplier captures teacher-accelerates-over-student-alone (interaction trades against pure speed). Presentation is computed **only** over the mandatory bucket — it strictly excludes everything else:

  | Source of time | In presentation? | Reason |
  | --- | --- | --- |
  | Code cells in mandatory notebooks (`mandatory` bucket) | **Yes** — × 0.6 of fresh cost | This is the in-class walk-through |
  | Markdown cells in mandatory notebooks | **No** — students read at home | Reading is already in *Mandatory student load* (above) at × 1.0; if the teacher chooses to also read markdown aloud in class, that overruns this estimate |
  | Code or markdown in optional notebooks (`optional` bucket) | **No** | Optional / career-track material is never walked through in class per the README's mandatory/optional split |
  | AI fluency readings (`ai-fluency` bucket) | **No** | Companion at-home reading, not lecture content |
  | Practice exercises (everything in `practice_exercises/`) | **No** | Per the README, "*practice exercises are optional and graded only positively*" — they are bonus at-home work, never class time |

  If a particular lecture genuinely walks through optional content or markdown cells in class, flag it as a Should-fix on cat 9 (the heuristic will underestimate the real presentation duration) and note the under-estimate in the report. Do not silently inflate the formula.

If `goals_split_present` is false (no Optional section in `goals_NN.md`), do not guess — bucket every pedagogical file as mandatory and report optional load as `0 h (no Optional section declared)`. The rubric will pick this up under categories 1 and 9.

**Per-notebook ceiling check.** Totals alone are not enough: one elephant notebook can hide behind four lightweights and still ship with a `solid` cat-9 verdict on the totals, even though the elephant exceeds what a beginner can read in a single sitting. For every notebook in the `mandatory` bucket, compute and record:

- Fresh walk-through time (= reading + walk × 1.0).
- Code-cell count.
- Total cell count (markdown + code).

A mandatory notebook is **over-ceiling** when **any** of these exceed:
- Fresh walk-through > 75 min (target: ≤ 75 min — one sitting).
- Code cells > 25.
- Total cells > 60.

Apply the same per-notebook check to `optional` notebooks but using **2× the ceilings** (optional notebooks read in larger blocks, not weekly). Hits feed cat 9 — see the rubric below — and the report's volume table must show one row per mandatory notebook with the ceiling cells highlighted (e.g., `**110 min**` when the budget is 75 min). *The canonical case: `lec_11e_polynomial_regression.ipynb` had 31 code cells and ~110 min fresh walk-through, alone bigger than the entire targeted at-home budget for the lecture. Previous evals scored cat 9 as `strong` because the totals were within band — the per-notebook ceiling existed only as a vibe, not as a check.*

Compare against targets:
- Presentation: 2–2.5 h.
- Mandatory student load — (a) attended-class model (× 0.4): 1.5–3 h. Over-budget at >4 h; thin at <1 h.
- Mandatory student load — (b) fresh, no-prior-context model (× 1.0): 3–5 h. Over-budget at >7 h; thin at <2 h. **Cat-9 takes the worse-tier of (a) and (b).**
- Mandatory code-cell count (lecture-wide total): ≤ 70 ideal; 70–90 needs-work; >90 gap. The Lecture 09 benchmark sits at ~40-60 mandatory code cells; >90 means the lecture is unusually heavy regardless of how the per-cell time math comes out.
- Per-notebook ceiling: as above. Any single mandatory notebook over ceiling triggers a cat-9 hit on its own.
- Optional student load: 1–3 h (optional notebooks only). Over-budget at >4 h; missing at 0 h when the lecture should have it — i.e., always per the README.
- Practice exercise budget: reported only. Required + stretch sub-totals.

**2d. Decomposition signals.** Heuristic — logical consistency, not size:

- File size: warn if any single file >50 MB (GH001 ceiling). Should never trigger for teaching notebooks.
- For each notebook, scan H1/H2 headings. If two distinct top-level topics appear (e.g., "K-Means clustering" *and* "Gradio deployment"), flag as a split candidate.
- For each notebook, check whether `goals_NN.md`'s per-file description uses "and" to link two distinct nouns ("covers KMeans clustering and Gaussian mixtures") — flag for human review.
- Compare against Lecture 09's notebook count and rough size as a benchmark — significant outliers in either direction are worth noting, not penalising.
- **Description-drift scan** (feeds the cat-2 sub-check). For every file listed in `goals_NN.md`, extract the named concrete references from its description sentence — industry-use examples, dataset names, hook-example noun phrases, section citations like `*(lec_NNa §B1.3)*` — and grep the corresponding file for each. A reference that does not resolve (e.g., the description names a hook that has been replaced, or cites a section that no longer exists in the file) is a description-drift hit. Report all hits under the cat-2 should-fix sub-check with the specific drift named.
- **Markdown readability scan** (feeds the cat-3 sub-check). For every `.ipynb` in scope, walk markdown cells and compute, per cell: (a) word count, (b) longest run of consecutive non-blank source lines that contain neither `- ` / `* ` / `1.` (no list items) nor a `  \n` hard-line-break terminator (i.e., the longest unbroken prose run, measured in source lines, not rendered lines), (c) presence of a bulleted/numbered list anywhere in the cell. Report two thresholds:
  - **>200 words AND no list AND longest unbroken prose run ≥6 source lines** → flagged as a readability hit. The cell is a wall of prose where bullets and hard line breaks would scan better.
  - **>300 words** → flagged regardless of list/break presence. The cell is too long; the unit is bigger than students will read in one pass.
  Report all hits under the cat-3 should-fix sub-check with `file:cell_index` and the word count. The threshold is calibrated against the `lec_11a` rewrite (the reference for the create-skill's "Scannable markdown style" pattern): cells 0, 4, 7 of that file are ≤200 words AND use bullets/hard line breaks; they should never appear as readability hits.
- **Fine-grained duplication scan** (feeds the cat-8 sub-check). For every pair of pedagogical files in the lecture: compute coarse similarity over markdown paragraphs (>50 words) and code blocks (>10 lines) using `difflib.SequenceMatcher.ratio()` ≥ 0.8 on the lower-cased, whitespace-stripped token sequence. Flag any pair with one or more high-similarity matches. Within each notebook: scan code cells for identical or near-identical content (and, where the cached `outputs` field is populated, identical printed results — same DataFrame head, same plot title, same scalar). All hits are reported under the cat-8 should-fix sub-check; **apply the cat-3 reinforcement carve-out described in the rubric below**.
- **Self-described preview-duplication scan** (feeds the cat-8 sub-check). The verbatim duplication scan above only catches token-level overlap; **conceptual overlap** (notebook N walks the same diagnostic on the same data that notebook N+1 covers formally) frequently survives a SequenceMatcher because the prose is paraphrased and the code uses a different fitted model. The reliable signal for conceptual duplication is the maintainer's own skip-callout text. For every markdown cell that contains `⏱ **Skip if running long.**` (the project's pause-point convention), extract the callout's body and check for **both** of these claims:
  - the callout names another notebook in this lecture as the formal owner (`lec_NNx`, `see lec_NNb §F`, `walked through formally in lec_NN`...), AND
  - the callout asserts nothing downstream depends on the section (`will not lose anything`, `nothing needed for lec_NNc`, `safe to skip`, `optional`...).
  When both clauses appear, the section is a **self-described preview** of content owned by the downstream notebook. Report under the cat-8 should-fix sub-check with the exact callout text and the named downstream owner. *The canonical case is `lec_11a` §9 in the first composite-strong landing of Lecture 11: a residuals-vs-fitted + QQ plot section whose own callout said "point students at `lec_11b` and skip §9 — they will not lose anything they need for `lec_11c`." It was deleted in the post-teaching update; the prevention is this scan.*
- **Section-letter integrity scan** (feeds the cat-8 sub-check). For each `.ipynb` in scope, extract every markdown header matching `^##\s+([A-Z][0-9]?)\.` (top-level section) and `^###\s+([A-Z][0-9]?)\.` (subsection) and build the ordered list of section letters per notebook. Then run three checks:
  - **Start letter**: report a hit if the first top-level section letter is not `A`. The starts-at-B pattern is the canonical case — an opening overview cell (title + "Three industry uses" + "What this notebook covers") is unlabelled, so the first lettered section ends up §B and the rest of the alphabet shifts. Fix: rename §B → §A (and shift everything down), OR turn the opening overview into an explicit §A heading.
  - **Gap detection**: report a hit if the letter sequence has a gap (e.g., `…H → J` skipping `I`, `B → D` skipping `C`). The `I → J` skip is the most common — authors sometimes skip `I` to avoid confusion with the digit `1`, but it should still be flagged so the choice is conscious.
  - **Cross-reference resolution**: extract every prose reference of the form `§[A-Z][0-9]?\b` or `[Ss]ection [A-Z]\b` in markdown cells. Each must resolve to a section header in the same notebook. Report unresolved refs with `file:cell_index` and the exact reference text.
  Each hit is a single should-fix on cat 8 with the specific letters / refs named. *The canonical case is `lec_11c` (2026-05-24): the notebook started at §B (no §A), ended with §H → §J (no §I), and the pile of stale internal cross-refs (`§G`, `§D2`, `§F4`, `§F3`, `§H`, `section E`) had to be renumbered together with the headers — exactly the change one scan should catch before review.*
- **Cross-notebook forward-pointer scan** (feeds the cat-2 description-drift sub-check). The description-drift scan above checks `goals_NN.md` against notebook content; this companion scan checks one notebook's *closing* prose against sibling notebooks' actual content. For each `.ipynb`, locate the closing section (typically the last lettered section, titled "What comes next" / "Next notebook" / "Where to next" / similar). In every markdown cell of that section, extract every `lec_NNx` mention. For each mention:
  - Verify the file exists on disk under the lecture's `reading_material/` (or lecture root for unrefactored lectures). Missing file → must-fix on cat 5.
  - If the prose makes a topic claim (e.g., *"`lec_11e` moves to polynomial regression and introduces regularisation"*), verify the topic appears in the referenced notebook's H1 title, opening overview cell, or first lettered section header. The source of truth is the referenced notebook's preamble — `# Title`, `## What this notebook covers`, `## Three industry uses`. A topic claim that fails this check is a should-fix on cat 2.
  - If the prose includes a section pointer (`lec_NNx §Y`), verify §Y exists in that file (re-using the section-letter extraction from the section-letter integrity scan). A dangling section pointer is a should-fix on cat 2.
  Report each hit with `file:cell_index — claims lec_NNx covers <topic>; lec_NNx.ipynb's preamble shows <actual topic>`. *The canonical case is `lec_11c §J` (2026-05-24): the closing section pointed to `lec_11e` for "coefficient interpretation" and `lec_11f` for "polynomial regression", but the actual files on disk were `lec_11d_advanced_linear_model_coeff_interpretation.ipynb` and `lec_11e_polynomial_regression.ipynb`. A file-rename / reshuffle had shifted the downstream notebooks one letter without anyone updating the §J pointers. The third pointer (`lec_11f` → VIF/ElasticNet/robust) happened to remain correct, which masked the bug on quick reads.*
- **Notebook-status preamble scan** (feeds the cat-1 / cat-2 sub-checks). Every pedagogical `.ipynb` should declare its mandatory/optional bucket in the first ~3 markdown cells, so a student opening the file in isolation can see its track without consulting `goals_NN.md`. The expected convention is a line of the form:
  - `**Status: Mandatory reading.**` (or the same wording embedded in the H1 title — e.g. `# Lecture 11a — Title (mandatory)`)
  - `**Status: Optional / career-track.**` (or `(optional)` / `(career-track)` in the H1)

  For each notebook in `mandatory` / `optional` buckets, scan cells 0–2 for one of these markers (case-insensitive). Then **cross-check against the `goals_NN.md` bucket**:
  - Notebook with no status marker AND bucket is mandatory → should-fix on cat 1 (mandatory notebooks should self-declare).
  - Notebook with no status marker AND bucket is optional → must-fix on cat 1 (optional notebooks must self-declare; students would otherwise treat them as required and overrun the budget).
  - Notebook declares one bucket but `goals_NN.md` lists it in the other → must-fix on cat 2 (bucket conflict — one of them is wrong).

  In addition, when an optional goal `Ox` in `goals_NN.md` points at a section *inside* a mandatory notebook (e.g. `*(file: lec_NNd §P3)*` where `lec_NNd` is mandatory), the section header in that file should carry an inline optional-callout (`> 🎯 **Optional / career-track (Ox).** ...`). A missing inline callout on a mandatory notebook's optional sub-section is a should-fix on cat 1 — without it, a student reading top-to-bottom cannot tell which parts are bonus.

  *The canonical case is `Lecture 11` (2026-05-24): all five then-mandatory notebooks lacked a status banner (only `lec_11f`, optional, self-declared), AND the embedded optional sub-sections `lec_11d §P3` (bootstrap, O2) and `lec_11e §D4` (lasso-then-OLS, O1) had no inline marker — so a student reading `lec_11d` from the top had no way to tell that the bootstrap mechanic was bonus.*

### Phase 3 — Editorial pass

Read each file once with the rubric in hand. For each finding, record:

- **Category** (1–9, see rubric)
- **Severity**: must-fix (gap or needs-work) | should-fix (solid trending down) | polish (solid trending up)
- **Evidence**: `file_path:cell_N` for notebooks, `file_path:LN` for scripts/markdown
- **Recommendation**: a specific, actionable change. Not "improve clarity" — say "rename `lec_05c.ipynb`'s cell 4 variable `x` to `temperature_celsius` and replace the magic number `0.5` with a named constant". For category 7 (real-world relevance), recommendations flag *what is missing*, not *what to add* — the future `create-improve-lecture` skill owns content suggestions.

Don't pad. If a category is genuinely fine, say so in two lines and move on.

### Phase 4 — Score and report

Score each category by selecting one tier from the rubric. Then compute the **composite tier**:

> The composite tier is the **lowest tier** across applicable categories.

Rationale: a lecture is `strong` only when nothing is missing. A single `gap` pulls the composite to `gap` because that gap is the binding constraint on improvement. `N/A` is reserved for categories that genuinely don't apply to a given lecture; it is not an escape hatch for missing content. Per the rubric, none of the nine categories is N/A by default.

Write the report to `.claude/uoa-py-course-lecture-eval-reports/<lecture-folder-name>_<YYYY-MM-DD>.md` using the template at the end of this file. Print the report path and the composite tier to the user.

## Rubric — 9 categories × 4 tiers

Calibrate strictly. `strong` requires demonstrable excellence across all sub-criteria, not merely the absence of problems. The tiers are equally weighted — fix the lowest-scoring category first.

### 1. Learning goals — explicit, measurable, complete, with required/optional split

- **gap** — `goals_NN.md` missing, empty, or one line; OR aspirational only ("understand X", "be familiar with Y"); OR `goals_split_present` is false (flat list with no Optional / Advanced / Career-track sub-section — violates the README structural requirement); OR any **optional** notebook in the lecture lacks a status preamble (students reading it cold would treat it as required and overrun the budget — see notebook-status preamble scan in Phase 2d).
- **needs work** — Required and optional sub-sections both present, but most required goals aren't observable; no clear connection to assessable behaviour. Or optional sub-section exists but is a single line / empty. OR more than half the **mandatory** notebooks lack a status preamble.
- **solid** — 5+ required goals + a populated optional sub-section; majority of required goals written as student-action verbs ("the student can write a `for` loop with `enumerate`"); a few aspirational allowed in the optional sub-section; every notebook self-declares its bucket; embedded optional sub-sections in mandatory notebooks carry inline `> 🎯 **Optional (Ox).**` callouts.
- **strong** — Every required goal is observable + measurable + cleanly mapped to one or more files; optional goals labelled explicitly and tied to the career-track files; no overlap between buckets; no gaps; every notebook + every embedded optional sub-section visibly self-declares.

### 2. Coverage — goals ↔ content, mandatory and optional

- **gap** — >30% of declared goals have no teaching material; OR >30% of pedagogical files aren't mentioned anywhere in `goals_NN.md`; OR `optional_files_section_present` is false (no labelled Optional / Further-reading Files sub-section — violates the README); OR a file is listed in `goals_NN.md` but doesn't exist on disk.
- **needs work** — Multiple goals without content; or files without goal alignment; or the Optional Files sub-section exists but is sparse (a single entry on a lecture where multiple files plausibly belong there); or goals introduced only inside exercises.
- **solid** — 1–2 minor mismatches; required Files and Optional Files sub-sections both populated; every pedagogical file appears in one of them; everything else clearly mapped.
- **strong** — Every goal traced to specific cells/sections; every pedagogical file accounted for in the correct sub-section of `goals_NN.md`; optional entries name the career-track value clearly (one line per file, not just a filename); cross-links between mandatory and optional files where one extends the other.

**Description-drift sub-check** (should-fix only — does not pull the tier on its own). Even when a file IS listed in `goals_NN.md` with the correct bucket, its prose description can become stale after content edits. Driven by the Phase 2d description-drift scan AND the cross-notebook forward-pointer scan, the eval flags the following as cat-2 should-fix findings:

- The description names specific examples (industry-use trio, hook example, dataset name) that no longer match the file's content. *Example from the 2026-05-12 Lecture 10 history: `goals_10.md` still said "industry uses: recommendation systems / nearest-neighbour retrieval / similarity baselines" after `lec_10a` cell 0 had been rewritten to use the medical-triage / few-shot-classification / honest-baseline trio.*
- The description cites a section (e.g. `*(lec_10a §B1.3 — Train / test / validation: when two splits become three)*`) that has been renamed, renumbered, or removed.
- The description's narrative verbs ("opens with X", "closes with Y") describe content that is no longer at the top / bottom of the file.
- A notebook's *closing* "What comes next" section claims a sibling `lec_NNx` covers a topic that the actual file does not — a stale forward-pointer left behind after a file rename or downstream reshuffle. *The canonical case is `lec_11c §J` (2026-05-24): its closing bullets pointed to `lec_11e` for coefficient-interpretation pitfalls (actually in `lec_11d`) and `lec_11f` for polynomial regression (actually in `lec_11e`). The third bullet (`lec_11f` → VIF/ElasticNet/robust) happened to remain correct, which is why the bug survived several review passes.*

Each drift hit appears as a single should-fix with the specific mismatch named (e.g., *"`goals_NN.md:L33` describes lec_NNa as opening with recsys / retrieval / similarity-baselines; `lec_NNa.ipynb:cell 0` now uses medical triage / few-shot embeddings / honest baseline"*, or *"`lec_11c.ipynb:§J` claims `lec_11e` revisits coefficient interpretation; the file at that name on disk is `lec_11e_polynomial_regression.ipynb` — the actual coefficient-interpretation notebook is `lec_11d`"*). A strong-tier lecture can still ship with one or two of these; each is a one-minute fix in `goals_NN.md` or the closing section.

### 3. Pedagogical scaffolding

- **gap** — Forward references throughout; concepts used before introduction; difficulty jumps are large; beginner can't follow without external help.
- **needs work** — Notable order violations; concepts introduced via exercise rather than worked example; uneven repetition.
- **solid** — Concepts introduced before used; one worked example per new idea; difficulty climbs steadily.
- **strong** — Difficulty gradient deliberate and visible; hard concepts revisited in two contexts ("explain three times" principle); explicit cross-lecture prerequisites.

**Markdown readability sub-check** (should-fix only — does not pull the tier on its own, but a large pile is a signal that the lecture is harder to read than its content warrants). Driven by the Phase 2d markdown readability scan, the eval flags:

- **Wall-of-prose cells**: markdown cells with >200 words, no bullet/numbered list, and an unbroken run of ≥6 source lines (no `  \n` hard line breaks, no list items). Beginners and teachers both skim notebook markdown; a wall of prose is the dominant cause of "I scrolled past the explanation and went straight to the code". The fix is structural: convert enumerations to bullets, break long sentences across visual lines with two trailing spaces + newline. The reference template is `lec_11a` cells 0, 4, 7 — open them side-by-side with the offending cell for the visual contrast.
- **Oversize cells**: any markdown cell >300 words. Even with bullets and line breaks present, a 300+ word cell is bigger than the unit students will read in one pass; split it across two cells with a section subheading.

Each hit is reported as `file:cell_index — <N> words; suggest bullets + hard line breaks (see lec_11a as template)`. A strong-tier lecture can still ship with one or two readability hits — they are cosmetic — but if every notebook in the lecture has 5+ hits, escalate the headline (the rubric does not move on this sub-check alone, but the prose density compounds with cat 9 over-volume and cat 8 within-notebook duplication; flag the pattern explicitly in the verdict's bottleneck line).

### 4. Exercises & assessment — required goals + optional/stretch tier

Required goals (Phase 1) drive the must-have exercises. Optional goals get optional/stretch exercises and count toward the strong tier.

- **gap** — Missing exercises file; OR solutions don't run; OR exercises require concepts the lecture didn't actually teach; OR a required goal has no exercise; OR no `lec_NN_exercises_solutions.{py,ipynb}` exists at all.
- **needs work** — Spotty required-goal coverage (one or two required goals without exercises); difficulty too uniform (all easy or all hard); some exercises unsolved in the solutions file; or no exercises tied to optional goals despite optional goals being declared.
- **solid** — Every required goal has an exercise; on-ramp + realistic levels; solutions runnable under `requirements.txt`; at least one optional/stretch exercise tied to an optional goal.
- **strong** — All of `solid` + clear easy/medium/hard tiers in the required set + at least one optional exercise per declared optional goal + solutions runnable, commented, reproducible (random seeds where relevant); optional exercises clearly labelled so beginners don't think they're required.

### 5. Code, data & references

Combines code execution, data hygiene, and hyperlink integrity (since they're all "references that must resolve"). For hyperlinks, only **bucket (a) confirmed broken** (per Phase 2b's triage) counts toward the tier — bucket (b) markdown source hygiene and bucket (c) needs verification are reported but do not pull the tier down.

- **gap** — Multiple notebooks fail to execute; OR ≥3 confirmed broken hyperlinks (bucket a); OR data paths broken; OR naming non-compliant.
- **needs work** — 1–2 cells fail; minor naming drift (`lec_05a` ↔ `lec_5a`); 1–2 confirmed broken hyperlinks (bucket a); OR a large pile of bucket-b markdown hygiene issues (≥5 — points at sloppy authoring, even if individually cosmetic).
- **solid** — All notebooks/scripts run cleanly under `course_venv`; naming matches conventions; outputs match cell claims; zero confirmed broken hyperlinks; bucket-b hygiene is clean or sparse; bucket-c needs-verification entries are listed for the maintainer.
- **strong** — All of `solid` + reproducible (random seeds where relevant); imports minimal and explicit; modern Python idioms (f-strings, pathlib, type hints where helpful); referenced sources are authoritative (Wikipedia, official docs, arxiv, .edu).

### 6. AI-fluency thread

Per the README (lines 41 and 57), AI Fluency complementary content is part of every lecture, not gated by lecture range. This category is therefore **never N/A** — every lecture is expected to carry the thread, and absence is a `gap`.

- **gap** — `ai_fluency_file_present` is false: no `read_agents_*.md` (or equivalent declared in `goals_NN.md`'s AI Fluency sub-section) exists, or the file is a stub (<200 words). The lecture violates the README's structural requirement.
- **needs work** — File present but uses outdated model names, deprecated UI flows, or vague claims; OR file exists on disk but isn't listed in `goals_NN.md`; OR content is generic (not tied to the lecture's topic).
- **solid** — `read_agents_*.md` (or equivalent) present, listed in `goals_NN.md`, with specific examples tied to the lecture's topic; current within ~6 months of the report date.
- **strong** — All of `solid` + concrete tasks for students to *try with* an agent (not just read about); honest discussion of failure modes (hallucinations, drift, context window); explicit pointer back to the optional/career-track section so students who want depth know where to go next.

`docs/Lectures_outline.md`'s "AI / Agents" table records the *current* state of the curriculum, not the *target* state. The README is the target. If a lecture's outline row is empty, that is itself a finding worth surfacing — it confirms the gap rather than excusing it.

### 7. Real-world relevance & motivation

Flag absence only — recommendations identify *what is missing*, not *what to add*.

- **gap** — No hook, no industry examples, no limitations, no career framing.
- **needs work** — Hook present but missing industry examples, OR examples present but no limitations.
- **solid** — Hook + 2 industry examples (one-liner each, naming who/for-what) + limitations explicitly stated.
- **strong** — All of `solid` + a third industry example + explicit career framing (e.g., "you'll see this in your first ML role when…").

### 8. Decomposition & structure

Logical consistency, not precise size measurement. Use Lecture 09 as the rough benchmark.

- **gap** — A notebook covers two distinct topics, OR any single file >50 MB (GH001 ceiling), OR the letter ordering doesn't reflect dependency.
- **needs work** — A notebook covers one topic but with a clear sub-topic that should be lifted out, OR notebooks are markedly larger or smaller than Lecture 09's range without justification.
- **solid** — One topic per notebook; ordering reflects dependency; sizes broadly comparable to Lecture 09.
- **strong** — All of `solid` + every notebook has a clear narrative arc (intro → development → recap); no merge or split candidates remain.

**Fine-grained duplication sub-check** (should-fix only — does not pull the tier on its own; the cat-3 carve-out below applies). Beyond the "one topic per notebook" rule above, the eval also flags duplicated content driven by the Phase 2d fine-grained duplication scan:

- **Across notebooks**: a code block of ≥10 lines appearing in two notebooks with `SequenceMatcher.ratio() ≥ 0.8` after stripping comments / whitespace; OR a markdown paragraph of >50 words appearing verbatim (or near-verbatim) in two notebooks.
- **Within a single notebook**: two code cells producing essentially the same output (same DataFrame head, same plot from the same data, same scalar print); OR a concept explained verbatim in three or more markdown cells.

The signal is typically a leftover after a content lift between files (e.g., `lec_10d` §7 being moved to `lec_10f` but not deleted from `lec_10d`), a copy-pasted boilerplate (`make_classification(...)` setup repeated in three places), or two cells written from the same template that the maintainer forgot to consolidate.

**Cat-3 reinforcement carve-out.** Cat 3's `strong` tier explicitly wants *"hard concepts revisited in two contexts (the 'explain three times' principle)."* Duplication that is *deliberate reinforcement* — a definition restated in a slightly different framing in `lec_NNa` and then deepened in `lec_NNb`, the same equation rendered once as math and once as code, the same dataset processed in two different feature subsets — is NOT a duplication finding. The test: *does the second occurrence add value the first did not?* If yes (different angle, different audience tier, different abstraction level), it is reinforcement — leave it. If no (literally the same tokens), it is mechanical duplication — flag as should-fix on cat 8 with the specific files / cells named.

**Self-described preview-duplication sub-check** (should-fix only — does not pull the tier on its own, but a single hit usually represents the deletion of an entire notebook section, so the *impact* per hit is larger than a typical cat-8 should-fix). Driven by the Phase 2d self-described preview-duplication scan, the eval flags:

- A markdown cell containing a `⏱ **Skip if running long.**` pause-point callout whose body **both** (a) names another notebook in this lecture as the formal owner of the section's content, AND (b) asserts that nothing downstream depends on the section. The combination is the maintainer's own admission that the section is a preview of content owned elsewhere, and that nothing in this lecture would break if it were removed.

The fix is almost always to delete the section (and update its forward-pointers — the recap of notebook N should explicitly hand off to notebook N+1, replacing the deleted preview). Carve-outs:

- A skip-callout that points at content in a **different lecture** (e.g., `lec_10a` flagging an aside as covered in Lecture 11) is **not** a duplication hit — cross-lecture forward-references are legitimate, the section adds value as an early preview that the current lecture cannot defer.
- A skip-callout that wraps a **deepening sub-section at a higher difficulty level** (a second worked example, an aside on a related-but-tangential topic, an optional algorithm comparison) is also not a duplication hit — that is the cat-9 pause-point pattern the rubric explicitly wants in strong-tier lectures.

The test for whether the carve-outs apply: **content provenance**. Does the callout's content already live in another notebook *in this lecture*? If yes → duplication hit. If no → legitimate pause-point. Report with the exact callout text and the named downstream owner so the maintainer can confirm.

**Section-letter integrity sub-check** (should-fix only — does not pull the tier on its own, but multiple hits on the same notebook compound: a notebook that starts at §B AND skips a letter AND has stale internal cross-refs is one the next reader will trip over). Driven by the Phase 2d section-letter integrity scan, the eval flags:

- **Starts-at-non-A**: a notebook's first top-level lettered section is not §A (typically §B because an unlabelled opening overview cell occupies §A's slot conceptually). The fix is either to rename the first lettered section to §A and shift the rest, or to label the opening overview cell explicitly as §A.
- **Skipped letter**: the lettered-section sequence has a gap (`…H → J` is the most common — authors sometimes drop `I` to avoid `1` confusion, but it should be a conscious choice rather than an editing leftover; `B → D` etc. are always leftover bugs).
- **Stale internal cross-reference**: a `§X` or `section X` reference in a markdown cell does not resolve to any header in the same notebook. This is what catches the renumbering aftermath — when sections shift, every prose pointer to them must shift too, and they almost never all get caught by hand.

Each hit is reported as `file:cell_index — <issue>` (e.g., *"`lec_11c.ipynb` starts at §B (no §A); §H is followed by §J (no §I); §G/§D2/§F4/§F3/§H/section E refs in cells 8, 12, 22, 31, 33, 35 do not resolve to any header"*). One should-fix per notebook covers all three sub-issues — don't fragment.

### 9. Volume & time budget — mandatory and optional, separately

Targets (from Phase 2c):
- Presentation: 2–2.5 h.
- Mandatory student load — **both models** required (cat 9 takes the worse-tier of the two):
  - **(a) Attended-class model (walk × 0.4)**: 1.5–3 h.
  - **(b) Fresh, no-prior-context model (walk × 1.0)**: 3–5 h.
- Mandatory **code-cell count** (lecture-wide total): ≤ 70 ideal; 70–90 needs-work; > 90 gap. The Lecture 09 benchmark is ~40–60 mandatory code cells.
- **Per-notebook ceiling** (mandatory bucket): no single notebook over fresh walk-through 75 min OR > 25 code cells OR > 60 total cells. Optional notebooks use 2× the ceilings.
- Optional / advanced student load (optional-bucket notebooks only): 1–3 h.
- Practice exercise budget: reported only, not tier-determining for cat 9 (per the README, exercises are optional bonus work).

Every axis can fail this category — cat-9 tier is the **lowest** verdict across all axes. AI Fluency reading time and the Practice exercise budget are reported separately and do **not** enter the cat-9 calculation (AI fluency is scored under category 6; exercise coverage is scored under category 4). The **presentation** axis specifically uses the mandatory bucket only — it strictly excludes optional notebooks (never walked through in class) and practice exercises (bonus work, never class time). See Phase 2c §"Presentation time" for the full exclusion table.

- **gap** — ANY of:
  - Mandatory load × 0.4 > 4 h, OR mandatory load × 0.4 < 1 h.
  - Mandatory load × 1.0 (fresh) > 7 h, OR mandatory load × 1.0 < 2 h.
  - Presentation > 3 h.
  - **Any single mandatory notebook** with fresh walk-through > 100 min OR > 35 code cells OR > 65 total cells. *One elephant is enough; the other notebooks being lightweight does not redeem the lecture.*
  - Total mandatory code cells > 90.
  - Optional load = 0 h on a refactored lecture (README requires optional/career-track material — its absence is a structural gap, distinct from category 1's gap on the goals split).
  - Optional load > 4 h (the optional track is bigger than the core, which inverts the structure).
- **needs work** — ANY of:
  - Mandatory × 0.4 in 1–1.5 h or 3–4 h.
  - Mandatory × 1.0 (fresh) in 5–7 h.
  - Presentation 2.5–3 h.
  - Any single mandatory notebook with fresh 75–100 min OR 25–35 code cells OR 50–65 total cells.
  - Total mandatory code cells in 70–90.
  - Optional load < 1 h on a lecture with an Optional section (declared but thin), OR optional 3–4 h.
- **solid** — ALL of:
  - Mandatory × 0.4 in 1.5–3 h AND mandatory × 1.0 in 3–5 h.
  - Presentation 2–2.5 h.
  - Every mandatory notebook ≤ 75 min fresh AND ≤ 25 code cells AND ≤ 60 total cells.
  - Total mandatory code cells ≤ 70.
  - Optional load 1–3 h.
- **strong** — All of `solid` + built-in pause points / Q&A buffer / explicit "skip if running long" sections in the mandatory track + the optional track is self-contained (reads cleanly without forcing a return to the mandatory notebooks).

*Regression-prevention anchor:* the per-notebook ceiling and the dual-model (× 0.4 AND × 1.0) requirement were added in the 2026-05-24 patch because three consecutive evals of Lecture 11 (`2026-05-23`, `2026-05-23b`, `2026-05-23c`) all scored cat-9 as `solid`/`strong` while in fact `lec_11e_polynomial_regression.ipynb` alone was 31 code cells and ~110 min fresh — bigger than the lecture's entire at-home target — and the five mandatory notebooks summed to 84 code cells and 5.05 h of total student work in a week. The totals × 0.4 looked fine (2.89 h); the totals × 1.0 (5.05 h) and the per-notebook ceiling were never computed. The rubric must compute both, and `solid`/`strong` requires both to be in band AND every notebook under-ceiling.

## Report template

```markdown
# Lecture <NN> evaluation — <lecture folder name>

**Date:** <YYYY-MM-DD>
**Lecture root:** `<relative path>`
**Refactor state:** <refactored | partially refactored | not refactored>
**Tutor:** Thanasis Argyriou
**Evaluator:** Claude Code (skill: uoa-py-course-lecture-eval)

## Verdict

**Composite tier:** **<single tier>**
*Bottleneck:* category <N> (<name>) — <one-line reason this category drags the composite down>.

| # | Category | Tier | One-line headline |
| - | --- | --- | --- |
| 1 | Learning goals | <tier> | <≤80 chars> |
| 2 | Coverage | <tier> | <≤80 chars> |
| 3 | Scaffolding | <tier> | <≤80 chars> |
| 4 | Exercises | <tier> | <≤80 chars> |
| 5 | Code, data & references | <tier> | <≤80 chars> |
| 6 | AI-fluency thread | <tier> | <≤80 chars> |
| 7 | Real-world relevance | <tier> | <≤80 chars> |
| 8 | Decomposition | <tier> | <≤80 chars> |
| 9 | Volume & time budget (mandatory / optional) | <tier> | <≤80 chars> |

**Structural conformance:** required-goals split = <yes/no>; optional-files section = <yes/no>; AI fluency file = <yes/no>.

**Single most important next step:** <one sentence>.

## Must-fix (gap / needs-work findings)

1. **[Cat. N]** <one-line problem statement>.
   *Evidence:* `<file>:<locator>`
   *Fix:* <concrete action>

## Should-fix (solid trending down)

1. **[Cat. N]** ...

## Polish (solid trending up)

1. **[Cat. N]** ...

## Mechanical checks

### Code execution

| File | Result | Detail |
| --- | --- | --- |
| `lec_09a_kmeans_clustering.ipynb` | PASS | 14 cells, 0 errors, 8.2s |
| `lec_09c_gradio_app_huggingface_deploy.ipynb` | SKIP | needs secret: HF_TOKEN |
| `app.py` | SKIP | interactive (Gradio), not auto-runnable |

### Hyperlinks

Three-bucket triage (per Phase 2b). Only bucket (a) counts as a broken-link finding.

- External: <N> total
  - **(a) Confirmed broken** (404/410 GET with browser UA): <N> — listed under cat 5 must-fix
  - **(b) Markdown source hygiene** (trailing `**`, nested `(http...)`, etc. — link still resolves): <N> — listed under cat 5 should-fix
  - **(c) Needs verification** (403/429/5xx/timeout — bot-walled or transient): <N> — listed below for the maintainer to spot-check; not a tier-determining finding
  - Auth-gated (401, page exists): <N> — informational only
- Internal: <N> total, <M> with missing target on disk (must-fix if any)
- Vague-anchor instances: <N> (should-fix)
- All entries cite source file + cell index / line number.

### Volume estimate

| Component | Mandatory | Optional | AI Fluency |
| --- | --- | --- | --- |
| Reading time | <N.N> h | <N.N> h | <N.N> h |
| Code walk-through (fresh) | <N.N> h | <N.N> h | — |
| Code walk-through (at-home, × 0.4) | <N.N> h | (no multiplier — students hit optional cold) | — |
| **Total student load (a) — attended-class (× 0.4)** | **<N.N> h** (target 1.5–3 h, needs-work 1–1.5 or 3–4, gap >4 or <1) | **<N.N> h** (target 1–3 h, gap if 0 or >4) | <N.N> h (reported only) |
| **Total student load (b) — fresh / no-prior-context (× 1.0)** | **<N.N> h** (target 3–5 h, needs-work 5–7, gap >7 or <2) | — | — |

**Cat-9 tiers on the worse of (a) and (b).** A `solid` cat-9 verdict requires both to be in band.

**Per-notebook ceiling check** (mandatory bucket — every notebook reported individually; flag any over-ceiling cell):

| Notebook | Fresh min | Code cells | Total cells | Tier |
| --- | ---: | ---: | ---: | --- |
| `lec_NNa_*.ipynb` | <N> | <N> | <N> | <solid / needs-work / gap> |
| ... | | | | |

Ceilings: ≤75 min fresh AND ≤25 code cells AND ≤60 total cells → solid; 75–100 min OR 25–35 code cells OR 50–65 total cells → needs-work; >100 min OR >35 code cells OR >65 total cells → gap. The worst per-notebook tier feeds the cat-9 verdict alongside the totals.

Estimated presentation time: <N.N> h (target 2–2.5 h, needs work 2.5–3 h, gap >3 h). **Mandatory walk-through (fresh) × 0.6**. Excludes: optional-bucket notebooks, AI fluency readings, practice exercises, and markdown reading in mandatory notebooks (read at home). If the teacher walks through any of these in class, the real duration overruns this estimate — flag explicitly.

Total mandatory code cells: <N> (target ≤70; needs-work 70–90; gap >90; Lecture 09 benchmark ~40–60).

**Practice exercise budget** (reported only; not tier-determining — exercises are bonus work per the README):

- Required exercises (tied to G1–Gn): <N> exercises, ~<N.N> h.
- Stretch exercises (tied to O1–On or marked stretch): <N> exercises, ~<N.N> h.
- Total: ~<N.N> h.

### Decomposition

- Notebook count: <N> (Lecture 09 benchmark: 6)
- Largest file: <name>, <size>
- Split candidates: <list or "none">
- Merge candidates: <list or "none">

## Inventory

- **Files in `reading_material/`:** <N> (<list>)
- **Files in `practice_exercises/`:** <N> (<list>)
- **Datasets committed:** <list>
- **Required goals declared in `goals_NN.md`:** <N>
- **Optional / advanced goals declared in `goals_NN.md`:** <N> (or "none — Optional section missing")
- **Mandatory pedagogical files:** <N> (<list>)
- **Optional / career-track pedagogical files:** <N> (<list> or "none — Optional Files section missing")
- **AI Fluency files:** <N> (<list> or "none — read_agents_*.md missing")
- **Unaccounted files (in folder but not listed in `goals_NN.md`):** <N> (<list or "none">)
- **Required goals with no matching content:** <N> (<list or "none">)
```

## Tone

Direct, concrete, no flattery. Every recommendation must be actionable in under an hour by someone familiar with the material. If you can't be specific, omit the finding rather than padding with vague advice.
