"""v4: severity-weighted release gate + Slack-shaped notification.

The default v3 diff returns new/fixed/still-present buckets but
doesn't decide whether the run blocks the release. v4 adds a
configurable gate:

- Critical violations always block.
- Major violations block if count > major_budget.
- Minor violations are informational.
- A separate `notify_payload()` builds a Slack-block-shaped JSON
  payload so the orchestrator can push to a webhook directly.

The gate is policy code; teams will tweak the budgets per project.
We expose them as constructor args so the gate config lives next
to the Jenkins / GitHub Actions wiring.
"""

from __future__ import annotations

from dataclasses import dataclass

from drcautomation.classify import Severity, classify
from drcautomation.parser import Violation


@dataclass(frozen=True, slots=True)
class GateVerdict:
    pass_: bool
    critical: int
    major: int
    minor: int
    rationale: str


@dataclass
class ReleaseGate:
    major_budget: int = 5  # allow up to N major violations through

    def evaluate(self, violations: list[Violation]) -> GateVerdict:
        c = m = mi = 0
        for v in violations:
            sev = classify(v)
            if sev == Severity.CRITICAL:
                c += 1
            elif sev == Severity.MAJOR:
                m += 1
            elif sev == Severity.MINOR:
                mi += 1
        if c > 0:
            return GateVerdict(
                pass_=False, critical=c, major=m, minor=mi,
                rationale=f"{c} critical violation(s) — release-no-go",
            )
        if m > self.major_budget:
            return GateVerdict(
                pass_=False, critical=c, major=m, minor=mi,
                rationale=f"{m} major violations exceed budget {self.major_budget}",
            )
        return GateVerdict(
            pass_=True, critical=c, major=m, minor=mi,
            rationale=f"{c}c/{m}m/{mi}m within budget — release-go",
        )


def notify_payload(verdict: GateVerdict, run_id: str) -> dict:
    """Build a Slack-blocks-style payload. The webhook posts this
    JSON; we keep the shape stable so a downstream UI can lay it
    out without parsing free text."""
    color = "danger" if not verdict.pass_ else "good"
    return {
        "attachments": [
            {
                "color": color,
                "title": f"DRC run {run_id}",
                "fields": [
                    {"title": "Critical", "value": str(verdict.critical), "short": True},
                    {"title": "Major", "value": str(verdict.major), "short": True},
                    {"title": "Minor", "value": str(verdict.minor), "short": True},
                    {"title": "Verdict", "value": verdict.rationale, "short": False},
                ],
            }
        ]
    }
