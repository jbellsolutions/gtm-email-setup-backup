# Enterprise Domain Filter for Auto-Reply Detection

## Problem

The `info@` and `contactus@` exception rule (pull message history for these prefixes from small-business domains) can still waste API calls on enterprise/SaaS domains where these addresses are guaranteed auto-responders (ZenDesk, Intercom, privacy compliance bots, etc.).

## Solution

Maintain a list of enterprise/SaaS domains. When an `info@` or `contactus@` address matches an enterprise domain, classify as `auto_reply` immediately — do NOT pull message history.

```python
ENTERPRISE_DOMAINS = {
    # Health/SaaS platforms (Jul 17, 2026)
    'embermedicalservices.com', 'lumoramd.com', 'agelessrx.com', 'bluechew.com',
    'avivawoman.com', 'vyvemd.com', 'ascenvalabs.com', 'evernow.com', 'amarihealth.com',
    'regenwellnessvitamins.com', 'warriorbabehealth.com', 'hormone-zone.com', 'tmates.com',
    'teamwellcore.com', 'hellowisp.com', 'thedoc.la', 'thedoctor.me', 'keeps.com',
    'thirtymadison.com', 'gethealthy.store', 'obuhealth.com', 'biopreventative.com',
    'texascenterwellness.com', 'balto.com', 'myrnk.com', 'myconnectmed.com',
    'everydayhealth.com', 'joinelev8health.com', 'wellrevolution.com',
    'strivepharmacy.com',       # pharmacy chain — multiple inbox entries (texas@, florida@)
}

def is_enterprise_auto_reply(email):
    """Returns True if the email prefix + domain combination is a guaranteed auto-reply."""
    email_lower = email.lower()
    domain = email_lower.split('@')[-1] if '@' in email_lower else ''

    # Standard auto-reply prefixes
    AUTO_PREFIXES = ['support@', 'info@', 'privacy@', 'contact@', 'contactus@', 'hello@',
        'admin@', 'help@', 'noreply@', 'no-reply@', 'team@', 'connect@', 'ask@', 'consult@',
        'trt@', 'orders@', 'staff@', 'frontdesk@', 'care@', 'press@', 'media@', 'podcast@',
        'compliance@', 'moreinfo@', 'concierge@']

    if not any(email_lower.startswith(p) for p in AUTO_PREFIXES):
        return False  # Personal address — always check

    # info@ and contactus@ from small biz domains are the exception
    if email_lower.startswith('info@') or email_lower.startswith('contactus@'):
        if domain in ENTERPRISE_DOMAINS:
            return True   # Enterprise info@ → guaranteed auto-reply
        return False      # Small biz info@ → pull message history to verify

    # All other auto-reply prefixes → guaranteed auto-reply
    return True
```

## When to add domains

Add a domain to the enterprise list when:
- The domain is clearly a SaaS platform, pharmacy chain, or large corporate entity (not a small clinic/business)
- Multiple inbox entries appear from the same domain across different campaigns
- The reply body pattern confirms auto-responder (ticket system, privacy notice, etc.)

## Small biz exception — do NOT add these

These are small businesses using `info@` as their main inbox — they generate genuine human replies:

- `everwellusa.com` — "Sure" (positive reply from TRT clinic)
- `bellobella.com` — "Sure, but also some info on your company please" (weight loss clinic)
- `scaledownweightloss.com` — "Sure feel free to send it" (weight loss clinic)

**Rule of thumb:** If you can't tell from the domain alone whether it's a big company or a small business, pull message history. Only add to the enterprise list after confirming auto-reply behavior.
