# Instantly weekly reply reconciliation

Use this for a retrospective sweep when replies appear to be missing.

## Verified workflow

1. Paginate `/accounts` with `limit=100` and `starting_after`; do not assume the first page represents all sending mailboxes. A live sweep found 269 accounts despite an earlier first-page check showing only 10.
2. Paginate `/emails?limit=100` with `starting_after` until the oldest record is older than the requested window, or the API returns an empty page. Respect the 20-requests/minute limit with roughly 3.2 seconds between pages.
3. Deduplicate by email-record `id`, parse `timestamp_email` as UTC, and filter the requested date window locally.
4. Treat `ue_type == 2` as inbound lead replies. Treat `ue_type == 1` as sent. `ue_type == 3` has been observed for outbound/operator replies and must not be classified as an inbound lead reply; use sender direction/account membership as a secondary check.
5. Archive the complete inbound set and triage summary in an Obsidian domain note, append the operational result to the daily log, and create/update one findable Notion archive record. Do not create a separate CRM lead row for every auto-reply or rejection.
6. Classify conservatively: suppress OOO, routing notices, ticket acknowledgements, retirements, rejections, unsubscribes, and already-handled threads. Hold unusual but potentially valuable questions/referrals for custom operator review rather than sending a generic template.
7. Before sending, inspect the thread for a later outbound message after the inbound timestamp. A positive reply already followed by a human outbound message is handled and must not receive a duplicate.
8. For a real positive reply, Instantly's reply endpoint requires `reply_to_uuid`, `eaccount`, `subject`, and a `body` containing `text` and `html`. Verify HTTP 200 and then re-query the thread for the resulting outbound record. Do not infer delivery from a local draft or daemon state.

## Known API quirks

- `/emails?thread_id=<id>` is not reliable as a strict server-side filter in the observed account: it returned unrelated records in addition to the requested thread. Always filter returned rows client-side by `thread_id`.
- A successful `POST /emails/reply` response includes a new outbound record with `id`, `eaccount`, `from_address_email`, `to_address_email_list`, `thread_id`, and `ue_type: 3`. Save that record ID in the archive.
- The reply body renders as HTML. Preserve paragraph breaks in the payload and use HTML links when the active reply standard requires them.

## Safety gate

Sending is approval-gated. Never batch-send all inbound records. Only send to clearly eligible positive replies after per-thread history review and QC. Keep custom questions, referrals, mismatched offers, and ambiguous shared-inbox messages in a review queue.
