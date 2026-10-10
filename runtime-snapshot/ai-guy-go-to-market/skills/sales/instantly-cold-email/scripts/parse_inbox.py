#!/usr/bin/env python3
"""Parse Instantly inbox JSON and summarize replies by campaign/date.

Usage:
  1. Instantly inbox replies --format json > /tmp/inbox_all.json
  2. python3 scripts/parse_inbox.py /tmp/inbox_all.json

Outputs:
  - Replies grouped by campaign with date, lead name, email, status
  - Today's replies
  - Unread replies with ⚠️ flag
"""

import json
import sys
from datetime import datetime


def parse_inbox(filepath):
    with open(filepath) as f:
        data = json.load(f)

    replies = data.get('data', [])
    today = datetime.utcnow().strftime('%Y-%m-%d')

    campaign_replies = {}
    today_replies = []
    unread_replies = []

    for r in replies:
        cid = r.get('email_campaign_id')
        lrt = r.get('last_reply_time', '')[:10]
        has_unread = r.get('has_new_unread_email', False)
        name = f"{r.get('lead_first_name','')} {r.get('lead_last_name','')}".strip()
        email = r.get('lead_email','')
        cname = r.get('email_campaign_name', '')
        lead_id = r.get('email_lead_id')

        entry = {
            'cid': cid,
            'cname': cname,
            'date': lrt,
            'name': name,
            'email': email,
            'lead_id': lead_id,
            'unread': has_unread,
            'status': r.get('lead_status', ''),
        }

        campaign_replies.setdefault(cid, []).append(entry)
        if lrt == today:
            today_replies.append(entry)
        if has_unread:
            unread_replies.append(entry)

    print("=== Campaign Reply Summary ===")
    for cid, entries in sorted(campaign_replies.items()):
        latest = max(e['date'] for e in entries)
        unread_count = sum(1 for e in entries if e['unread'])
        print(f"Campaign {cid} ({entries[0]['cname']}): {len(entries)} replies, latest={latest}, unread={unread_count}")
        for e in entries:
            flag = " ⚠️ UNREAD" if e['unread'] else ""
            print(f"  {e['date']} | {e['name']} ({e['email']}) | {e['status']}{flag}")

    print(f"\n=== Today's Replies ({today}) ===")
    if today_replies:
        for r in today_replies:
            print(f"  {r['name']} ({r['email']}) | Campaign {r['cid']} ({r['cname']})")
    else:
        print("  NONE")

    print(f"\n=== Unread Replies ===")
    if unread_replies:
        for r in unread_replies:
            print(f"  {r['name']} ({r['email']}) | Campaign {r['cid']} ({r['cname']})")
    else:
        print("  NONE")

    # Return structured data for programmatic use
    return {
        'campaign_replies': campaign_replies,
        'today_replies': today_replies,
        'unread_replies': unread_replies,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 parse_inbox.py <inbox_json_file>")
        sys.exit(1)
    parse_inbox(sys.argv[1])
