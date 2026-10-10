#!/usr/bin/env python3
"""
Bulk update a single custom field on all leads in a Instantly campaign.
Used in the lead-recycling workflow — swap per-lead personalization data
without deleting/re-uploading leads.

Rate: ~1 update/second. 4,500 leads = ~75 minutes. Run in background.

Usage:
    Instantly_API_KEY=<key> python3 bulk_update_custom_fields.py <campaign_id> <csv_path> <field_name>

CSV must have columns: email, <field_name>
The script paginates through all leads, matches by email, and updates.

Pitfalls:
    - `leads update` returns cosmetic "Not found" error — updates still apply. Ignore it.
    - ~1/second throughput. Don't rush it — Instantly rate-limits aggressively.
"""
import json, subprocess, os, csv, time, sys

LOG = "/tmp/bulk_update_log.txt"
def log(msg):
    with open(LOG, 'a') as f: f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    print(msg, flush=True)

campaign_id = int(sys.argv[1])
csv_path = sys.argv[2]
field_name = sys.argv[3]

# Load lookup CSV
lookup = {}
with open(csv_path) as f:
    for row in csv.DictReader(f):
        lookup[row['email'].strip().lower()] = row[field_name].strip()
log(f"Loaded {len(lookup)} values for field '{field_name}'")

api_key = os.environ.get('Instantly_API_KEY', '')
if not api_key:
    with open('/opt/data/.env') as f:
        for line in f:
            if 'Instantly_API_KEY' in line:
                api_key = line.strip().split('=', 1)[1].strip(); break

PATH = "/opt/data/home/.local/bin"
ENV = {**os.environ, 'PATH': PATH + ':' + os.environ.get('PATH', ''), 'Instantly_API_KEY': api_key}

offset = updated = skipped = errors = 0
start = time.time()

while True:
    cmd = f'Instantly leads list --campaign-id {campaign_id} --offset {offset} --limit 100 --format json'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=ENV, timeout=30)
    try: data = json.loads(result.stdout)
    except: offset += 100; continue
    
    leads = data.get('data', [])
    if not leads: break
    
    page_ok = 0
    for item in leads:
        lead = item.get('lead', item)
        email = lead.get('email', '').strip().lower()
        map_id = item.get('campaign_lead_map_id')
        name = lead.get('first_name', '')
        if not email or not map_id: continue
        if email not in lookup: skipped += 1; continue
        
        payload = {
            "email": email,
            "first_name": name,
            "custom_fields": {field_name: lookup[email]}
        }
        path = f'/tmp/bulkupd_{map_id}.json'
        with open(path, 'w') as f: json.dump(payload, f)
        
        cmd2 = f'Instantly leads update --campaign-id {campaign_id} --lead-id {map_id} --from-json {path}'
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, env=ENV, timeout=15)
        try: os.remove(path)
        except: pass
        
        # Cosmetic error = success
        if 'Not found' in result2.stderr or 'Invalid request' in result2.stderr:
            updated += 1; page_ok += 1
        else: errors += 1
    
    elapsed = time.time() - start
    log(f"  offset={offset}: +{page_ok} | total={updated} skip={skipped} err={errors} | {updated/max(elapsed,0.1):.0f}/s")
    offset += 100
    if len(leads) < 100: break
    time.sleep(0.15)

elapsed = time.time() - start
log(f"DONE in {elapsed:.0f}s: {updated} updated, {skipped} skipped, {errors} errors")