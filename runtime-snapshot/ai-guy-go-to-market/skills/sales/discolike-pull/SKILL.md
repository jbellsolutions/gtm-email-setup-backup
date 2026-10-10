---
name: discolike-pull
description: Pull a real lead list from DiscoLike. Use ONLY when the user explicitly says "pull the list", "run the discover", or similar after they've validated. This is the only skill that triggers paid_per_record MCP calls (discover-similar-companies, search-contacts). MUST use clarify() to get user approval before any paid call — Hermes' equivalent of the Claude Code PreToolUse hook.
---

# DiscoLike — Pull

The paid path. Everything else is design; this is the spend. Treat it accordingly.

## Pre-flight

Before the pull:
1. Confirm the user has a saved `query_id`.
2. Confirm they've validated (or have a reason to skip — "I just want 50 records to eyeball" is fine).
3. Read `account-status` and `usage-statistics` (both FREE) to confirm plan tier supports the pull size and to record current spend.
4. **Default `max_records` to 50** if the user hasn't specified one. That's $0.15 — a confirming sample, not a campaign.

## Gate the paid call

Before calling `discover-similar-companies` or `search-contacts`, use `clarify()`:

> "Ready to pull. This will call discover-similar-companies for N records at ~$3/1000 records. Estimated cost: ~$X.XX. Proceed?"

The user approves or denies. If they deny → stop. Don't retry, don't reduce max_records and try again. They said no.

## Company pull (discover-similar-companies)

If approved:
```
mcp__discolike__discover-similar-companies
  query_id: <id>          # or inline filters from saved query
  max_records: <n>
```

Results contain: domain, name, country, state, employee_range, digital_footprint, social_urls, description, industry_groups.

Save output: `/opt/data/discolike-output/<query_id>-<YYYYMMDD-HHMMSS>.csv`

Auto-chain into `discolike-post-pull` with the output path.

## Contact pull (search-contacts)

If the user wants contacts (not just company domains), use `search-contacts`:
```
mcp__discolike__search-contacts
  inclusion_query_id: <id>
  seniority: "vp"
  department: "Marketing"
  has_email: true
  email_validated: true
  max_records: 50
```

Contact-finder is smart about WHERE to look:
- B2B SaaS → Crunchbase + LinkedIn
- Influencers → social platforms
- Lawyers → bar association
- General businesses → company website + LinkedIn

Same gating, same approval flow. Same output path (different CSV columns).

## Don't fall back to validate

If the user asks for "just a tiny pull to see what it looks like" and you've not validated yet — don't say "let's pull 10 records to test." Say "let's run validate first, that's ~$0.30-$2, then you'll know whether the pull is worth it."

Exception: if the user has already done a walkthrough + design + validate on a similar query and just wants to expand `max_records`, the pull is reasonable.

## Why output goes to /opt/data/discolike-output/

Lead data stays on the VPS, not mixed with skills or code. Easy to find, easy to clean up.