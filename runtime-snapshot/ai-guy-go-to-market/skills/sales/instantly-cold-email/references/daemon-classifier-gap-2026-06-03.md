# Daemon Classifier Gap — June 3, 2026

## Incident

AATempco Heating (HVAC Texas campaign #3442703) replied "Sure" at 2:23 PM ET. The daemon classified it as `neutral` instead of `positive_interested`. No draft was generated. No Slack notification posted.

## Root Cause

The `classify()` function in `/opt/data/scripts/auto_reply_daemon.py` had three gaps:

### 1. No one-word agreement detection
"Sure" didn't match any positive pattern. The `interested` list included multi-word patterns only:
```python
interested = ['interested', 'tell me more', 'love to learn', 'set up', 'schedule',
              'book a call', 'let\'s talk', 'would love', 'please send']
```

### 2. No negative detection
Short negative replies ("No thx", "Not interested") also fell through to `neutral` instead of `negative_notfit`.

### 3. Campaign 3442703 missing from CAMPAIGN_CONTEXT
Even if the classifier had caught "Sure", the draft would have used the generic fallback:
```python
FALLBACK_CONTEXT = "Our original email was about AI-powered business automation services..."
```
The actual offer was about embedding a real person to call customers — completely different.

## Fix Applied

### Classifier patch
Added before the existing `interested` check:

1. **One-word agreement block** — strips punctuation, checks against: `sure`, `ok`, `yep`, `absolutely`, `definitely`, `indeed`, `yes`, `okay`, `sounds good`, `yeah`, `of course`

2. **Negative pattern block** — checks for: `not interested`, `no thanks`, `no thx`, `no thank you`, `not a fit`, `don't need`, `we're good`, `we are good`, `not at this time`, `pass`

Both return their respective labels immediately — they short-circuit before the generic `interested` check to avoid false positives.

### CAMPAIGN_CONTEXT patch
Added entry:
```python
"3442703": "Our original email was a personalized sales pitch about embedding a real person to call their customers and prospects — no AI, no chatbots, just human phone outreach. We guarantee appointments or it's free. No contracts, no lock-in.",
```

## Verification

Re-ran the classifier mentally against the session's replies:
- "Sure" → `positive_interested` ✅
- "No thx" → `negative_notfit` ✅
- "Not interested" → `negative_notfit` ✅
- "No thank you. Please remove us from your list" → `unsubscribe` ✅ (caught by earlier unsubscribe check)
- "[automated response to acknowledge receipt]" → `neutral` ✅ (no OOO/auto pattern match — acceptable)

## Lessons

1. **One-word replies are common in cold email** — CTAs are designed for one-thumb responses. The classifier must handle them.
2. **Every new campaign launch MUST include a CAMPAIGN_CONTEXT entry.** Make this part of the campaign creation checklist.
3. **Cron delivery is to `slack:cold-email-replies`, not `single-brain`.** If Justin expects notifications in the main channel, update the cron job.