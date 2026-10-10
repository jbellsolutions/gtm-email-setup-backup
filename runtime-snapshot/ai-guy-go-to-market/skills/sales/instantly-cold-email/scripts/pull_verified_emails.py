#!/usr/bin/env python3
"""Pull all verified emails from a Instantly prospector fetch into a CSV.

Usage:
  python3 pull_verified_emails.py <filter_id> [--csv output.csv]
  
Example:
  python3 pull_verified_emails.py 4478758 --csv /tmp/marketing_leads.csv
  
Output: CSV with email, name, company columns (only status=found + verificationStatus=valid).
Stderr prints progress per page.
"""
import json, csv, subprocess, sys, argparse

Instantly_BIN = "/opt/data/home/.local/bin/Instantly"

def pull_verified(filter_id, output_csv=None):
    offset = 0
    limit_val = 1000
    all_verified = []
    
    while True:
        payload = json.dumps({"filter_id": filter_id, "limit": limit_val, "offset": offset})
        result = subprocess.run(
            [Instantly_BIN, "prospect", "get", "--from-json", "/dev/stdin"],
            input=payload, capture_output=True, text=True, timeout=120
        )
        
        data = json.loads(result.stdout)
        contacts = data['data']['list']
        total = data['data']['totalCount']
        
        page_verified = 0
        for c in contacts:
            email = c.get("email", "")
            status = c.get("status", "")
            verif = c.get("verificationStatus", "")
            if email and email != "random@example.com" and status == "found" and verif == "valid":
                name = f"{c.get('firstName','')} {c.get('lastName','')}".strip()
                company = c.get('company', {}).get('name', '')
                all_verified.append((email, name, company))
                page_verified += 1
        
        print(f"  offset={offset}: {len(contacts)} contacts, {page_verified} verified (running: {len(all_verified)}/{total})", file=sys.stderr)
        
        offset += limit_val
        if offset >= total:
            break
    
    if output_csv:
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["email", "name", "company"])
            for email, name, company in all_verified:
                writer.writerow([email, name, company])
        print(f"Wrote {len(all_verified)} records to {output_csv}", file=sys.stderr)
    
    return all_verified

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull verified emails from Instantly prospector fetch")
    parser.add_argument("filter_id", type=int, help="Instantly filter ID")
    parser.add_argument("--csv", help="Output CSV path")
    args = parser.parse_args()
    
    verified = pull_verified(args.filter_id, args.csv)
    print(f"Total verified: {len(verified)}")
