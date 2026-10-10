# Staged large-send procedure

Use for an approved campaign sent through a warming SMTP provider or a list large enough that a provider cap, rate limit, or reputation event is material.

## Preflight

1. Confirm the campaign is the explicitly approved campaign and the other campaigns remain untouched.
2. Confirm the imported list count, confirmed count, unsubscribed count, campaign list assignment, From, Reply-To header, template, body hash, and `sent` baseline.
3. Confirm the intended provider is the only enabled global SMTP messenger. ListMonk SMTP selection is global, not campaign-specific.
4. Read `/api/logs` before starting. Existing SMTP errors are a hard stop.
5. Set conservative ListMonk settings, for example `concurrency: 1`, `message_rate: 1`, and a bounded `batch_size`. Record the values before changing them.
6. Check the provider's current accepted, delivered, bounced, rejected, complaint, quota, and daily-cap metrics. Do not infer deliverability from ListMonk's `sent` counter alone.

## Start and monitor

Use the dedicated status endpoint:

```text
PUT /api/campaigns/{id}/status
{"status":"running"}
```

Do not use `PUT /api/campaigns/{id}` with `{"status":"running"}`. That endpoint updates campaign metadata and may return `Invalid list IDs.` when passed a status-only payload.

Poll the campaign every 10-15 seconds. Compare successive values for `status`, `sent`, `to_send`, `bounces`, `views`, and `clicks`. During startup, ListMonk counters may lag or change in jumps, so do not claim an exact wave size until the campaign is paused and re-read.

Pause with:

```text
PUT /api/campaigns/{id}/status
{"status":"paused"}
```

Define the pause threshold before starting. For a requested first wave of roughly 1,000, pause when the persisted `sent` count reaches or slightly exceeds that threshold. If any bounce, complaint, rejection, rate-limit message, SMTP error, or provider warning appears, pause immediately regardless of count.

## Provider reconciliation

ListMonk's `sent` count is application-level attempted/sent state. Reconcile against the provider:

- Bird: `GET https://us1.platform.bird.com/v1/email/messages?limit=N`, filtering by exact campaign subject and send window. Report `accepted`, `delivered`, `bounced`, `rejected`, and `complained` from Bird records. Accepted is not delivered.
- Resend: use the Resend email list and per-message status/event endpoints. Report `last_event` and `reply_to` where available.

Do not report completion from a `{"data":true}` response, a background worker state, or a running campaign alone. After requesting the status change, GET the campaign and verify it is running and that `sent` advances. After the threshold, verify a post-pause GET and capture the actual persisted count, which may overshoot the target because of batching. Provider-level delivery records and post-pause ListMonk state are required. If the worker is silent, times out, or exits without a verified campaign transition, leave the campaign paused and report the launch as unverified.

## Guardrails

- Never start the full list in one burst when the request specifies staging.
- Never touch a different campaign while the staged campaign is running.
- Never resume the next wave automatically. Pause and report for explicit release.
- If the provider has a daily cap below the remaining list, stop at the cap and report the queue.
- Keep seed recipients in the list and reconcile them individually, but do not claim inbox-versus-spam placement unless the recipient confirms it from their mailbox.
- If counters behave unexpectedly, stop before guessing. Capture the campaign state, provider records, and logs, then report the discrepancy.
