"""厘米尺页面渲染测试。"""

import unittest

from rulerread.model import WorksheetItem
from rulerread.render import render_ruler_svg, render_worksheet


class RulerSvgTest(unittest.TestCase):
    def test_root(self):
        svg = render_ruler_svg(0, 40)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn('viewBox="0 0 120 52"', svg)

    def test_role_and_label(self):
        svg = render_ruler_svg(0, 40)
        self.assertIn('role="img"', svg)
        self.assertIn("0 到 10 厘米", svg)

    def test_tick_count(self):
        self.assertEqual(render_ruler_svg(0, 10).count("<line"), 103)

    def test_object_width(self):
        svg = render_ruler_svg(25, 70)
        self.assertIn('width="45.00"', svg)

    def test_end_markers(self):
        svg = render_ruler_svg(20, 50)
        self.assertIn('x1="29.00"', svg)
        self.assertIn('x1="59.00"', svg)

    def test_cm_numbers(self):
        svg = render_ruler_svg(0, 10)
        for value in ("0", "1", "5", "10"):
            self.assertIn(">%s</text>" % value, svg)

    def test_unit_label(self):
        self.assertIn("厘米", render_ruler_svg(0, 10))

    def test_ends_at_ten(self):
        self.assertIn("10", render_ruler_svg(0, 100))


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = [
            WorksheetItem("read", 0, 35),
            WorksheetItem("offset", 20, 65),
        ]

    def test_doctype(self):
        self.assertTrue(render_worksheet(self.items).startswith("<!DOCTYPE html>"))

    def test_item_count(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="item"'), 2)

    def test_svg_per_item(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('<svg class="ruler"'), 2)

    def test_prompts(self):
        page = render_worksheet(self.items)
        self.assertIn("0 刻度", page)
        self.assertIn("不在 0 刻度", page)

    def test_no_answers_default(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("3.5 厘米", page)
        self.assertIn("45 毫米", page)

    def test_empty(self):
        with self.assertRaises(ValueError):
            render_worksheet([])

    def test_custom_title(self):
        self.assertIn("周末测量", render_worksheet(self.items, title="周末测量"))

    def test_title_escaped(self):
        page = render_worksheet(self.items, title="<尺子>")
        self.assertIn("&lt;尺子&gt;", page)

    def test_answer_blank(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="blank"'), 2)


if __name__ == "__main__":
    unittest.main()
