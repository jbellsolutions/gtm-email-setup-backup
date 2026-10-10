---
name: newsletter-creation-qa-guide
description: Use for mandatory newsletter delivery QA and blocker checks.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, qa, browser-verification, compliance]
    related_skills: [newsletter-pipeline, newsletter-types]
---

# Newsletter Creation and QA

Run this checklist before every delivery and attach the completed report. If a blocker fails, do not deliver the issue as complete.

## Universal blockers

- One newsletter was produced at a time.
- Every external source was loaded in a real browser, confirmed as the specific article/page, and checked for the exact cited claim. Record URL, browser result, date, and verbatim quote.
- Stories are current unless the identity explicitly permits evergreen material.
- No fabricated facts, URLs, titles, dates, numbers, outcomes, or frameworks.
- The file differs from the prior version when called revised.
- No auto-send or test-send occurred.
- Image prompts are included; Xander generates the images.

## Type-specific checks

### Niche/industry: pure education
The Agency Insider, The Protocol, The Green Room, The People Person, The Daily Sun, and The Front Desk must contain no native affiliate card, no bottom CTA, no affiliate offer mention, and no offer link. Their job is trust and sender statistics.

### The Dealmaker
Editorial/informational, Brian Kurtz/Jay Abraham preeminence. Do not use the old direct-response letter format or shared Front Desk design. Its CTA and mission framing must follow the current identity brief.

### The Referral Channel
Editorial/independent news: strong lead, point-of-view framing, and dispatches. It must have a distinct newsroom identity and design, separate from The Dealmaker.

### Local Affiliate Pro
Story-led/promotional StoryBrand format. Do not use the old numbered roundup. The reader is the local-business hero; the mission concerns taking back power from Big-Tech advertising.

### The Open Source
Editorial/informational Donald Miller storytelling with the anti-big-AI superhero theme, once its identity skill is available.

## Compliance and HTML

- No `AI Integraterz`, `Published by AI Integraterz`, or `power partner` in customer-facing copy.
- No banned words: `game-changing`, `unlock`, `revolutionize`, `imagine if`, `supercharge`.
- No false relationship claims in cold outbound.
- Use the publication's own brand, byline, From, Reply-To, logo, design, address, unsubscribe controls, and approved merge tags.
- White background, spacious layout, distinct publication footprint, inline email-safe styles, and ASCII-safe entities.
- TOC and story structure must match the actual issue.

## Report sections

### A. Sourcing
List every external URL, browser result, specific-page confirmation, publication date, cited claim, and exact supporting quote. Confirm no duplicate story.

### B. Content/type
Confirm the issue follows its assigned type and identity. For niche newsletters, confirm zero offer touches. For permitted flagships, confirm the authorized mission-framed conversion path.

### C. Compliance
Confirm no prohibited brand leakage, banned wording, false relationship claims, unsupported claim, or incorrect sender metadata.

### D. Format/design
Confirm the identity-specific structure, distinct design, white background, inline HTML, merge tags, footer, and matching TOC.

### E. Delivery hygiene
Confirm the file diff, image prompts, attached source ledger, attached QA report, and no send/test activity.
