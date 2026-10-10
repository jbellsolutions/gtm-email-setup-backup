# Follow-Up Cadence Engine

Location: `/opt/data/scripts/followup_engine.py`
Cron: `ac18c07f72f9` (every 30 min)
Dashboard: `python3 /opt/data/scripts/followup_engine.py --dash`

## Overview

Automated follow-up engine for both SpeakerAgent (campaign 3577260) and Owned Audiences (campaigns 3617053, 3607306). Handles the entire follow-up lifecycle: calendar check → business day count → message rotation → send → state update.

## How It Works

For each lead in `awaiting_followup` or `replied` status:

1. **Check calendar** — queries Cal.com API to see if the lead already booked. If yes, marks as `booked` and stops.
2. **Count business days** — computes Mon-Fri days since last contact (`followup_sent_at` or `detected_at`). Weekends (Sat/Sun) do not count.
3. **Threshold check** — if < 3 business days, skip. Only sends when >= 3.
4. **Pick next message** — selects from 4-message rotation using `followup_count % len(messages)`. Each follow-up is a different message.
5. **Send** — uses `Instantly leads reply` via CLI with the lead's `stats_id`.
6. **Update state** — bumps `followup_count`, sets `followup_sent_at`, changes status to `replied`.

## Message Rotations

### SpeakerAgent (4 messages, from "Mila")
1. Circling back — happy to answer questions
2. New agencies in pipeline — want to be included?
3. Putting together next batch of referrals — no pressure
4. Last check-in — totally understand if timing's off

### Owned Audiences (4 messages, from "Justin")
1. Following up on the AI plan — walk through questions
2. Checking plan landed in inbox — thoughts?
3. Quick follow-up — call to discuss next steps
4. Last ping — understand if not right timing

## Business Day Calculation

```python
def business_days_since(then_iso):
    # Convert ISO timestamp to date
    then = datetime.fromisoformat(then_iso).date()
    today = date.today()
    # Count weekdays (Mon=0, Sun=6) between then+1 and today
    d, count = then + timedelta(days=1), 0
    while d <= today:
        if d.weekday() < 5:
            count += 1
        d += timedelta(days=1)
    return count
```

## Calendar Integration (Cal.com)

Requires `CALCOM_API_KEY` in `/opt/data/.env`.

API endpoint: `GET https://api.cal.com/v2/bookings?status=accepted&attendeeEmail={email}`

Headers:
- `Authorization: Bearer {CALCOM_API_KEY}`
- `Cal-Api-Version: 2024-08-13`

Response: `{"data": {"bookings": [...]}}` — non-empty array means the lead booked.

Without the API key, calendar checks are silently skipped (no blocking).

## State Updates

The engine writes back to the same state files used by the pipeline:
- `/tmp/speakeragent_followups.json`
- `/tmp/owned_audiences_followups.json`

Each lead gets:
- `followup_count`: incremented on each send
- `followup_sent_at`: ISO timestamp
- `status`: "replied" after follow-up, "booked" if calendar detects booking
- `status_history[]`: audit trail with notes

## Pitfalls

- **No `stats_id` → can't send**: If a lead was detected without a `stats_id`, the engine skips it. Manual Instantly intervention needed.
- **Campaign ID mismatch**: Owned Audiences leads must have `email_campaign_id` matching the configured `campaign_ids`. Leads from other campaigns in the same state file are ignored.
- **Calendar key missing**: Follow-ups proceed without calendar verification. Leads who already booked won't be detected.
- **Duplicate detection**: The engine only looks at leads with `awaiting_followup` or `replied` status. Leads in `booked` or `dead` are skipped entirely — no stale re-follow-ups.
