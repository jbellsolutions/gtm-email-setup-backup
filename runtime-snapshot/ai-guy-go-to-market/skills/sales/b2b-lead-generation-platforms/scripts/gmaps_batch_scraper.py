#!/usr/bin/env python3
"""Batch Google Maps scraper — Playwright headless with anti-detection.
Saves after each search — safe to interrupt and resume.

REQUIRES: pip install playwright && playwright install chromium
Chromium path may differ — check `which chromium` or ~/.cache/ms-playwright/

Usage: python3 gmaps_batch_scraper.py
Output: leads/all-power-partners-live.csv (saved after each search)
State:  leads/scraper_state.json (for resume)
"""

import asyncio, csv, os, json, re
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path('/opt/data/hermes/leads')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Edit this list for your campaign. Format: (category, "City ST")
SEARCHES = [
    ("barbershop", "Owings Mills MD"),
    ("gym fitness center", "Owings Mills MD"),
    ("chiropractor", "Owings Mills MD"),
    ("dentist", "Owings Mills MD"),
    ("steakhouse restaurant", "Owings Mills MD"),
    # Add more...
]

async def search_and_extract(page, query, location):
    fq = f"{query} {location}"
    url = f"https://www.google.com/maps/search/{fq.replace(' ', '+')}"
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(4000)
    except Exception as e:
        print(f"  Nav fail: {e}")
        return []
    results = []
    try:
        articles = await page.query_selector_all('[role="feed"] > div > div > a[href*="/maps/place/"]')
        if not articles:
            articles = await page.query_selector_all('a[href*="/maps/place/"][aria-label]')
        for a in articles[:20]:
            try:
                al = await a.get_attribute('aria-label')
                t = (await a.text_content() or '').strip()
                pt = await a.evaluate('el => el.closest("[role=\\"article\\"], article")?.textContent || ""')
                ft = pt if pt else t
                nm = al or t.split('\n')[0].strip()
                rm = re.search(r'(\d+\.?\d*)\s*stars?', ft)
                rt = rm.group(1) if rm else ''
                am = re.search(r'(\d{2,6}\s+[\w\s]+(?:Rd|Road|St|Street|Blvd|Ave|Avenue|Dr|Drive|Ln|Lane|Ct|Court|Way|Pkwy|Cir|Circle|Pike|Hwy|Highway)[\s,\w#]*(?:MD\s*\d{5})?)', ft, re.I)
                ad = am.group(1) if am else ''
                pm = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', ft)
                ph = pm.group(1) if pm else ''
                if nm and len(nm) > 2:
                    results.append({'name': nm[:100], 'rating': rt, 'category': '', 'address': ad, 'phone': ph, 'link': '', 'source_search': fq})
            except:
                continue
    except Exception as e:
        print(f"  Extract err: {e}")
    print(f"  {fq}: {len(results)} results")
    return results


def save_csv(results, filename):
    p = OUTPUT_DIR / filename
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['name', 'rating', 'category', 'address', 'phone', 'link', 'source_search'])
        w.writeheader()
        w.writerows(results)


async def main():
    sf = OUTPUT_DIR / 'scraper_state.json'
    all_results = []
    completed = set()
    if sf.exists():
        try:
            with open(sf) as f:
                st = json.load(f)
                completed = set(st.get('completed', []))
                all_results = st.get('results', [])
                print(f"Resume: {len(completed)} done, {len(all_results)} saved")
        except:
            pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path='/opt/data/home/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome',
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        ctx = await browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await ctx.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        total = len(SEARCHES)
        for i, (cat, loc) in enumerate(SEARCHES, 1):
            sk = f"{cat}|{loc}"
            if sk in completed:
                print(f"[{i}/{total}] SKIP: {cat} in {loc}")
                continue
            print(f"\n[{i}/{total}] Searching: {cat} in {loc}")
            r = await search_and_extract(page, cat, loc)
            all_results.extend(r)
            completed.add(sk)
            save_csv(all_results, "all-power-partners-live.csv")
            with open(sf, 'w') as f:
                json.dump({'completed': list(completed), 'results': all_results}, f)

        await browser.close()

    save_csv(all_results, "all-power-partners-live.csv")
    cats = {}
    for r in all_results:
        cats[r['source_search']] = cats.get(r['source_search'], 0) + 1
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_results)} leads from {len(cats)} searches")
    print(f"Saved to: {OUTPUT_DIR / 'all-power-partners-live.csv'}")

asyncio.run(main())
