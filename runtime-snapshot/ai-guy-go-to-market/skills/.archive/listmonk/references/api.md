# Listmonk REST API reference (condensed)

Full docs: https://listmonk.app/docs/apis/apis/

**Auth:** every request needs `Authorization: token <username>:<password_or_api_token>`.
Create API users in the admin UI: **Admin → Users → + New → type: API** (token shown once).
All responses are `{"data": ...}`. Errors return `{"message": "..."}` with a 4xx/5xx status.

## Health / misc
- `GET /api/health` — liveness check
- `GET /api/config` — server config summary
- `GET /api/logs` — recent server log lines (debug SMTP failures here). Returns a JSON array of log strings.
- `GET /api/settings` · `PUT /api/settings` — full settings object (SMTP lives here). **PUT replaces the entire settings object** — fetch first, modify, PUT the whole thing. Server **restarts** after PUT; wait ~5s and re-check health.

## Lists
- `GET /api/lists?page=1&per_page=100` — all lists (`minimal=true` for a light version)
- `GET /api/lists/{id}`
- `POST /api/lists` — `{"name":"...", "type":"public|private", "optin":"single|double", "tags":[...]}`
- `PUT /api/lists/{id}` · `DELETE /api/lists/{id}`

## Subscribers
- `GET /api/subscribers?page=1&per_page=100&list_id=1` — supports `query=` with SQL, e.g.
  `query=subscribers.email LIKE '%@gmail.com'`
- `GET /api/subscribers/{id}`
- `POST /api/subscribers` —
  `{"email":"...", "name":"...", "status":"enabled", "lists":[1], "attribs":{...}, "preconfirm_subscriptions":true}`
  (`attribs` = arbitrary JSON, usable in templates; 409 = already exists)
- `PUT /api/subscribers/{id}` — same body shape
- `PUT /api/subscribers/lists` — bulk: `{"ids":[1,2],"action":"add|remove|unsubscribe","target_list_ids":[3],"status":"confirmed"}`
- `DELETE /api/subscribers/{id}` · `POST /api/subscribers/query/delete` — `{"query":"..."}`
- `POST /api/subscribers/{id}/optin` — resend opt-in confirmation

## Import (bulk CSV)
- `POST /api/import/subscribers` — multipart form:
  - `params` (JSON string): `{"mode":"subscribe","subscription_status":"confirmed","delim":",","lists":[1],"overwrite":true}`
  - `file`: CSV with header `email,name,attributes` (attributes = optional JSON string)
- `GET /api/import/subscribers` — import status; `GET /api/import/subscribers/logs`

## Campaigns
- `GET /api/campaigns?page=1&per_page=100&order=desc&order_by=created_at`
- `GET /api/campaigns/{id}` — includes `sent`, `views`, `clicks`, `bounces`, `status`, `messenger`, `headers`
- `POST /api/campaigns` —
  ```json
  {"name":"...", "subject":"...", "lists":[1], "type":"regular",
   "content_type":"richtext|html|markdown|plain", "body":"<h1>...</h1>",
   "altbody":"plain text fallback", "from_email":"Name <a@b.com>",
   "template_id":1, "messenger":"email", "tags":[...],
   "headers":[{"key":"Reply-To","value":"reply@example.com"}],
   "send_at":"2026-08-01T09:00:00Z"}
  ```
  Key fields:
  - `messenger` must be `"email"` — omitting it causes "Unknown messenger" on test sends.
  - `headers` is an array of `{"key":"...","value":"..."}` objects — use it for Reply-To (there is no `reply_to` field).
  - `from_email` format is `"Display Name <email@domain>"`.
  - `template_id` selects the wrapping template. Use a raw passthrough template for standalone HTML.
- `PUT /api/campaigns/{id}` — update (only while draft/scheduled/paused). Must include `lists` or you'll get "Invalid list IDs." (400). Send the full campaign object, not just changed fields.
- `PUT /api/campaigns/{id}/status` — `{"status":"scheduled|running|paused|cancelled"}` — `running` starts real sending
- `POST /api/campaigns/{id}/test` — body = campaign fields + `"subscribers":["a@b.com"]`
  - **⚠️ ASYNC + NO DEDUP:** Returns `{"data":true}` immediately on accepting the request, NOT on SMTP delivery. If SMTP fails, messages stay queued and retry on next server cycle/restart. If you send another test, both batches deliver = duplicates. NEVER retry without verifying via the sending provider's API that the first batch didn't deliver.
  - Must include `"messenger":"email"` in the test payload (missing = `{"message":"Unknown messenger ."}` 400 error).
  - Required fields: `name`, `subject`, `lists` (int array), `type`, `content_type`, `body`, `from_email`, `template_id`, `headers`, `messenger`, `subscribers`.
- `DELETE /api/campaigns/{id}`
- Analytics: `GET /api/campaigns/analytics/{views|clicks|bounces|links}?id={id}&from=...&to=...`

## Templates
- `GET /api/templates` · `GET /api/templates/{id}/preview`
- `POST /api/templates` — `{"name":"...","type":"campaign|tx","body":"... {{ template \"content\" . }} ..."}`
- `PUT /api/templates/{id}/default` — set default

**Raw passthrough template** (for standalone HTML newsletters that have their own `<html>`/`<body>`):
```json
{"name":"Raw Passthrough","type":"campaign","body":"{{ template \"content\" . }}\n{{ TrackView }}"}
```
This outputs the campaign body verbatim with no HTML wrapper, plus the open-tracking pixel.

## Transactional email
- `POST /api/tx` —
  `{"template_id":2, "subscriber_email":"a@b.com", "data":{"any":"json"}, "content_type":"html"}`
  (template must be type `tx`; access data as `{{ .Tx.Data.any }}`)

## Media
- `POST /api/media` — multipart `file=@path` upload; returns JSON with `url` and `filename` fields for use in campaign bodies.
  Example response: `{"data":{"id":42,"filename":"banner_2AoDz1.jpg","url":"https://instance.up.railway.app/uploads/banner_2AoDz1.jpg"}}`
  Upload all images from a newsletter zip, then replace `src="images/..."` with the returned URLs.

## Settings (SMTP)
- `GET /api/settings` — returns full settings object including `smtp` array.
  Each SMTP block has: `name`, `uuid`, `enabled`, `host`, `port`, `auth_protocol`, `username`, `password` (masked in response), `tls_type`, `max_conns`, etc.
- `PUT /api/settings` — replace entire settings object. Update the `password` field in the relevant SMTP block to fix stale credentials (e.g. Resend API key). **Server restarts after PUT.**

## Template tags (in campaign/template bodies)
- `{{ .Subscriber.Email }}`, `{{ .Subscriber.Name }}`, `{{ .Subscriber.FirstName }}`, `{{ .Subscriber.Attribs.city }}`
- `{{ UnsubscribeURL }}`, `{{ TrackLink "https://..." }}`, `{{ MessageURL }}` (view in browser)
- `{{ TrackView }}` — open-tracking pixel (include in raw passthrough templates)
- `{{ template "content" . }}` — renders the campaign body inside a template

## Merge field conversion (from other ESPs)
| Placeholder | ListMonk equivalent |
|---|---|
| `{{VIEW_ONLINE_LINK}}` | `{{ MessageURL }}` |
| `{{UNSUBSCRIBE_LINK}}` | `{{ UnsubscribeURL }}` |
