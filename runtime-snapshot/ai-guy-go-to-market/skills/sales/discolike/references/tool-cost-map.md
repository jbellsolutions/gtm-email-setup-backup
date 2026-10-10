# DiscoLike MCP — Tool Cost Map

All costs are **estimates** until calibrated via `usage-statistics` after the first real call of each type.

## Free Tools (call as often as you like)

- `account-status`
- `usage-statistics`
- `usage`
- `count-matching-domains`
- `count-contacts`
- `match-contacts`
- `get-discogen-status`
- `cancel-discogen`
- `list-saved-queries`
- `save-mcp-query`
- `save-exclusion-list`
- `list-tags`
- `add-tags-to-query`
- `remove-tags-from-query`
- `get-domains-by-tags`
- `llm-providers`
- `search-providers`

## Paid Per Record (~$3/1000 records)

The big spenders. `discover-similar-companies` is THE list pull.

- `discover-similar-companies`
- `search-contacts`
- `bulk-match-contacts`
- `append-data`

## Paid Per Call — Cheap (~<$0.01 each)

Single-domain reads.

- `business-profile`
- `contact-lookup`
- `extract-website-text`
- `digital-footprint-score`
- `growth-metrics`
- `domain-redirects`
- `vendor-and-technology-data`
- `subsidiaries-and-parent-companies`

## Paid With Cache (free for ≤90d-old items)

- `run-discogen` — domains cached ≤90d are FREE
- `run-discogen-personas` — personas cached ≤90d are FREE

The cost gate can't see cache state, so always asks. The reason should note this.

## BYO External Cost

- `generate-contacts` — no DiscoLike billing; you pay your own LLM/search provider via BYOM/BYOS

## Pro Tier Only (requires $199/mo plan)

- `segment-domains` — will error on Starter

## Calibration Notes

Cost numbers are **estimates** until calibrated. After each first real paid call:
1. Call `usage-statistics` before and after
2. Diff = actual cost
3. Update estimates here and in memory
