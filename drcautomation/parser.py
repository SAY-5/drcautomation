"""DRC report parser.

The DRC tool emits text reports with one violation per block. Real
formats (Calibre RVE, Pegasus, Hercules) all share a common shape:
rule name, location, layer, optional comment. We normalize into a
single `Violation` record.

The parser accepts either a complete report string (`parse_report`)
or an iterable of lines (`parse_lines`) so the streaming layer can
feed it line-by-line without buffering.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Violation:
    rule: str
    layer: str
    x: float
    y: float
    note: str = ""

    @property
    def location(self) -> tuple[float, float]:
        return (self.x, self.y)


# Calibre-style line: "VIO: <rule> at (<x>,<y>) layer <layer> [comment]"
_VIO_RE = re.compile(
    r"VIO:\s+(?P<rule>\S+)\s+at\s+\(\s*(?P<x>-?\d+(?:\.\d+)?),\s*(?P<y>-?\d+(?:\.\d+)?)\s*\)"
    r"\s+layer\s+(?P<layer>\S+)(?:\s+(?P<note>.*))?",
)


def parse_report(text: str) -> list[Violation]:
    return list(parse_lines(text.splitlines()))


def parse_lines(lines: Iterable[str]) -> Iterator[Violation]:
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _VIO_RE.match(line)
        if not m:
            continue
        yield Violation(
            rule=m.group("rule"),
            layer=m.group("layer"),
            x=float(m.group("x")),
            y=float(m.group("y")),
            note=(m.group("note") or "").strip(),
        )
