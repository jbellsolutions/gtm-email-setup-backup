# Anti-AI Campaign Angle (HVAC)

## Positioning

The core campaign angle: **"Customers are tired of the AI hype. They want a real person to call them."**

This positioning attacks the current industry norm (AI chatbots, automated sequences, ad retargeting) and positions the service as refreshingly human — a real person making outbound calls to customers and prospects every day.

## Key Tagline

> If you're tired of the AI hype and all the headaches with ads, content, etc — guess what, your customers are as well. They want you to call them and connect with them.

## Value Prop in One Line

> We embed a real person on your phones who calls your customers and prospects every day. No AI. No automation. No chatbots. Just human conversations.

## Why This Works for HVAC

- HVAC is a trust-based, relationship-driven industry. Customers want to talk to a person when their AC breaks.
- The AI hype is at peak saturation. Standing out means going anti-AI.
- HVAC owners are tired of being sold AI tools. This positioning is contrarian and refreshing.
- Phone calls are still the highest-converting channel for HVAC leads.

## Critical: Instantly Does NOT Support Spintax

**Instantly sends `{option1|option2}` as literal text.** The curly brace + pipe syntax is not processed by Instantly's merge engine. All Spintax must be pre-resolved at generation time — randomly pick one variant per block per lead before uploading. The `{Hey|Hi|Hello}` in these templates is meant to be resolved by your generation script (see `hvac_personalize.py` for the `resolve_spintax()` function), never passed raw to Instantly.

## Banned-Word-Clean Framework Templates

These are pre-verified variants of all 10 frameworks with the anti-AI angle baked in. Every template has been checked against the full banned-word list. Use these as starting points — fill in lead-specific details (name, city, review count, company name).

**⚠️ Spintax note:** Templates contain `{Hey|Hi|Hello}` and `{option1|option2}` patterns. These MUST be resolved before uploading to Instantly — Instantly does NOT process Spintax natively. Use the `resolve_spintax()` function from `scripts/hvac_state_personalize.py` (or inline equivalent) to randomly pick one variant per block at generation time. The examples below show the template form — the actual output should be clean text.

### Framework 1: The Phones Are Quiet

```
{Hey|Hi|Hello} {first_name}, {review_text} — impressive. But when someone in {city} needs a new system or emergency repair, there's a gap between their search and your phone ringing. We embed a real person who calls your customers and prospects every day. No AI chatbots. No automated sequences. No guessing games with ads. Just human outbound calls — the thing that actually works. {risk_reversal} {cta}
```

### Framework 2: Ads Are Broken

```
{Hey|Hi|Hello} {first_name}, {review_text} tells me you do good work in {city}. But most HVAC companies are burning cash on ads and lead gen platforms hoping the phone rings. Meanwhile, customers are tired of the AI hype and chatbots. They want a real person to call them. We embed someone on your phones who calls your customers daily. Actual human conversations. Zero ad dependency. {risk_reversal} {cta}
```

### Framework 6: The Google Problem

```
{Hey|Hi|Hello} {first_name}, {review_text} in {city} — impressive. But here's the catch: Google controls who sees those reviews. Your next customer might be searching right now and never find you. We take a different approach. A real person calls your customers and prospects directly. No AI. No SEO guessing. No ad auctions. Just human outreach. {risk_reversal} {cta}
```

### Framework 4: People Want a Human

```
{Hey|Hi|Hello} {first_name}, here's the thing about {review_text} — people in {city} clearly trust your work. But in 2026, everyone is drowning in AI chatbots, automated texts, and follow-up sequences. Your customers are tired of it. They want someone to call them. We embed a real person on your phones who does exactly that. Human voice. Real conversations. Daily calls. {risk_reversal} {cta}
```

### Framework 5: Everyone Has AI — Nobody Has This

```
{Hey|Hi|Hello} {first_name}, every HVAC company in {city} is now running the same playbook — AI chatbots, automated emails, ad retargeting. {review_text} tells me you've got something better: actual trust from actual customers. We help you put that to work differently. A real person calls your customers. Every day. No AI hype. No automation. Just human conversations that fill your schedule. {risk_reversal} {cta}
```

### Framework 6: The Google Problem

```
{Hey|Hi|Hello} {first_name}, {review_text} in {city} — that's impressive. But here's the problem: Google controls who sees them. Your next customer might be searching right now and never find you because the algorithm changed. We take a different approach. A real person calls your customers and prospects directly. No AI. No SEO guessing. No ad auctions. Just human outreach. {risk_reversal} {cta}
```

### Framework 7: Your List Is a Goldmine

```
{Hey|Hi|Hello} {first_name}, {review_text}. That's a lot of customers who've trusted {company} in {city}. But here's my question — how many of them have heard from you recently? Not an automated email. Not a text blast. A real phone call. We embed a real person who calls your past customers every day. Checks in. Books tune-ups. Reactivates old maintenance agreements. No AI. No automation. Just human follow-up that actually works. {risk_reversal} {cta}
```

### Framework 8: The Silent Bleed

```
{Hey|Hi|Hello} {first_name}, here's something most {city} HVAC companies don't track: how many quotes they send that never turn into change-outs. How many service calls that could've been maintenance agreements. That silent bleed is real. We embed a real person who calls those leads — the ones who got a quote but went quiet, the ones who needed a follow-up. Human voice. No AI. No automation. Just calls that close. {risk_reversal} {cta}
```

### Framework 9: Your Competitors' Phones Are Ringing

```
{Hey|Hi|Hello} {first_name}, {city} is a competitive HVAC market. {review_text} shows you're holding your own. But here's what's happening: your competitors' phones are ringing because someone is actually calling their customers. Not AI. Not ads. Not automated sequences. Real human beings making calls. We embed that same person on your phones. {risk_reversal} {cta}
```

### Framework 10: Go Direct

```
{Hey|Hi|Hello} {first_name}, between lead gen platforms, ad networks, and middlemen, HVAC companies in {city} are sending money to 3-4 different parties just to maybe get a phone call. {review_text} proves you don't need a middleman. You need someone calling your customers directly. We embed a real person who does exactly that. No AI. No platforms. No per-lead nonsense. Just human calls. {risk_reversal} {cta}
```

## Template Variables

| Variable | Source | Example |
|---|---|---|
| `{first_name}` | Contact name or company name extraction (see `references/first-name-extraction.md`) | Mike |
| `{city}` | Lead's city | West Palm Beach |
| `{review_text}` | Formatted from rating + review count | "4.8 stars with 143 reviews" |
| `{risk_reversal}` | Rotated from 5 options (see SKILL.md) | "No contracts. No lock-in..." |
| `{cta}` | Rotated from 4 Spintax patterns (see SKILL.md) | "{Worth a look\|...}?" |
| `{company}` | Full company name | Mike's HVAC |

## Email 2 (Different Framework) Templates

Same structure as Email 1 but select a DIFFERENT framework. The anti-AI angle carries through naturally — just apply a new pain point from the second framework.

## Email 3 (Bump) Template

```
{Hey|Hi} {first_name}, did that last note land? {Curious if|Wondering whether} {pain_point_reference} is {still on your radar|something you're thinking about|still a priority}.
```

Under 30 words.

## Email 4 (Breakup) Template

```
{Hey|Hi} {first_name}, I'll leave you alone after this. If {pain_point} isn't {a priority|top of mind} right now, totally get it. But if it is, {this would be worth 5 minutes|I think this could help}. Either way, no hard feelings.
```

Under 40 words.
