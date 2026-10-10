#!/usr/bin/env python3
"""
HVAC State Email Personalization — Anti-AI Angle
==================================================
Uses pre-verified anti-AI framework templates from cold-email-personalized-agent skill.
Generates 4-email per-lead sequences with resolved Spintax, risk reversal rotation, and framework variation.
Usage: python3 hvac_state_personalize.py <input_leads.json> <output_personalized.json>

Input JSON format: [{"company": "...", "city": "...", "state": "...", "email": "...", "website": "...", "rating": "...", "reviews": "..."}]
Output: Instantly-ready JSON with custom_fields for email_subject, email_body, email2_subject, email2_body, email3_body, email4_body
"""

import json
import random
import re
import sys

random.seed(42)  # Reproducible rotation

# ── Spintax Resolver ────────────────────────────────────────────────
# Instantly does NOT support Spintax natively. {option1|option2} goes out as
# literal text. We pre-resolve all Spintax at generation time — randomly pick
# one variant per block so the email arrives clean.

def resolve_spintax(text):
    """Replace {opt1|opt2|opt3} patterns with a randomly chosen option."""
    def _replace(match):
        options = match.group(1).split('|')
        return random.choice(options)
    return re.sub(r'\{([^}]+)\}', _replace, text)

# ── Data Loading ────────────────────────────────────────────────────
def load_leads(path):
    with open(path) as f:
        return json.load(f)

# ── First Name Extraction ───────────────────────────────────────────
def extract_first_name(company_name):
    """Extract a usable first name from company name. Fall back to 'there'."""
    if not company_name:
        return "there"
    name = company_name.strip()
    # Remove common suffixes
    for suffix in [" LLC", " Inc", " Corp", " Ltd", " Co", " Services", " Solutions",
                   " Heating", " Air Conditioning", " Cooling", " Plumbing", " Mechanical",
                   " & Air", " and Air", " Heating &", " Heating and"]:
        name = name.replace(suffix, "")
    name = name.strip()
    # Take first word as potential first name
    first = name.split()[0] if name.split() else ""
    # Filter out obvious non-names (narrow list — business names like "United", "Ideal" are OK)
    if not first or len(first) <= 1:
        return "there"
    if first.upper() in ("A", "AC", "HVAC", "THE", "ALL", "AAA", "A1", "24", "24/7", "911",
                         "PRO", "DR", "MR", "AIR", "COOL", "ECO"):
        return "there"
    if first.isdigit():
        return "there"
    if len(first) == 1:
        return "there"
    # Clean punctuation
    first = re.sub(r'[^a-zA-Z\'-]', '', first)
    if len(first) <= 1:
        return "there"
    return first

# ── Review Text Formatter ───────────────────────────────────────────
def format_review_text(rating, reviews):
    """Format rating + review count into a natural reference."""
    try:
        r = float(rating) if rating else 0
        c = int(reviews) if reviews else 0
    except (ValueError, TypeError):
        r, c = 0, 0
    
    if r >= 4.5 and c >= 100:
        return f"{r} stars with {c} reviews"
    elif r >= 4.0 and c >= 20:
        return f"{r} stars and {c} reviews"
    elif r >= 4.0:
        return f"{r} stars"
    elif c > 0:
        return f"{c} reviews on Google"
    else:
        return "solid reviews on Google"

# ── Risk Reversal Options ───────────────────────────────────────────
RISK_REVERSALS = [
    "If the appointments aren't coming in, you don't owe us anything.",
    "If you're not seeing better results than before, we keep going at no charge until you do.",
    "We guarantee someone is on your phones every single day. If we don't deliver, we work for free until we do.",
    "No contracts. No lock-in. If it's not working, you leave.",
    "If your calendar isn't stronger than before we started, we keep working until it is — on us.",
]

# ── CTA Spintax Patterns ────────────────────────────────────────────
CTA_PATTERNS = [
    "{Worth a look|Something worth exploring|Would this be helpful}?",
    "{Is that something you'd want to hear more about|Would you want more info on how that works|Want me to send over some details}?",
    "Is {outbound calling|keeping the pipeline full|filling the calendar} something {you've got handled|that's on your radar|that's slipping right now}?",
    "{How are you handling|What does your process look like for} {outbound|customer follow-up|booking calls} right now?",
]

# ── Pain Point References (for Email 3/4) ───────────────────────────
PAIN_POINTS = [
    "keeping the phones ringing",
    "keeping your calendar full",
    "filling your schedule",
    "customer follow-up",
    "getting more calls booked",
    "outbound calling",
    "growing without more ad spend",
]

