"""厘米尺读数模型测试。"""

import unittest
from dataclasses import FrozenInstanceError

from rulerread.model import (
    KINDS,
    Ruler,
    RulerError,
    WorksheetItem,
    build_worksheet,
    check_answer,
    format_length,
    format_millimeters,
    parse_length,
)


class FormatTest(unittest.TestCase):
    def test_whole_centimeters(self):
        self.assertEqual(format_length(0), "0 厘米")
        self.assertEqual(format_length(10), "1 厘米")
        self.assertEqual(format_length(100), "10 厘米")

    def test_half_centimeters(self):
        self.assertEqual(format_length(5), "0.5 厘米")
        self.assertEqual(format_length(45), "4.5 厘米")

    def test_invalid(self):
        for bad in (-1, True, "5", None):
            with self.assertRaises(RulerError):
                format_length(bad)

    def test_millimeters(self):
        self.assertEqual(format_millimeters(45), "45 毫米")
        with self.assertRaises(RulerError):
            format_millimeters(-2)


class ParseLengthTest(unittest.TestCase):
    def test_plain_number_is_cm(self):
        self.assertEqual(parse_length("4.5"), 45)
        self.assertEqual(parse_length("0"), 0)
        self.assertEqual(parse_length("10"), 100)

    def test_cm_units(self):
        self.assertEqual(parse_length("4.5cm"), 45)
        self.assertEqual(parse_length("4.5 厘米"), 45)
        self.assertEqual(parse_length("4公分"), 40)
        self.assertEqual(parse_length("4CM"), 40)

    def test_mm_units(self):
        self.assertEqual(parse_length("45mm"), 45)
        self.assertEqual(parse_length("45 毫米"), 45)

    def test_combined_units(self):
        self.assertEqual(parse_length("4厘米5毫米"), 45)
        self.assertEqual(parse_length("4cm5mm"), 45)

    def test_too_many_decimals(self):
        with self.assertRaises(RulerError):
            parse_length("4.55")

    def test_partial_millimeter(self):
        with self.assertRaises(RulerError):
            parse_length("4.5mm")

    def test_negative(self):
        with self.assertRaises(RulerError):
            parse_length("-1")

    def test_empty(self):
        for bad in ("", "   ", None):
            with self.assertRaises(RulerError):
                parse_length(bad)

    def test_unrecognized(self):
        for bad in ("abc", "1米", "四厘米"):
            with self.assertRaises(RulerError):
                parse_length(bad)


class RulerTest(unittest.TestCase):
    def test_length(self):
        ruler = Ruler(25, 70)
        self.assertEqual(ruler.length_mm, 45)
        self.assertAlmostEqual(ruler.length_cm, 4.5)

    def test_answer_text(self):
        ruler = Ruler(0, 40)
        self.assertEqual(ruler.answer_text, "4 厘米")
        self.assertEqual(ruler.answer_long_text, "4 厘米（40 毫米）")

    def test_full_ruler(self):
        self.assertEqual(Ruler(0, 100).length_mm, 100)

    def test_equal_endpoints(self):
        with self.assertRaises(RulerError):
            Ruler(30, 30)

    def test_reversed(self):
        with self.assertRaises(RulerError):
            Ruler(70, 20)

    def test_out_of_range(self):
        with self.assertRaises(RulerError):
            Ruler(-1, 20)
        with self.assertRaises(RulerError):
            Ruler(0, 101)

    def test_non_integer(self):
        with self.assertRaises(RulerError):
            Ruler(0.5, 10)
        with self.assertRaises(RulerError):
            Ruler(True, 10)

    def test_frozen(self):
        ruler = Ruler(0, 10)
        with self.assertRaises(FrozenInstanceError):
            ruler.start_mm = 2


class WorksheetItemTest(unittest.TestCase):
    def test_read_prompt(self):
        item = WorksheetItem("read", 0, 40)
        self.assertIn("0 刻度", item.prompt)

    def test_offset_prompt(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertIn("不在 0 刻度", item.prompt)

    def test_answer(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertEqual(item.answer_text, "4.5 厘米")

    def test_ruler_property(self):
        item = WorksheetItem("read", 0, 55)
        self.assertIsInstance(item.ruler, Ruler)
        self.assertEqual(item.ruler.start_mm, 0)

    def test_invalid_kind(self):
        with self.assertRaises(RulerError):
            WorksheetItem("guess", 0, 30)

    def test_invalid_range(self):
        with self.assertRaises(RulerError):
            WorksheetItem("read", 30, 30)


class CheckAnswerTest(unittest.TestCase):
    def test_cm(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertTrue(check_answer(item, "4.5"))

    def test_cm_unit(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertTrue(check_answer(item, "4.5 厘米"))

    def test_mm(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertTrue(check_answer(item, "45mm"))

    def test_combined(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertTrue(check_answer(item, "4厘米5毫米"))

    def test_wrong_value(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertFalse(check_answer(item, "5"))

    def test_unparseable(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertFalse(check_answer(item, "很长"))

    def test_empty(self):
        item = WorksheetItem("offset", 20, 65)
        self.assertFalse(check_answer(item, ""))

    def test_non_item(self):
        self.assertFalse(check_answer(None, "4.5"))


class BuildWorksheetTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_worksheet(10, seed=1)), 10)

    def test_all_kinds_valid(self):
        for item in build_worksheet(12, seed=2):
            self.assertIn(item.kind, KINDS)

    def test_unique_items(self):
        items = build_worksheet(12, seed=3)
        keys = {(item.start_mm, item.end_mm) for item in items}
        self.assertEqual(len(keys), 12)

    def test_read_starts_at_zero(self):
        items = build_worksheet(6, seed=4, kinds=("read",))
        for item in items:
            self.assertEqual(item.start_mm, 0)
            self.assertGreater(item.end_mm, 0)

    def test_offset_nonzero(self):
        items = build_worksheet(6, seed=5, kinds=("offset",))
        for item in items:
            self.assertGreater(item.start_mm, 0)
            self.assertLessEqual(item.end_mm, 100)

    def test_deterministic(self):
        first = build_worksheet(8, seed=6)
        second = build_worksheet(8, seed=6)
        self.assertEqual(
            [(item.kind, item.start_mm, item.end_mm) for item in first],
            [(item.kind, item.start_mm, item.end_mm) for item in second],
        )

    def test_invalid_count(self):
        for bad in (0, -3, True, "6"):
            with self.assertRaises(RulerError):
                build_worksheet(bad)

    def test_invalid_kind(self):
        with self.assertRaises(RulerError):
            build_worksheet(3, kinds=("guess",))

    def test_empty_kinds(self):
        with self.assertRaises(RulerError):
            build_worksheet(3, kinds=())

    def test_too_many(self):
        with self.assertRaises(RulerError):
            build_worksheet(100, kinds=("read",))


if __name__ == "__main__":
    unittest.main()
