# Shared-calendar investigation checklist

## Evidence to capture

- Authenticated Google identity, when exposed by the integration.
- Calendar-list entries: `id`, display name, and access role.
- Exact target display name and requested invitee identity.
- Inclusive search start and end timestamps, including timezone.
- Query terms and whether a full bounded listing was also inspected.
- Matching event summaries, dates, and event IDs/links when available.

## Reporting template when target is missing

> I could not find the requested calendar in the calendars visible to the connected Google account. Visible calendars: `<list>`. I searched the accessible fallback calendar(s) from `<start>` through `<end>` for `<terms>` and found `<result>`. This indicates the connection may be authenticated as a different identity, or the share has not been accepted/propagated. Please verify the invitation was sent to the connected Google account and accepted, then retry.

Never phrase this as “the target calendar has no events” unless the target calendar was actually resolved and queried.