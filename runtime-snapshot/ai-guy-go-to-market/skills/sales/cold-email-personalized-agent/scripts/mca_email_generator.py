#!/usr/bin/env python3
"""
MCA Cold Email Generator — programmatic website signal extraction + framework selection + email generation.
Reads a JSON file of MCA/business-lending leads, curls each website, picks the best framework from 
the 10 MCA pain-point frameworks, and generates personalized emails.

Input: JSON array of leads with fields: first_name, email, company, domain, website, notes
Output: Instantly-ready CSV (first_name, last_name, email, company_name, email_subject, email_body)

Usage:
    python3 mca_email_generator.py leads.json output.csv

Dependencies: curl (system), Python 3 stdlib only
"""

import json
import re
import subprocess
import random
import csv
import sys

# ── Framework keyword mapping ──────────────────────────────────
FW_KEYWORDS = {
    'empty_seats': ['careers', 'hiring', 'join our team', 'open positions', 'we are hiring', 'job openings', 'work with us'],
    'aged_data': ['UCC', 'ucc', 'aged lead', 'trigger lead', 'trigger data', 'mailing list', 'aged data'],
    'sms_broken': ['SMS', 'text message', 'texting', 'text blast', 'bulk text', 'sms campaign'],
    'closers_cold_calling': ['closer', 'closers', 'live transfer', 'live transfers', 'warm transfer', 'setter', 'appointment setter'],
    'speed_kills': ['same day', 'within hours', '24 hour', 'instant approval', 'rapid funding', 'minutes', 'as fast as'],
    'dialer_bills': ['dialer', 'power dialer', 'predictive dialer', 'auto dialer', 'parallel dialer'],
    'renewals_walking': ['renewal', 'renewals', 'repeat business', 'refinancing', 'additional advance', 'second position'],
    'email_spam': [],   # fallback for small sites
    'app_volume': [],   # default for medium+ sites
    'revolving_door': [],  # hard to detect programmatically
}

RISK_REVERSALS = [
    "If the appointments don't come in, you don't owe us anything. Simple as that.",
    "We guarantee someone is on your phones every single day, managed and monitored. If we don't deliver, we keep going until we do.",
    "No long-term contracts. 90 days, and if it's not working, you walk.",
    "We replace anyone who leaves or underperforms — that's on us, not you.",
    "If we can't get your SMS actually delivered within the first two weeks, we keep working at no charge until we do.",
]

FRAMEWORK_SUBJECTS = {
    'empty_seats': ['quick question', 'your floor', 'staffing'],
    'aged_data': ['your aged data', 'quick thought', 'untapped data'],
    'sms_broken': ['sms question', 'your texts', 'text deliverability'],
    'app_volume': ['timing', 'right now', 'app volume'],
    'closers_cold_calling': ['your closers', 'quick thought', 'prospecting'],
    'revolving_door': ['familiar?', 'staffing', 'quick question'],
    'email_spam': ['your emails', 'inbox question', 'email deliverability'],
    'speed_kills': ['speed', 'honest question', 'first call'],
    'dialer_bills': ['your dialer', 'quick one', 'dialer costs'],
    'renewals_walking': ['your renewals', 'funded clients', 'repeat business'],
}

BAD_FIRST_NAMES = {
    'info', 'contact', 'support', 'hello', 'admin', 'sales', 'linkedin', 'team',
    'office', 'customersupport', 'customer', 'service', 'help', 'billing', 'accounts',
    'marketing', 'operations', 'legal', 'hr', 'careers', 'press', 'media', 'webmaster',
    'postmaster', 'noreply', 'no-reply', 'mail', 'email', 'submissions',
}

FIRST_NAME_FIXES = {
    'mmarkowitz': 'Mark', 'mjackson': 'Mike', 'lpeyton': 'LP',
    'brianroe': 'Brian', 'jnathaniel': 'J', 'jamesrath': 'James',
    'sbermingham': 'Scott', 'jschwartz': 'J', 'chen': 'Chen', 'cfurman': 'CF',
}

SKIP_TLDS = ['.za', '.co.uk', '.au', '.nz', '.in']
CONSUMER_KEYWORDS = ['payday', 'installment loan', 'car title', 'bad credit loan']
LENDING_KEYWORDS = [
    'merchant cash', 'cash advance', 'working capital', 'business loan', 'sba loan',
    'equipment financing', 'commercial loan', 'business funding', 'revenue based',
    'invoice factoring', 'line of credit', 'term loan', 'small business',
]

# ── Helpers ────────────────────────────────────────────────────

