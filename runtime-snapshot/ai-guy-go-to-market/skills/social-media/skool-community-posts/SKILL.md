---
name: skool-community-posts
description: "Write Skool community posts from AI news briefs: research, format, batch output."
version: 1.2.0
tags: [skool, community-posts, ai-news, content-writing, social-media]
related_skills: [web-article-research]
---

# Skool Community Posts from News Briefs

## When to Use

User (typically Xander Viaña) asks to create posts for a Skool group based on numbered items from an AI news brief. Common triggers:
- "Create a post for numbers 3, 5, 9..."
- "Write Skool posts for these items"
- Reference to sample screenshots showing the desired format
- Mentions of "Skool group" or "community posts" + AI/tech topics

## Voice & Format Rules

These posts are for an **AI integrator community**. The audience is people learning to use AI tools professionally and position themselves as consultants. Write like **Xander talking directly to his Skool group** — first person, casual, telling a friend about something cool.

### Structure (every post follows this):
1. ***Italic headline with emoji at the end*** — one punchy line (use `*text here* 🐦` format, not bold)
2. **Opening hook** — 1-2 sentences, jump straight into the news. First-person voice ("I was exploring...", "The way I see it...")
3. **Body** — break down the news in very short paragraphs (1-3 sentences). Include specific numbers, benchmarks, and pricing. No fluff.
4. **Bullet points** — ONLY for setup steps or feature lists. Never use bullets for the integrator angle or community impact.
5. **Integrator angle** — **woven naturally into the flow**, never called out as a separate labeled section. No "How this affects our community" or "What this means for AI integrators" headers. The insight about why this matters should read like part of the conversation.
6. **Engagement question + :point_down:** — end with a question to drive comments followed by `:point_down:`

### Style constraints:
- **First-person conversational voice.** Write like you are the one who discovered this and are sharing it.
- **NO em dashes** (—) anywhere. Use commas, periods, or restructure the sentence instead.
- "Here is" not "Here's" (but contractions elsewhere are fine).
- Very short paragraphs. 1-3 sentences max. Easy to scan on mobile.
- Include real numbers: benchmarks, pricing, percentages, dates. At least 2-3 per post.
- No section headers like "How this affects" or "What this means." Everything flows naturally.
- No hashtags. One emoji in the headline, :point_down: at the end. Nothing excessive.
- **Target 120-180 words.** Shorter than the old 200-350 range. This community scrolls fast.

## Workflow

1. **Clarify** — confirm which numbered items from the brief, and ask for details if the brief isn't fully visible
2. **Research each topic** — use `execute_code` with urllib (see `web-article-research` skill). Start with DuckDuckGo HTML search, but if it returns empty (common), immediately fall back to HN Algolia API (see Research Strategy). Batch all searches in a single execute_code call, then fetch 1-2 articles per topic for detail.
3. **Draft all posts** — output them sequentially with clear separators (--- between posts)
4. **Review pass** — scan every post for em dashes and remove them. Verify all numbers/claims against research.

## Research Strategy

