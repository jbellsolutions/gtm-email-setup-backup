---
name: charm-cold-email
description: >
  Writes Charm Offensive cold emails, full multi-step cold email sequences, the "magic" sales-call
  booking email, and the direct-mail-letter → follow-up-email combo — all personalized with research
  on the prospect. Use when the user asks to "write a cold email", "cold outreach", "email sequence",
  "book a sales call", "send a direct mail letter", "warm up a prospect", "reach out to {company}",
  or wants their outbound email to sound like Charm Offensive / disarming and funny rather than salesy.
version: "1.0.0"
source: "Adapted from Jon Buchan's Charm Offensive plugin"
metadata:
  hermes:
    tags: [outreach, cold-email, sales, copywriting, sequences]
    related_skills: [charm-offensive-foundation, charm-reply-handler, charm-proposal, Instantly-cold-email]
---

# Charm Offensive — Cold Email

Write cold emails and sequences that get opened, read, and replied to by being disarmingly honest and
funny instead of salesy. Every draft is grounded in the Charm voice AND in real research on the
prospect.

## Step 0 — Load the voice and the user's profile (always)

Before writing anything:

1. Load `skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')`.
2. Find the user's profile: look for a provided `charm-profile.md` (ask the user to point to it or
   paste it). If none exists, invoke the `charm-offensive-foundation` skill to build a quick one, or
   ask 3 fast questions: who do you help + what problem do you solve; your funny job-title trio /
   favourite-weapon photo; your booking link.

Load the template library via `skill_view(name='charm-cold-email', file_path='references/templates.md')` for the exact, proven copy to adapt.

## Step 1 — Understand the target

Confirm with the user (in one short batch): the specific prospect(s) or the list/segment; the goal
(a 7-minute call, a mini-audit, a reply); channel (cold email, a sequence, or the direct-mail combo);
volume (one bespoke email vs. a scalable template with merge fields).

## Step 2 — Research the prospect (this is what makes it personal)

Do real research before drafting. Use these tools in order of preference:

- **Instantly MCP** (if the lead is in a campaign): use `mcp_Instantly_get_lead_by_email` or `mcp_Instantly_list_campaign_leads` to pull existing data.
- **Lead enrichment / scraping skills**: if `scrapercity-specialist`, `apify`, or `b2b-lead-generation-platforms` skills are installed, use them.
- **Web search**: Use web search for the company site, recent news, a recent post, a genuine hook.
- **Browser automation**: Use `super-browser` skill for deeper research on company sites.

Capture only **true, specific, usable** hooks: a real reason you're reaching out, a genuine
compliment, a recent event, a relevant stat (with source). Never invent. For a scalable template,
research the *segment* and use safe merge fields ({{first_name}}, {{company}}) plus one segment-level
insight rather than fake per-person detail.

## Step 3 — Draft in the Charm voice

Adapt (don't blindly copy) the templates loaded from `references/templates.md`. A single cold email follows
the "magic email" skeleton:

- **Honest, funny opener** (the Reverse / list-worthy line, or a genuine hook from research).
- **Get to the point:** "I help {who} {solve what}" — plus a risk-reversal / no-brainer line if they
  have one.
- **Give them an out:** "if it's not a problem, that's totally cool."
- **Low-pressure CTA:** "would you be open to a quick 7-minute chat? I'll give you ideas you're free
  to steal."
- **The favourite weapon:** note where the pet/absurd photo attaches.
- **Signature:** the three job titles, warm sign-off.

For a **sequence**, use the 8-step arc in `references/templates.md` (intro → "forgot to mention" P.S.
→ sad-photo nudge → helpful-stat angle → light check-in → 3 convenient CTAs → amusing image → polite
final "breakup"). Space steps a few days apart; escalate charm, never pressure.

For the **direct-mail combo**: write a typewriter-style letter first (no logo, bright envelope, wax
seal or handwritten address, optional silly enclosure), then an email a few days later that references
the letter in the subject line and is *different but in the same style*. Two memorable touches beat one.

## Step 4 — Personalize and self-check

Run the self-check from `voice-and-humour.md`. Specifically: opener is a genuine pattern interrupt;
one honest admission + one (not five) jokes; value framed as a gift; CTA has an easy out; short and
scannable; every fact true; subject line intriguing (not "Quick question"); sounds like the user.

## Step 5 — Deliver

Output ready-to-send drafts with: a subject line (and 1–2 alternates), the body, a note of where the
photo/attachment goes, and the signature. For a sequence, label each step and its send-day offset.
If using Instantly, offer to save the sequence via `mcp_Instantly_save_campaign_sequences`. Never send
without explicit approval.

## Compliance

Cold email is legal in most places when done right: honest sender identity, a real reason, a genuine
way to opt out, and respect for unsubscribes (CAN-SPAM / GDPR / local law). Don't email people who've
opted out. Keep claims truthful. Flag to the user if a target segment looks like consumers/EU where
rules are stricter.

## References

- `references/templates.md` — the verbatim 8-part sequence, the "magic" call-booking email, and the
  direct-mail → follow-up combo, with annotations on why each line works.