# Instantly Daemon — Classification & Pagination Fixes (2026-08-12)

## The incident

The 08:30 UTC cron run found only 4 replies and misclassified two of them:

| Reply | Address | What the daemon said | What it actually was | Root cause |
|-------|---------|---------------------|---------------------|------------|
| #1 | misa@creativeinfosd.com | `neutral` | **positive** — "The partner-referral approach you described is interesting, especially as we continue expanding Creative Info SD…" | Classifier had no patterns for interested-but-not-asking style replies |
| #3 | megan@ducksinrows.com | `positive_interested` (+ DRAFT) | **OOO** — "I am OOO today with limited internet access. I will be slow to respond but will get back to you as soon as possible." | "get back to you" fooled classifier; no OOO patterns for "limited internet access" or "slow to respond" |
| All missing | Several inbox entries | Never seen | **Pagination stopped early** | `len(items) < 100` short-circuit dropped pages |

## Classification fixes applied to `instantly_reply_daemon.py`

### Missing OOO patterns (caused false positive drafts)

```python
# ADDED to ooo_patterns list:
'ooo', 'o.o.o'
'limited internet access'
'limited access to email'
'limited access to my email'
'limited bandwidth'
'currently out'
'slow to respond'
'will be slow to respond'
```

These catch:
- "I am OOO today with limited internet access" → OOO (was positive)
- "I'm currently OOO with limited access to email" → OOO
- "I'm travelling with limited bandwidth" → OOO
- "Hello! I am currently out" → OOO (was falling through to neutral)

### Missing positive-interest patterns (caused missed positives)

```python
# ADDED to interested list:
'approach you described is interesting'
'approach is interesting'
'especially as we continue'
```

These catch replies like "The partner-referral approach you described is interesting, especially as we continue expanding…" — the person is expressing genuine interest but not using trigger words like "tell me more" or "send it."

### Employee-departure notices classified as dead

```python
# NEW check before OOO detection:
if ('no longer a' in body_lower and ('employee' in body_lower or 'employed' in body_lower)) or 'automated reply' in body_lower:
    return 'dead'
```

Catches "The person you are trying to contact is no longer a Salem Electric employee" (was slipping through as neutral, wasting a state slot).

## Pagination fix

### Old (broken) code:
```python
if not next_cursor or len(items) < 100:
    break
```

Instantly returns pages with fewer than 100 items while a real `next_starting_after` cursor still exists. The daemon saw a 4-item page, called it done, and silently dropped everything after.

### New code:
```python
# Do not use page length as an end condition. Instantly can return a
# short page while another cursor page still exists; the cursor is the
# authoritative pagination signal.
if not next_cursor:
    break
```

Also bumped `max_pages` from 3 to 10. The accounts fetch has the same fix.

## Composio / Draft file removal

- Removed `DRAFT_FILE` writes (`/tmp/instantly_reply_drafts.json`) — drafts now print inline so the Hermes cron agent delivers them natively
- Cron job `5ff7af7572e2` updated: `deliver: slack:C0B02TY6R1T` via native Hermes, prompt explicitly bans Composio/MCP posting

## Verification

Post-fix daemon run found 12 inbound replies (vs. 4 before), correctly classified all four new ones including Ryan's genuine positive "I am interested in hearing more about this" which the old pagination would have missed entirely.
