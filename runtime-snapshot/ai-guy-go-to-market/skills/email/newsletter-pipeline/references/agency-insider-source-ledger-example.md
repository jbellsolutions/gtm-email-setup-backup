# Agency Insider verification example

This reference records the source-verification pattern established during the Agency Insider revision. It is an example of evidence format, not a permanent news bank.

## Verified direct sources

1. AdExchanger, `Q2 2026 Was The Quarter AI Media Started To Scale`
   - URL: https://www.adexchanger.com/data-driven-thinking/q2-2026-was-the-quarter-ai-media-started-to-scale/
   - Fetch result: HTTP 200
   - Supporting excerpts: “Holding companies Dentsu, WPP, Publicis and Omnicom joined as agency partners...” and “At Google Marketing Live, the company delivered new ad formats in AI Mode including conversational discovery ads and highlighted answers...”

2. Forrester, `Predictions 2026: Marketing Agencies Resign Their Agency`
   - URL: https://www.forrester.com/blogs/predictions-2026-marketing-agencies-resign-their-agency/
   - Fetch result: HTTP 200
   - Supporting excerpts: “A 15% reduction in agency jobs...” and “In 2026, principal media ... will account for nearly 33% of total agency billings.”

3. Accenture Newsroom, `Accenture to Acquire Leading Creator and Social Agency Whalar, from Whalar Group`
   - URL: https://newsroom.accenture.com/news/2026/accenture-to-acquire-leading-creator-and-social-agency-whalar-from-whalar-group
   - Fetch result: HTTP 200
   - Supporting excerpts: U.S. creator-economy ad spend is expected to reach $43.9 billion in 2026; more than $600 million in creator campaigns across more than 40 countries and 15 languages.

## Blocked native source example

The requested Medium short URL returned HTTP 403 from the execution environment because of a Cloudflare challenge. Record that status honestly. Do not describe it as HTTP 200 or direct-fetch verified. If the user supplies the article's verified content, use only that supplied content and keep the link as the requested URL. Do not invent case studies, timelines, conversion rates, or performance results.

## Evidence rule

A source ledger must include, per story: final direct URL, HTTP status, publication, date if available, and an exact supporting sentence or figure copied from the fetched page. A Google News redirect, guessed slug, homepage, or subagent assertion is not sufficient.