"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    Ruler,
    RulerError,
    build_worksheet,
    format_length,
    parse_length,
)
from .render import render_ruler_svg, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rulerread",
        description="厘米尺读数：长度换算、SVG 尺子与可打印练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    length_parser = subparsers.add_parser("length", help="计算两个刻度之间的长度")
    length_parser.add_argument("start", help="起点，例如 0 或 2.5")
    length_parser.add_argument("end", help="终点，例如 7.5")
    length_parser.add_argument("--svg", action="store_true", help="输出尺子 SVG")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=12, help="题目数量，默认 12")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：read（零刻度）、offset（非零起点）",
    )
    sheet_parser.add_argument("--title", default="厘米尺读数练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise RulerError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "length":
            start = parse_length(args.start)
            end = parse_length(args.end)
            ruler = Ruler(start, end)
            if args.svg:
                print(render_ruler_svg(start, end))
            else:
                print("起点：%s（%d 毫米）" % (format_length(start), start))
                print("终点：%s（%d 毫米）" % (format_length(end), end))
                print("长度：%s" % ruler.answer_long_text)
            return 0
        kinds = _parse_kinds(args.kinds)
        items = build_worksheet(args.count, args.seed, kinds)
        _write_output(render_worksheet(items, args.title, args.answers), args.output)
        return 0
    except RulerError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
