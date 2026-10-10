# Email-Thread-Confirmed Bookings

Some calls are confirmed entirely via email thread — the lead says "booked it" or "on the books for [day]" and the operator confirms, but no Cal.com entry exists on Justin's account. These are real calls that the pre-call report cron will miss if it only checks Cal.com sources.

**Also see:** `cross-cal-account-bookings.md` — some bookings ARE on Cal.com, but on a different account (e.g., `cal.com/speakeragent`). Those have a real Cal.com entry but won't appear in Justin's API.

## Detection Pattern

Scan Instantly message history for positive leads on active campaigns (#3639259, #3577260, #3617053, and any new campaign with SpeakerAgent or owned-audiences reply threads). Look for these patterns in REPLY messages:

```python
BOOKING_PATTERNS = [
    r'\bon the books\b',
    r'\bbooked\b.*\b(Tuesday|Wednesday|Thursday|Friday|Monday|weekend|tomorrow|next)\b',
    r'\btalk\b.*\b(Tuesday|Wednesday|Thursday|Friday|Monday)\b',
    r'\b(see you|see ya)\b.*\b(Tuesday|Wednesday|Thursday|Friday|Monday)\b',
    r'\blooking forward to it\b',
    r'\bconfirm(?:ed|ing)?\b.*\b(Tuesday|Wednesday|Thursday|Friday|Monday)\b',
    r'\bgrabbed a time on your calendar\b',   # cross-account Cal.com booking
]
```

Then check for a SENT reply from our side within 24h that confirms ("Talk Tuesday!", "Looking forward to it", "See you then"). If both exist AND the date reference points to a future day AND no Cal.com entry exists on Justin's account → generate the report.

## Case Study: Peter Vera (Jul 20, 2026)

**Campaign:** #3639259 (Podcasters - SpeakerAgent v2)
**Lead:** Peter Vera, peter@bizexitgrow.com, lead_id=4175232890
**Business:** BizExitGrow — exit planning for logistics companies

**Thread:**
- [REPLY] Jul 16: "Open to receiving guests! Any business owner with an exit, or anyone with an M&A background would be a fit."
- [SENT] Jul 16: SpeakerAgent reply from Branson
- [REPLY] Jul 18: "Got something on the books for Tuesday. Looking forward to it!"
- [SENT] Jul 19: "Awesome — looking forward to it, Peter. Talk Tuesday!"

**Gap:** Zero Cal.com records for peter@bizexitgrow.com. Not in cal_bookings.json. Not in Cal.com API.
**Call:** Tuesday Jul 21 — time and meeting link unknown.
**Report:** Created at `clients/bizexitgrow/pre-call-report.md` with Section 7 flag.

## Case Study: Jeffrey Bradbury (Jul 22, 2026) — Cross-Cal.com-Account Variant

**Campaign:** #3639259 (Podcasters - SpeakerAgent v2)
**Lead:** Jeffrey Bradbury, info@teachercast.net
**Business:** TeacherCast Educational Network
**Pattern:** Booked on `cal.com/speakeragent/15min` (Zayden's calendar), not `cal.com/usingaitoscale`
**Full details:** See `cross-cal-account-bookings.md`

## Workflow Integration

In the combined cron (Part A monitoring + Part B pre-call reports):

1. After the inbox monitoring sweep (Part A), pull message history for all positive leads on campaigns with SpeakerAgent or owned-audiences reply threads
2. Filter for REPLY messages matching the booking patterns above
3. Cross-reference against cal_bookings.json and Cal.com API — if no match, the booking is email-thread-only OR cross-account
4. Generate pre-call report with call time/meeting link flagged as "UNKNOWN — check Justin's primary calendar" or "UNKNOWN — check SpeakerAgent Cal.com"
5. Save to `clients/{slug}/pre-call-report.md`