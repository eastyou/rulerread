"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from rulerread.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class LengthCommandTest(unittest.TestCase):
    def test_whole_numbers(self):
        code, out, _ = run_cli(["length", "0", "7"])
        self.assertEqual(code, 0)
        self.assertIn("7 厘米（70 毫米）", out)

    def test_decimals(self):
        code, out, _ = run_cli(["length", "2.5", "7"])
        self.assertEqual(code, 0)
        self.assertIn("4.5 厘米（45 毫米）", out)

    def test_units(self):
        code, out, _ = run_cli(["length", "20mm", "7cm"])
        self.assertEqual(code, 0)
        self.assertIn("5 厘米", out)

    def test_svg(self):
        code, out, _ = run_cli(["length", "0", "4", "--svg"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)
        self.assertIn("40.00", out)

    def test_reversed(self):
        code, _, err = run_cli(["length", "7", "2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_equal(self):
        code, _, err = run_cli(["length", "3", "3"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_unparseable(self):
        code, _, err = run_cli(["length", "abc", "4"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class SheetCommandTest(unittest.TestCase):
    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_item_count(self):
        code, out, _ = run_cli(["sheet", "--count", "6", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 6)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "4", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            self.assertTrue(os.path.exists(target))

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))

    def test_read_only(self):
        code, out, _ = run_cli(["sheet", "--count", "4", "--seed", "5", "--kinds", "read"])
        self.assertEqual(code, 0)
        self.assertNotIn("不在 0 刻度", out)

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--count", "1", "--title", "测量小测"])
        self.assertEqual(code, 0)
        self.assertIn("测量小测", out)

    def test_invalid_count(self):
        code, _, err = run_cli(["sheet", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_kind(self):
        code, _, err = run_cli(["sheet", "--kinds", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_seed_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        _, second, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        self.assertEqual(first, second)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
