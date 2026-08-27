# Dataset rules — source of truth for the "appropriate dataset selection" feedback

Distilled from `final_assignment/data_selection_guidelines.ipynb`. The `inspect_datasets.py`
script encodes the mechanical parts; the editorial pass uses this file to phrase the guidance.
**This is coaching, not enforcement** — every issue below is "here is how to choose better",
never a deduction.

## Hard-ish requirements (flag if violated, but stay encouraging)

- **Two target types across the assignment.** At least one dataset with a *continuous*
  target (regression) and at least one with a *categorical* target (classification, binary or
  multi-class). Clustering may reuse either dataset with the labels removed.
- **Dataset reuse across notebooks — judge the USE, not the count (instructor ruling,
  class-2026, reaffirmed 2026-07-29).** `submission_requirements.prompt.md` §7 asks for "at least
  two different datasets", but the operative test in grading is **whether each dataset is used
  properly for its task**, not how many distinct files were submitted.

  **Reuse is explicitly OK — no penalty, no rejection flag — provided** the student
  (a) **applies clustering properly** (e.g. scaling for the distance metric, a genuine
  k-selection / evaluation), and (b) **the dataset is genuinely fit** for the task it is reused
  for. This holds for **classification + clustering** sharing a dataset and — per the 2026-07-29
  ruling — **equally when a single dataset serves ALL THREE notebooks**. The regression notebook
  must simply take a genuinely **continuous** target, distinct from the categorical
  classification target.

  ### Is the target variable allowed among the clustering features?

  **Grade this on scientific correctness, not on a mechanical "the target must be dropped" rule**
  (instructor ruling 2026-07-29). The common reflex — "including the target is leakage" — is
  **wrong here**. Leakage is a *supervised* pathology: it means a feature carries information
  about a held-out label, inflating a measured generalisation score. Clustering predicts nothing
  and holds nothing out, so there is no score to inflate and no leakage in the technical sense.

  **Including the target is scientifically legitimate** when the aim is to describe joint
  structure — segmenting countries by governance profile *including* the corruption score, or
  players by performance profile *including* points scored, are ordinary, defensible analyses.
  The target is then simply one descriptive dimension among several.

  **The real fault to look for is CIRCULAR INFERENCE**, and only this should ever cost marks:
  - The student includes the target, then presents the resulting cluster/target alignment as a
    *discovery*, a *validation* of the clustering, or confirmation that the clusters "found" the
    classes — when that alignment is guaranteed by construction. **That is a genuine
    `model_evaluation` / interpretation finding**, anchored to the cell making the claim.
  - Compare: a student who includes the target and simply *describes* the segments (including
    their differing target levels) has done nothing wrong at all.

  So: **never** raise "the target was not removed" as a finding on its own. Read what the student
  *concludes* from it. If the conclusion does not depend on the alignment being informative, there
  is no fault. If in doubt, there is no fault — the asymmetric rule applies.

  Where the target genuinely *is* dropped, that is also fine and worth a word of praise; it is one
  valid choice, not the only correct one.

  **What this means when grading:**
  - Never emit a `rejection_flag` for reuse as such.
  - Never dock `dataset_selection` for reuse — score each dataset on its own appropriateness
    (size, columns, quality, not-forbidden).

  Rationale: the ≥2 rule exists to push students toward variety and to stop them recycling one
  supervised pipeline three times. A student who re-frames the same data as a genuine unsupervised
  problem has done the harder, more instructive thing — penalising that would punish exactly the
  understanding the requirement is meant to build.
- **Size — rows.** At least **~300 rows**. "It really doesn't matter if it is a bit less than
  300", so treat 270–300 as a soft note, < 270 as a real flag.
- **Size — columns.** At least **7 columns total** (≥ 6 features + the target), for
  explainability.
- **Rows-to-columns ratio.** Rule of thumb: rows ≥ 10 × columns. Below that → note it as a
  "barely acceptable / may be thin" caution, not a hard fail.
- **Data quality.** Each column's meaning should be understandable. For Kaggle, prefer
  "Usability Rating" > 8 (a low rating is allowed but discouraged — see the FAQ).
