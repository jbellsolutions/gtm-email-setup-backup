# DiscoLike — Platform Insights

Notes from the founder call with George Rekouts + reading the docs.

## How DiscoLike is different

- **SSL certificates, not LinkedIn.** Every B2B-data competitor (Apollo, ZoomInfo, Ocean.io, List Kit, Prospia) buys the same LinkedIn scrape feed from one of two Israeli companies. DiscoLike spent 4 years building its own index off SSL certificate issuance.
- **Coverage:** ~70M+ business domains. ~3× LinkedIn coverage. ~2× Google Maps coverage.
- **Why this matters:** drive-to-location businesses don't put pins on Google Maps (they'd be 50 miles off). Fake companies on LinkedIn are rampant — created so scrapers can "see" something. DiscoLike sees only what registered a real domain + cert.
- **Demo data point:** 23,000+ merchant cash advance broker domains vs. ~2,300 in List Kit for the same keyword.

## Query design — what George actually said

- **ICP prompt → look-alike text + example domains + keywords.** Type the ICP in plain English. The system drafts: 5-10 anchor domains, a description for vector similarity, and Google-style keywords.
- **Vector + keyword combo is the gold standard.** Vector similarity on the description + AND on the keywords against the home page.
- **`+keyword` forces the word.** Bare keywords are OR by default. Prefix with `+` to make the term mandatory.
- **Validate before pulling.** The dashboard's Validate button runs yes/no/partial fit-check on a sample. >80% fit is great, 47% means you can tune higher.
- **Tuning loop is cheap.** Iterating the query is essentially free (counts + validate samples). Moats over Apollo/List Kit: "you can see fit BEFORE you pay for the list."

## Sizing companies without LinkedIn employee data

- `digital_footprint` (0-800) — derived from cert issuance volume + age. Bigger company = more certs across more subdomains = higher score.
- `employee_range` exists as a coarse bucket but is heuristic.
- For SaaS detection: `vendor-and-technology-data` is way better than BuiltWith because cert-keyed.

## Pricing reality

- **$3 per 1,000 records** for the list pull (discover endpoint).
- **Pro plan ($199/mo)** required to pull >10K records in one go.
- Starter can design and validate freely. Don't upgrade until you've validated.
- **Other endpoints:** single-domain reads are very cheap (estimate <$0.01). DiscoGen calls bill only on new domains; same domain within 90 days is cached and free.

## BYOM / BYOS

- **BYOM (Bring Your Own LLM):** plug your own provider into DiscoGen. George's recommendation: **Grok 4.3** (xAI overcapacity = cheap). OpenAI/Anthropic/Llama all work via LiteLLM-style proxy.
- **BYOS (Bring Your Own Search):** plug your own search provider for contact-finder. Currently Serper. Built-in SerpAPI coming (~3× cheaper). Recommend waiting if cost matters.
- **Where to add keys:** Settings → Integrations → AI Providers / Search Providers in the dashboard. MCP tools `llm-providers` and `search-providers` manage these programmatically (both FREE).

## Contact-finder behavior

When you call `search-contacts` (or `generate-contacts` via BYOM/BYOS), the contact finder is smart about WHERE to look:
- B2B SaaS → Crunchbase + LinkedIn
- Influencers → social platforms
- Lawyers → bar association
- Artists → portfolio sites
- General businesses → company website + LinkedIn

It picks ~6-7 best URLs per query based on company industry + home page text.

Email patterns: contact finder returns name. Verify the email via something like Million Verifier MCP or bouncer MCP. Guessing emails is a high-bounce, low-quality path.

## What's coming (from the founder call)

- Built-in SerpAPI (3× cheaper than Serper) — eta unspecified
- More improvements to DiscoGen quality
- "You bring your own model" is the norm for power users

## Justin's targets (from the call)

1. **Merchant cash advance brokers, US small** — tighten `digital_footprint` to drop big brokers. `phrase_match: "cash advance" "merchant cash advance" "working capital" +cash`
2. **Business loan brokers** — superset of MCA. Use as separate query; keep it narrow.
3. **Virtual-assistant agencies (PH, SA, ME)** — for recruiting business.
4. **Influencers / content creators** — domain-based discovery only works if they have a site. Many don't. Use contacts flow heavily.
