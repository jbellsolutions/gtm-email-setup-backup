---
name: discolike-design
description: Design a DiscoLike query without pulling. Use when the user says "design a query", "find companies that...", "build me an ICP search for...", or hands you a description and wants a structured query back. Uses only FREE tools (counts, saved-query CRUD). Never pulls a list — that's discolike-pull.
---

# DiscoLike — Design

Convert a user's plain-English ICP brief into a saved DiscoLike query with a projected pull cost. Stop there. The pull is a separate step.

## Sequence

### 1. Gather the ICP brief
Ask the user (or extract from their message):
- **Target description** — who, in plain English?
- **Geography** — country, state, region?
- **Size constraints** — small companies only? mid-market? big enterprises?
- **Must-have signals** — specific keywords, tech stack, social presence?
- **Exclusions** — what's a known false-positive pattern?
- **Anchor domains** — any companies they already know fit the profile?

### 2. Draft the query
Read `references/filter-grammar.md` (in the discolike skill) for the full filter syntax.

Key filter fields:
- `phrase_match` — Google-style: bare words = OR, `+word` forces AND, `"exact phrase"`, up to 20 phrases
- `country` — ISO-3166-1 alpha-2 (e.g. `US`, `GB`) or region codes (`ANZ`, `APAC`)
- `state` — ISO-3166-2 or full state name
- `employee_range` — `1-10`, `11-50`, `51-200`, `201-500`, `501-1k`, `1k-5k`, `5k-10k`, `10k+`
- `min_digital_footprint` / `max_digital_footprint` — integer 0-800, SSL-cert-derived size signal
- `category` — industry category
- `tech_stack` — vendor domains (e.g. `hubspot.com`, `gohighlevel.com`)
- `negate_*` variants for all of the above

### 3. Count-matching-domains (FREE, iterate)
```
mcp__discolike__count-matching-domains
  phrase_match: <draft>
  country: <draft>
  ... other filters
```
Iterate 2-3 times tightening filters until the count is in the right range.

### 4. Save the query (FREE)
```
mcp__discolike__save-mcp-query
  query_name: "<descriptive name>"
  phrase_match: <final>
  country: <final>
  ...
```
Returns a `query_id`.

### 5. Present results
Show:
- The final query JSON
- The saved query_id
- The matching domain count
- Projected pull cost:
  | max_records | est cost |
  |-------------|----------|
  | 100 | ~$0.30 |
  | 1,000 | ~$3 |
  | 10,000 | ~$30 |
  | Full count | ~$X |
- Reasoning: which filters tightened, which loosened, why

### 6. Hand off
Suggest:
- `discolike-validate <query_id>` to see fit % on a 100-sample (~$0.30-$2, recommended)
- `discolike-pull <query_id> max_records=50` to skip validate and pull a small confirming sample

## Gotchas
- **Anchor domains are critical** — 3-5 good fit examples make the lookalike vector much better
- **`+forced` keywords are cheap insurance** — adding a single mandatory word can drop 30-50% of noise
- **Watch for "too narrow"** — if count drops under ~100, over-constraining. Loosen something.
- **Don't auto-pull.** Route to `discolike-pull` for the gated path.