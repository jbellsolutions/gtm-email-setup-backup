# Website Research — JS-Heavy Site Extraction

Many coaching/wellness sites are built on Squarespace, Wix, Kajabi, or similar JS-heavy platforms. Direct `urllib` fetches return mostly `<script>` and CSS with minimal visible text. Two-pass approach:

## Pass 1 — Metadata (always works, 1-2 seconds)

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; HermesBot/1.0)'})
html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')

# Title
title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else 'N/A'

# Meta description
desc_m = re.search(r'<meta[^>]*name=[\"\']description[\"\'][^>]*content=[\"\']([^\"\']+)', html, re.I)
desc = desc_m.group(1) if desc_m else 'N/A'
```

## Pass 2 — Strip scripts/styles, extract visible sentences

```python
# Remove script and style blocks
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.I|re.S)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.I|re.S)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\s+', ' ', text).strip()

# Extract meaningful sentences (30+ char)
sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30][:10]
```

## What you typically get

- **Title + meta description:** enough to identify the business and niche
- **Visible sentences:** 5-10 meaningful fragments covering services, philosophy, testimonials
- **Contact/location:** phone area codes, city mentions in body text

## When this is enough

For building the partner-backed plan, you need: business name, niche, city/reach, what they sell, who they serve, and the owner's voice/philosophy. The metadata + visible text approach consistently delivers all of this for Squarespace/Wix/Kajabi sites in under 10 seconds, which is critical when processing 4+ leads in a cron run.

## When it's not enough

If the site returns fewer than 3 meaningful sentences, or if the title/description don't clearly identify the niche, the site may be fully client-side rendered (React, etc.). Fall back to web search or ask the user for a LinkedIn URL.