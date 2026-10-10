---
name: ai-news-digests
description: "Research and deliver AI news digests to Xander — covers shared sources, pitfalls, and both delivery formats (Breaking News Digest + Daily Trends Briefing)."
version: 1.0.0
tags: [ai-news, digest, briefing, research, xander]
related_skills: [web-article-research, skool-community-posts]
---

# AI News Digests

Research and deliver AI news to Xander in two formats: a twice-daily Breaking News Digest (Slack DM, headline format) and an on-demand Daily Trends Briefing (company-organized, tool/product focus). Both formats share the same research infrastructure — sources, tools, and pitfalls — described below.

## Shared Research Methodology

### Primary Sources (in priority order)

1. **AIToolsRecap daily digest** — `https://aitoolsrecap.com/Blog/ai-news-month-DD-2026` (adjust date). Best single source for the day's top stories. Fetch with `urllib` + User-Agent header.
2. **Hacker News front page** — `https://news.ycombinator.com/` — grep for AI-related stories. HN surfaces what the developer community is reacting to, especially "Show HN" posts.
3. **Company blogs** — check directly:
   - Anthropic: `https://www.anthropic.com/news`
   - OpenAI: `https://openai.com/index/` (blocks raw HTTP → use browser_navigate or rely on AIToolsRecap coverage)
   - Mistral: `https://mistral.ai/news/`
   - Meta AI: `https://ai.meta.com/blog/`
   - Google: `https://blog.google/technology/ai/`
4. **LLM-stats news** — `https://llm-stats.com/ai-news` (JS-rendered — use browser_navigate)
5. **GitHub trending** — `https://github.com/trending?since=daily` — filter for AI repos
6. **Nous Research** — `https://nousresearch.com/blog/` + `https://github.com/NousResearch/hermes-agent/releases`

### Research Tools

- Use `execute_code` with Python `urllib` for raw HTTP fetches (curl is not installed)
- Use `browser_navigate` + `browser_snapshot` for JS-rendered pages
- Batch all fetches in a single `execute_code` call when possible

### Shared Pitfalls

- **OpenAI.com blocks curl (403).** Use AIToolsRecap or browser_navigate for OpenAI stories. Don't waste time fighting the block.
- **DuckDuckGo HTML search no longer works.** `html.duckduckgo.com/html/` returns a JS-only page with zero search results as of May 2026. Skip it.
- **GitHub release detail pages require JS.** `/releases/tag/v0.13.0` 404s on raw HTTP. Use the main `/releases` page (server-side rendered) for version summaries.
- **TechCrunch/Verge/VentureBeat are JS-rendered.** Raw HTTP returns empty. Use browser_navigate if needed, but AIToolsRecap usually covers the same stories.
- **Some days are light.** AIToolsRecap typically has 3-5 major stories. 4-8 total after supplementing from HN/blogs is normal. Don't pad — ship what's there.
- **Be thorough, not fast.** Check ALL sources before concluding a day is slow.

### Nous Research Coverage

Always check Nous Research in both digest formats:
- Blog: `https://nousresearch.com/blog/`
- GitHub releases: `https://github.com/NousResearch/hermes-agent/releases`
- Check for: Hermes Agent releases, Hermes model updates, Tool Gateway/Portal news, Psyche Network, Atropos, new model releases, NousCoder

---

## Format A: Breaking AI News Digest

**Trigger:** Twice-daily cron (3 PM PH / 3 AM EDT and 3 AM PH / 3 PM EDT). Also ad-hoc: "give me the breaking AI news."

**Delivery:** Xander's personal Slack DM. Separate from the Daily Trends Briefing — broader scope, different format.

### Content Scope

Focus on **huge / breaking news from the top AI companies**: OpenAI, Anthropic, Google/DeepMind, Meta, Mistral, Nous Research. Include smaller players only if the news is genuinely major.

#### INCLUDE
- Major model releases, API changes, pricing shifts
- New products, platforms, developer tools from top companies
- Significant open-source releases with benchmark implications
- Company-defining deals or strategic moves
- Nous Research — always check, include if anything notable

#### EXCLUDE
- Funding rounds (unless truly massive + strategic)
- Policy/regulation/court cases
- Hiring announcements, office openings
- Minor product updates, point releases
- Academic papers without practical implications

