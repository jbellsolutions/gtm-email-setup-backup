# Partner Category Campaign Launch Pipeline

End-to-end pipeline for launching partner-category cold email campaigns (fractional CFOs, coaches, CMOs, CRM consultants, etc.) via Instantly Prospector.

## When to use
- Launching cold outreach to professionals who are both potential clients AND referral partners
- Multi-niche campaign launches where each niche has its own framework document
- Any campaign where Instantly Prospector is the lead source

## Pipeline Steps (do NOT skip any)

### 1. Search (free)
```bash
Instantly prospect search --from-json /tmp/search.json --format json
```
Use string-based filter fields (not numeric IDs). See `references/prospector-fields.md` for the exact field names.
- Returns `filter_id` and `total_count` — this tells you the pool size
- Search is FREE. Run as many searches as needed to tune filters

### 2. Fetch (consumes credits)
```bash
Instantly prospect fetch --from-json /tmp/fetch.json --format json
```
JSON format: `{"filter_id": <ID>, "limit": <N>}`
- Max 10,000 per fetch. Max 100,000 per day.
- Each filter can only be fetched ONCE. If re-fetch needed, create a new search for a fresh filter_id.
- Output from fetch is hard to parse. Use `fetched-searches` to verify success instead of trying to parse fetch output.
- Check results: `Instantly prospect fetched-searches --limit 5 --format json`

### 3. Get leads (download fetched contacts)
```bash
Instantly prospect get --from-json /tmp/get.json --format json
```
JSON format: `{"filter_id": <ID>, "limit": 1000, "offset": 0}`
- Max 1,000 per page. Paginate with `offset` and check `hasMore` in response.
- Filter to verified emails: keep leads where `@` is in email AND (`verificationStatus` is `"valid"` OR (`status` is `"found"` AND `verificationStatus` is empty))

### 4. Create Instantly campaign
```
mcp_Instantly_create_campaign(name="Partner: {Niche} v1")
```

### 5. Write sequences
- Use the framework document (if provided) as the authority
- Follow `cold-email-editorial-workflow` skill for 5-stage pipeline
- **MANDATORY**: human formatting — short lines, blank lines between sections, lowercase, varied line lengths. See `cold-email-editorial-workflow` Stage 3 formatting rules.
- 4 emails: Day 0 cold → Day 3 lane pivot → Day 7 check-in → Day 14 breakup
- **SAVE VIA CLI ONLY** — `mcp_Instantly_save_campaign_sequences` is unreliable (returns 400 on valid payloads):
```bash
Instantly campaigns save-sequence --id <ID> --from-json /tmp/seq.json
```
- JSON format: `{"sequences": [...]}` NOT a bare array. Each having `seq_number`, `seq_delay_details: {delay_in_days}`, `seq_variants: [{subject, email_body, variant_label}]`

### 6. Upload leads
```bash
Instantly leads add --campaign-id <ID> --from-json /tmp/upload.json
```
- Max 1,000 leads per batch. Split larger lists.
- Format: `{"lead_list": [...], "settings": {"ignore_duplicate_leads_in_other_campaign": true}}`
- Each lead: `{first_name, last_name, email, company_name, website, linkedin_profile, custom_fields: {title, industry, sub_industry, city, state, level, company_size, company_revenue}}`
- Custom fields from Prospector map 1:1 to Instantly custom_fields

### 7. Configure settings (use CLI, not MCP)
```bash
# Plain text + ESP matching
echo '{"send_as_plain_text": true, "enable_ai_esp_matching": true, "follow_up_percentage": 100, "stop_lead_settings": "REPLY_TO_AN_EMAIL"}' > /tmp/settings.json
Instantly campaigns update-settings --id <ID> --from-json /tmp/settings.json

# Track settings off
echo '{"track_settings": ["DONT_TRACK_EMAIL_OPEN", "DONT_TRACK_LINK_CLICK"]}' > /tmp/track.json
Instantly campaigns update-settings --id <ID> --from-json /tmp/track.json
```

### 8. Attach inboxes (use MCP)
```
mcp_Instantly_add_campaign_email_accounts(campaign_id, email_account_ids=[id1, id2, ...])
```
- Assign 3-4 inboxes per campaign from DIFFERENT domains
- Only use warmed inboxes (warmup status=ACTIVE, reputation 94%+)
- Check available: `Instantly mailboxes list --format json` — filter to `campaign_count: 0`

### 9. Set schedule (use MCP)
```
mcp_Instantly_update_campaign_schedule(campaign_id, days_of_the_week=[1,2,3,4,5], start_hour="08:00", end_hour="17:00", timezone="America/New_York", max_new_leads_per_day=<N>, min_time_btw_emails=9)
```
- `max_new_leads_per_day` should match inbox capacity: ~15 per inbox

### 10. Update daemon CAMPAIGN_CONTEXT (MANDATORY — do not skip)
Edit `/opt/data/scripts/auto_reply_daemon.py` and add the new campaign ID to `CAMPAIGN_CONTEXT` dict. Include:
- What the original email was about
- Which lane(s) the campaign uses
- Key offer details for reply context
- Booking link if applicable

This is critical because without it, positive replies get mismatched drafts or are silently dropped.

### 11. Start campaign
```
mcp_Instantly_update_campaign_status(campaign_id, "START")
```
- After start, re-read settings to confirm Instantly didn't auto-adjust anything
- Verify: `Instantly campaigns get --id <ID> --format json`

## Pitfalls
- **MCP `save_campaign_sequences` is unreliable** — always use CLI
- **MCP `update_campaign_settings` for `send_as_plain_text` may not persist** — use CLI
- **`fetch` filter can only be used once** — create a new search for a fresh filter_id
- **Prospector field names are string-based, not numeric IDs** — `"0 - 25"` not `1`
- **Ampersands in sub-industry names** — use "Professional Training & Coaching" not "and"
- **Instantly auto-adjusts settings on START** — verify after starting
- **Daemon CAMPAIGN_CONTEXT is mandatory** — campaigns without it lose replies
- **Text blocks are dead emails** — format every email with short lines, blank lines, varied rhythm