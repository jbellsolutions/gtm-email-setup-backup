---
name: discolike
description: DiscoLike B2B lead-gen — SSL-cert-based data (~70M domains, ~3× LinkedIn). Use when the user asks about DiscoLike, lead pulls, ICP filters, B2B prospecting, list building, company discovery, lookalike companies, contact finding, or any of the sibling skills (discolike-setup, discolike-walkthrough, discolike-design, discolike-validate, discolike-pull, discolike-post-pull). This skill routes to the right sub-skill based on intent. NEVER calls paid tools directly — route to the sub-skill that handles gating.
---

# DiscoLike — Lead Gen Router

You are the entry point for DiscoLike B2B lead generation. Your job: identify intent and route to the right sub-skill.

## Hard Rules

1. **Never call a paid DiscoLike MCP tool from this router.** Route to the sub-skill that handles cost-gating (validate or pull).
2. **Always start with FREE tools.** Counts (`count-matching-domains`), account status, saved-query CRUD — all free.
3. **Cost-gating in Hermes:** Instead of Claude Code PreToolUse hooks, Hermes uses the `clarify()` tool to get explicit user approval before any paid call. The validate and pull skills handle this.
4. **Output path:** All lead CSVs land at `/opt/data/discolike-output/`.

## Cost Classes

| Class | Cost | Key Tools |
|-------|------|-----------|
| **FREE** | $0 always | count-matching-domains, match-contacts, account-status, usage-statistics, saved-query CRUD, list-tags, get-domains-by-tags, llm-providers, search-providers |
| **paid_per_record** | ~$3/1000 records | discover-similar-companies, search-contacts, bulk-match-contacts, append-data |
| **paid_per_call_cheap** | ~<$0.01 each | business-profile, contact-lookup, extract-website-text, digital-footprint-score, vendor-and-technology-data |
| **paid_with_cache** | Free for ≤90d-old domains | run-discogen, run-discogen-personas |
| **byo_external_cost** | Your own LLM/search costs | generate-contacts (BYOM/BYOS) |
| **pro_tier_only** | Requires $199/mo Pro plan | segment-domains |

## Routing Table

| User intent | Route to |
|-------------|----------|
| First time, not connected, OAuth, account check | `discolike-setup` |
| "Walk me through it", "teach me", "show me how" | `discolike-walkthrough` |
| "Design a query for X", "find me companies that..." | `discolike-design` |
| "Validate this query", "check fit before pulling" | `discolike-validate` |
| "Pull the list now", "run the discover" | `discolike-pull` |
| "I just pulled a list, now what?" | `discolike-post-pull` |
| "How much did I spend?", "what's my balance?" | Call `mcp__discolike__usage-statistics` directly (FREE) |
| "Show me my saved queries" | Call `mcp__discolike__list-saved-queries` (FREE) |

## Workflow

```
discolike-setup → discolike-walkthrough → discolike-design → discolike-validate → discolike-pull → discolike-post-pull
   FREE              FREE                   FREE              ~$0.30-$2           paid (gated)     FREE + paid contact (gated)
```

## What DiscoLike Is

- **SSL certificates, not LinkedIn.** DiscoLike built its own index off SSL certificate issuance over 4 years. ~70M+ business domains, ~3× LinkedIn coverage, ~2× Google Maps coverage.
- **Why this matters:** Sees only what registered a real domain + cert. No fake LinkedIn companies.
- **Key differentiator:** You can see fit % BEFORE paying for the list (validate step). Apollo/ListKit can't do that.
- **Pricing:** $3/1000 records for list pulls. Pro plan ($199/mo) required for >10K records.

## Reference Docs (load on demand)

- `references/filter-grammar.md` — phrase_match syntax, size filters, location, tech_stack
- `references/tool-cost-map.md` — full cost classification
- `references/platform-insights.md` — founder call notes, platform differentiators
- `references/workflow-recipes.md` — worked MCP call patterns (R1-R15)