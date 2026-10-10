#!/usr/bin/env python3
"""Cross-lead similarity + hard-rule sweep for per-lead generated cold email copy.

Catches the template-swap defect class: every lead's email identical except the
company name. Pairwise Jaccard on word sets, per framework key, with
framework-canonical sentence stripping and company/city name removal.

Input: one or more JSON files shaped {"<lead_email>": {"<fw_key>": {"subject": "...", "body": "..."}}}
Optional --packets: JSON shaped {"<lead_email>": {"company": "...", "city": "..."}} for name stripping.

Usage:
  python3 cross_lead_similarity_check.py out_A.json out_B.json --packets packets.json --threshold 0.45

Exit 0 = clean, exit 1 = issues printed. Derived from the working FAP batch10 sweep (2026-09-06).
"""
import argparse
import itertools
import json
import re
import sys

# Framework-designated lines that are ALLOWED to repeat across leads (strip before comparing).
# Extend this list per campaign to match the campaign's framework doc designated lines.
CANONICAL_PATTERNS = [
    r'on july 23 and 24 an fda panel voted yes on the peptides your \w+ already talk about[^.]*',
    r'an fda panel voted yes on the peptides your \w+ already talk about[^.]*',
    r'every (?:member|client|student) (?:in your \w+ )?(?:right now )?is on peptides, hearing about them, or knows somebody who is',
]


def norm_words(text):
    """Lowercase word tokens; punctuation stripped so 'BMX.' -> 'bmx'."""
    return re.findall(r"[a-z0-9'&-]+", text.lower())


def strip_canonical(low_text):
    out = low_text
    for pat in CANONICAL_PATTERNS:
        out = re.sub(pat, ' ', out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('inputs', nargs='+', help='JSON files shaped {email: {fw_key: {subject, body}}}')
    ap.add_argument('--packets', help='optional JSON {email: {company, city}} for name stripping')
    ap.add_argument('--threshold', type=float, default=0.45,
                    help='Jaccard flag threshold (default 0.45)')
    ap.add_argument('--min-words', type=int, default=50)
    ap.add_argument('--max-words', type=int, default=100)
    args = ap.parse_args()

    copy = {}
    for path in args.inputs:
        copy.update(json.load(open(path)))
    packets = json.load(open(args.packets)) if args.packets else {}

    issues = []

    # Per-body hard rules
    for em, fws in sorted(copy.items()):
        for fw, v in sorted(fws.items()):
            body, subj = v['body'], v.get('subject', '')
            wc = len(norm_words(body))
            if not (args.min_words <= wc <= args.max_words):
                issues.append(f"[word_count] {em} {fw}: {wc}")
            if re.search(r'[\u2013\u2014]', body + subj):
                issues.append(f"[dash] {em} {fw}")
            if '!' in body + subj:
                issues.append(f"[exclamation] {em} {fw}")
            if re.search(r'https?://|www\.', body):
                issues.append(f"[link] {em} {fw}")
            if re.search(r'\{\{|\}\}|\{[a-z_]+\}', body + subj):
                issues.append(f"[unresolved_token] {em} {fw}")

    # Cross-lead similarity, per framework key
    keys = sorted({fw for fws in copy.values() for fw in fws})
    for key in keys:
        blobs = []
        for em, fws in sorted(copy.items()):
            if key not in fws:
                continue
            body = fws[key]['body']
            pk = packets.get(em, {})
            b = body
            for name in (pk.get('company'), pk.get('city')):
                if name:
                    b = re.sub(re.escape(name), ' ', b, flags=re.I)
            b = strip_canonical(b.lower())
            words = {w for w in norm_words(b) if len(w) > 3}
            blobs.append((em, words))
        for (em_a, wa), (em_b, wb) in itertools.combinations(blobs, 2):
            if not wa or not wb:
                continue
            j = len(wa & wb) / len(wa | wb)
            if j > args.threshold:
                issues.append(f"[cross_lead_sameness] {em_a} {key}: {round(j, 2)} vs {em_b}")

    for line in issues:
        print(line)
    print(f"checked {len(copy)} leads, {len(issues)} issues")
    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
