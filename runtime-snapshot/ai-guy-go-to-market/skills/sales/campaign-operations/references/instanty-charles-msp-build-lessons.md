# Instantly campaign build lessons: tagged accounts, pausing, and upload gates

## Verified API patterns

- Resolve tags through `GET /api/v2/custom-tags?limit=100`.
- Enumerate account/campaign tag mappings through paginated `GET /api/v2/custom-tag-mappings`.
- Assign an account tag with `POST /api/v2/custom-tags/toggle-resource`:
  `{"tag_ids":[tag_id],"resource_type":1,"resource_ids":[account_email,...],"assign":true}`.
- Query an account's campaigns through `GET /api/v2/account-campaign-mappings/{email}`.
- Pause a campaign through `POST /api/v2/campaigns/{id}/pause`.
- Create a campaign through `POST /api/v2/campaigns`; status `0` is Draft. Use `email_list`, `email_tag_list`, and variable-only sequence bodies when copy is stored per lead.
- Upload through `POST /api/v2/leads/add` and verify using `POST /api/v2/leads/list` with filter key `campaign` and cursor pagination.

## Operational lessons

1. A tag-based selection can be exact, but account-to-campaign mappings must be fetched per selected account before any pause operation.
2. Campaign pause is campaign-wide. If selected accounts share an active campaign, pausing it stops every account in that campaign. Report this impact explicitly and never call it a mailbox-only pause.
3. API acceptance is not editorial approval. Do not upload a batch with unresolved banned words, forbidden punctuation, placeholder names, weak research hooks, or failed word counts simply because the campaign endpoint accepts it. Keep such output local and the campaign Draft/Paused.
4. Website retrieval can return JavaScript/polyfill boilerplate instead of usable business evidence. Store the retrieval result as a research-status field, but do not present boilerplate as a personalization hook. Hold or rewrite the lead using only defensible supplied facts.
5. Generic/shared inboxes may be deliverable but do not establish a named decision maker. Keep them separately labeled and avoid personal claims or guessed names in copy.
6. A complete upload report plus a paginated campaign lead query is required. Confirm submitted, accepted, duplicated, blocklisted, invalid, and final stored counts separately.

## Review handoff checklist

- Campaign ID, fresh status, and exact account count.
- Tag ID and post-assignment mapping count/set.
- Every affected active campaign and the campaign-wide pause consequence.
- Source, generated, held, uploaded, and stored lead counts.
- Copy audit result before upload, not only after upload.
- Explicit statement that activation and sending did not occur.
