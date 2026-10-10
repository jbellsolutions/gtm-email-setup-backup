# email_lead_id Silent Empty History Pitfall

**Issue:** The `email_lead_id` field returned by `Instantly inbox replies` sometimes does not match the internal lead ID that `Instantly leads messages --lead-id <ID>` requires. The CLI returns `{"history":[]}` silently — no error, just zero messages — even for leads with active message threads.

This is distinct from the known "vestigial inbox entry" pitfall (leads actually deleted from campaign). These leads ARE still in the campaign with real message histories — the inbox's `email_lead_id` just doesn't map to the correct internal ID.

## Detection

When `leads messages` returns `{"history":[]}` for a lead:
1. The lead might be deleted from the campaign (vestigial inbox entry), OR
2. The `email_lead_id` from inbox is the wrong ID

## Resolution Workflow

```bash
# Step 1: Get global lead ID by email
Instantly leads get-by-email --email <email> --format json > /tmp/lookup.json

# Step 2: Extract internal lead ID
# The response has: { "id": <global_id>, "lead_campaign_data": [{ "campaign_lead_map_id": <map_id>, "campaign_id": <cid> }] }
# Use the top-level "id" field for leads messages

# Step 3: Pull message history with correct ID
Instantly leads messages --campaign-id <cid> --lead-id <global_id> --format json
```

## Confirmed Occurrences (July 21, 2026)

| Lead | Campaign | Inbox email_lead_id | get-by-email id | Messages found |
|---|---|---|---|---|
| daniel@gocamsolar.com | #3691319 (Solar) | 4208322608 → empty | 4205078246 | 2 msgs (OOO) |
| jeff.dillon@usmenshealth.com | #3617053 (Coaching OA) | 4214641002 → empty | 4163815206 | 3 msgs (positive, handled) |
| nicole@writekindagirl.com | #3577260 (PR v2) | 4208326602 → empty | 4102215240 | 7 msgs (handled) |

## Bottom Line

Never trust `email_lead_id` from inbox alone. Always have `get-by-email` as fallback. The extra API call is cheaper than silently missing a positive reply.