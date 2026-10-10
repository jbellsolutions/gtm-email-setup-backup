# Revenue Partner CRM inventory: source-to-stage mapping and gates

## Source evidence

| Evidence | Default proposal | Required verification |
|---|---|---|
| Sent email only | Prospected | Sent message ID, recipient, date; do not treat a sent email as engagement |
| Cal.com booking | Booked | Booking/event ID, invitee email, scheduled time, cancellation status |
| Completed/past call | Showed up | Appointment/call evidence and outcome if available; a past event alone does not prove attendance |
| Agreement/proposal sent | Offer made | Agreement/document ID, recipient, sent date, and delivery/send status |
| Explicitly declined / disqualified | One loss (review) | Preserve exact reason and confirm intended stage name |
| Explicitly lost | Lost | Source evidence and date |

If evidence supports multiple stages, select the furthest stage only when the evidence is unambiguous and retain all earlier provenance. A cancelled booking should not remain `Booked` unless another active booking exists.

## Deduplication

1. Normalize email addresses by trimming whitespace and lowercasing.
2. Use normalized email as the primary person key.
3. If no email exists, use normalized full name plus company/domain, then mark the match as lower confidence.
4. Match against GHL by email before creating a contact. Never create duplicate contacts solely because the source names differ in punctuation or order.
5. Keep a source-evidence list per canonical person so multiple bookings, emails, calls, and agreements are not collapsed into a single unexplained record.

## Inventory output

The review artifact should contain one row per person with:

- canonical name, email, company/domain
- evidence sources and IDs
- earliest and latest evidence dates
- proposed stage and confidence
- existing GHL contact/opportunity IDs
- conflict or missing-data flags
- next action and close-plan inputs

## Verification checklist

Before writes: confirm target location/profile, existing pipeline ID/stage IDs, token scopes, source pagination completion, deduplication count, and the proposed `One loss` interpretation.

After writes: re-read the pipeline, query each created/updated contact and opportunity, confirm location/pipeline/stage IDs, compare counts to the approved manifest, and report any skipped/conflicted rows. Never report completion from a command exit code alone.
