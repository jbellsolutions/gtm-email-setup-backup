---
name: charm-proposal
description: >
  Builds a winning Charm Offensive proposal and pitch after a discovery call — structured for IMPACT,
  the six persuasion principles, and tiered pricing, then delivered with the right follow-up email.
  Use when the user asks to "write a proposal", "put together a proposal/deck", "the perfect proposal",
  "pitch document", "quote a client", "price this project", "proposal follow-up email", or "prep for
  the pitch meeting" after a prospect has shown interest.
version: "1.0.0"
source: "Adapted from Jon Buchan's Charm Offensive plugin"
metadata:
  hermes:
    tags: [sales, proposals, pricing, closing, conversion]
    related_skills: [charm-offensive-foundation, charm-reply-handler]
---

# Charm Offensive — The Perfect Proposal & Pitch

Build a proposal that demonstrates you listened, have sound ideas and a solid plan, and gives clear
costs — structured so it lands (IMPACT first), persuades (the six principles), and prices smartly
(tiers/anchoring). Then deliver it with a warm, prompt follow-up.

## Step 0 — Load voice, story, and profile (always)

1. Load `skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')`.
2. Load `skill_view(name='charm-offensive-foundation', file_path='references/story-formula.md')` — IMPACT
   → Communicate → Persuade and the six persuasion principles are the backbone here.
3. Get the user's `charm-profile.md` (offer, proof points, team, testimonials, case studies).
4. Load `skill_view(name='charm-proposal', file_path='references/structure.md')` for the full section-by-section proposal outline and the send email.

## Step 1 — Gather the inputs

Pull everything learned on the discovery call (from `charm-reply-handler` if it ran, or ask the user):
the prospect's goals and challenges; their KPIs / "picture of success"; budget signal (or none);
decision-makers; what impresses them; and any assets they shared (customer profiles, analytics). Also
confirm which of the user's testimonials, case studies, and proof points are true and usable.

## Step 2 — Structure the proposal (see `references/structure.md`)

Order matters — win attention before you explain or persuade:

1. **Brief / Introduction** — restate *their* goals and challenges in their words (shows you
   listened) + a short intro to your business (the proposal may reach people you've never met).
2. **Your Approach** — show your process; use diagrams, not walls of text. Lead with **IMPACT**, then
   Communicate, then Persuade.
3. **Plan of Action** — the concrete steps you'll take, with timings where relevant.
4. **Your Team** — mini bios (experience, credentials, a fun fact); include freelancers/partners.
5. **Cost** — if you don't know the budget, offer **three tiers** that increase in service and price
   (anchoring). Don't overwhelm with options; too many options stall decisions.
6. **Testimonials & Case Studies** — real ones only. Offer to draft a testimonial for a client to
   approve (containing specific results). LinkedIn recommendations count.
7. **Conclusion / Summary** — restate goals+problems, how you help, your process, that referees can
   be contacted (with permission), and finish with why you'd love to work on this.

Weave the **six persuasion principles** throughout: Authority (proof, press, awards), Consensus
(named clients/logos), Liking (you're fun to work with; shared values), Reciprocity (deliver the
proposal in an interesting way; free ideas), Scarcity (a time-limited window), Commitment (make
starting easy — a trial/mini-engagement).

Keep prose tight and readable (Hemingway-style, ~grade 6). Never fabricate results, clients, or quotes.

## Step 3 — Build the deliverable

Produce the proposal in the format the user wants:
- **Slide deck** → use the `powerpoint` skill
- **Document** → format as markdown or use available document tools
- **PDF** → use `nano-pdf` skill for polished PDF output

For dream/important clients, go the extra mile (a fingers-crossed team photo, a short thank-you video,
a small gift with a handwritten note — mind corporate gift policies).

## Step 4 — The send email + pitch prep

- **Send email** (in `references/structure.md`): warm, prompt, "I got it to you a little earlier than
  expected", offers references, proposes the review call, "we'd absolutely love to work on this".
- **Pitch prep:** practise aloud and time it (leave room for questions); cut anything irrelevant or
  that you can't defend; bring a non-salesy team member (their enthusiasm reads as genuine); be
  enthusiastic — "enthusiasm is intoxicating… the least costly and most effective cosmetic available".
- **Follow up** the call/meeting promptly — it shows you care, and are prompt and reliable.

## References

- `references/structure.md` — the full section-by-section outline, tiered-pricing/anchoring guidance,
  the six-principles checklist, the proposal send email, and the pitch-day checklist.