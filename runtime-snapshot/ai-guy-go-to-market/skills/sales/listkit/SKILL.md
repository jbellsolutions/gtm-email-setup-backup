---
name: listkit
version: "1.0"
description: ListKit B2B lead generation platform — AI-powered list building, triple-verified leads, intent data, and cold email infrastructure. Covers list building workflow, credit economics, export process, automation strategies, and pricing.
---

# ListKit — B2B Lead Generation Platform

AI-powered B2B lead generation with triple-verified contacts, intent data, and optional fully-managed cold email infrastructure.

## Platform Architecture

```
┌─────────────────────────────────────────────────────┐
│                    LISTKIT ECOSYSTEM                 │
├─────────────────┬───────────────┬───────────────────┤
│   PLG (Self)    │  DFY Service  │  DFY Managed      │
│   ListKit App   │  + Sending    │  Fully Managed    │
├─────────────────┼───────────────┼───────────────────┤
│ You source      │ ListKit builds│ ListKit does      │
│ leads, export   │ infra, you    │ it all: leads,    │
│ CSV, handle     │ manage        │ campaigns,        │
│ outreach        │ campaigns     │ sending, optimize │
└─────────────────┴───────────────┴───────────────────┘
```

**Core platform URL:** `app.listkit.io`
**Sending tool:** `send.listkit.io`
**Documentation:** `docs.listkit.io/en/`
**Login:** `next.listkit.io/login`

## Auth & Login

### Login Methods
- **Google OAuth** — triggers 2FA device prompt. **DOES NOT WORK on cloud browsers** — the device prompt never registers.
- Apple OAuth
- LinkedIn OAuth
- **Email/password ★** — the only reliable method for automation

### Automation Strategy
**Use email/password login.** Google OAuth 2FA device prompts are fundamentally incompatible with cloud browser instances — the approval never propagates to the browser session.

1. **Browser Use Cloud Profile** — Create a profile, login with email/password once, profile persists cookies across sessions
2. **Credentials — ⚠️ MAY BE STALE:** Email `justin@usingaitoscale.com`, Password `UsingAITOScale2o24$`. As of June 2026, ListKit migrated to a new authentication provider and these credentials may be rejected with "Password or email address is incorrect." If so, the user must reset via "Forgot Password" on the login page before email/password login works again. Google OAuth is the fallback (see pitfalls).
3. **Active profile:** `a59f74a1-4ed9-435c-b4c9-06a1a97a0a26`
4. **Active session:** `e0bab6f5-0eb7-419b-84c3-cedd1a1206ce` (keep_alive=True)

```python
from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode

client = BrowserUse(api_key="[REDACTED]")
session = client.sessions.create(
    model=BuModel.claude_sonnet_4_6,
    proxy_country_code=ProxyCountryCode.us,
    keep_alive=True,
    profile_id='a59f74a1-4ed9-435c-b4c9-06a1a97a0a26',
)

# Login with email/password — NOT Google OAuth
result = client.run(
    session_id=str(session.id),
    task="""Go to https://next.listkit.io/login
In the email textbox, type: justin@usingaitoscale.com
In the password textbox, type: UsingAITOScale2o24$
Click the Login button.
Navigate to the dashboard.""",
)

# SESSION PERSISTED — reuse session.id for future tasks
```
# Step 3: Login (requires user for Google 2FA)
result = client.run(
    session_id=str(session.id),
    task="Go to https://next.listkit.io/login, click 'Log In with Google', complete sign-in",
    max_steps=15,
)

# Step 4: SESSION IS NOW PERSISTED — reuse session.id for future tasks
# The profile stores cookies/localStorage inside the session
# User will need 2FA approval once per new session (Google per-fingerprint policy)

# Step 5: Run tasks on the authenticated session
result = client.run(
    session_id=str(session.id),
    task="Go to https://app.listkit.io, use AI Company Search to find 'manufacturing software vendors helping automotive suppliers', extract all results",
)

