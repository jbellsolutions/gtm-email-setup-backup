# JangoMail v2 REST Endpoint Map

Discovered from `GET /swagger/v2/swagger.json` on 2026-07-16. ~90 paths.

## Account
- `GET /account` — account info (user_id, username, company, billing)
- `POST /account/authenticate` — login
- `GET /account/usage` — emails_allowed, emails_sent, bytes_allowed, bytes_sent
- `GET /account/subaccounts` — list subaccounts
- `GET /account/subaccounts/{id}/usage` — subaccount usage
- `POST /account/new` — create account
- `POST /account/subaccounts/new` — create subaccount
- `GET|PATCH|DELETE /account/subaccounts/{id}` — subaccount CRUD

## API Tokens
- `GET /apitokens` — list
- `DELETE /apitokens/{id}` — revoke

## Attachments
- `POST /attachments` — upload
- `GET /attachments/{filename}` — download

## Bounces
- `GET /bounces` — global bounce list

## Campaigns
- `GET /campaigns` — list active
- `GET /campaigns/previous` — list sent/deleted
- `POST /campaigns/new` — create
- `GET|PATCH|DELETE /campaigns/{id}` — CRUD
- `PUT /campaigns/{id}/send` — send
- `GET /campaigns/templates` — campaign templates
- `GET /campaigns/{id}/stats` — aggregate stats
- `GET /campaigns/{id}/stats/content` — content performance
- `GET /campaigns/{id}/stats/opens` — open events
- `GET /campaigns/{id}/stats/clicks` — click events
- `GET /campaigns/{id}/stats/bounces` — bounce events
- `GET /campaigns/{id}/stats/complaints` — complaint events
- `GET /campaigns/{id}/stats/unsubscribes` — unsubscribe events
- `GET /campaigns/{id}/stats/blocks` — block events
- `GET /campaigns/{id}/stats/recipients` — recipient list
- `GET /campaigns/{id}/stats/recipients/{message_id}/log` — per-recipient log
- `GET /campaigns/{id}/stats/removed_addresses` — scrubbed addresses

## Databases
- `GET /databases` — list databases

## Domain Keys (DKIM)
- `GET /domainkeys` — list DKIM keys
- `GET /domainkeys/{domain_name}/{selector}` — get key
- `POST /domainkeys/{domain_name}/{selector}/disable` — disable
- `POST /domainkeys/{domain_name}/{selector}/enable` — enable

## Lists
- `GET /lists` — list all
- `POST /lists/new` — create
- `GET|PATCH|DELETE /lists/{id}` — CRUD
- `GET /lists/{id}/name` — get name
- `PUT /lists/{id}/Name` — rename
- `GET /lists/{id}/count` — member count
- `GET /lists/{id}/scrubbed_addresses` — scrubbed
- `POST /lists/{id}/scrub` — scrub list
- `GET|POST /lists/{listid}/members` — list/add members
- `POST /lists/{listid}/members/new` — add single member
- `GET|DELETE /lists/{listid}/members/{id}` — member CRUD
- `POST /lists/{listid}/members/purge` — purge members
- `GET /lists/{listid}/members/{email}` — lookup by email
- `POST /lists/{listid}/members/import` — bulk import
- `GET|POST|DELETE /lists/{listid}/fields` — custom fields
- `GET|DELETE /lists/{listid}/fields/{id}` — field CRUD
- `POST /lists/{listid}/fields/new` — create field

## Files
- `POST /files` — upload
- `GET /files/{filename}` — download

## Tracking Domains
- `GET /trackingdomains` — get tracking domain config

## Transactional
- `GET /transactional` — list transactional sends
- `POST /transactional/new` — create
- `POST /transactional/send` — send
- `GET /transactional/ips` — dedicated IPs
- `GET|DELETE /transactional/ips/{id}` — IP management
- `GET /transactional/stats/{id}` — send stats
- `GET /transactional/errors` — error log
- `GET /transactional/{id}/log` — per-send log
- `POST /transactional/clear_errors` — clear error log

## Transactional Groups
- `GET /transactional_groups` — list (includes stats: total_sent, opens, clicks, bounces, complaints)
- `POST /transactional_groups/new` — create
- `GET|PATCH|DELETE /transactional_groups/{id}` — CRUD
- `GET /transactional_groups/{id}/stats` — aggregate stats
- `GET /transactional_groups/{id}/stats/opens` — open events
- `GET /transactional_groups/{id}/stats/clicks` — click events
- `GET /transactional_groups/{id}/stats/bounces` — bounce events
- `GET /transactional_groups/{id}/stats/recipients` — recipient events
- `GET /transactional_groups/{id}/stats/blocks` — block events

## Unsubscribes
- `GET /unsubscribes` — global list
- `POST /unsubscribes/new` — add
- `GET /unsubscribes/{email}` — lookup
- `GET /unsubscribes/domains` — unsubscribe domains
- `POST /unsubscribes/domains/new` — add domain
- `DELETE /unsubscribes/domains/{domain_name}` — remove domain

## Users
- `GET /users` — list
- `POST /users/new` — create
- `GET|PATCH|DELETE /users/{id}` — CRUD
- `GET /users/permissions` — permission list

## Utility
- `POST /verify_email` — verify single email
- `POST /purge_address` — purge address globally
- `POST /merge_lists` — merge two lists
- `POST /check_recipients` — batch check
- `GET /global_suppression` — global suppression list
- `GET /charactersets` — supported charsets
- `GET /encodings` — supported encodings
- `GET /field_types` — supported field types