"""Severity classifier. Maps a violation's `rule` to one of:

- CRITICAL: tape-out blocker (short, electrical opens, density floor)
- MAJOR: must-fix before signoff (spacing, width, antenna)
- MINOR: review-only (recommendation, density preference)

The mapping lives in a tag list per severity so a fab-specific rule
deck slots in by editing this dict.
"""

from __future__ import annotations

from enum import StrEnum

from drcautomation.parser import Violation


class Severity(StrEnum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    UNKNOWN = "unknown"


_RULES: dict[Severity, tuple[str, ...]] = {
    Severity.CRITICAL: ("short", "open", "missing_via", "density_floor"),
    Severity.MAJOR: ("spacing", "width", "enclosure", "antenna", "extension"),
    Severity.MINOR: ("recommendation", "density_pref", "label_check"),
}


def classify(v: Violation) -> Severity:
    rule = v.rule.lower()
    for sev, tags in _RULES.items():
        if any(tag in rule for tag in tags):
            return sev
    return Severity.UNKNOWN
