---
name: discolike-post-pull
description: Post-process a DiscoLike pull. Use after discolike-pull completes (auto-chain here), or when the user says "I just pulled a list, now what?", "dedup this", "export to CSV", "analyze the pull quality". Deduplicates against saved exclusion lists, emits clean CSV at /opt/data/discolike-output/, optionally chains to contact discovery, and refeeds quality findings back into the next design cycle.
---

# DiscoLike — Post-Pull

The pull is done, money is spent. Now make sure the result is usable AND the next pull is better.

## Sequence

### 1. Locate the output CSV
The pull skill writes to `/opt/data/discolike-output/<query_id>-<YYYYMMDD-HHMMSS>.csv`. If there's no CSV because the pull failed, route back to pull.

### 2. Dedup against exclusions (FREE)
Check for exclusion list tags:
```
mcp__discolike__list-tags
```
If any exclusion-list tags exist:
```
mcp__discolike__get-domains-by-tags
  tags: [<exclusion tags>]
  match: "any"
```
Drop those domains from the CSV. Report how many were removed.

### 3. Emit clean export
- Default: write a clean CSV at the same path with `-deduped.csv` suffix
- Columns: domain, name, country, state, employee_range, digital_footprint, social_urls, description, industry_groups
- If contacts were pulled too: also include name, title, email, email_validated, linkedin

### 4. Optionally chain to contacts
If the user wants contacts and the pull was domains-only:
- `match-contacts` (free) if user has names already
- `search-contacts` (paid, gate with `clarify()`) for bulk
- `generate-contacts` via BYOM/BYOS if Grok + Serper configured (no DiscoLike billing)

Use `clarify()` to get approval for any paid contact path before proceeding.

### 5. Calibrate cost (FREE)
```
mcp__discolike__usage-statistics
```
Compare month-to-date spend now vs. before the pull. Compute actual cost. Report to the user.

### 6. Refeed quality back into design
Ask the user to manually mark ~10 random samples as fit / not-fit. Write findings to `/opt/data/discolike-output/<query_id>-quality.md`:
- Sample size + fit %
- Themes in the "not fit" examples
- Specific filter changes that would have caught them

The next `discolike-design` run on a similar ICP should read this file.

### 7. Tag the saved query (FREE)
```
mcp__discolike__add-tags-to-query
  query_id: <id>
  tags: ["pulled", "<topic>", "<YYYY-MM>"]
```

## What the user takes away
- A clean, deduped CSV at a known path
- The actual cost of the pull (not an estimate)
- A quality note that makes the next pull better
- Confidence that the loop is closed