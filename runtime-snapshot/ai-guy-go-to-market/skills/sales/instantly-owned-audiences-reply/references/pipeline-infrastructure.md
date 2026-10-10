# Owned Audiences Pipeline Infrastructure

## Automated Monitoring (cron-based)

The inbox is scanned every 30 minutes by a pipeline that handles detection, classification, and tracking. Plan-building (this skill's job) is the **manual follow-up step** — it is NOT auto-replied.

| Component | Path / ID |
|---|---|
| Pipeline script | `/opt/data/scripts/owned_audiences_pipeline.py` |
| Dashboard | `/opt/data/scripts/owned_audiences_dashboard.py` |
| State file | `/tmp/owned_audiences_followups.json` |
| Cron job | `9be604c0cbce` (every 30 min) |

## Campaigns monitored

- **3617053** — "Coaching Owned Audiences" (ACTIVE)
- **3607306** — "Coaching - In-House AI Guy — July 2026" (ACTIVE)

## What the pipeline does

1. Polls Instantly inbox for replies to both campaigns (pages 0-9, 200 entries max)
2. Classifies each reply: positive_interested, positive_soft, neutral, hostile, skip, dead
3. **Auto-replies to high-confidence positives** (positive_interested and positive_soft with conf="high") using a template reply with Calendly link. Low-confidence positives are left as `awaiting_followup` for manual plan-building.
4. Tracks leads in the state file with statuses: `new` → `awaiting_followup` / `replied` → `plan_built` / `booked` / `dead`
5. Valid statuses in stats dict: `awaiting_followup`, `replied`, `booked`, `dead`, `plan_built`

## Pipeline resilience issues

### `Instantly leads messages` timeout on specific leads
Some lead IDs cause the Instantly API to hang. The subprocess timeout is 30s per call. When a lead times out, the pipeline crashes at that page and skips all remaining leads on that page. Fixes applied:
- Manual retry with 90-120s timeout for flagged leads
- Workaround via direct CLI with no subprocess timeout: `Instantly leads messages --campaign-id <ID> --lead-id <ID> --format json > /tmp/msg_<name>.json`
- Lead ID 4136969058 (Gina, beyondthescoreboards.com) — consistently times out, flagged

### "Circling back" to hostile leads
The pipeline's follow-up logic sends "circling back" case studies to prior-week positives. It checks whether a SENT reply exists after the REPLY timestamp but does NOT check the lead's prior reply classification. Leads who said "remove me" / "stop" still receive circling-back emails, causing hostile escalation (Nicholle, Jul 14).

## How this skill fits in

When the cron delivers results showing `awaiting_followup` leads, use this skill (`owned-audiences-email-reply`) to build the plan for each positive lead. After building:

```python
# Update state to "plan_built"
state["leads"][lead_id]["status"] = "plan_built"
```

## Sending domains (for filtering operator replies)

All `*aiintegraterz.com` and `*integraterz*.com` subdomains, plus `elevateaxisca.info`.

## Separation from SpeakerAgent

SpeakerAgent (campaign 3577260) has its own completely separate pipeline at `/tmp/speakeragent_followups.json` with cron `148920b114d6`. Owned Audiences and SpeakerAgent are separate businesses — do not mix their state, scripts, or workflows.
