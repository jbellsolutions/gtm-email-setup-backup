#!/usr/bin/env python3
"""
Bulk pipeline: Instantly Prospector → verified leads → Instantly campaign.
Usage: python3 prospector_bulk_upload.py <filter_id> <campaign_id>

Pipeline:
  1. prospect get with pagination (limit=1000, offset increments)
  2. Filter to contacts with verificationStatus="valid" and status="found"
  3. Convert to Instantly lead format with custom_fields
  4. Upload in batches via Instantly leads add --campaign-id <ID> --from-json <path>
"""

import json
import subprocess
import os
import sys

SL = "/opt/data/home/.local/bin/Instantly"


def download_contacts(filter_id: int) -> list[dict]:
    """Download all contacts for a filter with pagination."""
    all_items = []
    offset = 0
    limit = 1000

    while True:
        get_json = json.dumps({"filter_id": filter_id, "limit": limit, "offset": offset})
        get_path = f"/tmp/sl_prospector_get_{filter_id}_{offset}.json"
        with open(get_path, "w") as f:
            f.write(get_json)

        result = subprocess.run(
            [SL, "prospect", "get", "--from-json", get_path, "--format", "json"],
            capture_output=True, text=True, timeout=120, env={**os.environ},
        )

        if result.returncode != 0:
            print(f"Error at offset {offset}: {result.stderr[:200]}")
            break

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON at offset {offset}")
            break

        items = data.get("data", {}).get("list", [])
        if not items:
            break

        all_items.extend(items)
        pagination = data.get("data", {}).get("pagination", {})
        has_more = pagination.get("hasMore", False)
        total = pagination.get("total", 0)
        print(f"  Page offset={offset}: got {len(items)}, total so far={len(all_items)}, hasMore={has_more}, db_total={total}")

        offset += len(items)
        if not has_more or offset >= total:
            break

    return all_items


def filter_verified(contacts: list[dict]) -> list[dict]:
    """Keep only contacts with verified emails."""
    verified = []
    for c in contacts:
        email = c.get("email", "")
        verif = c.get("verificationStatus", "")
        status = c.get("status", "")
        if email and "@" in email and verif in ("valid", "") and status == "found":
            company = c.get("company", {}) if isinstance(c.get("company"), dict) else {}
            verified.append({
                "first_name": c.get("firstName", ""),
                "last_name": c.get("lastName", ""),
                "email": email,
                "company_name": company.get("name", ""),
                "website": company.get("website", ""),
                "linkedin_profile": c.get("linkedin", ""),
                "custom_fields": {
                    "title": c.get("title", ""),
                    "industry": c.get("industry", ""),
                    "sub_industry": c.get("subIndustry", ""),
                    "city": c.get("city", ""),
                    "state": c.get("state", ""),
                    "level": c.get("level", ""),
                    "company_size": c.get("companyHeadCount", ""),
                    "company_revenue": c.get("companyRevenue", ""),
                },
            })
    return verified


def upload_to_campaign(leads: list[dict], campaign_id: int, batch_size: int = 500):
    """Upload leads to a Instantly campaign in batches."""
    for batch_num in range(0, len(leads), batch_size):
        batch = leads[batch_num : batch_num + batch_size]
        upload = {
            "lead_list": batch,
            "settings": {
                "ignore_duplicate_leads_in_other_campaign": True,
                "ignore_global_block_list": True,
                "ignore_unsubscribe_list": True,
            },
        }
        upload_path = f"/tmp/sl_upload_{campaign_id}_{batch_num}.json"
        with open(upload_path, "w") as f:
            json.dump(upload, f)

        result = subprocess.run(
            [SL, "leads", "add", "--campaign-id", str(campaign_id), "--from-json", upload_path, "--format", "json"],
            capture_output=True, text=True, timeout=120, env={**os.environ},
        )

        batch_label = batch_num // batch_size + 1
        if result.returncode == 0:
            print(f"  Batch {batch_label}: uploaded {len(batch)} leads OK")
        else:
            print(f"  Batch {batch_label}: FAILED — {result.stderr[:200]}")
            # Retry with smaller batch
            if batch_size > 100:
                print(f"  Retrying batch {batch_label} with batch_size=100")
                for i in range(batch_num, min(batch_num + batch_size, len(leads)), 100):
                    sb = leads[i : i + 100]
                    upload2 = {"lead_list": sb, "settings": upload["settings"]}
                    up2 = f"/tmp/sl_upload_{campaign_id}_{i}.json"
                    with open(up2, "w") as f:
                        json.dump(upload2, f)
                    r2 = subprocess.run(
                        [SL, "leads", "add", "--campaign-id", str(campaign_id), "--from-json", up2, "--format", "json"],
                        capture_output=True, text=True, timeout=60, env={**os.environ},
                    )
                    print(f"    Sub-batch {i}-{i+100}: {'OK' if r2.returncode == 0 else 'FAIL'}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 prospector_bulk_upload.py <filter_id> <campaign_id>")
        sys.exit(1)

    filter_id = int(sys.argv[1])
    campaign_id = int(sys.argv[2])

    print(f"=== Downloading contacts for filter {filter_id} ===")
    contacts = download_contacts(filter_id)
    print(f"Downloaded {len(contacts)} total contacts")

    print(f"=== Filtering to verified emails ===")
    verified = filter_verified(contacts)
    print(f"Kept {len(verified)} verified leads")

    if not verified:
        print("No verified leads to upload. Exiting.")
        sys.exit(0)

    print(f"=== Uploading to campaign {campaign_id} ===")
    upload_to_campaign(verified, campaign_id)
    print("Done!")


if __name__ == "__main__":
    main()
