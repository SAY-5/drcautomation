"""v1: parser + classifier tests."""

from __future__ import annotations

from drcautomation import Severity, Violation, classify, parse_report

REPORT = """\
# header line, ignored
VIO: spacing_error at (100.5, 200.3) layer M1 width 0.025
VIO: short at (50.0, 75.0) layer M2
VIO: density_pref at (300, 400) layer V1 hint
VIO: random_unknown at (0, 0) layer X1
"""


def test_parser_extracts_all_violations() -> None:
    vs = parse_report(REPORT)
    assert len(vs) == 4
    assert vs[0].rule == "spacing_error"
    assert vs[0].layer == "M1"
    assert vs[0].x == 100.5
    assert vs[0].note == "width 0.025"


def test_parser_skips_header_and_blank_lines() -> None:
    text = "\n\n# comment\n\nVIO: x at (1,2) layer M1\n"
    vs = parse_report(text)
    assert len(vs) == 1


def test_classifier_maps_known_rules() -> None:
    vs = parse_report(REPORT)
    sevs = [classify(v) for v in vs]
    assert sevs == [Severity.MAJOR, Severity.CRITICAL, Severity.MINOR, Severity.UNKNOWN]


def test_violation_location_property() -> None:
    v = Violation(rule="r", layer="M1", x=1.5, y=2.5)
    assert v.location == (1.5, 2.5)
