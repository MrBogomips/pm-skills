"""Renderers of a parsed message: Outlook-safe HTML, Slack syntax and plain text.

Python 3 standard library only. The input is the block tuple of `message_markdown.parse`.

    render_html(blocks)   whole HTML document, inline styles only (no <style>, no classes)
    render_slack(blocks)  Slack mrkdwn: *bold*, _italic_, <url|text>
    render_plain(blocks)  text without markers: `text (url)` for links
"""
from __future__ import annotations

import html as htmllib
from typing import Callable, List, Tuple

from message_markdown import Block, Heading, ListBlock, Paragraph, Spans, Table

FONT = "font-family:Calibri,Arial,sans-serif;font-size:11pt;color:#1f1f1f"
CELL = "border:1px solid #bfbfbf;padding:4px 8px;" + FONT
HEAD_CELL = CELL + ";background:#f2f2f2;font-weight:bold"
TABLE = "border-collapse:collapse;margin:0 0 12px 0"
PARAGRAPH = "margin:0 0 10px 0;" + FONT
HEADING_PT = {1: 14, 2: 13}
LIST_STYLE = "margin:0 0 10px 0;padding-left:24px"
SEPARATOR = " — "


def _esc(text: str) -> str:
    return htmllib.escape(text, quote=True)


# HTML

def _inline_html(spans: Spans) -> str:
    out = []
    for span in spans:
        piece = _esc(span.text)
        if span.href is not None:
            piece = '<a href="%s">%s</a>' % (_esc(span.href), piece)
        if span.italic:
            piece = "<i>%s</i>" % piece
        if span.bold:
            piece = "<b>%s</b>" % piece
        out.append(piece)
    return "".join(out)


def _table_html(table: Table) -> str:
    def row(cells: Tuple[Spans, ...], style: str) -> str:
        return "<tr>%s</tr>" % "".join(
            '<td style="%s">%s</td>' % (style, _inline_html(c)) for c in cells)

    rows = [row(table.header, HEAD_CELL)] + [row(r, CELL) for r in table.rows]
    return '<table cellspacing="0" cellpadding="0" style="%s">%s</table>' % (TABLE, "".join(rows))


def _block_html(block: Block) -> str:
    if isinstance(block, Heading):
        return '<p style="margin:0 0 8px 0;%s;font-size:%dpt"><b>%s</b></p>' % (
            FONT, HEADING_PT[block.level], _inline_html(block.spans))
    if isinstance(block, Paragraph):
        return '<p style="%s">%s</p>' % (PARAGRAPH, _inline_html(block.spans))
    if isinstance(block, ListBlock):
        tag = "ol" if block.ordered else "ul"
        items = "".join('<li style="%s">%s</li>' % (FONT, _inline_html(i)) for i in block.items)
        return '<%s style="%s">%s</%s>' % (tag, LIST_STYLE, items, tag)
    return _table_html(block)


def render_html(blocks: Tuple[Block, ...]) -> str:
    body = "\n".join(_block_html(b) for b in blocks)
    return '<html><head><meta charset="utf-8"></head><body>\n%s\n</body></html>' % body


# Slack

def _inline_slack(spans: Spans) -> str:
    out = []
    for span in spans:
        piece = span.text
        if span.href is not None:
            piece = "<%s|%s>" % (span.href, piece)
        if span.italic:
            piece = "_%s_" % piece
        if span.bold:
            piece = "*%s*" % piece
        out.append(piece)
    return "".join(out)


def _inline_plain(spans: Spans) -> str:
    out = []
    for span in spans:
        if span.href is not None and span.href != span.text:
            out.append("%s (%s)" % (span.text, span.href))
        elif span.href is not None:
            out.append(span.href)
        else:
            out.append(span.text)
    return "".join(out)


def _table_lines(table: Table, inline: Callable[[Spans], str], bullet: str) -> List[str]:
    heads = [inline(h) for h in table.header]
    lines = []
    for row in table.rows:
        cells = [inline(c) for c in row]
        extra = ["%s%s: %s" % (SEPARATOR, heads[i], cells[i]) for i in range(1, len(cells))]
        lines.append(bullet + " " + cells[0] + "".join(extra))
    return lines


def _text_block(block: Block, inline: Callable[[Spans], str], bullet: str, bold: bool) -> str:
    if isinstance(block, Heading):
        text = inline(block.spans)
        return "*%s*" % text if bold else text
    if isinstance(block, Paragraph):
        return inline(block.spans)
    if isinstance(block, ListBlock):
        return "\n".join(("%d. %s" % (n, inline(i))) if block.ordered else "%s %s" % (bullet, inline(i))
                         for n, i in enumerate(block.items, 1))
    return "\n".join(_table_lines(block, inline, bullet))


def render_slack(blocks: Tuple[Block, ...]) -> str:
    return "\n\n".join(_text_block(b, _inline_slack, "•", True) for b in blocks) + "\n"


def render_plain(blocks: Tuple[Block, ...]) -> str:
    return "\n\n".join(_text_block(b, _inline_plain, "-", False) for b in blocks) + "\n"
