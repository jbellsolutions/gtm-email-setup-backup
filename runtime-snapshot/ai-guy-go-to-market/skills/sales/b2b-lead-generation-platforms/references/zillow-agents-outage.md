# Zillow Agents Outage — June 2, 2026

## Summary

The Zillow Agents scraper (`/api/v1/scrape/zillow-agents`) is returning HTTP 500 `{"error":"Launch failed"}` for all submissions. This is a server-side issue — other scrapers on the same account work fine.

## Reproduction

All of these fail identically:

```bash
scrapercity zillow-agents -l "Miami, FL"
scrapercity zillow-agents -l "Orlando, FL"
scrapercity zillow-agents -l "Denver, CO"
scrapercity zillow-agents -l "Tampa, FL" --limit 5
scrapercity zillow-agents -l "Tampa, FL" --specialty "agent"
scrapercity zillow-agents -l "Tampa, FL" --language "en"
```

Direct API (Python, Node.js) — same 500 result:
```json
{"error": "Launch failed"}
```

## What Works

- `scrapercity wallet` — ✅ (auth is fine)
- `scrapercity email-validate test@example.com` — ✅ (submits, returns runId)
- `scrapercity maps -q "plumbers" -l "Miami, FL"` — ✅ (submits, returns runId)

## What's Also Broken

- `scrapercity yelp -q "plumbers" -l "Miami, FL"` — ❌ same 500 "Launch failed"

## Pre-Existing Zillow Run

A Zillow run was submitted earlier on June 2, 2026 (before the outage?):
```
run_id: DseG5RKAxd6Fyv3hy
description: "FLORIDA - 1002"
status: SUCCEEDED
handled: 0
requested: 500
runTimeSecs: 6.289
```

The scraper ran for only **6 seconds** and processed **0 results**. The outputUrl (`/api/downloads/DseG5RKAxd6Fyv3hy`) returns HTTP 502 — likely because there's nothing to download.

## Ongoing Yelp Run

A Yelp run submitted before the outage is still running:
```
run_id: TBAAoHMGvnJRM807s
status: RUNNING
statusMessage: "Crawled 178/1258 pages, 0 failed requests, desired concurrency 7."
requested: 12200
```

This covers ~110 Florida cities for "AIR CONDITIONING, HVAC" and should complete successfully since it was submitted before the endpoint went down.

## Account Status

- Plan: Growth ($149/cycle)
- Balance: $113.60
- Key: 90c2ca64
- Auth works, credits available, not a 402/403/429 issue

## Resolution

This is a ScraperCity server-side issue. Contact support or wait for the endpoint to recover. Google Maps scraper can be used as a fallback for real estate agent queries.
