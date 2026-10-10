---
name: publishable-document-handoffs
description: Use when publishing shareable workflow or handoff documents.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [documents, handoff, publishing, google-drive, docx, pdf, sharing]
    related_skills: [docx, pdf, composio, google-workspace]
---

# Publishable Document Handoffs

## Overview

Turn completed workflows, technical kits, and operating systems into self-contained artifacts for people who cannot access the current chat. Produce the actual documents, sanitize them, and verify every external link or file claim.

## When to Use

Use for technical or operational handoff packages, reusable systems, playbooks, agent instructions, and requests for Google Drive, Google Docs, Word, PDF, or downloadable archives. Do not use for a casual answer that does not need a durable artifact.

## Operating principles

1. Publish the deliverable, not merely a summary.
2. Separate canonical source material from presentation documents.
3. Sanitize credentials, private IDs, internal paths, customer data, private metrics, and organization-specific history before sharing.
4. Make the handoff self-contained: scope, prerequisites, setup, workflow, safety gates, troubleshooting, acceptance checklist, and receiving-agent instructions.
5. State account boundaries clearly: recipients use their own account, credentials, data, and configuration.
6. Treat creation, sharing, rendering, and delivery as separate evidence boundaries.
7. If a requested binary upload or permission change is not verified, say so and provide the verified alternative.

## Workflow

### 1. Inventory

Name every source file in scope and classify it as canonical content, script/template, or human-facing material. The source inventory is complete only when every intended file is accounted for.

### 2. Sanitize

Scan the source package for organization names, credentials, private account IDs, private URLs, internal paths, customer data, private metrics, and account-specific history. Replace them with neutral language or recipient-owned placeholders. Re-run the scan after editing.

### 3. Build the documents

Create a polished combined document containing title/purpose, scope/exclusions, contents, operating contract, prerequisites, ordered workflow, quality and safety gates, troubleshooting, acceptance checklist, and explicit agent instructions. When requested, create DOCX and PDF versions with real headings, readable spacing, page breaks, and code formatting. The artifacts must open and contain substantive expected sections.

### 4. Publish to Google Drive/Docs

Prefer the configured Composio Google integration. For text handoffs:

1. Resolve a requested folder to an opaque folder ID.
2. Call `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` with MIME type `application/vnd.google-apps.document`.
3. Capture the returned file ID.
4. Call `GOOGLEDRIVE_GET_FILE_METADATA` requesting `id,name,mimeType,webViewLink,webContentLink,trashed,parents`.
5. Return the verified `webViewLink`.

For binary uploads, stage the file through the connector's supported cloud-backed mechanism and pass its `s3key`; never pass a local path where a staged key is required. If staging is not verified, publish the complete text handoff as a Google Doc and provide local binary paths separately.

### 5. Share safely

New Drive files are private by default. Broaden access only after explicit user instruction and with a named audience. Prefer named users/groups and least privilege. After permission changes, re-fetch metadata and, if needed, list permissions to verify propagation. Never claim link sharing unless the permission was actually created and verified.

### 6. Final response

Lead with the verified share link. Then list local artifacts, contents, sanitization performed, verification performed, and any limitation. Do not bury the primary link in a long explanation.

## Quality gates

- [ ] Scope and audience are clear.
- [ ] Workflow is ordered and actionable.
- [ ] Prerequisites and owner-supplied values are explicit.
- [ ] Side effects have approval gates.
- [ ] Unknown platform behavior is labeled.
- [ ] Sensitive source-specific facts are removed.
- [ ] DOCX/PDF/archive open and contain expected content.
- [ ] Cloud metadata matches intended name and MIME type.
- [ ] Share URL came from verified metadata, not a guessed URL.

## Common pitfalls

1. Summary instead of deliverable: create the actual documents.
2. Private details in a portable kit: sanitize and scan before publishing.
3. Creation mistaken for sharing: verify permissions separately.
4. Local path passed to remote upload: stage and use the required cloud key.
5. Guessed Drive URL: retrieve `webViewLink` via metadata.
6. Folder name passed where ID is required: resolve and verify the folder first.
7. Main document overloaded with implementation files: keep the handoff readable and preserve scripts in an archive.
8. Visual verification overstated: if rendering tools are unavailable, report structural/text verification only.

## Reference

See `references/google-drive-publishing.md` for the verified cloud-document recipe and binary-artifact boundary.

## Completion criteria

The task is complete only when the requested artifact exists, opens, has passed a sensitive-material scan, and every external link or limitation in the final response is grounded in actual tool output.
