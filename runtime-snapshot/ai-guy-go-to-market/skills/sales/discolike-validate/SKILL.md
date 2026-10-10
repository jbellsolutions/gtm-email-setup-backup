---
name: discolike-validate
description: Validate the fit % of a DiscoLike query against a 100-domain sample before any real pull. Use when the user says "validate this query", "check fit before pulling", "is this query good?", or wants to sanity-check before spending real money. Uses run-discogen (paid_with_cache) — costs ~$0.30-$2. MUST use clarify() to get user approval before any paid call.
---

# DiscoLike — Validate

Run a fit-check on a saved query's first 100 domains. The user sees yes/no/partial per domain + reasoning, computes precision, and decides whether to refine further or proceed to pull.

## Why validate separately
Validate spends a small amount ($0.30-$2 typically) to TELL YOU IF SPENDING MORE IS WORTH IT. It's the cost discipline step. Skipping it is the #1 way to get a surprise bill on a wrong list.

## Sequence

### 1. Confirm input
The user needs a `query_id` from `discolike-design` or `discolike-walkthrough`. If not, route them to one of those first.

Ask: **"What's the strict ICP definition?"** Specificity matters — "merchant cash advance brokers" is OK; "small US merchant cash advance brokers (not the lenders themselves, the appointment-setting middlemen)" is better.

### 2. Get the first 100 domains
First, list the saved query to get its domain results:
```
mcp__discolike__list-saved-queries
```
Extract up to 100 domains from the query result. This is FREE.

### 3. Gate the paid call
Before calling `run-discogen`, use `clarify()` to get explicit user approval:

> "Ready to validate. This will call run-discogen on 100 domains at ~$0.10/domain for NEW domains (free for any cached ≤90 days). Estimated cost: ~$0.30-$10 depending on cache state. Proceed?"

If user says no → stop. Don't retry, don't reduce. They said no.

### 4. Run discogen (PAID, gated)
If approved:
```
mcp__discolike__run-discogen
  query: "Is this company a <ICP definition>? Answer with one of: yes / partial / no. Then one sentence explaining your reasoning. Then your confidence: high / medium / low."
  domains: [<100 domains>]
  context_mode: "website"     # "domain" is cheaper but less accurate
  web_search: false           # only if user explicitly needs it (adds Serper cost)
```
Default `context_mode`: `domain` (cheapest). Use `website` only if user wants high accuracy.
`web_search`: false unless the user explicitly needs it.

### 5. Present the report
Parse results into:
- **Fit %:** X yes / Y partial / Z no
- **Confidence histogram:** high vs medium vs low
- **Top 5 themes in "no" reasoning** (filter-tightening targets)
- **Suggested refinements:**
  - "Add `+keyword` because 12 of 53 no-fits had X in their description"
  - "Add `negate_category` because 8 no-fits were in industry Y"

### 6. Decide next step
| Fit % | Suggest |
|-------|---------|
| ≥80% high confidence | Proceed to `discolike-pull` |
| 50-79% | Tighten filters via `discolike-design` then re-validate |
| <50% | Significant filter rework needed |

### 7. Calibrate cost
Call `mcp__discolike__usage-statistics` before and after to compute actual cost. Update memory with the calibrated per-domain cost for future estimates.

## Hard Caps
- **Cap the domain list at 100** in the discogen call, regardless of query size. `run-discogen` accepts up to 10,000 — that's a foot-gun.
- **One clarify() gate per validate run.** If the user rejects, abort gracefully.
- **Don't auto-chain into pull.** The user always sees the report first.