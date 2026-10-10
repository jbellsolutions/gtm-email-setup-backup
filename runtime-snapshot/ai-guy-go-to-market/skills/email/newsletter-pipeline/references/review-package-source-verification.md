# Review-package source verification and handoff

## Purpose

Use this when delegated agents produce newsletter research packages or when a user requests HTML files in Slack. It captures the failure modes from the August 2026 niche-newsletter workflow.

## Source gate

1. Treat delegated summaries, claimed QA counts, and Google News RSS results as intermediate evidence only.
2. For each customer-facing story, retain a direct publisher article URL, publisher, date, and the exact claim supported.
3. Fetch each URL independently before finalizing. A Google News redirect is not a source URL. A publisher homepage is not a source URL. Do not infer a slug from a headline.
4. Remove unsupported numbers, anonymous client results, inferred author details, and internal benchmarks unless they are explicitly labeled as internal and the brief permits them. Editorial briefs generally do not.
5. Keep a stat ledger in the source package and repeat the source evidence in HTML comments only for handoff. QA the visible HTML separately.

## Customer-visible HTML gate

After HTML generation, strip HTML comments and inspect only visible/customer-facing content:

- exactly `{{ MessageURL }}` and `{{ UnsubscribeURL }}` may remain;
- no generic ESP fields such as `{{ PreferencesURL }}`, `{{ SubscriberEmail }}`, `{{ MessageID }}`, or `{{ CampaignID }}`;
- no `AI Integraterz`, `Integraterz`, placeholder fields, social links, banned words, or em dashes;
- the native card is story card 3 and has the same presentation skeleton as cards 1, 2, and 4;
- the CTA URL appears only in the house blurb when the issue brief requires that placement;
- the native card links to the confirmed shared Medium URL and contains the sole semantic native offer mention;
- the footer uses the exact approved physical address and newsletter's own brand.

## Slack attachment gate

`send_message` can return success while warning that MEDIA attachments were omitted for Slack. This is a failed handoff, not a successful attachment delivery.

- Do not retry the same generic route repeatedly.
- Look for a native Slack `files_upload_v2` or equivalent file-upload tool.
- Upload one small known-good file first and verify returned file metadata/permalink.
- Upload the requested files, then verify Slack reports actual downloadable file attachments.
- If no native file-upload capability exists, report the exact blocker and preserve the local paths. Never claim the files were attached or substitute sandbox links when attachments were requested.

## Instruction precedence

When a generic skill conflicts with a user-provided issue brief, follow the issue brief for that issue and document the exception in QA. In the referenced niche workflow, the brief's explicit prohibition on opt-in/sign-up links and its exact two ListMonk merge tags controlled over generic newsletter defaults.