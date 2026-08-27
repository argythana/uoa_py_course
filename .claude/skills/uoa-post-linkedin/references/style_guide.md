# LinkedIn style guide — craft rules for `uoa-post-linkedin`

The detailed *writing* craft, split out of SKILL.md (mirrors the reference-file structure of
the strongest public LinkedIn-writing skills). SKILL.md owns the workflow + hard guards; this
file owns voice, hooks, and the anti-AI-tell rules. Read both before drafting.

## What this skill borrows from public LinkedIn skills — and what it rejects

Surveyed 2026-07-21: `kvsdileep/linkedin-writer` (anti-slop + 3-step hook), `attainmentlabs/
linkedin-algorithm-skill` (engagement signals), `aiskilloftheweek/...linkedin-hook-generator`
(7 hook angles), `sergebulaev/linkedin-skills` (humanizer + cadence).

**Adopted** (craft that keeps our honesty intact): the anti-AI-tell vocabulary and structure
list, the em-dash caution, the 3–5 hashtag reach rule, the "external link suppresses reach"
finding, and the framing that the first line earns the "see more" click.

**Rejected** (clashes with an evidence-first academic voice): engagement-bait hooks ("the
secret nobody tells you", "revenue impact", manufactured curiosity gaps), contrarian hot-takes
and "snapback" tension, and AI-detector-gaming as a goal. Our posts read as human because they
ARE the maintainer's considered voice announcing real work, not because they dodge a detector.
Every claim stays verified against the public repo (SKILL.md step 2); no engagement tactic ever
overrides the hard guards.

## Anti-AI-tell rules ("does this read like a person wrote it?")

**Em-dashes — the single most-cited AI tell of 2026.** Do not pepper a post with " — ". Use at
most one or two in a whole post, and only where no other punctuation works. Prefer a colon, a
period, a comma, or parentheses. This is a density rule, not a ban: one deliberate dash is
fine, six is a tell. (Rule of thumb: if a draft has more than ~2 em-dashes, rewrite the extras.)

**Banned vocabulary** (in addition to SKILL.md's list): leverage, delve, unlock, harness,
streamline, foster, seamless(ly), robust, deeply, truly, fundamentally, inherently, "deep
dive", "dive into", "here's the thing", "let that sink in", "in today's <X>", "lean into",
supercharge, elevate, "at the end of the day".

**Banned structures** (AI fingerprints):
- Rule-of-three lists used for rhythm ("faster, cheaper, better") — vary the item count.
- Performative simplicity: "That's it." / "Simple." as a standalone line.
- False reassurance: "And that's okay."
- Binary snapback: "Not X. Y." as a manufactured pivot.
- 3+ sentences of the same length in a row — vary sentence length so the rhythm is uneven.

## Hooks — the first line earns the "see more" click

The "see more" click is itself a ranked engagement signal, so the first ~200 chars are the
whole game. Pick ONE honest angle; never manufacture surprise the content cannot back:
- **Before/after** (our default for a rebuild story): "used to end at model.fit(); this year it
  ends at MLflow."
- **Concrete number**: "20 packages I maintain by hand become 288 my students install."
- **Plain state contrast**: "For years the final assignment was a Word document. Now it is
  three notebooks."
Avoid: "I'm excited/thrilled to announce", clearing your throat before the point, or opening
with a question.

## Algorithm-informed structure (from the engagement-signals skill)

- **Hashtags: 3–5, never 6+.** 6+ correlates with a measurable reach drop.
- **External links suppress reach.** LinkedIn down-ranks posts with an outbound link in the
  body. For a repo-sharing post the link IS the point, so two acceptable patterns:
  (a) keep the URL in the body — transparency wins, mild reach cost; or (b) end the body with
  "repo link in the first comment" and the maintainer posts the URL as the first comment.
  Offer (b) in the maintainer notes and let the maintainer choose per post; do not silently
  drop the link.
- **First 60–90 minutes matter** (LinkedIn refreshes embeddings early), so early replies help.
  This is a *posting* decision, not a drafting one — surface it as a one-line maintainer note,
  never bake it into the body.
- **Length**: the 900–1,600 target stands; the lower half (≈1,000–1,300) tends to get read to
  the end. Never pad to hit a number.
