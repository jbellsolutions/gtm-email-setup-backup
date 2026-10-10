# Reply-to-CRM migration preflight

Use this checklist when moving outbound-reply records from Instantly, Instantly, or another sender into a CRM such as GoHighLevel.

## Evidence boundaries

- A browser URL containing `/contacts/detail/{contact_id}` identifies one contact view, not an import endpoint or proof of location-level write access.
- Source CLI availability and credential availability are separate facts. Run a read-only health/list call before pulling records.
- A browser session, API token, and private integration token are not interchangeable. Verify CRM location ID, token scopes, and endpoint/UI import route independently.
- If the source credential returns 401/403, stop. Do not use cached reply files as if they were current unless explicitly labeled with their date and scope.

## Dry-run output

Before any write, produce:

1. Source platform and exact campaign IDs/names.
2. Authenticated read-only result and timestamp.
3. Reply count and inclusion/exclusion rules.
4. Available contact fields and missing/masked phone count.
5. Destination location ID and credential/scope check.
6. Proposed field mapping, including raw reply text and source IDs.
7. Treatment of opt-outs, hostile, negative, and OOO records.

## Recommended mapping

| Source | CRM field / note |
|---|---|
| first/last name | contact name fields |
| email | email |
| phone | phone; preserve original formatting and source |
| company | company name |
| campaign ID/name | custom field or tag |
| thread/message ID | custom field for deduplication |
| reply timestamp | custom field or note |
| raw reply body | note/custom field |
| classification | tag/status/custom field |
| source URL/platform | custom field or note |

Keep a canonical JSON/CSV export before import. Deduplicate by normalized email, then use source thread/message ID for audit and idempotency. Never overwrite a known phone with a blank or masked value. After import, re-query and compare every submitted record and key fields.

## User authorization gate

If the user says “all replies,” clarify in the operational record that this includes positive, neutral, negative, OOO, unsubscribe, and hostile replies. Those contacts may be imported for history, but suppression/opt-out records must remain excluded from future outreach.
