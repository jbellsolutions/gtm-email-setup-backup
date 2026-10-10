#!/usr/bin/env python3
"""
Batch profile enrichment: loops through a JSON company list from
adlibrary-search-companies, calls facebook profile on each, and outputs
an enriched CSV with website, email, phone, and page_intro.

Input:  /tmp/hvac_companies.json (from batch-search.py)
Output: /tmp/hvac_enriched.csv
        /tmp/hvac_enriched.json (full data + errors)

Dependencies: scrapecreators CLI installed and authenticated.
Cost: 1 ScrapeCreators credit per company.
"""

import subprocess
import json
import time
import csv
import sys

INPUT_FILE = "/tmp/hvac_companies.json"
OUTPUT_CSV = "/tmp/hvac_enriched.csv"
OUTPUT_JSON = "/tmp/hvac_enriched.json"

with open(INPUT_FILE) as f:
    companies = json.load(f)

enriched = []
errors = []
total = len(companies)

for i, c in enumerate(companies):
    alias = c.get("page_alias", "").strip()
    page_id = c.get("page_id", "")

    if alias:
        url = f"https://facebook.com/{alias}"
    elif page_id:
        url = f"https://facebook.com/{page_id}"
    else:
        continue

    try:
        result = subprocess.run(
            f'export PATH=~/.npm-global/bin:$PATH; scrapecreators facebook profile --url "{url}" 2>/dev/null',
            shell=True, capture_output=True, text=True, timeout=20
        )
        data = json.loads(result.stdout)

        if data.get("success"):
            enriched.append({
                "name": c["name"],
                "category": c["category"],
                "facebook_url": url,
                "page_id": page_id,
                "likes": c["likes"],
                "website": data.get("website", ""),
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "page_intro": data.get("pageIntro", ""),
                "rating": data.get("rating", ""),
                "rating_count": data.get("ratingCount", 0),
                "ig_username": c.get("ig_username", ""),
                "ig_followers": c.get("ig_followers", ""),
                "ad_status": data.get("adLibrary", {}).get("adStatus", ""),
                "creation_date": data.get("creationDate", ""),
            })
        else:
            errors.append({"name": c["name"], "url": url, "error": "not_success"})
    except Exception as e:
        errors.append({"name": c["name"], "url": url, "error": str(e)[:100]})

    if (i + 1) % 25 == 0:
        print(f"Progress: {i+1}/{total} — enriched: {len(enriched)}, errors: {len(errors)}")

    time.sleep(0.05)  # rate limit courtesy

print(f"\nDone! Enriched: {len(enriched)}, Errors: {len(errors)}")

# Save full data
with open(OUTPUT_JSON, "w") as f:
    json.dump({"enriched": enriched, "errors": errors}, f, indent=2)

# Save CSV
if enriched:
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=enriched[0].keys())
        writer.writeheader()
        writer.writerows(enriched)
    print(f"CSV saved: {OUTPUT_CSV}")

# Stats
with_website = sum(1 for e in enriched if e["website"])
with_email = sum(1 for e in enriched if e["email"])
with_phone = sum(1 for e in enriched if e["phone"])
print(f"With website: {with_website}/{len(enriched)} ({with_website/len(enriched)*100:.0f}%)")
print(f"With email:   {with_email}/{len(enriched)}")
print(f"With phone:   {with_phone}/{len(enriched)}")
