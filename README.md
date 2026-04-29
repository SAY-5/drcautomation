# drcautomation

Design Rule Check automation pipeline. Parses violation reports from
the DRC tool (Calibre / Pegasus / Hercules), classifies severity,
streams findings live as the Tcl runner emits them, and diffs runs
against a baseline so a human reviews **only what changed**.

```
layout ──Tcl──▶ DRC tool ──text report──▶ parser ──▶ Violation[]
                                                        │
                                                        ├─▶ classify (critical/major/minor)
                                                        ├─▶ stream (SSE)
                                                        └─▶ diff(baseline, this run)
```

## Versions

| Version | Capability | Status |
|---|---|---|
| v1 | Violation parser + classifier + aggregate counts | shipped |
| v2 | SSE streaming as the runner emits violations | shipped |
| v3 | Group/dedup similar violations + diff vs prior run | shipped |

## Quickstart

```bash
pip install -e ".[dev]"
pytest
echo '"violation: spacing_error at (100,200) layer M1"' | drcrun --baseline /dev/null
```
