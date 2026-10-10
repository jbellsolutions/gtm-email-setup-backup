---
name: main-street-affiliate-campaigns
description: "Use for Main Street Affiliates referral-campaign replies and one-pagers."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Main Street Affiliates, solar, affiliate, referral, campaigns]
    related_skills: [campaign-operations, charm-qc-gate, instantly-cold-email]
---

# Main Street Affiliates Campaigns

## Overview

Use this reusable framework when replying to a positive prospect for a Main Street Affiliates campaign. The core offer is a 100-level-deep power-partner strategy adapted to the prospect's niche, starting with solar and expanding to other home-service categories.

## Core operating model

1. Map complementary businesses and referral channels in the prospect's service area.
2. Prioritize four layers:
   - Tier 1: roofing, electrical, HVAC, remodeling, windows, insulation, batteries, generators, and energy audits.
   - Tier 2: real estate, mortgage, inspectors, property managers, builders, investors, and homeowner associations.
   - Tier 3: landscaping, tree service, pools, pest control, pressure washing, security, insurance, restoration, and relevant financial professionals.
   - Tier 4: employers, credit unions, chambers, developers, local media, newsletters, associations, and nonprofits.
3. Recruit affiliate/referral partners with a simple offer and referral path.
4. Create and schedule email, text, newsletter, event, seasonal, and other partner promotions.
5. Run the partner campaigns and route leads to the client.
6. The client follows up, closes systems, and pays commissions on agreed closed sales.

## Commercial offer

When explicitly authorized by the user, state:

- At least five referral partners in the first 90 days.
- 5x return or the client does not pay.

Before a proposal or launch, define the service area, attribution rules, tracking window, commission terms, and return calculation. Do not present illustrative projections as guaranteed lead counts. Do not invent local statistics, named businesses, or company details.

## Positive solar reply template

Use the prospect's verified company and market. Replace the linked report URL and company details only after checking the original thread.

```text
{First name},

Thanks for the quick reply. I went ahead and put together a short version of the solar partner strategy we would build for {Company} in the {Market} market:

<a href="{report_url}">Solar partner strategy</a>

The model is straightforward. We map the complementary businesses in your area, recruit them into referral relationships, schedule and orchestrate promotions with them, and run the email, text, newsletter, and other campaigns that generate referrals.

That includes roofers, electricians, HVAC companies, remodelers, real estate professionals, property managers, builders, landscapers, security companies, insurance agents, homeowner associations, and other businesses already speaking with homeowners who may be a fit for solar.

Your team receives the opportunities, follows up, and closes the systems. You pay commissions on the sales that close.

We guarantee at least five referral partners in the first 90 days, plus a 5x return or you don't pay. On the call, we'll confirm your service area, walk through the first partner categories, and show you how we'd prioritize the initial campaign.

Let's get something on the books to talk it over and see if it's a good fit. Here is my calendar for a quick 15-minute call:

<a href="https://cal.com/usingaitoscale/aiintegraterz">cal.com/usingaitoscale/aiintegraterz</a>

Talk soon.

Justin
```

Use a descriptive hyperlink label such as `Solar partner strategy`, never a bare here.now URL in the email body. Keep the copy plain, direct, and niche-specific. Do not say “thank you for getting back to me,” apologize, or use Owned Audience language.

## Reply handling

- Positive interest: send the tailored report and booking CTA after QC approval.
- Former-employee referral: do not reply to the departing contact; record each named referral for separate outreach.
- OOO: do not reply unless the user explicitly asks for a follow-up action.
- Negative, hostile, or unsubscribe: follow the applicable suppression workflow.

## QC and sending

Before any send:

1. Verify the recipient, campaign, original reply, company, market, report URL, and sending account.
2. Run the final copy through `charm-qc-gate`.
3. Confirm all links use HTML anchors with readable labels.
4. Confirm the message has short paragraphs, no em dashes, no apologetic opener, and a direct booking CTA.
5. Send only after explicit user approval.
6. Verify the platform response confirms recipient, sender account, subject, thread, and message ID. A 200 response is evidence of accepted send, not inbox delivery.

## One-pager standard

The client-facing document should be a clean, readable HTML page with a white background, black text, restrained green/lime accents, larger typography, responsive layout, print styling, and a clear booking CTA. Publish it to here.now. Use an authenticated account publish when confirmed. If here.now reports `addedToProfile: false` or returns no permanent account evidence, report that plainly and do not call the URL permanent.

## Chat delivery rule

In Slack, every Markdown or text draft file must also be delivered directly in the chat. Never give only a local file path. If the draft is saved locally for records, paste the complete draft into the Slack response as well.

## Verification checklist

- [ ] Exact recipient and campaign verified from live Instantly data.
- [ ] Company and market taken from the actual thread or verified research.
- [ ] Report hyperlink uses a descriptive label.
- [ ] No Owned Audience language.
- [ ] No “thank you for getting back to me.”
- [ ] No send before explicit approval.
- [ ] QC gate passed.
- [ ] Send response includes message ID, sender account, recipient, and thread ID.
- [ ] Saved draft was also delivered inline in Slack.
- [ ] here.now permanence claim matches actual API evidence.
