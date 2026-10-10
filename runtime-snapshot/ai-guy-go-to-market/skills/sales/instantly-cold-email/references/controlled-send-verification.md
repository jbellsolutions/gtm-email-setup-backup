# Controlled Send Verification

## Why this exists

Instantly campaign activation is asynchronous. An HTTP 200 response from the activation endpoint means the campaign accepted the state change, not that a message was sent.

## Known reproduction

1. A paused test campaign contained one approved lead and a valid sender.
2. Activation returned HTTP 200.
3. The campaign was paused immediately afterward.
4. `GET /emails` remained empty and the lead counters stayed at zero.
5. Re-activating the campaign and allowing the scheduler to run produced a message record.

## Authoritative confirmation

Use the message-level record, not activation status or analytics alone:

```json
{
  "to_address_email_list": "justin@usingaitoscale.com",
  "from_address_email": "miller@growthmapar.info",
  "subject": "owned audience",
  "timestamp_email": "2026-08-03T14:58:44.000Z",
  "campaign_id": "...",
  "lead_id": "...",
  "thread_id": "20-...",
  "step": "0_0_0"
}
```

The sent body was available under `body.html` and contained the expected `<br><br>` paragraph separators.

## Operator rule

Never tell the operator that an email was sent until `/emails` contains the expected recipient and message record. During the wait, say queued or not yet confirmed. If the operator wants the campaign left active, isolate the approved lead, cap the daily limit, and remove all unintended test recipients before leaving it on.
