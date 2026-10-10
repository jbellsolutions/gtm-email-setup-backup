# Browser-Based Meta Ad Library Scraping — Advanced Patterns

Full technical reference for production-grade Meta Ad Library browser scraping. This supplements `references/meta-ad-library-browser.md` (basic workflow) and `references/browser-scraping.md` (extraction JS and scroll recipes).

## Approach A: Browser Use Cloud (PRIMARY)

Browser Use Cloud runs hardened Chromium with anti-detect fingerprinting that passes CreepJS and BrowserLeaks. Built-in US residential proxies. This consistently works against Facebook at scale.

```python
from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode

client = BrowserUse()  # uses BROWSER_USE_API_KEY env var
session = client.sessions.create(
    model=BuModel.claude_sonnet_4_6,
    proxy_country_code=ProxyCountryCode.US,
)

result = client.sessions.run(
    session_id=session.id,
    task=f"Go to https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&q={keyword}&search_type=keyword_unordered&media_type=all — scroll to load all advertisers, extract every unique advertiser name and Facebook page URL. Return as JSON array.",
)

client.sessions.stop(session_id=session.id)
```

Cost: $0.02/hr browser + $5/GB proxy + LLM tokens. Requires $29/mo Dev plan.

## Approach B: Browserbase Tool Extraction (FALLBACK)

Use Hermes' built-in browser for moderate-volume extraction. Good for 50-200 advertisers per keyword. **Note: Facebook blocks Browserbase after 1-2 keywords.** Use Browser Use Cloud for scale.

### Step 1: Navigate

```
URL: https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&q={KEYWORD}&search_type=keyword_unordered&media_type=all
```

Use `browser_navigate` then `browser_snapshot` to verify results loaded. If only footer appears, use `browser_scroll(direction='down')` then snapshot again.

### Step 2: Scroll to Load

```javascript
async function s(n) {
  for (let i = 0; i < n; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 1200));
  }
  return 'n=' + n;
}
s(10).then(r => r);  // 10 scrolls = safe, 15+ risks page instability
```

**Stick to 8-12 scrolls.** Beyond ~15 scrolls, the page DOM becomes too heavy and `browser_console` calls start timing out.

### Step 3: Batch Extraction with Exhaustion Detection

Facebook's Ad Library pages become too heavy after 20-30 scrolls and freeze the browser. Use small batches (3 scrolls each) with state tracking:

```javascript
(async() => {
  for (let i = 0; i < 3; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 1500));
  }
  var m = new Map();
  document.querySelectorAll('a').forEach(a => {
    var u = a.href || '', t = a.innerText.trim();
    if (!t || t.length < 3 || u.includes('l.facebook.com') || u.includes('help')
        || t.includes('confirm') || t.includes('Log in') || t.includes('Privacy')
        || t.includes('Cookies') || u.includes('/ads/library') || u.includes('/language'))
      return;
    var m2 = u.match(/facebook\\.com\\/([^\\/\\?]+)/);
    if (m2 && !m2[1].match(/^(help|privacy|policies|ads|language|login|legal|marketplace|profile\\.php)/)
        && !m.has(m2[1]))
      m.set(m2[1], {name: t.substring(0, 80), page_id: m2[1]});
  });
  return JSON.stringify({batch: N, total: m.size});
})().then(r => r)
```

**Exhaustion detection:** Track the count per batch. When 2 consecutive batches return the same count (zero new advertisers), the page is truly exhausted — extract final results and move to next keyword.

## Approach C: Subagent Browsers (Use Sparingly)

Subagents with `browser` + `file` toolsets CAN extract 50-100 advertisers per keyword before hitting the 600s timeout. They work for parallel extraction (proven: 2 concurrent browser sessions in June 2026).

### When subagents work:
- Short scraping tasks: navigate → extract initial → scroll 4-6 times → extract final → save to file
- Fit within the 30s `browser_console` timeout per call
- Use `browser` + `file` toolsets so results are persisted to disk

### When subagents fail:
- Deep exhaustion (8+ scroll batches) — timeline exceeds 600s
- Complex multi-step instructions — subagents get distracted
- Without `file` toolset — results are lost in truncated summaries

### Parallel extraction pattern:
```python
delegate_task(tasks=[
    {"toolsets": ["browser", "file"], "goal": "Scrape keyword X, auto-scroll 6 times, save to /tmp/file.csv"},
    {"toolsets": ["browser", "file"], "goal": "Scrape keyword Y, auto-scroll 6 times, save to /tmp/file.csv"},
])
```

**For long-running exhaustive scrapes:** Do NOT use `delegate_task` subagents — they timeout at 600s. Use Browser Use Cloud instead.

## Deprecated Approaches

### Playwright + Residential Proxies — DOES NOT WORK

Facebook detects headless Chrome regardless of proxy type or stealth patches. Failures documented (June 2026): `domcontentloaded` timeout at 60s, `commit` strategy returns null body, `playwright-stealth` 2.0.3 fails, Decodo proxies authenticated but still blocked. Do not attempt.

### Apify Facebook Ads Scraper — FORBIDDEN

The `facebook-ads-scraper` actor ignores rate limits and burned $165 in 7 minutes with zero saved results (June 2026). User explicitly forbids. Never use.

## Output Format

Each keyword produces:
```json
{
  "keyword": "TRT clinic",
  "vertical": "Men's Health & Hormone",
  "batches": 8,
  "total_scrolls": 24,
  "unique_advertisers": 156,
  "advertisers": [
    {"name": "T Zone Mens TRT Clinic", "page_id": "tzonemenstestosterone"}
  ]
}
```

Final deliverable: merged CSV across all keywords with columns: vertical, keyword, advertiser_name, page_id, page_url.

## Advanced Pitfalls

1. **Playwright + residential proxies + stealth = STILL BLOCKED** — Facebook detects headless Chrome deterministically.
2. **Browserbase blocks after 1-2 keywords** — Facebook rate-limits Browserbase datacenter IPs.
3. **Browser becomes unstable after 15+ scrolls** — DOM grows massively with infinite scroll. Limit to 8-12 scrolls.
4. **Age-gated content hides ad copy** — Many health/pharma ads require login. Advertiser names are still visible.
5. **"drug rehab" catches political ads** — Use "addiction treatment center" for cleaner results.
6. **Subagents cannot handle heavy pages** — Subagent browser is less stable than parent browser.
7. **Meta changes DOM structure** — Test extraction on one keyword before mass spraying.
8. **Keyword overlap is high within a vertical** — Deduplicate by `page_id`, not name.
9. **browser_console has a hard 30s timeout** — Keep async loops to ≤6 scrolls with ≤2s delays. Split longer campaigns into multiple `browser_console` calls.
10. **Empty initial page is normal** — One `browser_scroll down` triggers loading.
11. **Browser sessions degrade** — after heavy use, re-navigate to reset the page DOM.