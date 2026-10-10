#!/usr/bin/env python3
"""Compile all Gameday lead sources into a single master CSV.
Usage: python3 scripts/compile_leads.py
Expects batch CSVs (all-power-partners-live.csv, -batch2.csv, -batch3.csv)
and power-partners.csv in the leads/ directory.
"""
import csv, re
from pathlib import Path
from collections import Counter

BASE = Path('/opt/data/hermes/leads')

def load(p):
    try:
        with open(p) as f: return list(csv.DictReader(f))
    except: return []

def classify(search):
    s = (search or '').lower()
    m = [
        (['barber','grooming'], ('Degree 1','Barbershops')),
        (['crossfit','gym','fitness','trainer','orangetheory','hotworx','hiit','boxing','martial','mma','bjj','yoga','pilates','spin'], ('Degree 1','Gyms and Fitness')),
        (['physical therapy','physiotherapy'], ('Degree 1','Physical Therapy')),
        (['chiropractor'], ('Degree 1','Chiropractic')),
        (['cryo','sauna','cold plunge','recovery','day spa','massage','acupuncture'], ('Degree 1','Wellness and Recovery')),
        (['med spa','aesthetics','botox'], ('Degree 1','Med Spas')),
        (['dentist','implant'], ('Degree 1','Dentistry')),
        (['golf','country club'], ('Degree 1','Golf')),
        (['running','racquet','tennis','pickleball'], ('Degree 1','Sports and Rec')),
        (['tailor','clothing'], ('Degree 1','Mens Clothing')),
        (['hair','scalp'], ('Degree 1','Hair Restoration')),
        (['orthopedic'], ('Degree 1','Orthopedics')),
        (['cigar'], ('Degree 2','Cigar Lounges')),
        (['steakhouse','upscale','fine dining'], ('Degree 2','Steakhouses')),
        (['restaurant'], ('Degree 2','Restaurants')),
        (['brewery','taproom','whiskey','bourbon','distillery'], ('Degree 2','Breweries and Spirits')),
        (['sports bar'], ('Degree 2','Sports Bars')),
        (['car dealer','detailing','ceramic','car wash'], ('Degree 2','Auto')),
        (['gun','firearm','shooting'], ('Degree 2','Gun Ranges')),
        (['financial','wealth','cpa','accountant'], ('Degree 2','Financial')),
        (['real estate'], ('Degree 2','Real Estate')),
        (['insurance'], ('Degree 2','Insurance')),
        (['coach'], ('Degree 2','Coaching')),
        (['tattoo'], ('Degree 2','Tattoo')),
        (['jewelry','watch'], ('Degree 2','Jewelry')),
        (['hunting','fishing','boat','marina'], ('Degree 2','Outdoor Rec')),
        (['motorcycle','powersports'], ('Degree 2','Motorcycle')),
        (['memorabilia'], ('Degree 2','Memorabilia')),
        (['coworking'], ('Degree 2','Coworking')),
        (['liquor','wine'], ('Degree 2','Liquor and Wine')),
        (['shoe'], ('Degree 2','Footwear')),
        (['urologist','fertility'], ('Degree 3','Urology')),
        (['primary care','concierge'], ('Degree 3','Primary Care')),
        (['cardiologist'], ('Degree 3','Cardiology')),
        (['dermatologist'], ('Degree 3','Dermatology')),
        (['optometrist','eye'], ('Degree 3','Optometry')),
        (['sleep'], ('Degree 3','Sleep')),
        (['attorney','law'], ('Degree 3','Attorneys')),
        (['iv therapy','vitamin'], ('Degree 3','IV Therapy')),
        (['meal prep','nutrition','supplement'], ('Degree 3','Nutrition')),
        (['photographer'], ('Degree 3','Photography')),
        (['butcher','meat'], ('Degree 3','Butcher')),
        (['coffee'], ('Degree 3','Coffee')),
        (['pharmacy'], ('Degree 3','Pharmacy')),
        (['grocery','supermarket'], ('Degree 3','Grocery')),
        (['urgent care'], ('Degree 3','Urgent Care')),
        (['veterinary','pet store','pet grooming'], ('Degree 3','Pet Services')),
        (['plumber','electrician','hvac','landscap','roofing','clean','dry cleaner','auto repair'], ('Degree 3','Home Services')),
        (['florist','bank','credit union','hardware','printing'], ('Degree 3','Local Services')),
    ]
    for keywords, result in m:
        if any(kw in s for kw in keywords):
            return result
    return ('Degree 2','Other')

b1 = load(BASE / 'all-power-partners-live.csv')
b2 = load(BASE / 'all-power-partners-batch2.csv')
b3 = load(BASE / 'all-power-partners-batch3.csv')
print(f"Raw: B1={len(b1)} B2={len(b2)} B3={len(b3)}")

seen = set()
results = []
for rows in [b1, b2, b3]:
    for row in rows:
        nm = (row.get('name') or '').strip()
        nc = re.sub(r'\b(closed|open|closes?\s*\d|opens?\s*\d)\b', '', nm, flags=re.I).strip()
        if not nc or len(nc) < 3:
            continue
        if nc.lower() in seen:
            continue
        seen.add(nc.lower())
        d, c = classify(row.get('source_search', ''))
        results.append([nm, d, c, (row.get('address') or '').strip(), (row.get('phone') or '').strip(), row.get('rating', ''), 'Google Maps', row.get('source_search', '')])

doc = load(BASE / 'power-partners.csv')
doc_new = 0
for row in doc:
    nm = (row.get('Name') or row.get('name') or '').strip()
    if not nm or len(nm) < 2:
        continue
    if nm.lower() in seen:
        continue
    seen.add(nm.lower())
    doc_new += 1
    results.append([nm, row.get('Degree','Degree 1'), row.get('Category','Referral'), (row.get('Address') or '').strip(), (row.get('Phone') or '').strip(), '', 'Document', ''])

out = BASE / 'gameday-master-leads.csv'
with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['name','degree','category','address','phone','rating','source','search_query'])
    w.writerows(results)

cats = Counter(r[2] for r in results)
degs = Counter(r[1] for r in results)
print(f"Total: {len(results)} leads ({doc_new} from document)")
print(f"Degrees: {dict(degs)}")
print(f"Categories: {len(cats)}")
for c, n in cats.most_common():
    print(f"  {c}: {n}")
print(f"Saved: {out}")
