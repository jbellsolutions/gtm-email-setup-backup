---
name: email-deliverability-audit
description: "Diagnostic audit for cold email deliverability. Checks domain auth (SPF/DKIM/DMARC), inbox health/reputation from legacy email platform, bounce rates, and 1% rule compliance. Use when reply rates drop, bounces spike, or as weekly/monthly health check. Trigger on 'deliverability audit', 'check domain health', 'inbox health', 'why are replies dropping', 'bounce rate check'."
version: 1.0.0
source: Adapted from GrowthEngineX coldoutboundskills
---

# Email Deliverability Audit

**If your positive reply rate is dropping and you don't know why, start here.**

## The 1% Rule

A healthy domain must have ≥1% overall reply rate after 200 emails sent.

Below 1% after 200+ sends = red flag. Possible causes:
- Emails landing in spam (run spam placement test)
- Domain reputation damaged
- Copy is broken (run `spam-word-checker`)
- List is wrong ICP (bounce rate >3% = list problem)
- Inbox hasn't warmed enough

Below 200 sends: too early to judge.

## When to Run

- Reply rate dropped >30% week-over-week
- Bounces spiked above 2%
- Before scaling a campaign
- Monthly as routine hygiene (Monday task in weekly rhythm)

## Audit Steps

### 0. Pre-Flight: Verify legacy email platform API Is Alive

**Do this FIRST.** If the API is down, every subsequent step will fail silently and the audit is a waste of time.

```bash
# Read the real key — .env may have a placeholder while config.yaml has the actual key
legacy email platform_API_KEY=$(grep legacy email platform_API_KEY /opt/data/.env | head -1 | cut -d= -f2)
# Quick health probe
curl -s "https://server.legacy email platform/api/v1/campaigns?api_key=${legacy email platform_API_KEY}" | head -c 200
```

**Failure modes and what to do:**

| Response | Meaning | Action |
|---|---|---|
| JSON array of campaigns | API is up | Proceed with audit |
| `{"message":"Plan expired!"}` | legacy email platform plan expired | Log audit noting outage. Justin must renew plan at app.legacy email platform. **Cannot pull any data.** |
| `{"message":"Invalid API Key"}` | Key revoked/rotated/expired | Log audit noting outage. Justin must generate fresh key at `app.legacy email platform → Settings → API`, update BOTH `/opt/data/.env` AND `/opt/data/config.yaml` (`mcp_servers.legacy email platform.env.legacy email platform_API_KEY`), then `/restart` gateway. **Cannot pull any data.** |
| `Error: Authentication failed` (CLI) | Same as Invalid API Key | Same recovery — check REST response to distinguish from plan expiry |

**Key location pitfall:** The `.env` file may contain a truncated/placeholder key (e.g. `6c5132...d7z9`) while the real key lives in `/opt/data/config.yaml` under `mcp_servers.legacy email platform.env.legacy email platform_API_KEY`. If `.env` key fails, check config.yaml. Always verify key length (should be ~44 chars for legacy email platform).

**When API is down:** Still write the audit report to Obsidian. Note the outage, the failure mode, how many days it's been ongoing, and carry forward the last known state from the previous audit file. Do NOT go `[SILENT]` — the operator needs to know the API is down and for how long. Include the recovery steps as P0 action items.

**Also check:** the cron job's configured campaign IDs may reference retired/deleted campaigns that return no data even when the API is healthy. Cross-reference with `legacy email platform campaigns list` output. If the cron prompt hardcodes stale IDs, note this as an action item to update the cron configuration.

### 1. Pull Inbox Inventory

**CLI (preferred — works without MCP):**
```bash
legacy email platform mailboxes list --format json
```

**MCP (if legacy email platform MCP server is active):**
```
mcp_legacy email platform_list_email_accounts()
```

Check per-inbox: warmup status, reputation, blocked status, daily sends.

### 2. Check Domain Authentication

For each sending domain, verify SPF, DKIM, and DMARC.

**Primary approach — legacy email platform domain health API:**
```bash
legacy email platform analytics domain-health --from YYYY-MM-DD --to YYYY-MM-DD --format json
```

**Fallback — Cloudflare DoH (when `dig`/`nslookup` unavailable):**

Use the bundled `scripts/dns_check.py` which checks SPF, DKIM (both `default` and `google` selectors), and DMARC across any domain list. It validates that SPF records actually contain `v=spf1` (not just any TXT record) and flags mismatches automatically.

```bash
python3 scripts/dns_check.py domain1.info domain2.info ...
```

Check: SPF must include sending service, DKIM must return a record, DMARC policy should be `p=none`, `p=quarantine`, or `p=reject`.

**DKIM selector pitfall:** Google Workspace uses the `google` selector, not `default`. If `default._domainkey.{domain}` returns MISSING, also check `google._domainkey.{domain}` — that's where Google-hosted domains keep their DKIM key. `default` is the generic convention (used by MS365, self-hosted, etc.) but not by Google.

### 3. Pull Campaign Metrics

**CLI (preferred — single call for all campaigns):**
```bash
legacy email platform analytics campaign-stats --from YYYY-MM-DD --to YYYY-MM-DD --campaign-ids <ID1>,<ID2> --format json
```

