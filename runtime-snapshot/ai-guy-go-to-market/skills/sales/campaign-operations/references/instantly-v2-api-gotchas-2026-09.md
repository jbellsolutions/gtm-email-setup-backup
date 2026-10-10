# Instantly v2 — replacing copy on already-uploaded leads (2026-09-03)

Verified while swapping a user-dictated CTA into a live paused campaign (705 leads, zero sends).
Create-payload shapes and the lead-cap 403 are NOT here — see `instantly-v2-schema-quirks-2026-09.md`.

## There is no lead update route
- `POST /api/v2/leads/update` → 404. `PUT /api/v2/leads` → 404. v1 `POST /api/v1/lead/update` → 404 (with and without `api_key` in body).
- The only way to change stored custom_variables is DELETE + re-add.
- Re-adding a lead that still exists returns `status: success` with `leads_uploaded: 0, duplicated_leads: 1` — the platform silently keeps the OLD variables. Always delete first, and verify the stored payload after re-adding.

## DELETE semantics (caution)
- Shape: `DELETE /leads` with body `{campaign_id, leads: [ids...]}` → `{"count": N}`.
- CAUTION: a call carrying a single lead id once deleted 50 (count: 50). After every delete round, re-list the campaign (`POST /leads/list`, filter key `campaign`, paginate `starting_after`) and assert the remaining count before continuing.
- Only run delete/re-add swaps on a campaign that has never sent (paused since creation, zero messages) — otherwise sequence position and lead timestamps are lost.

## Verified swap workflow
1. List all lead ids for the campaign; paginate to completion.
2. Delete in rounds; re-list and assert the remaining count after each round (ids come back with `id` + `email` keys).
3. Re-add with fresh `custom_variables` in 50-lead batches via `POST /leads/add`; assert `leads_uploaded == submitted` per batch.
4. Reconcile the final count against the plan; spot-read `lead.payload` (variables live under `payload` in leads/list responses) and confirm the new copy is actually stored.
5. Re-verify pause state: campaign `status == 2` AND `/sending-status` → `campaign_paused`.

## Verbatim-CTA protection when regenerating copy
When the user dictates exact CTA/proof copy and a generator applies automated rewrites (e.g. a contraction pass), swap the dictated string for a placeholder before the rewrite pass and restore it after — a global "I will → I'll" contraction silently rewrote the dictated CTA in all 57,290 bodies until this guard was added. Also: grep the full cohort (all steps) for any invented proof/case-study line the user rejects, and re-run word-count QA after swapping a longer/shorter CTA (a 4-word-longer CTA pushed 4,611 step-8 bodies over a 100-word cap and needed three targeted TRIMS entries to converge).