#### EDGE CASES
- Infrastructure deals (compute, data centers) — include if they involve top AI companies or reshape the competitive landscape
- Corporate governance — skip unless it directly impacts product availability

### Format

Concise headlines with source links. One sentence of context + the link.

```
**1. Company — Headline**
One sentence of context with key numbers.
→ url

**2. Company — Headline**
One sentence of context with key numbers.
→ url
```

- **Every item must have a source link** — non-negotiable
- Order by significance, not alphabetically
- If a day is light (3-4 stories), ship it as-is. Don't pad.
- If a day is heavy (10+), include everything but keep entries tight.

### Deduplication
- **NEVER repeat a story** already delivered in a previous run of THIS format
- Track what was sent and deduplicate. Use `session_search` to find prior deliveries
- Repeats across the TWO FORMATS are fine — repeats within this format are not
- Start from scratch — assume no prior deliveries for dedup purposes until history accumulates

### Cron Jobs

| Run | PH Time | EDT Time | Cron |
|-----|---------|----------|------|
| Morning US wave | 3 AM PH | 3 PM EDT (prev) | `0 15 * * *` |
| Overnight/Asia wave | 3 PM PH | 3 AM EDT | `0 3 * * *` |

---

## Format B: Daily AI Trends Briefing

**Trigger:** On-demand. "Give me the DAILY AI TRENDS BRIEF for today" / "What's happening in AI today?"

**Delivery:** Returned in-chat. Company-organized with detailed sections.

### Content Scope

Focus on **tools, products, features, and updates from AI companies**. Hard filter — Xander will push back if diluted with funding/strategy filler. Ask: "Is this a thing someone can use, install, or access today?"

#### INCLUDE (always)
- New model releases, API access expansions, model upgrades
- New tools, plugins, SDKs, frameworks, MCP servers, integrations
- Product launches, feature rollouts, platform expansions
- Open-source projects (Show HN, GitHub trending, new repos)
- Model benchmarks, capability improvements, context window bumps
- Nous Research (mandatory section, every brief)

#### EXCLUDE (never — these trigger pushback)
- Funding rounds (Series A/B/C, valuations, investor details)
- Earnings reports (Q1/Q4 revenue, net income, profit margins)
- Hiring announcements
- Corporate governance (IPO prep, share sellers, secondary markets)
- Policy, regulation, court cases, government actions
- Opinion pieces, culture-war articles
- Hardware/robotics unless it directly ships an AI product

#### EDGE CASES
- A company raises money AND launches a product → cover the product, skip the raise
- A big tech company reports earnings → skip unless there's a specific new AI product
- A startup emerges from stealth → skip unless they published a model, paper, or tool

### When Today Is Light on Tools

1. **Lead with "Tools & Products That Shipped"** — pull everything tool-adjacent, even minor launches
2. **Pull from the last 1-2 days** — yesterday's launches are fair game if Xander might have missed them
3. **Check GitHub trending** for AI open-source projects that popped today
4. **Relegate non-tool news** to a clearly-labeled secondary section ("Everything Else Today Is Strategy / Funding")
5. **Be honest if it's slow** — a short, honest brief beats padding with funding stories

### Format

```
# 📰 Daily AI Trends Brief — Day, Month DD, 2026

---

## Company Name

**Headline with key detail.** Context with specific numbers. Why it matters in one sentence.

---

## ⚡ Quick Hits

- **Bullet-point format** for smaller stories.
```

- Full company sections for major tool/product announcements (3+ sentences)
- `## ⚡ Quick Hits` for smaller items (single bullets)
- `## Nous Research` is a **required section** in every briefing
- Every entry needs at least one concrete number: price, benchmark score, context window size, percentage change, date of release

### Briefing-Specific Pitfalls

- **FUNDING ROUNDS ARE THE #1 PUSHBACK TRIGGER.** Even if it's the top story, do NOT lead with it. Relegate to the secondary section.
- **Fetching article URLs directly often 404s.** Prefer search snippets and cross-reference across multiple sources.
- **Don't spend too long on research.** 3-4 execute_code calls max. Better to ship with 8 solid items than chase 20.
- **Include specific numbers** in every entry.

---

## Reference

- AIToolsRecap monthly hub: `https://aitoolsrecap.com/Blog/ai-news-month-2026` — useful for broader month context on light days
