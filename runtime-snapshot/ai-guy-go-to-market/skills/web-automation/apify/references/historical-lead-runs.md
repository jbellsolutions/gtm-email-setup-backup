# Historical lead-run assembly reference

## Selection lesson

A single day can contain many unrelated Apify runs. In the July 30, 2026 session, the account had 39 successful runs: marketing/AI agency searches, solar searches, gym searches, and email-verifier runs. The requested Solar/Gyms output required selecting relevant Google Maps scrape runs and their corresponding verifier runs, not aggregating all 39 runs.

Classify Google Maps runs from dataset items, especially:

- `searchString` values such as `solar company ...` or `gym ...` / `fitness center ...`
- `categoryName` and `categories`
- `leadsEnrichment` presence for contact records

Do not rely on actor ID alone: both solar and gym runs used the same Google Maps scraper actor, and unrelated campaigns used it too.

## Data shape

Google Maps scrape datasets contained business records with `placeId`, website, phone, location, `searchString`, and optional `leadsEnrichment`. Verifier datasets contained one record per email with `email`, `status`, `technical_status`, `score`, and `catch_all`.

Recommended output layers:

1. Deduplicated business list by `placeId`.
2. Deduplicated contact list by lowercase normalized email.
3. Enrichment list containing businesses with no email plus contacts whose verifier status is not `good`.

A contact with an email from `leadsEnrichment` is not automatically verified. Match it against verifier output.

## Cost lesson

Capture `usageTotalUsd` from each selected run. Sum scrape runs and verifier runs separately. Be explicit that verifier spend is the cost of verification runs/submitted records, not necessarily the cost divided by the count of good emails.

## Operational pitfalls

- Fetch all dataset pages; sample pages are only for schema discovery.
- Avoid using a broad all-runs sum when the user asked for two specific lists.
- Verify output counts after deduplication and state the deduplication key.
- Never expose the Apify token in files, logs, or the final response.
