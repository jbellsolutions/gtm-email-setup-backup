---
name: instantly-solar-auto-reply
description: "Instantly solar replies; auto-send approved template."
version: 1.0.0
author: AI Integraterz
license: Proprietary
metadata:
  hermes:
    tags: [Instantly, solar, auto-reply, power-partners]
    related_skills: [instantly-cold-email, charm-qc-gate]
---

# Instantly Solar Auto-Reply

## Scope

This exception applies only to campaign `dbd68956-2dc6-47e4-a56e-5a518db39381` (`solar | open door`) and inbound records with `ue_type == 2`.

Justin explicitly authorizes automatic sending for ordinary positive replies in this campaign when the exact template below is used. This is the only campaign-specific auto-send exception. All other Instantly replies remain draft-only and require approval in Slack.

## Hard-stop routing

Do not auto-send if the inbound reply contains a specific question, objection, request for a custom plan, pricing question, service-area question, technical solar question, or unusual factual request. Create a draft for Justin instead.

Question signals include `?`, and substantive uses of `how`, `what`, `which`, `where`, `when`, `why`, `can you`, `do you`, `are you`, `is this`, `how much`, `pricing`, `cost`, `service area`, `battery`, `storage`, `inverter`, or `commercial`. Explicit negative, unsubscribe, OOO, auto-responder, and referral/routing messages are never auto-sent.

Short ordinary affirmatives such as `yes`, `yes please`, `sure`, `okay`, `sounds good`, `send it`, `tell me more`, and equivalent positive replies may use the template.

## Approved template

Use the lead's first name, company name when available, and sender persona. Keep the graph URL and booking URL unchanged. Do not add claims, guarantees, prices, or alternative wording.

```html
Hey {first_name} — love the quick yes. Here's a short version of what we do for {company_name} and what the power partner graph looks like:

<a href="https://arctic-flame-n5am.here.now/">View the solar power partner graph</a>

In a nutshell, we map out your referral program, then recruit the businesses already speaking with the homeowners and property owners who are a fit for solar. That can include roofers, electricians, HVAC companies, remodelers, real estate professionals, property managers, builders, landscapers, security companies, insurance agents, homeowner associations, and other local businesses with the right relationships.

We work directly with those partners, handling the outreach, campaigns, promotions, and follow-through for you. That keeps your team hands-off while leads, sales conversations, campaigns, and partner promotions move into your system every week.

You are not paying for ads. You pay a commission when a sale closes, so the partner network is tied to actual revenue instead of another monthly marketing expense.

<a href="https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery">Book a time here that works for you and let's jam out on it</a>

{sender_persona}
<a href="https://aiintegraterz.com/stop-renting">More on the approach</a>
```

## Short-version / case-study reply variant

When a solar prospect asks for a case study, asks for the short version, asks what the program would look like for them, or asks how it works, use exactly this reply structure. Replace `{business_name}` with the prospect's business name and hyperlink the business name to the graph URL. Do not add a booking link, explanation, pricing, extra claims, or additional wording.

```html
Here's an example of how it'll work for you.

<a href="https://arctic-flame-n5am.here.now/">{business_name}</a>
```

## Sending requirements

Instantly `POST /api/v2/emails/reply` requires `reply_to_uuid`, `eaccount`, `subject`, and `body.text` plus `body.html`. Use the inbound message ID as `reply_to_uuid` and the inbound `to_address_email_list` sender mailbox as `eaccount`. Verify HTTP 200 and a new outbound record before logging success.

## Verification checklist

- [ ] Campaign ID exactly matches the solar campaign.
- [ ] Inbound record is `ue_type == 2`.
- [ ] Reply is ordinary positive interest, not a question or objection.
- [ ] No later outbound reply exists in the thread.
- [ ] Template is unchanged except first name, company, and persona.
- [ ] HTML links and paragraph breaks are intact.
- [ ] Instantly returns HTTP 200 with a new outbound ID.
- [ ] Specific questions are drafted, not auto-sent.
