---
name: sendy
description: "Use when operating Sendy campaigns, lists, or reports."
version: 1.0.0
category: email
metadata:
  hermes:
    tags: [sendy, newsletter, campaigns, lists, deliverability, reporting]
---

# Sendy Operations

Sendy is the primary newsletter platform at `https://sendy.usingaitoscale.com`; brand ID is 1. It sends through the configured own SMTP route, with Amazon SES only as an optional backup. The engineering handoff is `https://mossy-quarry-84pj.here.now`.

## Required preflight

1. Run `health` before any operation. If the local Sendy script or credentials are missing, stop and report that blocker. A web HTTP 200 only proves the app is reachable, not API authentication.
2. Verify the exact newsletter, subject, HTML/body artifact, Reply-To, target list, sender, and draft/send mode.
3. Verify list hygiene before import or send using the verification hub. For cold sends, retain only `DELIVERABLE` results. Suppress every bounce and complaint; never re-mail them.
4. Check every CTA/link domain with Google Safe Browsing and run mail-tester before a send. A flagged CTA domain blocks the send.
5. Confirm sender authentication: From must be on a domain already SPF/DKIM-authorized by the configured SMTP. Never use `@usingaitoscale.com` as From.
6. Confirm domain warming status and approved daily volume. New domains ramp gradually with consistent volume and no spikes.
7. For production sends, obtain explicit confirmation from Xander. `--send` reaches real subscribers; never infer approval from a draft request.

## Brands and UI capabilities

Sendy brands are first-class containers. A brand can have its own campaigns, templates, lists, subscribers, blacklists, autoresponders, segmentation, SMTP settings, tracking/privacy defaults, GDPR options, custom-domain settings, client login, privileges, notifications, fees, and sending limits. The admin UI exposes brand creation with brand name, From name/email, Reply-To, logo, SMTP settings, tracking defaults, opt-in defaults, and client controls.

Brand creation is confirmed through the authenticated admin UI. The current documented wrapper does not expose a brand-create command, so use the UI for brand creation unless the private repository adds an API command. Creating a brand is a real configuration change and requires explicit user direction including the brand name and authorized From domain. Do not configure SMTP unless Justin explicitly directs it, because SMTP settings are UI-only and owned by Justin.

## Commands

Use the provided `sendy.sh` wrapper from the installed Sendy skill/repository:

- `health`
- `subscribe EMAIL ENCRYPTED_LIST_ID [NAME]`
- `unsubscribe EMAIL ENCRYPTED_LIST_ID`
- `delete-sub EMAIL ENCRYPTED_LIST_ID`
- `status EMAIL ENCRYPTED_LIST_ID`
- `count ENCRYPTED_LIST_ID`
- `create-campaign ...` creates a draft; append `--send` only after explicit Xander approval
- `lists ssh` returns numeric DB list IDs and active counts
- `campaigns [N] ssh` returns recent campaign engagement
- `report CAMPAIGN_ID ssh` returns delivered/bounces/complaints plus opens/clicks
- `sql "SELECT ..." ssh` is read-only only

## ID safety

Sendy's API uses encrypted list IDs from the UI. The SSH/DB `lists` command returns numeric IDs. They are not interchangeable. Cross-reference through the Sendy UI before using a list ID in an API command.

## SMTP boundary

SMTP configuration is UI-only and is maintained by Justin. Do not alter SMTP settings through API, SQL, or SSH. Never escalate the boxed reporting SSH account; it is SELECT-only.

## Reporting

After a completed campaign, pull the full `report CAMPAIGN_ID ssh` and report delivered, bounced, complaints, opens, and clicks. Keep application and transport denominators distinct, and note tracking limitations. A campaign creation response is not delivery evidence.

## Held campaign

Local Affiliate Pro remains held until `localaffiliatepro.com` is cleared or Justin supplies a clean stable CTA URL. Do not send it. Treat `whimsy-nebula-47ch.here.now` as a risky ephemeral CTA until replaced.

## Do not

- Do not auto-send.
- Do not send from `@usingaitoscale.com`.
- Do not touch Velocity/edcom for newsletter delivery unless Justin explicitly changes direction.
- Do not rely on SendFox while its payment issue remains unresolved.
- Do not claim Sendy API/SSH health when credentials or the wrapper are absent.
