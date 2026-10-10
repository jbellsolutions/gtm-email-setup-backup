---
name: email-send-reconciliation
description: Use before reusing an email list after prior sends.
version: 1.0.0
category: email
metadata:
  hermes:
    tags: [email, deliverability, suppression, listmonk, bird, resend, reconciliation]
---

# Pre-send Email Reconciliation

Use this class-level workflow before sending a new campaign to a list that has appeared in any prior campaign. Prevent repeat delivery to hard bounces, blocked recipients, and complainants while separating provider delivery evidence from ListMonk application counters.

## Campaign identity

For every prior campaign, record exact provider, sender, subject, send window, campaign ID if available, and audience. Do not identify a campaign only by approximate date or a shared sender.

## Recipient-level evidence

Retrieve hard bounces, blocked/suppressed recipients, complaints, and provider-permanent failures from every provider. Use provider pagination or an export and deduplicate by provider message ID. Account-wide totals and ListMonk `bounces` are health indicators, not recipient lists. A first API page is not a complete ledger.

Suppress a soft bounce only when the same normalized recipient is evidenced as soft-bounced on both prior sends. Preserve status, reason, provider, campaign, message ID, and timestamp. Never infer a recipient from an aggregate count.

If a required provider credential, campaign filter, pagination path, or export is unavailable, do not claim the audience is clean. Stop the scrub and report the precise missing evidence.

## Auditable suppression CSV

Normalize addresses by trimming whitespace and lowercasing. Deduplicate across providers and campaigns. Produce a final one-row-per-address CSV with at least:

`email, provider(s), campaign(s), status(es), reason(s), observed_at`

Keep detailed evidence separate from the owner-facing suppression file. Never expose API keys in the CSV or chat.

## Apply and verify

Add each final bad address to the provider suppression mechanism or ListMonk blocklist as appropriate. Remove them from the master list and every per-niche list. Re-fetch every affected list and suppression record to verify persistence. HTTP 200, a UI toast, or an API request count is not persistence proof. Report per-list removed counts, confirmed/unsubscribed counts, and final clean master count.

Do not delete source evidence before the owner-facing CSV is written and verified. Do not suppress deferred-only recipients or all members of an aggregate category.

## Test and approval gate

Before loading a reused audience, verify the asset, sender, reply-to, subject, tracking configuration, and provider isolation. For HTML with relative images, upload each image and rewrite every reference to a verified absolute URL, including CSS background URLs and Outlook/VML fallbacks. Preserve a finished layout when instructed.

Run only the explicitly authorized internal test. Verify arrival, mailbox placement where observable, image rendering, CTA destination, unsubscribe, view-online, and real tracking evidence. Provider acceptance proves transport only, not inbox placement or opens/clicks.

After the test, stop. A full-list send requires a clear explicit approval from the designated approver. Silence, a prior general authorization, or a test result is not approval.

## Provider isolation and reporting

With ListMonk, persist and re-read that exactly one SMTP provider is enabled. Record rate, concurrency, sender, reply-to, target list, campaign ID, audience snapshot, and body/template identity. Separate ListMonk counters from provider counters. Filter Bird or Resend stats by exact sender, subject, and time window before reporting.

## Pitfalls

- Do not start while the suppression set is incomplete.
- Do not rely on a local bounce file without confirming its campaign/provider.
- Do not call a campaign clean when one provider returned 403/401 or pagination stopped early.
- Do not send because an earlier message authorized a different campaign or provider.
- Do not report fabricated test arrival, rendering, placement, tracking, or provider totals.

## Reference

See `references/pre-send-suppression-reconciliation.md` for the evidence matrix, CSV schema, and verification checklist.
