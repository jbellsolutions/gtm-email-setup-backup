# Best Practices (from 24M cold emails — Jay Feldman, 2026)

These are the 8 tactics that still work at scale. Source: 24M emails sent, 53K calls booked, 3-5% avg reply rate (vs 1% industry avg).

## The Mastery Triangle
Cold email lives on three pillars. Missing any one caps you at 1%:
1. **Deliverability** — inbox placement >80%. DNS, warmup, plain text, no fingerprints.
2. **List** — right humans, right time, right offer. Decision makers only.
3. **Copy** — get open → get read → get reply. Short, human, non-salesy.

Audit all three before changing a word of copy.

## Tactic 1: Email Decision Makers Only ✅ WE DO THIS
CEOs, founders, CMOs, owners, presidents. Skip managers, coordinators, specialists.
- Mid-level: forward-to-boss (dies) or delete (no authority) → wasted send + spam risk
- Founder: reply or spam. That's it. **Doubles reply rates.**
- PipelineLabs filter: `seniorityIncludes: ["owner", "c_suite", "partner"]`

## Tactic 2: Lead Qualification Step ⚠️ NOT IMPLEMENTED
Run every lead through a qualification step BEFORE importing to Instantly. Without it: 1-2% reply. With it: 4-6%.
- B2B databases give basic matches — not actual fit. Expect to lose ~50% of list.
- The 20% you remove are the ones that would ghost or spam-report you.
- Use Clay AI, N8N, or custom Python. We should implement a lightweight Python qualifier.
- **Minimum check:** verify email deliverability, check company has website, exclude generic emails (info@, contact@, etc.)

## Tactic 3: Spam Folder Mining 🔮 FUTURE
Find people sending you cold email that landed in spam → tell them why → offer help. 20-30% reply rate.
- Scales to however many cold emails you receive.
- Pitch: "Hey, your cold email landed in my spam. Here's why. Want help?"
- Low volume but highest conversion play in existence.

## Tactic 4: Reverse Lead Magnet 🔮 FUTURE
Do work FIRST before asking. "Would it be okay if I spent an hour generating this for you?"
- Instead of "download my PDF" → "I built this custom audit for you"
- Perceived value much higher because they think it's unique
- 3-5% reply rate, top campaigns 7%+ on cold lists
- Our offer is already close to this — "we do the audit" — but could make it more explicit as first touch

## Tactic 5: Trojan Horse Framing ⚠️ COULD APPLY
Frame outreach as non-sale. Must be genuine — not bait and switch.
- Journalist interview, partnership exploration, research project, case study feature
- 10-20% reply rates when frame is real
- Our current emails are direct pitch. Could test: "researching how SMBs handle AI" as alternate framing

## Tactic 6: Diversify Sending Infrastructure 📋 JUSTIN'S CALL
- Under 50 mailboxes → all Google (current best)
- 500+ mailboxes → split Google / Microsoft / private SMTP
- Google update Nov 2025: overnight placement dropped 80→50%. Diversification protects against this.
- Private SMTP: fastest/cheapest to scale, quality depends on provider

## Tactic 7: Triple Tap Copy ✅ WE DO THIS
Three jobs of every cold email:
1. **Get open** — subject + preview text, 3-5 words, sound human, never salesy. "your AI person" = ✓
2. **Get read** — short body (4 sentences): why you → poke pain → social proof → ask. ✓
3. **Get reply** — CTA answerable with one thumb. "Yes." "Sure." "Worth learning how it works?" ✓

## Tactic 8: No Fingerprints ✅ WE DO THIS
- No links in email 1-3 ✓
- No open tracking ✓ (`DONT_TRACK_EMAIL_OPEN`)
- No link tracking ✓ (`DONT_TRACK_LINK_CLICK`)
- Plain text only ✓
- No promotional trigger words (guarantee, 100%, sale, free) ⚠️ audit our copy
- **Spintax** ❌ NOT YET — sending identical copy to 1000+ leads leaves a fingerprint. ESPs track this with AI. Need to implement spintax variation.

## Two Tactics to Kill (We Already Avoid These)

1. **Volume over quality** — bad list amplifies failure. We filter by decision makers but skip qualification step. Fix: add qualification before upload.
2. **Links + tracking in emails** — Calendly links, open pixels, link trackers. All gone from our stack. ✓

## Current Compliance Score

| Tactic | Status | Priority |
|---|---|---|
| Decision makers only | ✅ | — |
| Lead qualification | ✅ Implemented | `qualify_leads.py` before every upload |
| Spintax variation | 🚨 P0 CRITICAL | `resolve_spintax()` MUST run at generation time. Spintax is NOT supported by Instantly — `{Hey\|Hi\|Hello}` sends as literal text. Confirmed June 2: Florida HVAC sent ~850 emails with raw Spintax, zero replies expected. Fix: resolve to single variant per block per lead BEFORE upload. Never let raw `{option1\|option2}` reach Instantly. |
| Triple tap copy | ✅ | — |
| No fingerprints (links/tracking) | ✅ | — |
| Plain text | ✅ | — |
| Short subject (3-5 words) | ✅ | — |
| Simple CTA (one-thumb reply) | ✅ | — |
| Email verification | ✅ ScraperCity | **P0** — verify every email via ScraperCity `email-validate` ($0.0036/email) before upload. PipelineLabs "verified" is NOT reliable. |
| Spam word check | ❌ Not done | **P1** — run copy through checker |
| Diversified infra | 📋 Justin | — |
| Trojan horse framing | 🔮 Test later | — |
| Reverse lead magnet | 🔮 Test later | — |
| Spam folder mining | 🔮 Test later | — |

## Immediate Actions
1. 🚨 **P0 — Fix Spintax** — `resolve_spintax()` must run in `hvac_personalize.py` before upload. Confirmed production incident June 2: ~850 Florida HVAC emails sent with raw `{Hey|Hi|Hello}`. See `references/florida-spintax-incident-2026-06-02.md`.
2. ✅ **Lead qualification script** — built (`scripts/qualify_leads.py`), tested (98% pass rate on PipelineLabs output), integrated into upload workflow.
3. 🚨 **Source fresh Florida emails** — all 1,097 from #3441343 are burned. Instantly silently drops duplicate emails across campaigns.