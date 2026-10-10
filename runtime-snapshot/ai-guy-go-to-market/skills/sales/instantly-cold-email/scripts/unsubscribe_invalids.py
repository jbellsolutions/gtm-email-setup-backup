#!/usr/bin/env python3
"""Bulk unsubscribe invalid leads from a Instantly campaign.

Usage: python3 unsubscribe_invalids.py <campaign_id> <invalid_emails.json>

Where invalid_emails.json is either:
  - A flat list of email strings: ["bad@example.com", ...]
  - A dict mapping email → campaign_lead_map_id: {"bad@example.com": "12345", ...}

The script paginates through all campaign leads to find campaign_lead_map_ids
for the invalid emails, then unsubscribes them one at a time.
"""
import subprocess, json, os, sys, time

if len(sys.argv) < 3:
    print("Usage: python3 unsubscribe_invalids.py <campaign_id> <invalid_emails.json>")
    sys.exit(1)

CAMPAIGN_ID = sys.argv[1]
INVALID_FILE = sys.argv[2]

Instantly_KEY = os.environ.get("Instantly_API_KEY", "[REDACTED]")
Instantly_PATH = "/opt/data/home/.local/bin"
env = {
    **os.environ,
    "Instantly_API_KEY": Instantly_KEY,
    "PATH": f"{Instantly_PATH}:{os.environ.get('PATH', '')}"
}

with open(INVALID_FILE) as f:
    invalid_data = json.load(f)

# Detect format
if isinstance(invalid_data, dict):
    # Already have IDs
    invalid_ids = list(invalid_data.values())
    print(f"Using {len(invalid_ids)} pre-mapped lead IDs")
elif isinstance(invalid_data, list):
    # Need to look up IDs
    invalid_emails = set(e.strip().lower() if isinstance(e, str) else e.get("email", "").strip().lower() for e in invalid_data)
    print(f"Looking up {len(invalid_emails)} invalid emails in campaign {CAMPAIGN_ID}...")
    
    all_leads = {}
    offset = 0
    while True:
        result = subprocess.run(
            ["Instantly", "leads", "list", "--campaign-id", CAMPAIGN_ID,
             "--format", "json", "--limit", "100", "--offset", str(offset)],
            capture_output=True, text=True, timeout=60, env=env
        )
        if result.returncode != 0:
            print(f"Error at offset {offset}: {result.stderr[:100]}")
            break
        
        data = json.loads(result.stdout)
        items = data.get("data", [])
        if not items:
            break
        
        for item in items:
            lead = item.get("lead", {})
            email = (lead.get("email") or "").strip().lower()
            lead_map_id = item.get("campaign_lead_map_id", "")
            if email and lead_map_id:
                all_leads[email] = lead_map_id
        
        offset += len(items)
        if len(items) < 100:
            break
        if offset % 500 == 0:
            print(f"  Mapped: {len(all_leads)} leads...", flush=True)
    
    invalid_ids = [all_leads[e] for e in invalid_emails if e in all_leads]
    print(f"Total mapped: {len(all_leads)}, invalid found: {len(invalid_ids)}")
    print(f"Not found in campaign: {len(invalid_emails) - len(invalid_ids)}")

# Unsubscribe all
count = 0
for lid in invalid_ids:
    result = subprocess.run(
        ["Instantly", "leads", "unsubscribe", "--campaign-id", CAMPAIGN_ID, "--lead-id", lid],
        capture_output=True, text=True, timeout=15, env=env
    )
    if result.returncode == 0 or "already" in result.stderr.lower():
        count += 1
    
    if count % 100 == 0:
        print(f"  Unsubscribed: {count}/{len(invalid_ids)}", flush=True)
    time.sleep(0.05)

print(f"\nDONE: Unsubscribed {count} invalid leads from campaign {CAMPAIGN_ID}")
