"""Parser of the Markdown subset used to write chat and email messages.

Python 3 standard library only. The subset: `#` and `##` headings, paragraphs, one-level `- ` and `1. ` lists,
pipe tables with a `|---|` separator row, inline `**bold**`, `*italic*` and `[text](url)` (bold or italic may
wrap a link). Everything else is literal text. Links are limited to ALLOWED_SCHEMES; anything else is refused.

    parse(text) -> tuple of blocks; raises MessageError("line N: reason") on invalid input
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

ALLOWED_SCHEMES = ("http", "https", "mailto")

SCHEME_RE = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*):")
HEADING_RE = re.compile(r"^(#{1,2}) +(\S.*)$")
BULLET_RE = re.compile(r"^- +(\S.*)$")
NUMBERED_RE = re.compile(r"^[0-9]+\. +(\S.*)$")
SEPARATOR_RE = re.compile(r"^\|(\s*:?-+:?\s*\|)+\s*$")
LINK_RE = re.compile(r"(?<!!)\[([^\[\]]+)\]\(((?:[^()\s]|\([^()\s]*\))*)\)")
BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
ITALIC_RE = re.compile(r"\*(?=\S)([^*]+?)(?<=\S)\*")
INLINE_RE = re.compile("|".join("(?P<%s>%s)" % (n, r.pattern) for n, r in
                                (("link", LINK_RE), ("bold", BOLD_RE), ("italic", ITALIC_RE))))
# Inside a link text only emphasis is allowed, not another link.
EMPHASIS_RE = re.compile("|".join("(?P<%s>%s)" % (n, r.pattern) for n, r in
                                  (("bold", BOLD_RE), ("italic", ITALIC_RE))))


class MessageError(ValueError):
    """Invalid message; `line` is 1-based and the text reads `line N: <reason>`."""

    def __init__(self, line: int, reason: str) -> None:
        super().__init__("line %d: %s" % (line, reason))
        self.line = line


@dataclass(frozen=True)
class Span:
    text: str
    bold: bool = False
    italic: bool = False
    href: Optional[str] = None


Spans = Tuple[Span, ...]


@dataclass(frozen=True)
class Heading:
    level: int
    spans: Spans


@dataclass(frozen=True)
class Paragraph:
    spans: Spans


@dataclass(frozen=True)
class ListBlock:
    ordered: bool
    items: Tuple[Spans, ...]


@dataclass(frozen=True)
class Table:
    header: Tuple[Spans, ...]
    rows: Tuple[Tuple[Spans, ...], ...]


Block = Union[Heading, Paragraph, ListBlock, Table]


def check_url(url: str, line: int) -> str:
    match = SCHEME_RE.match(url)
    if match is None or match.group(1).lower() not in ALLOWED_SCHEMES:
        raise MessageError(line, "link %r is not http, https or mailto" % url)
    return url


def inline(text: str, line: int, bold: bool = False, italic: bool = False,
           href: Optional[str] = None) -> Spans:
    """Tokenize inline markup; unmatched markers stay as text."""
    spans: List[Span] = []
    pattern = EMPHASIS_RE if href is not None else INLINE_RE
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            spans.append(Span(text[pos:match.start()], bold, italic, href))
        spans.extend(_match_spans(match, line, bold, italic, href))
        pos = match.end()
    if pos < len(text):
        spans.append(Span(text[pos:], bold, italic, href))
    return tuple(spans)


def _match_spans(match: "re.Match[str]", line: int, bold: bool, italic: bool,
                 href: Optional[str]) -> Spans:
    kind = match.lastgroup
    if kind == "link":
        inner, url = LINK_RE.fullmatch(match.group(0)).groups()
        return inline(inner, line, bold, italic, check_url(url, line))
    pattern = BOLD_RE if kind == "bold" else ITALIC_RE
    inner = pattern.fullmatch(match.group(0)).group(1)
    return inline(inner, line, bold or kind == "bold", italic or kind == "italic", href)


def split_cells(line: str) -> List[str]:
    """Cells of a pipe-table row; `\\|` is a literal pipe."""
    body = line.strip()[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", body)]


def _table(lines: List[str], start: int) -> Tuple[Table, int]:
    """Parse the table at lines[start]; returns it and the index after its last row."""
    header = split_cells(lines[start])
    if len(split_cells(lines[start + 1])) != len(header):
        raise MessageError(start + 2, "separator has %d columns, header has %d"
                           % (len(split_cells(lines[start + 1])), len(header)))
    rows = []
    index = start + 2
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        cells = split_cells(lines[index])
        if len(cells) != len(header):
            raise MessageError(index + 1, "row has %d cells, header has %d" % (len(cells), len(header)))
        rows.append(tuple(inline(c, index + 1) for c in cells))
        index += 1
    head = tuple(inline(c, start + 1) for c in header)
    return Table(head, tuple(rows)), index


def _is_table_start(lines: List[str], index: int) -> bool:
    return (lines[index].startswith("|") and index + 1 < len(lines)
            and SEPARATOR_RE.match(lines[index + 1].strip()) is not None)


def _list(lines: List[str], start: int) -> Tuple[ListBlock, int]:
    ordered = NUMBERED_RE.match(lines[start]) is not None
    pattern = NUMBERED_RE if ordered else BULLET_RE
    items = []
    index = start
    while index < len(lines):
        match = pattern.match(lines[index].rstrip())
        if match is None:
            break
        items.append(inline(match.group(1), index + 1))
        index += 1
    return ListBlock(ordered, tuple(items)), index


def _starts_block(lines: List[str], index: int) -> bool:
    line = lines[index].rstrip()
    return bool(HEADING_RE.match(line) or BULLET_RE.match(line) or NUMBERED_RE.match(line)
                or _is_table_start(lines, index))


def _paragraph(lines: List[str], start: int) -> Tuple[Paragraph, int]:
    parts = [lines[start].strip()]
    index = start + 1
    while index < len(lines) and lines[index].strip() and not _starts_block(lines, index):
        parts.append(lines[index].strip())
        index += 1
    return Paragraph(inline(" ".join(parts), start + 1)), index


def parse(text: str) -> Tuple[Block, ...]:
    lines = text.splitlines()
    blocks: List[Block] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        heading = HEADING_RE.match(line)
        if not line.strip():
            index += 1
        elif heading:
            blocks.append(Heading(len(heading.group(1)), inline(heading.group(2), index + 1)))
            index += 1
        elif BULLET_RE.match(line) or NUMBERED_RE.match(line):
            block, index = _list(lines, index)
            blocks.append(block)
        elif _is_table_start(lines, index):
            block, index = _table(lines, index)
            blocks.append(block)
        else:
            block, index = _paragraph(lines, index)
            blocks.append(block)
    if not blocks:
        raise MessageError(1, "the message is empty")
    return tuple(blocks)
