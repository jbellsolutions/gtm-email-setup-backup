---
name: email-reply-crm-export
description: "Use when exporting email replies into a CRM."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [email, Instantly, CRM, CSV, GoHighLevel, data-export]
    related_skills: [xlsx]
---

# Email Reply → CRM Export

## Overview

Use this class-level workflow when moving replies from an email platform into a CRM, especially when the operator wants a downloadable CSV first. The source of truth is a complete, cursor-paginated export from the active platform, not a recent snapshot or cached seven-day report.

Separate **inventory**, **export**, and **CRM write**. Inventory and CSV creation may proceed once the source is authenticated. CRM writes require validation of the destination, field mapping, duplicate policy, and authorization.

## When to Use

- Exporting replies from Instantly into CSV.
- Preparing contacts for GoHighLevel or another CRM import.
- Preserving phone numbers embedded in reply signatures.
- Combining campaign, thread, timestamp, sender, body, and source metadata.
- Producing separate files for a focused campaign and related campaign families.

Do not use a recent cached snapshot when the operator asks for all-time history. Do not write CRM records until duplicate handling and field mapping are verified.

## Source Inventory

1. Authenticate to the designated sending platform. For this operation, use **Instantly**.
2. List campaigns and identify exact campaign IDs by name. Save the selected ID set in the export manifest.
3. Pull `/api/v2/emails` with cursor pagination: `limit=100`, then `starting_after=next_starting_after`, until no next cursor remains. Filter locally by selected campaign IDs.
4. Treat `ue_type` values `2` and `3` as inbound reply candidates, then deduplicate by message ID. Preserve each raw record.
5. Respect Instantly's documented rate limit of 20 requests per minute. Retry HTTP 429 with backoff and never call a partial sweep complete.
6. Record pages, records fetched, selected campaigns, inbound replies, phone-bearing records, and errors in a manifest.

The re-runnable export procedure is in `references/instant-reply-export.md`.

## Data Preservation and Phone Extraction

For every inbound reply, preserve:

- Reply/message ID and timestamp
- Campaign ID/name and thread ID
- From/To addresses and subject
- Lead ID when present
- Full plain-text body
- Full HTML body when present
- Raw JSON payload

Extract phone numbers from the full reply/signature text, not only the platform lead object. Keep all distinct matches in a separate `phone_numbers` field; never overwrite the original body. Phone extraction is enrichment, not proof that a number is current or callable.

Use UTF-8 with BOM for CSV files intended for spreadsheet/CRM upload. Preserve long text fields and set CSV parser field limits high enough for long email threads.

## Campaign-Family Outputs

When distinct lists are requested, create separate files:

- Focused campaign file, such as `solar_replies_all_time.csv`.
- Related family file, such as `jv_owned_audience_replies_all_time.csv`.
- Manifest containing counts and source campaign IDs.

Campaign-family membership must use explicit campaign IDs or a documented name rule. Do not infer membership from a cached report's labels.

## GoHighLevel Destination Gate

1. Confirm the location ID independently from the supplied URL. A contact-detail URL is not itself an import endpoint.
2. Validate the private integration token with a read-only request to `https://services.leadconnectorhq.com/locations/{location_id}` using the current API version header. A successful location response proves authentication and location access, not contact-creation authorization.
3. Confirm the returned destination name matches the intended location.
4. Inspect or confirm the CRM contact schema. Map `firstName`, `lastName`, `email`, `phone`, company, tags, and custom fields. Store full reply text/source metadata in notes or custom fields only when supported.
5. Produce a dry-run report: source rows, unique emails, duplicate emails, phone-bearing rows, missing usable names, and proposed mapping.
6. Only then create/update contacts in bounded batches with idempotency based on normalized email. Re-fetch a sample after writing and reconcile created, updated, skipped, and failed counts.

Never print private integration tokens in logs or generated files. If a token is pasted into chat, recommend rotation after the operation.

## Verification Checklist

- [ ] Exact Instantly campaign IDs are listed in the manifest.
- [ ] Pagination reached the terminal cursor with no unresolved errors.
- [ ] Export is all-time unless a date range was explicitly requested.
- [ ] Inbound direction is filtered correctly; sent messages are excluded.
- [ ] Message IDs are deduplicated.
- [ ] Full text, HTML, and raw payload are preserved.
- [ ] Phone extraction ran against full body/signature text.
- [ ] Separate campaign-family CSVs have verified row counts.
- [ ] CSV files are UTF-8 with BOM and readable after writing.
- [ ] CRM location authentication and destination name are verified read-only.
- [ ] Dry-run field mapping and duplicate report are complete before CRM writes.
- [ ] Post-write counts and sample records are verified.

## Common Pitfalls

1. **Using a seven-day snapshot for an all-time request.** Run a complete cursor sweep and store the manifest.
2. **Stopping at the first page.** Continue until `next_starting_after` is absent.
3. **Calling a successful API response complete while rate-limited midway.** Back off and resume; report partial results as partial.
4. **Assuming lead records contain phones.** Reply signatures often contain the strongest phone evidence; scan full bodies.
5. **Treating a contact-detail URL as an import endpoint.** Extract and validate the location ID, then use the documented CRM API.
6. **Writing contacts before a dry run.** Export and reconcile first; CRM writes can create duplicates.
7. **Discarding raw reply content after extraction.** Keep full text, HTML, and raw JSON for auditability.
8. **Logging or redistributing private integration tokens.** Use credential channels and rotate exposed tokens.
9. **Confusing campaign names with IDs.** Names group records for humans; API filtering and deduplication use IDs.
