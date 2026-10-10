# Instantly Reply Export Reference

## Verified session pattern

The all-time export used the active Instantly v2 API with a complete cursor sweep:

- `GET https://api.instantly.ai/api/v2/campaigns`
- Select campaigns by explicit IDs after reviewing names.
- `GET https://api.instantly.ai/api/v2/emails?limit=100`
- Continue with `starting_after={next_starting_after}` until the cursor ends.
- Filter locally by selected `campaign_id` values.
- Retain inbound records where `ue_type` is `2` or `3`.
- Deduplicate by `id` or `message_id`.

The successful sweep fetched 19,482 email records over 196 pages and yielded 331 inbound replies across four selected campaign IDs. The focused solar subset had 268 replies; the JV-owned-audience subset had 63. These figures are historical session output, not a standing expectation for future runs.

## Export fields

The verified CSV preserved reply ID, timestamp, campaign ID/name, thread ID, from/to addresses, subject, lead ID, extracted name, phone numbers, reply text, reply HTML, and raw JSON. CSV was written UTF-8 with BOM so spreadsheet and CRM import tools recognize it reliably.

## Phone extraction

Scan the complete plain-text body, including signature content and quoted text when the goal is preservation. Keep extracted numbers in a separate field. Do not replace the original body or assume a phone is current.

## Rate-limit behavior

Instantly returned HTTP 429 during an earlier broad sweep. A complete export must retry with backoff and record unresolved errors. A partial page count must never be reported as an all-time result.

## GHL validation

The Revenue Partners location ID used in the session was `cXlt94iCckJNp2OyUmwU`. A read-only request to `GET https://services.leadconnectorhq.com/locations/{location_id}` using a private integration token returned HTTP 200 and confirmed the location. This proves location authentication/access only; contact creation still requires schema and write authorization checks.

Never place private integration tokens in CSVs, logs, or assistant replies. Rotate tokens exposed in chat.
