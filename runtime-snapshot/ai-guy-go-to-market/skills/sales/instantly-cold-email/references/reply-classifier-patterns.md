# Reply Classifier Patterns

Complete classifier patterns for cold email reply monitoring — used by both the auto-reply daemon and manual inbox monitoring cron jobs.

## Our Outbound Domains (Filter Out)

When extracting replies from `leads messages`, filter out replies FROM our own sending domains. The `from_email` field is often empty in REPLY-type messages, so check the `message_id` header instead:

```python
OUR_DOMAINS = [
    'speakeragent.ai',
    'strategyvistaaz.info', 'advanceaxisnm.info',
    'growthsignalmn.info', 'horizonlineva.info',
    'prosperpointok.info', 'prosperstepms.info',
    'useaiintegraterz.com', 'joinaiintegraterz.com',
    'meetaiintegraterz.com',  # AI Guy coaching (#3607306)
    'hireaiintegraterz.com',  # AI Guy coaching — Mary (#3607306)
    'tryaiintegraterz.com',   # AI Guy coaching — Johnathan (#3607306)
    'strategypointil.info',   # Coaching Owned Audiences (#3617053) — Arianna
    'elevatedeskin.info',     # Coaching Owned Audiences (#3617053) — Anna
    'growthpathut.info',      # Coaching Owned Audiences (#3617053) — Grace
    'scaledeskct.info',       # Coaching Owned Audiences (#3617053) — Penelope
    'elevateaxisca.info',     # Coaching Owned Audiences (#3617053) — Kaylee
    'prosperaxisma.info',     # Coaching Owned Audiences (#3617053) — Aaliyah
    'progressaxismd.info',    # Coaching Owned Audiences (#3617053) — Skylar
    'successcrestco.info',    # Coaching Owned Audiences (#3617053) — Willow
    'prosperliftwi.info',     # Coaching Owned Audiences (#3617053) — Bella
    'strategyvistaaz.info',   # Coaching Owned Audiences (#3617053) — Gabriella
    'prospervistaoh.info',    # Coaching Owned Audiences (#3617053) — Lydia
    'horizonstepfl.info',     # Coaching Owned Audiences (#3617053) — Julia
    'growthmapar.info',       # Coaching Owned Audiences (#3617053) — Mila
    'horizonvistaky.info',    # Coaching Owned Audiences (#3617053) — Natalie
    'progressdeskks.info',    # Coaching Owned Audiences (#3617053) — Madeline
    'growthliftaz.info',      # Coaching Owned Audiences (#3617053) — Bella
    'progressvistasc.info',   # Coaching Owned Audiences (#3617053) — Penelope
    'growthliftwa.info',      # Coaching Owned Audiences (#3617053) — Emilia
    'advancelineor.info',    # PR Agencies v2 (#3577260) — Eleanor
    'advanceaxisnm.info',    # Legacy SpeakerAgent
]

def is_our_reply(msg):
    msg_id = msg.get('message_id', '')
    return any(d in msg_id for d in OUR_DOMAINS)
```

## Classification Tiers

**⚠️ CRITICAL: Regex pattern ordering matters.** Patterns like `\binterested\b` WILL match inside "not interested" if checked before the negative tier. The word "interested" appears in both "not interested" (negative) and "I'm interested" (positive).

**Always run tiers in this order:**
1. `auto_reply` (ticket system / helpdesk boilerplate)
2. `anti_spam_challenge` (BoxTrapper / cPanel challenge-response)
3. `ooo` (out of office)
4. `bounce` (mailer-daemon)
5. `hostile`
6. `unsubscribe`
7. `negative_notfit` (must check BEFORE positive — `\bnot interested\b` before `\binterested\b`)
8. `positive_interested`
9. `positive_soft`
10. `neutral` (everything else)

**Verified July 9, 2026:** When positive patterns were checked first, "not interested" (hello@remotedigitalmedia.online), "not interested in receiving referrals" (cary@carycarrcox.com), and "no thanks" (NMarshall@marshallpr.com) all misclassified as `positive_interested`. After reordering to run negative checks first, all three correctly classified as `negative_notfit`.

