import urllib.request, json, time, csv

# === CONFIG ===
API_KEY = "YOUR_KEY"  # from scrapecreators config get apiKey
BASE = "https://api.scrapecreators.com/v1/google/adLibrary/advertisers/search"

# Keywords and geos — adjust for your vertical
keywords = [
    "HVAC", "air conditioning", "heating and cooling",
    "duct cleaning", "heat pump",
]
metros = [
    "Florida", "Miami FL", "Tampa FL", "Orlando FL",
    "Jacksonville FL", "Fort Lauderdale FL",
]

# === HVAC FILTER (based on company name) ===
def is_hvac(name):
    """Post-filter to remove false positives from 'AC' matching academies etc."""
    name_lower = name.lower()
    exclude = {"academy", "flooring", "barber", "pavers", "aviation", "piano", "lifts"}
    for term in exclude:
        if term in name_lower:
            return False
    include = {"hvac", "air condition", "heating", "heat pump", "duct", "cooling"}
    for term in include:
        if term in name_lower:
            return True
    return False

# === RUN ===
all_results = []
seen_ids = set()

for metro in metros:
    for kw in keywords:
        query = f"{kw} {metro}"
        url = f"{BASE}?query={urllib.request.quote(query)}"
        req = urllib.request.Request(url, headers={
            "x-api-key": API_KEY,
            "accept": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=18) as resp:
                data = json.loads(resp.read().decode())
                advertisers = data.get("advertisers", [])
                websites = data.get("websites", [])
                new = 0
                for a in advertisers:
                    aid = a.get("advertiser_id")
                    if aid and aid not in seen_ids:
                        seen_ids.add(aid)
                        a["_query"] = query
                        a["_domains"] = [w["domain"] for w in websites]
                        all_results.append(a)
                        new += 1
                creds = data.get("credits_remaining", "?")
                if new > 0:
                    print(f"{query:40s} → {len(advertisers):2d} returned, {new:2d} new, creds={creds}")
            time.sleep(0.12)
        except Exception as e:
            print(f"{query:40s} → ERROR: {e}")

# Filter to HVAC
hvacs = [a for a in all_results if is_hvac(a["name"])]
non_hvac = [a for a in all_results if not is_hvac(a["name"])]

print(f"\nHVAC: {len(hvacs)} | Filtered out: {len(non_hvac)}")
for a in sorted(hvacs, key=lambda x: x.get("number_of_ads_estimate", 0), reverse=True):
    print(f"  {a['name']:60s} {a.get('number_of_ads_estimate',0):5d} ads")

# Save CSV
with open("google_hvac_leads.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name","advertiser_id","region","number_of_ads_estimate","domains","query"])
    w.writeheader()
    for a in hvacs:
        w.writerow({
            "name": a["name"],
            "advertiser_id": a["advertiser_id"],
            "region": a.get("region", ""),
            "number_of_ads_estimate": a.get("number_of_ads_estimate", 0),
            "domains": ", ".join(a.get("_domains", [])),
            "query": a.get("_query", ""),
        })
print(f"\nSaved {len(hvacs)} HVAC leads to google_hvac_leads.csv")
