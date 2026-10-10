---
name: the-open-source
description: Use for The Open Source anti-big-AI storytelling newsletter.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, editorial, informational, storytelling, open-source, ai]
    related_skills: [newsletter-pipeline, newsletter-types, newsletter-creation-qa-guide]
---

# The Open Source

The Open Source is an editorial/informational publication told through Donald Miller StoryBrand storytelling. It is a story-led feature built around one real open-source tool per edition, not a six-card roundup and not a direct-response letter.

## Identity and mission

- Brand: The Open Source
- Type: editorial/informational with Donald Miller storytelling
- Tagline: `Open-source AI for the businesses big tech forgot.` Pending final design lock; alternate: `We build the AI, give it away free, and teach you to run it.`
- Byline: Theo Marsh, placeholder pending confirmation; use a distinct builder-editor persona
- From: `The Open Source <open-source@send.usingaitoscale.com>`, local-part pending confirmation
- Reply-To: `xander@usingaitoscale.com`
- CTA: `https://whimsy-nebula-47ch.here.now/`, soft only, unless the free-tool destination replaces it
- SMTP: TBD; Justin assigns
- Source repository: `https://github.com/jbellsolutions`

Mission: level the playing field by helping small and local businesses use real open-source AI rather than remain dependent on big AI and big tech. The reader is the hero; the builders are the guide who arms the underdog.

## Recurring story spine

`199 projects later, you realize AI is only being sold to enterprise.` Contrast enterprise-focused AI sales and slide-deck experts with real software built for actual businesses and made available free. Do not fabricate the 199-project claim or any founder backstory; verify the applicable source before publishing it.

## StoryBrand arc

1. Character: small/local business owner priced out of enterprise AI.
2. Problem: inaccessible tools, cost, dependence, and fear of falling behind.
3. Guide: builders who empathize and have built real software.
4. Plan: explain one verified repo/tool and exactly how to run it.
5. Call to action: use or obtain the free open-source tool, softly.
6. Stakes: remain dependent versus run useful automation independently.
7. Success: a small business operating practical automation at low or no software cost.

## Per-edition structure

- Masthead with brand, on-theme emoji, tagline, issue number, date, Read online, Unsubscribe
- Hero banner image
- Good-morning intro naming the reader as hero and big AI/big tech as the external obstacle
- One POV thesis line
- The Problem
- What We Built, using `The Short Version`, `The Details`, and `Why It Matters` where useful
- How It Works in plain English
- Put It to Work: one concrete step for a small/local business
- Build-along/free tip
- Soft close focused on the free/open mission
- Named sign-off and compliant footer

Use quote blocks, bold/italics, text blocks, and image-as-format. Do not add cards, a table of contents, or a numbered offer list unless a later identity brief explicitly changes the format.

## Source and non-fabrication gate

Each edition features one real repository/tool. Inspect the live GitHub repository, README, and relevant code before drafting. Describe only verified features, setup, behavior, metrics, and backstory. Keep a running featured-repository log so editions do not repeat a repo. If a repository cannot be understood or verified, choose another.

The free-tool destination is unresolved. Do not promise a live download link until the destination is approved: possible options include an Open-Source-branded mirror, a soft reply flow, or a direct GitHub link with the separate-publication implications accepted.

## Design and imagery

Use a distinct white-background, wider layout with its own superhero/open-source identity. Candidate direction: ink-black display headlines, electric blue or comic red accent, bright secondary accent, restrained halftone/panel details, and a shield/crest/terminal/fork emblem. Lock palette, typography, logo, and masthead emoji during the design pass. Do not borrow another newsletter's look.

Xander generates all images. Write text-safe prompts for a small crew of builders arming an underdog, with a consistent heroic/comic editorial treatment that avoids canned stock imagery, readable text, logos, screens, paper, and other writable surfaces. A banner plus one or two in-story visuals is typical; a clean how-it-works graphic may be used when approved.

## Compliance and QA

No `AI Integraterz`, `Published by AI Integraterz`, `power partner`, banned words, fabricated claims, or false relationship language. Footer is The Open Source, `37460 Beacon Brick Road, Zephyrhills, Florida 33541`, and unsubscribe, with no social links. Use inline CSS, ASCII/HTML entities, and `{{ MessageURL }}` / `{{ UnsubscribeURL }}`. Run the mandatory QA report before delivery. Draft and approved test only; Xander approves before any real send.

## Open decisions before Issue 1

- Confirm or replace Theo Marsh.
- Confirm `open-source@` versus `builders@` or `hq@`.
- Approve the free-tool destination.
- Decide whether the standard CTA remains or points directly to the free tool.
- Lock palette, type, logo, emoji, and image direction.
