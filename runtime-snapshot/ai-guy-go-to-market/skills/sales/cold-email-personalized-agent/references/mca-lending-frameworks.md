# MCA / Business Lending — Cold Email Frameworks

10 pain-point frameworks for DialDesk outreach to MCA shops, business lenders, and alternative lending companies. Each framework targets a specific operational pain.

**Vertical:** MCA / Business Lending / Alternative Lending  
**Offer:** DialDesk — trained appointment setters + SMS + email campaigns  
**Word count:** 50–100 words per email  
**Tone:** Plain text, lowercase subject, human voice, no marketing speak

## MCA-Specific Language

**Use:** apps, submissions, aged data, UCC records, trigger leads, funded deals, advances, positions, renewals, stacking, closers, setters, floor, pipeline, dial sessions, live transfers, app volume

**Never use:** innovative, cutting-edge, revolutionary, synergy, leverage, solution, platform, ecosystem, disrupt

## The 10 Frameworks

### #1: Empty Seats
**Signal:** Hiring ads, careers page, "join our team", job postings  
**Angle:** Can't keep phone seats filled — revolving door of setters

### #2: Aged Data Graveyard  
**Signal:** Large operation, mentions data/UCC/triggers, established shop  
**Angle:** Thousands of aged leads untouched — money sitting in a spreadsheet

### #3: Can't Send Texts Anymore
**Signal:** No SMS mention, small-medium shop, tech-forward but no texting  
**Angle:** SMS is broken for lending shops — numbers get flagged, carriers crack down

### #4: App Volume Is Through the Roof
**Signal:** Growing market, active online, multiple products  
**Angle:** App volume surging, not enough seats to keep up

### #5: Closers Are Cold Calling
**Signal:** "Closers", "live transfers", opener-closer model on website  
**Angle:** Closers spending time dialing cold data instead of closing

### #6: The Revolving Door
**Signal:** Multiple job postings up for weeks, Glassdoor turnover signals  
**Angle:** Hire, train, lose, repeat — the #1 killer in MCA call floors

### #7: Email Going to Spam
**Signal:** Small operation, no email marketing visible, simple website  
**Angle:** Email campaigns end up in spam — no warmup, no metering

### #8: Someone Else Funds Them First
**Signal:** Speed-focused language, competitive market, "fast funding"  
**Angle:** First call wins — short-staffed shops lose deals to faster competitors

### #9: Dialer Bills Eating Your Margin
**Signal:** Large floor, high volume mentions, "dialer" keywords  
**Angle:** Per-minute dialer costs crushing margins on 500+ dials/day

### #10: Renewals Are Walking Out the Door
**Signal:** Established 2+ years, "renewal" language, funded client base  
**Angle:** Funded clients ready for renewal — but nobody's calling them

## Framework Selection Logic (Programmatic)

For scripted batch generation, keyword-matching against website text:

| Keywords Found | Framework |
|---|---|
| careers, hiring, join our team, open positions, job openings | #1 Empty Seats |
| UCC, aged lead, trigger lead, mailing list, aged data | #2 Aged Data |
| SMS, text message, texting, text blast, bulk text, sms campaign | #3 SMS Broken |
| closer, setters, live transfer, warm transfer, appointment setter | #5 Closers Cold Calling |
| same day, within hours, 24 hour, instant, rapid funding, minutes | #8 Speed Kills |
| dialer, power dialer, predictive dialer, auto dialer | #9 Dialer Bills |
| renewal, renewals, repeat business, refinancing, second position | #10 Renewals |
| No signals, small site (<300 chars) | #7 Email Spam (fallback) |
| No signals, medium+ site | #4 App Volume (default) |

## Scripted Batch Generation

The reusable script at `scripts/mca_email_generator.py` implements:
1. Curl each website (8s timeout, 5000 char text extraction)
2. Keyword-match for framework selection
3. Template-fill with per-lead variables (first_name, company, lending_type, location, risk_reversal)
4. Filter out consumer lending, non-US domains, private equity
5. Output Instantly-ready JSON and CSV

**Pitfalls encountered (June 2026):**
- Multi-email semicolons in ListKit CSVs: emails like `avigail@freedombf.com; chaim@freedombf.com` come as one field — split before upload
- First names from email local parts need cleaning: `mmarkowitz` → Mark, `brianroe` → Brian, `customerservice` → "there"
- Location extraction from website text often returns garbage — validate city,ST format before using
- ScraperCity cancelled (negative balance) — ListKit enrichment is fallback but less reliable

## Risk Reversal Options (rotate per lead)

1. "If the appointments don't come in, you don't owe us anything. Simple as that."
2. "We guarantee someone is on your phones every single day, managed and monitored. If we don't deliver, we keep going until we do."
3. "No long-term contracts. 90 days, and if it's not working, you walk."
4. "We replace anyone who leaves or underperforms — that's on us, not you."
5. "If we can't get your SMS actually delivered within the first two weeks, we keep working at no charge until we do."

## Hard Rules

- 50–100 words, plain text, no HTML
- No mention of cost, pricing, fees
- Never use "pay," "price," "cost," or "investment"
- Lowercase subject lines, 1–4 words
- No URLs in email body
- End with a question, never a pitch
- Every email must have one specific detail from research
- 8th grade reading level