### positive_interested (needs immediate operator attention)
- One-word agreements: "Sure", "OK", "Okay", "Yep", "Yes", "Absolutely", "Definitely", "Indeed", "Certainly", "Interested"
- "Sounds good", "Sounds great"
- Body is essentially just the agreement word (stripped of punctuation/signatures)
- **"Tell me more"** — concise, high-intent. Often includes contact info in signature (name, phone, title). Treat as positive_interested.
- **Booking link in signature** — "Feel free to book an appointment with the link in my signature I open to hearing what you do" → positive_interested. They're inviting a meeting.
- **Direct question about offering** — "Who is [company]?" when replying to the cold email → positive_interested. They read it and want context.

### positive_soft (needs operator attention, may convert)
- "tell me more", "send me more", "send more info", "more information"
- "interested in learning", "would love to learn", "would like to learn"
- "want to know more", "let's talk", "let's chat", "set up a call"
- "schedule a call", "book a call", "when can we", "how does it work"
- "how does this work", "what's the catch", "what is the cost"
- "pricing", "price", "cost", "demo", "case study", "case studies"
- "example", "examples", "walk me through", "send me info"
- "send info", "send me information", "please send", "send it over"
- "let me know when", "let me know when you're available", "when are you available"  # Jul 17: "Sure… let me know when you're available" (Jodi, #3577260) was missed
- "would be great", "love to hear", "talk further", "connect"
- "learn more", "more details", "how to get started"
- "i'm interested", "i am interested", "we're interested", "we are interested"

⚠️ AUTO-REPLY PRE-CHECK (run BEFORE positive_soft matching): Many ticket-system and helpdesk auto-replies contain positive-leaning boilerplate like "look forward to connecting" or "happy to help" — these are NOT genuine interest. Check for auto-reply markers FIRST, and if any match, classify as `auto_reply` regardless of positive-leaning phrases downstream:

```python
AUTO_REPLY_MARKERS = [
    r'we have received your (request|message|email)',
    r'thank you for (reaching out|contacting|your email|your message|getting in touch)',
    r'we will (respond|get back|reply|review)',
    r'we.ll (respond|get back|reply)',
    r'your (request|message|email) has been received',
    r'we appreciate your (patience|interest)',
    r'a member of our team',
    r'one of our (team|representatives|agents)',
    r'thanks for (contacting|reaching out|your message)',
    r'we look forward to (connecting|speaking|hearing)',
    r'please note that',
    r'we.ve received your',
    r'this is an automated',
    r'auto.{0,10}(reply|generated|response)',
]
# If body matches any AUTO_REPLY_MARKER within first ~300 chars → auto_reply (not positive_soft)
```

⚠️ MUST check for negative prefixes before classifying as positive:
```python
neg_precede = ['not ' + pat, 'no ' + pat]
if any(np in body_lower for np in neg_precede):
    return "negative_notfit"  # not "positive_soft"
```

⚠️ MUST check unsubscribe patterns BEFORE positive_soft — "please remove us from this list" should never hit positive_soft because it contains "please" near "let's connect". Check unsubscribe tier first.

