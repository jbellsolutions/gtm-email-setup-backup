# Skool Actors — Input Schemas & Capabilities

Discovered 2026-07-16 via Apify store search + builds/default endpoint.

---

## `memo23/skool-members-scraper` — Members scraper (PPE)

**Cost:** $0.02/member (PRICE_PER_DATASET_ITEM)
**Runs:** 10,228 | **Users:** 713

Scrapes Skool group member pages and discovery search results. Collects group metadata + member profiles + optional contact enrichment from linked websites.

### Input Fields (13 total)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cookies` | array | ✅ | Cookie JSON from EditThisCookie for skool.com auth |
| `startUrls` | array | ✅ | Skool URLs or search keywords (auto-converts to discovery URLs) |
| `includeContactsFromWebsite` | boolean | | Extract emails, phones, socials from member-linked websites |
| `includeProfileDetails` | boolean | | Include full profile details per member |
| `includeAdminUsers` | boolean | | Include admin users in results |
| `maxItems` | integer | | Max members to collect |
| `maxConcurrency` | integer | | Parallel page processing limit |
| `minConcurrency` | integer | | Minimum parallel pages |
| `maxRequestRetries` | integer | | Retries on failed requests |
| `memberStartDate` | string | | YYYY-MM-DD filter for join date |
| `alphabetSearchRefinement` | boolean | | 36 extra queries per saturated letter for better coverage |
| `monitoringMode` | boolean | | Delta mode — only new items since last run (discovery only) |
| `proxy` | object | | Proxy configuration |

### Key Notes
- `startUrls` can be either direct group URLs (`https://www.skool.com/group-name`) or keywords (`Shopify course` → auto-converted to discovery URL)
- Emails come from scraping member-linked websites, NOT from Skool profiles directly
- Cookies are mandatory — user must be logged into Skool and export via EditThisCookie

---

## `crustapi/skool-community-scraper` — Community discovery

**Cost:** PAY_PER_EVENT (per result item)
**Runs:** 993 | **Users:** 167

Discovers and extracts community data from Skool.com by scanning categories and running keyword-driven discovery. Deep scans up to 20,000+ communities per run.

### Input Fields (5 total)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `searchTerms` | array | | Keywords to search for communities (each returns up to 1,000 matches) |
| `startUrls` | array | | Specific community names or URLs to scrape directly |
| `maxCommunities` | integer | | Cap (0 = unlimited). Start with 50-100 to preview. |
| `includeOwnerDetails` | boolean | | Visit each about page for owner name, email, socials, course count |
| `concurrency` | integer | | Browser tabs in parallel (default 12) |

### Key Notes
- Leave `searchTerms` + `startUrls` empty to scrape top-ranked communities across all categories
- `includeOwnerDetails` adds ~2s per community but gives 3x more data
- No cookies/auth required — public communities only

---

## `gordian/skool-group-scraper` — Simple group scraper

**Cost:** PAY_PER_EVENT
**Runs:** 1,118 | **Users:** 193

Extracts group metadata, pricing, owner profiles, and social links. Discovers groups via URLs, slugs, or category/search/discovery pages.

### Input Fields (2 total)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | | Your email address |
| `urls` | array | | Skool search URLs or group URLs to scrape |

### Key Notes
- Simplest actor — minimal config, but least capable for bulk ops
- No explicit auth needed beyond email
- Better for targeted group lookups than large-scale discovery

---

## Other Skool Actors (not detailed, found in store)

| Actor | Focus | Runs |
|-------|-------|------|
| `memo23/skool-posts-with-comments-scraper` | Posts + nested comments + classroom media | 8,102 |
| `crustapi/skool-content-scraper` | Classroom videos, posts, members | 77 |
| `dz_omar/skool-scraper-pro` | FREE — communities, courses, posts, video downloads | 2,019 |
| `futurizerush/skool-group-scraper` | Group details: name, description, members, pricing | 456 |
| `futurizerush/skool-post-scraper` | Posts with content, author, engagement metrics | 444 |
| `sourabhbgp/skool-scraper` | 10 modes: discover, community, posts, members, events, classroom, profiles | 510 |
| `goat255/skool-scraper-goat` | Communities at scale — pricing, estimated MRR/ARR, engagement | 1,336 |
| `dz_omar/skool-map-scraper` | Member locations + GPS coordinates from community map | 110 |
| `scrapyspider/skool-community-scraper` | Posts + member profiles with emails (requires credentials) | 434 |
| `silentflow/skool-scraper-ppe` | PPE scraper: posts, comments, courses, events, leaderboards | 319 |
| `scrapersdelight/skool-classroom-scraper` | Classroom videos, lessons, transcripts, attachments | 73 |