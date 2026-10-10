# Direct Website Phone Scraping Script

Reusable script for extracting phone numbers from company websites. Run on any domain list — 51% hit rate across 498 MCA/business lending domains in 3 minutes (June 15, 2026).

## Usage

```bash
python3 scrape_phones.py domains.txt phones.csv
```

## What it does

- Tries homepage → `/contact` → `/contact-us` → `/about` → `/about-us`
- Falls back from HTTPS to HTTP
- Extracts US phone numbers via regex `(?:(?:\+|00)1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}`
- Filters out fake numbers (all-same-digit like 6666666667, area code starting with 0 or 1)
- Skips numbers near "fax", "tty", "tdd" in surrounding context
- Prefers numbers near "call", "phone", "contact", "sales", "support"
- Uses ThreadPoolExecutor(max_workers=20) for speed
- Handles SSL errors, timeouts, 403s gracefully

## Expected yield

- ~51% of domains return a phone number
- ~45% fail (no phone, timeout, blocked)
- ~4% return obviously fake numbers (filtered by validation)
