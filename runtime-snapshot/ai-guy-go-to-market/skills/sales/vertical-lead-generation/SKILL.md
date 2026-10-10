---
name: vertical-lead-generation
description: "Vertical-specific lead generation playbooks — sourcing prospects in niche B2B and B2C markets using ScrapeCreators, ScraperCity, Apify, browser scraping, and direct APIs."
version: "1.0"
category: sales
triggers:
  - lead generation
  - prospect sourcing
  - vertical lead gen
  - niche leads
  - book authors
  - podcast booking
  - MCA ISO
  - merchant cash advance
  - business lending
  - local business leads
  - referral partners
  - power partners
  - local influencers
  - Google Maps scraping
  - local business directory
---

# Vertical Lead Generation

Playbooks for sourcing prospects in specific verticals where generic lead-gen approaches fail. Each vertical has unique ICP definitions, source hierarchies, and pitfalls — documented here as labeled subsections with detailed references.

## Common Toolset

All verticals share the same underlying tools:

| Tool | Purpose | Skill |
|------|---------|-------|
| **ScrapeCreators** | Facebook/Google Ad Library search, profile enrichment | `scrapecreators-cli` |
| **ScraperCity** | Google Maps, email validation, Website Finder, Yelp, BuiltWith | `scrapercity` |
| **Apify** | PipelineLabs keyword search, LinkedIn scraping, email discovery | `job-scraper-pipeline` |
| **Browser Use Cloud** | Anti-detection browser for protected sites | `super-browser` |
| **Browserbase** | Built-in browser for Meta Ad Library scraping | `meta-ad-library-scraping` |

## Vertical: Local Business Partner & Influencer Lead Generation

Target: Building large referral-partner graphs (100+ categories, 3 degrees of separation) and local influencer lists for brick-and-mortar businesses. Example: Gameday Men's Health clinic opening in Owings Mills, MD needed 1,000-10,000 potential referral partners across barbershops, gyms, dentists, chiropractors, med spas, cigar lounges, steakhouses, wealth managers, country clubs, chambers of commerce, and more — plus local fitness/grooming influencers.

**Primary source: Playwright headless Google Maps scraping** — the fastest free approach that works (7-10 results/search, parallel instances). See `b2b-lead-generation-platforms` skill → "Playwright Headless Google Maps Scraping" for the working anti-detection config. This replaced the older browser_navigate approach which only gets 5-8 results and requires manual clicks for contact details.

**Batch strategy:** Three parallel batches covering Degree 1-3 categories, each with 25-91 searches. Typical yield: ~950 leads from ~130 searches across 45+ category types. Save CSV + JSON state file after every search for crash-resilience.

**Post-scraping compilation:** After all batches complete, run a compile script that:
1. Loads all batch CSVs + document-based leads
2. Classifies each lead by degree (1/2/3) and sub-category via keyword matching on the source_search field
3. Deduplicates by normalized business name (stripping "Closed"/"Open" suffixes)
4. Writes final master CSV with columns: name, degree, category, address, phone, rating, source, search_query
5. For document-based leads that survived dedup, preserves the original deliverable categorization

See `references/local-partner-compilation.md` for the full classification table and compile script.

**The 3-Degree Referral Graph Concept:** Not just obvious partners (gyms, barbers). Map every business that touches the target customer's life:
- **Degree 1 — Same customer, different service** (gyms, PT, chiropractors, dentists, med spas, country clubs, custom clothing)
- **Degree 2 — Same man, his lifestyle** (cigar lounges, steakhouses, auto detailers, gun ranges, wealth managers, breweries)
- **Degree 3 — His household, affiliations & employer** (chambers, Rotary, American Legion, BNI, youth sports, faith groups, unions)

**ICP:** Men 30-65, cash-pay, vitality-minded. Every lead must pass the fit test: (a) Is the audience local to the service area? (b) Does it skew male 30-65? (c) Does the partner already talk about health/fitness/performance (so a men's health mention isn't a swerve)?

**Data extraction:** Browser-based Google Maps yields 5-8 results per search with name, rating, category, partial address, and hours. Clicking into detail view reveals full address, phone number, and website. Snapshots are machine-readable (article → link → StaticText pattern) and parseable via regex in execute_code.

**Influencer sourcing:** Supplement Maps scraping with:
- DuckDuckGo/Google search for "[city] fitness influencers Instagram [year]" (Feedspot top-N lists)
- Instagram profile research for follower counts and content fit
- Tier structure: Tier 1 (best fit, content collab + affiliate), Tier 2 (awareness reach), Tier 3 (micro-creators for chair-side referral), Tier 4 (athlete/sports halo)
- Flag any unverified handles with *(verify)*

