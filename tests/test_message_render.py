"""Tests of the message Markdown subset parser."""
from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from _support import SCRIPTS  # noqa: F401  (puts shared/scripts on sys.path)

import message_markdown as mm
import message_render as mr


def _all_spans(block):
    """Yield every span of any block type."""
    if isinstance(block, (mm.Heading, mm.Paragraph)):
        yield from block.spans
    elif isinstance(block, mm.ListBlock):
        for item in block.items:
            yield from item
    else:
        for cell in block.header:
            yield from cell
        for row in block.rows:
            for cell in row:
                yield from cell


class ParseTest(unittest.TestCase):
    def test_blocks(self):
        blocks = mm.parse("# Requests\n\nHi **Ada**, *please* see [PR 42](https://example.com/p/42).\n\n1. one\n2. two\n\n- a\n- b\n")
        self.assertEqual([type(b).__name__ for b in blocks], ["Heading", "Paragraph", "ListBlock", "ListBlock"])
        self.assertEqual(blocks[1].spans[1], mm.Span("Ada", bold=True))
        self.assertEqual(blocks[1].spans[3], mm.Span("please", italic=True))
        self.assertEqual(blocks[1].spans[5], mm.Span("PR 42", href="https://example.com/p/42"))
        self.assertTrue(blocks[2].ordered)
        self.assertFalse(blocks[3].ordered)

    def test_table(self):
        t = mm.parse("| Who | By |\n|---|---|\n| **Ada L.** | 2026-11-30 |\n| a \\| b | x |\n")[0]
        self.assertEqual(len(t.header), 2)
        self.assertEqual(len(t.rows), 2)
        self.assertEqual(t.rows[0][0], (mm.Span("Ada L.", bold=True),))
        self.assertEqual(t.rows[1][0], (mm.Span("a | b"),))

    def test_ragged_table_is_refused(self):
        with self.assertRaises(mm.MessageError) as ctx:
            mm.parse("| Who | By |\n|---|---|\n| Ada |\n")
        self.assertEqual(ctx.exception.line, 3)
        self.assertTrue(str(ctx.exception).startswith("line 3: "))

    def test_disallowed_scheme_is_refused(self):
        for url in ("javascript:alert(1)", "file:///etc/passwd", "JAVASCRIPT:x", "example.com/x"):
            with self.assertRaises(mm.MessageError):
                mm.parse("see [x](%s)" % url)

    def test_allowed_schemes_are_accepted_in_any_case(self):
        for url in ("HTTPS://example.com", "mailto:ada@example.com", "http://example.com"):
            span = mm.parse("[x](%s)" % url)[0].spans[0]
            self.assertEqual(span.href, url)

    def test_outside_subset_is_literal(self):
        text = "```\ncode\n```\n\n![img](https://example.com/a.png)\n\n- a\n  - nested\n\n2 * 3 = 6"
        out = "".join(s.text for b in mm.parse(text) for s in _all_spans(b))
        for piece in ("```", "code", "![img]", "nested", "2 * 3 = 6"):
            self.assertIn(piece, out)
        for block in mm.parse(text):
            for span in _all_spans(block):
                self.assertIsNone(span.href)

    def test_empty_message_is_refused(self):
        with self.assertRaises(mm.MessageError):
            mm.parse("  \n\n")

    def test_paragraph_lines_are_joined_with_a_space(self):
        blocks = mm.parse("one\ntwo\n\nthree")
        self.assertEqual(blocks[0].spans, (mm.Span("one two"),))
        self.assertEqual(len(blocks), 2)

    def test_bold_around_a_link_and_unmatched_markers(self):
        spans = mm.parse("**[x](https://example.com)** and *open")[0].spans
        self.assertEqual(spans[0], mm.Span("x", bold=True, href="https://example.com"))
        self.assertEqual("".join(s.text for s in spans[1:]), " and *open")

    def test_headings_two_levels_only(self):
        blocks = mm.parse("# One\n\n## Two\n\n### Three")
        self.assertEqual([b.level for b in blocks[:2]], [1, 2])
        self.assertIsInstance(blocks[2], mm.Paragraph)


