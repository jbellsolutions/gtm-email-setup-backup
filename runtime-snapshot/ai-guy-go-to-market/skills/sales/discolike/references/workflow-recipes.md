# DiscoLike — Workflow Recipes

Worked patterns. Each recipe = goal → MCP call sequence → cost class → known gotchas.

## R1 — Find lookalike companies from seed domains

**Goal:** "Show me 20 B2B SaaS companies like Figma and Miro in US/UK."

```
mcp__discolike__discover-similar-companies
  domain: ["figma.com", "miro.com"]
  country: ["US", "GB"]
  employee_range: "50-200"
  max_records: 20
```
- **Cost:** paid_per_record (~$0.06)
- **Gate:** use clarify() before calling

## R2 — Natural-language ICP → company list

**Goal:** Describe the ICP in plain English; let the platform extract filters.

```
mcp__discolike__discover-similar-companies
  icp_prompt: "mid-market e-commerce platforms in Europe with headless or composable storefronts"
  max_records: 50
```
- **Cost:** paid_per_record (~$0.15)
- **Gotcha:** Less control than R1. Use after walkthrough proves the count looks right.

## R3 — Free contact name lookup

**Goal:** "Is there a John Smith at Salesforce?"

```
mcp__discolike__match-contacts
  name: "John Smith"
  company_name: "Salesforce"
```
- **Cost:** FREE. Use liberally before any paid enrichment.

## R4 — Full company profile

**Goal:** Everything DiscoLike knows about stripe.com.

```
mcp__discolike__business-profile
  domain: "stripe.com"
```
- **Cost:** paid_per_call_cheap. Single-domain read.

## R5 — Find decision-makers across target accounts

**Goal:** VP+/Director Marketing at 5 named accounts with validated emails.

```
mcp__discolike__search-contacts
  domain: ["hubspot.com","mailchimp.com","klaviyo.com","brevo.com","customer.io"]
  seniority: "vp"
  department: "Marketing"
  has_email: true
  email_validated: true
  max_companies: 5
  results_by_company: 5
```
- **Cost:** paid_per_record. Gate with clarify().

## R6 — Detect tech stack

**Goal:** What vendors is notion.so using?

```
mcp__discolike__vendor-and-technology-data
  domain: "notion.so"
  match: "client"
```
- **Cost:** paid_per_call_cheap
- **Why better than BuiltWith:** keyed off SSL certs, not page scrapes. GoHighLevel detection alone covers ~535K accounts.

## R7 — Extract website text

**Goal:** Read linear.app's homepage text.

```
mcp__discolike__extract-website-text
  domain: "linear.app"
```
- **Cost:** paid_per_call_cheap. FREE if discovered within last 90 days.

## R8 — Find redirect mappings

**Goal:** Where does heroku.com redirect to?

```
mcp__discolike__domain-redirects
  domain: "heroku.com"
  match: "from"
```
- `match: "to"` to find domains redirecting INTO yours.

## R9 — Bulk-enrich a domain list

**Goal:** Add bizdata + growth to a fintech short-list.

```
mcp__discolike__append-data
  domains: ["stripe.com","plaid.com","brex.com","ramp.com","mercury.com"]
  dataset: ["bizdata", "growth"]
```
- **Cost:** paid_per_record. Cap: 100 domains/call.

## R10 — Organize saved queries with tags

**Goal:** Group saved queries by campaign.

```
mcp__discolike__add-tags-to-query
  query_id: "abc123"
  tags: ["fintech", "outbound-q2"]
```
- **Cost:** FREE. Then `get-domains-by-tags` (free) pulls all domains across tagged queries.

## R11 — DiscoGen synchronous (≤10 domains)

**Goal:** Ask a structured question of ≤10 companies.

```
mcp__discolike__run-discogen
  query: "Does this company offer a free trial? What is their pricing model?"
  domains: ["notion.so","linear.app","clickup.com","monday.com","asana.com"]
  context_mode: "website"
  web_search: false
```
- **Cost:** paid_with_cache. ≤10 domains returns inline; >10 returns a task_id — poll with `get-discogen-status` (FREE).

## R12 — DiscoGen asynchronous (≥200 domains)

```
mcp__discolike__run-discogen
  query: "Is this company currently hiring for AI/ML roles?"
  domains: [... 200 ...]
  context_mode: "domain"
  web_search: true
```
- **Cost:** paid_with_cache + Serper search cost
- `context_mode: "domain"` is the cheap option (name only, no scrape).

## R13 — Qualify contacts as decision-makers

```
mcp__discolike__run-discogen-personas
  query: "Based on this person's title and seniority, are they likely a decision-maker for developer tools?"
  persona_ids: [12345, 12346, 12347]
  context_mode: "company"
```
- **Cost:** paid_with_cache

## R14 — Account status + usage check

```
mcp__discolike__account-status
mcp__discolike__usage-statistics
```
- **Cost:** FREE. Run at the start of every session.

## R15 — Validate before pulling (the skill pattern)

**Goal:** Before pulling 5,000 MCA brokers, confirm the query is tight.

1. `count-matching-domains` (FREE) → confirm size is in expected range
2. Pick 100 random domains from the saved query result
3. `run-discogen` with yes/no/partial prompt + 100 domains + `context_mode: "website"`
4. Parse: count yes / partial / no. Read no-reasoning for false-positive themes
5. Tighten `phrase_match` if needed and re-validate
6. Only when fit % is acceptable, run the real `discover-similar-companies` pull

**Cost:** paid_with_cache. Domain list capped at 100 — `run-discogen` itself accepts up to 10,000.
