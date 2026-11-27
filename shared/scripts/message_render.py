#!/usr/bin/env python3
"""Renders a message (the Markdown subset of `message_markdown`) to Outlook-safe HTML, Slack or plain text.

Python 3 standard library only.

    render_html(blocks)   whole HTML document, inline styles only (no <style>, no classes)
    render_slack(blocks)  Slack mrkdwn: *bold*, _italic_, <url|text>
    render_plain(blocks)  text without markers: `text (url)` for links

Usage:
    message_render.py --to html|slack|plain [--in FILE] [--out FILE] [--copy]
        reads the message from --in, or from stdin; writes the rendering to --out, or to stdout
        (with --copy and no --out, nothing is printed but a one-line confirmation on stderr)
        --copy  html: rich text on the clipboard with the plain rendering as its text twin; slack, plain: text
    exit 0 ok, 1 invalid message, 2 usage or I/O error, 3 clipboard unavailable
"""
from __future__ import annotations

import argparse
import html as htmllib
import shutil
import subprocess
import sys
from dataclasses import replace
from itertools import groupby
from typing import Callable, List, Optional, Tuple

from message_markdown import Block, Heading, ListBlock, MessageError, Paragraph, Spans, Table, parse

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

def _slack_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _unbold(spans: Spans) -> Spans:
    return tuple(replace(sp, bold=False) for sp in spans)


def _slack_span(span) -> str:
    piece = _slack_escape(span.text)
    if span.href is not None:
        piece = "<%s|%s>" % (span.href.replace("|", "%7C").replace(">", "%3E"), piece)
    return piece


def _inline_slack(spans: Spans) -> str:
    """Wrap each run of bold spans once in `*…*` and each run of italic spans inside it once in `_…_`."""
    out = []
    for bold, bold_run in groupby(spans, key=lambda sp: sp.bold):
        inner = []
        for italic, italic_run in groupby(bold_run, key=lambda sp: sp.italic):
            text = "".join(_slack_span(sp) for sp in italic_run)
            inner.append("_%s_" % text if italic else text)
        text = "".join(inner)
        out.append("*%s*" % text if bold else text)
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


def _table_lines(table: Table, inline: Callable[[Spans], str], bullet: str,
                 label: Callable[[Spans], str]) -> List[str]:
    heads = [label(h) for h in table.header]
    lines = []
    for row in table.rows:
        parts = []
        for index, cell in enumerate(row):
            text = inline(cell)
            if not text:
                continue
            first = not parts
            if index == 0 or not heads[index]:
                parts.append(text if first else SEPARATOR + text)
            else:
                parts.append(("" if first else SEPARATOR) + "%s: %s" % (heads[index], text))
        if parts:
            lines.append(bullet + " " + "".join(parts))
    return lines


def _text_block(block: Block, inline: Callable[[Spans], str], bullet: str, bold: bool) -> str:
    if isinstance(block, Heading):
        text = inline(_unbold(block.spans) if bold else block.spans)
        return "*%s*" % text if bold and text else text
    if isinstance(block, Paragraph):
        return inline(block.spans)
    if isinstance(block, ListBlock):
        return "\n".join(("%d. %s" % (n, inline(i))) if block.ordered else "%s %s" % (bullet, inline(i))
                         for n, i in enumerate(block.items, 1))
    return "\n".join(_table_lines(block, inline, bullet, (lambda h: inline(_unbold(h))) if bold else inline))


def _join(texts) -> str:
    return "\n\n".join(t for t in texts if t) + "\n"


def render_slack(blocks: Tuple[Block, ...]) -> str:
    return _join(_text_block(b, _inline_slack, "•", True) for b in blocks)


def render_plain(blocks: Tuple[Block, ...]) -> str:
    return _join(_text_block(b, _inline_plain, "-", False) for b in blocks)


# Clipboard

class ClipboardUnavailable(RuntimeError):
    """No clipboard tool for this platform, or the tool failed."""


MAC_RICH_SCRIPT = (
    "on run argv\n"
    "set the clipboard to {\u00abclass HTML\u00bb:\u00abdata HTML%s\u00bb, string:(item 1 of argv)}\n"
    "end run"
)
LINUX_TOOLS = (
    ("wl-copy", ["wl-copy"], ["wl-copy", "--type", "text/html"]),
    ("xclip", ["xclip", "-selection", "clipboard"], ["xclip", "-selection", "clipboard", "-t", "text/html"]),
)


def _invoke(run, args: List[str], data: Optional[bytes] = None) -> None:
    try:
        done = run(args, input=data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except OSError as exc:
        raise ClipboardUnavailable("%s could not run: %s" % (args[0], exc))
    if done.returncode != 0:
        raise ClipboardUnavailable("%s exited with status %d" % (args[0], done.returncode))


def _linux_tool(which, rich: bool) -> List[str]:
    for name, text_cmd, rich_cmd in LINUX_TOOLS:
        if which(name):
            return list(rich_cmd if rich else text_cmd)
    raise ClipboardUnavailable("no clipboard tool found (wl-copy or xclip)")


def copy_rich(html: str, plain: str, platform: str = sys.platform, run=subprocess.run,
              which=shutil.which) -> None:
    """Put `html` on the clipboard as rich text; on macOS `plain` rides along as its text twin."""
    if platform == "darwin":
        if not which("osascript"):
            raise ClipboardUnavailable("osascript not found")
        script = MAC_RICH_SCRIPT % html.encode("utf-8").hex()
        _invoke(run, ["osascript", "-e", script, "--", plain])
    elif platform.startswith("linux"):
        _invoke(run, _linux_tool(which, True), html.encode("utf-8"))
    else:
        raise ClipboardUnavailable("no clipboard support on %s" % platform)


def copy_text(text: str, platform: str = sys.platform, run=subprocess.run, which=shutil.which) -> None:
    if platform == "darwin":
        if not which("pbcopy"):
            raise ClipboardUnavailable("pbcopy not found")
        _invoke(run, ["pbcopy"], text.encode("utf-8"))
    elif platform.startswith("linux"):
        _invoke(run, _linux_tool(which, False), text.encode("utf-8"))
    else:
        raise ClipboardUnavailable("no clipboard support on %s" % platform)


# Command line

RENDERERS = {"html": render_html, "slack": render_slack, "plain": render_plain}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="message_render.py", description=__doc__.splitlines()[0])
    parser.add_argument("--to", required=True, choices=sorted(RENDERERS))
    parser.add_argument("--in", dest="source", help="message file (default: stdin)")
    parser.add_argument("--out", help="output file (default: stdout)")
    parser.add_argument("--copy", action="store_true", help="put the rendering on the clipboard")
    return parser


def _read(path: Optional[str]) -> str:
    if path is None:
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _write(path: Optional[str], text: str) -> None:
    if path is None:
        sys.stdout.write(text)
    else:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code in (0, None) else 2
    try:
        blocks = parse(_read(args.source))
    except MessageError as exc:
        print("invalid message: %s" % exc, file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as exc:
        print("cannot read the message: %s" % exc, file=sys.stderr)
        return 2
    rendered = RENDERERS[args.to](blocks)
    try:
        if args.out or not args.copy:
            _write(args.out, rendered)
    except OSError as exc:
        print("cannot write the output: %s" % exc, file=sys.stderr)
        return 2
    if not args.copy:
        return 0
    try:
        if args.to == "html":
            copy_rich(rendered, render_plain(blocks))
        else:
            copy_text(rendered)
    except ClipboardUnavailable as exc:
        print("clipboard unavailable: %s" % exc, file=sys.stderr)
        return 3
    print("copied to the clipboard (%s)" % args.to, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
