# Campaign cleanup and reconciliation

Use for a finished ListMonk campaign when the operator requests bounce exports, suppression, unsubscribe reconciliation, unsent-recipient identification, duplicate verification, or tracking repair.

## Evidence gates

- Keep the campaign finished/paused and enforce a no-send hold throughout cleanup.
- A test email is still email activity. Do not send it under `NO SEND` unless separately authorized.
- ListMonk application counters (`sent`, `to_send`, `views`, `clicks`, `bounces`) and Bird transport counters have different scopes and denominators.
- `to_send - sent` is only a reconciliation gap. It is not proof of failed, bounced, deferred, or unsent addresses.

## ListMonk read-only checklist

1. Fetch the campaign record and record `status`, `to_send`, `sent`, `views`, `clicks`, `bounces`, subject, sender, lists, and headers.
2. Fetch the target list and paginated subscribers. Record the list subscription status separately from the global subscriber status.
3. Query analytics endpoints with explicit dates: `/api/campaigns/analytics/views|clicks|bounces|links?id=...&from=YYYY-MM-DD&to=YYYY-MM-DD`.
4. For subscriber-level results, require actual per-recipient campaign events or provider records. Do not derive them from aggregate counters.

## Bird export gate

- Filter provider messages by exact campaign sender, subject, and send window before classifying.
- Paginate using the provider's documented cursor semantics. Validate that each page advances by checking page IDs and cursor progression. Never use an API response cursor that is visibly truncated or unchanged; stop and report the provider pagination blocker rather than inventing a complete export.
- Preserve `email, bounce_type, reason, timestamp`. Leave `reason` blank when Bird does not expose it. Do not infer hard/soft/block type from account aggregates.
- Deduplicate by provider message ID, then separately produce a unique-recipient view.
- Account summary totals are health snapshots only. They cannot reconcile a campaign without recipient-level filtering.

## Suppression rules

- Suppress only confirmed permanent evidence: hard bounce, or block/out-of-band with an explicit invalid-recipient reason such as `550 5.1.1` or “mailbox does not exist.”
- Retain soft bounces, deferrals, greylisting, full-mailbox, and reputation blocks unless a later recipient-level event establishes permanence.
- If the complete typed export cannot be produced, apply zero bounce-based suppressions and report why.

## Unsubscribes and webhook wiring

- Reconcile Bird unsubscribes only after filtering by campaign sender, subject, and window. Account-wide unsubscribe totals cannot prove campaign-specific compliance.
- Verify ListMonk’s existing list subscription statuses and do not assume provider events synced merely because ListMonk bounce processing is enabled.
- Treat `bounce.enabled`, `bounce.webhooks_enabled`, and an enabled bounce mailbox as separate settings. Automatic suppression is unverified until a destination is configured and a controlled event is observed.

## Tracking repair

- For future campaigns, require `privacy.disable_tracking=false` and `privacy.individual_tracking=true`.
- Confirm tracking flags and wrapped-link behavior on the draft before sending. Existing sends with tracking disabled cannot be backfilled.
- A tracking verification test requires explicit permission to send, plus a real recipient-side open and click. Do not claim this test passed without both events registered.
