# Partner Category Campaigns — July 2026

Four cold email campaigns targeting professional service providers as partnership channels. Each uses 2-lane frameworks: Lane A (direct — we build their referral engine) and Lane B (partner — we execute for their clients, reciprocal referrals, rev share).

## Active Campaigns

| ID | Name | Niche | Leads | Inboxes | Sends/Day | Framework |
|----|------|-------|-------|---------|-----------|-----------|
| 3698110 | Partner: Fractional CFOs & Accountants v1 | CFOs, CPAs, bookkeepers | 1,244 | 23 | ~276-345 | [CFO framework](/opt/data/cache/documents/doc_fe74d61ca72b_Cold Email Frameworks — Fractional CFOs & Accountants (Partner Category) v1.md) |
| 3698111 | Partner: Business Coaches & EOS v1 | EOS implementers, business coaches | 1,212 | 23 | ~276-345 | [Coaches framework](/opt/data/cache/documents/doc_be05a7ddcced_Cold Email Frameworks — Business Coaches & EOS Consultants (Partner Category) v1.md) |
| 3698112 | Partner: Fractional CMOs & Marketing v1 | Fractional CMOs, marketing consultants | 4,929 | 32 | ~384-480 | [CMO framework](/opt/data/cache/documents/doc_561263d22aea_Cold Email Frameworks — Fractional CMOs & Marketing Consultants (Partner Category) v1.md) |
| 3698114 | Partner: CRM & ESP Consultants v1 | HubSpot, GoHighLevel, Keap, ActiveCampaign consultants | 442 | 20 | ~240-300 | [CRM framework](/opt/data/cache/documents/doc_4f77075fec06_Cold Email Frameworks — CRM & ESP Consultants (Partner Category) v1.md) |

## Campaign Settings

All use:
- Plain text (`send_as_plain_text: true`)
- Track settings: `DONT_TRACK_EMAIL_OPEN`, `DONT_TRACK_LINK_CLICK`
- Follow-up: 100%
- Stop on: `REPLY_TO_AN_EMAIL`
- Schedule: Mon-Fri 8AM-5PM EST, 9 min between emails
- AI ESP matching: enabled
- No ScraperCity verification needed (Instantly Prospector fetches verified emails)

## Sequences (4-email each)

1. **Email 1 (Day 0):** Primary framework angle — opens with agreement, names their reality, offers the mechanism
2. **Email 2 (Day 3):** Lane pivot — switches offer direction, calendar link goes here
3. **Email 3 (Day 7):** Short check-in — one question, no pitch
4. **Email 4 (Day 14):** Breakup — game plan session offer restated, no pressure

## Formatting (MANDATORY)

See `references/email-formatting-rules.md` for the exact rules. Key: short lines, blank lines between every thought, lowercase throughout, no blocks of text.

## Daemon Context

All four campaigns are registered in `/opt/data/scripts/auto_reply_daemon.py` under `CAMPAIGN_CONTEXT` with lane-aware reply templates. When leads reply:
- Identify which campaign they're in
- Match the reply tone to the original email's lane
- Lane A replies: acknowledge interest in referral engine, offer case study + calendar
- Lane B replies: acknowledge interest in partnership, explain the split, offer calendar
- No pricing, no white label unless framework explicitly permits it
