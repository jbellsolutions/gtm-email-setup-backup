# DiscoLike — Filter Grammar Reference

Loaded by `discolike-design` and `discolike-walkthrough` when designing a query. All field names below appear on `count-matching-domains`, `discover-similar-companies`, and most contact-search tools.

## phrase_match — the text grammar

The most powerful filter. Google-style operators. Up to 20 phrases per call.

| Pattern | Meaning |
|---------|---------|
| `working capital` | bare words = **OR** between terms |
| `"merchant cash advance"` | double-quoted = exact phrase match |
| `+cash` | `+` prefix forces **AND** — the term MUST appear |
| `-consulting` | `-` prefix excludes (verify in your tier) |

Example from founder call:
```
working capital business funding cash advance +cash
```
= match any of `working capital`, `business funding`, `cash advance`, AND the word `cash` must also appear on the page. Pulls the brokers, drops the unrelated.

## Size + footprint

| Field | Values |
|-------|--------|
| `employee_range` | `1-10`, `11-50`, `51-200`, `201-500`, `501-1k`, `1k-5k`, `5k-10k`, `10k+` |
| `revenue_range` | `<1M`, `1-10M`, `10-100M`, `100M-1B`, `>1B` |
| `min_digital_footprint` | integer 0-800 (default 50) |
| `max_digital_footprint` | integer 0-800 (default 800) |
| `start_date` | YYYY-MM-DD or range; company inception |

**Digital footprint = SSL-cert-derived size signal.** This is the proxy for "company size" since DiscoLike isn't scraping LinkedIn employee counts. Lower the `max_digital_footprint` to find smaller players. Raise the `min` to drop tiny shops.

## Location

| Field | Values |
|-------|--------|
| `country` | ISO-3166-1 alpha-2 (e.g. `US`, `GB`) OR region codes (`ANZ`, `APAC`, `ASEAN`, etc.) |
| `state` | ISO-3166-2 or full state name. SINGLE country per request. |
| `language` | ISO-639-2 from the 56 supported. |

Negation: every location field has a `negate_*` twin (`negate_country`, `negate_state`, `negate_language`).

## Business shape

| Field | Values |
|-------|--------|
| `business_model` | `B2B`, `B2C`, `B2G`, `G2B`, `G2C`, `D2C`, `C2C`, `C2B` (OR logic) |
| `social` | `facebook`, `linkedin`, `twitter`, `instagram`, etc. — required social presence |
| `category` | BizData category strings (industry) |
| `tech_stack` | vendor domains, e.g. `hubspot.com`, `gohighlevel.com`, `salesforce.com` |

Negation twins exist for all of these too (`negate_business_model`, `negate_social`, `negate_category`, `negate_tech_stack`).

**`tech_stack` notes.** Keyed off SSL certs the vendor issues to the client. Higher resolution than BuiltWith for SaaS detection. GoHighLevel (`gohighlevel.com`) shows up on ~535,000 client domains — the largest CRM signal in the dataset.

## Pagination / output

| Field | Values |
|-------|--------|
| `max_records` | how many to return |
| `offset` | pagination offset |
| `redirect` | `0` or `1` — include redirect-only domains |

## Contact-search additions

When using `search-contacts`:
- `seniority` (e.g. `vp`, `director`, `c-level`)
- `department` (e.g. `Marketing`, `Engineering`, `Sales`)
- `skills`, `title`, `summary`, `name`
- `person_country`, `person_state`
- `has_email`, `email_validated`, `has_phone`, `has_mobile`, `has_linkedin`
- `min_connections`
- `filter_industry`, `filter_country`, `filter_state`, `employee_range` (these filter the contact's COMPANY, not the contact)
- `max_records` (20-10K), `max_companies` (1-10K), `results_by_company` (0-100), `consensus` (1-20)

## Working pattern (from founder call)

1. ICP prompt in plain English: `"merchant cash advance brokers in the US, small ones"`.
2. `run-discogen` drafts: example domains + "look-alike text" description + suggested `phrase_match` keywords.
3. Tighten by hand:
   - Add `+cash` to force the word
   - Drop `max_digital_footprint` from 800 to something lower to drop big brokers
   - Raise `min_digital_footprint` to drop microsites
4. `count-matching-domains` (FREE) → see the size move.
5. `save-mcp-query` (FREE) → persist before any paid call.
6. Validate sample via `run-discogen` with yes/no prompt (paid, but capped).
7. Only then think about a real `discover-similar-companies` pull.
