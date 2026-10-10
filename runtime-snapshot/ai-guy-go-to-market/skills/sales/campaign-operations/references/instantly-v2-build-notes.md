# Instantly v2 build notes

## Verified API shapes

- `GET /api/v2/accounts` supports `tag_ids`, `include_tags`, `limit`, and cursor pagination via `starting_after`.
- `GET /api/v2/custom-tags` returns tag IDs and labels.
- `POST /api/v2/campaigns` creates campaigns with `campaign_schedule`, `sequences`, `email_list`, `stop_on_reply`, `stop_on_auto_reply`, tracking controls, and `insert_unsubscribe_header`.
- `POST /api/v2/campaigns/{id}/pause` pauses a campaign.
- `GET /api/v2/campaigns/{id}` verifies status and sequence configuration.
- `POST /api/v2/leads/add` accepts up to 1,000 leads and supports `campaign_id`, `leads`, and per-lead `custom_variables`.
- `POST /api/v2/subsequences` supports parent campaign, trigger conditions including campaign-completed-without-reply, schedules, and sequences.

## Operational evidence

- The `puzzle inbox` custom tag was resolved to tag ID `7797a156-d8be-4e51-978f-9168f25f377b`.
- The first filtered account response was capped at 100; cursor pagination must be checked before claiming the complete population.
- Campaign creation initially rejected `America/New_York` because the account API schema allowed only its enumerated timezone values. `Etc/GMT+12` was accepted as a documented value.
- Campaign creation returned status `0`; explicitly calling `/pause` returned 200 and a fresh campaign GET returned status `2`.
- A lead import attempt returned HTTP 403 with `Lead limit reached. Remaining uploads: 248.` The batch was rejected before lead addition. Treat this as a quota hard stop and do not claim leads were uploaded.
- Five review campaigns were created paused with three steps each, but creation alone did not establish campaign chaining or rendered custom-variable content.

## Required evidence boundary

A campaign ID proves creation only. A paused status proves pause only. A successful lead-add response proves accepted import only after re-querying counts. Custom-variable persistence is not preview/render verification. Campaigns must remain paused until the user reviews them.