**Volume targets:** 1,000-10,000 leads for a territory-wide campaign. With 100 categories × 3-5 cities × 5 results each = 1,500-2,500 leads from Maps alone. Add influencers (20-50) and directory-sourced organizations (50-100).

**What NOT to try (all failed, July 2026):**
- curl + Google Maps/Search/YellowPages/DuckDuckGo — all blocked or empty
- Apify — API key invalid
- ScraperCity — account cancelled
- Delegate subagents for scraping — timeout at 600s per task

**✅ What works for scale:**
- **Playwright headless** (PRIMARY — fastest, highest yield): 7-10 results/search, 2+ instances can run in parallel. ~6 minutes for 90 searches → ~700 leads. See `b2b-lead-generation-platforms` skill → "Playwright Headless Google Maps Scraping" section for working config.
- **Browser-based scraping** (FALLBACK): `browser_navigate` + `browser_snapshot` via built-in Hermes browser. 5-8 results/search. Useful for one-off searches or when Playwright dependencies aren't available.

**Volume targets:** 1,000-10,000 leads for a territory-wide campaign. With 130+ searches across 3 batches covering ~45 category types × 7 results each = ~900 leads from Maps alone. Add document-based leads (50-100) and influencers (30-50).

## Vertical: Book Authors / Podcast Booking

Target: Recently published authors actively seeking exposure — ideal for podcast/guest booking outreach.

**Primary source:** OpenLibrary API (`openlibrary.org/search.json`) — free, no auth, clean JSON. 5K+ unique authors in <60 seconds across 25+ subjects.

**Full playbook:** `references/book-author-lead-scraping.md`

## Vertical: MCA / ISO / Business Lending

Target: ISOs, super-ISOs, and MCA brokers — the sales organizations that buy leads and run sales floors. Secondary: direct funders/lenders who recruit ISOs.

**Primary source:** deBanked Funder Directory (`debanked.com/funder-lender-directory/`) — 40-45 curated funders with phones and domains.

**Volume play:** Apify PipelineLabs keyword search ($1 per 1,000 leads). ⚠️ PipelineLabs emails are 90%+ invalid and phone numbers are MASKED — use only for company discovery, not contact data.

**Phone scraping:** Direct website scraping outperforms all enrichment tools for this vertical — 51% hit rate across 498 domains in 3 minutes using the bundled `scripts/scrape_phones.py`. This is the recommended path for phone numbers in ANY vertical where Maps returns no emails and PipelineLabs masks phones.

See `references/local-partner-compilation.md` for the full classification table and compile script.

**Full playbook:** `references/local-partner-lead-generation.md`

**Compile script:** `scripts/compile_leads.py` — automates merge, dedup, and classification. Run after all batch scrapers complete.

## When to Create a New Vertical Playbook

Each vertical needs its own playbook when:
- The ICP is industry-specific (not discoverable by generic keyword search)
- The best data sources are vertical-specific directories, not general-purpose scrapers
- Platform quirks (BuiltWith failures, Maps email limitations) differ from other verticals
- Failed sources and dead ends are worth memorializing to avoid repeated attempts

Add new verticals as subsections above (with a corresponding `references/<vertical>.md` detailed guide) rather than creating standalone skills.

## Pitfalls Across Verticals

1. **Maps returns zero emails** — every vertical that uses Google Maps scraping needs a separate email enrichment step (ScraperCity Website Finder or Apify).
2. **BuiltWith is useless for niche industries** — industry-specific CRMs (Centrex for MCA, ServiceTitan for HVAC) aren't tracked. Verify on builtwith.com before spending credits.
3. **Residential proxies fail on major platforms** — Facebook, Amazon, Google Books detect headless Chrome through residential proxies. Use Browser Use Cloud or Browserbase instead.
4. **Vertical directories are often incomplete** — deBanked has many dead pages, trade associations often don't publish member lists. Always verify before committing to a source.
1. **Maps returns zero emails** — every vertical that uses Google Maps scraping needs a separate email enrichment step (ScraperCity Website Finder or Apify).
2. **BuiltWith is useless for niche industries** — industry-specific CRMs (Centrex for MCA, ServiceTitan for HVAC) aren't tracked. Verify on builtwith.com before spending credits.
3. **Residential proxies fail on major platforms** — Facebook, Amazon, Google Books detect headless Chrome through residential proxies. Use Browser Use Cloud or Browserbase instead.
4. **Vertical directories are often incomplete** — deBanked has many dead pages, trade associations often don't publish member lists. Always verify before committing to a source.
5. **Don't create a standalone skill per vertical** — add it here instead. The shared toolset and cross-vertical patterns are the class-level knowledge.
6. **Shell heredocs choke on `&`** — when writing Python scripts via terminal heredocs (`<< 'EOF'`), category strings with `&` (like `"Gyms & Fitness"`) break because the shell interprets `&` as a background operator. Use `and` instead or write files via `write_file`.