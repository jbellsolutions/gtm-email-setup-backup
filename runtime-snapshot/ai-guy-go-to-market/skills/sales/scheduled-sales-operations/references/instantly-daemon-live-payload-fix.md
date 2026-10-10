# Instantly daemon live-payload fix

## Symptom

A cron run reported unread items, then stopped with:

```text
Error: expected string or bytes-like object, got 'dict'
```

No `__SUMMARY__` marker was emitted, so the run was not a valid zero-activity result.

## Verified live payload

`GET /api/v2/emails?i_status=1` returned unread records containing both inbound and outbound messages. The response used `items`; inbound records exposed `ue_type: 2`, while an observed outbound/operator follow-up exposed `ue_type: 3`. Bodies were objects containing `text` and/or `html`; sender direction was available through `from_address_email` and connected `/accounts` addresses.

## Durable fix

Before classification:

1. Ensure the direct cron runner loads `INSTANTLY_API_KEY` from the approved local environment source if the gateway has not injected it.
2. Validate the response wrapper (`items`/`data`) and preserve an error-shaped response as a failure, never an empty inbox.
3. Filter to verified inbound records (`ue_type == 2` in the observed payload) and exclude connected sending-account addresses. Treat unknown direction combinations as review items rather than silently classifying them.
4. Read `body.text` first, falling back to `body.html`.
5. Decode HTML entities, strip HTML, and remove quoted original messages before classification.
6. Emit a final `__SUMMARY__` marker. A missing marker means the run failed and must not be reported as zero activity.
7. Run the exact `--once` entry point after changes, then run it again to verify processed-message deduplication and state preservation.

## Delivery rule

Posting the draft to Slack is a separate side effect. Verify the Slack tool response (`data.ok`, channel, and timestamp). If the connection returns `token_revoked`, report Slack delivery as blocked and do not claim the draft was posted or sent.