# ── Framework Templates ─────────────────────────────────────────────
# All pre-verified against banned-word list. Spintax resolved at output time.

def f1_the_phones_are_quiet(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, {review_text} — impressive. But when someone in {city} needs a new system or emergency repair, there's a gap between their search and your phone ringing. We embed a real person who calls your customers and prospects every day. No AI chatbots. No automated sequences. No guessing games with ads. Just human outbound calls — the thing that actually works. {risk} {cta}"

def f2_ads_are_broken(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, {review_text} tells me you do good work in {city}. But most HVAC companies are burning cash on ads and lead gen platforms hoping the phone rings. Meanwhile, customers are tired of the AI hype and chatbots. They want a real person to call them. We embed someone on your phones who calls your customers daily. Actual human conversations. Zero ad dependency. {risk} {cta}"

def f3_before_there_were_ads(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, before Google Ads, before AI chatbots, before the endless content grind — HVAC companies grew by doing great work and picking up the phone. {review_text} tells me you've got the great work part figured out. We handle the phone part. A real person calls your customers and prospects every day. Old school? Absolutely. Works? Every time. {risk} {cta}"

def f4_people_want_a_human(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, here's the thing about {review_text} — people in {city} clearly trust your work. But in 2026, everyone is drowning in AI chatbots, automated texts, and follow-up sequences. Your customers are tired of it. They want someone to call them. We embed a real person on your phones who does exactly that. Human voice. Real conversations. Daily calls. {risk} {cta}"

def f5_everyone_has_ai(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, every HVAC company in {city} is now running the same playbook — AI chatbots, automated emails, ad retargeting. {review_text} tells me you've got something better: actual trust from actual customers. We help you put that to work differently. A real person calls your customers. Every day. No AI hype. No automation. Just human conversations that fill your schedule. {risk} {cta}"

def f6_the_google_problem(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, {review_text} in {city} — impressive. But here's the catch: Google controls who sees those reviews. Your next customer might be searching right now and never find you. We take a different approach. A real person calls your customers and prospects directly. No AI. No SEO guessing. No ad auctions. Just human outreach. {risk} {cta}"

def f7_your_list_is_a_goldmine(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, {review_text}. That's a lot of customers who've trusted {company} in {city}. But here's my question — how many of them have heard from you recently? Not an automated email. Not a text blast. A real phone call. We embed a real person who calls your past customers every day. Checks in. Books tune-ups. Reactivates old maintenance agreements. No AI. No automation. Just human follow-up that actually works. {risk} {cta}"

def f8_the_silent_bleed(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, here's something most {city} HVAC companies don't track: how many quotes they send that never turn into change-outs. How many service calls that could've been maintenance agreements. That silent bleed is real. We embed a real person who calls those leads — the ones who got a quote but went quiet, the ones who needed a follow-up. Human voice. No AI. No automation. Just calls that close. {risk} {cta}"

def f9_competitors_phones_ringing(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, {city} is a competitive HVAC market. {review_text} shows you're holding your own. But here's what's happening: your competitors' phones are ringing because someone is actually calling their customers. Not AI. Not ads. Not automated sequences. Real human beings making calls. We embed that same person on your phones. {risk} {cta}"

def f10_go_direct(first, city, review_text, risk, cta, company):
    return f"{{Hey|Hi|Hello}} {first}, between lead gen platforms, ad networks, and middlemen, HVAC companies in {city} are sending money to 3-4 different parties just to maybe get a phone call. {review_text} proves you don't need a middleman. You need someone calling your customers directly. We embed a real person who does exactly that. No AI. No platforms. No per-lead nonsense. Just human calls. {risk} {cta}"

FRAMEWORKS = [
    ("#1 - The Phones Are Quiet", f1_the_phones_are_quiet),
    ("#2 - Ads Are Broken", f2_ads_are_broken),
    ("#3 - Before There Were Ads", f3_before_there_were_ads),
    ("#4 - People Want a Human", f4_people_want_a_human),
    ("#5 - Everyone Has AI - Nobody Has This", f5_everyone_has_ai),
    ("#6 - The Google Problem", f6_the_google_problem),
    ("#7 - Your List Is a Goldmine", f7_your_list_is_a_goldmine),
    ("#8 - The Silent Bleed", f8_the_silent_bleed),
    ("#9 - Your Competitors' Phones Are Ringing", f9_competitors_phones_ringing),
    ("#10 - Go Direct", f10_go_direct),
]

# ── Subject Line Generator ──────────────────────────────────────────
SUBJECTS = [
    "your phones",
    "quick thought",
    "your list",
    "different angle",
    "quick idea",
    "real talk",
    "the quiet ones",
    "your customers",
    "google reviews",
    "shoulder season",
    "ads vs calls",
    "your pipeline",
]

def gen_subject(framework_name):
    mapping = {
        "#1": "your phones",
        "#2": "ads vs calls",
        "#3": "quick thought",
        "#4": "your customers",
        "#5": "different angle",
        "#6": "google reviews",
        "#7": "your list",
        "#8": "the quiet ones",
        "#9": "real talk",
        "#10": "quick idea",
    }
    for key, subj in mapping.items():
        if framework_name.startswith(key):
            return subj
    return random.choice(SUBJECTS)

# ── Main Processing ─────────────────────────────────────────────────
def process_lead(lead, idx, risk_idx, cta_idx):
    """Generate 4-email sequence for a single lead."""
    company = lead.get('company', 'Unknown')
    city = lead.get('city', 'your area')
    state = lead.get('state', 'your state')
    location = f"{city}, {state}" if city else state
    rating = lead.get('rating', '')
    reviews = lead.get('reviews', '')
    email = lead.get('email', '')
    
    first = extract_first_name(company)
    review_text = format_review_text(rating, reviews)
    
    # Framework selection — deterministic rotation
    f1_idx = idx % len(FRAMEWORKS)
    f2_idx = (idx + 3) % len(FRAMEWORKS)  # different framework for email 2
    
    f1_name, f1_fn = FRAMEWORKS[f1_idx]
    f2_name, f2_fn = FRAMEWORKS[f2_idx]
    
    risk = RISK_REVERSALS[risk_idx % len(RISK_REVERSALS)]
    risk2 = RISK_REVERSALS[(risk_idx + 1) % len(RISK_REVERSALS)]
    
    cta = CTA_PATTERNS[cta_idx % len(CTA_PATTERNS)]
    cta2 = CTA_PATTERNS[(cta_idx + 1) % len(CTA_PATTERNS)]
    
    pain = random.choice(PAIN_POINTS)
    
    # Generate emails
    email_body = f1_fn(first, city, review_text, risk, cta, company)
    email2_body = f2_fn(first, city, review_text, risk2, cta2, company)
    
    email_subject = gen_subject(f1_name)
    email2_subject = gen_subject(f2_name)
    
    # Email 3 — short bump
    email3_body = f"{{Hey|Hi}} {first}, did that last note land? Curious if {pain} is still on your radar."
    
    # Email 4 — breakup
    email4_body = f"{{Hey|Hi}} {first}, I'll leave you alone after this. If keeping your phones ringing isn't top of mind right now, totally get it. But if it is, this would be worth 5 minutes. Either way, no hard feelings."
    
    return {
        "first_name": first,
        "last_name": company.split()[-1] if company.split()[-1] not in ("LLC", "Inc", "Ltd", "Corp") else company.split()[0] if len(company.split()) > 1 else "",
        "email": email,
        "company_name": company,
        "website": lead.get('website', ''),
        "location": location,
        "custom_fields": {
            "email_subject": email_subject,
            "email_body": resolve_spintax(email_body),
            "email2_subject": email2_subject,
            "email2_body": resolve_spintax(email2_body),
            "email3_body": resolve_spintax(email3_body),
            "email4_body": resolve_spintax(email4_body),
        }
    }

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'leads.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'personalized.json'
    
    leads = load_leads(input_path)
    print(f"Processing {len(leads)} leads...")
    
    results = []
    for i, lead in enumerate(leads):
        result = process_lead(lead, i, i, i)
        results.append(result)
    
    # Word count check
    word_counts = []
    too_long = 0
    for r in results:
        wc = len(r['custom_fields']['email_body'].split())
        word_counts.append(wc)
        if wc > 100:
            too_long += 1
    
    avg_wc = sum(word_counts) / len(word_counts)
    print(f"Average word count: {avg_wc:.1f}")
    print(f"Emails >100 words: {too_long}/{len(results)}")
    print(f"Range: {min(word_counts)}-{max(word_counts)}")
    
    # Output
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Output: {output_path} ({len(results)} leads — Spintax resolved, clean)")
    
    # Show sample
    print("\n--- Sample Email ---")
    sample = results[0]
    print(f"To: {sample['first_name']} at {sample['company_name']}")
    print(f"Subject: {sample['custom_fields']['email_subject']}")
    print(f"Body: {sample['custom_fields']['email_body']}")

if __name__ == '__main__':
    main()
