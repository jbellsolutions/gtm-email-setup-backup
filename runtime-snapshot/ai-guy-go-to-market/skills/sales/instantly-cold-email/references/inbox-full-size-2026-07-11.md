# Instantly Inbox Full-Size Audit — July 11, 2026

Full inbox scan: **287 entries across 15 pages (0-280)**. Page 300 = empty.

## Page distribution

| Pages | Entries | Campaigns | Date Range |
|---|---|---|---|
| 0-200 | 220 | Active/recent (3617053, 3607306, 3577260, 3442703, etc.) | July 2026 |
| 220-280 | 67 | STOPPED legacy only | March 25 – May 15, 2026 |

## Legacy campaigns on pages 220-280 (uncatalogued until July 11)

| Campaign | ID | Entries | Date Range |
|---|---|---|---|
| SpeakerAgent PR Legacy | 3337105 | 7 | May 15, 2026 |
| SpeakerAgent v1 Legacy | 3316611 | 7 | May 11-13, 2026 |
| HVAC Florida STOPPED | 3318534 | 2 | May 12, 2026 |
| ai-operator-10hr-niche STOPPED | 3287518 | 7 | May 7-8, 2026 |
| Med-spa (unknown campaign) | 3287517 | 1 | May 6, 2026 |
| recruiters-power-partner-A STOPPED | 3249954 | 17 | Apr 30 – May 5, 2026 |
| recruiters-direct-value-A STOPPED | 3249956 | 2 | Apr 29-30, 2026 |
| Various legacy | 3103959, 3103961 | 8 | Mar 31 – Apr 30, 2026 |
| Earliest campaigns | 3080680, 3085916, 3085917, 3080532 | 16 | Mar 25-27, 2026 |

**Oldest entry:** March 25, 2026 (Justin's test sends to himself, campaign 3080532).

## State file impact

All 67 entries added to `/tmp/owned_audiences_state.json` on July 11. Total state now tracks 19 campaigns with 290 processed IDs.

## Monitoring implications

- **Full sweeps must paginate to at least page 280** — not 160 as previously documented.
- **15 API calls** for metadata collection (pages 0-280 in steps of 20).
- The inbox accumulates EVERY reply ever received across ALL campaigns. It does not expire entries.
- Periodic full-sweeps (weekly) prevent the state file from drifting. Each sweep catches the next un-catalogued block.
