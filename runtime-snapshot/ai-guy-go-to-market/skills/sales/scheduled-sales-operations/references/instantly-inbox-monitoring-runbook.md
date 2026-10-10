# Instantly Inbox Monitoring Runbook

## Purpose

Use this runbook for the Instantly-style cold-email reply monitor migrated to Instantly. It is not a pre-call, calendar, analytics, or general sales-ops reporting workflow.

## Required behavior

1. Run every 30 minutes during the configured business window.
2. Deliver to the requested main Slack channel, not the originating thread.
3. Scan all paginated `/emails` records. Do not use `is_unread` or `i_status=1` as the sole cursor: UI-read messages can otherwise be missed.
4. Filter prospect direction using `from_address_email` plus connected sending-account exclusion. Observed inbound records include `ue_type=2` and some inbound follow-ups with `ue_type=3`; never classify an outbound record from a connected account.
5. Read `body.text`, then `body.html`; decode entities, strip tags, and remove quoted original content before classification.
6. Use local message-ID state for deduplication. Do not mutate state after an incomplete page fetch or API error.
7. Post every newly discovered reply, regardless of classification. Add approval-gated drafts for positive/referral replies. Never auto-send in unattended monitoring.
8. Emit `__SUMMARY__` only after a complete run. A missing marker or an error-shaped response is a failed/incomplete run, not zero activity.

## Rate-limit handling

Instantly enforces a rolling limit of 20 requests/minute. On HTTP 429:

- preserve the successful snapshot and local state;
- back off using `Retry-After` when present, otherwise wait conservatively;
- retry the current page rather than advancing the cursor;
- throttle pagination requests;
- report the scan incomplete if the retry still fails.

Never report `[SILENT]`, zero replies, or a complete scan after a 429.

## Verification checklist

- `python3 -m py_compile /opt/data/scripts/instantly_reply_daemon.py`
- Run the exact `python3 /opt/data/scripts/instantly_reply_daemon.py --once` entry point.
- Require a final `__SUMMARY__` marker.
- On a successful run, verify newly emitted reply records and draft records.
- Run a second scan to confirm local message-ID deduplication.
- After cron changes, inspect the job and confirm `deliver=slack:<main-channel-id>` with no thread ID.

## Incident lesson

A monitor that filters only unread entries can appear healthy while missing replies that the operator has already opened. The durable boundary is paginated inbox retrieval plus local processed-ID state, not the provider's mutable unread flag.
