---
name: uoa-post-linkedin
description: Use this skill to draft English-language LinkedIn posts announcing updates to the UoA "Python for Data Science, ML and AI" MSc course. Trigger on requests like "draft the next linkedin post", "write the linkedin post about <theme>", "linkedin post for the course updates", "continue the course post series", "mark post N as published", or "rebuild the linkedin series plan". The series plan (themes, evidence, status) is the file admin_docs/linkedin_posts/series_plan.md — this skill reads it, gathers and VERIFIES evidence from git history and repo files, writes one plain-text post draft per invocation to admin_docs/linkedin_posts/post_NN_<slug>.md, and updates the plan's status column. It never publishes anything (no LinkedIn API — the maintainer copies the text out and posts manually), never invents numbers or features not verifiable in the public repo, and never mentions students, grades, PII, secrets, or gitignored private content. Do NOT use this skill to write feedback or grades (separate skills exist), to edit lecture material, or to post to any platform automatically. One post per invocation unless the user explicitly asks for the whole series.
---

# LinkedIn post drafting for the UoA Python course

You are drafting **one** LinkedIn post (unless told otherwise) in the **maintainer's first-person
voice**, in **English**, announcing real, verifiable improvements to the course repo
(`https://github.com/argythana/uoa_py_course`, public). The output is a draft file the
maintainer reviews and posts manually — this skill **never publishes**.

## Source of truth

`admin_docs/linkedin_posts/series_plan.md` holds the post series: one row per post with theme,
evidence pointers, and status (`planned` → `drafted` → `published`). Read it first, always.

- **If the plan file is missing**, rebuild it: run
  `git log --since=<start-of-year> --pretty=format:'%ad %s' --date=short`, group the commits
  into 4–7 thematic areas, propose the grouping to the user, then write the plan using the
  same table format described below before drafting anything.
- **Which post to draft**: the theme the user named, else the first row with status `planned`.
- **"Mark post N published"**: set status to `published`, record the date and the post URL the
  user provides, and stop — no drafting.

## Workflow

1. **Read the plan row.** It lists evidence commits, key file paths, and candidate numbers.
2. **Verify everything you will claim.** Re-run the row's git log command(s); open the key
   files; recount any number (lectures rebuilt, commits, packages) rather than trusting the
   plan — the repo may have moved on since the plan was written. A claim that cannot be
   verified in the repo right now does not go in the post.
3. **Collect 2–3 concrete specifics.** Real file names, real library names, real before/after
   facts ("final assignment moved from .docx to .ipynb") beat adjectives. Prefer facts a
   reader can check by opening the public repo.
4. **Draft** into `admin_docs/linkedin_posts/post_NN_<slug>.md` using
   `references/post_template.md`. The post body must be **plain text ready to paste into
   LinkedIn** — see format rules below.
5. **Self-check** against the checklist below; fix, don't annotate.
6. **Update the plan row** to `drafted` with today's date. Tell the user where the draft is
   and quote the post body in your reply so they can read it without opening the file.

## LinkedIn format rules (the craft)

`references/style_guide.md` holds the full craft (anti-AI-tell vocabulary and structures, hook
angles, algorithm-informed reach rules, and what this skill borrows vs rejects from public
LinkedIn skills). Read it. The essentials, inline:

- **Plain text only.** LinkedIn renders no Markdown: no `**bold**`, no `#` headers, no
  `[links](...)`. Bare URLs are fine. Unicode bullets (`•`, `→`) are fine. 0–3 emoji total.
- **The hook is the first ~200 characters** — that's all that shows before "…see more", and
  the "see more" click is itself a ranked engagement signal, so the first line earns it. State
  the most interesting concrete fact; never clear your throat or open with "I'm excited to
  announce". Honest angles: before/after, a concrete number, a plain state-contrast. Never
  manufacture surprise the content can't back.
- **Short paragraphs**: 1–3 lines each, blank line between. Total 900–1,600 characters
  target (the lower half, ≈1,000–1,300, tends to get read to the end); 3,000 is LinkedIn's
  hard cap. Never pad to hit a number.
- **One honest limitation** ("lectures 14–16 are still on the old format") — credibility
  beats polish. Vary the limitation across the series; don't reuse the same one twice running.
- **Em-dashes are the #1 AI tell of 2026 — ration them.** At most ~2 " — " in a whole post,
  and only where no other punctuation works; prefer a colon, period, comma, or parentheses.
  A draft with 5+ em-dashes reads as machine-written; rewrite the extras.
- **End with**: one call-to-action + the repo URL (or a deeper path if the post is about one
  area), a series footer line `— Post N/6 on this year's course rebuild`, then 3–5 theme-
  appropriate hashtags on the last line — **never 6+ (it measurably drops reach)** — and don't
  repeat the identical set every post. External links in the body suppress reach: the URL may
  stay in the body (transparency, our default) OR move to the first comment; offer the
  first-comment option in the maintainer notes and let the maintainer choose.
- **Voice**: first-person instructor-maintainer. Concrete, plain, quietly proud. Banned:
  "game-changer", "revolutionize", "🚀 excited to announce", "in today's fast-paced world",
  plus the AI-slop vocabulary in `references/style_guide.md` (leverage, delve, unlock, harness,
  streamline, foster, seamlessly, robust, "deep dive", …) and its AI-fingerprint structures
  (rule-of-three-for-rhythm, "That's it.", "And that's okay.", "Not X. Y." snapbacks). No
  sentence that could appear in any other course's post. The course openly uses Claude Code /
  Codex to build and maintain material — say so plainly when relevant; it is part of the story,
  not a confession.

## Hard guards (non-negotiable)

- **No student names, grades, submissions, or any PII** — ever, in any form, including
  "anonymized" examples. Posts about grading/feedback automation describe the *system* only.
- **No secrets**: nothing from `.env`, no tokens, no authenticated URLs, no eClass
  credentials or internal endpoints.
- **Public-repo evidence only.** If the supporting material lives in a gitignored path
  (`students_work/`, `admin_docs/`, `.claude/skills/` while still ignored…), either describe
  it generically without paths or leave it out. Never paste content from gitignored files
  into a post. (The series plan and drafts themselves live in `admin_docs/linkedin_posts/`
  by design — they are private working documents, not evidence; every claim in a post must
  still be independently verifiable in the public repo.)
- Numbers in a published post are commitments — verify each one at draft time (step 2).

## Self-check before finishing

- [ ] First 200 chars work as a standalone hook (count them).
- [ ] Body is plain text — would survive copy-paste into LinkedIn unchanged.
- [ ] Every number and named artefact verified against the repo this session.
- [ ] No PII, no secrets, no gitignored content.
- [ ] Total length 900–1,600 chars (report the count in the metadata block).
- [ ] **≤2 em-dashes; no banned vocabulary or AI-fingerprint structures** (see
      `references/style_guide.md`). Grep the body for " — " and the banned-word list.
- [ ] CTA + URL, series footer, 3–5 hashtags (never 6+), honest limitation not reused from
      the previous post.
- [ ] Link-in-first-comment option noted for the maintainer.
- [ ] Plan row updated.