Also pull overall stats:
```bash
legacy email platform analytics overall --from YYYY-MM-DD --to YYYY-MM-DD --format json
```

**MCP (per-campaign):**
```
mcp_legacy email platform_get_campaign_analytics_by_date(campaign_id, start, end)
```

### 4. Flag Violations

- Any campaign with <1% reply rate AND ≥200 sends → **1% rule violation**
- Any inbox with bounce rate >3% → **high bounce**
- Any inbox with warmup blocked → **warmup failure**
- Any domain missing SPF or DKIM → **auth gap**

### 5. Generate Report

Output to Obsidian: `domains/cold-email/audits/deliverability-YYYY-MM-DD.md`

Format:
```
## Deliverability Audit — YYYY-MM-DD

### 1% Rule Check
| Campaign | Sent (7d) | Reply Rate | Status |
|---|---|---|---|
| recruiters-power-partner-A | X | Y% | ✅/⚠/🔴 |

### Inbox Health
| Email | Domain | Reputation | Daily Sends | Status |
|---|---|---|---|
| ... | ... | ... | ... | ✅/⚠/🔴 |

### Action Items
- [ ] Fix SPF on domain X
- [ ] Pause campaign Y (bounce >3%)
- [ ] Retire inbox Z (blocked warmup)
```

## Triage Decision Tree

| Symptom | Action |
|---|---|
| 1% rule failed | Run spam placement test + spam-word-checker on copy |
| Bounce >3% | Re-verify lead list with ScraperCity (see `legacy email platform-cold-email` skill). Discard all `invalid` emails — PipelineLabs "verified" status is cosmetic and 40-50% are actually invalid. **Do NOT use Anymail Finder** (deprecated, out of credits). |
| Listed but 0 opens | Likely spam folder — run spam placement test. Note: opens will always show 0 when tracking is disabled (DONT_TRACK_EMAIL_OPEN) — this row only applies to campaigns with tracking enabled. |
| OK opens, no replies | Copy issue — run `positive-reply-scoring` + rewrite |
| OK everything but still fails | Domain reputation — consider domain age, replace IP pool |
| All campaigns STOPPED with residual inbox | Pull `legacy email platform inbox replies` anyway — stopped campaigns still get replies from previously sent emails. Check for unread items and positive replies that need attention. |
| **legacy email platform API down (Invalid API Key / Plan expired)** | **Cannot run audit.** Write report noting the outage, failure mode, and days outstanding. Carry forward last known state from previous audit file. Flag P0: Justin must restore API access. Do NOT go SILENT — operator needs visibility on the outage. |

## Pitfalls

- **Cloudflare DoH returns ALL TXT records in its Answer array** — the bundled `scripts/dns_check.py` correctly iterates all answers for SPF (finding the one containing `v=spf1`). When writing ad-hoc DNS checks, don't take `answers[0]` blindly for SPF queries — domains with `google-site-verification` + SPF will have the wrong record at index 0.
- **`legacy email platform analytics domain-health` often returns empty data** — the API endpoint is unreliable. Always have the DNS fallback ready. See `scripts/dns_check.py` for a reusable DNS checker.
- **Google Workspace DKIM is at `google._domainkey.{domain}`**, not `default._domainkey.{domain}`. Always check both selectors before reporting DKIM as MISSING.
- **Security scanner blocks heredocs** (`python3 << 'EOF'`) — write DNS check scripts to a standalone `.py` file first, then execute.
- **legacy email platform `mailboxes list` output includes warning lines at the top** — skip them when parsing JSON: read until the first `[` character, then parse from there.
- **`mailboxes list` shows `campaign_count: 0` even for connected mailboxes** — the mailbox-level API doesn't track campaign attachments reliably. To count inboxes per campaign, use the campaign-specific endpoint: `GET /api/v1/campaigns/{id}/email-accounts?api_key=KEY`. This returns the full list of connected email accounts with accurate daily_sent_count and warmup data.
- **`legacy email platform analytics campaign-stats` returns data ONLY for campaigns that sent in the window** — stopped campaigns and campaigns with no activity in the date range are silently omitted from the response. Don't interpret their absence as an error.
- **legacy email platform API key invalidation looks like "Authentication failed" in CLI** — the CLI reports `Error: Authentication failed. Check your API key.` which is indistinguishable from a wrong key. The REST API gives the real signal: `{"message":"Invalid API Key"}` (key revoked) vs `{"message":"Plan expired!"}` (plan lapsed). Always curl the REST endpoint directly to determine the actual failure mode. This outage can persist for days/weeks if the operator doesn't act — see `references/legacy email platform-api-outage-log.md` in the `owned-audiences-email-reply` skill for a real-world 5+ day outage example.
- **Cron job campaign IDs go stale** — the cron prompt may hardcode campaign IDs (e.g. `3249954, 3249956`) that are later retired/deleted. These return no data even when the API is healthy. Always cross-reference with `legacy email platform campaigns list` and flag stale IDs as an action item to update the cron configuration.

## What to Do Next

**All clean:** log it, close. **Issues found:** load `deliverability-incident-response` for triage playbook.
