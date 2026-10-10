# Meta Ad Library — Direct Browser Scraping

When the ScrapeCreators API's 15-result cap is fatal (clinical, medical, national-brand keywords), scrape the Meta Ad Library directly via browser. The public web interface shows real volumes (3,500–36,000+ results per keyword) with proper infinite scroll.

## When to Use This

- **USE browser scraping when:** keywords are clinical/medical (TRT, botox, semaglutide, drug rehab), national-brand products, or ecommerce — where geographic spraying returns zero new results after the first state
- **SKIP browser scraping for:** local service businesses (HVAC, roofing, plumbing) — the API's geographic spraying works fine there

## URL Pattern

```
https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&q={KEYWORD}&search_type=keyword_unordered&media_type=all
```

Always URL-encode the keyword. Example:
```
https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&q=TRT%20clinic&search_type=keyword_unordered&media_type=all
```

## Workflow

### Step 1: Navigate

Use `browser_navigate` with the URL. The page may initially render only the footer — this is normal.

### Step 2: Trigger Results

If results don't appear immediately (only footer visible), `browser_scroll` down once, then `browser_snapshot` to verify the results heading appeared (e.g., "~3,500 results").

### Step 3: Load More Ads via Scroll

Meta lazy-loads ads via infinite scroll. Use `browser_console` to run multiple scrolls:

```javascript
async function s(n) {
  for (let i = 0; i < n; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 1200));
  }
  return 'n=' + n;
}
s(8).then(r => r);
```

- 6 scrolls ≈ 40–80 advertisers visible
- 15–20 scrolls for deeper extraction (100–300+ advertisers)
- 1200ms delay between scrolls is safe; 800ms sometimes triggers rate limiting

### Step 4: Extract Advertisers

Use `browser_console` with this extraction script:

```javascript
(() => {
  const m = new Map();
  document.querySelectorAll('a').forEach(a => {
    const h = a.href || '', t = a.innerText.trim();
    if (!t || t.length < 3) return;
    // Filter out noise
    if (h.includes('l.facebook.com') || h.includes('facebook.com/help') ||
        h.includes('facebook.com/ads/about') || h.includes('facebook.com/policies') ||
        h.includes('metastatus.com') || t.includes('confirm your age') ||
        t.includes('Advertising Standards') || t.includes('Log in') ||
        t.includes('Privacy') || t.includes('English') || t.includes('Cookies') ||
        t.includes('Terms') || t.includes('FAQ') || t.includes('System status') ||
        t.includes('Subscribe') || t.includes('Branded Content') || t.includes('Ad Library') ||
        t.includes('See ad') || t.includes('See summary') || t.includes('Open Dropdown') ||
        t.includes('Play') || t.includes('Filters') || t.includes('Search by') ||
        t.includes('About ads') || t.includes('Settings') || t.includes('INSTAGRAM') ||
        t.includes('Visit Instagram') || t.includes('Next items') || t.includes('URLGENI') ||
        t.includes('Shop now') || t.includes('Learn More') ||
        h.includes('facebook.com/ads/library') || h.includes('facebook.com/language'))
      return;
    const m2 = h.match(/facebook\.com\/([^\/\?]+)/);
    if (m2 && !m2[1].match(/^(help|privacy|policies|ads|language|login|legal)/) &&
        !m.has(m2[1]))
      m.set(m2[1], {name: t, page_id: m2[1], page_url: h});
  });
  return {total: m.size, advertisers: Array.from(m.values())};
})();
```

Returns: `{total, advertisers: [{name, page_id, page_url}]}`

### Step 5: Filter Noise

The extraction catches some false positives. Common noise to remove post-extraction:
- Political advertisers (Trump, Daily Show, PragerU) — especially in "drug rehab" and other hot-button verticals
- Media/news pages (Yahoo, Connecticut Post, Us Weekly) — often appear because their content mentions the keyword
- "profile.php" IDs — Facebook profile pages, not business pages
- "marketplace" IDs — Facebook Marketplace listings
- Single-person names without clinic branding (Ashley Miller, Kevin Cooney) — may be legitimate small operators but need verification

### Step 6: Repeat for Multiple Keywords

For volume, search 3–5 keyword variations per vertical. Each keyword surfaces a different slice of the total results due to how Meta's ranking works. Deduplicate by `page_id` across keywords.

## Volume Expectations

| Keyword Type | Results Claimed | Extractable (8 scrolls) | Extractable (20 scrolls) |
|---|---|---|---|
| Niche clinical (semaglutide) | ~1,800 | 10–20 | 30–60 |
| Broad clinical (medspa) | ~15,000 | 80–120 | 200–400 |
| Hot-button (drug rehab) | ~36,000 | 40–80 | 150–300 |
| Trade service (kitchen remodel) | ~23,000 | 60–100 | 200–400 |
| Men's health (TRT clinic) | ~3,500 | 25–50 | 80–150 |

## Pitfalls

1. **Age-gating**: Weight loss, pharma, and some men's health ads show "To see this content, you need to confirm your age by logging in." Advertiser names are still extractable but ad copy is hidden. Keywords affected: semaglutide, tirzepatide, weight loss, TRT (partial).

2. **Footer-only initial load**: Some queries render only the footer on first load. Scroll down once to trigger result rendering. If scrolling doesn't work, try refreshing the page or using a slightly different keyword formulation.

3. **Browser-based, so single-threaded**: Only one browser tab at a time. Plan for ~20–30 seconds per keyword (navigate + scroll + extract). 5 verticals × 5 keywords = ~10–15 minutes.

4. **No login = no ad spend/impression data**: The public Ad Library shows advertiser names and ad copy but not spend ranges or impression counts. Those require login.

5. **Meta may eventually block**: Prolonged rapid scrolling could trigger bot detection. Keep delays reasonable (1.2s between scrolls). If blocked, wait 5 minutes and try again.

6. **JavaScript extraction is fragile**: If Meta changes their DOM structure, the extraction regex may break. Always verify the first few results look correct before trusting a batch extraction.

## Credit Comparison: API vs Browser

| Vertical | API (geographic spray) | Browser (1 keyword, 8 scrolls) |
|---|---|---|
| Med Spas | 300 credits → 89 unique | 0 credits → 107 unique |
| Men's Health | 250 credits → ~50 unique | 0 credits → 28 unique |
| Weight Loss | 250 credits → ~15 unique | 0 credits → 14 unique |

**Bottom line**: For clinical/medical verticals, the browser approach is not just cheaper — it's the only way to get meaningful volume.