SAMPLE = ("## Requests\n\n| Who | What | By | References |\n|---|---|---|---|\n"
          "| **Ada L.** | **Review the go-live runbook**; *done when the PR is approved* | **2026-11-30** | [PR 42 · Go-live runbook](https://example.com/acme/pull/42) |\n\n"
          "R&D says a < b.\n\n1. Dry run: **2026-12-09**\n")


class RenderTest(unittest.TestCase):
    def test_html(self):
        html = mr.render_html(mm.parse(SAMPLE))
        self.assertIn('<a href="https://example.com/acme/pull/42">PR 42 · Go-live runbook</a>', html)
        self.assertIn("<b>Ada L.</b>", html)
        self.assertIn("<i>done when the PR is approved</i>", html)
        self.assertIn("R&amp;D says a &lt; b.", html)
        self.assertIn("border-collapse:collapse", html)
        self.assertIn("<ol", html)
        self.assertNotIn("<style", html)
        self.assertNotIn("class=", html)
        self.assertTrue(html.startswith("<html>"))

    def test_html_escapes_href_and_text(self):
        html = mr.render_html(mm.parse('[a "q" <b>](https://example.com/?x=1&y="2")'))
        self.assertIn("&amp;y=", html)
        self.assertNotIn("<b>]", html)
        self.assertNotIn('"2"', html)

    def test_slack(self):
        out = mr.render_slack(mm.parse(SAMPLE))
        self.assertIn("*Requests*", out)
        self.assertIn("• *Ada L.* — What: *Review the go-live runbook*; _done when the PR is approved_ — By: *2026-11-30* — References: <https://example.com/acme/pull/42|PR 42 · Go-live runbook>", out)
        self.assertIn("R&amp;D says a &lt; b.", out)
        self.assertNotIn("|---", out)

    def test_slack_escapes_mentions_and_url_breakers(self):
        out = mr.render_slack(mm.parse("<!channel> and <@U123>\n\n[x](https://example.com/a|b>c)"))
        self.assertIn("&lt;!channel&gt; and &lt;@U123&gt;", out)
        self.assertNotIn("<!channel>", out)
        self.assertIn("<https://example.com/a%7Cb%3Ec|x>", out)

    def test_slack_heading_is_one_bold_pair(self):
        out = mr.render_slack(mm.parse("## **Hi** there\n\n| **What** | B |\n|---|---|\n| a | b |\n"))
        self.assertIn("*Hi there*", out)
        self.assertIn("• a — B: b", out)
        self.assertNotIn("**", out)

    def test_empty_cells_and_empty_tables(self):
        text = "| A | B |\n|---|---|\n|  | **x** |\n\n| H |\n|---|\n\ntail"
        for out, bullet in ((mr.render_slack(mm.parse(text)), "•"), (mr.render_plain(mm.parse(text)), "-")):
            self.assertNotIn("\n\n\n", out)
            self.assertIn("%s B: " % bullet, out)
            self.assertNotIn("%s  " % bullet, out)

    def test_plain(self):
        out = mr.render_plain(mm.parse(SAMPLE))
        self.assertIn("- Ada L. — What: Review the go-live runbook; done when the PR is approved — By: 2026-11-30 — References: PR 42 · Go-live runbook (https://example.com/acme/pull/42)", out)
        self.assertNotIn("*", out)
        self.assertIn("1. Dry run: 2026-12-09", out)


class _Done:
    returncode = 0


def _ok():
    return _Done()


