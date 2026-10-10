---
name: charm-linkedin
description: >
  Writes Charm Offensive LinkedIn connection invites and follow-up messages that get accepted and
  start conversations — personalized with research on the prospect. Use when the user asks to "write
  a LinkedIn invite", "LinkedIn connection request", "LinkedIn message", "LinkedIn outreach", "DM this
  person on LinkedIn", "follow up after they accept", set up a LinkedIn lead-gen sequence, or wants
  their LinkedIn messaging to sound human and funny instead of salesy.
version: "1.0.0"
source: "Adapted from Jon Buchan's Charm Offensive plugin"
metadata:
  hermes:
    tags: [outreach, linkedin, sales, copywriting, dm]
    related_skills: [charm-offensive-foundation, charm-reply-handler, outflo-linkedin]
---

# Charm Offensive — LinkedIn

Write LinkedIn invites and follow-ups that feel human, get accepted at scale, and open a real
conversation — using disarming honesty and humour, then a soft, gain-framed pitch.

## Step 0 — Load the voice and profile (always)

1. Load `skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')`.
2. Get the user's `charm-profile.md` (ask for it or build a quick one via `charm-offensive-foundation`).
   You need: what they do / who they help, the sector(s) they love, and their sign-off style.
3. Load `skill_view(name='charm-linkedin', file_path='references/templates.md')` for the exact invite + follow-up copy.

## Step 1 — Scale vs. key prospect

Ask which mode:

- **At scale** (a segment / OutFlo or LinkedHelper campaign): use the light, human, non-personalised invite —
  "even a generic-but-human invite gets a lot of accepts." Then a sector-specific follow-up after they
  connect. Use safe merge fields ({firstname}) only.
- **Key prospect** (someone they *really* want): fully personalise. Research them and reference a
  genuine, specific detail. This is worth the extra effort and always beats the scale template.

## Step 2 — Research

For key prospects (and to sharpen segment messaging): use OutFlo LinkedIn MCP tools if available,
web search, and the company's LinkedIn page to find role, what they post about, shared interests,
recommendations, the sector they're in. Capture only genuine hooks. For the sector follow-up, you
mainly need to name their sector convincingly and show you love working in it (the Liking principle).

## Step 3 — Draft

**Invite** — keep it short, human, and a little cheeky. Two proven shapes (see `references/templates.md`):
the "not-the-generic-invite" line, or the "one/two punch" (a curiosity hook + a funny escape hatch
that sets up the follow-up). Character-limit aware (300 characters for connection notes).

**Follow-up (after they accept)** — reference the humour in the invite, make light of the sudden
pitch, show you love their sector, and frame it as *them* gaining ("ideas you're free to steal"), not
a hard sell. Low-pressure CTA to chat.

Keep LinkedIn messages shorter than emails. One hook, one soft ask.

## Step 4 — Self-check and deliver

Run the voice self-check. Then output: the invite text (with character count if near the limit), the
accept-follow-up, and, for a sequence, any second nudge — each labelled. If the user runs OutFlo
LinkedIn, format with the right merge fields for that platform. Never automate sending without the
user's approval; respect LinkedIn's limits and terms.

## References

- `references/templates.md` — invite copy (generic-human + one/two punch), the sector-specific
  follow-up, and the post-accept "spill the beans" message, with annotations.