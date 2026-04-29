# Architecture

## Pipeline

```
DRC tool ──text report──▶ parser ──▶ Violation[]
                              │
                              ├─▶ classify (severity)
                              ├─▶ stream (SSE per violation)
                              ├─▶ group_similar (collapse repeats)
                              └─▶ diff_violations (vs baseline)
```

## Why a normalized `Violation` record

Real DRC reports come from at least three vendors (Calibre RVE,
Cadence Pegasus, Synopsys Hercules) plus several in-house formats.
Each has its own quirks; trying to write tests against the raw text
locks you into one vendor's ordering and whitespace.

The parser reduces every format to one shape:

```python
Violation(rule, layer, x, y, note)
```

Downstream code (classify, stream, group, diff) doesn't care which
tool produced the report.

## Streaming (v2)

`stream_report(lines)` is a generator: it accepts an iterable of lines
(typically a `tail -F` on the running log file), emits an SSE frame
per parsed violation, and never buffers more than one record. The
HTTP handler wires it directly into a `text/event-stream` response.

## Grouping (v3)

`group_similar` collapses violations sharing `(rule, layer)` into one
`VioGroup` carrying the count, a representative violation, and the
bounding box of all member coordinates. Sorted by count desc — the
biggest groups are usually the symptom of one fix-once issue.

This typically reduces a 2,000-line raw report to ~30–80 actionable
groups.

## Diffing (v3)

`diff_violations(baseline, current, tolerance=0)` matches by exact
location by default. With a non-zero `tolerance` it quantizes to a
grid first, so cells that drifted by less than `tolerance` units
between runs match.

The diff returns three buckets: `new`, `fixed`, `still_present`. The
caller decides whether `new_violations` should fail CI; we just
expose the change-set.
