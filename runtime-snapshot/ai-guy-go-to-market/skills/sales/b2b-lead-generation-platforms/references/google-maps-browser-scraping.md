# Google Maps Browser Scraping — Patterns & Pitfalls

Last verified: July 2026. Gameday Owings Mills lead generation session.

## The One Pattern That Works

```
browser_navigate → https://www.google.com/maps/search/<keyword>+<city>+<state>
                → browser_snapshot
                → parse article→link→StaticText pattern
```

Each search yields 5-8 results in "limited view" mode.

## Snapshot Structure (sidebar list view)

```
- article
  - link "BUSINESS_NAME" [ref=eXX]
  - StaticText "BUSINESS_NAME"
  - image "4.9 stars"
  - generic
    - StaticText "CATEGORY  ADDRESS"
  - generic
    - StaticText "HOURS"
```

### Example extracted data

| Field | Example |
|-------|---------|
| Name | "OCEAN CUTZ" |
| Rating | "4.9" (from image alt) |
| Category | "Barber shop" |
| Address (partial) | "8890 McDonogh Rd suit 104" |
| Hours | "Closed · Opens 11 AM" |

## Detail View (click into listing)

Clicking a result opens a detail panel with full contact data:

```
- main "4Lifecutzz Barbershop"
  - button "Address: 9616 Reisterstown Rd Ste 114, Owings Mills, MD 21117"
  - button "Phone: (410) 363-2282"
  - link "Website: 4lifecutzz03.booksy.com"
  - button "Located in: Phenix Salon Suites"
```

## What Was Tested and Failed

| Approach | Result |
|----------|--------|
| curl + Google Maps | Empty skeleton HTML (~50KB, all JS) |
| curl + Google Search (tbm=lcl) | All zero results, bot detection |
| curl + YellowPages | Cloudflare "Sorry, you have been blocked" |
| curl + DuckDuckGo | Rate-limited after 1 query (14,2xx bytes = block page) |
| Playwright headless + Google Maps | Empty DOM, bot detection |
| Playwright non-headless | Crashes — no X server on headless VPS |
| Apify Google Maps Scraper | API key invalid ("user-or-token-not-found") |
| ScraperCity Maps | Account cancelled (-$3.00) |
| Delegate subagent | Timeout (18 API calls in 600s) |
| browser_console DOM queries | Google's obfuscated class names break selectors |
| execute_code regex on curl HTML | No server-rendered content to parse |

## Scaling Strategies

### Strategy A: Sequential browser scraping (~300 leads)
- 100 searches × 20s each = ~33 minutes
- 5 results each = 500 leads
- Cost: $0 (built-in browser)
- Use for: Deliverable-quality lead lists up to 500

### Strategy B: Browser Use Cloud parallel sessions (1,000+ leads)
- 5 concurrent sessions × 20 searches each = ~8 minutes
- Cost: ~$0.02/hr browser + $5/GB proxy
- Credit remaining: $17.16 (July 2026)

### Strategy C: Apify (requires valid token)
- Actor: `WnMxbsRLNbPeYL6ge` (google-maps-with-contact-details)
- One search = 20+ results with phones/websites/addresses

## Search Queries Template

For Gameday Owings Mills (Baltimore County) campaign, 90+ category×location combos:

```
barbershop + Owings Mills MD
barber shop + Reisterstown MD  
CrossFit gym + Owings Mills MD
gym fitness center + Owings Mills MD
personal trainer + Owings Mills MD
dentist + Owings Mills MD
chiropractor + Owings Mills MD
physical therapy + Owings Mills MD
steakhouse + Owings Mills MD
cigar lounge + Owings Mills MD
auto detailing + Owings Mills MD
financial advisor + Owings Mills MD
real estate agent + Owings Mills MD
...
```

Full category list with location variants in the Gameday Owings Mills plan at `/opt/data/hermes/plans/gameday-owings-mills-lead-gen.md`.
