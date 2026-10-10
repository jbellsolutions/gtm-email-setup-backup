# Meta Ad Library Browser Scraping

When the ScrapeCreators API 15-result cap is too limiting (clinical/medical keywords don't benefit from geo-spraying), use direct browser scraping via the built-in browser tool.

## When to Use This

- Keywords like "TRT", "botox", "semaglutide" where geo-spraying yields zero new results
- You need 50–200+ advertisers per keyword instead of 15
- The Meta Ad Library shows thousands of results (e.g., "~28,000 results for TRT")

## Proven Extraction JS

Paste this in browser_console after scrolling:

```javascript
(()=>{const m=new Map();document.querySelectorAll('a').forEach(a=>{const h=a.href||'',t=a.innerText.trim();if(!t||t.length<3)return;if(h.includes('l.facebook.com')||h.includes('facebook.com/help')||h.includes('facebook.com/ads/about')||h.includes('facebook.com/policies')||h.includes('metastatus.com')||t.includes('confirm your age')||t.includes('Advertising Standards')||t.includes('Log in')||t.includes('Privacy')||t.includes('English')||t.includes('Cookies')||t.includes('Terms')||t.includes('FAQ')||t.includes('System status')||t.includes('Subscribe')||t.includes('Branded Content')||t.includes('Ad Library')||t.includes('See ad')||t.includes('See summary')||t.includes('Open Dropdown')||t.includes('Play')||t.includes('Filters')||t.includes('Search by')||t.includes('About ads')||t.includes('Settings')||t.includes('INSTAGRAM')||t.includes('Visit Instagram')||t.includes('Next items')||t.includes('URLGENI')||t.includes('Shop now')||t.includes('Learn More')||t.includes('Apply now')||h.includes('facebook.com/ads/library')||h.includes('facebook.com/language'))return;const m2=h.match(/facebook\\.com\\/([^\\/\\?]+)/);if(m2&&!m2[1].match(/^(help|privacy|policies|ads|language|login|legal|marketplace|profile\\.php)/)&&!m.has(m2[1]))m.set(m2[1],{name:t,page_id:m2[1],page_url:h})});return JSON.stringify({total:m.size,advertisers:Array.from(m.values())})})()
```

## Scroll Script

For moderate scrolling (8-12 scrolls, proven safe):

```javascript
async function s(n){for(let i=0;i<n;i++){window.scrollTo(0,document.body.scrollHeight);await new Promise(r=>setTimeout(r,1200))}return'n='+n}s(10).then(r=>r)
```

## In-Session Keyword Cycling

Instead of re-navigating for each keyword, reuse the same browser session:

1. `browser_type` on the search box (ref visible in snapshot)
2. `browser_press` with key="Enter"
3. Wait 3-5 seconds for results heading to appear
4. `browser_scroll` once if results don't immediately render
5. Scroll 8-12 times, extract, save

This cuts per-keyword time from ~30s to ~15s.

## Pitfalls

1. **Facebook blocks headless Chrome through residential proxies.** Decodo/Smartproxy residential proxies work for urllib but fail for Playwright's headless Chrome — Facebook returns empty bodies. Only Browserbase's stealth browser works.
2. **`domcontentloaded` wait strategy times out.** Facebook's Ad Library never fires DOMContentLoaded because it keeps loading scripts. Use `wait_until="commit"` instead.
3. **Playwright install on immutable filesystems** requires `PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/playwright-browsers` to avoid EACCES on `/opt/hermes/.playwright/`.
4. **Subagents can't do browser scraping at scale.** Pages become too heavy after ~12 scrolls, JS timeouts at 30s, and subagents hit max_iterations. Use the parent browser session.
5. **Pages occasionally load empty.** One `browser_scroll` down usually triggers the results to render.
6. **Single-letter keywords like "TRT" are too noisy.** "TRT" matches Turkish Radio Television, not just testosterone clinics. Use multi-word queries like "TRT clinic" or "testosterone replacement" for cleaner results.