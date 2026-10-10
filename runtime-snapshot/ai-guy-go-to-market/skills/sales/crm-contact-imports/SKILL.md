---
name: crm-contact-imports
description: "Use for outreach-contact CRM imports."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [crm, contact-import, GoHighLevel, Instantly, data-migration]
    related_skills: [email-platforms]
---

# CRM Contact Imports

## Overview

Use this class-level workflow when moving contacts, lead records, or outreach replies from an email platform into a CRM location. Preserve source context and enrichment such as phone numbers, while preventing writes to the wrong location or re-engagement of opted-out contacts.

The current operational source for outreach replies is Instantly.ai. Do not substitute a retired or unrelated sending platform when the user has explicitly named Instantly.

## When to Use

- Importing email replies or outreach leads into GoHighLevel or another CRM.
- Migrating reply bodies, campaign metadata, thread IDs, timestamps, or phone numbers.
- Reconciling a source export against CRM contacts before an upsert.

Do not use for sending email or replying to prospects.

## Required Workflow

### 1. Confirm the source

Use Instantly.ai's authenticated REST API and `/api/v2/emails` when Instantly is the named source. Check API health, use cursor pagination, respect 429 rate limits with backoff, and filter by exact campaign IDs or names. Distinguish inbound from sent messages using direction/type fields and inspect thread history where needed.

Completion criterion: the extraction report states source platform, campaign scope, pagination result, total records, and inbound-reply count.

### 2. Validate the CRM destination

A contact-detail URL is not automatically an import endpoint. For a GoHighLevel URL shaped like `/v2/location/{location_id}/contacts/detail/{contact_id}`, the segment after `location` is the location ID and the final segment is one contact ID.

Confirm location identity and private-token authorization with a read-only probe before writing. If the API returns an infrastructure or edge-security response, stop writes and report that blocker rather than claiming the token is invalid.

Completion criterion: destination identity and authorization are verified, or the import is explicitly blocked with evidence.

### 3. Normalize without losing source data

Retain email, reliable name fields, phone numbers, company, role, geography, website, LinkedIn, source platform, campaign, sender mailbox, thread/message IDs, subject, direction, timestamps, full reply text/HTML, and classification/status.

Extract phones from structured lead data and reply signatures. Do not assume the provider exposes an unmasked phone number. Preserve raw and normalized phone values and attribute signature-only numbers to the reply.

Use the deterministic email plus source thread/message key for deduplication. Never invent names from email usernames.

Completion criterion: every source reply has a raw payload and deterministic deduplication key.

### 4. Dry-run before writing

Preview selected count, records with email/name/phone/company, duplicates, identity conflicts, proposed native/custom CRM fields, create-versus-update counts, and opt-out/hostile/OOO records. Preserve those records if “all replies” was requested, but mark them suppression-safe rather than active.

Save the preview as a machine-readable artifact. Do not write merely because a token exists.

### 5. Idempotent upsert

Prefer create-or-update by email. Never delete and recreate a contact to add enrichment. Put phone in the native field and preserve the original in a source-data field when normalization changed it. Put source/campaign in tags or custom fields and full reply data in a note or bounded custom field with IDs and timestamps.

Use small resumable batches. Log each outcome, CRM contact ID, and retry/error status without printing credentials.

### 6. Verify after writing

Re-query the exact imported emails. Confirm successful count, phone persistence, metadata/notes, classifications, suppression-safe statuses, and no duplicate contacts. Report creates, updates, skipped duplicates, failures, phone matches, and opt-out count. Never report success based only on bulk HTTP acceptance.

## Common Pitfalls

1. Contact-detail URL mistaken for import destination: separate location ID from contact ID.
2. Wrong provider: use Instantly when explicitly requested; do not rely on stale platform references.
3. Token mistaken for access: distinguish authorization failure from Cloudflare/proxy/edge blocks.
4. “All replies” narrowed to positives: preserve negative, OOO, unsubscribe, and hostile records but suppress follow-up.
5. Phone data dropped: inspect both lead fields and signatures.
6. Writes made before preview: generate a count and mapping preview first.
7. Blind retries: use deterministic keys and reconcile each batch.
8. Shared-channel credential exposure: never repeat tokens; recommend rotation.
9. Stale local snapshot treated as current: refresh live data before importing.

## References

- `references/instantly-to-ghl-session-notes.md` — condensed source/destination findings and evidence from the first import attempt.

## Verification Checklist

- [ ] Correct source and exact campaign scope confirmed.
- [ ] Live extraction completed with cursor pagination and rate-limit handling.
- [ ] CRM location ID separated from contact ID.
- [ ] Read-only destination/auth probe completed.
- [ ] Dry-run preview saved.
- [ ] Phone numbers sourced from structured fields and/or signatures.
- [ ] Opt-outs and hostile replies marked suppression-safe.
- [ ] Upserts are idempotent and resumable.
- [ ] Post-write re-query verifies counts, phones, metadata, and statuses.
- [ ] Credential exposure handled through rotation guidance.
