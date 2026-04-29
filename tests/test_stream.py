"""v2: streaming SSE."""

from __future__ import annotations

import json

from drcautomation import stream_report


def test_stream_yields_one_frame_per_violation() -> None:
    lines = [
        "VIO: spacing at (1, 2) layer M1",
        "VIO: short at (3, 4) layer M2",
    ]
    frames = list(stream_report(lines))
    assert len(frames) == 2
    assert frames[0].startswith("event: violation\n")
    body = json.loads(frames[0].split("data: ", 1)[1].strip())
    assert body["rule"] == "spacing"
    assert body["severity"] == "major"


def test_stream_classifies_critical() -> None:
    frames = list(stream_report(["VIO: short at (1, 2) layer M1"]))
    body = json.loads(frames[0].split("data: ", 1)[1].strip())
    assert body["severity"] == "critical"


def test_stream_emits_nothing_on_blank_input() -> None:
    assert list(stream_report([])) == []
    assert list(stream_report(["", "# comment", " "])) == []
