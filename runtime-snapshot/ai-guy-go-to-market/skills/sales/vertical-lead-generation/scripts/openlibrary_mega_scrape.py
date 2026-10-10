#!/usr/bin/env python3
"""
OpenLibrary Mega Scraper — bulk book author lead generation.
Free, no auth, no rate limits. 5K+ authors in 60 seconds.

Usage:
    python3 openlibrary_mega_scrape.py [--limit 5000] [--output /tmp/authors.csv]
"""

import requests, csv, time, json, re, sys
from datetime import datetime

SUBJECTS = [
    "business","management","leadership","entrepreneurship","marketing","sales",
    "finance","investing","economics",
    "health","medicine","nutrition","fitness","wellness","psychology",
    "law","legal",
    "self-help","personal development","productivity","mindfulness","motivation",
    "technology","innovation","startups","biography",
]

def scrape(limit=5000, output=None):
    all_results = []
    seen = set()
    bytes_dl = 0

    def add(src, author, title, cat='', date='', url=''):
        if not author or not title: return False
        author = re.sub(r'\s+', ' ', str(author).strip())
        title = re.sub(r'\s+', ' ', str(title).strip())
        if len(author) < 3 or len(title) < 5: return False
        k = (author.lower()[:40], title.lower()[:60])
        if k in seen: return False
        seen.add(k)
        all_results.append({
            'source': src, 'author': author, 'book_title': title[:200],
            'category': cat, 'date': str(date)[:50], 'url': str(url)[:200]
        })
        return True

    for subj in SUBJECTS:
        cat_count = 0
        for page in range(1, 11):
            try:
                r = requests.get("https://openlibrary.org/search.json",
                    params={'subject': subj, 'sort': 'new', 'limit': 100,
                            'page': page, 'language': 'eng'},
                    timeout=25)
                bytes_dl += len(r.content)
                docs = r.json().get('docs', [])
                if not docs:
                    break
                for doc in docs:
                    title = doc.get('title', '')
                    for a in doc.get('author_name', []):
                        if add('OpenLibrary', a, title,
                               ', '.join(doc.get('subject', [])[:2]),
                               doc.get('first_publish_year', ''), ''):
                            cat_count += 1
            except Exception:
                break
            time.sleep(0.25)
        
        total = len(all_results)
        print(f"  {subj}: +{cat_count} (total: {total})", flush=True)
        if total >= limit:
            print(f"  Hit {limit}! Stopping.", flush=True)
            break

    if not output:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"/tmp/book_authors_{ts}.csv"

    with open(output, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['source', 'author', 'book_title', 'category', 'date', 'url'])
        w.writeheader()
        w.writerows(all_results)

    print(f"\nSaved {len(all_results)} authors to {output}")
    print(f"Data: {bytes_dl/1e6:.1f}MB")
    return output, len(all_results)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=5000)
    p.add_argument('--output', type=str, default=None)
    args = p.parse_args()
    scrape(args.limit, args.output)
