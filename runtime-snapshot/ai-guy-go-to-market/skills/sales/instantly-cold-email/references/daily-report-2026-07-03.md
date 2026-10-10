# Daily Report — Friday, July 3, 2026

## PR Agencies - SpeakerAgent v2 (#3577260) — ACTIVE

**4,512 leads | 96% INPROGRESS (page 0 sample)**

| Metric | Count |
|---|---|
| Today's inbox replies | 20 |
| OOO/holiday auto-replies | 17 |
| Unsubscribes | 2 |
| Hostile | 1 |
| **Positives** | **0** |

**Detail:**
- 🚨 **OutsidePR** (contact@outsidepr.com): *"You either need to work on your own writing skills or delete whatever AI agent you're using for this slop"* — hostile. New signal: "slop" as hostile indicator added to classifier.
- 📤 **Jess** (jess@outintheboons.me): "Unsubscribe"
- 📤 **TLC Marketing** (info@tlcmarketingconsultants.com): "Not interested but thanks; please unsubscribe me" — Tammy Fruits, CEO
- 📅 17 OOO — mostly July 4th holiday closures. Expected seasonal pattern.

**Cumulative (Jul 1-3):** 41 total replies, 1 positive_soft (Ben @ venturepr.co — still unhandled), 3 hostile, 6 unsub, 31 OOO/auto.

**⚠️ Ben @ venturepr.co positive_soft from Jul 1 still unhandled** — daemon has no CAMPAIGN_CONTEXT for #3577260. Needs SpeakerAgent hardcoded reply template.

## AI Guy — Organic Outreach (#3520103) — COMPLETED

No new inbox replies. ⚠️ Missing from daemon CAMPAIGN_CONTEXT (was ACTIVE since Jun 22 uncovered).

## ai-operator-10hr-niche (#3287518) — STOPPED

1,948 leads. No sends. No replies. Status unchanged since May 14 stop.

## TX HVAC (#3442703) — COMPLETED

⚠️ **2 unhandled positive replies, now 4 days stale:**
- Alpha Mechanical (jeff@alphamechanical.us): "Ok. Send me to information including cost please." — Jun 29
- Source Rentals → Nichole (jason@1sourcerentals.com): "Jason is no longer at the company" — Jun 29 referral

## Classifier Updates (July 3, 2026)

Three edge cases discovered and fixed in `scripts/classify.py`:

1. **"slop" → hostile**: OutsidePR used "slop" to insult AI-generated email. Added to hostile_patterns.
2. **Holiday closure patterns**: "closed in observance", "office is closed", "will be closed on", "we will reopen on", "auto-generated reply", "i am currently out" → OOO.
3. **Form auto-responder gaps**: "ticket has been created", "your email has been received", "due to a high volume of emails", "thank you for reaching out" → form_auto_patterns.