### hostile
- "fuck", "f***", "shit", "junk", "spam", "garbage", "slop"
- "delete this", "piss off", "screw off", "get lost"
- "harassment", "how dare you", "who the hell", "what the hell"
- "are you kidding", "nonsense", "scam"
- "psycho"
- **"clearly written by AI"** — auto-rejection of AI-generated cold email. The person detected the email was AI-written and rejects on that basis alone. Classify as hostile — there is no recovering this lead. (July 13, #3617053: julianne@juliannekanzaki.com)
- **Bare "Stop"** — unique pattern from mobile clients (Outlook for iOS, Apple Mail). Body may be "Stop", "Stop\nGet Outlook for iOS", "Stop\nSent from my iPhone", etc. Check: `body_lower.startswith('stop')` AND `len(body_lower.split()) <= 3` (short body where first word is "stop"). The bare `body.strip()=='stop'` check is too narrow — mobile clients append signatures.
- **"BUSINESS SOLD - STOP MAIL"** — the "stop" inside a multi-word body triggered the single-word positive check because the word count includes the pasted original email. Extract just the reply part (before "On ... wrote:" or "-----Original Message-----") before classifying.

### negative_notfit
- "not interested", "not a fit", "not the right fit", "no thanks", "no, thank you"
- "no thank you", "no thx", "pass", "not for us", "not for me"
- "don't need", "do not need", "already have", "we're good"
- "not looking"
- "not currently looking", "not in the market", "not right now", "please don't"
- "must decline", "decline", "but I must decline"
- "stop emailing", "stop sending", "stop contacting"
- "don't own", "do not own", "i don't own a", "i do not own a"
- "wrong person", "wrong email", "not a [business type]"
- **"no interested"** — typo of "not interested" (missing 't'). Same intent. Classify as negative_notfit.
- **"no [positive word]"** — when body starts with "no" followed by a positive-leaning word ("no interested", "no thanks"), check negative patterns FIRST before positive. "No interested" should not hit the one-word positive check on "interested".

### unsubscribe
- "unsubscribe", "opt out", "opt-out", "remove from list"
- "remove from your list", "un sub", "unsub", "remove us from"
- "remove me from", "take me off", "take us off", "please remove"
- "remove from this list", "removed from this list"
- "please remove us", "please remove me"  # catch before "please" hits positive_soft

⚠️ Check unsubscribe BEFORE positive/negative — someone saying "unsubscribe" is not also "not interested."

### anti_spam_challenge (automated challenge-response)
**Pattern:** "The message you sent requires that you verify that you are a real live human being and not a spam source. To complete this verification, simply reply to this message and leave the subject line intact or click the link below"

Generated by BoxTrapper, SpamAssassin with challenge-response, or cPanel mail filters. These are AUTOMATED — not human replies. **Do NOT notify the operator.** Add to state silently.

**Detection:** `'verify that you are a real live human'` in body OR `'challenge-response'` OR `'bxd.cgi'` in body (the cPanel BoxTrapper verification link). Classify as `anti_spam_challenge` — treat same as `auto_reply` (add to state, no notification).

**Scale:** 4/40 inbox entries on July 9, 2026 (10% rate). 3/20 on July 10, 2026 (15% rate) on campaign #3617053. Common on shared hosting mail servers (Bluehost, HostGator, cPanel-based hosts). These are NOT deliverability failures — they just mean the recipient's server uses challenge-response filtering. The email still got through their system.

**Detection code:**
```python
ANTI_SPAM_MARKERS = [
    r'verify that you are a real live human',
    r'verify that you are a real human',
    r'bxd\\.cgi',  # cPanel BoxTrapper
    r'challenge.response',
    r'spam source',
    r'complete this verification',
]
# If any marker matches → anti_spam_challenge (add to state, skip notification)
```

### ooo (out of office / auto-reply)
**Correct catches:**
- "out of office", "out-of-office", "ooo", "on vacation", "on maternity"
- "annual leave", "holiday", "away from the office", "autoreply", "auto-reply"
- "auto reply", "automated response", "automatic reply", "away from my desk"
- "no longer with", "no longer at", "no longer employed", "left the company"
- "moved on from", "transitioned", "stepping away"
- **Discovered July 7:** "I am out of the office [Thu/Fri]", "currently out of the office... returning [date]", "I will reply to your email as soon as I can", "out of the office starting [date]", "I'm away on vacation, returning [date]", "I am away from my email... back [date]"

**False positive risks:**
- "I hope you had a wonderful vacation! Just wanted to follow up on the guest idea I sent before you were away." — Contains "vacation" AND "away" but is a human following up about a podcast booking, NOT an out-of-office. **Narrow OOO detection:** require an explicit "I am"/"I'm" subject reference in the first sentence, e.g. `re.search(r'(?i)^[^.!?]{0,80}\b(i am|i\'m)\b.*\b(out of|away|vacation|ooo|returning)\b', body)`. Without a first-person subject within the first ~80 chars, don't classify as OOO.

### neutral
Everything else. Includes:
- Threading artifacts (replies to wrong thread)
- Content-less replies
- Replies that don't match any pattern
- **Monitor these** — a "neutral" that looks human-written might be a misclassified positive

## Common Misclassifications (History)

| Date | Reply | Wrong Class | Correct Class | Root Cause |
|---|---|---|---|---|
| Jun 3 | "Sure" | neutral | positive_interested | One-word agreement not in patterns |
| Jun 3 | "No thx" | neutral | negative_notfit | Short negative not in patterns |
| Jun 24 | "Hi, send more info please" | neutral | positive_soft | "send more info" not in patterns, daemon marked as processed without replying |
| Jul 1 | "Ok. Send me to information including cost please." | neutral | positive_soft | "send [me] information" + "cost" not caught (2nd occurrence of same gap) |
| Jul 7 | "Stop" (bare, Outlook iOS) | neutral | hostile | "Stop" alone not caught; only "stop now"/"stop emailing" matched |
| Jul 7 | "I am out of the office Thursday and Friday" | neutral | ooo | "out of the office" not in OOO patterns |
| Jul 7 | "currently out of the office... returning July 12" | neutral | ooo | "currently out of the office" not in patterns |
| Jul 7 | "I will reply to your email as soon as I can" | neutral | ooo | Auto-reply phrasing not in patterns |
| Jul 7 | "I hope you had a wonderful vacation! Just wanted to follow up on the guest idea..." | ooo | neutral | False positive: "vacation" proximity to "away" triggered OOO on non-OOO threaded reply |
| Jul 7 | "Hello Audrey We have received your request. We are reviewing your request and we will get back to you as soon as possible." | positive_soft | auto_reply | Freshdesk ticket auto-reply with "we will get back to you" boilerplate. Classified as positive_soft because "look forward to" / positive-leaning phrases triggered before the auto-reply check. Fix: auto-reply pre-check MUST run before positive_soft matching. Any body matching "we have received your (request|message)" within first ~300 chars → auto_reply. |
| Jul 7 | "Hello and thank you for reaching out to 88 Dragons. We will respond to your note as soon as possible and we look forward to connecting!" | positive_soft | auto_reply | Standard "thank you for reaching out" + "we will respond" helpdesk boilerplate. "look forward to connecting" triggered positive_soft. Same fix: auto-reply pre-check first. |
| Jul 7 | "please remove us from this list" | positive_soft | unsubscribe | Pattern `remove\s+(?:me|from)` didn't match "remove us" — the "us" falls between "remove" and "from". Fix: add `remove\s+(?:us|me)` or broader `please remove` as first-line catch |
| Jul 7 | "Stop\nGet Outlook for iOS" | positive_soft | hostile | Bare "Stop" check `body.strip()=='stop'` failed because Outlook iOS appends "Get Outlook for iOS" — result was "Stop Get Outlook for iOS". Fix: `body_lower.startswith('stop')` AND body word count ≤3 |
| Jul 7 | "Tell me more" (Ethan, Campfire Group) | not classified | positive_interested | Short, high-intent. Added to patterns. |
| Jul 7 | "Feel free to book an appointment with the link in my signature I open to hearing what you do" | not classified | positive_interested | Booking link invitation = they want to talk. Added to patterns. |
| Jul 7 | "no interested" (Howard, hlstrategy.com) | positive_interested | negative_notfit | Typo of "not interested" (missing 't'). "no" prefix matched one-word positive check first. Fix: check "no" + word combos for negative intent before one-word positive check. |
| Jul 9 | "not interested" x3 (remotedigitalmedia, carycarrcox, marshallpr) | positive_interested | negative_notfit | Regex ordering: \binterested\b matched before \bnot interested\b. Fix: run neg before pos. |
| Jul 9 | anti-spam challenge-response x4 (theformeytouch, etc.) | negative_notfit | anti_spam_challenge | BoxTrapper/cPanel. Added anti_spam_challenge tier + silent state handling. 10% rate on shared hosting. |
| Jul 9 | `leads messages` top-level `from`/`to` treated as dicts | AttributeError | — | `from`/`to` are bare strings, not `{name, email}` dicts. Documented in monitoring-pitfalls-2026-07-10.md. |
| Jul 10 | "I don't own medical practice. Please stop contacting me" (Chris, #3617053) | positive_interested | negative_notfit | "me" and "contact" keywords matched positive patterns. Short negation ("I don't own [X]") with "stop contacting" at end. Fix: check for "stop contacting", "don't own", "wrong person", "not a [business type]" before positive matching. |
| Jul 13 | "I am not currently looking for assistance" (Ppavey, #3617053) | positive_interested | negative_notfit | "looking" + "interested" in "assistance" triggered positive match. Fix: neg check BEFORE positive. Same root cause as Jul 9 (ordering). |
| Jul 13 | "No, thank you. Have a great week!" (Meghan, #3617053) | positive_interested | negative_notfit | "no, thank you" is a polite negative but "thank" matched positive patterns. Fix: "no, thank you" in negative_notfit. |
| Jul 13 | "Thanks for thinking of me. But I must decline." (Mike, #3617053) | positive_interested | negative_notfit | "thanks" + polite phrasing masked "decline." Fix: check "must decline" / "decline" as negative. |
| Jul 13 | "No interest" (Jared, #3617053) | positive_interested | negative_notfit | "interest" substring match. Fix: "no interest" → negative_notfit (was already in patterns but ordering meant positive hit first). |
| Jul 13 | "No thanks" (Drd, #3617053) | positive_interested | negative_notfit | Same ordering bug as Jul 9. "no thanks" already in patterns but positive check ran first. |
| Jul 13 | "This was clearly written by AI" (Julianne, #3617053) | not classified | hostile | Not in patterns. Added "clearly written by AI" to hostile tier. |
| Jul 17 | "Sure… let me know when you're available" (Jodi, #3577260) | neutral | positive_interested | "Sure" opened but 4+ words bypassed one-word check. "Let me know when" / "let me know when you're available" not in positive_soft patterns. Bare "sure" caught by one-word override but multi-word "Sure + booking request" falls through. Add "let me know when you're available" and "let me know when" to positive_soft. |
| Jul 17 | "sure" (Ethan/Spark, #3577260) — deep-funnel close | positive_interested | same ✅ | One-word override correctly caught lowercase "sure" after $1,500–$3,000/mo pricing given. 13-message, 16-day thread. Campaign #3577260 COMPLETED, not in CAMPAIGN_CONTEXT — monitoring sweep was the only safety net. Sat 3+ hours unhandled at `our_replies_after=0`. |

## High-Risk Sender Patterns

- **`info@` addresses** — 100% unsubscribe/hostile on PR campaign #3577260 (July 7, 2026: 3/3 unsubscribes). Shared inbox = no individual decision maker. Other generic prefixes to watch: `media@`, `press@`, `podcast@`, `admin@`, `hello@`, `help@`, `support@`, `contact@`.
- **`help@` / `support@` addresses** — 100% auto-reply/ticket-system on PR campaign #3577260 (July 7, 2026). These are helpdesk inboxes (Freshdesk, Zendesk, etc.) that auto-generate ticket acknowledgments. Never a human reply. Do not waste API calls fetching message history for these — classify as `auto_reply` from the email address alone.
- **`info@` / `hello@` / `contact@` at scale** — July 7, 2026 PR campaign audit: 20+ auto-responders from these address types classified as `positive_interested`/`positive_soft`. Common template: "Thank you for your interest! We will respond within 24 hours", "We have received your email and our team will try our best to answer within 24 hours", "Thank you for reaching out to us! We will get back to you", "Hello there! Thank you so much for reaching out to [Company] — we look forward to connecting soon!" **All false positives.** The classifier's auto-reply pre-check catches most but the pipeline can still misclassify at scale. When processing PR campaign replies, expect 40-50% auto-responders from `info@`/`hello@`/`contact@` addresses. Pre-filter by address domain before fetching message history to avoid wasting API calls.
- **`contact@` addresses** — high hostile/unsub rate. OutsidePR (contact@outsidepr.com) replied hostile "slop" on PR campaign #3577260.
- **Journalist titles** — "I am a journalist" replies from mis-targeted leads. The PipelineLabs keyword search for PR agencies catches journalists at PR-adjacent companies. Pattern to detect: "journalist", "reporter", "editor" in title or reply body.