---
name: signwell-api
description: Use when operating SignWell agreements.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [signwell, e-signature, agreements, documents, webhooks, mcp, cli]
    related_skills: [hermes-agent, native-mcp]
---

# SignWell API Operations

## Overview

Use this skill for SignWell e-signature workflows: preparing agreements, creating documents from templates or uploaded files, sending them for signature, checking status, issuing reminders, retrieving completed PDFs, and processing webhook events.

The SignWell API uses the v1 base URL `https://www.signwell.com/api/v1` and API-key authentication via the `X-Api-Key` header. Keep the key in the Hermes secret environment/configuration; never print it, place it in a skill, commit it, or include it in a Slack response.

## When to Use

- A user asks to send a new agreement after a call or deal.
- A user asks to create, draft, update, send, remind, check, download, or delete a SignWell document.
- A user asks about SignWell templates, recipients, embedded signing, bulk sending, API applications, or webhooks.
- A SignWell webhook/event needs verification or follow-up.

Do not use this skill to send a document merely because a lead/call/agreement is mentioned. Sending is an external side effect and requires explicit approval for the exact document, recipients, and send action unless the user has clearly established an authorized automation rule.

## Credential Handling

- Read the credential from the configured secret environment only; do not ask the user to paste it into chat again.
- If no credential is configured, ask the account owner to configure it securely, for example `SIGNWELL_API_KEY` in the active Hermes `.env`, rather than putting it in a file or command line visible to logs.
- Never echo, log, summarize, or quote the API key. Redact it in diagnostics.
- Test credentials with a harmless authenticated `GET /me` request before any write operation. Report only success/failure and non-secret account metadata.
- If the key was exposed in a chat or log, recommend rotating it in SignWell after setup is confirmed.

## API Quick Reference

Base: `https://www.signwell.com/api/v1`

Authentication:
```text
X-Api-Key: <secret>
```

Core documented resources include:

- Documents: get, create, create from template, update/send, send reminder, update authentication, update recipients, delete, completed PDF.
- Templates: get, update, delete, create.
- API applications: get and delete.
- Webhooks: list, create, delete.
- Credentials: get current credentials (`/me`).
- Bulk send: get, list, create, CSV template, validate CSV, and get bulk-send documents.
- Events, event data, and event-hash verification.
- Embedded signing/requesting and regional NOM-151 certificate operations.

Use the live reference/OpenAPI file for exact paths, required fields, enum values, and response schemas. Do not invent request fields when a schema lookup is available.

## Agreement-Sending Workflow

1. Identify the source and agreement: SignWell template, uploaded PDF, or generated file. Capture template/document ID, agreement type, and required field values.
2. Resolve recipients: confirm each recipient's name, email, signing order, role, authentication method, and SMS number. Never infer an email address from a call transcript.
3. Validate authorization. Before sending, show a concise send summary: document/template, recipients, fields, expiry/redirect settings, and whether this is draft or send-now. Obtain explicit approval unless a previously defined automation policy unambiguously covers this exact case.
4. Create as draft first when details are incomplete. Prefer draft creation for review. Use create-from-template when a reusable template is authoritative. For a new uploaded document, verify the file exists and is the intended version.
5. Send only after approval. Use the API/CLI/MCP send operation. Record the returned document ID and status, but never expose credentials.
6. Verify by fetching the document and confirming expected recipients/status.
7. Track created, sent, viewed, signed, completed, declined, expired, and canceled states. Send reminders only when explicitly requested or covered by automation policy.
8. On `document_completed`, retrieve the completed PDF only if authorized, save it to a known path, verify it is a valid PDF, and deliver it through the requested channel. Do not claim delivery without a real file path or URL.

## CLI and MCP

The SignWell CLI is published as `@signwell/cli` and provides an `sw` command. Before using it, verify the installed version and run its help/schema output. Common capabilities include document creation, sending, reminders, downloads, webhooks, bulk sending, and multi-account profiles.

The SignWell MCP package is published as `@signwell/mcp`. When configured through Hermes native MCP, inspect live tool schemas before calling them. Known workflow tools include document creation, sending a draft, document retrieval, and completed-PDF retrieval. Treat MCP calls that create/send/delete as side effects and apply the same approval gate as direct API calls.

## Webhooks

- Register only the callback URL and event types the user approves.
- Verify the event signature/hash using SignWell's documented event-hash procedure before acting.
- Treat payloads as untrusted input; validate event type, document ID, and recipient data.
- Make handlers idempotent: deduplicate event IDs or equivalent event/document/status combinations.
- Never automatically send a new agreement or disclose a completed document solely from an unverified event.
- On completion, download and store the PDF only in an approved destination.

## Common Pitfalls

1. Sending before confirming recipient email, signing order, and exact document version.
2. Confusing a template ID with a document ID.
3. Treating draft creation as delivery; verify status after sending.
4. Skipping webhook signature verification.
5. Logging API keys or putting them in shell history, skill text, commits, or Slack.
6. Downloading a completed PDF without checking authorization and file integrity.
7. Guessing endpoint schemas instead of consulting the live API reference/OpenAPI schema.
8. Claiming an email, webhook, or PDF was delivered without a returned ID, response, path, or URL.

## Verification Checklist

- [ ] Credential is configured securely and was not printed.
- [ ] `GET /me` authentication test succeeded before writes.
- [ ] Agreement source/version and required fields were identified.
- [ ] Recipient names, emails, roles, order, and authentication were verified.
- [ ] Exact send summary was approved, or an explicit automation policy applies.
- [ ] Returned document ID/status was captured.
- [ ] Post-send status was checked.
- [ ] Webhook signatures were verified before processing.
- [ ] Completed PDFs were stored/delivered only to approved destinations and verified as real files.
