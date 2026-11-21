"""厘米尺读数：长度模型、答案解析与练习纸题目。"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

MM_PER_CM = 10
RULER_MAX_MM = 100
RULER_MIN_MM = 0
KINDS = ("read", "offset")

KIND_LABELS: Dict[str, str] = {
    "read": "从零刻度读数",
    "offset": "非零起点读数",
}


class RulerError(ValueError):
    """尺子读数相关的输入错误。"""


def _check_mm(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RulerError("%s必须是整数毫米" % name)
    if value < RULER_MIN_MM or value > RULER_MAX_MM:
        raise RulerError("%s需在 %d 到 %d 毫米之间" % (name, RULER_MIN_MM, RULER_MAX_MM))
    return value


def format_length(mm: int) -> str:
    """把整数毫米格式化为厘米，整厘米不带小数。"""
    if isinstance(mm, bool) or not isinstance(mm, int) or mm < 0:
        raise RulerError("长度必须是非负整数毫米")
    if mm % MM_PER_CM == 0:
        return "%d 厘米" % (mm // MM_PER_CM)
    return "%d.%d 厘米" % (mm // MM_PER_CM, mm % MM_PER_CM)


def format_millimeters(mm: int) -> str:
    if isinstance(mm, bool) or not isinstance(mm, int) or mm < 0:
        raise RulerError("长度必须是非负整数毫米")
    return "%d 毫米" % mm


def _to_mm(value: float, unit: str) -> int:
    if value < 0:
        raise RulerError("长度不能为负数")
    if unit == "cm":
        scaled = value * MM_PER_CM
        if abs(scaled - round(scaled)) > 1e-9:
            raise RulerError("厘米最多保留一位小数")
        return int(round(scaled))
    if unit == "mm":
        if abs(value - round(value)) > 1e-9:
            raise RulerError("毫米必须是整数")
        return int(round(value))
    raise RulerError("未知单位：%s" % unit)


_COMBINED_RE = re.compile(r"^(\d+(?:\.\d+)?)cm(\d+(?:\.\d+)?)mm$")
_SINGLE_RE = re.compile(r"^(\d+(?:\.\d+)?)(cm|mm)?$")


def parse_length(text: str) -> int:
    """解析学生答案，统一返回整数毫米。

    接受 ``4.5``、``4.5cm``、``4.5 厘米``、``45mm``、``4厘米5毫米`` 等写法。
    """
    if not isinstance(text, str) or not text.strip():
        raise RulerError("答案不能为空")
    cleaned = text.strip().lower()
    cleaned = cleaned.replace("公分", "cm").replace("厘米", "cm").replace("毫米", "mm")
    cleaned = re.sub(r"\s+", "", cleaned)
    combined = _COMBINED_RE.match(cleaned)
    if combined:
        return _to_mm(float(combined.group(1)), "cm") + _to_mm(
            float(combined.group(2)), "mm"
        )
    single = _SINGLE_RE.match(cleaned)
    if not single:
        raise RulerError("无法识别长度：%s" % text)
    unit = single.group(2) or "cm"
    return _to_mm(float(single.group(1)), unit)


@dataclass(frozen=True)
class Ruler:
    """尺子上的一段：左右两端刻度的毫米值。"""

    start_mm: int
    end_mm: int

    def __post_init__(self) -> None:
        _check_mm(self.start_mm, "起点")
        _check_mm(self.end_mm, "终点")
        if self.start_mm >= self.end_mm:
            raise RulerError("终点必须大于起点")

    @property
    def length_mm(self) -> int:
        return self.end_mm - self.start_mm

    @property
    def length_cm(self) -> float:
        return self.length_mm / MM_PER_CM

    @property
    def answer_text(self) -> str:
        return format_length(self.length_mm)

    @property
    def answer_long_text(self) -> str:
        return "%s（%s）" % (self.answer_text, format_millimeters(self.length_mm))


@dataclass(frozen=True)
class WorksheetItem:
    """一道读数题。"""

    kind: str
    start_mm: int
    end_mm: int

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise RulerError("未知题型：%s" % self.kind)
        Ruler(self.start_mm, self.end_mm)

    @property
    def ruler(self) -> Ruler:
        return Ruler(self.start_mm, self.end_mm)

    @property
    def answer_text(self) -> str:
        return self.ruler.answer_text

    @property
    def answer_long_text(self) -> str:
        return self.ruler.answer_long_text

    @property
    def prompt(self) -> str:
        if self.kind == "read":
            return "物体从 0 刻度开始，读出它的长度。"
        return "物体左端不在 0 刻度，读出它的长度。"


def check_answer(item: WorksheetItem, text: str) -> bool:
    """校验读数答案，单位可写厘米或毫米。"""
    if not isinstance(item, WorksheetItem):
        return False
    try:
        given = parse_length(text)
    except RulerError:
        return False
    return given == item.ruler.length_mm


def _candidates(kind: str) -> List[Tuple[str, int, int]]:
    rows: List[Tuple[str, int, int]] = []
    if kind == "read":
        for length in range(5, RULER_MAX_MM, 5):
            rows.append((kind, 0, length))
        return rows
    for start in range(10, 51, 10):
        for length in range(5, RULER_MAX_MM - start + 1, 5):
            rows.append((kind, start, start + length))
    return rows


def build_worksheet(
    count: int = 12,
    seed: Optional[int] = None,
    kinds: Sequence[str] = KINDS,
) -> List[WorksheetItem]:
    """随机抽取读数题，同一题不会重复。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise RulerError("题目数量必须是正整数")
    if not kinds:
        raise RulerError("至少需要一种题型")
    for kind in kinds:
        if kind not in KINDS:
            raise RulerError("未知题型：%s" % kind)
    pool: List[Tuple[str, int, int]] = []
    for kind in kinds:
        pool.extend(_candidates(kind))
    if count > len(pool):
        raise RulerError("可用题目不足 %d 道" % count)
    rng = random.Random(seed)
    chosen = rng.sample(pool, count)
    return [WorksheetItem(kind=kind, start_mm=start, end_mm=end) for kind, start, end in chosen]
