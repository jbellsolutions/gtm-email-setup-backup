# Sending a Reply — When the CLI Fails

The `Instantly inbox reply --from-json` CLI occasionally fails with a JSON parse error (`Unexpected token 'E', "Email adde"... is not valid JSON`) while the API itself succeeds. The API returns plain-text `"Email added to the queue, will be sent out soon!"` which trips the CLI's `OkMessageSchema` validation.

## Curl Fallback (Always Works)

```bash
API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2-)

# JSON payload: email_stats_id + email_body only.
# Do NOT include campaign_id — it's in the URL path.
cat > /tmp/reply.json << 'JSONEOF'
{
  "email_stats_id": "55c1ee08-16ff-486a-8161-439a8f9f06c8",
  "email_body": "Hey Name — thanks.\n\nReply body here.\n\nMary"
}
JSONEOF

curl -s -X POST \
  "https://server.Instantly/api/v1/campaigns/<CAMPAIGN_ID>/reply-email-thread?api_key=$API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/reply.json
```

## Key Details

- **`api_key` goes in the query string**, NOT as a header. The Instantly API uses `?api_key=...` (not `api-key:` header, not `Authorization: Bearer`). This is non-standard and easy to miss.
- **`campaign_id` is in the URL path only** — including it in the JSON body returns `400: "campaign_id" is not allowed`.
- **`email_stats_id`** comes from `Instantly leads messages --campaign-id <ID> --lead-id <ID>` output — the `stats_id` field on the SENT message you're replying to.
- Reply body should be **plain text** (no HTML) per the reply playbook rules.
- Expected success response: text `"Email added to the queue, will be sent out soon!"` (not JSON).

## Endpoint

`POST https://server.Instantly/api/v1/campaigns/{campaign_id}/reply-email-thread?api_key={key}`

Body: `{"email_stats_id": "...", "email_body": "..."}`

## Finding the email_stats_id

```bash
# 1. Find the lead's email_lead_id from inbox
Instantly inbox unread --format json  # look for email_lead_id

# 2. Get message history to find stats_id
Instantly leads messages --campaign-id <ID> --lead-id <email_lead_id> --format json
# Look for the SENT message you want to reply to → stats_id field
```
