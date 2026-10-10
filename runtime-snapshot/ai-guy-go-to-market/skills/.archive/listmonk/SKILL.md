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
scripts/lm.sh create-campaign "Name" "Subject" 1,2 body.html  # basic: lists + HTML body
scripts/lm.sh create-campaign "Name" "Subject" 1,2 body.html html "Name <a@b.com>" 7 "reply@b.com"  # full: + from_email, template_id, reply_to
scripts/lm.sh test-campaign 3 me@x.com        # send test of campaign 3 to one address
scripts/lm.sh test-campaign 3 me@x.com you@x.com  # send test to MULTIPLE addresses
scripts/lm.sh start-campaign 3                # START SENDING campaign 3 (confirm first!)
scripts/lm.sh upload-media images/banner.jpg  # upload image → returns hosted URL
scripts/lm.sh logs                            # recent server logs (check SMTP errors)
scripts/lm.sh tx 2 jane@x.com '{"order_id":"123"}'   # transactional send: template, recipient, data
scripts/lm.sh raw GET /api/settings           # any other endpoint
scripts/lm.sh raw POST /api/lists '{"name":"VIP","type":"private","optin":"single"}'
```

For anything the script doesn't cover, use `raw` with the endpoint reference in [references/api.md](references/api.md). The Issue 002 media upload failure and recovery sequence is documented in [references/issue-002-media-upload-failure.md](references/issue-002-media-upload-failure.md). For multi-draft HTML persistence, browser/API credential boundaries, and chat attachments, see [references/listmonk-multi-draft-and-attachments.md](references/listmonk-multi-draft-and-attachments.md). For large HTML visual drafts and stale-body diagnosis, use [references/large-html-draft-debugging.md](references/large-html-draft-debugging.md).

## Creating a raw passthrough template

When sending standalone HTML newsletters (e.g. from a zip file with their own `<html>`/`<head>`/`<body>`), the default ListMonk templates **double-wrap** your content in their own HTML shell. To avoid this, create a raw passthrough template:

```bash
scripts/lm.sh raw POST /api/templates '{"name":"Raw Passthrough","type":"campaign","body":"{{ template \"content\" . }}\n{{ TrackView }}"}'
```

This template outputs the campaign body verbatim with no wrapper, plus the open-tracking pixel. Use the returned template ID when creating campaigns that already have their own HTML structure.

## Uploading and wiring images

For newsletters with local image folders (e.g. `images/*.jpg`):

1. Upload each image via `POST /api/media` (multipart `file=@path`). The response includes a `url` field.
2. Replace all `src="images/..."` references in the HTML with the hosted URLs.
3. Check for remaining `images/` references — HTML comments containing them are harmless, but `src=` attributes must all point to the hosted URLs.

```bash
scripts/lm.sh upload-media images/banner.jpg   # returns JSON with "url" field
```

## Reply-To, from_email, and headers

- **Reply-To** is NOT a top-level campaign field. Set it via the `headers` array: `"headers": [{"key": "Reply-To", "value": "reply@example.com"}]`
- **from_email** uses the format `"Display Name <email@domain.com>"` and should match a sender configured in ListMonk SMTP settings.
- **template_id** selects which template wraps the campaign body. Use the raw passthrough template (above) for standalone HTML.
- **messenger** must be `"email"` — the test endpoint fails with "Unknown messenger" if this is omitted. `create-campaign` in lm.sh sets this automatically.

## Merge field conversion

When importing newsletter HTML from another ESP, convert merge field placeholders to ListMonk's Go template syntax:

| Other ESP placeholder | ListMonk equivalent |
|---|---|
| `{{VIEW_ONLINE_LINK}}` | `{{ MessageURL }}` |
| `{{UNSUBSCRIBE_LINK}}` | `{{ UnsubscribeURL }}` |
| `{{ .Subscriber.FirstName }}` | (already ListMonk syntax) |

## Click tracking

ListMonk auto-tracks all links in campaign bodies when `privacy.disable_tracking` is `false` (the default). No need to manually wrap links with `{{ TrackLink }}` — leave editorial links raw and ListMonk handles click tracking automatically.

## SMTP credential troubleshooting

If test sends fail with `535 Authentication credentials invalid`:

1. `GET /api/settings` and inspect the `smtp` array.
2. Update the password field for the relevant SMTP block (e.g. the Resend API key for `smtp.resend.com`).
3. `PUT /api/settings` with the **entire** settings object (PUT replaces, not merges).
4. **The server restarts** after a settings PUT — wait ~5 seconds, then `health` check before retrying.
5. Check `GET /api/logs` for confirmation — successful sends produce no error log entries.

## Image validation without vision tools

When vision/image analysis tools are unavailable, use file entropy (bits/byte) as a proxy to detect flat placeholder images vs real content:

```python
import math, collections
def file_entropy(path):
    with open(path, 'rb') as f: data = f.read()
    freq = collections.Counter(data)
    total = len(data)
    return -sum((c/total) * math.log2(c/total) for c in freq.values())
# entropy < 5.0 = likely flat placeholder; 7.5+ = real photographic content
```

MD5 hash comparison detects duplicate/identical images across story cards.

## Workflow rules

1. **Always `health` first in a session — fail fast on bad URL/credentials.**
2. **Admin UI credentials and REST API credentials are not interchangeable.** If the dedicated API token is unavailable or rejected, use the already-authenticated admin browser session and make same-origin `fetch()` calls from the ListMonk UI. Do not keep retrying REST with admin username/password and do not report an API path as available when it returns 403.
3. **For large HTML drafts, use the proven UI sequence:** create the campaign shell with name, subject, From address, target list, select `Raw HTML`, then continue to the Content step and inject the complete body through the editor's actual content mechanism. Verify the saved campaign by returning to the campaign record and checking `status: draft`, `sent: 0`, target list, `content_type: html`, and exact/non-empty body length or hash. A shell with metadata is not a completed draft.
4. **Complete one campaign end-to-end before starting the next.** After each write, GET/inspect and record its campaign ID and body verification. If a content write fails, stop that campaign and diagnose the editor/API path rather than creating four unverified shells.
5. **Never claim completion from a partially filled form or a successful navigation.** The only completion proof is a persisted campaign record whose body matches the intended HTML.


2. **Campaign sending is irreversible.** Before `start-campaign`: show the user the campaign subject, body summary, and recipient count (`GET /api/campaigns/{id}` → `lists`, and subscriber counts), send them a `test-campaign` to their own address if they want one, and get explicit confirmation. Never start a campaign unprompted.
3. **Bulk imports**: for >100 subscribers use the CSV import endpoint (see references/api.md § Import) rather than looping `add-sub`.
   - **⚠️ CSV quoting pitfall:** If your CSV has an `attributes` column with JSON values (e.g. `{"company": "Acme"}`), the JSON quotes will break ListMonk's CSV parser with `bare " in non-quoted field`. Fix: use Python's `csv.writer` to produce properly quoted CSV (fields with commas or quotes get wrapped in double quotes, internal quotes doubled). Never hand-build CSV strings with JSON attributes.
   - **Import status is async:** `POST /api/import/subscribers` returns immediately with `status: "importing"`. Poll `GET /api/import/subscribers` every 3s until `status: "finished"`. Check `GET /api/import/subscribers/logs` if status is `"failed"`.
   - **Subscriber count vs list count:** `GET /api/lists/{id}` returns `subscriber_count` that may include cross-list memberships. To verify actual subscribers on a specific list, use `GET /api/subscribers?list_id={id}&per_page=200` and count the results.
4. **Subscribers added via API** with `preconfirm_subscriptions: true` skip double opt-in — only do this for contacts who already consented.
5. SMTP must be configured in the admin UI (Settings → SMTP) before anything sends. If sends fail, check that first, then `GET /api/logs`. ListMonk's SMTP selection is global, not campaign-specific; keep the intended provider enabled alone and preserve the real password when PUTting the full settings object because masked password fields cannot be written back.
6. Content: campaigns accept `content_type` of `richtext`, `html`, `markdown`, or `plain`. Use `{{ .Subscriber.FirstName }}`-style Go template tags for personalization; `{{ UnsubscribeURL }}` is auto-appended by the default template.
7. Test endpoint payloads must use integer list IDs, not the GET response's list objects. Build the test payload from the campaign record, transform `lists: [{"id": 8, ...}]` to `lists: [8]`, include complete campaign fields, `subscribers`, and the explicit messenger when required. A `{"data":true}` response without a corresponding `/api/logs` SMTP line is inconclusive, not proof of delivery.
8. Campaign `to_send` is the original audience snapshot and `sent` is application-level state. After `finished`, reconcile with provider records before assuming the difference is bounced or retrying the campaign.
7. **Draft-body verification is mandatory.** A successful UI/API update is not proof that the HTML was stored. After creating or updating a draft, immediately `GET /api/campaigns/{id}` and verify `status == draft`, `content_type == html`, and `len(body)` is close to the source HTML length. Never report a populated draft when the record still contains an empty body or a test placeholder.
 8. **Template placeholders must be ListMonk syntax before saving.** Generic tokens such as `{{MEDIUM_URL}}` are parsed as Go-template functions and can cause `Error compiling campaign body`. Resolve confirmed URLs first, or leave a non-template marker such as `[MEDIUM_URL_PENDING]` for visual drafts. Convert generic ESP tokens to ListMonk tags: `{{VIEW_ONLINE_LINK}}` → `{{ MessageURL }}` and `{{UNSUBSCRIBE_LINK}}` → `{{ UnsubscribeURL }}`.
 9. **Campaign test-send verification.** Fetch the campaign first and normalize returned `lists` objects to integer IDs before POSTing. Include the complete campaign payload plus `subscribers` and an explicit configured messenger such as `email-bird`; a response of `{"data":true}` is only API acceptance. Verify `/api/logs` for transport evidence. If no transport log appears, treat the result as inconclusive and do not resume bulk sending from it. See `references/test-send-and-remote-smtp.md`.
9. **Complete-document campaigns need a blank template.** Use a campaign template whose entire body is `{{ template "content" . }}` when the uploaded body already contains its own doctype, html, head, body, and layout. Verify `template_id` after the campaign write. Persist Reply-To through the campaign `headers` field, for example `[{"key":"Reply-To","value":"xander@usingaitoscale.com"}]`, and GET the campaign to confirm it remains stored.

### Large HTML draft workflow

For a visual-only draft, do not send or test-send. Use the browser-authenticated API session when dedicated API credentials are unavailable. Load the HTML into the same browser page/session, update `PUT /api/campaigns/{id}` with `content_type: "html"`, then verify with `GET /api/campaigns/{id}`. Do not rely on a contenteditable editor event for a 20–30KB body: it may visually accept the content while persisting only a short placeholder. If the browser session cannot retain the body, stop with the campaign still in Draft and report the exact stored body length.

See `references/large-html-draft-debugging.md` for the reproducible failure modes and verification recipe.
7. When importing newsletter HTML, validate every `{{...}}` token against ListMonk's supported template tags before saving. Generic placeholders such as `{{MEDIUM_URL}}` are parsed as Go-template functions and cause a 400 compile error. Use `{{ MessageURL }}` and `{{ UnsubscribeURL }}` for the corresponding generic view/unsubscribe fields, then fetch the saved campaign to verify the body is non-empty and still `draft`.

For the detailed draft-update procedure and failure transcripts, see `references/listmonk-draft-body-update.md` in the newsletter-pipeline skill.
7. **CRITICAL — double-send prevention on test sends.** The `/api/campaigns/{id}/test` endpoint queues messages asynchronously and returns `{"data":true}` even if the SMTP send later fails. If SMTP credentials are invalid, messages stay queued and get retried on the next server restart or retry cycle. If you then send another test, both the retried batch AND the new batch deliver = duplicates. Safeguards:
   - **Pre-send SMTP health check:** Always `GET /api/logs` and scan for `error` entries before sending. If errors exist, fix SMTP first.
   - **Never retry a failed test send without verifying the queue is clear.** If a test send fails with SMTP errors, the messages are queued. Fixing SMTP settings triggers a server restart, which flushes the queue (delivering the original batch). Only after confirming the original batch delivered (via the sending provider's API — e.g. Resend: `GET https://api.resend.com/emails?limit=10` or Bird: `GET https://us1.platform.bird.com/v1/email/messages?limit=100`) should you send a new test.
   - **Verify delivery count after every test send.** Use the provider's API to confirm exactly N emails went out (one per recipient). If count > N, investigate before proceeding.
   - **For real campaign sends:** `max_msg_retries` (currently 2) controls retry behavior. Real campaign sends are tracked per-subscriber in ListMonk's database with deduplication — the double-send risk is specific to the test endpoint, which doesn't track per-subscriber delivery state.
8. **SMTP credential persistence:** Settings updated via `PUT /api/settings` are stored in ListMonk's PostgreSQL database and persist across restarts. The `config.toml` only provides initial settings on first boot. Do NOT edit config.toml to change SMTP — always use the API. If a provider's API key rotates, update via `PUT /api/settings` (read current settings first, modify only the password field, write back the full settings object). **⚠️ Password masking:** ListMonk masks all SMTP passwords as bullet characters (`•••••`) on API output. You cannot read the current password back. When modifying SMTP settings, you MUST explicitly set the password field to the real key.
7. **CRITICAL — double-send prevention on test sends.** The `/api/campaigns/{id}/test` endpoint queues messages asynchronously and returns `{"data":true}` even if the SMTP send later fails. If SMTP credentials are invalid, messages stay queued and get retried on the next server restart or retry cycle. If you then send another test, both the retried batch AND the new batch deliver = duplicates. Safeguards:
   - **Pre-send SMTP health check:** Always `GET /api/logs` and scan for `error` entries before sending. If errors exist, fix SMTP first.
   - **Never retry a failed test send without verifying the queue is clear.** If a test send fails with SMTP errors, the messages are queued. Fixing SMTP settings triggers a server restart, which flushes the queue (delivering the original batch). Only after confirming the original batch delivered (via Resend API: `GET https://api.resend.com/emails?limit=10`) should you send a new test.
   - **Verify delivery count after every test send.** Use the Resend API to confirm exactly N emails went out (one per recipient). If the count exceeds N, investigate before proceeding.
   - **For real campaign sends:** `max_msg_retries` (currently 2) controls retry behavior. If a campaign send fails, ListMonk retries up to 2 times. This is safe for real sends (one campaign, one queue, tracked per-subscriber). The double-send risk is specific to the test endpoint, which doesn't track per-subscriber delivery state.
8. **SMTP credential persistence:** Settings updated via `PUT /api/settings` are stored in ListMonk's PostgreSQL database and persist across restarts. The `config.toml` only provides initial settings on first boot. Do NOT edit config.toml to change SMTP — always use the API. If Resend API key rotates, update via `PUT /api/settings` (read current settings first, modify only the password field, write back the full settings object).

## Creating and verifying a draft

For a draft-only newsletter request, create the campaign with `status: draft`, the correct list, subject, From display name, tags, and `content_type: html`, then verify the API record. A campaign can appear in the UI as Draft with correct metadata while the API reports `body: ""`; the definitive check is `GET /api/campaigns/{id}`, not the visible editor. Do not report completion until `status` is `draft`, `content_type` is `html`, `body` is non-empty and matches the intended HTML length or hash, and `sent` is `0`.

The ListMonk CodeMirror/contenteditable editor may fail to persist large HTML when driven through browser automation. If that occurs, use an authenticated API `POST /api/campaigns` or `PUT /api/campaigns/{id}` from the logged-in browser session. For large bodies, use a two-step placeholder-create then full-body update, or base64/chunked injection. Re-read the campaign API response after saving. A successful metadata save is not proof that the body upload succeeded.

## Common recipes

**"Create a visual HTML draft without sending":** health → identify or create the target draft → read the actual HTML artifact from disk → convert unsupported generic placeholders before upload (`{{VIEW_ONLINE_LINK}}` → `{{ MessageURL }}`, `{{UNSUBSCRIBE_LINK}}` → `{{ UnsubscribeURL }}`; never pass literal `{{MEDIUM_URL}}`) → update/create with `content_type: html` and the complete body → do not test, schedule, or start → GET the campaign record and verify `status: draft`, `sent: 0`, and a non-empty body whose length/hash matches the uploaded artifact. A successful UI response is not proof of persistence. If the body is still `<p>test</p>`, empty, or stale, report failure and retry with a file-backed/base64/browser transport rather than claiming completion.

**"Send this newsletter to my list":** health → `lists` (find target list id + subscriber count) → write HTML body to a temp file → `create-campaign` → `test-campaign` to the user's own email → report recipient count and wait for user's go-ahead → `start-campaign` → poll `GET /api/campaigns/{id}` until `status: finished`, report sent count.

**"Send a standalone HTML newsletter from a zip":** unzip → upload all images via `POST /api/media` → replace `src="images/..."` with hosted URLs in HTML → convert merge field placeholders to ListMonk Go template syntax → create raw passthrough template (if not already exists) → `create-campaign` with from_email, template_id, reply_to headers → `test-campaign` to test addresses → check `logs` for errors → report results. Do NOT `start-campaign` unless explicitly authorized.

**"Add these people to the list":** health → `lists` → `add-sub` per contact (or CSV import for many) → confirm final count via `subs <list_id>`.

**"How did the last campaign do?":** `campaigns` → read `views`, `clicks`, `sent`, `bounces` from the response; `GET /api/campaigns/analytics/*` endpoints for detail.

## Pitfalls

1. **Test endpoint needs full campaign fields.** The `POST /api/campaigns/{id}/test` endpoint requires `messenger`, `from_email`, `template_id`, and `headers` in the payload — not just `name`/`subject`/`body`. The `test-campaign` function in lm.sh copies all these fields from the campaign object. If you build the payload manually, include them or you'll get "Unknown messenger" (400).
2. **Default templates double-wrap HTML.** Templates like "Newsletter Passthrough" (ID 6) wrap content in their own `<html>`/`<head>`/`<body>` shell. For standalone HTML newsletters, create and use a raw passthrough template instead.
3. **Settings PUT restarts the server.** After `PUT /api/settings`, the ListMonk server restarts. Wait ~5 seconds and re-check `health` before retrying any sends.
4. **Settings PUT replaces, not merges.** Send the complete settings object back — not just the field you changed. Fetch first, modify, then PUT the whole thing.
5. **Reply-To is a header, not a field.** There is no `reply_to` field on campaigns. Use `"headers": [{"key": "Reply-To", "value": "email@example.com"}]`.
6. **Stale HTML comments.** Newsletter HTML may contain build-info comments like `<!-- Images NOT generated yet -->` that are outdated after images are added. These don't affect rendering but can mislead you during inspection — verify with actual `src=` attribute checks.
