# Local Partner Lead Compilation

## Classification Table

Maps each `source_search` query to a (degree, category) pair. Used in the post-scraping compile step.

| Keyword Triggers | Degree | Category |
|---|---|---|
| barber, barbershop, grooming | Degree 1 | Barbershops & Grooming |
| crossfit, gym, fitness, trainer, orangetheory, hotworx, hiit, boxing, martial, mma, bjj, yoga, pilates, spin | Degree 1 | Gyms & Fitness |
| physical therapy, physiotherapy | Degree 1 | Physical Therapy |
| chiropractor | Degree 1 | Chiropractic |
| cryo, sauna, cold plunge, recovery, day spa, massage, acupuncture | Degree 1 | Wellness & Recovery |
| med spa, aesthetics, botox | Degree 1 | Med Spas |
| dentist, implant | Degree 1 | Dentistry |
| golf, country club | Degree 1 | Golf |
| running, racquet, tennis, pickleball | Degree 1 | Sports & Recreation |
| tailor, clothing | Degree 1 | Mens Clothing |
| hair, scalp | Degree 1 | Hair Restoration |
| orthopedic | Degree 1 | Orthopedics |
| cigar | Degree 2 | Cigar Lounges |
| steakhouse, upscale, fine dining | Degree 2 | Steakhouses |
| restaurant | Degree 2 | Restaurants |
| brewery, taproom, whiskey, bourbon, distillery | Degree 2 | Breweries & Spirits |
| sports bar | Degree 2 | Sports Bars |
| car dealer, detailing, ceramic, car wash | Degree 2 | Auto |
| gun, firearm, shooting | Degree 2 | Gun Ranges |
| financial, wealth, cpa, accountant | Degree 2 | Financial Services |
| real estate | Degree 2 | Real Estate |
| insurance | Degree 2 | Insurance |
| executive coach, life coach | Degree 2 | Coaching |
| tattoo | Degree 2 | Tattoo |
| jewelry, watch | Degree 2 | Jewelry |
| hunting, fishing, boat, marina | Degree 2 | Outdoor Recreation |
| motorcycle, powersports | Degree 2 | Motorcycle |
| memorabilia | Degree 2 | Sports Memorabilia |
| coworking | Degree 2 | Coworking |
| liquor, wine | Degree 2 | Liquor & Wine |
| shoe | Degree 2 | Footwear |
| urologist, fertility | Degree 3 | Urology & Fertility |
| primary care, concierge | Degree 3 | Primary Care |
| cardiologist | Degree 3 | Cardiology |
| dermatologist | Degree 3 | Dermatology |
| optometrist, eye | Degree 3 | Optometry |
| sleep | Degree 3 | Sleep Clinics |
| attorney, law | Degree 3 | Attorneys |
| iv therapy, vitamin | Degree 3 | IV Therapy |
| meal prep, nutrition, supplement | Degree 3 | Nutrition |
| photographer | Degree 3 | Photography |
| butcher, meat | Degree 3 | Butcher Shops |
| coffee | Degree 3 | Coffee Shops |
| pharmacy | Degree 3 | Pharmacies |
| grocery, supermarket | Degree 3 | Grocery Stores |
| urgent care | Degree 3 | Urgent Care |
| veterinary, pet store, pet grooming | Degree 3 | Pet Services |
| plumber, electrician, hvac, landscap, roofing, clean, dry cleaner, auto repair | Degree 3 | Home Services |
| florist, bank, credit union, hardware, printing | Degree 3 | Local Services |

Default for unmatched queries: `Degree 2`, `Other`.

## Compile Script Pattern

The compile step merges all batch CSVs + document-based leads:

```python
# 1. Load all batches
b1 = load('all-power-partners-live.csv')
b2 = load('all-power-partners-batch2.csv')
b3 = load('all-power-partners-batch3.csv')

# 2. Deduplicate by normalized name (strip "Closed"/"Open" suffixes)
seen = set()
for row in b1 + b2 + b3:
    name_clean = re.sub(r'\b(closed|open|closes?\s*\d|opens?\s*\d)\b', '', name, flags=re.I).strip()
    if name_clean.lower() in seen: continue
    seen.add(name_clean.lower())
    # classify row and append

# 3. Add document-based leads (skip already-seen names)
for row in doc:
    if row['Name'].lower() not in seen:
        seen.add(row['Name'].lower())
        results.append([...])

# 4. Write final CSV
```

**Naming convention for batch scrapers:**
- `all-power-partners-live.csv` — batch 1 output
- `all-power-partners-batch2.csv` — batch 2 output
- `all-power-partners-batch3.csv` — batch 3 output
- `gameday-master-leads.csv` — final compiled output
- `all-influencers-merged.csv` — separate influencer file

**Pitfalls avoided:**
- `&` in category strings breaks shell heredocs — use `and` instead
- Don't use `execute_code` for long scripts — write to file via `write_file` then run via `terminal`
- Google Maps sometimes returns 0 results for generic queries (`brewery in Reisterstown` got 0) — accept blanks and move on
