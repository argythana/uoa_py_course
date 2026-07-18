# Post draft file template

Each draft lives at `admin_docs/linkedin_posts/post_NN_<slug>.md` and follows this layout.
The **Post body** section is the exact plain text to paste into LinkedIn — nothing in it
may rely on Markdown rendering.

```markdown
# Post NN — <theme title>

| field | value |
| --- | --- |
| status | drafted |
| drafted | YYYY-MM-DD |
| published | — (date + LinkedIn URL once posted) |
| char count | NNNN |
| evidence commits | <short hashes or `git log` range used> |

## Post body

<plain text, ready to paste — hook line first, blank lines between short paragraphs,
CTA + URL, series footer, hashtags on the last line>

## Notes for the maintainer

- <anything the maintainer should double-check before posting, e.g. "add a screenshot
  of the MLflow UI", "post 2 should go live before this one">
```

Keep the notes section short; it is for the human, not part of the post.
