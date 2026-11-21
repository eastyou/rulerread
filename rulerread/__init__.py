"""厘米尺读数：可打印 SVG 尺子与练习纸。"""

from .model import (
    KIND_LABELS,
    KINDS,
    MM_PER_CM,
    RULER_MAX_MM,
    Ruler,
    RulerError,
    WorksheetItem,
    build_worksheet,
    check_answer,
    format_length,
    format_millimeters,
    parse_length,
)

__version__ = "0.1.0"

__all__ = [
    "KIND_LABELS",
    "KINDS",
    "MM_PER_CM",
    "RULER_MAX_MM",
    "Ruler",
    "RulerError",
    "WorksheetItem",
    "build_worksheet",
    "check_answer",
    "format_length",
    "format_millimeters",
    "parse_length",
]
