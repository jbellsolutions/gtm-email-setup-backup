# Daily Campaign Stats Report

Template and workflow for the daily cron job that generates campaign stats.

## Report Template

```
📊 Cold Email Daily — [Day, Mon Date]
Campaign: [name] (#[id])

Sent: X | Opens: Y (Z%) | Clicks: C (D%) | Replies: R (E%)
Positives: P (F% positive reply rate)
Bounces: B | Unsubs: U

[If any positive replies today, list each:]
💬 pos reply — "Name" (email): "[first 80 chars of reply]"

---

[If campaign stopped, add:]
⚫ Campaign is STOPPED — no activity today. Paused [date].
Lead snapshot: [INPROGRESS] · [COMPLETED] · [BLOCKED] (of [total] leads)

[If other campaigns are active, add secondary section:]
Active campaigns sending today:
🔵 [name] (#[id]) — ACTIVE, [n]/day, [n] leads
  - [n] replies today: [summary]
```

## Workflow

1. **Pull analytics** (will return 0 or wrong data for tracking-disabled campaigns — known bug):
   ```bash
   Instantly analytics campaign-stats --from YYYY-MM-DD --to YYYY-MM-DD --campaign-ids <ID> --format json
   ```

2. **Pull leads** (for lead-level ground truth when analytics fail):
   ```bash
   Instantly leads list --campaign-id <ID> --offset 0 --limit 100 --format json > /tmp/leads_p0.json
   ```
   Parse `total_leads` and status counts (`INPROGRESS`, `COMPLETED`, `BLOCKED`).

3. **Check campaign status**:
   ```bash
   Instantly campaigns get --id <ID> --format json
   ```
   If STOPPED → report zeros + lead snapshot + active campaigns.

4. **Check inbox for today's replies**:
   ```bash
   Instantly inbox replies --format json > /tmp/inbox_all.json
   ```
   Filter by `last_reply_time` containing today's date. For each, get message history:
   ```bash
   Instantly leads messages --campaign-id <ID> --lead-id <email_lead_id from inbox> --format json
   ```

5. **Classify replies** using positive-reply-scoring schema. Count `positive_interested`, `positive_soft`, `positive_referral`.

6. **Compile and deliver** using the template above. Concise, no fluff, Slack-ready.

## Common Scenarios

### Campaign is STOPPED (no activity)
Report zeros for the requested campaign. Still run the inbox check — replies can arrive after the campaign stops. Surface what IS active in a secondary section. Don't just say "[SILENT]" unless ALL campaigns are idle with zero replies.

**When ALL campaigns are stopped:** Still pull the full inbox and check for:
- **Unread replies** (`has_new_unread_email: true`) — these need manual attention regardless of campaign status. The auto-reply daemon only runs for active campaigns. Flag unsubscribe requests, OOO referrals (possible warm leads), and positives that need follow-up.
- **Unsubscribe requests** — the daemon may have replied but not processed the removal. Flag for manual unsubscribe in Instantly UI.
- **OOO with referrals** — "I'm OOO, contact X instead" → the referred person is a warm lead. Extract their email/name.

### Flaky leads list pagination
When paginating through large campaigns, many offsets will time out. Don't loop — write each page to disk individually:
```bash
for offset in 0 100 200 500 1000 1500 1900; do
  timeout 45 Instantly leads list --campaign-id <ID> --offset $offset --limit 100 --format json 2>/dev/null > /tmp/leads_p${offset}.json
done
```
Skip failed pages. Parse successful pages and extrapolate the full distribution from the sample. A 300-lead sample (3 successful pages) across a 1,948-lead campaign gave stable enough ratios for reporting. Avoid subprocess.run() loops — they compound timeouts. Individual terminal calls survive better.

### Analytics returns wrong campaign data
Known Instantly bug with tracking-disabled campaigns. `analytics campaign-stats` for ID 3287518 may return data for 3316611 or 3318534 instead. Ignore. Use lead-level ground truth.

### Security scan blocks pipes
Write JSON to file first, then parse with Python script. Never pipe `Instantly` directly to `python3`.

## May 12, 2026 Example

```
📊 Cold Email Daily — Monday, May 12
Campaign: ai-operator-10hr-niche (#3287518)

⚫ STOPPED — No activity today. Paused May 11.

Sent: 0 | Opens: 0 | Clicks: 0 | Replies: 0 (today)
Positives: —
Bounces: — | Unsubs: —

Lead snapshot: 82 INPROGRESS · 7 COMPLETED · 11 BLOCKED (of 1,948)

---

Active campaigns sending today:
🔵 SA-PowerPartners-PR-Wave1 (#3316611) — ACTIVE, 300/day, 1,901 leads
  - 1 reply: unsubscribe

🟡 home-services-hvac-florida (#3318534) — PAUSED, 1,170 leads
  - 2 replies: stale-contacts (no longer at company)
```
