#!/usr/bin/env python3
"""Re-crawl unreachable/thin pages in a per-lead research corpus (JSONL).

Usage:
  python3 refresh_research_corpus.py <leads.csv>... <research.jsonl> [--min-text 350] [--workers 12]

- Leads CSVs must contain an 'email' column; a 'Domain' column supplies the website.
- Research JSONL is one {"email": ..., "research": {...}} per line, in-place updated.
- Targets: leads with research status != 'ok', or 'ok' with text shorter than --min-text.
- Tries https://domain/, https://www.domain/, http://domain/ in order with a browser UA.
- Never prints credentials; exit 0 even when some sites stay down (they are reported).
"""
import argparse, csv, gzip, io, json, re, ssl, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

CTX = ssl.create_default_context()
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html',
                                               'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        raw = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        return r.status, raw.decode('utf-8', errors='replace')

def extract(html):
    title = desc = h1 = ''
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
    if m: title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()[:200]
    m = (re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I | re.S)
         or re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html, re.I | re.S))
    if m: desc = re.sub(r'\s+', ' ', m.group(1)).strip()[:300]
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.S)
    if m: h1 = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()[:200]
    body = re.sub(r'<(script|style|noscript).*?</\1>', ' ', html, flags=re.I | re.S)
    text = re.sub(r'<[^>]+>', ' ', body)
    for ent in ('&nbsp;', '&#160;'):
        text = text.replace(ent, ' ')
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()[:4000]
    return title, desc, h1, text

def try_site(domain):
    if not domain: return {'status': 'unreachable', 'error': 'no_domain'}
    d = domain.strip().rstrip('/')
    candidates = ([d if d.endswith('/') else d + '/'] if d.startswith('http')
                  else [f'https://{d}/', f'https://www.{d}/', f'http://{d}/'])
    last = None
    for u in candidates:
        try:
            status, html = fetch(u)
            if status == 200 and len(html) > 300:
                title, desc, h1, text = extract(html)
                return {'status': 'ok', 'url': u, 'title': title,
                        'description': desc, 'h1': h1, 'text': text}
        except Exception as e:
            last = type(e).__name__
    return {'status': 'unreachable', 'error': last or 'unknown'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csvs', nargs='+')
    ap.add_argument('jsonl')
    ap.add_argument('--min-text', type=int, default=350)
    ap.add_argument('--workers', type=int, default=12)
    a = ap.parse_args()

    leads = {}
    for p in a.csvs:
        with open(p, encoding='utf-8-sig', newline='') as f:
            for r in csv.DictReader(f):
                e = (r.get('email') or '').strip().lower()
                if e and e not in leads:
                    leads[e] = r

    research = {}
    with open(a.jsonl) as f:
        for line in f:
            d = json.loads(line)
            research[d['email']] = d.get('research', {})

    targets = [e for e, r in leads.items()
               if research.get(e, {}).get('status') != 'ok'
               or len(research.get(e, {}).get('text') or '') < a.min_text]
    print('retry targets:', len(targets), flush=True)

    done = improved = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(try_site, leads[e].get('Domain')): e for e in targets}
        for fut in as_completed(futs):
            e = futs[fut]
            try:
                res = fut.result()
            except Exception as ex2:
                res = {'status': 'unreachable', 'error': type(ex2).__name__}
            research[e] = res
            improved += res.get('status') == 'ok'
            done += 1
            if done % 200 == 0:
                print('done', done, flush=True)

    with open(a.jsonl, 'w') as f:
        for e, r in research.items():
            f.write(json.dumps({'email': e, 'research': r}, ensure_ascii=False) + '\n')
    print(f'retried: {len(targets)} improved: {improved} still_down: {len(targets) - improved}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
