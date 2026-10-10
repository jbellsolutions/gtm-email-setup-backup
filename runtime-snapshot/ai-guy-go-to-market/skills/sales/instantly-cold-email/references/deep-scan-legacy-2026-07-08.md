# Deep Scan Audit — July 8, 2026

**Context:** Full inbox sweep across all pages (0-159). Previously only pages 0-139 had been processed (154 message IDs in state). This audit discovered pages 140-159 had 15 unprocessed replies from STOPPED legacy campaigns.

**Total inbox size:** 160 entries across 8 pages (pages 0-7, 20 per page).
**State file before:** 154 message IDs.
**State file after:** 169 message IDs (+15).

## New Replies Found (Page 140-159)

All from STOPPED campaigns dating back to May-June 2026.

| # | Name | Email | Campaign | Date | Classification | Reply |
|---|---|---|---|---|---|---|
| 145 | Dave | office@davemastroair.com | #3441343 (FL HVAC v1) | Jun 3 | negative_notfit | "No thank you. Please remove us from your list." |
| 146 | American | onlinecustomerservice@midamerican.com | #3441343 | Jun 2 | ooo | Ticket system auto-reply |
| 147 | Joshua | joshua@lalongevity.com | #3287518 (med-spa) | May 7 | unsubscribe | "Unsubscribe" |
| 148 | Jim | jim@jimslist.com | #3337105 (SpeakerAgent) | May 28 | **positive_interested** | "Please send more info and cost. Send to Jim@Cargo2Casa.org..." |
| 149 | Nona | nona@mitchrich.com | #3337105 | May 20 | negative_notfit | "I am not interested in receiving inquiries..." |
| 150 | Ryan | ryan@mugsypr.com | #3337105 | May 15 | negative_notfit | "No thanks, we're good." |
| 151 | Warner | warner@5borough.us | #3337105 | May 15 | hostile | "Stop" |
| 152 | Lauren | lauren@d1a.com | #3316611 (SpeakerAgent v1) | May 15 | dead | "Lauren Gordon is no longer with Day One Agency → rob@d1a.com" |
| 153 | Miranda | miranda@cc-pr.co | #3337105 | May 15 | dead | "I am no longer with CC-PR → courtney@cc-pr.co" |
| 154 | Rob | rob@tonyfaypr.com | #3337105 | May 15 | negative_notfit | "no thank you" |
| 155 | Alexis | alexis@change-llc.com | #3337105 | May 15 | ooo | "I'm out of the office...return Monday May 18" |
| 156 | Michael | michael@opinionmovers.com | #3337105 | May 15 | hostile | "You should look up the legal requirements for unsolicited commercial email..." |
| 157 | Michelle | michelle@lernercommunications.com | #3337105 | May 15 | ooo | "I am at a work event and may be slow to respond" |
| 158 | Sally | sally@thebuzzagency.net | #3337105 | May 15 | ooo | "I'll be out of the office today" |
| 159 | Caitlin | caitlin@fcpcommunications.com | #3337105 | May 15 | ooo | "I am currently out of the office" |

## Classification Summary

| Classification | Count |
|---|---|
| positive_interested | 1 (Jim — 41 days stale) |
| negative_notfit | 4 |
| ooo | 5 |
| hostile | 2 |
| dead | 2 |
| unsubscribe | 1 |

## Key Takeaway

The daemon's 1-minute `--once` cron only catches the most recent inbox page. STOPPED campaigns' replies accumulate on deep pages (100+) where they're never found by routine monitoring. A periodic full-sweep audit — paginating until empty, not stopping at 5-6 pages — is required to catch these. The inbox can easily reach 160+ entries when multiple campaigns (active + legacy) are included.

## Jim's Reply (Positive — 41 Days Stale)

**Campaign:** #3337105 (SpeakerAgent PR — STOPPED, May 2026)
**Original pitch:** SpeakerAgent finds podcast/speaking opportunities automatically. An AI agent researches hosts, drafts pitches, delivers 3 leads/week.
**His reply:** "Please send more info and cost. Send to Jim@Cargo2Casa.org. This is my company that does a lot of speaking. Jim Forde APPROVED REAL ESTATE ACADEMY Phone: 714-875-0979 Email: Jim@ApprovedRealEstateAcademy.com"

**Draft response (generated July 8, not sent — operator's call given 41-day delay):**
> Hey Jim —
>
> Appreciate you getting back to me — sorry for the delay on our end.
>
> SpeakerAgent finds and vets podcast and speaking opportunities for thought leaders. An AI agent researches hosts, drafts personalized pitches, and delivers ready-to-send leads weekly — no hands-on supervision needed.
>
> Happy to walk you through how it works for Cargo2Casa. 15 minutes and you'll see if it's a fit.
>
> When's a good time?
