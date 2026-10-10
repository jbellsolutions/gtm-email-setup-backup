---
name: independent-newsletter-production
description: Use for independent-news email issues.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, independent-news, editorial, email, qa]
    related_skills: [newsletter-pipeline, newsletter-creation-qa-guide, grounded-citations]
---

# Independent Newsletter Production

Use this class-level workflow for newsletters that behave like independent editorial publications: a reported lead, point-of-view analysis, shorter dispatches, and a recognizable newsroom identity. This is not a roundup-card or promotional-card workflow.

## Editorial shape

1. Choose one timely, source-verifiable development in the publication's beat.
2. Separate reported fact from analysis. Attribute dates, organizations, announcements, figures, and quotes directly to the source.
3. Build one strong LEAD with an explicit point of view, then 2–4 compact dispatches that extend, complicate, or localize the lead.
4. Keep the issue useful to practitioners: explain the incentive shift, operating consequence, or power change behind the news.
5. Keep commentary clearly distinguishable from reported facts; do not inflate a press release into a claimed business outcome.

## Research and source ownership

- Verify every customer-facing source in a real browser, not only with curl or a search snippet.
- A search-result snippet can identify a candidate story but cannot support article details. Load the specific article page and record the exact passage; if the body fails to load, use only claims verified on an accessible primary page and label the news lead unconfirmed.
- Distinguish an indexed source package or cached proof bank from the actual named primary files. When an identity brief requires a source archive or swipe file, do not reconstruct attributed principles or quotations from memory. Stop, or draft only independently verified high-level material without attribution until the package is supplied.
- Resolve the sending platform before locking HTML. Do not guess between providers whose merge tags, draft behavior, tracking, or footer rules differ; mark HTML platform-unresolved if the platform is not confirmed.
- Record exact page URL, final URL, publication/date, title, and verbatim evidence for every load-bearing factual claim.
- Prefer an owned or issue-specific source footprint. Do not reuse a shared article/link across publications when the identity requires zero shared footprint.
- If the requested owned source is unavailable, mark the issue blocked rather than silently substituting a shared source.
- Use a citation ledger while drafting; do not reconstruct URLs from memory after prose is written.

## Visual identity and email design

- Give each publication its own visual world. A broadcast/newsroom treatment can use a chyron-like wordmark, white background, wide canvas, black ink, and one electric accent.
- Do not reuse another publication's palette, image source/tool, typography system, card grid, or hero treatment.
- Use an independent image lane and write text-safe prompts only; the designated image generator creates the assets.
- Prefer one lead image plus text-led dispatches. Avoid turning independent news into six decorative cards.
- Build with inline CSS, table layout where needed, generous whitespace, ASCII-safe entities, and mobile-safe widths.

## Compliance and delivery gates

- Verify exact From, Reply-To, byline, brand, CTA authorization, physical address, unsubscribe control, and platform merge tags.
- For ListMonk-style templates, use `{{ UnsubscribeURL }}` and `{{ MessageURL }}` only as required by the platform and validate their exact spelling.
- Run prohibited-brand, banned-phrase, unsupported-claim, duplicate-source, and metadata checks before delivery.
- A missing physical address is a send-readiness blocker. Do not invent one; report the blocker and keep the package draft-only.
- Deliver HTML, image prompts, a source ledger/evidence record, and a QA report. Never auto-send or test-send without explicit authorization.

## Reusable reference

For the verified source-ownership and newsroom-layout lessons from a Referral Channel issue build, see `references/referral-channel-issue-2-lessons.md`.
