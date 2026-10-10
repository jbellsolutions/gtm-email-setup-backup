# Domain Scraping for Email Discovery — June 2026

## Technique

Scraped 4,390 law firm domains via `urllib.request` with concurrent.futures:

```python
def scrape(domain):
    for scheme in ['https://', 'http://']:
        try:
            req = urllib.request.Request(f"{scheme}{domain}", headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode('utf-8', errors='ignore')[:200000]
                emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)))
                return emails
        except: continue
    return []
```

## Performance

| Metric | Value |
|--------|-------|
| Domains | 4,390 |
| Workers | 30 |
| Timeout | 5s |
| Success rate | 83.6% (3,668/4,390) |
| Duration | 323s (5.4 min) |
| Raw emails | 1,839 |
| After filtering generics/placeholders | 645 |
| After ScraperCity verification | 26 valid (4.3%) |
| Invalid | 471 (78.6%) |
| Cost (scraping) | $0 |
| Cost (verification) | $2.16 |

## False Positive Sources

- WordPress theme author emails embedded in templates (`impallari@gmail.com`, `aldusleaf`)
- GoDaddy/default hosting placeholders (`filler@godaddy.com`)
- Generic placeholder strings (`name@email.com`, `user@domain.com`)
- Pattern-matched email-looking strings that aren't real addresses
- Guessed first-name patterns that don't map to real inboxes (`sribera@riberalaw.com`)

## First-Name Extraction

```python
def extract_first_name(email, title):
    # Try email prefix for known patterns
    prefix = email.split('@')[0].lower()
    known_names = {'brendan', 'nathan', 'scott', 'bryan', 'david', 'terry', 'blake', 'christine'}
    if prefix in known_names:
        return prefix[0].upper() + prefix[1:]
    # Fallback to company name
    skip = {'the','law','a','an','and','of','at','pc','apc','llc','llp','pa','group'}
    for word in title.split()[:4]:
        w = word.strip(',.')
        if w.lower() not in skip and len(w) > 1 and w[0].isupper():
            return w
    return "there"
```

## Conclusion

DIY domain scraping is free but yields <5% real emails after verification. Only viable for small lists where 5% yield is acceptable. For anything larger, use purpose-built email finders (Apify snipercoder, Hunter.io, etc.).
