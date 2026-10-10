#!/usr/bin/env python3
"""Audit Instantly email accounts for deliverability issues.

Usage: python3 audit-accounts.py /tmp/sl_accounts.json
       python3 audit-accounts.py -   (read from stdin)
"""

import json
import sys
from collections import Counter


def audit(data):
    """Analyze a list of Instantly email account objects."""
    total = len(data)
    problems = []
    healthy = 0

    for a in data:
        issues = []

        # Connection health
        if not a.get("is_smtp_success"):
            issues.append(f"SMTP_FAIL: {str(a.get('smtp_failure_error', 'unknown'))[:80]}")
        if not a.get("is_imap_success"):
            issues.append(f"IMAP_FAIL: {str(a.get('imap_failure_error', 'unknown'))[:80]}")

        # Warmup health
        w = a.get("warmup_details") or {}
        w_status = w.get("status", "N/A")
        w_rep = w.get("warmup_reputation", "N/A")
        if w_status not in ("ACTIVE", "N/A"):
            issues.append(f"WARMUP_STATUS:{w_status}")
        try:
            if int(w_rep.replace("%", "")) < 90:
                issues.append(f"LOW_REP:{w_rep}")
        except (ValueError, TypeError):
            pass

        # Rate limits
        sent = a.get("daily_sent_count", 0)
        limit = a.get("message_per_day", 0)
        if limit > 0 and sent >= limit:
            issues.append(f"AT_LIMIT:{sent}/{limit}")

        tags = [t.get("tag_name", "") for t in a.get("tags", [])]

        if issues:
            problems.append({
                "id": a["id"],
                "email": a["from_email"],
                "name": a["from_name"],
                "type": a.get("type", "?"),
                "tags": tags,
                "issues": issues,
                "warmup_rep": w_rep,
                "warmup_status": w_status,
                "smtp": a.get("is_smtp_success"),
                "imap": a.get("is_imap_success"),
                "campaigns": a.get("campaign_count", 0),
                "sent": sent,
                "limit": limit,
            })
        else:
            healthy += 1

    # ---- Report ----
    print(f"Total accounts: {total}")
    print(f"Healthy: {healthy}")
    print(f"Problematic: {len(problems)}")
    print()

    # Problem rate by tag
    print("=== PROBLEM RATE BY TAG ===")
    tag_total = Counter()
    for a in data:
        for t in a.get("tags", []):
            tag_total[t.get("tag_name", "")] += 1
    tag_prob = Counter()
    for p in problems:
        for t in p["tags"]:
            tag_prob[t] += 1
    for tag in sorted(tag_total):
        total_t = tag_total[tag]
        prob = tag_prob.get(tag, 0)
        pct = f"{prob}/{total_t} ({prob / total_t * 100:.0f}%)" if total_t else ""
        flag = " 💀" if total_t > 0 and prob / total_t > 0.5 else ""
        print(f"  {tag}: {pct}{flag}")
    print()

    # Detailed problem list
    print(f"=== PROBLEMATIC ACCOUNTS ({len(problems)}) ===")
    for p in sorted(problems, key=lambda x: (",".join(x["tags"]), x["email"])):
        print(f"\n  ID:{p['id']} | {p['email']} ({p['name']})")
        print(f"  Type: {p['type']} | Tags: {', '.join(p['tags']) if p['tags'] else '(none)'}")
        smtp_icon = "✓" if p["smtp"] else "✗"
        imap_icon = "✓" if p["imap"] else "✗"
        print(f"  SMTP: {smtp_icon} | IMAP: {imap_icon} | Warmup: {p['warmup_status']} (rep: {p['warmup_rep']})")
        print(f"  Campaigns: {p['campaigns']} | Sent: {p['sent']}/{p['limit']}")
        for issue in p["issues"]:
            print(f"  ❌ {issue}")

    # Domain clusters
    print(f"\n=== DOMAIN REPUTATION CLUSTERS ===")
    domain_reps = {}
    for a in data:
        email = a.get("from_email", "")
        if "@" in email:
            domain = email.split("@")[1]
            w = a.get("warmup_details") or {}
            rep = w.get("warmup_reputation", "N/A")
            try:
                rep_val = int(rep.replace("%", ""))
            except (ValueError, TypeError):
                rep_val = None
            if domain not in domain_reps:
                domain_reps[domain] = {"count": 0, "reps": [], "total": 0}
            domain_reps[domain]["count"] += 1
            if rep_val is not None:
                domain_reps[domain]["reps"].append(rep_val)
            domain_reps[domain]["total"] += 1

    flagged_domains = []
    for domain, d in domain_reps.items():
        if d["reps"] and d["count"] >= 3:
            avg_rep = sum(d["reps"]) / len(d["reps"])
            low_count = sum(1 for r in d["reps"] if r < 90)
            if low_count == d["count"]:
                flagged_domains.append((domain, avg_rep, d["count"]))
    flagged_domains.sort(key=lambda x: x[1])
    for domain, avg_rep, count in flagged_domains:
        print(f"  🔴 {domain}: {count} accounts, avg rep {avg_rep:.0f}% — ALL below 90%")

    print()
    print("=== TYPE DISTRIBUTION ===")
    types = Counter(a.get("type", "?") for a in data)
    for t, c in types.most_common():
        print(f"  {t}: {c}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if path == "-":
            data = json.load(sys.stdin)
        else:
            data = json.load(open(path))
    else:
        data = json.load(sys.stdin)
    audit(data)