Use execute_code with Python urllib, not delegate_task (subagents often can't access browser):

```python
import urllib.request, urllib.parse, re

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
query = urllib.parse.quote("topic keywords 2026")
url = f"https://html.duckduckgo.com/html/?q={query}"
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='replace')

# Extract snippets, titles, links
results = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
```

Then fetch full articles for detail. Strip HTML, extract the 2000-4000 char range (skips nav/header boilerplate).

### Fallback: HN Algolia API

DuckDuckGo HTML search frequently returns empty results, especially for niche tech topics. When DDG fails, use the Hacker News Algolia search API — it indexes all HN stories and comments and rarely captchas:

```python
import urllib.request, json

hn_url = "https://hn.algolia.com/api/v1/search?query=TOPIC+KEYWORDS&tags=story"
req = urllib.request.Request(hn_url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
for hit in data.get('hits', []):
    print(f"{hit.get('title')} — {hit.get('url')} (points: {hit.get('points')})")
```

Use the discovered URL (often a tweet, blog post, or direct article) as the source. For tweet URLs, extract content via Twitter syndication (`cdn.syndication.twimg.com/tweet-result?id=TWEET_ID`) or X oembed API (`publish.x.com/oembed?url=TWEET_URL`) since Nitter is also unreliable.

## Companion Images

When the user wants an image to accompany a Skool post, generate a Canva-style graphic announcement as an HTML artifact, then screenshot it with the browser.

### Image Specs
- **4:3 aspect ratio** — set html/body to exactly 800×600, no margins, no visible borders or padding outside the canvas
- **Dark background** — #1a1817 or similar dark tone with subtle glow effects (blurred colored circles)
- **Accent line** — thin gradient bar across the top in warm tones (#cc5a4a → #d4896a)
- **Minimal content** — just the headline, subheading, feature pills, and a brand logo mark. No dates, no emojis, no section labels.
- **Logo** — small brand mark (geometric shape + text) in the top-left corner
- **Feature pills** — rounded pill badges with colored dots for key features/specs
- **Subtle decor** — thin outline circles in bottom corner, low opacity. Nothing distracting.

### Workflow
1. Write the HTML file to `/tmp/skool-post-<topic>.html` with html/body set to exactly 768×576 (a viewport-safe 4:3). Body background must match the canvas so there is no visible border.
2. Serve via `python3 -m http.server 8899 &` in `/tmp`
3. Navigate browser to `http://localhost:8899/skool-post-<topic>.html`
4. Use `browser_console` to get the canvas element's bounding rect: `document.querySelector('.canvas').getBoundingClientRect()` — note the left, top, width, height values
5. Take screenshot with `browser_vision` (vision may fail but screenshot is captured)
6. **Crop the screenshot** to the exact canvas dimensions using ffmpeg:
   ```
   ffmpeg -y -i <screenshot_path> -vf "crop=<width>:<height>:<left>:<top>" /tmp/<topic>-4x3.png
   ```
7. **Verify dimensions** with ffprobe:
   ```
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 /tmp/<topic>-4x3.png
   ```
   Confirm it reads e.g. `768,576` — exact 4:3 with no borders.
8. Share the cropped file via `MEDIA:/tmp/<topic>-4x3.png` in the response
9. Iterate based on user feedback

## Pitfalls

- **Browser viewport is wider than the canvas** — the screenshot will include black space if html/body width is 800px but the viewport is 1280px. Always crop with ffmpeg, never send the raw browser screenshot. Verify final dimensions with ffprobe.

- **Em dashes creep in** — do a final search-and-replace check. Common in AI-generated text.
- **Generic posts** — always include at least 2-3 specific numbers (benchmarks, pricing, dates, scores). Vague posts get no engagement.
- **Separate "How this affects" sections** — NEVER use labeled section headers for the integrator angle. Xander explicitly rejected this format. Weave the insight into the natural flow of the post instead.
- **Too long** — each post should be roughly 120-180 words. Longer than that and people scroll past on Skool.
- **Third-person or impersonal voice** — write in first person ("I was exploring...", "The way I see it..."). The post should sound like Xander sharing something he found.
- **Bullet points for community impact** — bullets are ONLY for setup steps or feature specs. Never use them for the "what this means for us" part.
- **delegate_task for research** — avoid. Subagents frequently can't access browser/Chrome. Do research in the main agent with execute_code.

- **DuckDuckGo HTML search returns empty** — DDG's HTML search endpoint (`html.duckduckgo.com/html/`) frequently returns zero results even for valid queries, especially after mid-2025. The page renders fine in a browser but the lite HTML endpoint seems degraded. When it happens, immediately fall back to the HN Algolia API (see Research Strategy fallback above). Do not waste calls retrying DDG with different query phrasings.
