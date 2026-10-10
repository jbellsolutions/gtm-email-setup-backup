#!/usr/bin/env python3
"""
PR Agency Referral Network Email Generator (Trojan Horse Angle)
Reads existing personalized CSV with signals, generates single referral email per lead.

Template: "We get inquiries from people looking for PR agency referrals.
Your name came up. Can we refer people to you?"

SpeakerAgent mentioned as managed service. Single-email campaign. Zero links.

Input: CSV with columns: first_name, email, company_name, signal
Output: Instantly-ready CSV with email_subject + email_body + signal

Usage:
    python3 pr_referral_generator.py [input_csv] [output_csv]
    Default input: /tmp/pr_v2_all_4567.csv (existing personalized CSV)
"""
import csv, random, re, sys

GREETINGS = ["Hey", "Hi", "Hello"]
SUBJECTS = ["referral question", "your name came up", "quick question", "referring clients"]

BANNED = {
    "pay", "price", "cost", "investment", "spend", "budget",
    "unlock", "10x", "synergy", "leverage", "innovative", "cutting-edge",
    "solution", "game-changer", "transform", "revolutionize", "scale your",
    "disrupt", "revolutionary", "guarantee", "roi", "affordable", "cheap",
    "expensive", "fee",
}

SIGNAL_FIXES = [
    # Phrase-level (longest first to avoid partial matches)
    (r'\breturn on investment\b', 'measurable results'),
    (r'\bleverage data-driven\b', 'use data-driven'),
    (r'\binvestment opportunities\b', 'client opportunities'),
    (r'\binvestment firms\b', 'client firms'),
    # Word-level
    (r'\bleverage\b', 'use'),
    (r'\binnovative\b', 'creative'),
    (r'\binvestment\b', 'client'),
    (r'\bbudget\b', 'planning'),
    (r'\bsolution\b', 'approach'),
    (r'\btransform\b', 'reshape'),
    (r'\bscale your\b', 'grow your'),
    (r'\bgame-changer\b', 'difference-maker'),
]

EMAIL_TEMPLATE = """{greeting} {first_name},

Saw {signal_detail} — liked what we saw.

We get dozens of inquiries every month from people looking for a PR agency. Your name came up in some searches. We have a managed service called SpeakerAgent that connects agencies with the right clients.

Can we refer people to you? If so let's hop on a quick call. We'll get a feel for what you do, vet you out a little, and make sure we're clear on how to hand clients off to you.

Worth 15 minutes?"""


def clean_signal(text):
    """Remove/replace banned words from signal text before embedding in email."""
    text = text.strip().rstrip('.,;:')
    for pattern, replacement in SIGNAL_FIXES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = text.strip().rstrip('.,;:')
    if not text or len(text) < 5:
        return "your work"
    return text


def count_words(text):
    return len(text.split())


def check_banned(text):
    words = set(text.lower().split())
    return [w for w in words if w in BANNED]


def generate_email(first_name, signal):
    greeting = random.choice(GREETINGS)
    subject = random.choice(SUBJECTS)
    clean = clean_signal(signal)

    body = EMAIL_TEMPLATE.format(
        greeting=greeting,
        first_name=first_name,
        signal_detail=clean,
    )
    body = re.sub(r'\.{2,}', '.', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    body = body.strip()

    return {
        "subject": subject,
        "body": body,
        "word_count": count_words(body),
        "banned": check_banned(body),
    }


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pr_v2_all_4567.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "/tmp/pr_referral_emails.csv"

    print(f"Reading: {input_csv}")
    with open(input_csv, 'r') as f:
        all_rows = list(csv.DictReader(f))
    print(f"Total leads: {len(all_rows)}")

    results, banned_count, word_counts = [], 0, []
    for row in all_rows:
        gen = generate_email(
            row.get("first_name", "").strip(),
            row.get("signal", "").strip(),
        )
        if gen["banned"]:
            banned_count += 1
        word_counts.append(gen["word_count"])
        results.append({
            "first_name": row.get("first_name", "").strip(),
            "email": row.get("email", "").strip(),
            "company_name": row.get("company_name", "").strip(),
            "domain": row.get("domain", "").strip(),
            "signal": row.get("signal", "").strip(),
            "email_subject": gen["subject"],
            "email_body": gen["body"],
            "word_count": gen["word_count"],
            "has_banned": "yes" if gen["banned"] else "",
        })

    fieldnames = ["first_name", "email", "company_name", "domain", "signal",
                  "email_subject", "email_body", "word_count", "has_banned"]
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    avg_wc = sum(word_counts) / len(word_counts)
    over_100 = sum(1 for wc in word_counts if wc > 100)
    under_50 = sum(1 for wc in word_counts if wc < 50)
    print(f"\n─── QUALITY REPORT ───")
    print(f"Total: {len(results)} leads")
    print(f"Word count: avg={avg_wc:.1f}, min={min(word_counts)}, max={max(word_counts)}")
    print(f"Over 100: {over_100} ({over_100/len(results)*100:.1f}%)")
    print(f"Under 50: {under_50} ({under_50/len(results)*100:.1f}%)")
    print(f"Banned: {banned_count} ({banned_count/len(results)*100:.1f}%)")
    print(f"\nOutput: {output_csv}")

    # Sample emails
    print(f"\n─── SAMPLE EMAILS ───")
    for i in [0, 500, 1500, 2500, 3500]:
        if i >= len(results): break
        r = results[i]
        print(f"\n--- Lead {i+1}: {r['first_name']} @ {r['company_name']} ---")
        print(f"Signal: {r['signal'][:100]}")
        print(f"Subject: {r['email_subject']}")
        print(r['email_body'])
        print(f"WC: {r['word_count']}")


if __name__ == "__main__":
    main()