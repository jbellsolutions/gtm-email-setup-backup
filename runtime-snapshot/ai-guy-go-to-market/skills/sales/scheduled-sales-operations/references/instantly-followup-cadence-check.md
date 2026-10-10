# Instantly follow-up cadence check

For unattended Instantly cadence runs, use Instantly's native campaign state, not the legacy Instantly follow-up engine.

## Verified live observations

- `GET /campaigns` returned three campaigns: one active solar campaign, one stopped AI SDR campaign with no leads, and one paused custom-variable test campaign.
- The active campaign had `status: 1`, a 15-step sequence, `stop_on_reply: true`, and delays of one day for the first step followed by two-day intervals.
- `POST /leads/list` accepts a campaign filter and cursor pagination via `starting_after`; it returned 3,361 leads for the active solar campaign during the check.
- `GET /emails?i_status=1` returned both sent and inbound records. Filter inbound messages by `ue_type == 2`; sent records use `ue_type == 1`.
- `GET /emails?campaign_id=<id>&limit=100` returned a broader page that required client-side filtering by `campaign_id`. Do not assume server-side filters are exact.
- A same-day inbound record can be unread and still be non-actionable. The verified example contained only a CEO signature and phone numbers, with no request or buying signal.
- Latest live cadence run (2026-08-07): `POST /leads/list` cursor pagination returned 3,363 records across the account: 3,361 in the active solar campaign and two in the paused custom-variable test. No `pause_until` dates were past due. Two unread inbound messages were observed in one solar thread: a positive "Yes, please" and a separate unsubscribe; both were correctly held by reply/stop conditions. Thirteen replied solar leads still showed active status without a visible `pause_until`, so they were held for stop-state review rather than queued.

## Safe decision procedure

1. Enumerate all campaigns and record status, native sequence delays, and `stop_on_reply`.
2. Paginate campaign leads conservatively. Use native last-step/status timestamps for due calculations.
3. Pull inbound records and normalize body text. Strip signatures and quoted content before classification.
4. Treat every inbound reply, including unclear/signature-only replies, as a stop condition when `stop_on_reply` is enabled. Hold for review instead of scheduling a duplicate follow-up.
5. Exclude replies, bounces, unsubscribes, and explicit stops before drafting anything.
6. If the campaign is newer than the manual threshold or its native sequence owns the next touch, report zero manual follow-ups due.
7. Never invoke `/emails/reply` from an unattended cadence check. Drafts may be queued for the configured approval gate only.

## Rate-limit and pagination handling

Instantly enforces a 20-requests-per-minute limit on these reads. A 429 is not an empty result: stop expanding the scan, preserve the successful snapshot, wait for the window to clear, and retry only the failed page. Avoid restarting the entire pagination pass. When a filter returns a broad result set, filter locally rather than issuing many per-thread requests.

## Platform boundary

Do not run `/opt/data/scripts/followup_engine.py` or read/write `/tmp/speakeragent_followups.json` and `/tmp/owned_audiences_followups.json` for Instantly. Those artifacts use Instantly campaign IDs and Instantly reply semantics. Instantly follow-up checks must remain REST-only and must not query Instantly.