- **Not too large, either.** There is no upper limit in the rules, but a very large file
  (`inspect_datasets.py` sets `very_large: true` above ~50 MB) is impractical for this course —
  it makes every run slow and the notebook hard to re-execute. If a student ships a huge raw file,
  coach them to **work from a representative sample** and submit that sample (many already do,
  e.g. a `*_sample.csv`), so the notebook runs quickly and reproducibly for the grader.

## Out-of-scope data types (the course did not teach these algorithms)

Flag, and gently redirect, if the dataset is fundamentally:

- **Time series** — `y` as a function of time where the value at time *t* depends on previous
  values. (A column merely containing a date is not automatically time series — judge whether
  the modelling task is temporal.)
- **Text** data (NLP), **image** data (CV), or **audio** data.
- **Ranked / ordinal-target** problems that need ordered-logistic models (not covered) — if the
  target is naturally ordered, advise picking an appropriate algorithm or reframing.
- A **unique-identifier target** — e.g. athlete or artist *names* as the classification target.
  Each is its own category; that is not a learnable classification problem here.

## Forbidden datasets — used in the course or as library tutorials

Do **not** accept these (the list in the guidelines is explicitly *non-complete*). Match by
filename **and** by column signature, because students often rename the file:

| Dataset | Filename hints | Column-signature hints (case-insensitive substrings) |
| --- | --- | --- |
| Iris | `iris` | `sepal`, `petal`, `species` |
| Wine | `wine` | `alcohol`, `malic`, `flavanoid`, `proline` |
| Breast Cancer | `breast`, `cancer`, `wdbc` | `radius_mean`, `texture_mean`, `concavity`, `diagnosis` |
| Boston Housing | `boston`, `housing` (Boston) | `crim`, `zn`, `indus`, `nox`, `rm`, `medv`, `lstat` |
| Diabetes | `diabetes` | `pregnancies`, `glucose`, `bloodpressure`, `bmi`, `dpf`, `outcome` |
| MNIST | `mnist`, `digits` | `pixel`, or 784 numeric pixel columns |
| Mall customers | `mall`, `mall_customers` | `customerid`, `annual income`, `spending score` |
| Heart Disease | `heart` | `cp`, `trestbps`, `thalach`, `oldpeak`, `chol`, `thal`, `target`/`num` |

If a dataset matches by **column signature** but not filename (renamed), say so explicitly —
that is the most common way a forbidden dataset slips in.

### Variant / augmented copies of forbidden datasets

A signature match is **not always the class's actual data** — Kaggle hosts many synthetic or
augmented same-schema variants. When a match fires, verify before ruling: compare against the
course's actual file(s) (column overlap, row-level overlap with the original), and count how
many of the variant's features are genuinely new.

- **From the class of 2027 onwards:** a variant of a forbidden dataset is allowed **only if at
  least 50% of its features are new** relative to the forbidden original. One or two added
  columns do **not** qualify — with the same core schema, the class's tutorial solutions still
  transfer nearly verbatim, which is exactly what the forbidden list exists to prevent.
- **Class of 2026 (grandfathered):** same-family variants that are not the course's actual
  file are accepted without penalty — this rule was not published when 2026 students chose
  their datasets. (Instructor ruling 2026-07-18, first applied to a synthetic UCI-schema
  heart-disease variant: not the class file, 0% row overlap with classic UCI, 3 of 17
  columns new — scored as a normal, non-forbidden selection for 2026.)

Also forbidden: any dataset already used as a **tutorial example in the lectures**, and any
dataset **already claimed by another student** in the shared declaration sheet (the skill
cannot see that sheet — remind the student to check it themselves).

## What to do when a dataset issue is found

Phrase it as a choice the student still controls. Examples of the right register:

- *"`data/heart.csv` looks like the Heart Disease dataset, which is used in the course and
  can't be used for the assignment. Pick a dataset on a topic you're genuinely curious about —
  UCI and Kaggle (usability > 8) are good starting points."*
- *"Your regression dataset has 180 rows; the guideline asks for ~300+. A bit more data will
  make your train/test split and fine-tuning results much more trustworthy."*
- *"Only 5 columns here — aim for at least 6 features plus the target so you have something to
  explore and select features from."*
