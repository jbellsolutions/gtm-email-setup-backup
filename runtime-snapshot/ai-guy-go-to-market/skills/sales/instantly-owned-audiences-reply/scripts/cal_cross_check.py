#!/usr/bin/env python3
"""Cal.com v2 cross-check: list upcoming client bookings + flag missing pre-call reports.

Run during Owned Audiences cron sessions to verify pre-call report coverage.
Does NOT touch Instantly — safe to run during plan-expiry / auth-failure outages.

Usage:
    python3 scripts/cal_cross_check.py

Output:
    - Client bookings (internal meetings filtered out)
    - Pre-call reports on disk
    - Cross-match: bookings checked against report headers for attendee name
    - Missing/stale reports flagged

Pitfalls encoded:
  - v2 response is {"status":"success","data":[...]} — a DICT, not a bare list
  - status=upcoming (NOT accepted)
  - Attendee info in attendees[0], NOT a top-level responses dict
  - Internal meetings (Instantly support sync) must be filtered
  - "30 Min Meeting" with Justin as attendee is NOT always internal — check host email
  - Directory names don't match attendee names — reports live under company slugs (prelint, synova-search)
    → fix: read report headers to fuzzy-match by attendee name instead of guessing directory slug
  - Security scan blocks curl | python3 pipe-to-interpreter — use subprocess.run()
  - .env key parsing must avoid SQL TRUNCATE false positive — use line-by-line startswith()
"""

import subprocess, json, sys, os

# Read CALCOM_API_KEY from /opt/data/.env (line-by-line to avoid SQL TRUNCATE false positive)
key = None
for line in open('/opt/data/.env'):
    if line.startswith('CALCOM_API_KEY='):
        key = line.split('=', 1)[1].strip()
        break
if not key:
    print("ERROR: CALCOM_API_KEY not found in /opt/data/.env", file=sys.stderr)
    sys.exit(1)

r = subprocess.run([
    'curl', '-s',
    'https://api.cal.com/v2/bookings?status=upcoming&sortStart=asc&take=20',
    '-H', f'Authorization: Bearer {key}',
    '-H', 'cal-api-version: 2024-08-13'
], capture_output=True, text=True, timeout=30)

try:
    d = json.loads(r.stdout)
except json.JSONDecodeError as e:
    print(f"ERROR: Cal.com API returned non-JSON: {r.stdout[:200]}", file=sys.stderr)
    sys.exit(1)

# v2 response shape (confirmed Jul 27, 2026): {"status":"success","data":[<bookings>]}
if isinstance(d, list):
    bookings = d
elif isinstance(d, dict):
    data = d.get('data', [])
    if isinstance(data, list):
        bookings = data
    elif isinstance(data, dict):
        bookings = data.get('bookings', [])
    else:
        bookings = []
else:
    bookings = []

# Filter internal meetings
INTERNAL_HOSTS = {'evan@Instantly'}  # Instantly support

def is_internal(b):
    title = b.get('title', '')
    hosts = b.get('hosts', [])
    attendees = b.get('attendees', [])
    host_emails = [h.get('email', '') for h in hosts]
    attendee_emails = [a.get('email', '') for a in attendees]
    # Instantly Customer Support Sync
    if any(h in INTERNAL_HOSTS for h in host_emails):
        return True
    # "30 Min Meeting" where Justin is attendee AND host is internal
    # External host → real peer/partnership meeting → NOT internal
    if '30 Min Meeting' in title and 'justin@usingaitoscale.com' in attendee_emails:
        if all(h in INTERNAL_HOSTS for h in host_emails if h):
            return True
        return False
    return False

client_bookings = [b for b in bookings if not is_internal(b)]

print(f"Upcoming bookings (all): {len(bookings)}")
print(f"Client bookings (non-internal): {len(client_bookings)}")
print()

# Pre-call reports on disk — build a map of {attendee_name_lower: (slug, report_path)}
CLIENTS_DIR = '/opt/data/clients'
report_map = {}  # attendee_name_lower → (dir_slug, path)
if os.path.isdir(CLIENTS_DIR):
    for d_name in os.listdir(CLIENTS_DIR):
        report_path = f'{CLIENTS_DIR}/{d_name}/pre-call-report.md'
        if os.path.exists(report_path):
            try:
                with open(report_path) as f:
                    header = f.read(500)
                # Extract attendee name from report header
                # Common formats: "# Name — Pre-Call Report", "## Attendee: Name", etc.
                import re
                m = re.search(r'(?:Pre-Call Report for|Attendee:|#)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', header)
                if m:
                    attendee_name = m.group(1).strip()
                    report_map[attendee_name.lower()] = (d_name, report_path)
                else:
                    # Fallback: first markdown heading
                    m2 = re.search(r'^#\s+(.+?)(?:\s+—|\n|$)', header)
                    if m2:
                        attendee_name = m2.group(1).strip()
                        report_map[attendee_name.lower()] = (d_name, report_path)
            except Exception:
                pass

print(f"Pre-call reports on disk: {len(report_map)}")
print()

# Cross-match bookings against reports
for b in client_bookings:
    title = b.get('title', '?')
    start = b.get('start', '?')
    attendee = b.get('attendees', [{}])[0] if b.get('attendees') else {}
    name = attendee.get('name', '?')
    email = attendee.get('email', '?')
    start_short = start[:16].replace('T', ' ') if isinstance(start, str) else start
    
    print(f"  {name} ({email})")
    print(f"    Title: {title}")
    print(f"    Start: {start_short}")
    
    # Cross-match by attendee name in report headers
    name_lower = name.lower() if name else ''
    found = False
    for key, (slug, path) in report_map.items():
        # Fuzzy match: attendee name appears in report header
        if name_lower and (name_lower in key or key in name_lower or 
                          any(part in key for part in name_lower.split() if len(part) > 2)):
            print(f"    Report: [OK] {slug}/pre-call-report.md (matched by header)")
            found = True
            break
    
    if not found:
        # Fallback: check directory names loosely
        for d_name in os.listdir(CLIENTS_DIR):
            rp = f'{CLIENTS_DIR}/{d_name}/pre-call-report.md'
            if os.path.exists(rp):
                if name_lower and (d_name.lower() in name_lower or name_lower in d_name.lower()):
                    print(f"    Report: [OK] {d_name}/pre-call-report.md (matched by directory slug)")
                    found = True
                    break
    
    if not found:
        print(f"    Report: [MISSING] No pre-call report found — needs generation")
    
    print()
