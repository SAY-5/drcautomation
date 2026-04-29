"""Smoke CLI: read a DRC report from stdin, optionally diff against a
baseline file, print a summary on stdout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from drcautomation import (
    Severity,
    classify,
    diff_violations,
    group_similar,
    parse_report,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="drcrun")
    p.add_argument("--baseline", type=Path, help="prior run report to diff against")
    p.add_argument("--tolerance", type=float, default=0.0, help="coordinate match tolerance")
    args = p.parse_args(argv)

    current_text = sys.stdin.read()
    current = parse_report(current_text)

    by_severity: dict[Severity, int] = {}
    for v in current:
        sev = classify(v)
        by_severity[sev] = by_severity.get(sev, 0) + 1

    print(f"violations: {len(current)}")
    for sev in [Severity.CRITICAL, Severity.MAJOR, Severity.MINOR, Severity.UNKNOWN]:
        print(f"  {sev.value}: {by_severity.get(sev, 0)}")

    groups = group_similar(current)
    print("\ntop groups (by count):")
    for g in groups[:10]:
        print(f"  {g.count:5d}  {g.rule}@{g.layer}")

    if args.baseline and args.baseline.exists():
        baseline = parse_report(args.baseline.read_text())
        d = diff_violations(baseline, current, tolerance=args.tolerance)
        print(f"\ndiff vs baseline: +{len(d.new_violations)} new, "
              f"-{len(d.fixed_violations)} fixed, "
              f"={len(d.still_present)} unchanged")
        return 1 if d.has_new else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
