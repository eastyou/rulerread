"""厘米尺与练习纸的 SVG / HTML 渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import MM_PER_CM, RULER_MAX_MM, WorksheetItem

STYLE = """
@page { size: A4 portrait; margin: 13mm 10mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1f2937;
  font-size: 11pt;
  line-height: 1.6;
}
h1 { font-size: 21pt; margin: 0 0 1.5mm; }
.sub { color: #6b7280; font-size: 9.5pt; margin: 0 0 5mm; }
ol.items { margin: 0; padding-left: 7mm; }
li.item { margin-bottom: 7mm; page-break-inside: avoid; }
.prompt { margin: 0 0 1.5mm; }
.prompt .num { color: #b45309; font-weight: 600; margin-right: 1.5mm; }
.ruler { width: 160mm; height: auto; }
.answer-line { margin-top: 1mm; color: #475569; font-size: 10pt; }
.blank { display: inline-block; min-width: 30mm; border-bottom: 0.7pt solid #94a3b8; height: 1.1em; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { margin: 0; padding-left: 7mm; }
.answers li { margin-bottom: 3mm; }
.answers .ans { color: #0f4c81; }
.answers .mm { color: #6b7280; font-size: 9.5pt; }
"""

RULER_X0 = 9.0
RULER_Y = 30.0
RULER_HEIGHT = 16.0
VIEW_WIDTH = 120.0
VIEW_HEIGHT = 52.0


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_ruler_svg(start_mm: int, end_mm: int) -> str:
    """画出 0–10 厘米的尺子，并用色块标出物体。"""
    parts: List[str] = [
        '<svg class="ruler" viewBox="0 0 %.0f %.0f" role="img" '
        'aria-label="0 到 10 厘米刻度的尺子">' % (VIEW_WIDTH, VIEW_HEIGHT),
    ]
    parts.append(
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1" '
        'fill="#fffdf5" stroke="#94a3b8" stroke-width="0.5"></rect>'
        % (RULER_X0, RULER_Y, float(RULER_MAX_MM), RULER_HEIGHT)
    )
    for mm in range(RULER_MAX_MM + 1):
        x = RULER_X0 + mm
        if mm % MM_PER_CM == 0:
            length = 8.0
            parts.append(
                '<line x1="%.2f" y1="%.1f" x2="%.2f" y2="%.1f" '
                'stroke="#334155" stroke-width="0.4"></line>'
                % (x, RULER_Y, x, RULER_Y + length)
            )
            parts.append(
                '<text x="%.2f" y="%.1f" font-size="2.6" text-anchor="middle" '
                'fill="#334155">%d</text>'
                % (x, RULER_Y + 13.5, mm // MM_PER_CM)
            )
        elif mm % 5 == 0:
            parts.append(
                '<line x1="%.2f" y1="%.1f" x2="%.2f" y2="%.1f" '
                'stroke="#64748b" stroke-width="0.3"></line>'
                % (x, RULER_Y, x, RULER_Y + 5.5)
            )
        else:
            parts.append(
                '<line x1="%.2f" y1="%.1f" x2="%.2f" y2="%.1f" '
                'stroke="#94a3b8" stroke-width="0.25"></line>'
                % (x, RULER_Y, x, RULER_Y + 3.5)
            )
    left = RULER_X0 + start_mm
    right = RULER_X0 + end_mm
    parts.append(
        '<rect x="%.2f" y="17" width="%.2f" height="8" rx="1" '
        'fill="#fbbf24" fill-opacity="0.85" stroke="#b45309" stroke-width="0.4"></rect>'
        % (left, float(end_mm - start_mm))
    )
    for x in (left, right):
        parts.append(
            '<line x1="%.2f" y1="12" x2="%.2f" y2="%.1f" '
            'stroke="#b45309" stroke-width="0.5"></line>' % (x, x, RULER_Y)
        )
    parts.append(
        '<text x="%.1f" y="%.1f" font-size="2.4" fill="#64748b">厘米</text>'
        % (RULER_X0 + RULER_MAX_MM + 1.0, RULER_Y + 5)
    )
    parts.append("</svg>")
    return "".join(parts)


def render_worksheet(
    items: Sequence[WorksheetItem],
    title: str = "厘米尺读数练习",
    include_answers: bool = False,
) -> str:
    """生成 A4 读数练习纸。"""
    if not items:
        raise ValueError("至少需要一道题目")
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        rows.append(
            '<li class="item"><p class="prompt"><span class="num">%d.</span>%s</p>'
            "%s"
            '<p class="answer-line">长度：<span class="blank"></span>厘米　'
            "（也可以写成毫米）</p></li>"
            % (
                index,
                _escape(item.prompt),
                render_ruler_svg(item.start_mm, item.end_mm),
            )
        )
    body = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % _escape(title),
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % _escape(title),
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<ol class="items">',
        "\n".join(rows),
        "</ol>",
    ]
    if include_answers:
        body.extend(_answer_section(items))
    body.extend(["</body>", "</html>"])
    return "\n".join(body)


def _answer_section(items: Sequence[WorksheetItem]) -> List[str]:
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        rows.append(
            '<li><span class="num">%d.</span> <span class="ans">%s</span> '
            '<span class="mm">%s</span></li>'
            % (index, _escape(item.answer_text), _escape(item.answer_long_text))
        )
    return [
        '<section class="answers">',
        "<h2>参考答案</h2>",
        "<ol>",
        "\n".join(rows),
        "</ol>",
        "</section>",
    ]
