# Click Tracking Investigation — Jul 28, 2026

## Problem

0 clicks across 168 opens on 4 JangoMail newsletter campaigns sent Jul 27, 2026.
Total 1,217 recipients, 4 campaigns (Green Room, Protocol batch 1, People Person, Protocol coaching).

## Investigation

### Step 1: Inspect stored HTML for link wrapping

Pulled `GET /campaigns/{id}/stats/content` (v2) and `GetCampaignDetails_XML` (v1) for all 4 campaigns.

**Finding:** All editorial links (source citations, Medium articles, case study PDFs, `speakeragent.ai`) were raw URLs — NOT wrapped through `track.scaleverticalwithai.com`. Only 4 system links per campaign were tracked:
- 2x unsubscribe: `track.scaleverticalwithai.com/u.z?***uniqueid****`
- 2x view-online: `track.scaleverticalwithai.com/w.z?***uniqueid****`
- 0 click-tracking links: zero `/c.z` URLs

### Step 2: Test if TrackClicks auto-wraps links

Sent test emails with both methods:

**v1 SendMassEmail with `Options='TrackOpens,TrackClicks'`:**
- Sent test to `xander@usingaitoscale.com` (JobID 399419771)
- Pulled stored content via `GET /campaigns/{id}/stats/content`
- Result: 21 links total, 4 tracked (system), 0 `/c.z`, 17 still raw

**v2 POST /campaigns with `tracking.click_track_html: True`:**
- Created and sent test campaign (ID 399419805)
- Pulled stored content
- Result: 21 links total, 4 tracked (system), 0 `/c.z`, 17 still raw

**Conclusion:** JangoMail's `TrackClicks` option does NOT cause automatic link wrapping in either v1 or v2. The stored HTML always shows raw editorial links regardless of tracking options.

### Step 3: Test manual link wrapping

Manually wrapped all editorial `href` attributes through the tracking domain using:
```
https://track.scaleverticalwithai.com/c.z?***uniqueid****&u=URLENCODED_DESTINATION
```

Sent test via v1 `SendMassEmail` with `Options='TrackOpens,TrackClicks'` (JobID 399419843).

**Result:** Stored content preserved the wrapping — 17/17 editorial links wrapped through `/c.z`, 0 raw. The `***uniqueid****` placeholder was preserved in stored HTML (replaced per-recipient at send time).

### Step 4: Verify v2 API surface for reply tracking

Checked swagger spec (90+ paths) — zero reply-related endpoints exist. The v1 method `Reports_GetReplies_String` accepts `JobID` but returns empty for all 4 campaigns. JangoMail does not natively track inbound replies — they land in the reply-to inbox.

### Step 5: Check v1 reporting API for click data

Tried `Reports_GetClicksByURL_String`, `Reports_GetAllClicks_String`, `Reports_GetAllClicks_XML` — all either "method not valid" or require undocumented `SortBy` values. v2 `GET /campaigns/{id}/stats/clicks` returns `[]` (empty array) confirming 0 tracked clicks.

## Solution

**Manual link wrapping before sending.** Use `wrap_editorial_links()` function (in SKILL.md "Mandatory: Click Tracking" section) to wrap all editorial URLs through `track.scaleverticalwithai.com/c.z?***uniqueid****&u=ENCODED_URL`. Also pass `Options='TrackOpens,TrackClicks'` as belt-and-suspenders.

## Campaigns tested

| Campaign | JobID | Date | Recipients | Opens | Clicks (before fix) |
|---|---|---|---|---|---|
| Green Room | 399400061 | Jul 27 12:47 UTC | 250 | 57 | 0 |
| Protocol batch 1 | 399400311 | Jul 27 12:55 UTC | 250 | 23 | 0 |
| People Person | 399405595 | Jul 27 18:28 UTC | 220 | 48 | 0 |
| Protocol coaching | 399406882 | Jul 27 23:59 UTC | 497 | 40 | 0 |
| **Total** | | | 1,217 | 168 | 0 |

## First sends with manual wrapping (Jul 28, 2026)

| Campaign | JobID | Recipients | Sent | Delivered |
|---|---|---|---|---|
| Green Room (PR) | 399419858 | 1,500 | 1,493 | 1,492 |
| Protocol (Coaching) | 399419863 | 1,500 | 1,498 | 1,498 |
