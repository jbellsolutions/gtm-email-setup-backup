---
name: spam-word-checker
description: "Always-on spam/deliverability guardrails for cold email copy. Apply to every subject line, opener, follow-up, and CTA. Trigger on 'check this for spam', 'spam check', 'QA this copy', 'flag banned words', 'is this safe to send', or whenever cold email copy is generated or reviewed."
version: 1.0.0
source: Adapted from GrowthEngineX coldoutboundskills
---

# Spam Word Checker

Apply these rules to EVERY piece of cold email copy.

## Banned Single Words

`get`, `bank`, `credit`, `access`, `open`, `compare`, `problem`, `now`, `billing`, `deal`, `finance`, `financial`, `claims`, `insurance`, `mortgage`, `soon`, `new`, `performance`, `freedom`, `home`, `sales`, `medical`, `urgent`, `life`, `marketing`, `investment`, `diagnostics`, `friend`, `cash`, `invoice`, `extra`, `purchase`

Compound variants are also banned: `cash-cycle`, `invoice-line`, `extra-room`, `purchase-cycle` etc.

## Banned Short Phrases

`off chance`, `one time`, `all good`, `following up here`, `last note from me here`, `great fit`, `bumping this once`, `just following up once`, `circle back`, `one more quick follow-up`, `keep this open`, `compare notes`, `compare notes live`, `appreciate the reply`

## High-Risk Promotional Wording (Banned)

`$$$`, `50% off`, `100% guaranteed`, `100% free`, `act fast`, `act immediately`, `act now`, `amazing deal`, `best price`, `bonus`, `buy now`, `call now`, `claim now`, `click here`, `click below`, `discount`, `exclusive deal`, `expires today`, `fast cash`, `free`, `free access`, `free trial`, `guaranteed`, `hurry up`, `limited time`, `lowest price`, `make money`, `no cost`, `no obligation`, `no strings attached`, `once in a lifetime`, `order now`, `risk-free`, `satisfaction guaranteed`, `save $`, `special offer`, `take action now`, `this won't last`, `unbeatable`, `unbelievable`

## Phishing-Style Language (Banned)

`access your account`, `account update`, `activate now`, `change password`, `click to verify`, `confirm your details`, `final notice`, `immediate action required`, `last warning`, `log in now`, `password reset`, `security breach`, `verify identity`

## Formatting & Style Bans

- No em dashes (—)
- No ALL CAPS
- No multiple exclamation marks (!!)
- No greeting prefix before first name (no "Hi John," — just "John,")
- No third-person company references (`[Company] offers`, `[Company] helps`)
- No fake urgency or misleading subject lines

## Unsubscribe / Closeout Line Rules

Never promise to stop following up based on silence.

**Banned:** "I will take silence as a no", "read no reply as a pass", "If I don't hear back I'll leave it there"
**Allowed:** "A reply of 'no' or 'pass' is enough and I'll step out of your inbox", "Just say the word and I'll stop"

Rule: the user must do something explicit for the sequence to stop. Silence keeps cadence running.

## Safe Replacements

| Banned | Replacement |
|---|---|
| `free consultation` | `open to a short conversation` |
| `special offer` | `what we're seeing in the market` |
| `act now` | `if relevant, happy to send details` |
| `guaranteed results` | `this may be relevant depending on your situation` |
| `click here` | `let me know and I can send it over` |
| `limited time` | `not sure if this is timely for you` |

## Rewriting Logic

- Rewrite hype → plain, observational language
- Replace pressure → permission
- Replace promotional wording → specific business language
- If it sounds like an ad, coupon, scam, or phishing → rewrite
- If it sounds AI-polished → simplify until it reads like a person speaking plainly

## Final QA Checklist

- [ ] Scan subject line for spam triggers
- [ ] Scan body for banned/high-risk wording
- [ ] Rewrite hype-heavy lines into plain language
- [ ] Remove fake urgency
- [ ] Confirm email sounds like a credible real person

## What to Do Next

If copy passes: proceed to upload. If flags fired: rewrite flagged lines, re-check.

## Related

- Already enforced in `/tmp/ai-integraterz-cold-email/data/voice_rules.md` (25+ banned slop phrases, no URLs in emails 1-3, no em dashes)
- legacy email platform campaigns use plain text (not HTML)