def fetch_text(url):
    """Curl a website and extract raw text (first 5000 chars)."""
    if not url:
        return ""
    try:
        r = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '8', '-A', 'Mozilla/5.0', url],
            capture_output=True, text=True, timeout=12
        )
        t = re.sub(r'<script[^>]*>.*?</script>', '', r.stdout, flags=re.DOTALL | re.IGNORECASE)
        t = re.sub(r'<style[^>]*>.*?</style>', '', t, flags=re.DOTALL | re.IGNORECASE)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'\s+', ' ', t).strip().lower()[:5000]
        return t
    except Exception:
        return ""


def clean_first_name(raw):
    """Extract a usable first name from email local part or raw name."""
    name = raw.strip().lower()
    if name in BAD_FIRST_NAMES:
        return None
    if name in FIRST_NAME_FIXES:
        return FIRST_NAME_FIXES[name]
    if len(name) == 1:
        return raw.capitalize()
    if '.' in raw:
        return raw.split('.')[0].capitalize()
    return name.capitalize()


def pick_framework(text, notes=""):
    """Select best framework based on website text keyword matching."""
    combined = (text + ' ' + (notes or '').lower())
    scores = {}
    for fw, kws in FW_KEYWORDS.items():
        scores[fw] = sum(1 for kw in kws if kw.lower() in combined)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return 'email_spam' if len(text) < 300 else 'app_volume'
    return best


def extract_location(text):
    """Extract 'City, ST' from website text. Returns '' if unclear."""
    m = re.search(
        r'(?:in|serving|based in|located in|office in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}),?\s*'
        r'(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|'
        r'NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)',
        text, re.IGNORECASE
    )
    if m:
        city = m.group(1)
        # Reject garbage: too short, too long, or contains non-name words
        if len(city) < 4 or len(city) > 25:
            return ""
        garbage = {'busi', 'the a', 'cash', 'loan', 'funding', 'capital', 'advance', 'finance'}
        if city.lower() in garbage:
            return ""
        return f"{city}, {m.group(2).upper()}"
    return ""


def extract_lending_types(text):
    """Determine what kind(s) of lending the shop does."""
    types = []
    if any(w in text for w in ['merchant cash', 'cash advance', 'mca ']):
        types.append('MCA')
    if 'sba' in text:
        types.append('SBA')
    if 'equipment' in text and any(w in text for w in ['financ', 'leas']):
        types.append('equipment financing')
    if 'invoice' in text and 'factor' in text:
        types.append('invoice factoring')
    if 'line of credit' in text:
        types.append('lines of credit')
    if 'working capital' in text:
        types.append('working capital')
    return types or ['business lending']


def should_skip(lead, text):
    """Return True if this lead should be excluded."""
    domain = lead.get('domain', '')
    if any(domain.endswith(tld) for tld in SKIP_TLDS):
        return True
    if any(kw in text for kw in CONSUMER_KEYWORDS):
        return True
    if text and not any(kw in text for kw in LENDING_KEYWORDS):
        return True
    return False


# ── Email generation ───────────────────────────────────────────