# Step 6: Stop session when done (profile survives for next session)
client.sessions.stop(session_id=str(session.id))
```

## Credits System

Three credit types consumed on export:

| Credit Type | Cost | Purpose |
|-------------|------|---------|
| **Email Credit** | 1 credit | Export a business email |
| **Verification Credit** | +1 credit | Triple-verify the email on export |
| **Phone Credit** | +5 credits | Export a mobile phone number |

**Total for one triple-verified email:** 2 credits (1 email + 1 verify)
**Total for email + phone:** 7 credits (1 email + 1 verify + 5 phone)

Credits are purchased in-app: `app.listkit.io` → Settings → Credit Usage → "Get credits now"

## Pricing Tiers (Self-Serve PLG)

All plans include: Unlimited Users, AI Company Search, Triple-Verification, Intent Data, Data Enrichment, CRM Integrations.

| Plan | Monthly | Yearly (15% off) | Credits |
|------|---------|-------------------|---------|
| **Pro** | $97/mo | $82/mo | 24,000 |
| **Scale** ★ | $297/mo | $252/mo | 120,000 |
| **Ultimate** | $597/mo | $507/mo | 600,000 |
| **Enterprise** | Custom | Custom | Custom |

**Credit cost per lead:** Pro $0.0034/credit, Scale $0.0021/credit, Ultimate $0.00085/credit

---

## List Building: AI Company Search

### Step 0: Generate Keyword Variations (DO THIS FIRST)

Before entering anything into ListKit, generate 5-8 semantically equivalent keyword phrases. These are NOT word fragments — they're alternative ways to describe the SAME business category.

**CRITICAL RULE: Variations must mean the same thing, not be subsets of the phrase.**

| ICP | ✅ Good Variations | ❌ Bad (word fragments — different meaning) |
|-----|-------------------|---------------------------------------------|
| "merchant cash advance lender" | business loan provider, business lending company, revenue-based financing, MCA provider, small business funder, alternative business lender, working capital lender | "merchant", "cash advance", "lender" (these are different industries or too broad) |
| "roofing contractor" | roofing company, roof repair business, roof installation service, residential roofing, commercial roofer | "roofing", "contractor", "roof" (too broad or different category) |
| "HVAC service provider" | heating and cooling company, HVAC contractor, air conditioning service, furnace repair, HVAC installation | "HVAC", "service", "heating" (fragments, not equivalent) |
| "digital marketing agency for dentists" | dental marketing agency, dentist advertising company, dental practice marketing, dental SEO agency, dentist lead generation | "marketing", "digital", "dentist" (each means something completely different alone) |

**Principle: If you wouldn't use the word by itself to find the same companies, don't use it as a variation.**

### Workflow
1. **Generate keyword variations** using the rule above (5-8 semantically equivalent phrases)
2. Enter the first variation into ListKit's AI Company Search
3. Review results, then test 2-3 more variations to capture different slices of the market
4. Combine or refine with filters across all successful prompts
5. Click "People" to see individual contacts within matched companies
6. Export when satisfied

### AI Prompt Principles (CRITICAL)

| Rule | Good | Bad |
|------|------|-----|
| **Be specific** | "Marketing agencies helping dentists get patients" | "Marketing companies" |
| **Keep it short** | 5-9 words sweet spot | Long paragraphs |
| **Match market language** | "Software" not "SaaS" | Jargon |
| **Test variations** | 3-5 semantically equivalent prompts (see Step 0) | One prompt only |
| **Formula** | `Company Type + Service/Product + Target Market (+ Outcome)` | Random words |
| **No filters in prompt** | Keep locations/funding/titles out | "Series A fintech in NYC" |
| **Don't use word fragments** | Full phrase equivalents only | Individual words from the ICP |

**Prompt example formula:**
```
[Company Type] + [Service/Product] + [Target Market]
→ "Manufacturing software vendors helping automotive suppliers"
→ "Recruitment agencies specializing in healthcare staffing"
→ "Digital marketing agencies selling Facebook ads to real estate"
```

**Full keyword variation workflow example:**

ICP: "merchant cash advance lender"

Step 0 — generate 5-8 semantically equivalent variations:
1. "business loan provider"
2. "business lending company"  
3. "revenue-based financing company"
4. "MCA provider"
5. "small business funder"
6. "alternative business lender"
7. "working capital lender"

Step 1 — test in ListKit AI Company Search:
- "merchant cash advance lender" → check result count
- "business loan provider" → check result count
- "revenue-based financing company" → check result count

Step 2 — pick top 2-3 performers and refine with filters
Step 3 — switch to People view and scrape

A **Custom GPT Prompt Builder** is available that takes a company URL and generates 5 optimized prompts.

### Search Field

The homepage has an AI search textbox where you type natural language queries. Example prompts from the UI:
- "Cold email lead generation agencies"
- "Fintech companies helping banks automate workflows"
- "Law firms specializing in personal injury cases"
- "Consulting firms advising C-suite executives"

---

## Filters Reference

### AI-Powered Company Filters

| Filter | Options |
|--------|---------|
| **AI Score** | High, Medium, Low |
| **Target Audience** | SMB, Mid-Market, Enterprise, Developers, Agencies, etc. |
| **Business Model** | SaaS, Agency, Marketplace, Ecommerce, Services, Hybrid |
| **Revenue Model** | Subscription, Usage-based, One-time, Commission, Retainer, Freemium |
| **Growth Stage** | Early, Growth, Scaling, Mature, Series A, Public, Acquired |
| **Vertical** | Software, Healthcare, Financial Services, etc. |
| **Micro Industry** | CRM, Marketing Automation, Telehealth, DTC Brands, etc. |

### Standard Company Filters

| Filter | Description |
|--------|-------------|
| **Funding** | Type, range, latest round date |
| **Industry** | Include/exclude specific industries |
| **Technologies** | Target companies using specific tools (HubSpot, Shopify, Salesforce, etc.) |
| **Employee Range** | 1-50, mid-market, 500+ enterprise |
| **Include/Exclude Companies** | Manual domain control |
| **Hiring Status** | Filter by companies actively hiring |
| **Company Location** | Country, State, Region, City |

### People Filters

| Filter | Description |
|--------|-------------|
| **Job Titles** | Contains (partial match) or Exact Match; can exclude titles |
| **Keywords** | Refine niche ("SaaS", "Construction", "Real estate") |
| **People Location** | Country, State, City (where the person lives) |

**⚠️ Important:** Use Company Location (not People Location) in most cases. Filtering both can exclude decision-makers who work abroad.

### Pre-Built Filters
Ready-made filters created by ListKit team — best for new users, quick lists, and testing ideas fast.

---

## Intent Data (AI Data Stream)

### Overview
Shows companies actively researching a topic in the last 30 days. **U.S.-only** currently.

### Signal Sources
- Google searches
- Video views
- LinkedIn group joins
- + more behavioral signals

**Scale:** 21 billion daily buying signals tracked. Dataset updates every 24 hours.

### Workflow
1. Log in → Click "AI Data Stream" in top nav
2. Add topics (manual from 20,000+ library OR let AI pick based on what you sell)
3. ListKit pulls all companies showing intent in last 30 days
4. Click "People" to view individual leads within matched companies
5. Narrow with filters (Job Title, Department, Seniority, Location, Industry, Employee Count)
6. Export when ready

**Key insight:** Intent signals are a prioritization layer, not a guarantee. Use to warm-target accounts already in buying mindset.

---

## Triple Verification Engine

### Verification Process (on export)
1. Email syntax and formatting check
2. Domain existence and mail server configuration check
3. Mailbox existence validation (without sending test emails)

### Result Labels

| Label | Meaning | Action |
|-------|---------|--------|
| **Good** | Confirmed deliverable | Safe to use |
| **Bad** | Not deliverable | NEVER use — will bounce |
| **Risky** | Catchall domain | Separate campaign or test first |

### Bounce Rate Expectations
- **2-4% total bounce rate is normal** even with Triple-Verified leads
- Mostly soft bounces (temporary: downtime, full inbox, greylisting)
- Hard bounces rare (invalid address, closed account, non-existent domain)
- Remove hard bounces immediately; soft bounces often resolve
- Bounces happen because verification is a snapshot — employees leave, servers change

**Database stats:** 731M+ triple-verified contacts, 5M emails verified monthly

---

## Export Process

### Steps
1. Apply filters, review lead counts (Companies + People views)
2. Click "Checkout" (top-right)
3. Select export fields
4. Download CSV

### Export Fields & Credit Costs

**Paid Fields (consume credits):**
| Field | Credits |
|-------|---------|
| Business Email | 1 credit |
| Business Email Triple Verification | +1 credit (2 total) |
| Mobile Phone Number | +5 credits |

**Free Fields (automatic, no credits):**
- Company name & domain
- Industry
- Employee count
- Company location
- First & last name
- Job title
- Lead location

**Optional Paid Fields:**
- Company address
- Company LinkedIn URL
- Tech stack
- Funding info
- Personal LinkedIn URL
- Personal email
- Triple verification for personal email

### Export Settings
- **Max people per company** — Limits leads per company (e.g., 3 = max 3 per company)
- **Lead quantity** — Total leads to export
- **Exclusion options (recommended):** Exclude emails from order history, Exclude Do Not Call numbers

---

## DFY (Done-For-You) Cold Email Service

### What ListKit Handles
- Setup custom inboxes/domains (private infrastructure — not Google/Outlook)
- New targeted lead lists monthly
- Write & optimize campaigns monthly
- Manage deliverability & performance

### What You Handle
- Approve messaging/strategy
- Respond to leads
- Take sales calls
- Sign clients

### Launch Timeline (3 weeks to live)
- **Week 1:** Script writing, domain & inbox setup, script approvals
- **Week 2:** Inbox warmup, deliverability testing, 3-step sequence crafting
- **Week 3:** First campaign launch & monitoring
- **Week 4+:** Continuous optimization, new campaigns, monthly reporting

### Pricing (all include $1,500 one-time setup)

| Plan | Domains | Leads/mo | Volume/mo | Inboxes | 1st Month | Ongoing/mo |
|------|---------|----------|-----------|---------|-----------|------------|
| **Gold** | 30 ($300/yr) | 10,000 | 30,000 | 60 | $3,180 | $1,680 |
| **Platinum** | 45 ($450/yr) | 15,000 | 45,000 | 90 | $3,800 | $2,300 |
| **Custom Base** | 75 ($750/yr) | 25,000 | 75,000 | 150 | $5,340 | $3,840 |
| **Custom Scale** | 105 ($1,050/yr) | 35,000 | 105,000 | 210 | $7,260 | $5,760 |
| **Custom Enterprise** | 210 ($2,100/yr) | 70,000 | 210,000 | 420 | $11,100 | $9,600 |

All include: Private infrastructure, 24/7 AI deliverability monitoring, sending tool, phone enrichment, AI lead finder/verification/personalization.
**Quarterly billing saves 17%.**

---

## DFY Managed (Full Service)

ListKit handles EVERYTHING — lead sourcing, campaign creation, messaging, sending, deliverability, optimization.

### Client's Only 3 Responsibilities
1. Reply to warm leads (within 5 min = up to 21× higher conversion)
2. Book and run sales calls
3. Keep ListKit informed (offer changes, ICP changes, sales feedback)

### Timeline
- **Month 1:** Setup + warm-up + ramp-up
- **Months 2-3:** Learning + refining (data-driven iteration)
- **Months 4-6:** Compounding results (scaling)
- **Month 7+:** Predictable pipeline ("Think SEO, not ads")

### The 48-Hour Rule
- Campaign audit completed → findings sent → 48-hour response window
- No response → campaign launches as planned
- Non-critical edits → applied next cycle
- Critical issues → fixed immediately

---

## Dashboard Layout (Real Environment)

### Account
- **Name:** Justin Bellware
- **Plan:** Universal Access Plan
- **Credits:** 2,000 credits (check top-right or settings)
- **URL:** `next.listkit.io/b2b` (Companies search)
- **Version:** v.2.27.2026.0223

### Top Navigation
- Companies · People · Email Verification · Enrichment · Workflows · Order History · Email Engine (beta)

### Filter Panel (left sidebar)
| Section | Filters |
|---------|---------|
| **Pre-Built Filters** | Ready-made templates |
| **AI Data Stream** | Intent-based topic filtering |
| **AI Company Search** | Natural language ICP prompts (NEW!) |
| **People** | Job Title, Keywords, Gender, Age Range, Income Range, Net Worth, Seniority, Department, AI Job Titles Search |
| **People Location** | Country, City, State |
| **Company** | Funding, Industry, Keywords, Technology, Employees, SIC Code, Company Name, Include/Exclude, AI Score |
| **Target Audience** | Business Model, Revenue Model, Growth Stage, Revenue Range, Vertical, Micro Industry, Hiring |
| **Company Location** | Country, City, Region, State |

### Footer
- Chat support bubble (bottom-right)
- No search results until filters applied + "Search for Companies" clicked

### For List Building (Scraping Lists)

ListKit is an SPA at `app.listkit.io`. Post-login workflow:

1. Navigate to `app.listkit.io`
2. Use AI Company Search (type prompt, AI generates filters)
3. Apply additional filters as needed
4. Navigate to "People" view
5. Scrape results using `browser_console` JavaScript extraction
6. Export via CSV download or scrape inline

### For Result Scraping (Post-List Build)

Once a list is built and results are displayed:

```javascript
// Extract leads from the people table
const rows = document.querySelectorAll('table tbody tr');
const leads = [];
rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length > 0) {
        leads.push({
            name: cells[0]?.textContent?.trim(),
            title: cells[1]?.textContent?.trim(),
            company: cells[2]?.textContent?.trim(),
            email: cells[3]?.textContent?.trim(),
            phone: cells[4]?.textContent?.trim(),
            location: cells[5]?.textContent?.trim(),
        });
    }
});
return leads;
```

### Credential Storage

Google OAuth credentials:
- Email: `justin@usingaitoscale.com`
- Password: `UsingAITOScale2o24$`
- **2FA required** — Google device prompt (iPhone 16 Pro Max, YouTube app)
- Store in Hermes secrets or env vars for automation

---

## Key URLs

| Resource | URL |
|----------|-----|
| Homepage | `https://www.listkit.io/` |
| App Dashboard | `https://app.listkit.io/` |
| Login | `https://next.listkit.io/login` |
| Sending Tool | `https://send.listkit.io/` |
| Documentation | `https://docs.listkit.io/en/` |
| Pricing | `https://www.listkit.io/pricing` |
| Triple-Verified Leads | `https://www.listkit.io/triple-verified-leads` |
| Intent Data | `https://www.listkit.io/unlimited-intent-data` |
| Cold Email Setup | `https://www.listkit.io/cold-email-setup` |
| Phone Numbers | `https://www.listkit.io/phone-numbers` |

