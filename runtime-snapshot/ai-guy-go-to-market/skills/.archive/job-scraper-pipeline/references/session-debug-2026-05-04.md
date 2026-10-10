# Session Debug Notes — May 4, 2026

## Pipeline Runs

### Run 1 (after config fix)
- Ingested: 875 jobs (175 Indeed + 700 LinkedIn)
- Qualified: 275 (DeepSeek scored ≥60)
- Result: 0 contacts, 0 emails — all "Hiring team"

### Run 4 (LinkedIn 502)
- LinkedIn: 502 Bad Gateway from Apify
- Indeed only: 175 jobs, 113 qualified
- Result: 0 contacts — no company_url for LinkedIn scraper

## Batch Enrichment
- 113 leads → 61 emails (54%)
- ~7 sec/company with website-email-phone-finder
- Domain guessing: strip suffixes, lowercase, remove special chars → companyname.com

## Actor Field Samples

LinkedIn scraper (JkfTWxtpgfvcRQn3p): job_id, job_title, company_name, company_url, apply_url, job_url
Indeed scraper (hMvNSpz3JnHgl5jkh): id, positionName, company, externalApplyLink
LinkedIn employees (9Qmr7CUJ3fVH6bAmC): name, link, designation — input: companyUrls NOT companies
Website email finder (mD5Xdfj9XeMS5FWPc): emails[] — input: domains — 7 sec result

## legacy email platform Auto-Reply
- CLI reply works but JSON parse error is cosmetic
- API: POST /api/v1/campaigns/:id/reply-email-thread?api_key=KEY
- Body: email_stats_id, email_body only
- Confirmed: 4 messages in James Chung thread