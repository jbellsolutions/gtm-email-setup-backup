#!/usr/bin/env python3
"""
HVAC Owned Audience v1 — Personalized Email Generator (Reference Implementation)
Generates per-lead custom emails using the 10 HVAC partnership frameworks.
Uses deterministic company-name hash rotation + available lead signals.

See /tmp/hvac_email_gen.py for the latest version used in production.
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

def clean_first_name(name, company):
    """Fix garbled first names from ListKit extractions."""
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
                         "texas", "preferred", "gator", "lone"}
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
    parts = location.split(",")[0].strip()
    return parts.title()

FRAMEWORK_NAMES = [
    "Who's In Their House", "Shared-Lead Trap", "Referral System",
    "Local Show Engine", "Authority Gap", "Dead List",
    "One Per Market", "Realtor Pipeline", "Property Manager Play",
    "Ten Years In Home Services"
]

def select_framework(lead, idx):
    company = lead.get("company", "")
    return sum(ord(c) for c in company) % 10