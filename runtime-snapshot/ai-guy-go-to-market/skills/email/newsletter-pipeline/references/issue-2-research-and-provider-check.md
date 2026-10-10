# Issue 2 Research and Provider Check

## Established Referral Channel format

The supplied Issue 1 source and HTML document four story cards total: three editorial cards plus the native affiliate announcement at position 3. The generic playbook says six cards, but the prior gold-standard artifact takes precedence for this identity unless the user requests a format change. Preserve the four-card skeleton and image slots:

```text
banner.jpg
s1.jpg
s2.jpg
s3.jpg   # native card
s4.jpg
s5.jpg   # utility
```

## Sources successfully fetched for the pilot

- Awin, “Our Top Affiliate Marketing Predictions for 2026”: https://www.awin.com/us/sector-insights/affiliate-marketing-trends-2026
  - Published Jan. 29, 2026.
  - Page cites an eMarketer forecast of roughly $1 in every $7 of US ecommerce sales coming from affiliate marketing in 2026.
  - Treat as a forecast and attribute it to the Awin roundup/eMarketer, not as booked revenue.
- Forrester, “Continued Growth In Scale And Complexity: The State Of Partner Ecosystems In 2025”: https://www.forrester.com/blogs/the-state-of-partner-ecosystems-2025/
  - Fetched page states 67% of surveyed B2B decision-makers expected indirect revenue to grow above or significantly above the prior year, described as more than 30% greater.
- Impact.com, “Why your affiliate program is your most underrated GEO asset”: https://impact.com/affiliate/generative-engine-optimization-affiliate-strategy/
  - Analysis: partner content can influence AI visibility; do not turn its strategic claims into unsupported market statistics.
- Impact.com, “Why your 2026 search strategy depends on partnerships (and how to track the results)”: https://impact.com/affiliate/how-to-track-brand-mentions-in-ai-search/
  - Page reports several attributed claims, including 23% of 2026 Super Bowl national ad spots linked to AI and 97% of brands integrating AI into affiliate strategy. Verify the original linked sources before using these numbers in a future issue.
- Impact.com, “How to build a brand-owned influencer ecosystem”: https://impact.com/influencer/how-to-build-an-online-community/
  - Case study says Elite Supplements managed 50+ partners manually and Impact reports 10+ ROAS month over month within 12 months after operational changes. Frame as a platform/company case study, not a benchmark or promise.
- Impact.com, “Your partnership program is driving AI-influenced sales—your attribution model just can’t prove it”: https://impact.com/affiliate/measure-roi-from-zero-click-searches/
  - Page attributes 73% of brands reporting increased affiliate-program revenue to Impact.com’s 2025 Global State of Affiliate Marketing report. Verify the underlying report before reuse.
- Conquer Local / Amber Spears episode: https://www.conquerlocal.com/podcast/partnering-for-profits-how-to-build-powerful-affiliate-relationships/
  - Fetched page dated May 29, 2024. Contains podcast-page claims about Amber Spears and East 5th Avenue. Do not print the “$530 million” or “2,500 companies” figures without clearly attributing them to the page’s self-reported promotional copy.

## Provider / 401 diagnosis

- `/opt/data/config.yaml` routes auxiliary `web_extract`, `compression`, `session_search`, `skills_hub`, and `approval` to DeepSeek with `key_env: DEEPSEEK_API_KEY`.
- The configured DeepSeek key was present and a direct `GET https://api.deepseek.com/v1/models` probe returned HTTP 200.
- No separate title-generation key was found in the accessible environment/configuration. A prior title-helper 401 was not reproducible; likely causes are a stale process environment, cached helper credential, or a different provider-specific key.
- Safe diagnostic pattern: inspect only variable names/presence and key length/prefix; never print full credentials. Do not rotate or edit credentials without explicit instruction.

## Search fallback

Google search was blocked by an anti-bot interstitial in the browser. Bing News and direct authoritative URLs worked. When search is blocked, use direct source pages, Bing News, or the publisher’s own resource hub; do not fill gaps with unverified summaries.
