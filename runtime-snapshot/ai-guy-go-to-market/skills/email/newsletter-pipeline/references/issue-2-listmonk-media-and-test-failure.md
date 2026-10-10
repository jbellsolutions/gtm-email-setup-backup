# Issue 002 ListMonk media and test-send record

## Working media path

The browser upload path was unreliable, but the dedicated ListMonk API user worked:

```bash
BASE='https://listmonk-production-2930.up.railway.app'
AUTH='apiuser:<dedicated-api-token>'
curl -u "$AUTH" -F 'file=@images/logo.png' "$BASE/api/media"
```

`POST /api/media` returned filesystem-backed public URLs under `/uploads/`. Verify each URL without authentication before placing it in HTML. For Issue 002, four uploads returned HTTP 200 with the expected image content types and sizes. Replace every `images/*.jpg` or `images/*.png` reference with its returned HTTPS URL, then verify the persisted campaign body has zero relative image paths.

## Campaign persistence

Use a file-backed JSON payload for large HTML. For Issue 002, campaign 22 was created as:

- name: `The Dealmaker - Issue 002`
- subject: `The best salesperson only gets paid when you do`
- list: `Test-Xander` (list 6)
- content type: `html`
- from: `The Dealmaker <justin@send.usingaitoscale.com>`
- status after creation: `draft`
- sent: `0`

The GET-after-write body length and SHA-256 matched the transformed local HTML exactly. The old placeholders were absent and `{{ MessageURL }}` plus `{{ UnsubscribeURL }}` each appeared twice.

## Test endpoint requirements

The test endpoint is `POST /api/campaigns/{id}/test`. A minimal body containing only `subscribers` produced:

```json
{"message":"Invalid length for name."}
```

Sending the complete campaign payload plus `subscribers`, but omitting `messenger`, produced:

```json
{"message":"Unknown messenger ."}
```

Including the configured messenger name (`messenger: "email-resend"`) returned `{"data":true}`. That response means the request was accepted, not necessarily delivered.

## Delivery verification

Immediately GET the campaign and inspect `/api/logs`. The Issue 002 test remained `status: draft`, `sent: 0`, and all counters at zero. Logs showed both intended recipients failed with:

```text
535 Authentication credentials invalid
```

Therefore the test was not delivered. Never report delivery from `{"data":true}` alone. Confirm transport-level success in ListMonk logs or provider-level message status, then confirm the Reply-To and unsubscribe links in the received messages.

## Reply-To caveat

The campaign API accepted a payload containing `reply_to: "xander@usingaitoscale.com"`, but the subsequent GET returned `reply_to: null`. Treat Reply-To as unverified and block the test until the supported ListMonk field/schema or UI setting is identified.

## Reusable gates

1. Health check with the dedicated API credentials.
2. Upload media via `/api/media`; verify URLs anonymously.
3. Transform merge fields before campaign creation.
4. Create/update with file-backed JSON.
5. GET and compare body hash, status, content type, list, and sent count.
6. Confirm persisted Reply-To, not just request payload.
7. Test with full payload and explicit messenger.
8. Inspect campaign state and server logs for transport delivery before claiming success.
