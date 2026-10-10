# Cross-Platform Email Operations Registry

## Why ListMonk did not show the reported campaigns

ListMonk only reports campaigns created and launched inside ListMonk. Campaigns sent through JangoMail, Instantly/Winnr, Bird API-direct, or Resend-direct do not appear in ListMonk. Therefore ListMonk cannot be the total-volume source when multiple senders are active.

## Required registry structure

Use a single Notion landing page with these databases or equivalent views:

- **Email Platforms:** platform, purpose, status, route, sending domain, tracking owner, health, owner. Store references to secrets, never secret values.
- **Email Campaign Registry:** campaign name/ID, platform, transport, audience, owner, status, planned volume, actual sent/attempted volume, delivered, bounces, opens, clicks, replies, source link, notes.
- **Email Daily Stats:** date, platform, campaign, attempted, sent, delivered, bounces, opens, clicks, replies, reconciled checkbox, discrepancy notes.
- **Email Ops Tasks:** task, owner, status, due date, priority, related campaign/platform, notes.

## Read-only onboarding inventory

For every platform, collect before changing configuration or sending:

1. Account usage and plan/quota.
2. Campaign list with IDs, subjects/names, dates, recipients, status, and engagement.
3. Delivery failures: bounces, blocks, complaints, and connection failures.
4. Sending route: direct API, SMTP, or application-managed SMTP.
5. Tracking owner and whether open/click tracking is enabled.
6. Current domain/authentication health.

Record platforms with zero campaigns so the inventory reflects configured infrastructure, not only observed sends.

## Reconciliation rules

- Keep application-level campaign stats separate from transport-level provider stats.
- Treat provider recipients/attempts, accepted, delivered, bounces, and blocks as distinct fields.
- Do not add pre-send suppressed/removed addresses to attempted or delivered totals.
- Do not infer better inbox placement from open rate alone. Require comparable audience, delivered denominator, tracking configuration, and time since send.
- If an account reaches its sending quota, create an explicit high-priority ops task and stop or gate further sends through that route until the limit is resolved.

## Session findings, July 31, 2026

- JangoMail reported `emails_sent=5000` against `emails_allowed=5000`, making the account limit an immediate blocker.
- Existing JangoMail campaign history showed recipient and engagement fields, but some draft/test records had zero recipients and must not be included in production totals.
- Xander reported that Green Room Campaign 4 was sent July 30 through Bird SMTP and had stronger open performance than prior JangoMail sends. Exact Bird denominators and counts were still required, so this was recorded as a hypothesis plus a follow-up task rather than a confirmed deliverability conclusion.
- The Notion landing page was created and seeded with Email Platforms, Email Campaign Registry, Email Daily Stats, and Email Ops Tasks structures. The four tracked platforms were JangoMail, ListMonk, Bird, and Resend.

## Common implementation pitfall

A Notion integration wrapper may expose a create-page tool whose schema appears available but silently drops required `parent_id` and `title` fields when called through a multi-execute wrapper. If that happens, use the canonical Notion REST API with `POST /v1/pages` and `parent: {page_id: ...}` after checking for duplicates. Verify the created page by reading its child blocks and checking the expected count/types.
