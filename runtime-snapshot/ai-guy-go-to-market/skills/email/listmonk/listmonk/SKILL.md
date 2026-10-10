---
name: listmonk
description: Operate a listmonk newsletter server via its REST API — manage lists, add/import subscribers, create and send campaigns, send transactional email, check stats. Use when asked to "send a newsletter", "add subscribers", "create a campaign", "email the list", "import contacts into listmonk", or anything involving listmonk.
---

# Listmonk Operations

Drive a self-hosted [listmonk](https://listmonk.app) instance (newsletter + mailing list manager, Mailchimp alternative) through its REST API.

## Setup (once per machine)

The skill reads connection details from environment variables (put them in your shell profile or the project's `.env.local`):

```bash
export LISTMONK_URL="https://listmonk-production-2930.up.railway.app"  # your instance, no trailing slash
export LISTMONK_USER="admin"          # admin username OR an API user name
export LISTMONK_TOKEN="..."           # that user's password OR API token
```

Prefer a dedicated API user over admin credentials: in the listmonk admin UI go to **Admin → Users → + New**, choose type **API**, copy the generated token, and use that as `LISTMONK_USER`/`LISTMONK_TOKEN`.

If these vars are unset, ask the user for their listmonk URL and credentials before doing anything else.

## The helper script

All operations go through [scripts/lm.sh](scripts/lm.sh) (curl wrapper, auto-auth, pretty-prints JSON):

```bash
scripts/lm.sh health                          # connectivity check — RUN THIS FIRST
scripts/lm.sh lists                           # list all mailing lists
scripts/lm.sh create-list "Weekly Digest" public single
scripts/lm.sh subs [list_id]                  # subscribers (optionally filter by list)
scripts/lm.sh add-sub jane@x.com "Jane Doe" 1,2   # email, name, list IDs (pre-confirmed)
scripts/lm.sh campaigns                       # list campaigns
scripts/lm.sh create-campaign "Name" "Subject line" 1,2 body.html   # lists + HTML body file
scripts/lm.sh test-campaign 3 me@x.com        # send test of campaign 3
scripts/lm.sh start-campaign 3                # START SENDING campaign 3 (confirm first!)
scripts/lm.sh tx 2 jane@x.com '{"order_id":"123"}'   # transactional send: template, recipient, data
scripts/lm.sh raw GET /api/settings           # any other endpoint
scripts/lm.sh raw POST /api/lists '{"name":"VIP","type":"private","optin":"single"}'
```

For anything the script doesn't cover, use `raw` with the endpoint reference in [references/api.md](references/api.md).

## Workflow rules

For the validated raw-HTML, hosted-media, and Reply-To draft sequence, see `references/raw-html-draft-media-replyto.md`.

1. **Always `health` first in a session — fail fast on bad URL/credentials.** The REST API does not use HTTP Basic Auth. Its header is `Authorization: token <username>:<password-or-api-token>`. A Basic-auth `401/403` is an authentication-method error, not proof that the instance is unavailable. If API credentials fail but admin UI credentials are available, authenticate at `/admin/login` with the supplied username/password and use the same-origin browser session for the explicitly authorized operation. UI login success is evidence of UI access, not proof that API credentials work. When creating a draft in the UI, inspect the available campaign lists and exact IDs/names first; stop for clarification if duplicate list names exist rather than guessing. For a draft-only operation, select the appropriate list, choose Raw HTML, populate campaign metadata, and save/continue without using Send, schedule, publish, or start controls. Create a dedicated API user in the UI when API automation is required.
2. **Campaign sending is irreversible.** Before `start-campaign`: show the user the campaign subject, body summary, and recipient count (`GET /api/campaigns/{id}` → `lists`, and subscriber counts), send them a `test-campaign` to their own address if they want one, and get explicit confirmation. Never start a campaign unprompted. A `NO SEND`, `HARD HOLD`, or “do not send campaign mail” instruction also forbids a test email unless the user explicitly authorizes that separate test.
3. **Bulk imports**: for >100 subscribers use the CSV import endpoint (see references/api.md § Import) rather than looping `add-sub`.
4. **Subscribers added via API** with `preconfirm_subscriptions: true` skip double opt-in — only do this for contacts who already consented.
5. SMTP must be configured in the admin UI (Settings → SMTP) before anything sends. If sends fail, check that first, then `GET /api/logs`. For provider reconciliation, treat ListMonk `sent`, `views`, `clicks`, and `bounces` as application-level counters, not proof of provider delivery.
6. Content: campaigns accept `content_type` of `richtext`, `html`, `markdown`, or `plain`. Use `{{ .Subscriber.FirstName }}`-style Go template tags for personalization; `{{ UnsubscribeURL }}` is auto-appended by the default template.
7. **Tracking is a two-setting gate plus an evidence gate.** `privacy.disable_tracking=false` permits tracking, but `privacy.individual_tracking=true` is required for subscriber-level attribution. Confirm both settings before a future send, and inspect the campaign body/config for tracking-disabled flags. Existing campaigns sent with tracking disabled cannot have opens or clicks reconstructed. Do not call zero analytics “zero engagement” when instrumentation was off or analytics is empty. For a live proof test, capture the campaign’s views/clicks baseline before sending, send only to the explicitly authorized internal seed, then require recipient-side confirmation that the message was opened and a tracked link clicked. Re-read the same campaign after those actions and report the before/after counters. A test endpoint returning `{"data":true}` proves queue/application acceptance only; a pre-existing view count, unchanged view count, or zero clicks is not proof that the recipient opened or clicked. Never claim end-to-end tracking success without observed counter movement attributable to the test.
8. **Bounce-processing is separate from provider-webhook wiring.** Enabling ListMonk bounce processing does not configure Bird events. Verify `bounce.enabled`, `bounce.webhooks_enabled`, and/or an enabled bounce mailbox independently. Do not claim automatic suppression until a destination is configured and a controlled event is observed. Suppress only recipient-level permanent-bounce evidence; never suppress a whole aggregate bounce category.
9. **Recipient reconciliation requires recipient-level evidence.** `to_send - sent` is an unresolved gap, not a list of unsent recipients. Do not create an “unsent” CSV, infer duplicates, or retry the gap unless a per-recipient send ledger is available and reconciled against the transport provider. Campaign status `finished` alone does not prove every audience member received one message.
10. For read-only campaign analytics, query `/api/campaigns/analytics/{views|clicks|bounces|links}` with explicit valid `from` and `to` dates; an empty result plus disabled tracking means unavailable instrumentation, not confirmed zero activity. See `references/campaign-cleanup-reconciliation.md` for the verification matrix.

11. **Real-send tracking proof requires a non-empty seed audience.** Create a dedicated private seed list, add the explicitly authorized internal recipients, then GET the list and each subscriber before creating the proof campaign. Verify `subscriber_count`, confirmed subscription status, campaign `to_send`, and `sent: 0` are all correct. Never start a campaign whose proof list reports `subscriber_count: 0` or whose campaign reports `to_send: 0`; a running/paused status transition with zero recipients is not a tracking test and must not be reported as one.

12. **SMTP provider isolation must be persisted and re-read.** When switching providers, change only the intended SMTP enable flags, save through the settings UI/API, then re-fetch `/api/settings` and verify exactly one provider is enabled before any test or send. UI checkbox clicks are not evidence of persistence. Record the provider initialization line from `/api/logs` as a second check. If the persisted state still has both providers enabled, do not send because ListMonk may round-robin across them.

13. **Proof campaign lifecycle safety.** For an authorized small real-send proof, capture the baseline campaign counters, verify the seed list is non-empty, start the campaign, immediately GET the persisted campaign state, and pause only after confirming the actual recipient count. If the campaign starts with zero recipients, pause it, verify `sent: 0`, and report the proof as not performed. Do not infer delivery, open, click, or provider success from an HTTP `200`/`{"data":true}` response alone.

14. **Campaign identity and template verification.** Before a proof or production send, GET the exact campaign and verify ID, name/issue, subject, `from_email`, Reply-To header, target list, template/content type, and body length/hash. Do not use a different issue as a substitute for the requested campaign. A draft campaign with hosted images can still be invalid if the audience, provider, or persisted metadata is wrong.

## Common recipes

**"Send this newsletter to my list":** health → `lists` (find target list id + subscriber count) → write HTML body to a temp file → `create-campaign` → `test-campaign` to the user's own email → report recipient count and wait for user's go-ahead → `start-campaign` → poll `GET /api/campaigns/{id}` until `status: finished`, report sent count.

**"Add these people to the list":** health → `lists` → `add-sub` per contact (or CSV import for many) → confirm final count via `subs <list_id>`.

**"How did the last campaign do?":** `campaigns` → read `views`, `clicks`, `sent`, `bounces` from the response; `GET /api/campaigns/analytics/*` endpoints for detail.
