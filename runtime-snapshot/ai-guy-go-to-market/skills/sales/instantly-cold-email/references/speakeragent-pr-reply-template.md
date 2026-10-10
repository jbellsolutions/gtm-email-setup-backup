# SpeakerAgent PR Agency Reply Templates (#3577260, #3316611)

Hardcoded reply templates for PR agency / communications campaigns. Rules: NO pricing, NO white label, NO made-up features. Keep it clean and direct.

These templates bypass DeepSeek entirely — the daemon should use them for any #3577260 or #3316611 reply.

## Template 1: "What does a typical engagement look like?" (Second reply after case study)

Used when a lead who already got the initial reply + case study asks for engagement details.

```
Hey {Name},

Good questions — happy to break it down.

A typical engagement: we plug SpeakerAgent.AI into your backend. The system researches and qualifies podcast opportunities for your clients — finding shows that match their expertise and audience. Then it handles outreach, booking logistics, and follow-up under your brand. Your team stays focused on client strategy. We're the engine behind the scenes.

Speaking opportunities follow the same model — SpeakerAgent scans for relevant conferences and events, handles the submission pipeline.

{FOUNDER_NAME} (looped on this thread) can walk you through what it looks like in practice and whether it's a fit for {COMPANY}'s client base. Worth 15 minutes?

{SENDER_NAME}
```

**Variables:**
- `{Name}`: lead's first name (from reply)
- `{COMPANY}`: lead's company (from research or email signature)
- `{FOUNDER_NAME}`: Tony (for SpeakerAgent campaigns) or Justin (for AI Integraterz campaigns)
- `{SENDER_NAME}`: persona name from the original sent email

## Template 2: Initial reply — "Tell me more" (First reply)

```
Hey {Name},

In a nutshell, we work hand-in-hand with you as a partner in the backend to help you fulfill all your client's needs for podcast bookings, and soon also for conferences.

I've looped in the owner of SpeakerAgent.ai, {FOUNDER_NAME}, on this email so you guys can connect and see if there is some synergy.

{SENDER_NAME}
```

## Template 3: Case study follow-up (Circling back after no response)

```
Hey {Name},

Following up — wanted to share a case study from an agency we worked with. I think there are some parallels with what you're doing: https://aiintegraterz.com/case-studies/marketing-agency

Worth 15 minutes?

{SENDER_NAME}
```

## Template 4: Pricing question (Deep-funnel — lead who's seen case study + engagement details)

Used when a lead who's gone through the full funnel asks about pricing. They've already seen the case study, gotten the engagement breakdown, and are now asking "how do you price?" / "what's the cost?" This is a buying signal — handle it without giving numbers.

```
Hey {Name} — glad it's clicking.

Pricing really depends on scope and client volume — it's not one-size-fits-all. {FOUNDER_NAME} (already on this thread) can walk you through what it looks like for {COMPANY} specifically.

Worth hopping on a quick call?

{SENDER_NAME}
```

**Real example (Jul 17, 2026):** Spark (Campfire Group, #3577260) — 5-message thread: "Tell me more" → case study → "what does a typical engagement look like?" → engagement breakdown → "Makes sense, how do you price?" Used this template, replied within 21 minutes. No pricing numbers, pushed to Tony call.

## Template 5: Post-pricing acceptance (Deep-funnel close — lead said "sure" after numbers were given)

**⚠️ This template is an EXCEPTION to the "never mention pricing" rule.** Use ONLY when the operator has already given real pricing numbers in the thread and the lead replied "sure" / "yes" / "let's do it." Do NOT use this for initial pricing questions — those still get Template 4.

Used when pricing was already given, the lead accepted, and you need to close with a booking link. Reference the accepted range to show you're aligned, re-loop the founder, and push to the call.

```
Hey {Name} —

Great. Let's get this moving.

{FOUNDER_NAME} (looped back on this thread) can walk you through the onboarding and get you set up. We'll work within the {PRICE_RANGE} range we discussed for the {SCOPE} setup.

Here's a time that works: {BOOKING_LINK}

{SENDER_NAME}
```

**Variables:**
- `{PRICE_RANGE}`: the exact range the operator gave (e.g. "$1,500–$3,000"). Quote it verbatim — don't renegotiate.
- `{SCOPE}`: what the pricing was for (e.g. "single-client", "3-client"). From the operator's pricing message.
- `{BOOKING_LINK}`: Cal.com booking link for Tony/Justin
- `{FOUNDER_NAME}`: Tony (SpeakerAgent) or Justin (AI Integraterz)

**Real example (Jul 17, 2026):** Spark (Campfire Group, #3577260) — after 12 messages over 16 days, the operator gave $1,500–$3,000/mo for single-client setup. Ethan replied "sure" at 4:55 PM ET. Cron monitoring sweep caught it ~3h later with `our_replies_after=0`. Closing reply sent at ~4:30 PM ET with Template 5, re-looping Tony. Full case study: `references/spark-deep-funnel-case-study-2026-07-17.md`.

**Why this template breaks the "never mention pricing" rule:** The pricing is already in the thread. Not referencing it looks evasive or like you don't remember what you sent. Acknowledging the agreed range builds trust: "We talked about X, and that's what we'll do." The call is still where the deal closes — the email just gets them there.

## Pitfalls

- **Never mention pricing** — no "$X/hour" or "$X/month" or "as little as." This is NOT the AI operator $10/hr offer. That offer belongs to #3520103 (AI Guy) only. When a lead asks "how do you price?", use Template 4 — acknowledge the question, say it depends on scope, and push to the founder call. Never deflect entirely (looks evasive) but never give a number. **Exception:** if the operator has ALREADY given real pricing numbers in the thread and the lead accepted ("sure" / "yes"), use Template 5 (post-pricing acceptance) — acknowledge the agreed range, re-loop the founder, and push to booking. The pricing is already in the thread; not referencing it looks evasive.
- **Never mention white label** — "under your brand" is OK. "White label" triggers agency owners who've been burned by resellers.
- **Never make up features** — SpeakerAgent does podcast booking and conference submissions. Don't invent LinkedIn automation, cold email, or other capabilities.
- **Tony is the closer** — the reply should loop Tony in, not try to close the deal in email. The call IS the pitch.
- **Sender persona extraction** — get the sender name from the quoted "On ... wrote:" line in the reply body. The `from_name` field on SENT messages is unreliable (often null).