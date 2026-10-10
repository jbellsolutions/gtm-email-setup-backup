# Nine-step partner campaign rebuild

## Trigger

Use this pattern when a partner/outreach campaign needs three distinct angles, with two follow-ups attached to each angle, for nine total emails per lead.

## Verified Instantly pattern

- Fetch campaign leads with `POST /api/v2/leads/list`, using `campaign` as the filter and `starting_after` cursor pagination.
- Update existing leads with `PATCH /api/v2/leads/{lead_id}` and per-lead `custom_variables` named `email_1_subject` through `email_9_subject` and `email_1_body` through `email_9_body`.
- Patch the campaign with nine variable-only email steps. Use a per-step body such as `<div>{{email_1_body}}</div>` and a subject such as `{{email_1_subject}}`.
- Set `stop_on_reply: true` and `stop_on_auto_reply: false` when real human replies should stop progression but OOO/autoreplies should not.
- Re-fetch the campaign and all leads after updates. Assert lead count, nine steps, paused/draft state, and zero update failures.

## QA gates

For the full lead set, verify:

- Every lead has all 9 subject/body variables.
- Email 1 bodies are materially distinct across leads. A unique-body count near the lead count is evidence against a shared template.
- Greetings do not use role labels or malformed first names. Treat names like `Info`, `Office`, `Admin`, and digit-prefixed mailbox-derived names as unresolved.
- Every subject is lowercase and 1-4 words.
- Bodies preserve paragraph breaks as `<br><br>` and contain no em dashes, hype, or banned words.
- Word counts are checked after HTML break tags are normalized. Resolve both under-minimum and over-maximum failures before re-uploading.
- Do not treat custom-variable persistence as rendered-email verification. Preview a representative lead in the platform before activation.

## Failure lessons

A first pass can appear personalized while still repeating the same structure. Company/service substitution alone is insufficient. Use three genuinely different angles and distinct follow-up questions, then machine-check the resulting lead records. Also scan source-derived company/service/research text for banned words: the source signal can reintroduce terms that the template itself avoids.
