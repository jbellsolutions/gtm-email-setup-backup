# Positive-reply and booking reconciliation

Use this evidence boundary whenever an operator asks to inventory positive replies, compare them with calendar bookings, follow up, and recycle leads.

## Required evidence

1. Pull a fresh, complete provider inventory. Do not treat a cached positive-roster JSON, prior Slack report, or partial page as the current complete list.
2. Group messages by thread and deduplicate contacts. Use the latest inbound message for classification, but inspect the full thread for later outbound replies.
3. Keep these states separate:
   - genuine positive interest
   - specific question or objection requiring a tailored/manual reply
   - referral/routing response
   - OOO/auto-responder
   - unsubscribe/negative/poor fit
4. A reply is not a booking. A calendar-link mention, suggested time, or positive response does not count as booked without an independently verified calendar record.
5. Validate the calendar endpoint and response schema with a known-good probe before looping over a roster. HTTP 400/401/429, malformed response, or incomplete pagination means booking status is **unknown**, not “not booked.”
6. Do not send follow-ups or recycle leads while booking status is unknown. Preserve the roster and resume after the calendar query is fixed.

## Cadence policy

- Send the next follow-up only to a genuine positive who is confirmed unbooked, has not already received that follow-up, and is past the configured cooldown.
- Keep specific questions, objections, referrals, and unusual factual requests out of generic positive templates. Route them to a tailored/manual draft.
- Recycle into the sequence only after the lead has received at least two direct follow-ups, still has no independently confirmed booking, and is not suppressed by a negative, unsubscribe, OOO, or invalid-account state.
- After every send, require the provider's outbound ID and reconcile the thread before marking the follow-up complete.

## Reporting

Report counts by state and evidence quality: fresh inventory coverage, positive candidates, already-replied, follow-up sent/failed, booked, unbooked-confirmed, and booking-unknown. Never collapse “unknown” into “unbooked.”