def _run(argv, stdin_text=""):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(stdin_text)), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = mr.main(argv)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_copy_rich_macos_passes_hex_and_plain_as_argument(self):
        calls = []
        mr.copy_rich("<b>è</b>", 'say "hi"', platform="darwin",
                     run=lambda a, **k: calls.append((a, k)) or _ok(), which=lambda n: "/usr/bin/" + n)
        args = calls[0][0]
        self.assertEqual(args[0], "osascript")
        self.assertIn("<b>è</b>".encode("utf-8").hex(), " ".join(args))
        self.assertEqual(args[-1], 'say "hi"')
        self.assertNotIn('say "hi"', args[2])

    def test_copy_rich_macos_plain_starting_with_dash_follows_separator(self):
        calls = []
        mr.copy_rich("<b>x</b>", "- Ada", platform="darwin",
                     run=lambda a, **k: calls.append((a, k)) or _ok(), which=lambda n: "/usr/bin/" + n)
        args = calls[0][0]
        self.assertEqual(args[-2:], ["--", "- Ada"])

    def test_copy_text_macos_uses_pbcopy_stdin(self):
        calls = []
        mr.copy_text("héllo", platform="darwin",
                     run=lambda a, **k: calls.append((a, k)) or _ok(), which=lambda n: "/usr/bin/" + n)
        self.assertEqual(calls[0][0], ["pbcopy"])
        self.assertEqual(calls[0][1]["input"], "héllo".encode("utf-8"))

    def test_copy_linux_picks_first_tool_found(self):
        calls = []
        run = lambda a, **k: calls.append((a, k)) or _ok()  # noqa: E731
        mr.copy_rich("<b>x</b>", "x", platform="linux", run=run,
                     which=lambda n: "/usr/bin/xclip" if n == "xclip" else None)
        self.assertEqual(calls[0][0], ["xclip", "-selection", "clipboard", "-t", "text/html"])
        mr.copy_text("x", platform="linux", run=run, which=lambda n: "/usr/bin/" + n)
        self.assertEqual(calls[1][0], ["wl-copy"])

    def test_copy_unavailable(self):
        with self.assertRaises(mr.ClipboardUnavailable):
            mr.copy_rich("<b>x</b>", "x", platform="linux", run=None, which=lambda n: None)
        with self.assertRaises(mr.ClipboardUnavailable):
            mr.copy_text("x", platform="win32", run=None, which=lambda n: None)

    def test_copy_tool_failure_is_unavailable(self):
        class Bad:
            returncode = 1
        with self.assertRaises(mr.ClipboardUnavailable):
            mr.copy_text("x", platform="darwin", run=lambda a, **k: Bad(), which=lambda n: "/x")

    def test_main_exit_codes(self):
        self.assertEqual(_run(["--to", "plain"], "Hi **Ada**")[:2], (0, "Hi Ada\n"))
        self.assertEqual(_run(["--to", "html"], "see [x](javascript:1)")[0], 1)
        self.assertEqual(_run(["--to", "pdf"], "x")[0], 2)
        self.assertEqual(_run(["--to", "plain", "--in", "/nonexistent/file"], "")[0], 2)

    def test_main_copy_html_sends_plain_twin(self):
        with mock.patch.object(mr, "copy_rich") as rich:
            code, out, err = _run(["--to", "html", "--copy"], "Hi **Ada**")
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("clipboard", err)
        html, plain = rich.call_args[0]
        self.assertIn("<b>Ada</b>", html)
        self.assertEqual(plain, "Hi Ada\n")

    def test_main_copy_slack_uses_text(self):
        with mock.patch.object(mr, "copy_text") as text:
            code = _run(["--to", "slack", "--copy"], "Hi **Ada**")[0]
        self.assertEqual(code, 0)
        self.assertEqual(text.call_args[0][0], "Hi *Ada*\n")

    def test_main_copy_unavailable_still_writes_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "m.html")
            with mock.patch.object(mr, "copy_rich", side_effect=mr.ClipboardUnavailable("no tool")):
                code, _out, err = _run(["--to", "html", "--copy", "--out", target], "Hi **Ada**")
            self.assertEqual(code, 3)
            self.assertIn("clipboard", err)
            with open(target, encoding="utf-8") as handle:
                self.assertIn("<b>Ada</b>", handle.read())


if __name__ == "__main__":
    unittest.main()
