#!/usr/bin/env python3
"""Batch process job leads: guess domains, find emails via Apify, generate sequences via DeepSeek.

Usage:
    cd /tmp/ai-integraterz-job-scraper
    DEEPSEEK_API_KEY="sk-..." python3 batch_enrich.py
"""

import sqlite3, json, os, re, time
from urllib.parse import urlparse
import urllib.request, ssl

APIFY_TOKEN = "[REDACTED]"
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DB = os.path.join(os.path.dirname(__file__), "..", "backend", "job_scraper.db")
ctx = ssl.create_default_context()

GENERIC_PREFIXES = {
    "info", "contact", "hello", "support", "admin", "sales", "hr",
    "help", "office", "team", "general", "enquiries", "inquiries",
    "noreply", "no-reply", "careers", "jobs", "hiring", "press",
    "media", "marketing", "investors", "webmaster", "abuse", "postmaster",
}


def guess_domain(company_name):
    """Guess a domain from company name."""
    name = company_name.lower().strip()
    for suffix in [" inc", " llc", " ltd", " corp", " corporation", " co.", " co", " limited", " group", " holdings"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    name = re.sub(r'[^a-z0-9]', '', name)
    if not name or len(name) < 2:
        return None
    return f"{name}.com"


def find_emails(domain):
    """Use Apify website-email-phone-finder to find emails for a domain."""
    url = f"https://api.apify.com/v2/acts/mD5Xdfj9XeMS5FWPc/runs?token={APIFY_TOKEN}"
    body = json.dumps({"domains": [domain], "maxEmailsPerDomain": 10}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Content-Type": "application/json"})
    
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = json.loads(resp.read())
        run_id = data["data"]["id"]
    except Exception as e:
        print(f"  Failed to start run for {domain}: {e}")
        return []
    
    for i in range(40):
        time.sleep(2)
        poll_url = f"https://api.apify.com/v2/acts/mD5Xdfj9XeMS5FWPc/runs/{run_id}?token={APIFY_TOKEN}"
        try:
            req = urllib.request.Request(poll_url)
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            sd = json.loads(resp.read())
            status = sd["data"]["status"]
            if status in ("SUCCEEDED", "FAILED", "ABORTED"):
                if status == "SUCCEEDED":
                    ds_id = sd["data"].get("defaultDatasetId")
                    ds_url = f"https://api.apify.com/v2/datasets/{ds_id}/items?token={APIFY_TOKEN}&clean=true&format=json"
                    req = urllib.request.Request(ds_url)
                    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
                    items = json.loads(resp.read())
                    emails = []
                    for item in items:
                        for e in (item.get("emails") or []):
                            if isinstance(e, str):
                                emails.append(e)
                            elif isinstance(e, dict):
                                emails.append(e.get("email", ""))
                    personal = [e for e in emails if e.split("@")[0].lower() not in GENERIC_PREFIXES]
                    return personal
                return []
        except:
            continue
    return []


def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    c.execute("""
        SELECT lr.id, jn.title, jn.company_name, 
               json_extract(jn.normalized_payload, '$.description'),
               jn.total_score, jn.role_category
        FROM leadrecord lr
        JOIN jobnormalized jn ON lr.job_id = jn.id
        WHERE lr.status IN ('qualified', 'contact_needed')
        ORDER BY jn.total_score DESC
    """)
    
    leads = c.fetchall()
    print(f"Processing {len(leads)} leads...")
    
    found_emails = 0
    for i, (lead_id, title, company, desc, score, role) in enumerate(leads):
        domain = guess_domain(company)
        if not domain:
            continue
        
        print(f"\n[{i+1}/{len(leads)}] {company} ({title}) -> {domain}")
        emails = find_emails(domain)
        
        if emails:
            found_emails += 1
            email = emails[0]
            print(f"  ✅ {email}")
            
            c.execute("""
                UPDATE decisioncontact 
                SET email = ?, email_source = 'website_finder'
                WHERE id = (SELECT contact_id FROM leadrecord WHERE id = ?)
            """, (email, lead_id))
            
            c.execute("""
                UPDATE leadrecord 
                SET status = 'qualified', 
                    notes = json_set(coalesce(notes, '{}'), 
                        '$.contact_quality', 'email_found', 
                        '$.contact_note', 'Email found via domain guess')
                WHERE id = ?
            """, (lead_id,))
            conn.commit()
        else:
            print(f"  ❌ No personal emails found")
    
    print(f"\nDone. Found emails for {found_emails}/{len(leads)} leads.")
    conn.close()


if __name__ == "__main__":
    main()
