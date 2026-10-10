# Campaign bounce export and suppression review

Use after a campaign is finished and the operator requests bounced addresses.

## Safety

- Keep the named campaign paused/finished while exporting.
- Do not remove subscribers automatically from a bounce count.
- Suppress confirmed hard bounces before future sends; retain deferred recipients for reconciliation because deferrals can later deliver.
- Bird account totals are not campaign-specific. Filter message records by exact `from.email`, subject, and campaign send window.

## Export sequence

1. Pull Bird `/v1/email/messages` with pagination. If supported, add `status=bounced`.
2. Follow `next_cursor` until absent; deduplicate by message ID.
3. Select records whose sender, subject, and `created_at` match the campaign.
4. For each recipient, retain `email`, optional name, Bird message ID, timestamp, status, bounced count, and provider reason/error when available.
5. Write two files:
   - detailed CSV with message evidence;
   - unique one-column `email` CSV for suppression review.
6. Verify row counts and report whether bounce reasons were actually exposed. Do not infer hard/soft classification from aggregate counts alone.

## Known quirks

- The Bird `/v1/suppressions` route may be unavailable on the current platform API even when documented in local references. Export first and report the route error rather than claiming suppression was applied.
- Some message list responses expose no bounce reason. Leave the reason blank and label the CSV as confirmed bounced-message records.
- A naive first page or default pagination can undercount the campaign. Cursor pagination is required.
- Duplicate rows can occur if a message has multiple recipients or if a cursor page is repeated; dedupe by message ID and then by email for the unique file.

## Output handoff

Use native attachment paths in the final response, for example:

`MEDIA:/tmp/the-referral-channel-bounced-unique.csv`

Only claim attachment delivery when the native file-upload path confirms it; otherwise report the local path and blocker.