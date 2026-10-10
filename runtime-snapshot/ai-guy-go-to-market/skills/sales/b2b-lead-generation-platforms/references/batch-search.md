# Batch Company Search via ScrapeCreators API

Spray keyword×geo combos to build 250–350 unique companies per ~100 credits. The API returns max 15 per call — volume comes from diversity.

**Google Ad Library variant:** See `scripts/google-batch-advertisers.py` for a Google-specific batch script with AC false-positive filtering.

Export to CSV and then enrich with `references/profile-enrich.py` to get website/email/phone from each Facebook profile (1 credit/company):

```python
import urllib.request, json, time

api_key = "YOUR_KEY"  # from scrapecreators config

states = ["Florida", "Texas", "California", "Georgia", "Arizona", "North Carolina", "Ohio"]
keywords = ["HVAC", "AC repair", "air conditioning", "heating and cooling"]

all_results = []
seen_pages = set()

for state in states:
    for kw in keywords:
        query = f"{kw} {state}"
        url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/search/companies?query={urllib.request.quote(query)}"
        req = urllib.request.Request(url, headers={"x-api-key": api_key, "accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
                results = data.get("searchResults", [])
                new = 0
                for r in results:
                    pid = r.get("page_id")
                    if pid and pid not in seen_pages:
                        seen_pages.add(pid)
                        all_results.append(r)
                        new += 1
                print(f"{query:40s} → {len(results):2d} returned, {new:2d} new")
            time.sleep(0.15)
        except Exception as e:
            print(f"{query:40s} → ERROR: {e}")

print(f"\nTotal unique companies: {len(all_results)}")

# Save
with open("/tmp/companies.json", "w") as f:
    json.dump(all_results, f, indent=2)
```

## Known-Effective Keyword×Geo Pairs

- **Florida, Texas, Arizona, Alabama**: richest results across all keywords
- **California, Georgia**: solid results for "HVAC" and "air conditioning"
- **North Carolina, Ohio**: sparse — many zero-result combos
- **"air conditioning {state}"** and **"heating and cooling {state}"**: different results from "HVAC {state}" — include all three
- **"AC repair {state}"**: fewer hits but non-overlapping companies
- **"duct cleaning {state}"**, **"furnace repair {state}"**, **"heat pump {state}"**: niche keywords for gap-filling

## Post-Processing

Filter out non-service companies. Useful categories to keep:
- `Heating, Ventilating & Air Conditioning Service`
- `Home Improvement`, `Local Service`, `Local Business`, `Contractor`

Export to CSV and then enrich with `references/profile-enrich.py` to get website/email/phone from each Facebook profile (1 credit/company).
```python
import csv
with open("contractors.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name","category","likes","page_id","page_alias","ig_username","ig_followers","verification"])
    writer.writeheader()
    for c in contractors:
        writer.writerow({k: c.get(k, "") for k in fieldnames})
```

## Session Results (June 1, 2026)

### Facebook — 17-State HVAC Spray
- 306 unique HVAC companies from 17 states, ~95 API calls
- 243 filtered to HVAC service contractors (63 were schools/supply/non-HVAC)
- Credits depleted — 402 errors started after ~95 calls (API cap per batch)
- Top states by yield: Florida, Texas, California, Georgia, Alabama, Arizona

### Google Ad Library — Florida HVAC (June 1, 2026)
- Platform: Google Ad Library (`/v1/google/adLibrary/advertisers/search`)
- 17 HVAC companies from 41 queries across Florida cities
- 196 total estimated ads across all advertisers
- Top keywords: "air conditioning {city}" (most productive), "HVAC {city}" (1-2 each)
- Zero-yield keywords: "AC repair", "HVAC contractor", "HVAC company", "furnace repair", "HVAC installation"
- "AC Florida" returned 10 results but 8 were false positives (academies, pavers, flooring) — required name-based filtering
- Google yields 10-20x fewer results than Facebook but advertisers signal higher intent (active Google Ads spend)

### Keyword Effectiveness (by unique yield)

| Keyword pattern | Facebook avg unique/query | Google avg unique/query | Notes |
|----------------|--------------------------|------------------------|-------|
| `HVAC {state}` | 6-8 | 0-2 | Broadest coverage on Facebook, sparse on Google |
| `air conditioning {state}` | 5-7 | 2-5 | Best performer on Google; different results from "HVAC" |
| `heating and cooling {state}` | 4-6 | 0 | Good on Facebook, zero on Google |
| `AC repair {state}` | 1-3 | 0 | Sparse on both, zero on Google |
| `duct cleaning {state}` | 2-5 | 0 | Niche, not on Google |
| `HVAC installation {state}` | 0-2 | 0 | Minimal on both |
| `furnace repair {state}` | 0-1 | 0 | Minimal on both |
| `heat pump {state}` | 0-1 | 1 | Rare on both |
| `mini split {state}` | 1-2 | — | Niche specialty |
| `emergency AC {state}` | 0-1 | — | Almost no results |
| `HVAC service {state}` | 0-1 | — | Redundant with "HVAC {state}"
