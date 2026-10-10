# Lead Enrichment Pipeline

Post-ScrapeCreators workflow: from raw company data → enriched contacts ready for cold email.

## PRIMARY: Profile Enrichment via `facebook profile` (1 credit/call)

The `facebook profile` endpoint is the reliable enrichment path. It bypasses Facebook's login wall and returns structured data:

```bash
scrapecreators facebook profile --url "https://facebook.com/FloridaFederalFHVAC" --pretty
```

**Returns:** `website`, `email`, `phone`, `pageIntro`, `rating`, `ratingCount`, `adLibrary.adStatus`, `creationDate`, `links`, `coverPhoto`, `profilePhoto`.

**Credit cost:** 1 per profile. Batch script: `references/profile-enrich.py`.

**Yield:** ~60-80% have website, ~20-40% have public email, ~50-70% have phone.

## Blockers Discovered (2026-06-01) — Now Bypassed

These were blockers before discovering the profile endpoint. Listed for context:

| Approach | Status | Why |
|----------|--------|-----|
| Facebook `/about` page scrape | ❌ Blocked | Login wall |
| DDG Lite search from VPS | ❌ Blocked | CAPTCHA |
| Google search from VPS | ❌ Blocked | Bot detection |
| Bing via browser | ❌ No results | Doesn't surface small local businesses |
| Domain guessing | ❌ 0% hit rate | Small contractors don't own `companyname.com` |
| **Profile endpoint** | ✅ Works | 1 credit, bypasses login wall |

## Domain Guessing (DEPRECATED)

Domain guessing from company names was tested on 30 HVAC contractors with **0% hit rate**. These businesses operate primarily through Facebook — most don't have standalone websites, and when they do, the domain rarely matches the business name cleanly. Do not rely on this approach. Use profile enrichment instead.

## Anymail Finder API v5.1

Base URL: `https://api.anymailfinder.com`
Auth: `Authorization: Bearer {api_key}` header (NOT `x-api-key`)

### Known Endpoints

| Endpoint | Method | Params | Notes |
|----------|--------|--------|-------|
| `/v5.1/find-email/person` | POST | `{domain, full_name}` | Requires BOTH domain AND name |
| `/v5.1/find-email/domain` | POST | `{domain}` | Returns emails for a domain |
| `/v5.1/find-email/company` | POST | `{company_name}` | By company name |
| `/v5.1/find-email/decision-maker` | POST | `{company, category}` | By role (e.g., "owner") |

All endpoints return 404 on wrong version. Only `v5.1` confirmed working. `v4.0` and `v5.0` both 404.

### Error Responses

```json
{"error":"upgrade_needed","message":"Your account does not have enough credits..."}
```

Credit status: check at https://app.anymailfinder.com/purchase

## Enrichment Workflow (End-to-End)

1. **Build lead list** via ScrapeCreators `adlibrary-search-companies` (state×keyword spraying)
2. **Discover domains** via domain guessing or browser search
3. **Find decision maker names** via website about pages (browser tool) or LinkedIn search
4. **Find emails** via Anymail Finder `/v5.1/find-email/person`
5. **Output enriched CSV** with: company name, domain, owner name, email, page_id

## Credit Economics

| Service | Cost per lookup | Needed per 250 leads |
|---------|----------------|---------------------|
| ScrapeCreators | 1 credit = ~1 API call | ~100 credits |
| Anymail Finder | 1 credit = 1 email lookup | ~125-250 credits (2 lookups per valid result) |

Both services deplete fast. Budget ~$50-75 per 250-lead batch for full enrichment.
