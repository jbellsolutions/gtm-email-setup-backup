# Researching Captcha-Blocked Sites

Many coaching/business sites use SiteGround, Bluehost, or similar hosting that serves captcha challenges to non-browser requests. Google cache is also unreliable (returns obfuscated JS). When the lead's site is blocked, don't give up — the DuckDuckGo HTML search fallback works.

## Why this happens

Sites hosted on SiteGround use `sgcaptcha` (SiteGround Captcha) that returns a meta-refresh redirect for any request without a valid browser session:
```html
<meta http-equiv="refresh" content="0;/.well-known/sgcaptcha/?r=%2F&y=ipr:...">
```
Google cache pages often serve the same obfuscated JS blob instead of cached content.

## The DDG HTML search fallback

DuckDuckGo's HTML-only search endpoint (`html.duckduckgo.com`) returns clean, parseable HTML with rich snippets — no JS, no captcha. These snippets often contain enough detail for a quality plan:

```bash
# Search for the lead by name + business + niche
curl -sL --max-time 15 -o /tmp/research.html \
  "https://html.duckduckgo.com/html/?q=kylie+ryan+my+mind+coach+supercoach+society+life+coach+training" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
```

## Extracting what you need

DDG HTML results include three fields per result block: title, URL, and snippet. Combined, they give you:

- **Business description** — from the meta/snippet text
- **Products/services** — membership sites, courses, private coaching
- **Social proof** — Facebook like counts, YouTube channel descriptions
- **Niche positioning** — "Australia's leading Mindset & Motivation Coach", "22 years experience"
- **Related sites** — personal brand domains, membership platforms, team pages

Example extraction script (write to file — never pipe):

```python
import re, html as htmlmod

with open('/tmp/research.html') as f:
    content = f.read()

blocks = re.findall(r'<div class="result results_links.*?</div>\s*</div>\s*</div>', content, re.DOTALL)

for block in blocks:
    title_m = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
    snippet_m = re.search(r'class="result__snippet"[^>]*>(.*?)(?:</a>|$)', block, re.DOTALL)
    
    title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else ''
    snippet = re.sub(r'<[^>]+>', '', snippet_m.group(1)).strip() if snippet_m else ''
    
    print(f'{htmlmod.unescape(title)}')
    print(f'  {htmlmod.unescape(snippet)[:400]}')
    print()
```

## What you lose vs. a full site visit

- No "about" page narrative or founder story
- No pricing or specific program details
- No recent blog posts or case studies
- No visual brand assets

## What you still get (enough for a plan)

- Niche confirmation and business category
- Years of experience and geographic reach
- Product types (membership, courses, 1:1 coaching)
- Adjacent brands and related URLs
- Social presence indicators (Facebook followers, YouTube channel)

## When to escalate

If DDG returns fewer than 3 relevant results or no business description at all, the lead may have minimal web presence. In that case:
- Try searching just the domain name
- Try Facebook/LinkedIn search (often unblocked)
- If still thin, mark the plan with fewer named entities and more category-based partners — never invent names

## Session proven (July 13, 2026)

Kylie Ryan — all 3 sites (mymindcoach.com.au, supercoachsociety.com, kylieryan.com) returned SiteGround captcha. DDG search yielded 9 rich results with enough detail to build a quality 5-page plan: niche (mindset coaching + coach training), location (Sydney), experience (22 years), products (SuperCoach Society membership, private coaching, courses, YouTube), and Facebook following (13K+).