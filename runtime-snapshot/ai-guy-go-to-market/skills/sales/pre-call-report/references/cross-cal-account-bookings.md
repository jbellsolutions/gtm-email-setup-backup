# Cross-Cal.com-Account Bookings

Some leads book on Cal.com accounts OTHER than Justin's `usingaitoscale`. The most common: **SpeakerAgent's `cal.com/speakeragent/15min`** — used by podcaster campaign (#3639259) personas (Zayden, Branson, Orin, Camila). These bookings will NOT appear in Justin's Cal.com API or `cal_bookings.json`.

## Detection

When scanning Instantly message history for SpeakerAgent campaigns, the SENT reply often contains the booking link:

> "Here's a link to book in: https://cal.com/speakeragent/15min"

When a lead later replies "I just grabbed a time on your calendar. Looking forward to the chat!" — the booking exists on `cal.com/speakeragent`, not `cal.com/usingaitoscale`.

## Case Study: Jeffrey Bradbury (Jul 22, 2026)

**Campaign:** #3639259 (Podcasters - SpeakerAgent v2)
**Lead:** Jeffrey Bradbury, info@teachercast.net
**Business:** TeacherCast Educational Network — K12 EdTech podcast network
**Persona:** Zayden (zayden@dalkus.info)

**Thread:**
- [SENT] Jul 15: Cold email from Zayden — SpeakerAgent intro
- [REPLY] Jul 20: "Can you share links to my show so I can check for accuracy?"
- [SENT] Jul 20: SpeakerAgent beta pitch from Zayden, with `cal.com/speakeragent/15min` link
- [REPLY] Jul 22: "I just grabbed a time on your calendar. Looking forward to the chat!"

**Gap:** Zero Cal.com records for info@teachercast.net on Justin's account. Not in `cal_bookings.json`. Not in live Cal.com API.
**Call:** Date/time unknown — booked on SpeakerAgent's Cal.com account.
**Report:** Created at `clients/teachercast/pre-call-report.md` with Section 7 flag.

## Detection Pattern

```python
SPEAKERAGENT_CAL_PATTERNS = [
    r'cal\.com/speakeragent',
    r'speakeragent.*calend',
    r'book in.*speakeragent',
    r'grabbed a time on your calendar',
]
```

When a REPLY matches any of these AND the lead's email doesn't appear in Justin's Cal.com API → cross-account booking. Generate report with call logistics flagged as unknown.

## Known Cross-Account Calendars

| Account | Cal.com Slug | Used By | Campaigns |
|---|---|---|---|
| SpeakerAgent | `speakeragent` | Zayden, Branson, Orin, Camila | #3639259, #3316611 |
| Justin (primary) | `usingaitoscale` | Justin | All direct bookings |

If additional accounts are discovered, add them to this table.