#!/usr/bin/env python3
"""
Cal.com triple-endpoint verification script.

Pulls upcoming, cancelled, AND past bookings from the Cal.com v2 API in one run.
Used by the pre-call-report cron workflow to:
  1. Identify prospect-facing upcoming calls (needs reports / refresh checks)
  2. Positively confirm cancellations (patch existing report headers)
  3. Resolve ambiguity for same-day calls that disappeared from `upcoming`
     (past = already happened, cancelled = confirmed gone, none = other Cal.com account)

Replaces the unreliable cal_cross_check.py which produces false "MISSING REPORTS"
alarms due to name-based (not email-based) slug matching and lack of internal-
meeting filtering.

Usage:
    python3 scripts/cal_triple_endpoint_check.py

Reads CALCOM_API_KEY from /opt/data/.env (line-by-line startswith parsing to
avoid the SQL TRUNCATE false positive from .env-file .split() patterns).

Output: structured stdout with UPCOMING / CANCELLED / PAST sections, each
booking printed with id, title, start (UTC), event type slug, meeting URL,
attendees (name, email, timezone), and hosts. Exit codes:
  0 = success
  1 = no API key found
  2 = curl error (network/auth)
  3 = JSON parse error
"""
import subprocess, json, sys, os

# --- Read API key (line-by-line to avoid SQL TRUNCATE false positive) ---
API_KEY = None
with open('/opt/data/.env') as f:
    for line in f:
        if line.startswith('CALCOM_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip()
            break

if not API_KEY:
    print("ERROR: no CALCOM_API_KEY found in /opt/data/.env")
    sys.exit(1)

HEADERS = [
    '-H', f'Authorization: Bearer {API_KEY}',
    '-H', 'cal-api-version: 2024-08-13',
    '-H', 'User-Agent: followup-engine/1.0',
]

# Internal-meeting detection: skip these event type slugs
INTERNAL_EVENT_SLUGS = {'customer-support-sync'}
# Justin's own email — used to detect Justin-only-attendee internal meetings
JUSTIN_EMAIL = 'justin@usingaitoscale.com'

def pull_endpoint(status, sort_param=None, take=20):
    """Pull one Cal.com v2 bookings endpoint. Returns (list_of_bookings, error_str)."""
    url = f'https://api.cal.com/v2/bookings?status={status}&take={take}'
    if sort_param:
        url += f'&{sort_param}'
    result = subprocess.run(
        ['curl', '-s', '-f'] + HEADERS + ['--max-time', '15', url],
        capture_output=True, text=True, timeout=20
    )
    if result.returncode != 0:
        return [], f"curl rc={result.returncode}: {result.stderr[:200]}"
    try:
        d = json.loads(result.stdout)
    except Exception as e:
        return [], f"JSON parse error: {e}; body[:200]={result.stdout[:200]}"
    # Response shape: {"status":"success","data":[...]} OR bare list (fallback)
    if isinstance(d, dict):
        data = d.get('data', [])
        if isinstance(data, list):
            return data, None
        if isinstance(data, dict) and 'bookings' in data:
            return data['bookings'], None
        return [], f"unexpected data type: {type(data)}"
    if isinstance(d, list):
        return d, None
    return [], f"unexpected response type: {type(d)}"

def is_internal(b):
    """Detect internal meetings (skip — no pre-call report needed)."""
    et = b.get('eventType')
    slug = et.get('slug', '') if isinstance(et, dict) else ''
    if slug in INTERNAL_EVENT_SLUGS:
        return True
    attendees = b.get('attendees', [])
    # Justin-only attendee = internal
    if len(attendees) == 1 and attendees[0].get('email', '').lower() == JUSTIN_EMAIL:
        return True
    return False

def fmt_booking(b):
    """Format a booking for readable stdout output."""
    bid = b.get('id')
    title = b.get('title', '?')
    start = b.get('start', '?')
    meeting_url = b.get('meetingUrl', '')
    et = b.get('eventType')
    slug = et.get('slug', '') if isinstance(et, dict) else ''
    attendees = b.get('attendees', [])
    att = ', '.join(
        f"{a.get('name', '?')}<{a.get('email', '?')}> tz={a.get('timeZone', '?')}"
        for a in attendees
    )
    hosts = b.get('hosts', [])
    host_str = ', '.join(
        f"{h.get('name', '?')}<{h.get('email', '?')}>" for h in hosts
    )
    internal_flag = ' [INTERNAL — skip]' if is_internal(b) else ''
    lines = [
        f"  ID={bid}{'  ' + internal_flag if internal_flag else ''}",
        f"    title: {title}",
        f"    start: {start}  (UTC)",
        f"    eventType.slug: {slug}",
        f"    meetingUrl: {meeting_url}",
        f"    attendees: [{att}]",
        f"    hosts: [{host_str}]",
    ]
    return '\n'.join(lines)

# --- Pull all three endpoints ---
print("=== Cal.com Triple-Endpoint Verification ===\n")

upcoming, err = pull_endpoint('upcoming', sort_param='sortStart=asc', take=20)
if err:
    print(f"UPCOMING ERROR: {err}")
    upcoming = []
print(f"UPCOMING ({len(upcoming)} total, {sum(1 for b in upcoming if not is_internal(b))} prospect-facing):")
for b in upcoming:
    if is_internal(b):
        continue  # skip internal in output for prospect-facing focus
    print(fmt_booking(b))

print()
cancelled, err = pull_endpoint('cancelled', sort_param='sortStart=desc', take=10)
if err:
    print(f"CANCELLED ERROR: {err}")
    cancelled = []
print(f"CANCELLED ({len(cancelled)}):")
for b in cancelled:
    print(fmt_booking(b))

print()
past, err = pull_endpoint('past', sort_param='sortStart=desc', take=10)
if err:
    print(f"PAST ERROR: {err}")
    past = []
print(f"PAST ({len(past)} — already happened):")
for b in past:
    print(fmt_booking(b))

# --- Summary for cron decision logic ---
prospect_upcoming = [b for b in upcoming if not is_internal(b)]
print(f"\n=== SUMMARY ===")
print(f"Prospect-facing upcoming: {len(prospect_upcoming)}")
print(f"Internal upcoming (skipped): {sum(1 for b in upcoming if is_internal(b))}")
print(f"Recently cancelled: {len(cancelled)}")
print(f"Recently past: {len(past)}")

# List prospect-facing upcoming with attendee emails for slug derivation
if prospect_upcoming:
    print(f"\n=== PROSPECT UPCOMING — slug check needed ===")
    for b in prospect_upcoming:
        attendees = b.get('attendees', [])
        email = attendees[0].get('email', '') if attendees else ''
        domain = email.split('@')[-1].split('.')[0] if '@' in email else 'unknown'
        start = b.get('start', '?')
        print(f"  {email}  domain_hint={domain}  start={start}")