---
name: instantly-deliverability-audit
description: "Diagnostic audit for Instantly cold email deliverability. Checks domain auth (SPF/DKIM/DMARC), inbox health/reputation from Instantly's accounts endpoint, bounce rates, and 1% rule compliance. Use when Instantly reply rates drop, bounces spike, or as weekly/monthly health check. Trigger on 'instantly deliverability audit', 'check instantly domain health', 'instantly inbox health'. Mirrors email-deliverability-audit's legacy email platform workflow."
version: 1.0.0
source: Adapted from GrowthEngineX coldoutboundskills; forked from email-deliverability-audit for Instantly
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

### 0. Pre-Flight: Verify Instantly API Is Alive

**Do this FIRST.** If the API is down, every subsequent step will fail silently and the audit is a waste of time — same lesson `email-deliverability-audit` learned the hard way on legacy email platform (see that skill for a real multi-day-outage incident and the false-all-clear failure mode).

```bash
curl -s -o /dev/null -w "%{http_code}" "https://api.instantly.ai/api/v2/campaigns" \
  -H "Authorization: Bearer $INSTANTLY_API_KEY"
```

200 → proceed. 401/403 → key invalid/revoked, stop and log the outage rather than silently reporting an empty audit. Instantly's specific failure-mode response bodies are unverified (unlike legacy email platform's documented `"Plan expired!"` vs `"Invalid API Key"` distinction) — until observed, treat any non-200 as "cannot pull data."

**When API is down:** Still write the audit report to Obsidian. Note the outage and carry forward the last known state from the previous audit file. Do NOT go `[SILENT]` — the operator needs to know the API is down.

### 1. Pull Inbox Inventory

```bash
curl -s "https://api.instantly.ai/api/v2/accounts" -H "Authorization: Bearer $INSTANTLY_API_KEY"
```

Check per-mailbox: warmup status, reputation, blocked status, daily sends — exact field names unverified until a real account with connected mailboxes is inspected (currently 0 connected).

### 2. Check Domain Authentication

For each sending domain, verify SPF, DKIM, and DMARC.

**No Instantly domain-health endpoint has been verified.** legacy email platform's `analytics domain-health` (see `email-deliverability-audit`) has no confirmed Instantly equivalent — check `GET /accounts` for domain-auth fields when a real account is inspected. Until then, use DNS directly:

Use the bundled `scripts/dns_check.py` which checks SPF, DKIM (both `default` and `google` selectors), and DMARC across any domain list. It validates that SPF records actually contain `v=spf1` (not just any TXT record) and flags mismatches automatically.

```bash
python3 scripts/dns_check.py domain1.info domain2.info ...
```

Check: SPF must include sending service, DKIM must return a record, DMARC policy should be `p=none`, `p=quarantine`, or `p=reject`.

**DKIM selector pitfall:** Google Workspace uses the `google` selector, not `default`. If `default._domainkey.{domain}` returns MISSING, also check `google._domainkey.{domain}` — that's where Google-hosted domains keep their DKIM key. `default` is the generic convention (used by MS365, self-hosted, etc.) but not by Google.

### 3. Pull Campaign Metrics

```bash
curl -s "https://api.instantly.ai/api/v2/campaigns/analytics" -H "Authorization: Bearer $INSTANTLY_API_KEY"
```

Whether this returns per-campaign or aggregate data, and whether it has the same "returns 0 when tracking is disabled" bug legacy email platform's analytics endpoints have (see `instantly-cold-email`), is unverified — no campaign has sent yet. If it proves unreliable, fall back to lead/message-level ground truth the same way the legacy email platform skill does.

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
| Bounce >3% | Re-verify lead list with Reacher (`verify-leads` skill). Discard all `invalid` emails — PipelineLabs "verified" status is cosmetic and 40-50% are actually invalid. |
| Listed but 0 opens | Likely spam folder — run spam placement test. Note: opens will always show 0 when tracking is disabled — this row only applies to campaigns with tracking enabled. |
| OK opens, no replies | Copy issue — run `instantly-reply-scoring` + rewrite |
| OK everything but still fails | Domain reputation — consider domain age, replace IP pool |
| All campaigns STOPPED with residual inbox | Pull `GET /emails` anyway — stopped campaigns can still get replies from previously sent emails. Check for unread items and positive replies that need attention. |
| **Instantly API down** | **Cannot run audit.** Write report noting the outage. Carry forward last known state from previous audit file. Flag P0: Justin must restore API access. Do NOT go SILENT. |

## Pitfalls

**Portable (DNS-check pitfalls, apply regardless of sending platform):**
- **Cloudflare DoH returns ALL TXT records in its Answer array** — the bundled `scripts/dns_check.py` correctly iterates all answers for SPF (finding the one containing `v=spf1`). When writing ad-hoc DNS checks, don't take `answers[0]` blindly for SPF queries — domains with `google-site-verification` + SPF will have the wrong record at index 0.
- **Google Workspace DKIM is at `google._domainkey.{domain}`**, not `default._domainkey.{domain}`. Always check both selectors before reporting DKIM as MISSING.
- **Security scanner blocks heredocs** (`python3 << 'EOF'`) — write DNS check scripts to a standalone `.py` file first, then execute.

**Instantly-specific: none recorded yet.** No mailboxes are connected and no audit has run against live Instantly data. `email-deliverability-audit`'s legacy email platform-specific pitfalls (mailbox-list JSON parsing quirks, campaign-count field unreliability, stale cron campaign IDs, the "Authentication failed" vs "Invalid API Key" vs "Plan expired" distinction) were all learned from real production API responses — none of it can be assumed to transfer. Add entries here as they're actually discovered.

## What to Do Next

**All clean:** log it, close. **Issues found:** load `deliverability-incident-response` for triage playbook.
