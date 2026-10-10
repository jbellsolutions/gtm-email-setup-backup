# SendFox API reference

Source: https://sendfox.com/developer/docs/ (SendFox API 1.4.0 as inspected during skill creation).

## Authentication and limits

- Personal access tokens are created at `https://sendfox.com/account/oauth`.
- Send `Authorization: Bearer <token>`.
- OAuth client authorization URL: `https://sendfox.com/oauth/authorize`.
- OAuth token URL: `https://sendfox.com/oauth/token`.
- Limit: 60 requests/minute per authenticated user.
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` on 429.
- Errors use `message`; 422 responses may include `errors`.
- API is available on every plan, but plan limits can return 402. Restricted accounts return 403 with `account_restricted`.

## Campaign endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/campaigns` | Paginated campaign list, 100/page |
| POST | `/campaigns` | Create draft or scheduled campaign |
| GET | `/campaigns/{id}` | Fetch campaign |
| PATCH | `/campaigns/{id}` | Update an unsent draft |
| DELETE | `/campaigns/{id}` | Soft-delete a draft |
| POST | `/campaigns/{id}/send` | Schedule a draft for immediate sending |
| GET | `/campaigns/{id}/stats` | Fetch performance statistics |

Create fields: `title` required, `subject` required, `html` required, `from_name` required, `from_email` required; optional `preview_text`, `scheduled_at`, and `lists` (integer IDs). Title/subject/preview/from fields are limited to 191 chars; HTML is limited to 1,000,000 chars. Scheduled campaigns require at least one list. Subject cannot begin with `RE:` or `FWD:`.

Immediate sending requires the campaign not already sent/scheduled, at least one assigned list, and no warmup/throttle restriction. Existing abuse prevention, content approval, throttles, spam detection, and bounce monitoring apply.

Stats fields: `sent_count`, `unique_open_count`, `unique_click_count`, `unsubscribe_count`, `bounce_count`, `spam_count`, `open_rate`, `click_rate`, `unsubscribe_rate`, `bounce_rate`, and `spam_rate`.

## Contacts

| Method | Path | Purpose |
|---|---|---|
| GET | `/contacts` | Paginated contacts, optional `query`, `unsubscribed`, `email` |
| POST | `/contacts` | Create contact; `email` required; optional names, IP, lists, fields |
| GET | `/contacts/{id}` | Fetch contact |
| PATCH | `/contacts/{id}` | Update names, list memberships (replaces), fields |
| DELETE | `/contacts/{id}` | Soft-delete contact and cancel scheduled deliverables |
| GET | `/contacts/{id}/activity` | Contact engagement and deliverables |
| POST | `/contacts/batch` | Up to 1,000 contacts; creates or updates |
| GET | `/contacts/unsubscribed` | Paginated unsubscribed contacts |
| PATCH | `/unsubscribe` | Unsubscribe by required email |

## Lists

| Method | Path | Purpose |
|---|---|---|
| GET | `/lists` | Paginated list search |
| POST | `/lists` | Create with required `name` |
| GET | `/lists/{id}` | Fetch list and average rates |
| PATCH | `/lists/{id}` | Rename list |
| DELETE | `/lists/{id}` | Soft-delete; 409 if in use |
| GET | `/lists/{list_id}/contacts` | Paginated contacts in list, optional query |
| POST | `/lists/{list_id}/contacts` | Add existing contact with `contact_id` |
| DELETE | `/lists/{list_id}/contacts/{contact_id}` | Remove contact |

## Other resources

The API also documents forms, automations, domains, users, and contact fields. Use the live documentation before implementing those operations because their schemas and plan requirements are more branch-specific.

## Safe request example

```bash
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer ${SENDFOX_API_KEY}" \
  -H 'Accept: application/json' \
  'https://sendfox.com/api/campaigns'
```

Never place a real token in this file or in shell history.
