# Atlas Platform — Technical Specification (v4.2, March 2026)

## Overview
Atlas is Synnovate's managed data-processing platform. It ingests customer event streams,
applies transformation pipelines, and exposes results through a REST API and a query console.

## Deployment tiers
- **Standard** — shared infrastructure, single region, up to 50 million events per month.
- **Enterprise** — dedicated infrastructure, multi-region failover, unlimited events.
- **Sovereign** — customer-hosted in their own cloud account, air-gapped option available.

## Service level agreement
- Enterprise tier: 99.95% monthly uptime, 15-minute response for Severity 1 incidents.
- Standard tier: 99.5% monthly uptime, 4-hour response for Severity 1 incidents.
- Sovereign tier: no uptime SLA, as the customer controls the infrastructure.
- Credits: 10% of monthly fee per 0.1% below target, capped at 50%.

## Rate limits
- Standard: 200 requests per second per API key, burst to 500 for 60 seconds.
- Enterprise: 2,000 requests per second per API key, burst to 5,000 for 300 seconds.

## Data retention
Processed events are retained for 90 days on Standard and 400 days on Enterprise.
Raw ingested payloads are discarded after 14 days on all tiers unless Extended Raw
Storage is purchased.
