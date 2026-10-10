# JangoMail v2 REST API — Full Endpoint Map

**Source:** `https://api-v2.jangomail.com/swagger/v2/swagger.json` (fetched Jul 14, 2026)
**Auth:** Basic (Base64 username:password) or Bearer token (user-created API key)
**Base URL:** `https://api-v2.jangomail.com`
**Docs:** `https://api-v2.jangomail.com/docs` (Swagger UI with `Try It` enabled)

## Campaign Endpoints (for newsletters)

| Method | Path | Purpose |
|--------|------|---------|
| POST | /campaigns | Create campaign |
| GET | /campaigns | List campaigns |
| PUT | /campaigns/{id}/send | Send a campaign |
| GET | /campaigns/{id} | Get campaign details |
| DELETE | /campaigns/{id} | Delete campaign |
| GET | /campaigns/{id}/stats | Campaign stats |
| GET | /campaigns/{id}/stats/content | Sent HTML & plain text (verify link wrapping) |
| GET | /campaigns/{id}/stats/opens | Open stats |
| GET | /campaigns/{id}/stats/clicks | Click stats |
| GET | /campaigns/{id}/stats/bounces | Bounce stats |
| GET | /campaigns/{id}/stats/blocks | SMTP block stats |
| GET | /campaigns/{id}/stats/complaints | Complaint stats |
| GET | /campaigns/{id}/stats/unsubscribes | Unsubscribe stats |
| GET | /campaigns/{id}/stats/recipients | Recipient list |
| GET | /campaigns/{id}/stats/removed_addresses | Pre-send suppressions |
| GET | /campaigns/{id}/stats/recipients/{message_id}/log | Per-recipient send log |
| GET | /campaigns/templates | List templates |
| GET | /campaigns/new | Get blank campaign schema |

## List/Group Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | /lists | List all groups |
| POST | /lists | Create group |
| GET | /lists/{id} | Get group details |
| DELETE | /lists/{id} | Delete group |
| PUT | /lists/{id}/name | Rename group |
| GET | /lists/{id}/count | Member count |
| GET | /lists/{id}/Name | Group name |
| POST | /lists/{id}/scrub | Scrub list |
| POST | /lists/{listid}/members | Add member(s) |
| GET | /lists/{listid}/members | List members |
| DELETE | /lists/{listid}/members/{id} | Delete member |
| PUT | /lists/{listid}/members/{email} | Update member by email |
| DELETE | /lists/{listid}/members/purge | Purge all members |
| POST | /lists/{listid}/members/import | Bulk import |

## Transactional Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /transactional/send | Send transactional email |
| GET | /transactional | List transactional sends |
| GET | /transactional/{id}/log | Get send log |
| GET | /transactional/stats/{id} | Get stats |
| GET | /transactional/errors | Get sending errors |
| PUT | /transactional/clear_errors | Clear error queue |

## Account Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /account/authenticate | Login (returns token?) |
| GET | /account | Account info |
| GET | /account/usage | Usage stats |
| GET | /account/subaccounts | List subaccounts |
| POST | /apitokens | Create API token |

## Unsubscribes & Bounces

| Method | Path | Purpose |
|--------|------|---------|
| GET | /unsubscribes | List unsubscribes |
| DELETE | /unsubscribes/{email} | Remove unsubscribe |
| POST | /unsubscribes/domains | Block domain |
| GET | /bounces | List bounces |
| DELETE | /bounces | Clear bounces |

## Full Endpoint List (all paths from Swagger spec)

