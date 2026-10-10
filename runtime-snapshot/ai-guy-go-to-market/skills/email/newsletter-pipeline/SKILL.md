---
name: newsletter-pipeline
description: Use for source-verified newsletter research, production, QA, and approval gates.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, research, editorial, qa, listmonk]
    related_skills: [newsletter-types, newsletter-creation-qa-guide]
---

# Newsletter Pipeline

This is the shared workflow. Every newsletter is its own publication; load its identity skill and `newsletter-types` before production. Never impose a shared template or footprint.

## Core gates

1. Work on one newsletter at a time.
2. Never fabricate facts, statistics, dates, quotes, URLs, outcomes, or frameworks.
3. Verify every customer-facing source in a real browser. Confirm that it loads, is the specific article or official page, and contains the exact claim used. Record the browser result, final URL, title/publisher, date, and verbatim evidence. Curl/HTTP output alone is insufficient.
4. Use current sources, normally within approximately 60 days for news issues, unless the identity explicitly calls for evergreen material.
5. Diff against prior files before calling anything revised. Never deliver an unchanged file as revised.
6. Write image prompts only. Xander generates images.
7. Run the completed QA checklist before every delivery and attach it. If a blocker fails, fix it or stop.
8. Draft only. Never auto-send or test-send. Xander and Justin approve before any list send.

## Type and offer routing

- Editorial/informational: Dealmaker and niche/industry newsletters. Niche newsletters are pure education with no native affiliate card, no bottom CTA, no offer mention, and no offer link.
- Editorial/independent news: The Referral Channel. Use a strong lead, dispatches, and point-of-view newsroom voice; conversion is mission-framed only when authorized.
- Storytelling: Main Street Affiliate and the story spine of Local Affiliate Pro/Open Source.
- Promotional/story-led: Local Affiliate Pro, using StoryBrand principles with the reader as hero.

The affiliate offer appears only where the identity/type permits it. Never force the old native-card structure onto niche newsletters.

## Production sequence

Research and browser verification -> draft in the identity's type and voice -> write labeled text-safe image prompts -> build the identity's own email-safe HTML -> run QA -> load as a ListMonk draft if requested -> stop for preview approval -> send only after explicit approval.

Use white backgrounds and spacious layouts as the universal design direction, but each publication must have its own fonts, colors, logo, imagery, layout, and subject matter. The old shared Front Desk/Rundown template is retired.

## Delivery package

Deliver the named HTML, source ledger with browser evidence, labeled image prompts, and completed QA report. Do not claim send-ready when images, design, source evidence, destination, or approval gates remain unresolved.

Use `{{ MessageURL }}` and `{{ UnsubscribeURL }}` only when the sending platform requires them. For ListMonk drafts, use blank/raw template ID 8, host images through the media API, and verify the persisted draft body, tracking settings, bounce configuration, and Reply-To before any authorized test.
