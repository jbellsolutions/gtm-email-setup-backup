# Comprehensive Nationwide Sweep — Busting the 15-Result API Cap

ScrapeCreators Facebook Ad Library API returns **max 15 results per query** with no pagination. To get true nationwide coverage, use a two-tier approach: city-level queries in top states to break through the cap, plus state-level queries for remaining states.

## Two-Tier Strategy

### Tier 1 — Top States, City-Level Queries (deep coverage)
For the 10-15 states with the most solar activity, query individual cities/metros with multiple keyword variations. This avoids the 15-result cap because each city×keyword combo returns a different slice of results.

**City selection:** Use 4-6 major metros per state.

**Keywords (3 per city):**
- `"solar {city}"`
- `"solar installation {city}"`  
- `"solar panels {city}"`

Example: California → query "solar Los Angeles", "solar installation Los Angeles", "solar panels Los Angeles", then repeat for San Diego, San Francisco, Sacramento, San Jose, Fresno. That's 18 queries for one state instead of 1, producing 3-8× more unique companies.

### Tier 2 — Remaining States, State-Level (baseline coverage)
For the other 35+ states, use a single state-level query: `"solar energy {state}"`. These states are lower-volume, so the 15-result cap is rarely an issue.

### State Mapping
**Pitfall:** When using city-level queries, you can't parse the state from the query string (e.g., `"solar Los Angeles"` doesn't contain "California"). Add explicit `state` and `tier` fields to each record during collection:

```python
for city, state_abbr in city_state_map:
    query = f"solar {city}"
    # ... API call ...
    for r in results:
        r["state"] = state_abbr    # "California"
        r["tier"] = 1
        # ...
```

Use a mapping dict:
```python
city_state_map = [
    ("Los Angeles", "California"), ("San Diego", "California"),
    ("Houston", "Texas"), ("Dallas", "Texas"),
    ("Miami", "Florida"), ("Orlando", "Florida"),
    # ... etc
]
```

## Performance: subagent vs execute_code

**Subagent delegation (delegate_task) is much slower for bulk API calls.** A 133-query Google sweep in a subagent timed out at 600s. The same sweep ran directly via `execute_code` completed in 193s. For bulk sequential API calls with sleep delays, use `execute_code` directly — subagent overhead is significant.

**Subagent is good for:** parallelizing two different platforms (FB + Google simultaneously), since each runs independently. But make the per-subagent workload leaner — aim for <100 queries per subagent.

## Google: Same Company, Different Advertiser IDs

Google's Ad Library can return the same company under **different advertiser IDs** (e.g., GREEN SOLUTIONS SOLAR appeared with two IDs, 31 and 22 ads). The `advertiser_id` dedup alone isn't enough — also deduplicate by **case-insensitive company name**, merging ad counts:

```python
seen_names = set()
deduped = []
for a in advertisers:
    nl = a["name"].strip().lower()
    if nl not in seen_names:
        seen_names.add(nl)
        deduped.append(a)
    else:
        for e in deduped:
            if e["name"].strip().lower() == nl:
                e["number_of_ads_estimate"] += a.get("number_of_ads_estimate", 0)
```

## Session Results (June 3, 2026 — Solar Sweep)

### Facebook: 438 companies across 31 states
- 226 queries (191 city-level Tier 1 + 35 state-level Tier 2)
- Top states: TX (86), CA (69), FL (51), AZ (40), NV (34), GA (28)
- Categories: Solar Energy Company (98), Solar Energy Service (94), Energy Company (42)
- 19 states returned 0 results — no solar companies advertising on Facebook there

### Google: 23 advertisers (300 total ads)
- 133 queries across 60+ cities + 5 broad terms
- After name-based dedup: 23 unique advertisers
- Top: Go Solar Power (61 ads), Green Solutions Solar (53), Simple Power Solar (43)
- Google yields 20× fewer results than Facebook for solar