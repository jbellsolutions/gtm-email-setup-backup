#!/usr/bin/env python3
"""
HVAC Owned Audience v1 — Personalized Email Generator
Generates per-lead custom emails using the 10 HVAC partnership frameworks
from hvac-owned-audience-frameworks-v1.md.

Usage:
    python3 hvac_owned_audience_gen.py

Input: /tmp/hvac_all_leads.json (from Instantly CLI extraction)
Output: /tmp/hvac_owned_audience_Instantly.csv (Instantly-ready CSV)

Features:
- Deterministic framework rotation via company name hash
- clean_company() strips "solutions", "innovative" from company names to avoid banned-word hits
- clean_first_name() fixes garbled ListKit extractions
- Skips generic emails (info@, hello@, etc.) and bad first names
- Generates 4-email sequences (email 1-4)
- Word count verification (target: 50-100)
- Banned word filtering
"""
import json, re, random
from collections import Counter

BANNED = {
    "price", "cost", "investment", "spend", "budget", "unlock", "10x",
    "synergy", "leverage", "innovative", "cutting-edge", "solution",
    "game-changer", "transform", "revolutionize", "scale your", "disrupt",
    "guaranteed", "comfort solutions", "hvac solutions"
}

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    for word in BANNED:
        text = re.sub(rf'\b{word}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'  +', ' ', text).strip()
    return text

def clean_company(company):
    """Strip banned-word-containing suffixes from company names for email display."""
    c = re.sub(r'\b\w*solutions?\w*\b', '', company, flags=re.IGNORECASE)
    c = re.sub(r'\b\w*innovative\w*\b', '', c, flags=re.IGNORECASE)
    c = re.sub(r'  +', ' ', c).strip()
    if len(c) < 4:
        return company
    return c

def word_count(text):
    return len(text.split())

def clean_first_name(name, company):
    bad = {"there", "", "null", "none", "nan"}
    if name.lower().strip() in bad:
        company_words = company.split()
        skip = {"the", "a", "ac", "air", "heating", "conditioning", "hvac",
                "plumbing", "cooling", "mechanical", "services", "service",
                "and", "&", "inc", "llc", "co", "company", "comfort",
                "refrigeration", "solutions", "home", "pro", "brothers"}
        bad_indicators = {"conditioning", "commercial", "service",
                         "cool", "ideal", "fuse", "royal", "florida",
                         "solutions", "innovative", "affordable", "premium",
                         "maximum", "elevated", "alpha", "atlantic", "united",
                         "texas", "preferred", "gator", "lone", "adept",
                         "eze", "bcs", "sheet", "pro-hvacr", "relyonllc",
                         "sub-thermal", "alamance", "nc", "crothers",
                         "pabstoling", "empiremfort", "farmers"}
        for w in company_words:
            clean = re.sub(r'[^a-zA-Z]', '', w)
            if clean.lower() not in skip and len(clean) >= 2:
                if clean.lower() not in bad_indicators:
                    return clean.title()
        return "there"
    return name.strip()

def extract_city(location):
    if not location:
        return ""
    return location.split(",")[0].strip().title()

# ── 10 HVAC Owned Audience Frameworks ──────────────────────────
# Each returns (subject, body) tuple.

def fw1_whos_in_their_house(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["quick thought", "the roofers", "your customers"]
    body = f"Hey {first_name},\n\n"
    if city:
        body += f"Saw {company} handles AC across {city} — solid reviews naming your crews.\n\n"
    else:
        body += f"Saw {company} handles AC in the area — solid reviews naming your crews.\n\n"
    body += "Quick thought: the roofers, plumbers, and home inspectors near you are standing in your future customers' houses every day, and most have no AC company they consistently send people to.\n\n"
    body += "I set those partnerships up. Trained under Jay Abraham — the strategy big companies use, brought to local AC.\n\n"
    body += f"Want me to send a short version of what this would look like for {company}, plus how it played out for another AC company in a different market?"
    return random.choice(subjects), clean_text(body)

def fw2_shared_lead_trap(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["bought leads", "the lead game", "quick one"]
    body = f"Hey {first_name},\n\n"
    body += "You already know how those lead platforms work: they sell the same homeowner to four other companies, then it's a race to the phone and a bidding war nobody wins.\n\n"
    body += "I build the other channel — partnerships with the plumbers, roofers, and realtors who already have your customers' trust, sending people who only call you.\n\n"
    body += f"Want me to send a short breakdown of what that would look like for {company}, plus a case study from another AC company we set this up for?"
    return random.choice(subjects), clean_text(body)

def fw3_referral_system(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["referrals", "word of mouth", "quick question"]
    body = f"Hey {first_name},\n\n"
    body += "Here's the thing about referrals: they close better than anything you buy, but most AC companies get them by luck. A happy customer mentions you at a barbecue, or doesn't.\n\n"
    body += "I turn that into a system — the plumbers, electricians, and inspectors already in your customers' homes, set up to send people your way on purpose.\n\n"
    body += f"Want me to send a short version of what that system looks like, plus how it played out for another AC company in a different market?"
    return random.choice(subjects), clean_text(body)

def fw4_local_show(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["local show", "podcast idea", "quick idea"]
    body = f"Hey {first_name},\n\n"
    body += "One of the easiest plays I run for AC companies: a simple local show where the owner sits down with the realtors, inspectors, and property managers in your area. You're not pitching them — you're featuring them. Every guest becomes a partner with a reason to send you their people.\n\n"
    body += "Takes an hour a week. I handle the setup and the invites.\n\n"
    body += "Would sitting down with a few local realtors and inspectors be doable for you?"
    return random.choice(subjects), clean_text(body)

def fw5_authority_gap(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["noticed something", "your market", "heads up"]
    body = f"Hey {first_name},\n\n"
    if city:
        body += f"Was looking around {city} and noticed something — none of the AC companies there have any real presence beyond ads and a Google profile.\n\n"
    else:
        body += "Was looking around your market and noticed something — none of the AC companies there have any real presence beyond ads and a Google profile.\n\n"
    body += "That's normal, until one owner starts a local home show, gets friendly with every realtor and inspector in town, and becomes the company people ask for by name. Then everyone else is fighting over what's left.\n\n"
    body += "I build that engine — the show, the partners, the name people repeat. Simpler than it sounds.\n\n"
    body += f"Want me to send a short version of what it would look like for {company}, plus how it played out for another AC company?"
    return random.choice(subjects), clean_text(body)

def fw6_dead_list(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["old customers", "your list", "quick thought"]
    body = f"Hey {first_name},\n\n"
    body += "Here's what most owners forget: your list is full of people due for a replacement who haven't heard from you since the invoice. Calling them cold feels like begging. A local show and a partner network give you a reason to land in their inbox that isn't 'buy something.'\n\n"
    body += f"Want me to send a short version of how we turned an old customer list back on for another AC company?"
    return random.choice(subjects), clean_text(body)

def fw7_one_per_market(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["your market", "one thing", "quick heads up"]
    body = f"Hey {first_name},\n\n"
    if city:
        body += f"Up front: I set this up for one AC company per market, and nobody has {city} yet.\n\n"
    else:
        body += "Up front: I set this up for one AC company per market, and your market's still open.\n\n"
    body += "The play — partnerships with the roofers, plumbers, realtors, and property managers already standing in your future customers' homes, plus a simple local show that makes them want to promote you. Once one company owns those relationships, there isn't room for a second.\n\n"
    body += "Your reviews and years in town made you my first call.\n\n"
    body += "Want first look at it before I go down the list?"
    return random.choice(subjects), clean_text(body)

def fw8_realtor_pipeline(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["realtors", "home sales", "quick idea"]
    body = f"Hey {first_name},\n\n"
    body += "Every home sale in your area triggers an inspection, and half those reports flag the HVAC. The realtors and inspectors on those deals decide who gets that call — and most of them have no go-to AC company. That's a pipeline that doesn't care what leads cost these days.\n\n"
    body += "I set those relationships up as real partnerships, not a business-card drop.\n\n"
    body += f"Want me to send a short breakdown of the realtor play, plus how it worked for another AC company in a different market?"
    return random.choice(subjects), clean_text(body)

def fw9_property_manager(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["property managers", "one relationship", "quick one"]
    body = f"Hey {first_name},\n\n"
    body += "One property manager runs hundreds of units, and every unit has equipment that fails on schedule. Land three or four of those relationships and you've got steady work all year — no shoulder-season cliff, no chasing one-off calls.\n\n"
    body += "Getting in isn't about bidding lowest. It's about being the company they already know and trust. That's what I build — partnerships plus a simple local presence PMs actually notice.\n\n"
    body += f"Want me to send a short version of the property manager play, plus how it went for another AC company?"
    return random.choice(subjects), clean_text(body)

def fw10_ten_years(first_name, company_raw, city, state, signals):
    company = clean_company(company_raw) if company_raw else company_raw
    subjects = ["back in the day", "home services", "quick story"]
    body = f"Hey {first_name},\n\n"
    body += "Quick story: I spent ten years working with local home services — AC and roofing — back when buying leads was profitable and the SEO tricks still worked. Got video from those days to prove it. Neither works like that anymore.\n\n"
    body += "Ads still have a place. They just can't be the only channel.\n\n"
    if city:
        body += f"I'll map the businesses in {city} already sitting on your customers — at no charge, just to show you the potential. Want me to put it together for {company}?"
    else:
        body += f"I'll map the businesses already sitting on your customers — at no charge, just to show you the potential. Want me to put it together for {company}?"
    return random.choice(subjects), clean_text(body)

FRAMEWORKS = [fw1_whos_in_their_house, fw2_shared_lead_trap, fw3_referral_system,
              fw4_local_show, fw5_authority_gap, fw6_dead_list,
              fw7_one_per_market, fw8_realtor_pipeline, fw9_property_manager,
              fw10_ten_years]

FW_NAMES = ["Who's In Their House", "Shared-Lead Trap", "Referral System",
            "Local Show Engine", "Authority Gap", "Dead List",
            "One Per Market", "Realtor Pipeline", "Property Manager Play",
            "Ten Years In Home Services"]

def select_framework(lead):
    company = lead.get("company", "")
    return sum(ord(c) for c in company) % 10

def gen_email2(first_name, company, city, state, fw1_idx):
    fw2_idx = (fw1_idx + 3) % 10
    subj, body = FRAMEWORKS[fw2_idx](first_name, company, city, state, {})
    return random.choice(["different thought", "another angle", "one more thing"]), body

def gen_email3(first_name, company, city, state):
    return "re:", f"Hey {first_name}, did my last note land? Curious if referral partnerships are on your radar this year, or if it's all ads and bought leads for now."

def gen_email4(first_name, company, city, state):
    if city:
        body = f"Hey {first_name}, last one from me. If getting the roofers, realtors, and inspectors in {city} to send you their people isn't a priority right now, no worries at all. If it ever is, I'm around — I'll even map it out at no charge, just to show you the potential. Either way, good luck out there."
    else:
        body = f"Hey {first_name}, last one from me. If getting the roofers, realtors, and inspectors near you to send you their people isn't a priority right now, no worries at all. If it ever is, I'm around — I'll even map it out at no charge, just to show you the potential. Either way, good luck out there."
    return "last one", body

def main():
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hvac_all_leads.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "/tmp/hvac_owned_audience_Instantly.csv"
    
    with open(input_file) as f:
        leads = json.load(f)
    
    print(f"Processing {len(leads)} HVAC leads from {input_file}...")
    
    output = []
    skipped_generic = skipped_bad_name = word_count_issues = 0
    
    generic_prefixes = {"info", "hello", "contact", "support", "sales",
                       "admin", "office", "service", "billing", "help",
                       "privacy", "abuse", "postmaster", "webmaster"}
    
    for i, lead in enumerate(leads):
        if i % 500 == 0:
            print(f"  {i}/{len(leads)}...")
        
        email = lead.get("email", "").lower().strip()
        company = lead.get("company", "")
        
        if email.split("@")[0].lower() in generic_prefixes:
            skipped_generic += 1
            continue
        
        first_name = clean_first_name(lead.get("first_name", ""), company)
        if first_name.lower() == "there":
            skipped_bad_name += 1
            continue
        
        location = lead.get("location", "")
        city = extract_city(location)
        cf = lead.get("custom_fields", {})
        
        fw_idx = select_framework(lead)
        subj, body = FRAMEWORKS[fw_idx](first_name, company, city, extract_city(location) if location else "", cf)
        
        wc = word_count(body)
        if wc < 50 or wc > 100:
            word_count_issues += 1
        
        e2_subj, e2_body = gen_email2(first_name, company, city, extract_city(location) if location else "", fw_idx)
        e3_subj, e3_body = gen_email3(first_name, company, city, extract_city(location) if location else "")
        e4_subj, e4_body = gen_email4(first_name, company, city, extract_city(location) if location else "")
        
        output.append({
            "first_name": first_name,
            "last_name": lead.get("last_name", ""),
            "email": email,
            "company": company,
            "email_subject": subj,
            "email_body": body,
            "email2_subject": e2_subj,
            "email2_body": e2_body,
            "email3_subject": e3_subj,
            "email3_body": e3_body,
            "email4_subject": e4_subj,
            "email4_body": e4_body,
        })
    
    # Save CSV
    with open(output_file, "w") as f:
        f.write("first_name,last_name,email,company,email_subject,email_body,email2_subject,email2_body,email3_subject,email3_body,email4_subject,email4_body\n")
        for o in output:
            def csv_escape(s):
                s = str(s).replace('"', '""')
                return f'"{s}"' if ',' in s or '"' in s or '\n' in s else s
            row = [csv_escape(o[k]) for k in ["first_name","last_name","email","company",
                     "email_subject","email_body","email2_subject","email2_body",
                     "email3_subject","email3_body","email4_subject","email4_body"]]
            f.write(",".join(row) + "\n")
    
    print(f"\nResults: {len(output)} leads saved to {output_file}")
    print(f"  Skipped generic: {skipped_generic}")
    print(f"  Skipped bad names: {skipped_bad_name}")
    print(f"  Word count issues: {word_count_issues}")
    
    fw_dist = Counter(o["framework"] for o in output if "framework" in o)
    if fw_dist:
        print("Framework distribution:", dict(fw_dist))

if __name__ == "__main__":
    main()