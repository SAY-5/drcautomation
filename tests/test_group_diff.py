"""v3: grouping + diff vs baseline."""

from __future__ import annotations

from drcautomation import Violation, diff_violations, group_similar


def _v(rule: str, layer: str, x: float, y: float) -> Violation:
    return Violation(rule=rule, layer=layer, x=x, y=y)


def test_group_collapses_repeats() -> None:
    vs = [_v("spacing", "M1", x, y) for x in (10, 20, 30) for y in (40, 50)]
    vs.append(_v("short", "M2", 100, 100))
    groups = group_similar(vs)
    assert len(groups) == 2
    # Largest group first.
    assert groups[0].rule == "spacing"
    assert groups[0].count == 6
    assert groups[0].bbox == (10, 40, 30, 50)
    assert groups[1].count == 1


def test_diff_classifies_new_fixed_and_unchanged() -> None:
    baseline = [_v("spacing", "M1", 10, 20), _v("short", "M2", 30, 40)]
    current = [_v("spacing", "M1", 10, 20), _v("antenna", "M3", 50, 60)]
    d = diff_violations(baseline, current)
    assert {v.rule for v in d.new_violations} == {"antenna"}
    assert {v.rule for v in d.fixed_violations} == {"short"}
    assert {v.rule for v in d.still_present} == {"spacing"}
    assert d.has_new


def test_diff_with_tolerance_matches_close_coordinates() -> None:
    baseline = [_v("spacing", "M1", 10.0, 20.0)]
    current = [_v("spacing", "M1", 10.04, 20.02)]
    # No tolerance → treated as new
    d_strict = diff_violations(baseline, current)
    assert d_strict.new_violations
    # Tolerance 0.1 → quantizes to (10.0, 20.0) on both sides
    d_loose = diff_violations(baseline, current, tolerance=0.1)
    assert not d_loose.new_violations
    assert d_loose.still_present
