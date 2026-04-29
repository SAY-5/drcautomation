"""drcautomation — DRC violation parser, classifier, streamer, differ."""

from drcautomation.classify import Severity, classify
from drcautomation.diff import RunDiff, diff_violations
from drcautomation.group import VioGroup, group_similar
from drcautomation.parser import Violation, parse_report
from drcautomation.stream import stream_report

__all__ = [
    "RunDiff",
    "Severity",
    "VioGroup",
    "Violation",
    "classify",
    "diff_violations",
    "group_similar",
    "parse_report",
    "stream_report",
]
