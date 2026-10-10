---
name: web-article-research
description: "Fetch, extract, and synthesize multiple web articles into research briefings."
version: 1.0.0
tags: [research, web-scraping, content-briefing, news-analysis]
---

# Web Article Research & Content Briefings

## When to Use

**User provides URLs** (news articles, blog posts, release announcements, GitHub repos) and asks for deeper research, summaries, or content angles. Common triggers:
- "Tell me more about these" + list of links
- "Summarize these articles"
- "Research these topics for content ideas"
- News digest deep-dives (user picks items from a curated list)

**User asks for current news with no URLs** — "what's changing today", "AI news roundup", "what happened in AI this week". Follow the News Discovery workflow below to source stories, then compile a numbered briefing. Offer deep dives on any items the user picks.

## News Discovery & Sourcing (when no URLs are provided)

When the user asks for current news but provides no URLs, follow this sourcing strategy in order:

### Priority 1: Direct aggregator fetches (fastest, most reliable)
Skip search engines entirely. Go straight to known AI news aggregators:
- **aiflashreport.com** — daily AI news roundup, updated every 24h. Fetch homepage or `?date=YYYY-MM-DD`. Covers model releases, company news, tools, research.
- **aiweekly.co** — weekly newsletter with live alert ticker. Good for breaking stories and broader industry context (funding, legal, geopolitics).
- **theaitrack.com** — monthly digest with in-depth breakdowns by topic. Heavy CSS bloat, so look for content after skipping the inline stylesheet dump.

### Priority 2: Google News RSS (reliable, structured)
When direct aggregators don't cover a topic or you need broader coverage:

```python
import urllib.request, urllib.parse, re

query = urllib.parse.quote("search terms here")
url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=12)
rss = resp.read(50000).decode('utf-8', errors='replace')

items = re.findall(r'<item>(.*?)</item>', rss, re.DOTALL)
for item in items:
    title = re.search(r'<title>(.*?)</title>', item)
    desc = re.search(r'<description>(.*?)</description>', item)
    source = re.search(r'<source[^>]*>(.*?)</source>', item)
```

### Priority 3: DuckDuckGo HTML search (fragile, rate-limited)
Use `https://html.duckduckgo.com/html/?q=...` as a last resort. DDG rate-limits aggressively — expect empty results after 2-3 queries in quick succession. When that happens, fall back to Priority 1 or 2.

### News curation preferences

When Xander (or a collaborator in his workspace) asks for the daily AI trends brief, focus on **tools, products, features, and updates from AI companies** — not finance, policy, regulation, or investment news. Organize by company (OpenAI, Anthropic, Google, Meta, etc.) or product category. If the user says "can you give me more like..." or "I'm interested in...", they want a refocused/repivoted version of the briefing, not a longer list. Cut the fat, keep it punchy and scannable.

### Researching specific stories for deep dives
When the user picks items from the briefing for more detail, use Google News RSS with specific queries to find articles, then fetch those articles directly with urllib. Do NOT try to search DuckDuckGo again if it was already rate-limited.

**Critical pitfall — Google News RSS article links are NOT directly fetchable:** Google News wraps article links in redirect URLs (e.g., `https://news.google.com/rss/articles/CBMi...`) that return a JS-rendered interstitial page, not the actual article. urllib will get CSS/JS garbage, not readable content. Instead, use the `<source>` and `<title>`/`<description>` fields from the RSS items directly — they contain enough detail for a deep dive. Only attempt direct article fetches when you have the actual publisher URL (not a Google News redirect).

This environment often lacks `curl` and browser/Chrome may not be pre-installed. Use this priority order:

### 1. Python urllib (fastest, works for most sites)
```python
import urllib.request, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://example.com/article"
req = urllib.request.Request(url, headers=headers)
r = urllib.request.urlopen(req, timeout=15)
content = r.read(80000).decode('utf-8', errors='replace')

# Strip HTML to text
content = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.DOTALL|re.IGNORECASE)
text = re.sub(r'<[^>]+>', ' ', content)
text = re.sub(r'\s+', ' ', text).strip()
```

### 2. GitHub API (for repos/READMEs)
```python
# Repo metadata
url = "https://api.github.com/repos/OWNER/REPO"
req = urllib.request.Request(url, headers={**headers, 'Accept': 'application/vnd.github+json'})
data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())

# README raw content
url = "https://raw.githubusercontent.com/OWNER/REPO/main/README.md"
```

### 3. Browser (last resort — for JS-heavy sites like Wix, SPAs)
Browser/Chrome may need installing first:
```bash
npx puppeteer browsers install chrome
```
Note: Even after install, the agent-browser cache path may not pick it up. The browser tool checks specific paths — Puppeteer installs to `~/.cache/puppeteer/chrome/`.

### 4. Alternative sources (when primary URL fails)
- HuggingFace model pages → use HF API or direct urllib fetch
- GitHub repos → use GitHub API (see above)
- News articles behind 403 → try web_search for cached/alternative coverage
- Wix/SPA sites → look for the same content on a different domain

## Pitfalls

- **403 Forbidden**: Common on OpenAI, Anthropic docs, and some news sites. Try alternative sources or web_search.
- **DuckDuckGo rate-limiting**: DDG HTML search silently returns empty results after 2-3 rapid queries. Use Google News RSS or direct aggregator fetches as the primary approach for news discovery. Only use DDG as a fallback, and space queries at least 1 second apart.
- **JS-rendered sites** (Wix, React SPAs): urllib returns CSS/JS gibberish. Need browser or find alternative source.
- **delegate_task max concurrency**: Default is 3 concurrent subagents. Don't send 4+ tasks in one call.
- **Subagent browser failures**: Subagents often can't use browser tools (Chrome not found in their env). Even after installing Chrome with `npx puppeteer browsers install chrome` in the main agent, subagents launched via delegate_task run in separate environments and won't see it. **Always prefer fetching in the main agent with execute_code** for reliability. Reserve delegate_task for non-browser work only.
- **Large HTML payloads**: Limit reads to 50-80KB, strip scripts/styles before processing.

## Synthesis Workflow

### For user-provided URLs:
1. **Batch independent fetches** using execute_code with multiple URLs in one call
2. **For each article**, extract: key claims, numbers/stats, quotes, named entities, dates
3. **Cross-reference** claims across sources when covering the same topic
4. **Format output** based on user's use case:
   - **Content creator**: Lead with the "angle" — what makes this a story? Include specific numbers, quotes, and a hook
   - **Researcher**: Lead with facts, methodology, limitations
   - **Decision maker**: Lead with implications and action items
5. **Offer next steps**: draft scripts, outlines, social posts, or deeper dives on specific items

### For news discovery (no URLs provided):
1. **Source from aggregators first** (aiflashreport.com, aiweekly.co) to get a quick snapshot
2. **Compile a numbered briefing** organized by category (Model Wars, Legal & Geopolitics, Hardware, Tools, Quick Hits). Each item gets 1-2 lines with the key fact and source.
3. **Add emoji section headers** for scanability. Keep each item punchy — the whole list should fit in one Slack message.
4. **Wait for user to pick items** before doing deep dives. When they do, use Google News RSS to find articles on that specific topic, then fetch 1-2 articles for detail.
5. **Deep dive format**: bolded headline, key specs/numbers in bullet form, strategic context paragraph, and a "what this means" takeaway.
