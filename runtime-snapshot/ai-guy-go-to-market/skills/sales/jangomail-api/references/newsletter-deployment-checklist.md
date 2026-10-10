# Newsletter Deployment Checklist

End-to-end flow for deploying HTML newsletters to JangoMail with mail-tester QA,
lead list import, staggered sends, and delivery analysis.

## Phase 1 — Asset Prep

1. **Unzip the newsletter archive** — watch for Windows backslash paths (SKILL.md has fix script)
2. **Verify image hashes** against existing hosted URLs — reuse if identical (saves re-upload)
3. **Read index.html** — extract subject line from masthead (first headline with emoji)
4. **Fix preheader** — use `max-height:0px;overflow:hidden;` NOT `font-size:1px` (costs 2.5 spam points)

## Phase 2 — HTML Rewrite

1. **Swap image paths** `src="images/sN.jpg"` → hosted URLs (`https://img.jangomail.com/2606407/Images/prefix-sN.jpg`)
   - ⚠️ **Use unique filenames per upload** — append version + timestamp (e.g., `pp-v3-1785175890-s0.jpg`). Never reuse filenames across versions — the CDN serves stale cached images from the old upload.
   - Upload via curl, not urllib (urllib silently returns empty response on JangoMail's POST /files). See SKILL.md "Image CDN Cache-Busting" section.
   - If "File already exists" (400), use a different filename — do NOT try to delete and re-upload to the same name.
2. **Replace `{{UNSUBSCRIBE_LINK}}`** → `https://track.scaleverticalwithai.com/u.z?***uniqueid****`
3. **Replace `{{VIEW_ONLINE_LINK}}`** → `https://track.scaleverticalwithai.com/w.z?***uniqueid****`
4. **Wrap editorial links for click tracking** — JangoMail does NOT auto-wrap raw URLs even with TrackClicks enabled. Manually wrap every editorial `href` through the tracking domain using `wrap_editorial_links()` (see SKILL.md "Mandatory: Click Tracking" section). Format: `https://track.scaleverticalwithai.com/c.z?***uniqueid****&u=URLENCODED_URL`. After wrapping, verify zero raw editorial links remain (only `w3.org`, `img.jangomail.com`, and `track.scaleverticalwithai.com` URLs should be unwrapped).
5. **Fix byline date** — newsletter packages arrive with stale draft dates. Replace with actual send date. Sweep entire HTML for tense issues ("meets" → "met", "this week" → "last week", "Thursday" → "last Thursday").
6. **Verify:** zero `src="images/` references, zero `{{...}}` placeholders, zero old dates, correct `***uniqueid****` count (4 for system links + N for editorial links), zero raw editorial hrefs

## Phase 3 — Campaign Creation

1. **Create draft** via v2 `POST /campaigns` with `create_only: True`
2. **Subject:** use Unicode emoji (not Slack `:shortcode:`), exactly as specified
3. **From:** `email@scaleverticalwithai.com` with newsletter-specific name
4. **Encoding:** `character_set: 'UTF-8'`, `encoding: 'Quoted Printable'`

## Phase 4 — Mail-Tester QA + Pre-Send Link Gate

### 4A. Mail-Tester QA

1. **Get address** from mail-tester.com (fresh one per campaign)
2. **Send test** — use v2 `POST /campaigns` with `to_other` containing the mail-tester address, `tracking.click_track_html: True`, `create_only: False` (sends immediately)
3. **Check score** at `mail-tester.com/test-{id}`
4. **Verify headers:** Both `List-Unsubscribe` AND `List-Unsubscribe-Post: One-Click` present
5. **Verify auth:** SPF=pass, DKIM=pass, DMARC=pass
6. **Score target:** 10/10 before proceeding. A 9/10 with only "broken links" deductions from bot-protected sites (Medium, news sites returning 403 to crawlers) is effectively a 10/10 — those links work for real readers.
7. **Encoding check:** Pull `GET /campaigns/{id}/stats/content` and verify: 0 replacement chars (`\ufffd`), 0 mojibake (`Ã` patterns), emoji chars present, em-dashes intact, charset=UTF-8 declared. If garbled, the HTML source or encoding pipeline has a problem — do not proceed.

### 4B. Pre-Send Link Gate (MANDATORY — no campaign goes out without passing)

This gate exists because "links are wrapped" is NOT the same as "links work." On July 28, 2026, manually-wrapped `/c.z` links appeared wrapped in stored HTML but returned HTTP 500 for every recipient — 33 dead editorial links across two production sends. This gate would have caught that.

**Step 1 — Send test to real inbox:**
Send the campaign to `xander@usingaitoscale.com` via v2 API (same payload as the production send, just `to_other` instead of `to_lists`).

**Step 2 — Load an editorial link end-to-end:**
After receiving the test email, open it and click ANY editorial link (not just the unsubscribe/view-online system links). The link must:
- Resolve to the actual destination page (e.g., clicking a Medium article link lands on the Medium article, NOT an error page or blank screen)
- Load within 5 seconds (not hang)
- Return HTTP 200 at the destination

**Step 3 — Verify click registered in JangoMail reporting:**
After clicking, wait 30 seconds and check:
```
GET https://api-v2.jangomail.com/campaigns/{test_campaign_id}/stats/clicks
Authorization: Basic base64("UsingAIToScale:Jango123!")
```
The response must contain at least 1 click record with the recipient's email address, IP, timestamp, and link position. If `clicks: 0` after a confirmed click, click tracking is broken — do not proceed to production send.

**Step 4 — Verify encoding on test send:**
Pull `GET /campaigns/{test_campaign_id}/stats/content` and confirm: 0 replacement chars, 0 mojibake, emoji/em-dash/special chars intact. This catches encoding issues from any HTML processing.

**Gate result:**
- ✅ Link resolves to destination AND click registers AND encoding clean → proceed to production send
- ❌ Link 500s/hangs/redirects to wrong page OR click not tracked OR encoding garbled → STOP. Fix before sending.

**Spam folder diagnosis:** If the email scores 9-10/10 on mail-tester but still lands in spam for specific recipients, the cause is domain reputation age (new sending domain, low volume history), not content or auth. This improves with continued sends and recipient engagement. DMARC `p=none` also contributes — tighten to `p=quarantine` after building reputation.

## Phase 5 — List Import

1. **CSV must have** `EmailAddress` column (not `Email`) for v1 import
2. **Create group** via `AddGroup` (v1) or `POST /lists` (v2, lowercase `name`)
3. **Import members** via `ImportGroupMembersFromData` (v1, async — re-check count)
4. **Verify count** — exactly the expected number. If zero, wait 15s and re-check.

## Phase 6 — Send

1. **Use v2 API for all sends** — `POST /campaigns` with `tracking.click_track_html: True` + `PUT /campaigns/{id}/send`. v1 SendMassEmail does NOT support click tracking on editorial links (tested Jul 28 2026 — v1 TrackClicks option does not wrap links at delivery time).
2. **Use RAW editorial links** in the HTML — do NOT manually wrap through `/c.z` (that endpoint does not exist). v2's SMTP pre-processor wraps links automatically when `click_track_html: True` is set.
3. **Required v2 fields:** `from` (object), `subject`, `message_html`, `message_plain`, `to_lists` (array of `{'id': list_id}`) or `to_other`, `tracking: {click_track_html: True, track_opens: True}`, `character_set: 'UTF-8'`, `encoding: 'Quoted Printable'`
4. **For test sends to 1 recipient:** use v2 with `to_other: [{'email': '...'}]` and `create_only: False` (sends immediately)
5. **Stagger:** 8-10 minutes between v2 campaign sends when sending multiple newsletters. JangoMail queues sequentially.
6. **v2 send returns 400 but works:** `PUT /campaigns/{id}/send` may return HTTP 400 — check `GET /campaigns/{id}` for `status: "Sending"` before assuming failure.
7. **Verify:** campaign status → `Complete` (v1 `GetMassEmailStatus`). Note: v2 stats may show `recipients: 0` for up to 30s after send — wait and re-check.
8. **Account usage:** After sending, check `GET /account/usage` (v2) for remaining email quota against plan cap.
9. **Click tracking verification:** After recipients click links, check `GET /campaigns/{id}/stats/clicks` — click records will show email, IP, timestamp, link position. Stored HTML (`/stats/content`) will show RAW links — this is normal (wrapping happens at SMTP delivery level).

## Phase 7 — Delivery Analysis

1. **Check stats:** `GET /campaigns/{id}/stats`
2. **Breakdown:** recipients → minus bounces → minus blocks = delivered
3. **Investigate removed:** `removed_addresses` for pre-send suppression (exclude permanently)
4. **Investigate bounces:** hard bounces → remove from future lists; soft bounces → can retry
5. **Investigate blocks:** SMTP-level blocks → may be spam filters, wrong MX records
6. **Late unsubscribes/complaints:** check again 2-4 days post-send. These often appear days after the send.

## Phase 8 — +2hr Stats Report

After sending, schedule a one-time cron job to pull stats at +2 hours and deliver to the originating Slack thread:

```
Schedule: once at <send_time + 2 hours> in America/New_York
Deliver: origin (the Slack thread that requested the send)
Prompt: Pull stats for campaign {id} via JangoMail v2 API GET /campaigns/{id}/stats. Report: recipients, bounces, blocks, delivered, opens, clicks, unsubscribes, complaints. Open rate as % of delivered.
```

For multiple campaigns sent in the same session, use ONE combined cron job that pulls stats for all campaigns and reports them side-by-side. Cancel any previously scheduled single-campaign cron jobs first.

## Standing Rules

- **Only send to Instantly `lead_status=COMPLETED`** — never STARTED or INPROGRESS
- **Permanently suppressed:** list maintained in agent memory
- **Mail-tester before every campaign:** 10/10 or fix before sending
- **No automated sends:** All newsletter sends require explicit user confirmation. Never schedule a send without the user saying "send it" or equivalent.
- **Stagger multiple sends:** 8-10 minutes between SendMassEmail calls in the same session
