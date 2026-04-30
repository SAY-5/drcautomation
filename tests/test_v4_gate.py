from __future__ import annotations

from drcautomation import Violation
from drcautomation.gate import ReleaseGate, notify_payload


def _v(rule: str) -> Violation:
    return Violation(rule=rule, layer="M1", x=0, y=0)


def test_clean_run_passes() -> None:
    g = ReleaseGate()
    v = g.evaluate([])
    assert v.pass_
    assert "release-go" in v.rationale


def test_critical_blocks_unconditionally() -> None:
    g = ReleaseGate(major_budget=100)
    v = g.evaluate([_v("short")])  # critical
    assert not v.pass_


def test_major_within_budget_passes() -> None:
    g = ReleaseGate(major_budget=5)
    vs = [_v("spacing")] * 3  # 3 majors, within budget 5
    v = g.evaluate(vs)
    assert v.pass_


def test_major_over_budget_blocks() -> None:
    g = ReleaseGate(major_budget=2)
    vs = [_v("spacing")] * 5
    v = g.evaluate(vs)
    assert not v.pass_
    assert "exceed budget" in v.rationale


def test_minor_does_not_block() -> None:
    g = ReleaseGate(major_budget=0)
    vs = [_v("recommendation")] * 50  # all minor
    v = g.evaluate(vs)
    assert v.pass_


def test_notify_payload_is_well_formed_for_pass() -> None:
    g = ReleaseGate()
    v = g.evaluate([])
    payload = notify_payload(v, "run-42")
    assert payload["attachments"][0]["color"] == "good"
    assert any(f["title"] == "Critical" for f in payload["attachments"][0]["fields"])


def test_notify_payload_is_red_on_block() -> None:
    g = ReleaseGate()
    v = g.evaluate([_v("short")])
    payload = notify_payload(v, "run-42")
    assert payload["attachments"][0]["color"] == "danger"