---

## Pitfalls & Gotchas

1. **⚠️ Auth Provider Migration (June 2026)** — ListKit migrated to a new authentication provider. Existing email/password credentials may be rejected with "Password or email address is incorrect" and a banner reading "We have migrated to a new authentication provider. If you use email/password as your login method, please reset your password by clicking on Forgot Password." User must reset password before email/password login works again. Google OAuth continues to work but requires 2FA device approval (see pitfall #2).
2. **Google 2FA breaks headless automation** — Google OAuth requires device approval (YouTube app on iPhone 16 Pro Max). Each new Browser Use Cloud session = new fingerprint = fresh 2FA, even with correct credentials. Strategy: create a `keep_alive=True` session ONCE with user present for 2FA, then reuse `session.id` for subsequent `client.run()` calls. Sessions expire after 4 hours max or 15 min inactivity. Browser Use Cloud profiles persist cookies within a session but don't carry 2FA approval across sessions. On session timeout, user must re-approve 2FA.
2. **Browser Use Cloud 502 Bad Gateway** — When session times out, subsequent `client.run()` calls return 502. Catch `BrowserUseError`, check `client.sessions.get()`, create new session + profile if needed.
3. **Credits deducted on export, not on search** — Building and refining lists is free; credits only consumed when you export/download.
4. **Company Location vs People Location** — Filtering on both can exclude valid leads (decision-makers working abroad). Prefer Company Location.
5. **Prompt wording matters significantly** — "Marketing companies selling Facebook ads" vs "Marketing agencies selling Meta ads" = 2,400 vs 3,100 companies. Test 3-5 variations.
6. **Triple-verified ≠ zero bounce** — Expect 2-4% bounce rate. Verification is a snapshot, not a guarantee.
7. **Intent Data is US-only** — No international intent signals.
8. **DFY requires Porkbun domain purchases separately** — Domains not included in DFY pricing. $10/yr per domain from Porkbun.
9. **The site is an SPA** — Product pages route client-side. Use Browser Use Cloud agent task descriptions, not direct URL navigation for internal pages.
12. **ListKit is NOT an API platform** — No public API. All automation must use browser automation (Browser Use Cloud recommended for the authenticated SPA).
13. **Keep session alive** — Inactivity timeout can kill the session. Keep `keep_alive=True`, poll regularly, and reuse `session.id`.
14. **SPA validation errors are invisible to the accessibility tree** — React/Next.js form validation errors (red error text, migration banners) often do NOT appear in `browser_snapshot` output. When form submissions silently fail, use `browser_vision` to visually inspect the page for error messages, banners, or CAPTCHAs that the DOM snapshot misses.

---

## Integration with legacy email platform

ListKit exports → legacy email platform imports. The typical workflow:
1. Build list in ListKit (AI Company Search)
2. Triple-verify and export CSV
3. Clean CSV (remove Bad/Risky, keep Good)
4. Import into legacy email platform campaign via `mcp_legacy email platform_add_leads_to_campaign`

This pairs with the `legacy email platform-cold-email` skill for end-to-end cold email pipeline.
