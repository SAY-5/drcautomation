"""v2: stream violations as the DRC tool emits them.

The DRC runner is a long-running Tcl process that writes to a log
file as it works. We tail the log line-by-line, parse, classify, and
yield SSE frames so a dashboard updates in real time.

Test surface: `stream_report` accepts an iterable of lines; production
wraps `tail -F` in a generator.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator

from drcautomation.classify import Severity, classify
from drcautomation.parser import parse_lines


def stream_report(lines: Iterable[str]) -> Iterator[str]:
    """Yield SSE frames as violations are parsed from `lines`.

    Frames:
        event: violation
        data: {"rule":...,"layer":...,"x":...,"y":...,"severity":"major","note":""}
    """

    for v in parse_lines(lines):
        sev: Severity = classify(v)
        body = {
            "rule": v.rule,
            "layer": v.layer,
            "x": v.x,
            "y": v.y,
            "severity": sev.value,
            "note": v.note,
        }
        yield f"event: violation\ndata: {json.dumps(body, separators=(',', ':'))}\n\n"
