# Instantly reply-send verification

## Durable pattern

For an approval-gated reply, verify the target inbound message and thread before sending. Check for any outbound message after the inbound timestamp, including records labeled `ue_type: 3`; Instantly can use `ue_type: 3` for outbound follow-up/reply records, so `ue_type: 1` alone is insufficient.

Use the exact `reply_to_uuid` from the target inbound record and preserve the POST response. A successful `POST /api/v2/emails/reply` response containing a new message `id`, recipient, sender account, thread ID, subject, and rendered HTML body is strong send evidence. A subsequent thread query may be incomplete or briefly stale, and broad inbox scans can hit HTTP 429. Do not resend solely because post-send verification is rate-limited or does not yet show the new record.

If additional verification is needed, query the exact thread with bounded backoff, match the returned message ID first, then match exact thread ID plus a distinctive body token and recipient. Treat API acceptance and later visibility as separate evidence fields. Never retry the POST unless duplicate checks establish that no outbound record exists.

## Copy/QC note

When a user supplies wording containing a banned deferential phrase such as “feel free to,” preserve the requested intent but make the smallest QC-compliant edit, such as “Give me a call or text.” Keep the user's phone number and substantive proposal unchanged unless asked otherwise.

## Reproduction evidence

A live approval-gated reply returned message ID `01a05ea7-ea2f-7197-a674-308ee99bd893`, recipient `info@modernmedicalfl.com`, sender `gail.kim@learnshop.co`, target thread `dc-xuILEE5X4ldYpawyr5l_nAv`, and an HTML body containing the requested phone number and collaboration proposal. The immediate follow-up thread query was not sufficient to rediscover the record, demonstrating why the POST response and duplicate-safe verification sequence must be retained separately.

## Campaign-wide reply sweep

When the operator asks to reply to everyone in a campaign, do not rely on the daemon's local state or a single unread page. Paginate `GET /emails` with the campaign filter and cursor, then build a candidate set from inbound records (`ue_type` 2 or 3) while excluding known sending-account addresses, opt-outs, auto-responders, and outbound/operator artifacts. Deduplicate by thread and inspect each candidate's reply text before acting.

For every candidate, use the exact inbound message ID as `reply_to_uuid` and check for any later outbound record before POSTing. Do not assume `ue_type: 1` is the only outbound marker: Instantly has returned `ue_type: 3` for outbound replies/follow-ups in live data. Also do not trust `GET /emails?thread_id=...` as an exact filter: live responses have returned unrelated/newest records and omitted the requested inbound. Treat the thread response as advisory only; match exact message ID, exact thread ID, recipient, timestamp, and body token client-side. If the exact inbound cannot be found or history is ambiguous, hold rather than risk a duplicate or reply to the wrong lead.

Respect the API's 20-requests-per-minute limit during campaign-wide work. Use cursor pagination, bounded exponential/backoff on HTTP 429, and avoid one history request per record unless the candidate has passed the initial inbound/opt-out/artifact filters. If a sweep returns zero candidates after a rate-limited or incomplete fetch, report the scan as incomplete rather than claiming there were no replies.

For a user-supplied campaign-wide template, preserve the substantive wording and phone number, but apply only mandatory QC edits (for example, replace banned deferential wording such as `feel free to` with `Give me a call or text`). Add a late-reply apology only when the inbound timestamp meets the operator's stated cutoff, and record exact sent IDs/counts. The POST response containing the new message ID, recipient, sending account, thread ID, subject, and rendered body is the primary send evidence; a stale or malformed follow-up query must not trigger a resend.
