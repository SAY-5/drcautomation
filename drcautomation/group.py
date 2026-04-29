"""v3: group similar violations.

DRC reports often contain hundreds of instances of the same rule on
the same layer at slightly different coordinates — a single P&R
problem that produces many findings. Grouping by `(rule, layer)`
collapses them so reviewers see one entry instead of 300.

Each group carries a representative violation + a count + the
bounding box of all members' locations.
"""

from __future__ import annotations

from dataclasses import dataclass

from drcautomation.parser import Violation


@dataclass(frozen=True, slots=True)
class VioGroup:
    rule: str
    layer: str
    count: int
    representative: Violation
    bbox: tuple[float, float, float, float]  # x_min, y_min, x_max, y_max


def group_similar(violations: list[Violation]) -> list[VioGroup]:
    buckets: dict[tuple[str, str], list[Violation]] = {}
    for v in violations:
        buckets.setdefault((v.rule, v.layer), []).append(v)

    out: list[VioGroup] = []
    for (rule, layer), members in buckets.items():
        xs = [m.x for m in members]
        ys = [m.y for m in members]
        out.append(
            VioGroup(
                rule=rule,
                layer=layer,
                count=len(members),
                representative=members[0],
                bbox=(min(xs), min(ys), max(xs), max(ys)),
            )
        )
    # Largest groups first — that's where reviewers should focus.
    out.sort(key=lambda g: g.count, reverse=True)
    return out
