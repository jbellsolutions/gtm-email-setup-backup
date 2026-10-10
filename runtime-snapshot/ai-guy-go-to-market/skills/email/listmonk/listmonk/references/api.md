# Listmonk REST API reference (condensed)

Full docs: https://listmonk.app/docs/apis/apis/

**Auth:** every request needs `Authorization: token <username>:<password_or_api_token>`.
Create API users in the admin UI: **Admin → Users → + New → type: API** (token shown once).
All responses are `{"data": ...}`. Errors return `{"message": "..."}` with a 4xx/5xx status.

## Health / misc
- `GET /api/health` — liveness check
- `GET /api/config` — server config summary
- `GET /api/logs` — recent server log lines (debug SMTP failures here)
- `GET /api/settings` · `PUT /api/settings` — full settings object (SMTP lives here; careful, PUT replaces)

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
- `GET /api/campaigns/{id}` — includes `sent`, `views`, `clicks`, `bounces`, `status`
- `POST /api/campaigns` —
  ```json
  {"name":"...", "subject":"...", "lists":[1], "type":"regular",
   "content_type":"richtext|html|markdown|plain", "body":"<h1>...</h1>",
   "altbody":"plain text fallback", "from_email":"Name <a@b.com>",
   "template_id":1, "tags":[...], "send_at":"2026-08-01T09:00:00Z"}
  ```
- `PUT /api/campaigns/{id}` — update (only while draft/scheduled/paused)
- `PUT /api/campaigns/{id}/status` — `{"status":"scheduled|running|paused|cancelled"}` — `running` starts real sending
- `POST /api/campaigns/{id}/test` — body = campaign fields + `"subscribers":["a@b.com"]`
- `DELETE /api/campaigns/{id}`
- Analytics: `GET /api/campaigns/analytics/{views|clicks|bounces|links}?id={id}&from=...&to=...`

## Templates
- `GET /api/templates` · `GET /api/templates/{id}/preview`
- `POST /api/templates` — `{"name":"...","type":"campaign|tx","body":"... {{ template \"content\" . }} ..."}`
- `PUT /api/templates/{id}/default` — set default

## Transactional email
- `POST /api/tx` —
  `{"template_id":2, "subscriber_email":"a@b.com", "data":{"any":"json"}, "content_type":"html"}`
  (template must be type `tx`; access data as `{{ .Tx.Data.any }}`)

## Media
- `POST /api/media` — multipart `file=` upload; returns URL for use in campaign bodies

## Template tags (in campaign/template bodies)
- `{{ .Subscriber.Email }}`, `{{ .Subscriber.Name }}`, `{{ .Subscriber.FirstName }}`, `{{ .Subscriber.Attribs.city }}`
- `{{ UnsubscribeURL }}`, `{{ TrackLink "https://..." }}`, `{{ MessageURL }}` (view in browser)
