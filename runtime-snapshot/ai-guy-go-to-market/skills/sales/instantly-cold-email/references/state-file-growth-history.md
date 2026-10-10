# State File Growth History

Tracking the auto_reply_state.json growth across monitoring runs. This file exists because the SKILL.md hit the 100K character limit and the state-file-audit pitfall can no longer fit inline.

## Current State (as of July 13, 2026 ~7PM ET)
- 351 replied message IDs
- 27 hostile senders
- 21 unsubscribers

## Growth Timeline

| Date | Replied IDs | Hostile | Unsubs | Delta | Event |
|---|---|---|---|---|---|
| Pre-July 7 | ~95 | ~15 | ~15 | — | Baseline |
| July 7 | 150 | ~20 | ~18 | +55 | Deep audit: 55 missed from PR launch burst + TX HVAC |
| July 8 | 169 | ~22 | ~19 | +19 | Auto-responders (4) + legacy deep-scan (15) |
| July 10 | ~200 | ~22 | ~19 | +31 | Campaign #3617053 launch — first replies |
| July 13 AM | ~320 | 23 | 21 | +120 | Bulk of #3617053 replies classified |
| July 13 PM | 351 | 27 | 21 | +31 | 19 auto-replies + 4 hostile + 3 rescued positives + 4 PR campaign |

## Key Finding: Both Monitors Have the Same Failure Mode

The Instantly daemon (1-minute cron) and the owned-audiences monitor (30-minute cron) both suffer from:
1. **Page-0-only scanning** during launch bursts — replies on pages 1+ get missed
2. **Classification bugs** that silently drop positives (positive-before-negative ordering — fixed July 13)
3. **No staleness retry** — a reply seen but not acted on stays that way forever

### July 13 Remediation: 3 Rescued Positives
Campaign #3617053 deep scan found 3 positive replies from July 9-10 that sat unhandled for 3-4 days:
- Jared Callahan (MONALI Health) — "Yes, I would be interested. Send it over"
- Wendy (The Sensible Woman) — "Send over your information"
- Robyn Kenney (Mindfulness Athletics) — "Yes please send it over"

All three received case study replies + custom plans. See `owned-audiences-email-reply` skill → `references/monitoring-workflow.md` for the rescue workflow.

## Recommended Cadence

- **Daily**: Quick sweep (page 0 only) for today's replies — the normal cron
- **Weekly**: Full remediation audit (pages 0-3, all message histories, classify manually)
- **After any launch burst**: Run within 48 hours
- **If daemon is quiet but inbox shows activity**: Run immediately