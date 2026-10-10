---
name: sendfox
description: "Use for SendFox newsletters and API campaigns."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sendfox, newsletters, email, campaigns, contacts, lists, api]
    related_skills: [email-platforms, newsletter-pipeline, newsletter-creation-qa-guide]
---

# SendFox API

## Overview

Use this skill for SendFox newsletter operations through the REST API: create draft campaigns, update drafts, assign lists, schedule or immediately send campaigns, inspect campaign statistics, and manage contacts and lists.

The authoritative documentation is [SendFox API docs](https://sendfox.com/developer/docs/). The docs currently identify API version 1.4.0 and describe OAuth 2.0 / personal-access-token authentication. For complete endpoint details, load `references/sendfox-api.md`.

## New AI tools

SendFox now offers three AI-assisted features:

- **AI Writer:** Start from an X post, YouTube video, blog article, or a plain-language idea. After answering a few questions, SendFox drafts an email in a voice matched to previously sent campaigns. Review, edit, and add your own details before sending.
  - Free accounts: 5 drafts to try
  - Lifetime plans: 15 drafts per month
  - Pro plans: unlimited drafts per month
  - Try it: https://sendfox.com/trk/click/gv99wy0j/8nzqgzr
- **AI subject-line suggester:** Available in the campaign composer to generate alternative subject lines. SendFox states that suggestions have been shown to improve open rates by 14%; treat this as a vendor-reported claim, not a guaranteed result.
  - Try it: https://sendfox.com/trk/click/gv99wy0j/8nzqgzr
- **SendFox MCP:** Connects a SendFox account to AI assistants such as Claude for plain-English account management, including adding and tagging contacts, drafting and sending campaigns, building automations, and checking email performance. Available for Pro and Empire plans.
  - Try it: https://sendfox.com/trk/click/gv99wy0j/xgljrl5

See the announcement/changelog for the full details: https://sendfox.com/trk/click/gv99wy0j/we0py0j

When using AI-generated drafts or subject lines, review the output for factual accuracy, brand voice, privacy, links, unsubscribe handling, and compliance before sending. The existing explicit approval and send-safety gates in this skill still apply. Do not treat MCP access as authorization to send or modify an account without the user's explicit approval for that operation.

## Credential handling

- Never put the API token in this skill, a source file, a command-line argument, a campaign body, or chat output.
- Use an environment variable named `SENDFOX_API_KEY` loaded from the active profile's secret environment file.
- The user-provided token was exposed in chat. Treat it as compromised and rotate it at `https://sendfox.com/account/oauth` before production use.
- Do not send, schedule, create, update, or delete anything until the requested operation and target list/campaign are explicit. Read-only discovery is safe.

```bash
export SENDFOX_API_KEY='REPLACE_WITH_A_NEW_SENDFOX_TOKEN'
```

## API connection

- Base URL: `https://sendfox.com/api`
- Authentication: `Authorization: Bearer $SENDFOX_API_KEY`
- Content type: `application/json`
- Rate limit: 60 requests/minute per authenticated user. On `429`, honor `Retry-After`.
- Common errors: `401` unauthorized, `403` forbidden/account restricted or plan restriction, `402` plan/contact limit, `409` conflict, `422` validation error.
- Error bodies use Laravel-style JSON with `message` and, for validation, `errors`.

```bash
curl --fail-with-body --silent --show-error \\
  -H "Authorization: Bearer ${SENDFOX_API_KEY}" \\
  -H 'Accept: application/json' \\
  'https://sendfox.com/api/campaigns'
```

Never print the authorization header or token. Redact response fields that could contain subscriber PII.

## Newsletter workflow

1. **Inventory:** `GET /lists` and `GET /campaigns`; identify the exact list ID and check for duplicates.
2. **Prepare:** write subject, preview text, HTML, sender name, and sender email. Validate links, unsubscribe handling, and mobile-safe HTML.
3. **Create a draft:** `POST /campaigns` without `scheduled_at` and preferably without `lists` while reviewing. Required: `title`, `subject`, `html`, `from_name`, `from_email`. HTML limit is 1,000,000 characters; title and subject limits are 191 characters.
4. **Review:** `GET /campaigns/{id}` and confirm subject, sender, HTML, and exact target list.
5. **Assign:** `PATCH /campaigns/{id}` with `lists: [LIST_ID]`. This replaces all current list assignments.
6. **Final gate:** re-fetch. Confirm draft state, exact list, valid subject, and explicit approval for send or schedule.
7. **Send or schedule:** immediate uses `POST /campaigns/{id}/send`; scheduled uses `PATCH /campaigns/{id}` with ISO-8601 `scheduled_at` and at least one list.
8. **Verify:** fetch the campaign and later `GET /campaigns/{id}/stats`. Record the campaign ID and state without secrets or unnecessary subscriber data.

## Campaign quick reference

| Operation | Method | Endpoint | Notes |
|---|---:|---|---|
| List campaigns | GET | `/campaigns` | Paginated, 100 per page |
| Create draft | POST | `/campaigns` | Required title, subject, html, from_name, from_email |
| Get campaign | GET | `/campaigns/{id}` | Verify before transitions |
| Update draft | PATCH | `/campaigns/{id}` | Only unsent; lists replace assignments |
| Delete draft | DELETE | `/campaigns/{id}` | Soft delete; sent campaigns cannot be deleted |
| Send now | POST | `/campaigns/{id}/send` | Requires list; warmup/throttle rules apply |
| Stats | GET | `/campaigns/{id}/stats` | Delivery and engagement counts/rates |

Draft payload shape:

```json
{
  "title": "Weekly AI Briefing",
  "subject": "The practical AI updates worth your attention",
  "preview_text": "Three useful launches and what changes next.",
  "html": "<html>...</html>",
  "from_name": "Your Brand",
  "from_email": "newsletter@example.com"
}
```

For a draft, omit `scheduled_at` and `lists`. Never use placeholder values in a live API request.

## Lists and contacts

Core endpoints include `GET/POST /lists`, `PATCH/DELETE /lists/{id}`, `GET /lists/{list_id}/contacts`, `POST /lists/{list_id}/contacts`, `DELETE /lists/{list_id}/contacts/{contact_id}`, `GET/POST /contacts`, `POST /contacts/batch` (up to 1,000), and `PATCH /unsubscribe`.

Respect consent, unsubscribe status, applicable law, and audience authorization. Never bulk-import or send to a list merely because it exists.

## Safety rules

- Draft creation is reversible; sending, scheduling, deleting, unsubscribing, and changing membership require separate confirmation.
- Do not call `/send` as a test. Use a separate test list or an approved SendFox test path.
- `201` from draft creation means resource created, not delivery.
- Do not retry a send after an ambiguous timeout until `GET /campaigns/{id}` proves it remains unsent.
- For `403`, distinguish account restriction from plan or scheduling restrictions using the response body and account status page.

## Common pitfalls

1. Use `https://sendfox.com/api`, not the docs URL.
2. `PATCH` lists replace all assignments, so preserve intended IDs.
3. Immediate send requires an unsent campaign with at least one list and no warmup/throttle block.
4. Subjects beginning with `RE:` or `FWD:` are rejected.
5. `402` can indicate contact or feature limits even though the API is available on all plans.
6. List endpoints are paginated; the first page is not necessarily the whole audience.

## Verification checklist

- [ ] `SENDFOX_API_KEY` is configured without printing it.
- [ ] Exposed token was rotated.
- [ ] Base URL and Bearer auth are correct.
- [ ] Exact list and audience were verified.
- [ ] Draft was fetched and content parity checked.
- [ ] Send/schedule approval was explicit and separate from draft approval.
- [ ] Post-action state and stats were fetched.
- [ ] Errors were recorded without secrets or unnecessary PII.
