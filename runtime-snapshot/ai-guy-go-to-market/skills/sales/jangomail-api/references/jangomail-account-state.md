# JangoMail Account State (2606407)

Last verified: Jul 27, 2026

## Account

| Item | Value |
|---|---|
| Username | `UsingAIToScale` |
| User ID | 2606407 |
| Plan | 5,000 emails/month |
| Sending domain | `scaleverticalwithai.com` (authorized) |
| Default From | `email@scaleverticalwithai.com` |
| Default From Name | `Scale Vertical AI` |
| Tracking domain | `track.scaleverticalwithai.com` |
| Image CDN | `https://img.jangomail.com/2606407/Images/` |
| SMTP relay | `express-relay.jangosmtp.net` (ports 25, 2525, 465, 587) |

## DNS Records (live)

| Type | Record | Value |
|---|---|---|
| SPF (TXT) | `scaleverticalwithai.com` | `v=spf1 include:_spf.mail.hostinger.com include:jangomail.com ~all` |
| DKIM (CNAME) | `jm._domainkey.scaleverticalwithai.com` | → `jm._domainkey.jmsend.com` |
| DMARC (TXT) | `_dmarc.scaleverticalwithai.com` | `v=DMARC1; p=none; rua=mailto:dmarc@scaleverticalwithai.com` |
| MX | `scaleverticalwithai.com` | Hostinger (`mx1.hostinger.com`, `mx2.hostinger.com`) |

**Only JangoMail is authenticated.** No Bird, AutoSend, or Resend SPF/DKIM records exist.

## Sending Lists (as of Jul 27)

| Group Name | Group ID | Members | Notes |
|---|---|---|---|
| pr-agencies-MONDAY-250 | 1005541711 | 250 | Sent Jul 27 (Green Room) |
| menshealth-coaching-MONDAY-250 | 1005542436 | 250 | Sent Jul 27 (Protocol) |
| recruiting-VERIFIED-224 | 1005961051 | 224 | Ready for People Person send |
| pr-agencies-batch-01 | 1004607476 | 100 | Jul 23 batch |
| menshealth-clinic-batch-01 | 1004607621 | 100 | Jul 23 batch |
| recruiting-batch-01 | 1004607331 | 100 | Jul 23 batch (paused) |
| test-list-temp | 1004607766 | 0 | Empty test list |

## Campaigns (full history as of Jul 29)

### Newsletter → Campaign Mapping

| Newsletter | Emoji | Audience |
|---|---|---|
| Green Room | 🎙️ | PR agencies |
| The Protocol | 🧬 | Men's health clinics / coaching |
| People Person | 🎯 | Recruiting firms |
| Men's Health | (none) | Men's health clinics |

### All Sent Campaigns

| Campaign ID | Newsletter | Subject | Date (ET) | Recipients | Opens | Clicks | Bounces | Blocks | Unsubs | Complaints | v2 Click Track? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 399343647 | Protocol | 🧬 FDA Panel Weighs Seven Peptides Thursday | Jul 23 | 95 | 18 | 0 | 22 | 3 | 0 | 0 | ❌ (v1) |
| 399344421 | Green Room | 🎙️ The Long Tail Belongs On Your Media List | Jul 23 | 100 | 32 | 0 | 0 | 0 | 2 | 0 | ❌ (v1) |
| 399400061 | Green Room | 🎙️ The Long Tail Belongs On Your Media List | Jul 27 | 250 | 57 | 0 | 0 | 0 | 4 | 1 | ❌ (v1) |
| 399400311 | Protocol | 🧬 FDA Panel Weighed Seven Peptides Last Week | Jul 27 | 250 | 24 | 0 | 0 | 0 | 0 | 0 | ❌ (v1) |
| 399405595 | People Person | 🎯 AI Firms Grow Four Times Faster | Jul 27 | 220 | 48 | 0 | 0 | 0 | 0 | 0 | ❌ (v1) |
| 399406882 | Men's Health | Testosterone lost its heart warning | Jul 27 | 497 | 50 | 0 | 1 | 4 | 3 | 0 | ❌ (v1) |
| 399419858 | Green Room | 🎙️ The Long Tail Belongs On Your Media List | Jul 28 | 1,493 | 242 | 0 | 1 | 3 | 3 | 0 | ❌ (v1) |
| 399419863 | Men's Health | Testosterone lost its heart warning | Jul 28 | 1,498 | 90 | 0 | 1 | 1 | 2 | 0 | ❌ (v1) |
| 399443331 | Green Room | 🎙️ The Long Tail Belongs On Your Media List | Jul 29 | 558 | 133 | 58 | 0 | 0 | 2 | 0 | ✅ (v2) |
| 399444272 | Green Room | 🎙️ The Long Tail Belongs On Your Media List (overflow) | Jul 29 | 9 | 2 | 1 | 0 | 0 | 0 | 0 | ✅ (v2) |

**Test sends excluded:** 399419771, 399419805, 399419843, 399419856 (Jul 28, 1 recipient each), 399443140 (Jul 29, 1 recipient)
**Draft campaigns excluded:** 399343166, 399343167, 399343168 (Jul 23), 399420947 (Jul 28) — never sent (recipients=0)

### Grand Totals (sent campaigns only)

| Metric | Count |
|---|---|
| Total Sent | 4,975 |
| Total Delivered | 4,939 |
| Total Opens | 700 (14.1%) |
| Total Clicks | 60 (1.2%) |
| Total Bounces | 25 |
| Total Blocks | 11 |
| Total Unsubs | 16 |
| Total Complaints | 1 |

**Rule: All future newsletter sends via v2 API with `click_track_html: true`.** v1 `SendMassEmail` does NOT track editorial link clicks — deprecated for newsletters as of Jul 29, 2026.

## Usage

| Metric | Value |
|---|---|
| Emails sent (Jul 29) | ~4,975 of 5,000 monthly cap |
| Remaining | ~25 |
| Bandwidth used | ~40MB / 500MB |

⚠️ **Monthly cap nearly exhausted.** Next billing cycle resets the 5,000 email limit.