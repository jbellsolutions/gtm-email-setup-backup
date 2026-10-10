# SpeakerAgent Pipeline — Architecture Reference

Full architecture for the automated positive-reply pipeline (July 2026).

## Architecture

```
Inbox (paginated 0-180) → Filter campaign #3577260 → Fetch message history
→ Filter operator replies → Classify (inline rules, NOT scripts/classify.py)
→ Track in state file → Auto-reply (high-confidence only) → Dashboard → Slack
```

## Key Files

| File | Purpose |
|---|---|
| `/opt/data/scripts/speakeragent_pipeline.py` | Pipeline runner: paginate, classify, track, auto-reply |
| `/opt/data/scripts/speakeragent_dashboard.py` | Visualization dashboard |
| `/tmp/speakeragent_followups.json` | State file: tracks every positive through lifecycle |
| Cron `148920b114d6` | Runs pipeline + dashboard every 30 min |

## State File Structure

```json
{
  "version": 1,
  "campaign_id": 3577260,
  "last_run": "2026-07-12T11:47:00Z",
  "known_reply_message_ids": ["msg_abc123"],
  "leads": {
    "4102214369": {
      "lead_id": 4102214369,
      "first_name": "Kyle", "last_name": "Wolfe",
      "email": "kyle@kylewolfemedia.com",
      "classification": "positive_interested",
      "confidence": "high",
      "reply_text": "I'm interested",
      "detected_at": "2026-07-12T00:58:50Z",
      "status": "awaiting_followup",
      "status_history": [{"status":"new","at":"2026-07-12T00:58:50Z"}],
      "followup_sent_at": null, "followup_method": null,
      "followup_message_id": null, "notes": ""
    }
  },
  "stats": {"total_detected":1, "awaiting_followup":1, "replied":0, "booked":0, "dead":0}
}
```

## Lifecycle

- `awaiting_followup` → just detected, needs operator or auto-reply
- `replied` → auto-reply sent, waiting for response
- `booked` → meeting booked (manually set)
- `dead` → no response or backed out

## Auto-Reply Templates

**positive_interested (BOOK):**
Hey {first_name}! Awesome, glad to hear you're interested. Here is my calendar: https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery — looking forward to connecting!

**positive_soft (INFO):**
Hey {first_name}! Thanks for your interest. Check out what we do: https://aiintegraterz.com/stop-renting — and if you'd like to chat, book here: https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery

Auto-replies only fire for `high` confidence. `medium` confidence is tracked as `awaiting_followup` for manual review.

## Dedup

Uses `known_reply_message_ids` (per-message), not lead IDs. New replies from tracked leads ARE caught. Same reply IS deduplicated.

## Classification

Uses inline rules from `references/campaign-slack-push.md` with all July 2026 edge cases. OOO → Unsub → Hostile → Not fit → Not now → Bounce → Referral → POSITIVE (interested/soft) → skip.

## Running Manually

```bash
python3 /opt/data/scripts/speakeragent_pipeline.py   # full run
python3 /opt/data/scripts/speakeragent_dashboard.py  # dashboard only
python3 /opt/data/scripts/followup_engine.py          # follow-up cadence (both pipelines)
python3 /opt/data/scripts/followup_engine.py --dash   # follow-up dashboard
```

## Known Issues

- **Bot not in C0AFU5EH56X (#speakeragent-ai)** — delivers to main thread instead. Invite @Hermes.
- **Cold start** — empty state file processes everything. Seed with known positives first.
- **Inline classifier gaps** — new patterns found in sweeps. Update both campaign-slack-push.md AND pipeline `classify()` function.
