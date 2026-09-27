# Q1 2026 Platform Performance Review

## Headline metrics
- Total events processed: 41.3 billion, up 28% on Q4 2025.
- Median API latency: 84 milliseconds. 99th percentile: 610 milliseconds.
- Measured uptime: 99.97% Enterprise, 99.71% Standard.

## Incident summary
Three Severity 1 incidents, totalling 47 minutes of Standard-tier degradation.
The largest, INC-2026-0114, was a pipeline scheduler deadlock lasting 31 minutes.
No Enterprise-tier customer breached SLA, so no credits were issued.

## Customer growth
- 312 active accounts at quarter end, up from 265.
- Enterprise accounts: 48, up from 39.
- Net revenue retention: 118%.

## Cost per request
Infrastructure cost per million events fell from $2.14 to $1.87, driven mainly by
the move to ARM-based compute for the transformation workers.
