# Instantly-to-GoHighLevel Import Notes

## Durable findings

- The user explicitly corrected the source platform: use Instantly.ai, not the retired legacy email platform.
- Instantly REST authentication succeeded against `GET /api/v2/campaigns` during the session.
- A stored sweep artifact showed 34 replies overall and 2 solar replies in its seven-day window; a separate solar inventory showed 32 reply/positive threads. These are historical snapshots, not a substitute for a fresh pull.
- Solar campaign IDs observed in the environment include `dbd68956-2dc6-47e4-a56e-5a518db39381` and additional solar-related campaigns must be re-discovered from the live campaign list before import.
- The Instantly reply payload can contain `from_address_email`, `timestamp_email`, `subject`, `campaign_id`, `thread_id`, and `body.text`/`body.html`. A reply body may include quoted original messages and signatures.
- Phone numbers can appear in reply signatures. One stored example included a labeled cell phone in the signature. Signature extraction must be separate from quoted-message stripping and must preserve the raw evidence.
- The URL supplied by the user identifies GoHighLevel location `cXlt94iCckJNp2OyUmwU` and one contact `nL86YDQDAFH9LOsKJD51`; it is not itself a bulk import route.
- The supplied private integration token must not be printed or persisted in logs. Because it was posted in a shared Slack conversation, rotation should be recommended after use.

## Blocker classification

A direct API request to GoHighLevel's services endpoint returned HTTP 403 with Cloudflare Error 1010 / `browser_signature_banned` from the execution environment. This is an edge-security block, not sufficient evidence that the private token is invalid. Stop writes, retain the exact response class, and retry only through an approved/API-accessible route.

## Reproduction-safe extraction pattern

1. Authenticate to Instantly.
2. List campaigns and identify all solar campaigns by exact ID/name.
3. Fetch `/api/v2/emails` with a page limit and `next_starting_after` cursor.
4. Back off on HTTP 429 and preserve already-fetched pages.
5. Keep inbound types (including observed `ue_type` 2 and 3), then normalize message bodies and extract phone signatures.
6. Deduplicate on normalized email plus thread/message ID.
7. Generate a dry-run preview before contacting GoHighLevel.

Do not use the historical JSON snapshots as proof of the current reply count.
