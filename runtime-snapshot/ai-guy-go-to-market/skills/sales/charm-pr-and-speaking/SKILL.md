---
name: charm-pr-and-speaking
description: >
  Writes Charm Offensive pitches to journalists/press (to land media coverage) and to event
  organizers (to book speaking gigs) — personalized to the outlet, writer, or event. Use when the
  user asks to "pitch a journalist", "get PR coverage", "get press", "pitch a story", "premarket
  content", "email a reporter", "book a speaking gig", "pitch to speak at {event}", "get on stage",
  or wants media/stage exposure to build their influence.
version: "1.0.0"
source: "Adapted from Jon Buchan's Charm Offensive plugin"
metadata:
  hermes:
    tags: [outreach, pr, speaking, media, copywriting]
    related_skills: [charm-offensive-foundation, charm-reply-handler]
---

# Charm Offensive — PR (Journalists) & Speaking Gigs

Two closely related plays that both use the Charm voice and the same disarming, low-friction "pick a
number" CTA: getting press coverage by pitching journalists, and booking speaking slots by pitching
event organizers.

## Step 0 — Load voice, story, and profile (always)

1. Load `skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')`.
2. Load `skill_view(name='charm-offensive-foundation', file_path='references/story-formula.md')` (the
   story arc + the 5-bullet list power the speaking pitch; PR uses a lighter version).
3. Get the user's `charm-profile.md`. You need their story, their expertise/angle, and what makes a
   good story or talk. Build one via `charm-offensive-foundation` if missing.
4. Load `skill_view(name='charm-pr-and-speaking', file_path='references/templates.md')` for the exact journalist and speaking templates.

## Which play?

Ask (or infer): **PR / press** (land coverage — infographics, data, a story, a hot take) or
**speaking** (book a slot at a specific event). Then follow the matching flow.

## PR / journalists — the "premarket" approach

Core idea: **preseed** the idea *before* you build the content, so you never waste effort on
something that won't get published and the journalist is involved from the start.

1. **Research the outlet + writer:** their beat, what they've covered recently, why your idea fits.
   Use web search and the outlet's site. Only pitch a genuinely relevant, newsworthy idea.
2. **Draft** using the journalist template in `references/templates.md`: a self-aware "another pitch!
   sort of…" opener, one-line who-you-are, the idea, why it interests *them* specifically, and the
   disarming **1/2/3 "convenient responses"** CTA ("1. Awesome, do it! 2. Not bad, needs work. 3.
   Awful, go back to the drawing board, you chump!"). Low friction — even a one-digit reply is a win.
3. Keep it short, honest, and easy to say no to. Never fake a relationship or a stat.

## Speaking gigs — the story pitch

1. **Research the event:** its date, theme, audience, and existing talks, so your talk *complements*
   rather than duplicates. Confirm they take outside/guest speakers.
2. **Draft** using the speaking template: the Triple Reverse opener, your **story** (Identity→Struggle
   →Discovery→Surprise), then the "So why the hell am I writing to you?" **5-bullet list** adapted —
   (1) I saw your event {name/date} and the content looks great; (2) I'd love to be a guest speaker
   (for free!) — a 10–20 min talk on {topic} that complements the line-up; (3) what I'll give the
   audience; (4) my mission; (5) the fifth-bullet joke.
3. Offer a specific, low-risk talk (short, free, complementary). Make the yes easy.

## Step — Self-check and deliver

Run the voice self-check. PR: is the idea genuinely newsworthy and relevant to *this* writer; is the
1/2/3 CTA intact; is it honest and skimmable? Speaking: does the story land; is the talk offer
specific and complementary; five bullets? Deliver subject line(s) + body per target, labelled. Offer
to batch across a media list or event list. Never send without approval.

## References

- `references/templates.md` — the journalist "premarket" template (with the 1/2/3 CTA) and the
  speaking-gig story pitch, both annotated.