```
POST   /account/authenticate
GET    /account
PUT    /account
POST   /account
GET    /account/usage
GET    /account/subaccounts
POST   /account/subaccounts
GET    /account/subaccounts/{id}/usage
GET    /account/new
GET    /account/subaccounts/new
GET    /account/subaccounts/{id}
DELETE /account/subaccounts/{id}
PUT    /account/subaccounts/{id}
GET    /apitokens
POST   /apitokens
GET    /apitokens/{id}
DELETE /apitokens/{id}
GET    /attachments
POST   /attachments
GET    /attachments/{filename}
DELETE /attachments/{filename}
GET    /bounces
DELETE /bounces
GET    /campaigns/new
POST   /campaigns
GET    /campaigns
POST   /campaigns/previous
PUT    /campaigns/{id}/send
PUT    /campaigns/{id}
GET    /campaigns/{id}
DELETE /campaigns/{id}
GET    /campaigns/templates
GET    /campaigns/{id}/stats
GET    /campaigns/{id}/stats/content
GET    /campaigns/{id}/stats/opens
GET    /campaigns/{id}/stats/clicks
GET    /campaigns/{id}/stats/bounces
GET    /campaigns/{id}/stats/complaints
GET    /campaigns/{id}/stats/unsubscribes
GET    /campaigns/{id}/stats/blocks
GET    /campaigns/{id}/stats/recipients
GET    /campaigns/{id}/stats/recipients/{message_id}/log
GET    /campaigns/{id}/stats/removed_addresses
GET    /databases
GET    /domainkeys
POST   /domainkeys
GET    /domainkeys/{domain_name}/{selector}
DELETE /domainkeys/{domain_name}/{selector}
PUT    /domainkeys/{domain_name}/{selector}/disable
PUT    /domainkeys/{domain_name}/{selector}/enable
GET    /lists/{listid}/fields
POST   /lists/{listid}/fields
GET    /lists/{listid}/fields/{id}
DELETE /lists/{listid}/fields/{id}
PUT    /lists/{listid}/fields/{id}
GET    /lists/{listid}/fields/new
GET    /files
POST   /files
GET    /files/{filename}
DELETE /files/{filename}
GET    /lists
POST   /lists
GET    /lists/new
GET    /lists/{id}/Name
GET    /lists/{id}/count
GET    /lists/{id}/scrubbed_addresses
PUT    /lists/{id}/name
GET    /lists/{id}
DELETE /lists/{id}
PUT    /lists/{id}
POST   /lists/{id}/scrub
GET    /lists/{listid}/members
POST   /lists/{listid}/members
DELETE /lists/{listid}/members
GET    /lists/{listid}/members/new
GET    /lists/{listid}/members/{id}
DELETE /lists/{listid}/members/{id}
PUT    /lists/{listid}/members/{id}
DELETE /lists/{listid}/members/purge
PUT    /lists/{listid}/members/{email}
GET    /lists/{listid}/members/import
POST   /lists/{listid}/members/import
GET    /trackingdomains
PUT    /trackingdomains
GET    /transactional
GET    /transactional/new
POST   /transactional/send
GET    /transactional/ips
POST   /transactional/ips
GET    /transactional/ips/{id}
DELETE /transactional/ips/{id}
GET    /transactional/stats/{id}
GET    /transactional/errors
GET    /transactional/{id}/log
PUT    /transactional/clear_errors
GET    /transactional_groups
POST   /transactional_groups
GET    /transactional_groups/new
GET    /transactional_groups/{id}
DELETE /transactional_groups/{id}
GET    /transactional_groups/{id}/stats
GET    /transactional_groups/{id}/stats/opens
GET    /transactional_groups/{id}/stats/clicks
GET    /transactional_groups/{id}/stats/bounces
GET    /transactional_groups/{id}/stats/recipients
GET    /transactional_groups/{id}/stats/blocks
GET    /unsubscribes
POST   /unsubscribes
GET    /unsubscribes/new
GET    /unsubscribes/{email}
DELETE /unsubscribes/{email}
GET    /unsubscribes/domains
POST   /unsubscribes/domains
GET    /unsubscribes/domains/new
DELETE /unsubscribes/domains/{domain_name}
GET    /users
POST   /users
GET    /users/new
PUT    /users/{id}
DELETE /users/{id}
GET    /users/permissions
GET    /verify_email
POST   /purge_address
POST   /merge_lists
POST   /check_recipients
DELETE /global_suppression
GET    /charactersets
GET    /encodings
GET    /field_types
```
