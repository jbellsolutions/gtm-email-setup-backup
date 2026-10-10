# Instantly account allocation and API evidence

## Minimal-capacity allocation

When the operator specifies a per-campaign daily target, do not attach every tagged inbox by default. Resolve the exact custom-tag ID, paginate accounts with `tag_ids` and `include_tags=true`, and re-check the returned account tags. Preserve actual per-account daily limits.

Allocate disjoint groups using the smallest practical number of accounts that meets each campaign target. For ten campaigns targeting 50/day, five Puzzle Inbox accounts per campaign worked when each group contained three accounts limited to 12/day and two limited to 10/day, yielding 56/day per group. This used 50 of 100 accounts and avoided assigning one inbox to multiple campaigns.

## Safe configuration sequence

1. Resolve the requested tag and paginate all matching accounts.
2. Verify each selected account is enabled, warmup-active, not setup-pending, and has a positive warmup score.
3. Partition accounts into disjoint groups and assert each group capacity is at least the campaign target.
4. PATCH each campaign with the selected `email_list`, `daily_limit`, and `daily_max_leads`.
5. Re-fetch each campaign and assert the exact email list, status, and limits.
6. Check `/campaigns/{id}/sending-status`; `campaign_draft` confirms it has not launched.
7. Never call the activation endpoint unless the user separately authorizes launch.

## Evidence boundary

A configured email list and daily limit prove configuration only. They do not prove actual delivery. Keep campaigns in Draft state until mailbox assignment and copy review are complete. Account tags and warmup scores are readiness signals, not proof of inbox reputation or successful delivery.
