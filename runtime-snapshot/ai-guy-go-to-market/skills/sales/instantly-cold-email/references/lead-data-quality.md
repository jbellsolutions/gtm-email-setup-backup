# Instantly Lead Data Quality

Instantly leads scraped without enrichment have null phone/social fields.

## The problem

Leads imported via Instantly's bulk import or Apify scraping (without enrichment add-on) have:

| Field | Typical value |
|---|---|
| `phone_number` | `null` |
| `linkedin_profile` | `null` |
| `company_url` | `null` |
| `website` | `null` |

**Real example (July 2026):** 91 tracked Owned Audiences leads — ZERO had phone or social data. The only phone numbers found were extracted from email signatures in reply body HTML.

## Where phone numbers come from

The ONLY reliable source for phone/social data post-scrape is the **reply body HTML** in message history. Parse with:

```python
import re

# Phone numbers in signatures
phones = re.findall(r'(?:\+1[-\s]?)?\(?\d{3}\)?[-\s\.]?\d{3}[-\s\.]?\d{4}', body)
phone_labels = re.findall(r'(?:phone|call|cell|mobile|text|tel)[\.:\s]*[\+\d\(\)\-\s\.]{7,20}', body, re.IGNORECASE)

# LinkedIn profiles
linkedin = re.findall(r'https?://(?:www\.)?linkedin\.com/[^\s<>"\']+', body)

# Websites
websites = re.findall(r'https?://[^\s<>"\']+', body)
```

## Instantly API — batch lookups are fast but unhelpful

```python
# This returns in 1-2s per lead, but will have nulls if scraped without enrichment
mcp_Instantly_get_lead_by_email(email="lead@domain.com")
```

## Fix: Enrich at scrape time

- **ScraperCity** — `find_mobiles` and `find_emails` can enrich after the fact (requires active API key)
- **Apify** — some actors include phone/social enrichment
- **Manual** — extract from reply signatures (works but only after lead replies)

## Recommendation

If phone/social data matters for call tracking (Called 1-5 columns), enrich at scrape time OR budget for a ScraperCity backfill after leads reply. Lead signatures are the most reliable free source but only available post-reply.