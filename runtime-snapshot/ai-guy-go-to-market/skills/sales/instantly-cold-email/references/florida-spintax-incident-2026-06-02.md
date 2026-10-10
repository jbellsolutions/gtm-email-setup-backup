# Florida HVAC Spintax Incident — June 2, 2026

## Timeline
- **~17:16 UTC (1:16 PM ET)**: Campaign #3441343 (HVAC - Florida - June 2026) starts sending
- **~17:16 UTC**: First email sent to Blake (lead_id 3926041150) via inbox isabella@strategyharborne.info
- **~17:16 UTC** (9 seconds later): Auto-reply from MidAmerican Energy customer service mailbox
- **~18:36 UTC (2:36 PM ET)**: Campaign PAUSED — ~850 emails sent
- **Status**: 844 INPROGRESS, 244 STARTED, 6 BLOCKED, 3 COMPLETED

## Root Cause
`resolve_spintax()` was NOT called in `hvac_personalize.py`. The personalized email body contained raw Spintax blocks that Instantly sent as literal text:

```
{Hey|Hi|Hello} Blake, Longwood is a competitive HVAC market. 13 reviews at 4.4 stars
shows you're holding your own. But here's what's happening: your competitors' phones
are ringing because someone is actually calling their customers. Not AI. Not ads.
Not automated sequences. Real human beings makin...
```

Instantly does NOT process Spintax syntax — `{option1|option2}` is sent verbatim. Every recipient saw literal curly-brace blocks.

## Impact
- **~850 emails** sent with unreadable Spintax garbage in the body
- **Zero replies expected** — text is incomprehensible to recipients
- **1,097 emails burned** in Instantly — cannot re-upload (Instantly silently drops duplicates across campaigns)
- **Fresh leads needed** for any Florida re-launch
- **Sender reputation** may be damaged from high spam-rate (confusing emails → spam reports)

## The Fix
Add `resolve_spintax()` to `hvac_personalize.py` or any personalization script that generates Spintax:

```python
import re, random

def resolve_spintax(text):
    """Resolve {option1|option2|option3} to a single random variant."""
    def pick(match):
        options = match.group(1).split('|')
        return random.choice(options)
    return re.sub(r'\{([^}]+)\}', pick, text)

# Apply before writing to custom_fields
email_body = resolve_spintax(raw_template)
```

## Confirmed
- Sent email body via `Instantly leads messages --campaign-id 3441343 --lead-id 3926041150`
- Raw Spintax visible in the SENT message's `email_body` field
- Reply was auto-reply from `OnlineCustomerService@support.midamerican.com` — standard "your request has been received" auto-responder
