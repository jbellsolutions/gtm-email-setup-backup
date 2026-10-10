# Browserbase Blocking Pattern

## Symptom: API Splash Page Instead of Ad Results

When Facebook rate-limits a Browserbase IP, the Meta Ad Library page loads but shows the **API informational splash page** instead of ad results. The page structure:

```
- Meta Ad Library (header)
- United States (dropdown)
- All ads (dropdown)
- searchbox with your keyword
- System status (link)
- Ad Library API (heading)
- About ads and data use
- Privacy
- Terms
- Cookies
- Meta © 2026 | English (US)
```

**Key indicators this is a block:**
- No result count heading (e.g., "~9,500 results")
- No ad cards or article elements
- No "Sponsored" labels
- Only footer/info links visible
- `browser_console` extraction returns 0 relevant advertisers (only system page links)

## When It Happens

- As of June 2026: after just **1-2 keywords** of scrolling (even light scrolling of 30-50 advertisers). The block is faster and more aggressive than previously documented.
- Browserbase free tier uses datacenter IPs that Facebook flags aggressively
- The stealth warning says "Running WITHOUT residential proxies"
- Once blocked, the IP stays blocked — subsequent sessions from the same IP also show the splash page

## What To Do

1. **Stop the current session** — further scrolling won't help
2. **Switch to ScrapeCreators API** — free, existing credits, 15 results per keyword. Run all remaining keywords through ScrapeCreators. 29 keywords × 15 results = 394+ unique advertisers.
3. **NEVER fall back to Apify** — the `facebook-ads-scraper` actor is a documented cost trap. It ignores rate limits and burns money with zero saved results.
4. **Upgrade Browserbase** — residential proxy add-on would rotate IPs (unproven, may still be detected)

## Detection JS

```javascript
// Run this to check if you're blocked
(() => {
    const hasResults = document.querySelector('[role="article"]') !== null;
    const hasCount = document.body.innerText.match(/~\d+[,.]?\d*\s*results/);
    const hasSplash = document.body.innerText.includes('Ad Library API') && 
                      document.body.innerText.includes('System status');
    return { hasResults, hasCount: !!hasCount, hasSplash, blocked: hasSplash && !hasResults };
})()
```

If `blocked: true`, you're on the splash page — stop and switch strategies.