"""Tests of the message Markdown subset parser."""
from __future__ import annotations

import unittest

from _support import SCRIPTS  # noqa: F401  (puts shared/scripts on sys.path)

import message_markdown as mm


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


if __name__ == "__main__":
    unittest.main()
