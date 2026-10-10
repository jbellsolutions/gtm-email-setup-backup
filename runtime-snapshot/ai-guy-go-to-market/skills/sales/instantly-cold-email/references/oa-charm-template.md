# Owned Audiences Cold Email Template — Charm Offensive + J. Abraham

**Rules:** Charm Offensive voice, J. Abraham partnership framing, no events/home shows/trade shows, no ads. Core value: "We execute proven partnership strategies. You show up and close."

## Sender Personas

Use operator personas (Anna, Brielle, Willow, Lucy, Mila, Julia, Emilia, Bella, Violet, Penelope, etc.) — never sign as Justin. Each persona has their own domain and mailbox.

## Offer

We build referral partnerships using Jay Abraham's methodology — the businesses near you that already have your clients, set up to send them your way. We handle the setup, the conversations, the campaigns. You show up and close.

No ads. No events. No home shows. Just partnerships that generate leads and revenue without spending a dollar on ads.

## Email 1 — The Intro (Day 0)

```
{{first_name}},

You've never heard of me. I got your details while researching {{industry}} businesses — not the smoothest opener, I know.

Here's why I'm in your inbox. We execute Jay Abraham-style partnership strategies for {{industry}} businesses like {{company}}. The practices near you that already have your clients' trust — we turn those into referral engines.

We handle everything. The research, the conversations, the campaigns. You show up and close.

No ads, no events, no trade show booths. Just warm introductions from businesses your future clients already trust.

If this isn't on your radar right now, totally fair. If it is — want me to send over a short version of what this would look like for {{company}}, plus a case study?

{{sender_name}}
```

**Subject:** {{first_name}}, quick thought

---

## Email 2 — The Value Angle (Day 3)

```
Hey {{first_name}},

Sent a note earlier this week about partnerships — the businesses near you that already have your clients walking through their doors.

Different angle today. Most {{industry}} owners I talk to tell me the same thing: ads keep getting more expensive and less effective. Meanwhile, their best clients come from referrals and word of mouth.

We've been executing Jay Abraham's partnership methodology for years. The businesses we set up as referral partners don't cost you a dollar in ad spend. They just send you people who already trust their recommendation.

If this resonates, I'll map out your first three partner categories at no charge. Takes about 15 minutes to review together.

{{sender_name}}
```

**Subject:** different angle on {{company}}

---

## Email 3 — The Nudge (Day 7)

```
{{first_name}},

Did my last couple notes land? I'll be honest — I sent them and now I'm nervously checking my inbox like a teenager waiting for a text back.

If partnerships aren't a priority for {{company}} right now, just say the word and I'll step out.

But if you're even a little curious about what a partnership map looks like for your business, hit reply. I'll build it out, no charge, no pitch — just to show you the potential.

Fingers crossed.

{{sender_name}}
```

**Subject:** re: {{first_name}}, quick thought

---

## Email 4 — The Breakup (Day 14)

```
Hey {{first_name}},

Last one from me. I may have jumped the gun assuming partnerships were on your radar this quarter.

If getting the businesses around you to send clients your way ever becomes a priority, the door's open. We've been doing this long enough to know it works — no ads, no events, no gimmicks. Just warm introductions at scale.

Either way, I wish you and {{company}} all the best.

{{sender_name}}
```

**Subject:** last one, {{first_name}}

---

## Per-Lead Variables

- `{{first_name}}` — lead's first name
- `{{company}}` — company name
- `{{industry}}` — niche/vertical descriptor (e.g., "HVAC", "coaching", "recruiting")
- `{{sender_name}}` — operator persona first name

## Banned Words & Phrases

- events, home shows, trade shows, expos, booths
- ads, advertising, PPC, Google Ads, Facebook Ads (except in "no ads" context)
- unlock, 10x, synergy, leverage, innovative, cutting-edge, solution, game-changer, transform, revolutionize, scale, disrupt
- free consultation, special offer, act now, guaranteed, limited time
- em dashes (—), ALL CAPS, multiple exclamation marks

## Spam Check

Run through `spam-word-checker` skill before uploading any copy. Key flags:
- `get`, `now`, `new`, `free`, `open`, `access` — avoid or replace
- No greeting prefix before first name — use `{{first_name}},` not `Hi {{first_name}},`
- No third-person company references
- No "click here" or promotional language

## QC Gate

Every email 1-4 must pass through `charm-qc-gate` before upload. Check:
- Formatting: blank lines, no collapsed paragraphs
- Language: zero banned words, zero banned phrases, confident tone
- Grammar: no typos, proper casing
