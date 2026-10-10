# Instantly Campaign Stats Interpretation

Use this reference when an operator sees sent, completed, and reply numbers that appear inconsistent.

## Verified live example

A live review of three active campaigns showed:

| Campaign | Sent/contacted | Unique replies | Automatic replies | Bounces | Completed |
|---|---:|---:|---:|---:|---:|
| Mamas and Minis | 20 | 0 | 0 | 1 | 0 |
| PR Conferences | 200 | 0 | 1 | 3 | 0 |
| Charles MSP | 300 | 3 | 0 | 3 | 3 |

The dashboard fields mean different things:

- `emails_sent_count` / `contacted_count`: cumulative messages sent or contacts reached, not necessarily today's activity unless timestamps confirm it.
- `reply_count_unique`: unique prospect replies. This is the primary engagement count.
- `reply_count_automatic_unique`: automated responses, such as OOO notices or ticket acknowledgments. Keep them visible, but do not count them as genuine prospect interest.
- `completed_count`: leads that reached the sequence-completion state. It is not a reply count and must never be described as “people who responded.”
- `daily_limit`: a ceiling, not a guaranteed send quantity. A campaign may send fewer messages because of eligible-lead availability, account capacity, scheduling, start date, or sequence state.

## Review procedure

1. Pull live campaigns and analytics, validating response shapes (`campaigns`/`accounts` commonly use `data.items`; analytics may use a list under `data`).
2. Pull `/emails` with bounded cursor pagination. Respect the provider rate limit and follow every cursor; a short page does not prove the scan is finished.
3. Reconcile current-day activity from message timestamps, separating outbound and inbound records. For the observed payload, `ue_type: 1` was outbound and `ue_type: 2` was inbound. Keep the broader inbound guardrails from the monitoring runbook for later payload variations.
4. Separate genuine prospect replies from automatic replies using sender direction, connected sending-account exclusion, subject/body signals, and quote-stripped body text.
5. Present a compact per-campaign table before explaining terminology. State whether figures are cumulative, observed today, or exact provider totals.
6. If a real reply exists, surface it as the next action even when the dashboard's “completed” field is zero or otherwise unrelated.

## Pitfalls

- Do not report “no emails sent” when the provider shows verified sent message records; clarify that the user may be looking at today's view versus cumulative or vice versa.
- Do not report an OOO or ticket-system message as a sales response merely because it appears in inbox activity.
- Do not infer a sending failure from `sent < daily_limit`; inspect schedule, campaign status, eligible leads, mailboxes, and delays first.
- Do not call a campaign stalled solely because `completed_count` is zero. New leads may have only received the first step and remain active in the sequence.