def generate_email(lead, framework, text, lead_index):
    fn = clean_first_name(lead.get('first_name', '')) or lead.get('company', 'there')
    company = lead.get('company', '')
    lending = extract_lending_types(text)
    ld = lending[0]
    loc = extract_location(text)
    
    risk = RISK_REVERSALS[lead_index % len(RISK_REVERSALS)]
    subject = random.choice(FRAMEWORK_SUBJECTS.get(framework, ['quick question']))
    
    # Relevance line
    if loc and len(loc.split()) <= 3:
        relevance = f"Saw your {ld} operation out of {loc} — looks solid."
    elif company:
        relevance = f"Noticed {company} does {ld} work — looks like a solid operation."
    else:
        relevance = f"Saw your {ld} operation — looks solid."
    
    # Framework-specific content
    pain_map = {
        'empty_seats': "Most lending shops can't keep appointment setters long. Train them, they produce for a month, then gone. Back to square one with leads piling up.",
        'aged_data': "Most shops are sitting on thousands of aged leads — submissions, UCC records, trigger data — that nobody's calling. That's money in a spreadsheet.",
        'sms_broken': "SMS to business owners is brutal right now. Numbers get flagged, carriers crack down, texts don't land. But texting is still the highest-response channel in MCA.",
        'speed_kills': f"In {ld.lower()}, the first call wins. When you're short-staffed, fresh apps sit for hours. By the time your team calls, three other shops already did.",
        'closers_cold_calling': "Your closers should be closing, not cold calling. Every hour they spend dialing data is an hour they're not funding deals.",
        'email_spam': "Most lending shops that try email campaigns end up in spam. No warmup, no metering — emails never hit inboxes. So they give up on the channel.",
        'renewals_walking': "You've already found the business owner, underwrote them, funded the deal. Now they're half paid down and ready for another advance. But nobody's calling them.",
        'dialer_bills': "When you're running a lending floor, per-minute dialer rates on 500+ dials a day add up fast. That's a serious line item.",
        'app_volume': "App volume is surging but most shops don't have enough seats to keep up. Fresh apps go stale in hours while competitors call first.",
        'revolving_door': "Hiring appointment setters in MCA is a nightmare. Most don't last 60 days. Training takes two weeks. By the time they're producing, they're already looking for the next thing.",
    }
    
    value_map = {
        'empty_seats': "We place trained MCA setters on your phones and manage everything. If someone leaves, we replace them — no gap, no headache.",
        'aged_data': "We put trained callers on your aged data every day and run unlimited SMS and email alongside. Your list gets worked.",
        'sms_broken': "We run SMS campaigns with proper deliverability — compliant, registered, metered. Your texts actually get delivered, and we manage responses.",
        'speed_kills': "We put trained callers on your phones who hit fresh leads immediately and grind through aged data all day. SMS and email run alongside.",
        'closers_cold_calling': "We put dedicated setters on the phones who qualify and warm-transfer to your closers. Your closers only talk to people who are ready to move.",
        'email_spam': "We run unlimited email campaigns with proper infrastructure — domain management, warmup, content. Your emails actually land in inboxes.",
        'renewals_walking': "We put people on your phones who run renewal campaigns every day. Your funded clients hear from you first, not a competitor.",
        'dialer_bills': "We have a dialer partnership that gives you unlimited minutes at a flat fee. Scale your dials without scaling your bill.",
        'app_volume': "We place trained callers who dial your leads every day and run unlimited SMS and email alongside. Your apps get worked immediately.",
        'revolving_door': "We handle the hiring, training, and replacement. If someone leaves, we swap them — no gap, no cost, no headache for you.",
    }
    
    cta_map = {
        'empty_seats': "How many setters do you have dialing right now?",
        'aged_data': "How much aged data is sitting untouched right now?",
        'sms_broken': "Have you tried texting your leads recently?",
        'speed_kills': "How fast are your apps getting worked right now?",
        'closers_cold_calling': "Would it help to get your closers off the cold calls?",
        'email_spam': "Are you running any email outreach right now?",
        'renewals_walking': "How many funded clients haven't been called about a renewal?",
        'dialer_bills': "What are you spending on your dialer right now?",
        'app_volume': "How's your team keeping up with the volume right now?",
        'revolving_door': "How many setters have you gone through this year?",
    }
    
    pain = pain_map.get(framework, pain_map['app_volume'])
    value = value_map.get(framework, value_map['app_volume'])
    cta = cta_map.get(framework, cta_map['app_volume'])
    
    greeting = random.choice(['Hey', 'Hi', 'Hello'])
    
    body = f"""{greeting} {fn},

{relevance}

{pain}

{value}

{risk}

{cta}"""
    
    return {
        'first_name': fn,
        'email': lead['email'],
        'company_name': company,
        'framework': framework,
        'subject': subject,
        'email_body': body,
        'word_count': len(body.split()),
        'lending_type': ld,
    }


# ── Main ───────────────────────────────────────────────────────

def main(input_path, output_path):
    with open(input_path) as f:
        leads = json.load(f)
    
    print(f"Processing {len(leads)} leads...")
    results = []
    skipped = 0
    
    for i, lead in enumerate(leads):
        url = lead.get('website', '') or f"https://{lead.get('domain', '')}"
        if not url.startswith('http'):
            url = f'https://{url}'
        
        text = fetch_text(url)
        
        if should_skip(lead, text):
            skipped += 1
            continue
        
        fw = pick_framework(text, lead.get('notes', ''))
        result = generate_email(lead, fw, text, i)
        results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(leads)}...")
    
    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['first_name', 'last_name', 'email', 'company_name', 'email_subject', 'email_body'])
        for r in results:
            writer.writerow([r['first_name'], '', r['email'], r['company_name'], r['subject'], r['email_body']])
    
    # Report
    from collections import Counter
    fw_dist = Counter(r['framework'] for r in results)
    wcs = [r['word_count'] for r in results]
    
    print(f"\nDone! {len(results)} emails generated ({skipped} skipped)")
    print(f"Frameworks: {dict(fw_dist.most_common())}")
    print(f"Words: min={min(wcs)}, max={max(wcs)}, avg={sum(wcs)/len(wcs):.0f}")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 mca_email_generator.py <leads.json> <output.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])