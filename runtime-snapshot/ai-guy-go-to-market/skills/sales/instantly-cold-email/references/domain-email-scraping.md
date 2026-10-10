# Domain → Email Scraping (Direct, No Proxy)

When you have a list of domains but no emails, and Apify costs are too high or API keys are broken, scrape homepages directly with Python.

## When to Use

- You have a list of domains (e.g., from Google Maps CSV)
- Apify email finder actors are too expensive ($0.12/domain for `contact-info-scraper`)
- Decodo proxy auth is broken (407) and sites don't need residential IPs
- Target sites are small/unsophisticated (law firm WordPress sites, local businesses)
- Budget is tight (<$10 for thousands of domains)

## Workflow

1. **Extract domains** from CSV website column
2. **Scrape homepages** with Python `urllib` + 5s timeout + 25-30 concurrent workers
3. **Extract emails + phones** via regex
4. **Filter aggressively**: remove generics (info@), WordPress placeholders (`name@email.com`), theme author emails, cross-domain mismatches
5. **Save incremental checkpoints** so partial progress survives crashes

## Cost

Free. No proxy, no API fees. The only cost is your VPS bandwidth.

## The Script

See `scripts/domain_email_scraper.py` — reusable, checkpoint-aware, configurable worker count and timeout.

## Performance (June 2026 — 4,390 law firm domains)

| Metric | Value |
|--------|-------|
| Domains scraped | 4,390 |
| Time | ~6 minutes |
| OK connections | ~82% |
| Domains with email | 22% (raw) → 12% (after strict filtering) |
| Total unique emails | 645 from 529 contacts |
| Top categories | Personal injury, estate planning, family law |

## Filtering Rules

Apply in this order, reject if any match:

1. **Known fakes**: `name@email.com`, `user@domain.com`, `filler@godaddy.com`, `email@example.com`
2. **Fake domains**: `email.com`, `domain.com`, `example.com`, `test.com`, `godaddy.com`
3. **Theme authors**: `aldusleaf`, `impallari`, `theme`, `wordpress` keywords in address
4. **Generics**: `info`, `contact`, `support`, `admin`, `hello`, `sales`, `office`, `mail`, `general`, `inquiries`, `reception`, `frontdesk`, `administrator`
5. **Cross-domain mismatch**: Skip if email domain doesn't match site domain, unless it's a known personal provider (`gmail.com`, `yahoo.com`, `outlook.com`, `fastmail.fm`, etc.)

## Pitfalls

- **Heredoc buffering**: When running via `python3 << 'PYEOF'`, stdout may be fully buffered even with `flush=True`. Write to a file instead and use `scripts/domain_email_scraper.py`.
- **Timeouts stack**: With 30 concurrent workers at 5s timeout, the first batch takes up to 5s but subsequent batches are faster as failing sites return quickly.
- **Checkpoint saves**: Write incremental JSON after each batch. Resuming from checkpoint avoids re-scraping.
- **Missing names**: Google Maps CSVs have company names but not contact names. Use `first-name-extraction.md` in the cold-email-personalized-agent skill to derive first names from business names.
