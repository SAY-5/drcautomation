"""v3: regression diff between two DRC runs.

Match violations by `(rule, layer, x, y)`. Returns:
- `new_violations`: present in `current` but not in `baseline` →
  introduced regressions
- `fixed_violations`: present in `baseline` but not in `current` →
  resolved
- `still_present`: in both runs

Coordinate matches are exact; if your design moves cells frequently
you'll want a coordinate tolerance — pass `tolerance` to round
locations to a grid before keying.
"""

from __future__ import annotations

from dataclasses import dataclass

from drcautomation.parser import Violation


def _key(v: Violation, tolerance: float) -> tuple[str, str, float, float]:
    if tolerance > 0:
        return (
            v.rule,
            v.layer,
            round(v.x / tolerance) * tolerance,
            round(v.y / tolerance) * tolerance,
        )
    return (v.rule, v.layer, v.x, v.y)


@dataclass(frozen=True, slots=True)
class RunDiff:
    new_violations: tuple[Violation, ...]
    fixed_violations: tuple[Violation, ...]
    still_present: tuple[Violation, ...]

    @property
    def has_new(self) -> bool:
        return bool(self.new_violations)


def diff_violations(
    baseline: list[Violation],
    current: list[Violation],
    tolerance: float = 0.0,
) -> RunDiff:
    base_idx = {_key(v, tolerance): v for v in baseline}
    cur_idx = {_key(v, tolerance): v for v in current}
    new = tuple(v for k, v in cur_idx.items() if k not in base_idx)
    fixed = tuple(v for k, v in base_idx.items() if k not in cur_idx)
    still = tuple(v for k, v in cur_idx.items() if k in base_idx)
    return RunDiff(new_violations=new, fixed_violations=fixed, still_present=still)
