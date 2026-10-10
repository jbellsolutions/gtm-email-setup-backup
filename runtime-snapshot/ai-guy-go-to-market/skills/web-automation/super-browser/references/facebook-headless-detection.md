# Facebook Headless Detection — Why Playwright + Decodo Failed

**Date:** June 2026
**Source:** Empirical testing during Meta Ad Library scraping attempts

## The Failure

`playwright-stealth` 2.0.3 + Decodo residential proxies were deployed against Facebook Ad Library. Result: blank page or API splash page — zero ad results rendered.

## Detection Vectors (Why It Failed)

Facebook's anti-bot stack detected the browser as headless through multiple signals:

### 1. Navigator WebDriver Property
```javascript
navigator.webdriver === true  // Dead giveaway — set by Chrome in headless mode
```
`playwright-stealth` patches this to `false`, but Facebook checks it through multiple indirect paths.

### 2. Canvas Fingerprinting
Facebook renders invisible canvas elements and hashes the output. Headless Chromium uses software rendering (SwiftShader) which produces different canvas output than hardware-accelerated Chrome. Even with `playwright-stealth`'s canvas noise injection, Facebook's statistical models detect the pattern.

### 3. WebGL Vendor/Renderer
```
WebGL: vendor = "Google Inc. (SwiftShader)"
        renderer = "Google SwiftShader"
```
Headless Chromium's SwiftShader strings are a hard signal. `playwright-stealth` tries to override them, but Facebook checks `WEBGL_debug_renderer_info` extension directly — bypassing JavaScript property overrides.

### 4. Font Enumeration
Headless Chromium has a limited, predictable font set. Facebook queries available fonts via Flash fallback and `document.fonts`. The absence of common user-installed fonts (Arial, Times New Roman variants) is a signal.

### 5. Mouse Movement Absence
Facebook's JavaScript monitors `mousemove` events. Headless browsers generate zero mouse events. Even with `page.mouse.move()` calls, the timing patterns are distinguishable from human movement.

### 6. `chrome.runtime` API
Facebook checks for the presence of `chrome.runtime` (available in real Chrome but absent in headless Chromium when launched without extensions).

### 7. `window.outerWidth` / `window.outerHeight`
In headless mode, these equal `window.innerWidth`/`innerHeight` (no window chrome). Facebook detects the equality.

## Why Browser Use Cloud Succeeds

Browser Use Cloud's hardened Chromium fork addresses these at the **binary level**, not through JavaScript patching:

| Vector | Playwright + Stealth | Browser Use Cloud |
|--------|---------------------|-------------------|
| `navigator.webdriver` | JS override (bypassable) | Removed from binary |
| Canvas fingerprint | Noise injection (detectable) | Hardware rendering + randomization |
| WebGL renderer | String override (bypassable) | Recompiled with real GPU strings |
| Font enumeration | Cannot fix | Full real font set installed |
| Mouse movement | Simulated (pattern-detectable) | Real human-like movement engine |
| `chrome.runtime` | Cannot add | Full extension API present |
| Window dimensions | Cannot fix | Proper window chrome rendered |

## The Proxy Lesson

Residential proxies (Decodo) are necessary but **not sufficient**. A detectable browser behind a residential proxy is still detectable. The proxy only hides the IP — the browser fingerprint gives you away. Browser Use Cloud combines hardened Chromium + residential proxy, which is why it works.

## What This Means for the Stack

- **Tier 1 (Browser Use Cloud)**: Only option for sites with aggressive headless detection
- **Decodo + Playwright**: Works for sites WITHOUT headless detection (standard web scraping, API endpoints)
- **Browserbase**: Works for ~2-3 queries against Facebook before being rate-limited — its stealth is good but its infrastructure gets IP-blocked
- **Never**: Use raw Playwright/Puppeteer/Selenium in headless mode against Facebook
