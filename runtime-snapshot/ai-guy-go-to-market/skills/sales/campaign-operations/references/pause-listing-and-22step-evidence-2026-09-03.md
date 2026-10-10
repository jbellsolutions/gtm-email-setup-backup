# Verified Instantly evidence: pause, campaign listing, 22-step structure (2026-09-03)

Live-verified during the GYMS Connect Med One pause and the Fitness Affiliate Program draft build.
All shapes below were exercised against the production workspace on 2026-09-03.

## Pause evidence pattern

```
POST /api/v2/campaigns/{id}/pause        -> HTTP 200, body may be empty
GET  /api/v2/campaigns/{id}              -> {"status": 2, ...}          # 2 = Paused
GET  /api/v2/campaigns/{id}/sending-status ->
{"summary": {"status": "campaign_paused",
             "status_message": "Campaign is paused",
             "issue_started_at": null,
             "last_healthy_send_at": "2026-09-03T13:11:00.002Z",
             "ai_summary": null}}
```

A pause HTTP 200 alone is not evidence. Assert `status == 2` on re-fetch AND
`summary.status == "campaign_paused"` before reporting a campaign as paused.
Verified across a ten-campaign pause batch (all ten returned both markers).

## Campaign listing pagination

- `GET /campaigns?limit=100` caps at 100 items. A large workspace silently hides
  campaigns beyond page one (observed: 10 target campaigns present, only 6 returned).
- Paginate with a query parameter: `GET /campaigns?limit=100&starting_after=<cursor>`,
  following `next_starting_after` until it is absent.
- `POST /campaigns/list` is NOT a route (404 `Route POST:/api/v2/campaigns/list not found`).
- Always assert the expected count of targeted campaigns after listing
  (e.g. `len(gym_campaigns) == 10`), never proceed on a partial page.

## Name-matching gotcha

Campaign names contain a literal `|` (e.g. `GYMS Connect Med One | Framework 1`).
In `re.fullmatch(r'...\| Framework ...')` the pipe must be escaped; an unescaped
`|` alternation silently matches fewer/more names and cost one debug cycle here.

## 22-step framework-sequence creation (verified payload)

Structure policy: ten framework emails + ten follow-ups + two closers, one campaign.
Verified creation via `POST /api/v2/campaigns`:

```python
steps = []
for i in range(1, 23):
    subject = f'{{{{email_{i}_subject}}}}' if i % 2 else ''   # odd = new thread, even = reply in thread
    steps.append({'type': 'email', 'delay': 0 if i == 1 else 3, 'delay_unit': 'days',
                  'pre_delay_unit': 'days',
                  'variants': [{'subject': subject,
                                'body': f'<div>{{{{email_{i}_body}}}}</div>',
                                'v_disabled': False}]})
payload = {'name': 'Fitness Affiliate Program', 'sequences': [{'steps': steps}],
           'campaign_schedule': {'schedules': [{'name': 'Weekdays',
             'timing': {'from': '08:00', 'to': '17:00'},
             'days': {'0': True, '1': True, '2': True, '3': True, '4': True, '5': False, '6': False},
             'timezone': 'America/Detroit'}]},
           'text_only': True, 'first_email_text_only': True,
           'daily_limit': 1000, 'daily_max_leads': 1000,
           'stop_on_reply': True, 'stop_on_auto_reply': False,
           'open_tracking': False, 'link_tracking': False,
           'email_list': <sorted account emails>, 'email_tag_list': [],
           'insert_unsubscribe_header': True, 'prioritize_new_leads': True}
```

Post-create: `POST /campaigns/{id}/pause`, re-fetch, assert status 2 and
`campaign_paused`. Verified returned `status: 2`, `email_list_count: 100`,
`daily_limit: 1000`, `sequence_steps: 22`. Leads carry `email_1_subject` ...
`email_22_body` as per-lead custom variables (stored under `payload`).

## Research-corpus reuse (2026-09-03 evidence)

Same 7,825-lead union re-supplied for a new framework. Prior build's research
corpus (`gyms_research.jsonl`, one homepage fetch per lead) matched the
reconstructed union 7825/7825 with zero missing and zero extra, so no re-fetch
of the full list was needed. Re-crawl targets were only 1,693 leads:
1,113 previously unreachable + 580 thin pages (<350 chars of text).
Per-lead fact extraction then classifies each lead individually: vertical,
one verifiable detail, and offer-track flags (~50 leads whose own site already
advertises peptide/GLP-1 services switch that lead to the grow-track variant).
