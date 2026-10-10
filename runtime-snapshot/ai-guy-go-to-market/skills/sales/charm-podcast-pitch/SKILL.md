---
name: charm-podcast-pitch
description: >
  Writes Charm Offensive cold-email pitches to get the user booked as a guest on podcasts —
  personalized to the specific show and host, using the Identity→Struggle→Discovery→Surprise story
  arc. Use when the user asks to "get on podcasts", "pitch a podcast", "be a podcast guest", "book
  podcast interviews", "email a podcast host", or wants to land guest spots to build influence.
version: "1.0.0"
source: "Adapted from Jon Buchan's Charm Offensive plugin"
metadata:
  hermes:
    tags: [outreach, podcast, pr, sales, copywriting]
    related_skills: [charm-offensive-foundation, charm-reply-handler]
---

# Charm Offensive — Podcast Guest Pitch

Land guest spots by sending a pitch that's genuinely fun to read: an honest ego-rub, a compelling
personal story, and a clear, self-aware case for why you'd be a great guest for *this* show.

## Step 0 — Load voice, story, and profile (always)

1. Load `skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')`.
2. Load `skill_view(name='charm-offensive-foundation', file_path='references/story-formula.md')` — the
   Identity→Struggle→Discovery→Surprise arc and the "So why the hell am I writing to you?" 5-bullet list
   are the backbone of this pitch.
3. Get the user's `charm-profile.md` (story + offer + voice assets). You especially need a **strong
   personal story** and a clear sense of what value/entertainment they bring to an audience. If there's
   no story yet, build one with `charm-offensive-foundation` first.
4. Load `skill_view(name='charm-podcast-pitch', file_path='references/template.md')` for the exact pitch skeleton.

## Step 1 — Research the show (do this genuinely)

For each target podcast, use web search / the show's site / recent episodes / the host's socials to find:
the host's name, the show's angle and audience, a few recent episode topics, and an **honest** reason
you like it. The method's rule: an ego-rub is great, but keep it honest — don't pretend to be a
long-time superfan if you just discovered it. "Love your podcast. Really enjoyable. I just discovered
it recently and I'll listen to as many as I can" is honest and still flattering.

Also identify a genuine, specific angle you can offer *their* audience that isn't already covered.

## Step 2 — Draft the pitch

Follow `references/template.md`:

- **Intriguing subject line**, optionally in an unusual font, to stand out.
- **Honest ego-rub** opener (real, not fake-superfan).
- **Your story** using Identity→Struggle→Discovery→Surprise — make them scroll, keep curiosity alive,
  end on a pattern interrupt (the absurd image/prop). This is the emotional hook.
- **"So why the hell am I writing to you?"** → the 5-bullet list: (1) I like your show; (2) why I'd be
  a good guest [your reasoning/proof]; (3) what I can offer your audience [useful + entertaining +
  ideally unique]; (4) my mission; (5) the self-aware fifth-bullet joke.
- **Warm, low-key close:** "Fingers crossed. Either way, thanks for the podcast — keep up the great
  work. Stay vigilant,". Unusual sign-off + job title.

Personalise every pitch to the specific show — the story can be reused, but the compliment, the angle
for their audience, and the reasoning must be true for *that* podcast.

## Step 3 — Self-check and deliver

Run the voice self-check. Confirm: the ego-rub is honest; the story has all four beats and a curiosity
gap; the 5-bullet list is show-specific; there's a genuine unique angle for their audience; sign-off
has personality. Deliver the subject line (+ alternate) and body, and note where any image/prop goes.
Offer to produce a batch personalised to a list of shows. Never send without approval.

## References

- `references/template.md` — the podcast pitch skeleton with the story arc and 5-bullet list, plus the
  annotated "drunk cold email" example that famously booked the author onto shows.