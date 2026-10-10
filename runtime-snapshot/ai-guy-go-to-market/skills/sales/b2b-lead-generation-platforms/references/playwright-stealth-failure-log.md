# Playwright + Stealth Failure Log
## Proving headless Chrome is detected by Facebook regardless of proxy or stealth

### Test 1: Playwright + Decodo proxy, domcontentloaded (June 4, 2026)
- **Proxy**: `http://spo2nwl1tw:***@us.decodo.com:10001` (Decodo residential, authenticated)
- **Wait strategy**: `domcontentloaded`
- **Result**: Timeout after 60s. Facebook never fires `domcontentloaded`.
- **Body**: N/A (navigation never completed)

### Test 2: Playwright + Decodo proxy, commit (June 4, 2026)
- **Proxy**: Same Decodo residential
- **Wait strategy**: `commit`
- **Result**: Page loads with title "Ad Library", 13KB body, but `document.body` is null.
- **Body preview**: Empty — JavaScript never executed. Facebook detected headless and served a blank shell.

### Test 3: Playwright + Decodo proxy + playwright-stealth 2.0.3 + commit (June 4, 2026)
- **Proxy**: Same Decodo residential
- **Stealth**: `playwright-stealth` 2.0.3, `Stealth` class with full evasion flags (navigator_webdriver, navigator_languages, navigator_plugins, navigator_permissions, webgl_vendor, chrome_runtime, chrome_app, hairline)
- **Wait strategy**: `commit`
- **Result**: Same as Test 2 — `document.body` is null. Stealth patches do not help.
- **Error**: `Page.evaluate: TypeError: Cannot read properties of null (reading 'innerText')`

### Test 4: Browserbase (browser tool), multiple keywords (June 4, 2026)
- **First keyword ("bath remodel")**: SUCCESS — 105 unique advertisers extracted across ~14 scrolls
- **Subsequent keywords**: Facebook serves API informational splash page — no ad results, only footer links ("Ad Library API", "System status", "Privacy", "Terms", "Cookies"). Browserbase IP was rate-limited.
- **Subagent test ("solar installation")**: SUCCESS — 92 advertisers extracted by a parallel subagent

### Conclusion
- Facebook detects headless Chrome deterministically — even with residential proxies AND stealth patches
- Browserbase works briefly but gets IP-blocked after ~1 keyword of heavy scrolling
- Browserbase parallel sessions are possible (2 concurrent sessions confirmed)
- The only reliable path: Apify Facebook Ads Scraper (purpose-built, handles anti-bot) or Browserbase with residential proxy upgrade