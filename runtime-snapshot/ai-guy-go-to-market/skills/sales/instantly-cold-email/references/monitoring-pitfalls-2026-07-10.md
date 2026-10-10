# Monitoring Pitfalls — July 10, 2026 Session

## `leads messages` top-level `from`/`to` are STRINGS

The response structure is:
```json
{"from": "operator@domain.com", "to": "lead@company.com", "history": [...]}
```
These are bare email strings, NOT `{"name": "...", "email": "..."}` dicts. Using `.get()` on them raises `AttributeError`. Use directly as strings.

## Regex Classification Ordering

Patterns like `\binterested\b` WILL match inside "not interested" if checked first. This causes "not interested" replies to classify as `positive_interested`.

**Fix:** Always run negative/hostile/OOO/anti-spam patterns BEFORE positive interest patterns:
```python
# 1. Check OOO
# 2. Check anti-spam challenges
# 3. Check hostile
# 4. Check unsubscribe
# 5. Check negative (not interested, no thanks, no thx, not a fit, etc.)
# 6. Only THEN check positive interest patterns
```

The key ordering: `\bnot interested\b` must be tested BEFORE `\binterested\b`.

## New Operator Domains (AI Guy Coaching #3607306)

These domains belong to operators sending from campaign #3607306 and should be in the OUR_DOMAINS filter list:
- `hireaiintegraterz.com` (Mary)
- `tryaiintegraterz.com` (Johnathan)

Full operator domain list as of July 10, 2026:
```python
OUR_DOMAINS = [
    'speakeragent.ai', 'progressdeskks.info', 'successcrestco.info', 'growthmapar.info',
    'horizonedgenv.info', 'joinaiintegraterz.com', 'useaiintegraterz.com',
    'strategyvistaaz.info', 'advanceaxisnm.info', 'meetaiintegraterz.com',
    'riseedgecs.info', 'peakstrategymail.info',
    'hireaiintegraterz.com', 'tryaiintegraterz.com',  # AI Guy coaching (#3607306)
]
```

## Verified Operator Handling (July 9, 2026)

All 24 inbox entries from today were already in state and handled:
- **Pam "Sure"** → Mary replied (hireaiintegraterz.com) with $10/hr offer + "When works?"
- **Steve Kayser "Could you send info"** → Ella replied (growthmapar.info) with Calendly + Tony CC
- **nsconsultingli "Yes, how can we connect?"** → Victoria replied (successliftia.info) with Calendly
- **Mike "Yes"** → operator handled
- Remaining: negatives ("not interested", "no thanks"), OOO, anti-spam challenges, hostile
