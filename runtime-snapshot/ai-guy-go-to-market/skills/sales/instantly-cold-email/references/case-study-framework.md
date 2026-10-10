# Case Study Framework

Repeatable workflow for generating cold email performance case studies from Instantly data.

## When to Use

- Weekly campaign performance reviews
- Sales collateral / proof-of-performance documents
- Client reporting

## Data Pipeline

### Step 1: List Active Campaigns

```bash
export PATH=/opt/data/home/.local/bin:$PATH
export Instantly_API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2)
Instantly campaigns list --format json
```

Filter to campaigns active in the target date range.

### Step 2: Pull Analytics by Date Range

For each campaign, use the Instantly API (not CLI — analytics endpoint returns sent/reply/bounce counts by date range):

```
GET /api/v1/campaigns/{campaign_id}/analytics?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

Key fields: `sent_count`, `unique_sent_count`, `reply_count`, `bounce_count`, `unsubscribed_count`.

Also pull all-time totals with the non-date-filtered analytics endpoint.

### Step 3: Pull Inbox Replies

The CLI is the primary method (API inbox endpoint can return empty):

```bash
Instantly inbox replies --offset 0 --limit 20 --format json
```

Paginate until empty data array (typically 10-15 pages covers all active inbox entries).

Filter by `last_reply_time` to the target date range.

### Step 4: Fetch Message History

For each reply, get the actual reply body:

```bash
Instantly leads messages --campaign-id {cid} --lead-id {email_lead_id} --format json
```

**Use `email_lead_id`** from inbox, NOT `email_lead_map_id`. Rate limit: 0.3-0.5s between calls.

### Step 5: Classify Replies

Use the inline classification rules from `positive-reply-scoring` skill. The `scripts/classify.py` has ~30% error rate — for case studies where every positive counts, use inline rules.

Key classification categories:
- `positive_interested` — booking calls, "yes let's talk"
- `positive_soft` — info requests, pricing inquiries
- `positive_referral` — "not me but talk to X"
- `neutral_question`, `negative_notfit`, `negative_notnow`, `negative_hostile`
- `unsubscribe`, `ooo`, `bounce`

### Step 6: Compute Rates

```
reply_rate = replies / sent
positive_rate = (interested + soft + referral) / sent
bounce_rate = bounces / sent
```

## Case Study Structure

The format that works (validated July 2026):

### Executive Summary
One paragraph. Total sends, total replies, reply rate, number of buyer signals. State clearly: all cold email.

### Campaign Performance Table
Side-by-side comparison of all campaigns in the date range. Columns: Campaign, Audience, Sent, Replies, Reply %, Bounces, Bounce %, Unsubscribes, Sequences.

### The Story
What the numbers mean. Cross-vertical comparison if applicable.

### Reply Quality
Classification breakdown table + direct quotes from every positive reply. Include lead name and company.

### Campaign Architecture
The stack and methodology that produced these results.

### Key Takeaways
5 bullet points for sales conversations. Each one is a selling point backed by data.

### What We're Selling
The pitch paragraph — ready to use in sales calls.

## CRITICAL: Campaign Type Framing

**All campaigns are cold email.** There is no "warm audience" in this system. The naming conventions:

- **"SpeakerAgent" campaigns** — cold outreach to PR agencies
- **"Owned Audiences" campaigns** — cold outreach from owned/proprietary lead lists (still cold, NOT warm)
- **"In-House AI Guy" campaigns** — cold outreach to coaching businesses

Do NOT frame any campaign as "warm" in case studies. "Owned Audiences" refers to list ownership, not audience warmth.

## PDF Publishing

```bash
cd /opt/data/case-studies
pandoc {file}.md --pdf-engine=weasyprint \
  --metadata title="Title" \
  --metadata author="AI Integraterz" \
  -V colorlinks=true -V linkcolor=blue \
  -o {file}.pdf

cd /opt/data/skills/here-now
./scripts/publish.sh /opt/data/case-studies/{file}.pdf \
  --title "Title" --client hermes
```

## Pitfalls

- **API inbox returns empty** — use CLI `Instantly inbox replies` instead
- **`email_lead_id` vs `email_lead_map_id`** — use the former for `leads messages`
- **Rate limit Instantly** — 0.3-0.5s between calls, some will still fail; classify what you get
- **Don't miscategorize Owned Audiences as warm** — they're cold
- **The `Instantly-cold-email` skill SKILL.md is at 100KB and can't be patched** — use this reference file instead