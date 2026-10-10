# Instantly solar sweep and routing

Use this reference when the operator asks for solar-only pending replies.

## Scope gate

1. Fetch `GET /campaigns` first.
2. Confirm the target is exactly `solar | open door`, campaign ID `dbd68956-2dc6-47e4-a56e-5a518db39381`.
3. Filter `/emails` client-side to that campaign ID. Never include roster, marketing-agency, or other owned-audience campaigns.

## Complete scan

- Follow every `next_starting_after` cursor. A short page is not an end marker.
- Respect the 20-requests/minute limit with backoff. If pagination is incomplete, report the result as incomplete and do not claim an all-replies result.
- Include inbound `ue_type == 2`; treat `ue_type == 3` as inbound only after sender-direction verification and connected-account exclusion.
- Normalize `body.text`/`body.html`, strip HTML and quoted content, and classify the earliest genuine inbound reply per `thread_id`.

## Routing

For solar campaign reporting, human replies have no neutral class:

- Explicit `no`, `no thanks`, `not interested`, and equivalent direct rejection -> negative.
- Every other human-authored reply -> positive and draft.
- OOO, ticket acknowledgement, verification challenge, employee departure/routing, generic customer-service acknowledgement, and other machine-generated messages -> operational exclusion, no draft.

Do not let `no` inside a signature or quoted text create a negative. Classify the unquoted lead-authored segment.

## Pending-response check

Local daemon state means processed/seen, not replied. For each candidate thread, check for a later outbound record (`ue_type == 1`) after the earliest inbound timestamp. Only positive threads with no later outbound record belong in the pending report.

## Drafting

Create an individual draft for every pending positive. Keep the solar offer specific: local referral partners, outreach/campaign follow-through, commission on closed sales, and the approved booking URL:

`https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery`

Do not use the AI-operator or marketing-agency offer in this workflow. Do not send drafts unless the user separately approves sending. For the solar auto-send exception, apply the hard-stop rules in `instantly-solar-auto-reply` and verify the outbound ID after sending.

## Known operational exclusions

Observed records that must not become drafts include:

- `Out of office`, `OOO`, vacation, leave, limited access/bandwidth, traveling, or slow-response notices.
- Ticket systems (`Ticket Received`, `service request`, dispatcher acknowledgements).
- Email-verification challenges asking the sender to prove they are human.
- Employee departure, unmonitored mailbox, acquired/closed company, or contact-routing notices.
- Generic “we received your email / will respond” customer-service acknowledgements.

The full result should report counts for inbound records, unique threads, pending positives, operational exclusions, explicit negatives, and already-answered positives.