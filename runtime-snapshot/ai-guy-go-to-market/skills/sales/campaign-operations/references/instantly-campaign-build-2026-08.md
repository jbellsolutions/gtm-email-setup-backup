# Instantly v2 campaign build reference

## Verified endpoints and payload details

- `POST /api/v2/campaigns` creates a campaign. Include `sequences`, schedule, `email_tag_list`, tracking flags, and `stop_on_reply`.
- Campaign creation can return status `0`; call `POST /api/v2/campaigns/{id}/pause`, then re-fetch `GET /api/v2/campaigns/{id}`. Status `2` was the verified paused state.
- `POST /api/v2/leads/add` accepts a campaign plus `leads`; per-lead fields used successfully were `email`, `first_name`, `last_name`, `company_name`, `website`, and `custom_variables`. A 50-lead batch returned accepted counts and zero duplicate/invalid/incomplete counts.
- `POST /api/v2/leads/list` must use the filter key `campaign` to filter by campaign. `campaign_id` was not the correct filter key and returned mixed-campaign results. Paginate with `starting_after`, and assert each returned item's `campaign` equals the target campaign ID.
- `DELETE /api/v2/campaigns/{id}` deletes a campaign. Verify deletion with `GET /api/v2/campaigns/{id}` returning 404 before recreating.

## Evidence boundaries

- Campaign ID proves creation only.
- Pause response plus fresh GET proves paused state.
- Lead-add response proves accepted import only for that request. Final campaign membership requires paginated `leads/list` verification.
- Custom-variable persistence is not rendered-email verification. Keep campaign paused until preview/render inspection is complete.
- Do not activate or claim delivery from successful creation or upload responses.

## Reconciliation pattern

The verified email CSV is authoritative for addresses. Exact-domain enrichment is context, not proof of contact identity. Generic role addresses and unmatched domains should be held rather than personalized from the local-part. Record accepted, held, rejected, and verified counts separately.
