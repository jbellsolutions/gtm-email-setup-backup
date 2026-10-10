#!/usr/bin/env python3
"""Verify leads via ScraperCity email-validate CLI. Async batch: submit → poll → download."""
import subprocess, json, csv, os, sys, time, re

SCRAPER = '/opt/data/home/.npm-global/bin/scrapercity'
API_KEY = os.environ.get('SCRAPERCITY_API_KEY', '90c2ca64-81bc-48ab-a6b2-980abfaea898')
PATH = '/opt/data/home/.npm-global/bin:' + os.environ.get('PATH', '')
BATCH_SIZE = 500
INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else None
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else '/tmp/sc_verify_results.csv'

if not INPUT_FILE:
    print("Usage: python3 verify_leads.py <emails.txt> [output.csv]")
    print("  emails.txt: one email per line")
    sys.exit(1)

# Read emails
with open(INPUT_FILE) as f:
    emails = [e.strip().lower() for e in f.readlines() if e.strip() and '@' in e]
print(f"Loaded {len(emails)} emails to verify")

# Submit batches
env = {**os.environ, 'SCRAPERCITY_API_KEY': API_KEY, 'PATH': PATH}
run_ids = []

for i in range(0, len(emails), BATCH_SIZE):
    batch = emails[i:i + BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    print(f"Submitting batch {batch_num} ({len(batch)} emails)...")
    result = subprocess.run(
        [SCRAPER, 'email-validate'] + batch,
        capture_output=True, text=True, timeout=30, env=env
    )
    match = re.search(r'Run ID: ([a-f0-9-]+)', result.stdout + result.stderr)
    if match:
        run_ids.append(match.group(1))
        print(f"  OK {match.group(1)}")
    else:
        print(f"  FAIL: {result.stderr[:200]}")

print(f"\n{submitted} {len(run_ids)} batches submitted. Polling...")

# Poll and collect results
all_results = []
for rid in run_ids:
    print(f"\nPolling {rid}...")
    subprocess.run(
        [SCRAPER, 'poll', rid],
        capture_output=True, text=True, timeout=300, env=env
    )
    subprocess.run(
        [SCRAPER, 'download', rid],
        capture_output=True, text=True, timeout=30, env=env
    )
    csv_path = f'{rid}.csv'
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_results.append({
                    'email': row.get('email', ''),
                    'status': row.get('sc_email_status', ''),
                    'message': row.get('sc_validation_message', ''),
                    'catch_all': row.get('sc_is_catch_all', ''),
                    'mx_provider': row.get('sc_mx_provider', ''),
                })
        os.remove(csv_path)

# Write output
with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['email', 'status', 'message', 'catch_all', 'mx_provider'])
    writer.writeheader()
    writer.writerows(all_results)

valid = sum(1 for r in all_results if r['status'] == 'valid')
invalid = sum(1 for r in all_results if r['status'] == 'invalid')
print(f"\nDone. {len(all_results)} verified: {valid} valid, {invalid} invalid ({invalid/len(all_results)*100:.1f}%)")
print(f"Results: {OUTPUT_FILE}")
