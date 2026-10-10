# JangoMail Click Tracking Investigation (Jul 28, 2026)

Full investigation log: why click tracking showed 0/168 across 4 campaigns, what methods were tested, and which one actually works.

## The Problem

July 27 newsletter sends (4 campaigns, 1,217 recipients, 168 opens) showed 0 clicks across all campaigns. Investigation needed to determine: is this a tracking gap or are recipients genuinely not clicking?

## Root Cause

The July 27 campaigns were sent via v1 `SendMassEmail` WITHOUT `TrackClicks` in the Options string. All editorial links went out as raw URLs. JangoMail has no way to track clicks on raw URLs — they bypass the tracking domain entirely.

## Methods Tested (Jul 28, 2026)

### Method 1: v1 SendMassEmail + TrackClicks in Options

**Test:** Sent campaign with `Options='TrackOpens,TrackClicks'` and raw editorial links.

**Result:** ❌ FAILED — 0 clicks tracked
- Stored HTML shows raw links (no auto-wrapping visible)
- v1 `SendMassEmail` does NOT wrap editorial links at delivery time
- Opens ARE tracked (via tracking pixel), clicks are NOT

**JobIDs tested:** 399419771 (ToOther), 399420947 (group send)

### Method 2: Manual /c.z link wrapping

**Test:** Manually rewrote all editorial hrefs to: `https://track.scaleverticalwithai.com/c.z?***uniqueid****&u=URLENCODED_DESTINATION`

**Result:** ❌ FAILED — 0 clicks tracked, links broken for recipients
- `/c.z` is NOT a valid JangoMail click tracking endpoint
- With literal `***uniqueid****`: returns HTTP 500 immediately (0.09s)
- With valid `j=HASH&m=HASH` hashes (from `GetViewAsWebPageURL`): hangs for 10+ seconds, returns HTTP 000
- `***uniqueid****` is ONLY replaced for system links (`/u.z`, `/w.z`) — NOT for custom `/c.z` URLs
- Links appear to redirect (because `u=` param contains destination) but the redirect is unreliable and clicks are NOT registered
- `/u.z` returns HTTP 200, `/w.z` returns HTTP 200 — these are valid endpoints
- `/c.z` returns HTTP 500 — this is NOT a valid endpoint

**JobIDs tested:** 399419843, 399419856 (ToOther tests), 399419858, 399419863 (production sends — 188+81 opens, 0 clicks)

**Impact:** 33 editorial links across 2 production sends (3,000 recipients) are dead. Recipients who click editorial links get a 500 error page. System links (unsubscribe, view-online) still work because `/u.z` and `/w.z` are valid endpoints.

### Method 3: v2 POST /campaigns with tracking.click_track_html=True ✅ WORKING

**Test:** Created campaign via v2 REST API with:
```python
'tracking': {
    'click_track_html': True,
    'track_opens': True
}
```
Sent via `PUT /campaigns/{id}/send`.

**Result:** ✅ SUCCESS — 2 clicks tracked from xander@usingaitoscale.com
- Click records include: email, IP address, user agent, timestamp, link position, html (bool)
- Stored HTML shows raw links (wrapping happens at SMTP delivery time, not in template)
- v2's pre-processor wraps each href per-recipient at send time using hash-based tracking URLs (similar to `j=HASH&m=HASH` format used by `/w.z`)
- Recipients receive emails with wrapped links that redirect correctly and register clicks

**JobID tested:** 399419805 (ToOther=xander, 1 recipient, 1 open, 2 clicks)

## v1 vs v2 API Comparison

| Capability | v1 SendMassEmail | v2 POST /campaigns |
|---|---|---|
| Open tracking | ✅ (tracking pixel) | ✅ (tracking pixel) |
| Click tracking | ❌ (does not wrap links) | ✅ (wraps at delivery time) |
| Link wrapping method | N/A | Per-recipient hash-based URLs at SMTP level |
| Stored HTML shows | Raw links | Raw links (wrapping is delivery-time only) |
| Auth | Form fields (Username, Password) | Basic Auth |
| List/group sending | `ToGroups='group-name'` | `to_lists: [{'id': list_id}]` |
| Single recipient | Use `SendTransactionalEmail` instead | `to_other: [{'email': '...'}]` |

## JangoMail Reporting API Limitations Discovered

- `Reports_GetReplies_String` (v1): Returns empty for all campaigns — JangoMail does NOT track inbound replies. Replies land in the reply-to inbox, invisible to JangoMail reporting.
- `Reports_GetAllClicks_String` (v1): Requires `SortBy` parameter, but all intuitive values (Date, URL, EmailAddress, etc.) return `InvalidOptionException`. Valid values are undocumented.
- `Reports_GetClicksByURL_String` (v1): Also requires `SortBy`, also fails with all tested values.
- `Reports_GetComplaintsByCampaign_String` (v1): Same `SortBy` issue.
- v2 `GET /campaigns/{id}/stats/clicks`: Returns clean JSON array of click records — use this instead of v1.
- v2 `GET /campaigns/{id}/stats/opens`: Returns clean JSON array of open records with email, IP, user agent, timestamp.

## Key Takeaway

**Use v2 API exclusively for all JangoMail campaign sends.** v1 does not support click tracking on editorial links. The v2 `tracking.click_track_html: True` setting is the only way to enable click tracking. Never manually wrap links through `/c.z` — that endpoint does not exist and will break all editorial links for recipients.
