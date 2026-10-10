---
name: charm-offensive-foundation
description: >
  The shared voice, story, and offer engine for all Charm Offensive outreach skills. Use this
  when the user wants to "set up my Charm Offensive profile", "define my story", "define my offer",
  "define my ideal clients", capture their brand voice for outreach, or when ANY other charm-* skill
  needs the user's story/offer/voice and no profile exists yet. Produces and stores a reusable
  charm-profile.md and teaches the Charm Offensive humour and voice rules that every draft must follow.
version: "1.0.0"
source: "Adapted from Jon Buchan's Charm Offensive plugin (Claude Code plugin)"
metadata:
  hermes:
    tags: [outreach, cold-email, linkedin, sales, copywriting, voice, branding]
    related_skills: [charm-cold-email, charm-linkedin, charm-podcast-pitch, charm-pr-and-speaking, charm-social-content, charm-reply-handler, charm-proposal]
---

# Charm Offensive — Foundation (Voice, Story & Offer)

This skill does two jobs:

1. It **captures the user's Charm Offensive profile** (their story, ideal clients, and offer) and
   stores it as a reusable file the other skills read.
2. It is the **canonical reference for the Charm Offensive voice and humour** — every other
   `charm-*` skill loads `references/voice-and-humour.md` and `references/story-formula.md` from
   here before writing a single word.

The whole method comes from Jon Buchan's Charm Offensive: win attention with disarming honesty and
humour, be human, offer "ideas you're free to steal", and never sound like a corporate sales robot.

## When another skill calls you

If a `charm-*` skill needs the user's story/offer/voice and there is no profile yet, do the fast
version: read `references/profile-template.md`, ask the user the minimum questions to fill it, save
`charm-profile.md` to the user's working directory, then hand control back. Do not block a drafting
task for longer than necessary.

## Building the profile (the full flow)

Use `skill_view(name='charm-offensive-foundation', file_path='references/profile-template.md')` for the exact structure. Walk the user through it, but keep it
light — ask in small batches, not one giant form. Capture:

**Your Story** — what you're great at (up to 5 things); what you stand for (3 values); what you're
against (up to 3 issues in your sector); obstacles you've faced (a struggle that resonates); your
ambitions (not about money). This becomes the raw material for the Identity → Struggle → Discovery →
Surprise story arc used in podcast, PR and speaking pitches. If something isn't genuine, leave it out.

**Your Ideal Clients** — who you help most (roles/titles); sectors you're excited about; where they
are; the attributes you look for (so we can lean on the "Liking" principle).

**Your Offer** — the pain points you solve (general + problems with existing solutions); the pain
points you help them AVOID (e.g. no long contracts, no sleazy tactics); your risk-reversal or
"no-brainer" hook if you have one.

**Your Voice Assets** — the concrete props that make Charm emails land: a photo of a pet / animal
doing something silly (the "favourite weapon"); a self-deprecating photo for follow-ups; three job
titles for the signature (serious / descriptive / funny); the URL and Calendly/booking link; the
sign-off style (e.g. "Have an absolutely wonderful day," / "Stay vigilant,").

## Saving the profile

Write the completed profile to a `charm-profile.md` file and deliver it to the user. Tell
them to keep it handy — they can point any charm skill at it, or paste its contents, so drafts sound
like them and use their real details instead of placeholders.

## The non-negotiable voice rules

Before writing anything in ANY channel, load and apply `references/voice-and-humour.md` (use `skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')`). The essentials:

- **Disarming honesty beats slick selling.** Admit the awkward truth ("I got your details from a
  list… but hey, you're list-worthy, that's gotta count for something, right?").
- **Humour is the pattern interrupt.** Use the ten humour formulas (the Reverse, Triples, Lists,
  Understatement, Exaggeration, Incongruent Absurdity, Funny Words, Oxymorons, Parody). One or two
  well-placed laughs, not a comedy routine.
- **Make it look like they gain**, not like they're being hard-sold. Offer "ideas you're free to steal."
- **Low-pressure CTAs** with a humorous escape hatch ("hit reply, or send me your most cutting insult").
- **Be human and warm.** Sign off with personality. Never corporate, never jargon, never a wall of text.
- **Genuine only.** Never fabricate a shared interest, a fake stat, or a compliment you don't mean.

## Guardrails

Keep it ethical and compliant: real reasons, real facts, honest claims. For cold email, respect
opt-outs and local law (CAN-SPAM/GDPR) — see the note in `charm-cold-email`. Never invent testimonials,
metrics, or client names. If the user hasn't given you a real detail, ask or leave a clearly marked
`{placeholder}` rather than making something up.

## References

- `references/voice-and-humour.md` — the full voice rules + ten humour formulas with examples.
- `references/story-formula.md` — the Identity/Struggle/Discovery/Surprise arc + IMPACT and the six
  persuasion principles.
- `references/profile-template.md` — the exact profile structure to fill and save.