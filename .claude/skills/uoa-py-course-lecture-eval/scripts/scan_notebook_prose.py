#!/usr/bin/env python3
"""Report prose and terminology problems in the uoa_py_course notebooks.

Copy of teach-llm-system's tools/notebook_prose.py, adapted to the uoa_py_course layout;
keep the two in step. The rules are numbered P1, P2 and 1-11 in the
``uoa-py-course-create-excellent-lecture`` skill; the ``uoa-py-course-lecture-eval``
skill runs this scan in Phase 2d. This is a report, not a gate: some checks are
heuristics, so read each hit. Standard library only, Python >= 3.10.

Notebooks, under ``--root`` (default: the current directory):
  lectures_*/lecture_NN_*/reading_material/*.ipynb    teaching notebooks
  lectures_*/lecture_NN_*/practice_exercises/*.ipynb  exercises and solutions
  lectures_*/lecture_NN_*/*.ipynb                     lectures not yet refactored
Lecture folders directly under the root (teach-llm-system's layout) are read too, so the
two tools can be compared on the same notebooks. Archive folders are never read.

Teaching order: lecture number, then the letter after ``lec_NN`` (a, b, c, ... z), then
notebooks without a letter, then the practice exercises.

Mandatory or optional: ``goals_NN.md`` decides, not the letter. A notebook is optional
when the goals file names it (by file name, or by its ``lec_NNx`` prefix) under a heading
that contains "Optional", "Advanced", "Career" or "Further reading", outside the Learning
Goals section (whose optional goals also point into mandatory notebooks). Every other
notebook is mandatory, and so is every notebook of a lecture without ``goals_NN.md``.
Exercises are neither.

Checks, one id per rule:
  para-long            a prose paragraph over 3 sentences or 60 words (rule 7, P1)
  def-form             a bullet that starts with a bold term but has neither "is/are"
                       (a definition) nor a colon or a bold label ending in . : ? !
                       (a list bullet) (P2)
  def-multi-term       a definition bullet with more than one bold span (rule 1)
  def-pronoun          a definition that points back ("it", "them", "this"...) before
                       it is complete, so it cannot be read alone (rule 2)
  def-inline           a term defined in a prose paragraph ("**X**, a ...") instead of a
                       bullet (rule 4)
  term-table           a "| Term | Meaning |" table instead of definition bullets (rule 4)
  term-undefined       a bold term in a recap or "What this notebook covers" list that no
                       notebook defines (rule 4)
  bold-emphasis        bold that is not a defined term, a list anchor, a label or a callout
                       (rule 5)
  lazy-continuation    a list item's continuation line that is not indented (rule 6)
  blank-lines          two blank lines in a row (rule 6)
  single-bullet        a one-item list that is neither a definition nor a command to
                       remember (rule 8)
  list-merge           definition bullets and other bullets in one rendered list: two lists
                       separated only by a blank line render as one; put a sentence between
                       (rule 6)
  def-duplicate        a term defined in two places (defined once)
  def-in-exercises     a definition bullet in an exercises notebook (they refer back)
  used-before-defined  a term used in an earlier notebook than the one that defines it, or a
                       mandatory notebook relying on a definition in an optional one
  def-order            a definition that uses a term defined after it (rule 9)
  backref-mismatch     "term (`lec_NNx`)" pointing to a notebook that does not define the term
                       while another one does (rule 10)
  cell-words           a Markdown cell over 160 words of prose, fenced code excluded (the rule
                       is about 150)
  wall-of-prose        a Markdown cell over 200 words with no list and a run of 6 or more
                       consecutive prose source lines with neither a list item nor a
                       trailing-two-space hard break (the eval skill's readability threshold)
  oversize-cell        a Markdown cell over 300 words (the eval skill's readability threshold)
The three cell checks count the same words: prose, fenced code excluded. teach-llm-system's
cell-count check (25 code cells, 60 cells) does not apply here: the eval skill's
per-notebook ceiling covers notebook size.

Trailing-two-space hard breaks are deprecated (rule 7): they still end a prose run for
wall-of-prose, but para-long reads the lines they join as one paragraph, as Markdown
renders them.

Adapted to uoa's headings: a "## Recap" or "## Summary" heading, with or without a section
prefix ("## §J. Recap", "## 6. Summary"), marks a recap cell, and a "What this notebook
covers" heading opens a covers list like the bold label does. A ``<div>`` wrapper around a
Markdown cell is stripped.

Editorial, with ``--terms`` listing every definition and the defined terms it uses: "define,
don't describe" (rule 3), the complete chain (rule 10: every technical word a definition
relies on is defined before it) and one word, one meaning (rule 11).

Usage, from the repository root:
    python3 .claude/skills/uoa-py-course-lecture-eval/scripts/scan_notebook_prose.py
        [--root PATH] [--report | --terms | --inventory] [--only ID[,ID...]]
        [--lecture NN] [NOTEBOOK ...]
--report (default) prints "short_name cell N  check-id  excerpt" lines and a summary line
with the count per check id; --terms prints every definition bullet and a "uses:" line;
--inventory prints the candidate-term Markdown table. --lecture NN limits the output to one
lecture's notebooks, and NOTEBOOK to notebooks given by short name (``lec_11a``) or path.
Definitions and first uses are always computed over the whole course, because they cross
notebooks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

PARA_MAX_SENTENCES = 3
PARA_MAX_WORDS = 60
CELL_MAX_WORDS = 160  # the authoring rule: about 150 words per Markdown cell
WALL_MIN_WORDS, WALL_MIN_RUN = 200, 6  # wall-of-prose: words and prose source lines
OVERSIZE_WORDS = 300
NO_LETTER_RANK = 26  # a notebook without a letter after lec_NN comes after the z one
EXERCISES_RANK = 27  # exercises come after every reading notebook

_FENCE = re.compile(r"^\s*(```|~~~)")
_LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_WRAPPER = re.compile(r"^\s*<div[^>]*>\s*|\s*</div>\s*$")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE_SPAN = re.compile(r"`+[^`]*`+")
_CODE_TERM = re.compile(r"`[^`]+`")  # a term written as code, such as `Document`
_URL = re.compile(r"https?://\S+")
_POINTER = re.compile(r"`lec_\d\d[a-z]?\w*`")
_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_ARTICLE = r"(?:(?:A|An|The)\s+)?"
# - [A/An/The] **term** [(alias)] is/are ...
_DEFINITION = re.compile(
    rf"^{_ARTICLE}\*\*(?P<term>[^*]+?)\*\*(?:\s*\([^)]*\))?\s+(?:is|are)\b"
)
_ANCHOR = re.compile(rf"^\[?{_ARTICLE}\*\*")  # a linked anchor starts with "[**"
_COMMAND_ANCHOR = re.compile(r"^(\*\*)?`")
# what follows a bold term that is being defined in place
_DEFINES_AFTER = re.compile(
    r"^\s*(?:\([^)]*\)\s*)?(?:[,:—]\s+(?:a|an|the|its|one|any|which)\b|\s(?:is|are|means)\b)",
    re.IGNORECASE,
)
_POINTS_BACK = re.compile(
    r"\b(it|them|they|these|those|above|previous|this(?!\s+(?:course|notebook|lecture)))\b",
    re.IGNORECASE,
)
_ABBREV = re.compile(r"\b(e\.g|i\.e|etc|vs|cf|approx)\.", re.IGNORECASE)
_SENTENCE_END = re.compile(r"[.?!](?=\s|$)")

# uoa layout: lec_11a, instruct_03c; lecture folders lecture_NN_topic
_SHORT = re.compile(r"([a-z]+_\d\d[a-z])(?:_|$)")
_LECTURE_DIR = re.compile(r"lecture_(\d\d)(?:_|$)")
# "## Recap", "## §J. Recap and what is next", "## H. Recap", "## 6. Summary — ..."
_RECAP_HEADING = re.compile(
    r"^##\s+(?:(?:§\s*[A-Z]?\d*|[A-Z]\d*|\d+)\.?\s*(?:[—–-]\s*)?)?(?i:recap|summary)\b"
)
_SECTION_NUMBER = re.compile(r"##\s+(?:§\s*(\w+)|(\d+|[A-Z]\d*)\.)")
_OPTIONAL_HEADING = re.compile(
    r"optional|advanced|career|further reading", re.IGNORECASE
)
_GOALS_HEADING = re.compile(r"\bgoals?\b", re.IGNORECASE)
_NOTEBOOK_NAME = re.compile(r"[\w.-]+\.ipynb")


@dataclass
class Item:
    """One list item: its first paragraph (``text``) and where it sits."""

    indent: int
    text: str
    lazy: bool
    group: int  # items with the same group number form one list level


@dataclass
class Block:
    kind: str  # para, list, heading, table, code, quote, html
    text: str = ""
    items: list[Item] = field(default_factory=list)


@dataclass
class Cell:
    index: int
    kind: str  # markdown or code
    source: str
    blocks: list[Block] = field(default_factory=list)
    section: str = "intro"
    recap: bool = False


@dataclass
class Notebook:
    path: Path
    lecture: int
    rank: int  # the letter after lec_NN (a = 0), NO_LETTER_RANK or EXERCISES_RANK
    cells: list[Cell]
    optional: bool = False  # named under an optional heading of goals_NN.md

    @property
    def mandatory(self) -> bool:
        return not self.optional and not self.is_exercises

    @property
    def is_exercises(self) -> bool:
        return self.rank == EXERCISES_RANK

    @property
    def short(self) -> str:
        m = _SHORT.match(self.path.stem)
        return m.group(1) if m else self.path.stem

    @property
    def order(self) -> tuple[int, int]:
        return (self.lecture, self.rank)


@dataclass
class Definition:
    term: str
    text: str
    notebook: Notebook
    cell: int
    section: str

    @property
    def aliases(self) -> list[str]:
        if _CODE_TERM.fullmatch(self.term.strip()):
            return [
                self.term.strip()
            ]  # `Document` matches only as code, not "documents"
        names = [normalize(self.term)]
        names += [normalize(a) for a in re.findall(r"\(([^)]+)\)", self.term)]
        return [n for n in names if n]

    @property
    def body(self) -> str:
        """The definition after its bold term."""
        return _BOLD.split(self.text, maxsplit=1)[-1]


@dataclass
class Hit:
    notebook: Notebook
    cell: int
    check: str
    excerpt: str


# ---------------------------------------------------------------- parsing


def normalize(term: str) -> str:
    """Lower-case a term, drop backticks, a parenthesised alias and a plural ending."""
    t = re.sub(r"\([^)]*\)", "", term).replace("`", "").lower()
    t = " ".join(t.split())
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("s") and not t.endswith("ss") and len(t) > 3:
        return t[:-1]
    return t


def _leading(line: str) -> int:
    return len(line) - len(line.lstrip())


def _starts_block(line: str) -> bool:
    s = line.strip()
    return (
        s == ""
        or s.startswith(("#", ">", "|", "<"))
        or bool(_FENCE.match(line))
        or bool(_HR.match(line))
    )


def _parse_list(lines: list[str], i: int) -> tuple[list[Item], int]:
    items: list[Item] = []
    levels: dict[int, int] = {}  # indent -> current group number
    group_count = 0
    n = len(lines)
    while i < n:
        m = _LIST.match(lines[i])
        if not m:
            break
        indent = len(m.group(1))
        content_indent = indent + len(m.group(2)) + 1
        for deeper in [k for k in levels if k > indent]:
            del levels[deeper]
        if indent not in levels:
            group_count += 1
            levels[indent] = group_count
        body, lazy, j = [m.group(3)], False, i + 1
        while j < n and not _starts_block(lines[j]) and not _LIST.match(lines[j]):
            lazy = lazy or _leading(lines[j]) < content_indent
            body.append(lines[j].strip())
            j += 1
        items.append(Item(indent, " ".join(body), lazy, levels[indent]))
        k = j
        while k < n and lines[k].strip() == "":
            k += 1
        # a list goes on after blank lines while the next line is an item, or an
        # indented paragraph that belongs to the item above
        while k < n and k > j and _leading(lines[k]) >= 2 and not _LIST.match(lines[k]):
            while k < n and lines[k].strip() != "":
                k += 1
            while k < n and lines[k].strip() == "":
                k += 1
        if k < n and _LIST.match(lines[k]):
            i = k
            continue
        return items, j
    return items, i


def parse_blocks(source: str) -> list[Block]:
    lines = source.split("\n")
    blocks: list[Block] = []
    i, n = 0, len(lines)
    while i < n:
        line, s = lines[i], lines[i].strip()
        if s == "":
            i += 1
        elif _FENCE.match(line):
            j = i + 1
            while j < n and not _FENCE.match(lines[j]):
                j += 1
            blocks.append(Block("code", "\n".join(lines[i : j + 1])))
            i = j + 1
        elif s.startswith("#"):
            blocks.append(Block("heading", s))
            i += 1
        elif s.startswith(("|", ">")):
            j = i
            while j < n and lines[j].strip().startswith(s[0]):
                j += 1
            kind = "table" if s[0] == "|" else "quote"
            blocks.append(Block(kind, "\n".join(lines[i:j])))
            i = j
        elif s.startswith("<"):
            blocks.append(Block("html", s))
            i += 1
        elif _LIST.match(line):
            items, i = _parse_list(lines, i)
            blocks.append(Block("list", items=items))
        else:
            j, para = i + 1, [s]
            while j < n and not _starts_block(lines[j]) and not _LIST.match(lines[j]):
                para.append(lines[j].strip())
                j += 1
            blocks.append(Block("para", " ".join(para)))
            i = j
    return blocks


def markdown_of(cell: dict) -> str:
    return _WRAPPER.sub("", "".join(cell["source"])).strip("\n")


def load_notebook(
    path: Path, lecture: int, rank: int, optional: bool = False
) -> Notebook:
    raw = json.loads(path.read_text(encoding="utf-8"))
    cells: list[Cell] = []
    section = "intro"
    for index, c in enumerate(raw["cells"]):
        if c["cell_type"] != "markdown":
            cells.append(Cell(index, "code", "".join(c["source"])))
            continue
        source = markdown_of(c)
        cell = Cell(index, "markdown", source, parse_blocks(source))
        for block in cell.blocks:
            if block.kind == "heading" and block.text.startswith("## "):
                m = _SECTION_NUMBER.match(block.text)
                section = (
                    f"§{m.group(1) or m.group(2)}" if m else block.text[3:].strip()
                )
        cell.section = section
        cell.recap = any(
            b.kind == "heading" and _RECAP_HEADING.match(b.text) for b in cell.blocks
        )
        cells.append(cell)
    return Notebook(path, lecture, rank, cells, optional)


def lecture_folders(root: Path) -> list[tuple[int, Path]]:
    """Every ``lecture_NN*`` folder, in ``lectures_*/`` or directly under the root."""
    found = []
    for folder in [
        *root.glob("lectures_*/lecture_[0-9][0-9]*"),
        *root.glob("lecture_[0-9][0-9]*"),
    ]:
        m = _LECTURE_DIR.match(folder.name)
        if m and folder.is_dir():
            found.append((int(m.group(1)), folder))
    return sorted(found)


def goals_file(folder: Path) -> Path | None:
    candidates = [
        *sorted((folder / "reading_material").glob("goals_*.md")),
        *sorted(folder.glob("goals_*.md")),
    ]
    return candidates[0] if candidates else None


def optional_names(goals: Path | None) -> set[str]:
    """File names and ``lec_NNx`` prefixes that goals_NN.md lists as optional."""
    names: set[str] = set()
    if goals is None:
        return names
    headings: list[tuple[int, str]] = []  # the headings that enclose the current line
    fenced = False
    for line in goals.read_text(encoding="utf-8").split("\n"):
        if _FENCE.match(line):
            fenced = not fenced
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m and not fenced:
            level = len(m.group(1))
            headings = [h for h in headings if h[0] < level] + [(level, m.group(2))]
            continue
        titles = [title for level, title in headings if level > 1]
        if any(_GOALS_HEADING.search(t) for t in titles):
            continue
        if any(_OPTIONAL_HEADING.search(t) for t in titles):
            for name in _NOTEBOOK_NAME.findall(line):
                names.add(name)
                short = _SHORT.match(name[: -len(".ipynb")])
                if short:
                    names.add(short.group(1))
    return names


def _letter_rank(path: Path) -> int:
    m = _SHORT.match(path.stem)
    return ord(m.group(1)[-1]) - ord("a") if m else NO_LETTER_RANK


def _read(path: Path, lecture: int, rank: int, optional: set[str]) -> Notebook | None:
    short = _SHORT.match(path.stem)
    listed = path.name in optional or bool(short and short.group(1) in optional)
    try:
        return load_notebook(path, lecture, rank, listed)
    except (OSError, ValueError, KeyError) as error:
        print(f"skipped {path}: {error}", file=sys.stderr)
        return None


def course_notebooks(root: Path) -> list[Notebook]:
    """Every course notebook, in teaching order: lecture by lecture, a to z, exercises."""
    notebooks: list[Notebook | None] = []
    for lecture, folder in lecture_folders(root):
        optional = optional_names(goals_file(folder))
        for path in [
            *sorted(folder.glob("*.ipynb")),
            *sorted((folder / "reading_material").glob("*.ipynb")),
        ]:
            notebooks.append(_read(path, lecture, _letter_rank(path), optional))
        for path in sorted((folder / "practice_exercises").glob("*.ipynb")):
            notebooks.append(_read(path, lecture, EXERCISES_RANK, optional))
    return sorted(
        (nb for nb in notebooks if nb is not None),
        key=lambda nb: (nb.order, nb.path.name),
    )


# ---------------------------------------------------------------- text helpers


def _plain(text: str) -> str:
    return _LINK.sub(r"\1", _CODE_SPAN.sub("CODE", text))


def sentence_count(text: str) -> int:
    return len(_SENTENCE_END.findall(_ABBREV.sub(r"\1", _plain(text))))


class _Span:
    """A bold match found on masked text, read back from the original text."""

    def __init__(self, text: str, m: re.Match) -> None:
        self._text, self._start, self._end = text, m.start(), m.end()

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end

    def group(self, i: int = 0) -> str:
        whole = self._text[self._start : self._end]
        return whole if i == 0 else whole[2:-2]


def bold_spans(text: str) -> list[_Span]:
    """Bold spans outside inline code (``**`` inside backticks is code, not bold)."""
    masked = _CODE_SPAN.sub(lambda m: "`" + "x" * (len(m.group()) - 2) + "`", text)
    return [_Span(text, m) for m in _BOLD.finditer(masked)]


def _excerpt(text: str, width: int = 100) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def _covers_lists(cell: Cell) -> set[int]:
    """Indexes of the list blocks that follow a "What this notebook covers" label."""
    found, after_label = set(), False
    for i, block in enumerate(cell.blocks):
        if block.kind == "para":
            after_label = "what this notebook covers" in block.text.lower()
        elif (
            block.kind == "heading"
            and "what this notebook covers" in block.text.lower()
        ):
            after_label = True  # uoa writes the label as a heading too
        elif block.kind == "list" and after_label:
            found.add(i)
            after_label = False
    return found


def prose_run(source: str) -> int:
    """The longest run of consecutive prose source lines, for wall-of-prose.

    A blank line, a list item, a line ending in a trailing-two-space hard break, a
    heading, a table row, an HTML line, a rule or fenced code ends a run.
    """
    longest = run = 0
    fenced = False
    for line in source.split("\n"):
        if _FENCE.match(line):
            fenced = not fenced
            run = 0
            continue
        s = line.strip()
        if (
            fenced
            or not s
            or line.endswith("  ")
            or _LIST.match(line)
            or _HR.match(line)
            or s.startswith(("#", "|", "<"))
        ):
            run = 0
            continue
        run += 1
        longest = max(longest, run)
    return longest


def _is_definition(item: Item) -> bool:
    return bool(_DEFINITION.match(item.text))


def _definition_clause(item: Item) -> str:
    """The definition up to its first full stop, colon or semicolon after is/are."""
    rest = item.text[_DEFINITION.match(item.text).end() :]
    return re.split(r"[.:;](?=\s|$)", rest, maxsplit=1)[0]


def definitions(notebooks: list[Notebook]) -> list[Definition]:
    found = []
    for nb in notebooks:
        for cell in nb.cells:
            if cell.kind != "markdown" or cell.recap:
                continue
            covers = _covers_lists(cell)
            for i, block in enumerate(cell.blocks):
                if block.kind != "list" or i in covers:
                    continue
                for item in block.items:
                    m = _DEFINITION.match(item.text)
                    if m:
                        found.append(
                            Definition(
                                m.group("term"), item.text, nb, cell.index, cell.section
                            )
                        )
    return found


def prose_of(text: str, longer: Iterable[str] = ()) -> str:
    """The prose of ``text``: no code spans, link targets or URLs, and no longer
    defined terms that contain the term being searched ("token ID" when searching "ID")."""
    text = _URL.sub(" ", _LINK.sub(r"\1", text))
    text = _CODE_SPAN.sub(  # a notebook pointer such as `lec_01c` stays readable
        lambda m: m.group().strip("`") if _POINTER.fullmatch(m.group()) else " ", text
    )
    for other in longer:
        text = re.sub(
            rf"(?<![\w-]){re.escape(other)}(?:s|es)?(?![\w-])", " ", text, flags=re.I
        )
    return " ".join(text.split())


def longer_aliases(alias: str, aliases: Iterable[str]) -> list[str]:
    """The other aliases that contain ``alias`` as a whole word."""
    word = re.compile(rf"(?<![\w-]){re.escape(alias)}(?![\w-])", re.IGNORECASE)
    return [a for a in aliases if a != alias and word.search(a)]


def mentions(text: str, alias: str, longer: Iterable[str] = ()) -> bool:
    if _CODE_TERM.fullmatch(alias):
        return alias in text
    pattern = rf"(?<![\w-]){re.escape(alias)}(?:s|es)?(?![\w-])"
    return re.search(pattern, prose_of(text, longer), re.IGNORECASE) is not None


# ---------------------------------------------------------------- checks


def check_cell(nb: Notebook, cell: Cell, defined: set[str]) -> list[Hit]:
    hits: list[Hit] = []

    def hit(check: str, text: str) -> None:
        hits.append(Hit(nb, cell.index, check, _excerpt(text)))

    prose = "\n".join(
        b.text for b in cell.blocks if b.kind != "code"
    )  # not fenced code
    prose += "\n" + "\n".join(
        it.text for b in cell.blocks if b.kind == "list" for it in b.items
    )
    words = len(re.sub(r"<[^>]+>", " ", prose).split())
    if words > CELL_MAX_WORDS:
        hit("cell-words", f"{words} words: {cell.source}")
    if words > WALL_MIN_WORDS and not any(b.kind == "list" for b in cell.blocks):
        run = prose_run(cell.source)
        if run >= WALL_MIN_RUN:
            hit("wall-of-prose", f"{words} words, {run} prose lines: {cell.source}")
    if words > OVERSIZE_WORDS:
        hit("oversize-cell", f"{words} words: {cell.source}")
    if re.search(r"\n[ \t]*\n[ \t]*\n", cell.source):
        hit("blank-lines", cell.source)

    covers = _covers_lists(cell)
    for bi, block in enumerate(cell.blocks):
        if block.kind == "table":
            header = block.text.split("\n")[0].strip("| ").split("|")[0].strip().lower()
            if header in {"term", "word"}:
                hit("term-table", block.text)
        elif block.kind == "para":
            hits += _check_paragraph(nb, cell, block.text)
        elif block.kind == "list":
            review = cell.recap or bi in covers
            top = min(item.indent for item in block.items)
            top_items = [it for it in block.items if it.indent == top]
            if len(top_items) == 1 and not review:
                only = top_items[0]
                if not _is_definition(only) and not _COMMAND_ANCHOR.match(only.text):
                    hit("single-bullet", only.text)
            kinds = {_is_definition(it) for it in top_items}
            if len(kinds) == 2 and not review:
                hit("list-merge", " / ".join(it.text[:40] for it in top_items))
            for item in block.items:
                hits += _check_item(nb, cell, item, review, defined)
    return hits


def _check_paragraph(nb: Notebook, cell: Cell, text: str) -> list[Hit]:
    hits = []
    sentences, words = sentence_count(text), len(text.split())
    if sentences > PARA_MAX_SENTENCES or words > PARA_MAX_WORDS:
        hits.append(
            Hit(
                nb,
                cell.index,
                "para-long",
                _excerpt(f"{sentences} sentences, {words} words: {text}"),
            )
        )
    callout = text.startswith(("⏱", "⏸"))
    for k, m in enumerate(bold_spans(text)):
        label = m.start() == 0 or (k == 0 and (callout or text.startswith("[**")))
        after = text[m.end() :]
        opening_label = label and ":" in m.group(1)  # **Next: `lec_01d`**, ...
        if _DEFINES_AFTER.match(after) and not opening_label:
            hits.append(Hit(nb, cell.index, "def-inline", _excerpt(text[m.start() :])))
        elif not label:
            hits.append(
                Hit(nb, cell.index, "bold-emphasis", _excerpt(text[m.start() :]))
            )
    return hits


def _check_item(
    nb: Notebook, cell: Cell, item: Item, review: bool, defined: set[str]
) -> list[Hit]:
    hits = []

    def hit(check: str, text: str) -> None:
        hits.append(Hit(nb, cell.index, check, _excerpt(text)))

    if item.lazy:
        hit("lazy-continuation", item.text)
    bolds = bold_spans(item.text)
    anchored = bool(_ANCHOR.match(item.text)) and bool(bolds)  # "**x" never closed
    if _is_definition(item) and not review:
        if nb.is_exercises:
            hit("def-in-exercises", item.text)
        if len(bolds) > 1:
            hit("def-multi-term", item.text)
        if _POINTS_BACK.search(_plain(_definition_clause(item))):
            hit("def-pronoun", item.text)
        return hits
    if anchored and not review:
        after = re.sub(r"^\]\([^)]*\)", "", item.text[bolds[0].end() :])
        label = bolds[0].group(1).rstrip().endswith((".", ":", "?", "!"))
        if not label and not re.match(r"^\s*(?:\([^)]*\)\s*)?:", after):
            hit("def-form", item.text)
    for k, m in enumerate(bolds):
        if k == 0 and anchored:
            continue
        if review:
            if not any(a in defined for a in _known(m.group(1))):
                hit("term-undefined", item.text[m.start() :])
        elif _DEFINES_AFTER.match(item.text[m.end() :]):
            hit("def-inline", item.text[m.start() :])
        else:
            hit("bold-emphasis", item.text[m.start() :])
    return hits


def _known(bold_text: str) -> list[str]:
    """Normalised words and phrases of a bold span that a definition could match."""
    if _CODE_TERM.fullmatch(bold_text.strip()):
        return [bold_text.strip()]
    t = normalize(bold_text)
    words = t.split()
    phrases = {t}
    for size in range(1, len(words) + 1):
        for start in range(len(words) - size + 1):
            phrases.add(normalize(" ".join(words[start : start + size])))
    return sorted(phrases)


def cross_notebook_hits(notebooks: list[Notebook], defs: list[Definition]) -> list[Hit]:
    hits: list[Hit] = []
    every = [a for d in defs for a in d.aliases]
    first: dict[str, Definition] = {}
    for d in defs:
        key = normalize(d.term)
        if key in first:
            other = first[key]
            hits.append(
                Hit(
                    d.notebook,
                    d.cell,
                    "def-duplicate",
                    _excerpt(
                        f"also defined in {other.notebook.short} cell {other.cell}: {d.text}"
                    ),
                )
            )
        else:
            first[key] = d
    for d in first.values():
        for nb in notebooks:
            earlier = nb.order < d.notebook.order
            relies = nb.mandatory and not d.notebook.mandatory
            if nb is d.notebook or not (earlier or relies):
                continue
            for cell in nb.cells:
                if cell.kind == "markdown" and any(
                    unpointed_mention(
                        cell.source, a, d.notebook.short, longer_aliases(a, every)
                    )
                    for a in d.aliases
                ):
                    where = "an optional notebook" if relies else "a later notebook"
                    hits.append(
                        Hit(
                            nb,
                            cell.index,
                            "used-before-defined",
                            f"'{d.term}' is defined in {where}, {d.notebook.short} cell {d.cell}",
                        )
                    )
                    break
    return hits


def unpointed_mention(
    text: str, alias: str, owner: str, longer: Iterable[str] = ()
) -> bool:
    """A mention of ``alias`` that is not a forward gloss pointing to its owner.

    "a chat template, the recipe ... (`lec_01c` looks inside)" names the notebook that
    defines the term, or its lecture ("lecture 2"), within 150 characters: an allowed
    forward mention.
    """
    if _CODE_TERM.fullmatch(alias):
        flat = " ".join(text.split())
        pattern, flags = re.escape(alias), 0
    else:
        flat = prose_of(text, longer)
        pattern = rf"(?<![\w-]){re.escape(alias)}(?:s|es)?(?![\w-])"
        flags = re.IGNORECASE
    lecture = re.match(r"lec_(\d\d)", owner)
    pointers = [re.escape(owner.lower())]
    if lecture:
        pointers.append(rf"lecture {int(lecture.group(1))}(?!\d)")
    near = re.compile("|".join(pointers))
    return any(
        not near.search(flat[max(0, m.start() - 150) : m.end() + 150].lower())
        for m in re.finditer(pattern, flat, flags)
    )


def uses(d: Definition, defs: list[Definition]) -> list[Definition]:
    """The other definitions whose term the definition ``d`` mentions."""
    own = set(d.aliases)
    every = [a for x in defs for a in x.aliases]
    return [
        e
        for e in defs
        if e is not d
        and not own & set(e.aliases)
        and any(mentions(d.body, a, longer_aliases(a, every)) for a in e.aliases)
    ]


def order_hits(defs: list[Definition]) -> list[Hit]:
    """Prerequisite order: a definition may only use terms defined before it."""
    position = {id(d): k for k, d in enumerate(defs)}
    hits = []
    for d in defs:
        for e in uses(d, defs):
            if position[id(e)] > position[id(d)]:
                hits.append(
                    Hit(
                        d.notebook,
                        d.cell,
                        "def-order",
                        f"'{d.term}' uses '{e.term}', defined later in "
                        f"{e.notebook.short} cell {e.cell}",
                    )
                )
    return hits


_BACKREF = re.compile(r"([^()]{1,80}?)\s*\(`(lec_\d\d[a-z])`\)")


def backref_hits(notebooks: list[Notebook], defs: list[Definition]) -> list[Hit]:
    """A "term (`lec_NNx`)" pointer must lead to the notebook that defines the term."""
    owner = {}
    for d in defs:
        for a in d.aliases:
            owner.setdefault(a, d)
    hits = []
    for nb in notebooks:
        for cell in nb.cells:
            if cell.kind != "markdown":
                continue
            for m in _BACKREF.finditer(" ".join(cell.source.replace("*", "").split())):
                words = normalize(re.sub(r"`", "", m.group(1))).split()[-5:]
                for size in range(len(words), 0, -1):
                    d = owner.get(normalize(" ".join(words[-size:])))
                    if d:
                        if d.notebook.short != m.group(2):
                            hits.append(
                                Hit(
                                    nb,
                                    cell.index,
                                    "backref-mismatch",
                                    f"'{d.term}' points to {m.group(2)} but is defined in "
                                    f"{d.notebook.short} cell {d.cell}",
                                )
                            )
                        break
    return hits


def all_hits(notebooks: list[Notebook]) -> list[Hit]:
    defs = definitions(notebooks)
    defined = {a for d in defs for a in d.aliases}
    hits = []
    for nb in notebooks:
        for cell in nb.cells:
            if cell.kind == "markdown":
                hits += check_cell(nb, cell, defined)
    return (
        hits
        + cross_notebook_hits(notebooks, defs)
        + order_hits(defs)
        + backref_hits(notebooks, defs)
    )


# ---------------------------------------------------------------- output


@dataclass
class Selection:
    """Which notebooks the output shows: one lecture, named notebooks, or all."""

    lecture: int | None
    names: list[str]

    def __call__(self, nb: Notebook) -> bool:
        if self.lecture is not None and nb.lecture != self.lecture:
            return False
        return not self.names or any(
            f in (nb.short, nb.path.stem, nb.path.name) or Path(f).resolve() == nb.path
            for f in self.names
        )


def print_report(
    notebooks: list[Notebook], selected: Selection, only: set[str]
) -> None:
    hits = [
        h
        for h in all_hits(notebooks)
        if selected(h.notebook) and (not only or h.check in only)
    ]
    hits.sort(key=lambda h: (h.notebook.order, h.notebook.path.name, h.cell, h.check))
    for h in hits:
        print(f"{h.notebook.short:27} cell {h.cell:3}  {h.check:19} {h.excerpt}")
    counts: dict[str, int] = {}
    for h in hits:
        counts[h.check] = counts.get(h.check, 0) + 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "no hits"
    print(f"\n{len(hits)} hits: {summary}")


def print_terms(notebooks: list[Notebook], selected: Selection) -> None:
    """Every definition, then the defined terms it relies on (for the complete-chain read)."""
    defs = definitions(notebooks)
    for d in defs:
        if not selected(d.notebook):
            continue
        where = f"{d.notebook.short} {d.section} cell {d.cell}"
        print(f"{where:30} {d.text}")
        used = ", ".join(f"{e.term} ({e.notebook.short})" for e in uses(d, defs))
        print(f"{'':30} uses: {used or 'no other defined term'}")


def print_inventory(notebooks: list[Notebook], selected: Selection, root: Path) -> None:
    """Every candidate term with its first use and later uses (Markdown table)."""
    candidates: dict[str, dict] = {}

    def add(term: str, nb: Notebook, cell: Cell, kind: str) -> None:
        key = normalize(term)
        if not key or len(key) < 2:
            return
        entry = candidates.setdefault(
            key, {"term": term, "nb": nb, "cell": cell.index, "kinds": set()}
        )
        entry["kinds"].add(kind)

    for nb in notebooks:
        for cell in nb.cells:
            if cell.kind != "markdown" or cell.recap:
                continue
            covers = _covers_lists(cell)
            for bi, block in enumerate(cell.blocks):
                if block.kind == "para":
                    for m in bold_spans(block.text):
                        if m.start() > 0:
                            add(m.group(1), nb, cell, "prose")
                elif block.kind == "table":
                    rows = block.text.split("\n")[2:]
                    header = block.text.split("\n")[0].lower()
                    if "term" in header.split("|")[1]:
                        for row in rows:
                            term = row.strip("| ").split("|")[0]
                            add(term.replace("**", "").strip(), nb, cell, "table")
                elif block.kind == "list" and bi not in covers:
                    for item in block.items:
                        bolds = bold_spans(item.text)
                        for k, m in enumerate(bolds):
                            anchored = k == 0 and _ANCHOR.match(item.text)
                            if anchored and _is_definition(item):
                                add(m.group(1), nb, cell, "bullet")
                            elif anchored:
                                continue  # a list anchor, not a term
                            else:
                                add(m.group(1), nb, cell, "in-bullet")

    goals = [
        path.read_text(encoding="utf-8")
        for _, folder in lecture_folders(root)
        if (path := goals_file(folder)) is not None
    ]
    print("| term | first use | how | later notebooks | goals | proposal |")
    print("| --- | --- | --- | --- | --- | --- |")
    for key, e in candidates.items():
        nb = e["nb"]
        if not selected(nb):
            continue
        later = [
            other.short
            for other in notebooks
            if other.order > nb.order
            and any(
                c.kind == "markdown" and mentions(c.source, key) for c in other.cells
            )
        ]
        in_goals = any(mentions(text, key) for text in goals)
        if "bullet" in e["kinds"]:
            proposal = "keep bullet"
        elif later or in_goals:
            proposal = f"bullet in {nb.short}"
        else:
            proposal = "inline or italics"
        shown = ", ".join(later[:6]) + (" …" if len(later) > 6 else "")
        print(
            f"| {e['term']} | {nb.short} cell {e['cell']} | {'/'.join(sorted(e['kinds']))} "
            f"| {len(later)}: {shown} | {'yes' if in_goals else ''} | {proposal} |"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--root", default=".", help="the course repository (default: current directory)"
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="list the hits (default)")
    mode.add_argument("--terms", action="store_true", help="list every definition")
    mode.add_argument("--inventory", action="store_true", help="candidate terms table")
    ap.add_argument("--only", default="", help="comma-separated check ids")
    ap.add_argument("--lecture", type=int, help="limit the output to lecture NN")
    ap.add_argument("notebooks", nargs="*", help="limit the output to these notebooks")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    notebooks = course_notebooks(root)
    if not notebooks:
        print(f"no notebooks under {root}/lectures_*/lecture_NN_*/", file=sys.stderr)
        return 2
    selected = Selection(args.lecture, args.notebooks)
    if not any(selected(nb) for nb in notebooks):
        wanted = [f"lecture {args.lecture:02d}"] if args.lecture is not None else []
        wanted += args.notebooks
        print(f"no notebook matches: {', '.join(wanted)}", file=sys.stderr)
        return 2
    if args.terms:
        print_terms(notebooks, selected)
    elif args.inventory:
        print_inventory(notebooks, selected, root)
    else:
        only = {c.strip() for c in args.only.split(",") if c.strip()}
        print_report(notebooks, selected, only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
