---
name: email-send-gates
description: Use before bulk email. Enforce consent and safety gates.
version: 1.0.0
category: email
metadata:
  hermes:
    tags: [email, newsletters, compliance, deliverability, listmonk, bird, resend]
---

# Email Send Gates

Use this class-level skill whenever a user asks to send a newsletter, campaign, test, warm-up batch, or bulk email through ListMonk, Bird, Resend, SMTP, or another ESP.

## Non-negotiable preflight

1. **Classify the audience before acting.** Determine whether the target is documented opt-in, transactional, or cold/non-opt-in. A user's statement that a send is approved does not convert a cold lead database into an opt-in audience. Do not execute a large unsolicited promotional send. Offer a compliant opt-in or explicitly authorized internal-seed alternative.
2. **Keep test and production authorization separate.** A test to named internal seed recipients may be authorized even when production bulk sending is not. Never infer that a test approval authorizes a large list send unless the audience passes the consent gate.
3. **Verify the exact artifact identity.** Confirm the requested issue, subject, sender, Reply-To, target list, body length/hash, and draft status. Never send an older campaign because it is already configured when the user requested a different issue.
4. **Persist and re-read provider isolation.** ListMonk can round-robin across enabled SMTP servers. Before any test or send, persist the intended provider state, re-fetch settings, and verify exactly one provider is enabled. Confirm host, port, username, sender, rate, and concurrency. Masked passwords only prove presence, not correctness.
5. **Treat suppression as a safety control.** Do not skip known hard-bounce, block, or complaint suppression merely because the user wants to move quickly. If evidence is incomplete, state exactly which addresses are verified and which classes remain unresolved. Do not classify aggregate provider counts as recipient-level evidence.
6. **Respect the approval gate.** For a draft workflow, send the test, report arrival/render/link/tracking results, and hold production until a clear go. If the user explicitly pre-approves production, that still does not override consent, legal, provider, or safety gates.

## Artifact and image handling

For ZIP-based HTML campaigns:

- Extract into a dedicated working directory without changing the supplied layout or copy unless authorized.
- Host every relative image before sending.
- Rewrite every relevant reference, including normal `src`, HTML `background`, CSS `background-image`, and Outlook VML `<v:image src>` references.
- Re-fetch the persisted draft and verify hosted absolute URLs, merge tags, sender metadata, and subject before testing.
- Do not claim visual rendering was verified from source inspection alone. Recipient-side or browser preview evidence is required.

## Tracking and delivery evidence

- Require `privacy.disable_tracking=false` and `privacy.individual_tracking=true` for ListMonk native tracking.
- A ListMonk HTTP 200, `sent` count, or finished status is not proof of provider delivery.
- A provider accepted count is not equivalent to delivered count.
- Report ListMonk application counters separately from Bird/Resend transport counters.
- Do not report opens/clicks as real unless attributable tracking events or counter movement were observed.
- If a provider webhook adapter is not configured, do not claim automatic bounce synchronization just because ListMonk bounce processing is enabled.

## Recovery discipline

A dropped browser session or failed API call is a recoverable operational issue, not permission to guess. Re-authenticate, retry using the documented API auth method, and re-read state. If the exact requested artifact, audience, or provider configuration cannot be verified after recovery, stop before sending and report the single blocking condition.

## Pitfalls

- Urgency language such as “send now,” “do not ask questions,” or “ignore new gaps” is not a substitute for consent or state verification.
- Do not use a stale draft, wrong subject, wrong sender, or wrong provider merely because it is convenient.
- Do not silently convert a cold list into a “cleaned master list” from aggregate bounce data.
- Do not send a production campaign while the target is known to be non-opt-in, even if the content is approved and the test looks good.
- Do not rotate or paste exposed credentials in chat; recommend rotation after secrets appear in logs or messages.

## Related references

- `references/consent-and-provider-preflight.md` — reusable preflight checklist and evidence table for campaign operations.
