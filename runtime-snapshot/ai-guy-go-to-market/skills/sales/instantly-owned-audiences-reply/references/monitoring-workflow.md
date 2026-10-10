# Monitoring Workflow — Owned Audiences Reply Cron

Step-by-step monitoring workflow for the 30-minute cron. Focus: campaign #3617053 only.

## Quick Flow (30-minute cron)

**⚠️ Pipe-to-interpreter blocked:** Security scan rejects `cat file | python3 -c` and `Instantly ... | python3 -c`. Always write JSON output to a temp file (`> /tmp/file.json`), then write a Python script to a `.py` file and run it with `python3 script.py`. Never inline Python logic in a terminal command.

```
1. Pull inbox pages 0-1 → 40 entries, 2 API calls (redirect to temp files, not pipes)
2. Filter to campaign #3617053
3. Pre-filter auto-replies by email address:
- starts with: support@, info@, privacy@, contact@, contactus@, hello@, admin@, help@, noreply@, no-reply@, team@, partnerships@, podcast@, podcasts@, media@, press@, care@, compliance@, staff@, frontdesk@, **concierge@**
- Also: connect@, ask@, consult@, trt@, orders@, notifications@, mailer-daemon@
   - These are ZenDesk tickets, CSAT surveys, privacy confirmations, OOO messages, shared inboxes
4. For remaining leads: pull message history (Instantly leads messages)
5. For each lead with REPLY-type messages:
   a. Strip HTML tags, decode HTML entities (`html.unescape()`), THEN strip quoted original email (everything after "\nOn ... wrote:" or "\n>")
   b. Classify ONLY the reply portion
   c. Check for prior handling (any SENT message after this reply's timestamp)
   d. **⚠️ Add message ID to state for ALL classifications** — not just positives. This prevents false "new lead" rediscovery on subsequent runs.
6. For unhandled positive replies: draft case study reply via skill workflow
7. For hostile/unsub: add to auto_reply_state.json hostile_senders
8. For auto-replies/OOO: add message_id to state (replied_message_ids)
```

### ⚠️ State File Hygiene (CRITICAL — Jul 14, 2026)

**After every classification, add the message ID to `known_reply_message_ids`.** The "seen it" list must grow with every lead the pipeline touches, regardless of outcome. If only positives are added, negative/hostile/auto-reply leads appear as "new" on every subsequent 30-minute cron, wasting API calls and risking re-engagement.

**Real incident (Jul 14 01:30 AM):** 4 leads appeared as "new" 4+ times across prior cron runs because their message IDs were never written to state. Each run pulled message history, classified them as negative, but didn't persist the ID — so the next run's "not in known_reply_message_ids" check flagged them as new again.

## Classification Patterns

Order matters — check negatives BEFORE positives. The most common false positives come from:
- Quoted original email text contaminating classification (especially when HTML entities like `&#x202F;` prevent quote stripping)
- HTML entities (`&#x202F;`, `&nbsp;`, `&amp;`) in quote delimiters preventing the regex from matching — always `html.unescape()` after stripping tags, before stripping quotes
- "sorry" in greeting ("Sorry, what are you suggesting?") triggering OOO
- "not" in quoted original triggering negative_notfit

### Priority order:
1. **auto_reply** — ticket systems, support requests, CSAT surveys, privacy confirmations. **⚠️ Narrow-check `thanks? (for|you).*email` — this pattern alone catches human replies like "Thank you for your email. I would love to chat with you, do you have a calendar link?" Only classify as auto_reply when the body is short (<100 chars) AND contains no human-positive signals (chat, call, calendar, schedule, interested, happy to, would love). When in doubt, let the reply fall through to neutral/positive classification.**
2. **anti_spam_challenge** — "verify that you are a real live human", BoxTrapper, bxd.cgi
3. **hostile** — "fuck", "f off", "stop emailing", "remove me", "report it", "stop" with optional punctuation (`^stop[!.]*\\s*$`, also catches "Stop!!!!", "stop."), "clearly written by AI", "ai generated", "spam", "leave me alone", "do not contact", "do not email", "creepy", "stalker", **"blacklist"** (podcast campaign: hosts who publicly blacklist AI-sourced guests — **Jul 15: Michael Krigsman cxotalk.com, #3639259**)
4. **unsubscribe** — "unsubscribe" in short body
5. **ooo** — "out of office", "vacation", "away from", "returning", "on leave", "currently out"
6. **negative_notfit** — MUST check BEFORE positive. "not interested", "no thanks", "no interest", "must decline", "not looking", "not currently looking", "please remove", "i said no", "don't need", "no thank you", **"i have retired", "i've retired", "i am retired", "i officially retired", "retired from"** (retirement announcements are NOT positive — even if they say "please send emails to..." the lead is gone)
7. **positive_interested** — "sure", "send me info", "tell me more", "would love", "book a call", "what are you suggesting", **"attached will help", "attached is", "here's my", "see attached", "media kit"** (attachment-sharing replies from podcast/media leads are warm positives — they're actively engaging by sending materials)
8. **neutral** — everything else

### Patterns that are NOT what they look like:
- "Stop!!!!" — NOT neutral. This is hostile. `^stop\\s*$` fails with exclamation marks. Use `^stop[!.]*\\s*$` to catch "Stop!!!!", "stop.", "STOP!!" etc. **July 13 PM:** Dawn (new-dawn-coaching.com) replied "Stop!!!!" — classified as `positive_interested` by prior cron (no negative/hostile pattern matched with `!!!`), got a case study reply, then never replied again. The `!!!` variant is common on iOS/Outlook mobile.
- **"Hopefully the attached will help" / attachment-sharing replies — NOT neutral.** When a lead replies with their media kit, podcast info, or company materials, they're actively engaging. The classifier has no pattern for this and defaults to `neutral`. Classify attachment-sharing replies as `positive_interested` UNLESS the body contains rejection language. **Jul 17:** Drew McLellan (Agency Management Institute, #3639259) replied "Hopefully the attached will help. Drew McLellan CEO/Partner" — classified as `neutral` but actually a warm positive. He sent his media kit and was open to a SpeakerAgent partnership. Check for: `attached will help`, `attached is`, `here's my`, `here is my`, `media kit`, `one sheet`, `see attached`.
- **"Please note that I have retired... Please send all emails to our new CFO" — NOT positive_interested.** The `\\bplease\\b.*\\bsend\\b` positive pattern catches "please send" but the context is a retirement announcement forwarding to a successor. This is `negative_notfit`. **July 16:** James (jc@kindredpartners.com, #3652624) triggered `positive_interested` via `\\bplease\\b.*\\bsend\\b` — his actual message was "I have retired from Kindred Partners... Please send all emails to our new CFO, Thomas Gang at tg@kindredpartners.com." The lead is gone. Check for retirement patterns BEFORE positive patterns.
- "Sorry Natalie, what are you suggesting?" — NOT OOO. "Sorry" as apology, not auto-reply. This is neutral/question.
- "Referrals are definitely key. Always have been." — NOT OOO. The "Lori" signature isn't an OOO marker. This is positive/neutral.
- "No interest" — NOT OOO. This is negative_notfit.
- "I am not currently looking for assistance" — NOT positive. "not currently looking" contains "looking" but is a negative. The "interested" substring inside "assistance" can also false-match. Always check negative prefix "not" before positive patterns.
- "Thanks for thinking of me. But I must decline." — NOT positive. "thanks" and polite phrasing mask the "decline." Check for "decline" as negative.
- "No, thank you. Have a great week!" — NOT positive. "No, thank you" is a polite negative. The "No" prefix must block positive matching.
- "Thank you for your email. I would love to chat with you, do you have a calendar link?" — NOT auto_reply. This is a human positive reply. The `thanks? (for|you).*email` auto-reply pattern over-catches it. **Jul 15 PM:** Isabel (tumcoeur.com, #3639259) replied with this exact pattern — classified as `auto_responder` but actually human. Check for human-positive signals (chat, call, calendar, schedule, interested, happy to, would love) before committing to auto_reply.
- "All good!" — NOT neutral when it follows a case study or follow-up. This is a polite decline (negative_notfit). Short dismissals without hostility are polite negatives — mark as dead without adding to hostile_senders. **Jul 15 PM:** Sfrontera (exclusivepr.biz, #3577260) replied "All good!" to a case study follow-up.

### ⚠️ \r\n line endings break quote extraction (Jul 20, 2026 — FIX VERIFIED Jul 21)

Instantly stores reply bodies with \r\n (CRLF) line endings from Outlook/iOS/Windows clients. The extract_reply_body() patterns use \n (LF) only and do NOT match \r\n delimiters. When the quote delimiter is not matched, the entire quoted original email contaminates classification.

**CANONICAL FIX — always normalize line endings first.** This must be the FIRST operation in extract_reply_body():
```python
def extract_reply_body(full_body):
    body = full_body.replace('\r\n', '\n').replace('\r', '\n')
    patterns = [
        r'\n>',
        r'\nOn .* wrote:', r'\nOn .* at .* wrote:',
        r'On .* at .* wrote:', r'On .*, .* wrote:',  # inline (no \n prefix)
        r'\nFrom:.*\n(?:Sent|Date):.*\nTo:',  # Outlook forward (covers both Sent: and Date:)
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            return body[:m.start()].strip()
    return body.strip()
```

**Real incident (Jul 20):** Jeff Dillon (#3617053) replied "Yes, I'd be open to see what you have" from Outlook with \r\n line endings. The un-normalized \nOn .* wrote: pattern failed to match \r\nOn. The Outlook forward footer "From: Aubrey Scott <...>\r\n Date: Thursday, July 16...\r\n To: jeff.dillon@..." also wasn't stripped. Cold email words like "already have their own" from the original message contaminated classification → false `negative_notfit`. Jeff was a strong positive — the case study was sent by a separate cron but the classifier bug would have silently killed an unhandled positive.

**Real incident (Jul 21):** Confirmed the \r\n → \n normalization fix resolves the issue. After normalization, `\nOn .* wrote:` correctly matches and `\nFrom:.*\nDate:` catches the Outlook forward variant. The `\nFrom:.*\n(?:Sent|Date):` combined pattern is now the canonical Outlook forward handler.

### ⚠️ Negative-delay false classification — `last_sent_time` reflects operator follow-up, not cold email (Jul 21, 2026)

When quickly scanning inbox entries, do NOT use `(last_reply_time - last_sent_time) < 30s` alone as an auto-responder signal. Instantly's `last_sent_time` reflects the MOST RECENT send to that lead — which is often an operator follow-up sent AFTER the lead's reply. Leads with active threads (Nicole, Jeff, Peter, Spark, Drew, Jodi, Steve — all with 5+ message histories) will show a NEGATIVE delay because the operator's follow-up was sent after the reply. The 30-second `delay <= 30` check catches all negative numbers as "instant" and falsely classifies real engaged leads as auto-responders.

**Fix:** Only apply the instant-reply heuristic when `last_sent_time` is close to `last_reply_time` AND both timestamps are within a few seconds of each other (signal of a mailer-daemon bounce or ticket-system auto-reply, not a human). For negative delays (reply before send), pull message history before deciding. Better yet: always pull message history for non-prefix leads — the `delay_sec` heuristic is a pre-filter optimization, not a classification tool.

**Leads affected in this session:** Nicole Wald (#3577260, delay=-5782s), Jeff Dillon (#3617053, -900s), Peter Vera (#3639259, -58711s), Spark (#3577260, -245199s), Drew (#3639259, -21233s), Jodi (#3577260, -858s), Steve (#3639259, -1435s). All are real engaged leads — none are auto-responders.

### ⚠️ `cal_bookings.json` format — may be a dict, not a list (Jul 21, 2026)

The `/tmp/cal_bookings.json` file at 6,972 bytes was not parseable as a list of bookings. It may be a dict with keys like `bookings` or `data`, or use a different top-level structure. When the Part B pre-call phase cannot parse the file, fall back to scanning `clients/*/pre-call-report.md` headers for today's/tomorrow's date — those are more reliable than the raw Cal.com snapshot.

**Workflow:** If `cal_bookings.json` fails to parse as a list, skip it entirely. Scan client reports + run the live Cal.com API call (`curl` with `CALCOM_API_KEY`) as documented in the `pre-call-report` skill.

One-word check requires len(body_words) <= 2. "Yes, I'd be open to see what you have" (7+ words) falls through. No positive regex matches "I'd be open to."

**Fix — first-word check BEFORE negative patterns:**
```python
first_word = body_words[0].lower().rstrip('.!?,;:')
if first_word in ('yes', 'yeah', 'yep', 'yup', 'absolutely', 'definitely', 'indeed', 'sure'):
    if not re.search(r'\b(?:not interested|decline|pass|don.t need|no thanks|remove me)\b', body_text.lower()):
        return 'positive_interested', 'first-word positive'
```

**Real incident:** Jeff Dillon — combo of \r\n quote-extraction bug + missing first-word positive pattern = false negative.

---

## 🔎 Periodic Remediation Audit — When Positives Go Stale

**The 30-minute cron is a best-effort safety net, not a guarantee.** Prior cron runs have missed positive replies that sat unhandled for 3-4 days. Run a remediation audit weekly, or whenever the daemon seems quiet while Instantly inbox shows activity.

### July 13, 2026 — Remediation: 3 Unhandled Positives (3-4 Days Stale)

Deep scan of all #3617053 message histories across pages 0-1 found **3 positive replies from July 9-10 that prior cron runs never acted on:**

| Lead | Business | Reply | Days Stale |
|---|---|---|---|
| Jared Callahan | MONALI Health (monalihealth.com) | "Yes, I would be interested. Send it over - Thanks!" | 3 |
| Wendy | The Sensible Woman (thesensiblewoman.com) | "I work mostly with women. Send over your information and let me take a look." | 3 |
| Robyn Kenney | Mindfulness Athletics (mindfulnessathletics.com) | "Yes please send it over for me to look at. Thanks," | 3 |

**Root causes (multiple):**
1. Classification order was positive-before-negative at the time these replies arrived (fixed July 13 — negative now checked first)
2. The cron's page-0-only scan may have missed them if they arrived during a burst
3. No automated retry or staleness check existed — a lead that was "seen but not acted upon" stayed that way forever

**Remediation sent:** All three received case study replies + custom plans published to here.now:
- Jared (MONALI Health): case study + plan at glacial-nebula-5hk6.here.now — sent as Bella
- Wendy (The Sensible Woman): case study + plan at clever-tundra-njjk.here.now — sent as Anna
- Robyn (Mindfulness Athletics): case study + plan at frosty-dahlia-4yak.here.now — sent as Penelope

**Note on Wendy:** Original cold email was men's-coaching-framed ("Been following your work with men"). She replied she works mostly with women. The custom plan and reply were adapted for women's health. The men's coaching case study was used with an explicit note that "the model is the same, just with different partners."

### How to Run a Remediation Audit

```bash
# Deep scan: pull ALL message histories for campaign #3617053
# Use the full inbox scan, then check every lead that has a REPLY-type message
# but NO SENT message after the reply timestamp (our_replies_after == 0)

# 1. Pull inbox pages 0-3 (80 entries)
for offset in 0 20 40 60; do
  echo '{"offset":'$offset',"limit":20}' > /tmp/iq.json
  Instantly inbox replies --from-json /tmp/iq.json --format json > /tmp/inbox_p$((offset/20)).json
done

# 2. For each lead with REPLY type AND our_replies_after == 0, check classification
# 3. For any positives: follow the full owned-audiences workflow (case study + custom plan if promised)
# 4. For any new negatives/hostiles/OOO: add to state silently
```

**Frequency:** Weekly at minimum. After any campaign launch burst, run within 48 hours. Before running: ensure the state file's hostile_senders and replied_message_ids are current to avoid re-processing.

## July 16, 2026 (6:30 PM ET) — New Campaigns #3652623 & #3652624 Launch + Peter Handled

### New Campaign Launch — Expected Auto-Responder Wave
Campaigns #3652623 (HVAC Owned Audience) and #3652624 (Recruiting & Staffing Owned Audience) launched today. First 8 hours of monitoring:
- **#3652623:** 2 real leads — Juan (OOO, returns Jul 20), Connie (OOO, limited access). Zero genuine positives.
- **#3652624:** 5 real leads — James (RETIRED — false positive from `\bplease\b.*\bsend\b` classifier bug, caught and corrected), Angela (retired), Sue (surgery recovery OOO), Eric (unsub, in hostile_senders), Jill (sabbatical OOO). Zero genuine positives.

**Pattern confirmed:** New owned-audience campaigns produce a 24-48 hour auto-responder wave identical to #3617053's July 13-14 tail. OOO messages, retirement announcements, ticket-system auto-replies, and unsub requests dominate the first day. This is NORMAL — do not interpret SILENT monitoring runs as broken.

**Key classifier fix:** `\bplease\b.*\bsend\b` catches retirement announcements where the lead says "I have retired... Please send all emails to our new CFO, Thomas Gang at tg@..." — this is NOT positive. Added retirement patterns to negative_notfit check: `\bi have retired\b`, `\bi've retired\b`, `\bi am retired\b`, `\bi officially retired\b`, `\bretired from\b`.

### #3639259 — Peter Handled
**Peter Vera** (peter@bizexitgrow.com): "Brandon, Open to receiving guests! Any business owner with an exit, or anyone with an M&A background would be a fit." — replied 4:03 PM ET, handled by monitoring sweep at 6:36 PM ET using SpeakerAgent podcaster template via Branson. Daemon missed him (#3639259 not in CAMPAIGN_CONTEXT). ~2.5 hour handling delay.

### State Update
- Daemon: 446 msg_ids, 33 hostile, 24 unsubs
- OA: 175 msg_ids, 83 leads tracked
- `concierge@` added to auto-reply prefix list (concierge@amarihealth.com was a ticket-system auto-reply on #3617053)

## July 13, 2026 (PM Run) — Classifier Bug Confirmed

### Stats
- 50 inbox entries from campaign #3617053 across pages 0-2
- 13 auto-replies filtered by email prefix (support@/info@/privacy@/contact@/hello@)
- 7 pre-filtered (hostile/unsub from prior runs)
- 30 needed message history checks
- 8 new replies TODAY (July 13), 1 from July 12 — ALL already handled by prior cron runs
- 1 new hostile added: Julianne (julianne@juliannekanzaki.com) — "clearly written by AI"

### 🚨 Classifier false positives: 5 TODAY
The classification order was positive BEFORE negative, causing:
| Lead | Actual Reply | Classified As | Got Case Study Reply |
|---|---|---|---|
| Ppavey | "I am not currently looking for assistance" | POSITIVE | ✅ Yes — at 21:12 UTC |
| Meghan | "No, thank you. Have a great week!" | POSITIVE | ✅ Yes — at 21:12 UTC |
| Mike | "Thanks for thinking of me. But I must decline." | POSITIVE | ✅ Yes — at 21:12 UTC |
| Jared | "No interest" | POSITIVE | ✅ Yes — at 21:12 UTC |
| Drd | "No thanks" | POSITIVE | ✅ Yes — at 21:12 UTC |

All 5 are second-reply landmines — people who said "no" and got marketing material anyway. Same pattern as Fran, Liz, Breathe from the skill's pitfall section who replied "remove me" / "report it" after receiving case study replies.

**Root cause:** `negative_notfit` was at position 5, `positive_interested` at position 4. "not interested" matches `\binterested\b` before the negative check runs. Fixed in this update: negative BEFORE positive (same fix as July 9 in `reply-classifier-patterns.md`).

## July 13, 2026 (PM Run #2, 8:00PM ET) — Classification Bugs + No New Positives

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- 14 auto-replies pre-filtered by email prefix (support@/info@/privacy@/contact@/hello@)
- 22 real leads needed message history checks
- 8 positive_interested — ALL already handled (`our_replies_after > 0`)
- 7 negative_notfit — all already handled
- 6 hostile (4 first-contact, 2 second-reply)
- 1 neutral — already handled

**No new unhandled positives.** System fully caught up on #3617053.

### 🚨 Two classifier bugs found (both on already-handled leads, no harm this run):

| Lead | Actual Reply | Classified As | Root Cause |
|---|---|---|---|
| Dawn RWTX | "Sure. Send me more info, please." | `negative_notfit` | `&#x202F;` HTML entity in quote delimiter prevented stripping. `\bnot\b` matched from cold email copy. Fix: `html.unescape()` after `strip_html`, before `extract_reply_body`. |
| Dawn New-Dawn | "Stop!!!!" | `positive_interested` | `^stop\s*$` didn't match with `!!!`. Fix: `^stop[!.]*\s*$` |

Both leads already had `our_replies_after > 0` so no action was needed this run, but these bugs would have caused false positives/negatives on unhandled leads.

### 6 hostiles added to state:
- **First contact:** Nicholle (colebeecoaching.com) — "stop emailing me", Fran (pureandmindful.com) — "remove me", Liz (askliz.com) — "Remove me now and do not contact again", Breathe (thewaythru.com) — "i said no. Email me again and i will report it"
- **Second reply (received case study, now hostile):** Andrea (performore.biz), Chris (nextlevelhealthwellness.com)

### Campaign #3577260 (PR Agencies):
- 1 reply: Tony (berlinmediarelations.com) — "Thank you - do you charge a fee for referrals?" — human operators handle this campaign.

## July 13, 2026 (8:30 PM ET) — Batch Cron Confirmation + 1 Hostile Second Reply

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- 14 auto-replies pre-filtered by email prefix (39% hit rate)
- 22 real leads — **ZERO unhandled owned-audiences positives**
- 1 hostile second reply: Robyn (mindfulnessathletics.com) — "I'm not interested thanks, the AI plan is super generic. Please remove me"

### Key Finding: Batch Cron Effectiveness

Prior cron run at ~5:12 PM ET sent case-study replies to all 12 leads that had replied today. The 8:30 PM run had nothing left to do — every lead already had `our_replies_after > 0`. **The batch case-study send catches everything within the same day.** The 30-minute monitoring cadence is redundant during active sending windows.

### Hostile Second Reply — Robyn K

Pattern match: second reply after case study follow-up → hostile. This is the exact pattern from the skill's pitfall section.
- July 10: Cold email → Robyn positive reply → custom plan sent
- July 13 7:40 PM: "Circling back" follow-up with case study + new custom plan
- July 13 8:11 PM: "I'm not interested thanks, the AI plan is super generic. Please remove me"
- → Added to hostile_senders + state file

## July 13, 2026 (11:30 PM ET) — Hostile Cascade Confirmed + All Caught Up

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- 14 auto-replies pre-filtered
- 15 real leads on #3617053 — **ZERO unhandled positives**
- 5 false-positive case study sends confirmed from 5:12 PM batch (Ppavey, Meghan, Mike, Jared, Drd — all said "no", all got case studies)
- 4 hostile second-replies from that wave (Nicholle "stop emailing me", Fran "remove me", Liz "Remove me now", Breathe "i will report it")
- 5 message IDs added to state (Drd + 4 hostile second-replies)
- State: 359 msg_ids, 28 hostile, 22 unsubs

### Key Finding: The Batch False-Positive Cascade Is Now Visible

The 5:12 PM cron sent case studies to **every lead who replied**, regardless of what they said. The hostile wave (Nicholle/Fran/Liz/Breathe/Andrea/Chris) is the direct result — all these leads said "no" or "remove me" in their FIRST reply, but got marketing material anyway. The second reply is always hostile:

| Lead | First Reply (July 13) | Got Case Study? | Second Reply |
|---|---|---|---|
| Nicholle | "stop emailing me" | ✅ Yes at 5:12 PM | "And I said stop emailing me" (10:50 PM) |
| Fran | "remove me from your email list" | ✅ Yes at 5:12 PM | "My response was to remove me" (9:34 PM) |
| Liz | "Remove me now and do not contact again" | ✅ Yes at 5:12 PM | Already first-reply hostile |
| Breathe | "i said no. Email me again and i will report it" | ✅ Yes at 5:12 PM | Already first-reply hostile |

**Corollary:** The batch send at 5:12 PM was triggered by the same classification-order bug (positive before negative). By 11:30 PM, the hostile cascade had completed — all 4 hostile leads are now in both `hostile_senders` and `replied_message_ids`. No further action needed on them.

### Campaign #3577260 — Tony Berlin Still Stale

- **Tony Berlin** (berlinmediarelations.com): "Thank you - do you charge a fee for referrals?" — replied July 9, `our_replies_after=0`, 4+ days unhandled. Message ID in state but no human reply sent. **Same stale pattern as Austral HVAC (16 days) and Alpha Mechanical (10 days).** Needs operator attention.
- **Anabelle Alarcon**: already handled by operator.

### System State: Fully Caught Up on #3617053

By 11:30 PM ET, every lead on #3617053 had `our_replies_after > 0` or was in hostile_senders. No unhandled positives remain. The batch case-study approach (send to all, then absorb hostile replies) works but generates avoidable second-reply hostility — **classify BEFORE sending to prevent case studies going to negatives.**

## July 14, 2026 (12:35 AM ET) — Gina BOOKED Confirmed + Pipeline Timeout + Circling-Back Bug

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- No new unhandled owned-audiences positives — pipeline fully caught up
- **1 ⭐ BOOKED confirmed**: Gina (beyondthescoreboards.com) — first confirmed booking from campaign
- **2 new hostile/dead added**: Nicholle (colebeecoaching.com) hostile escalation, Robyn (mindfulnessathletics.com) turned negative
- Pipeline run at 04:00 UTC timed out on Gina's lead (ID 4136969058) — required manual recovery

### Pipeline Resilience Issue — Gina's Lead Times Out Consistently

Lead ID 4136969058 (Gina, beyondthescoreboards.com) causes `Instantly leads messages` to timeout at 30s, 60s, and 120s. The pipeline crashed on page 0 at this lead, skipping all remaining processing. Manual workaround: `Instantly leads messages ... > /tmp/msg_gina.json` (direct CLI, no subprocess timeout) succeeded in ~90s.

**Fix applied:** Flagged lead ID in `references/pipeline-infrastructure.md`. Future pipeline runs should catch `TimeoutExpired` per-lead and skip rather than crashing the entire page scan.

### ⛔ "Circling Back" Sent to Hostile Lead — Nicholle

Nicholle (colebeecoaching.com) replied "Remove me from your list" on Jul 10. Pipeline classified her as hostile. But on Jul 13 at 9:12 PM ET, the "circling back" logic sent her a case study anyway. She replied Jul 13 at 10:50 PM: "And I said stop emailing me."

**Root cause:** The circling-back logic checks for `our_replies_after > 0` but does NOT check the lead's prior reply classification. Since no SENT reply existed after her Jul 10 message, the logic treated her as "prior-week positive with no follow-up" and sent the case study.

**Fix documented in SKILL.md pitfalls:** Before sending circling-back, cross-reference the lead's `status` and `classification` in the state file. If `status == "dead"` with `classification in ("hostile", "unsubscribe")` — never re-engage.

### Robyn — Positive → Negative After Case Study

Robyn (mindfulnessathletics.com) replied "Yes please send it over" on Jul 10. Got case study + custom plan. On Jul 13 at 11:40 PM ET, circling-back sent another case study. She replied Jul 14 at 12:11 AM: "I'm not interested thanks, the AI plan is super generic. Please remove me from your mailing list."

This is the standard "second reply = hostile after case study" pattern. Added to state as dead.

### State File Stats Fix

The `stats` recalculation in the pipeline only tracked `awaiting_followup`, `replied`, `booked`, `dead`. The 5 `plan_built` leads (Kylie, Kareem, Lori, Dawn RWTX, Truwellness) showed as 0 in all categories. Added `plan_built` to the stats dict. Maintainers: when adding a new status, update both the lead status field AND the stats dict.

### Updated Dashboard State

| Metric | Count |
|---|---|
| Total tracked | 23 |
| ⭐ Booked | 1 (Gina) |
| 📋 Plan built, awaiting response | 5 |
| 🆕 Awaiting follow-up | 0 |
| ❌ Dead | 17 |

### Campaign #3607306 — Zero Activity

Inbox pages 0-1 have zero entries from campaign #3607306 (AI Guy). No sends, no replies, nothing to report.

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- 14 auto-replies pre-filtered (support@/info@/contact@/hello@) — 39%
- 8 known hostile/unsub pre-filtered
- 3 new replies today on #3617053, rest older/known

### 3 Today's Replies on #3617053

| Lead | Business | Reply | Classification | Action |
|---|---|---|---|---|
| Kylie Ryan | My Mind Coach | "thank you...would you consider a call during 9-5pm AEST" | `positive_interested` — second reply, timezone concern | **Replied** from Natalie, offering early-morning ET slots |
| Gina Tucci | Beyond the Scoreboards | "Thank you. I booked an appointment for next week" | `positive_interested` — BOOKED | No action — 4-day close |
| Robyn Kenney | Mindfulness Athletics | hostile second reply | `hostile` | Skipped — in hostile_senders |

### Kylie — Timezone Variant of Second-Reply Positives
Kylie's first reply was "Sorry Natalie, what are you suggesting?" → case study sent. Second reply: wants to book but AEST timezone doesn't work with Calendly. Same pattern as prior Kylie entry — genuine interest expressed as practical concern. 14h gap (AEST UTC+10 vs ET UTC-4). Early-morning ET (7-8am) = 9-10pm AEST — workable.

**Persona mismatch caught:** July 13 case study sent from `natalie@horizonvistaky.info` but signed "Willow." Domain maps to Natalie. Today's handcrafted reply correctly signed as Natalie.

### Gina — The 4-Day Close
Cold email Jul 10 → "Yes, please send that over" Jul 11 → custom plan + case study follow-ups → booked Jul 14. Custom plan + case study combo closed it in 4 days.

### #3577260 — Tony Berlin Still Stale
Tony (berlinmediarelations.com): "do you charge a fee for referrals?" — replied Jul 13, `our_replies_after=0`. Same stale-positive pattern. Flagged for operator.

### State Update
- Added Kylie's message ID. Gina's already in state.
- State: 360 msg_ids, 28 hostile, 22 unsubs

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- 15 auto-replies pre-filtered (support@/info@/privacy@/contact@/hello@)
- 5 negatives/declines: Mike (must decline), Drd (no thanks), Jared (no interest), Meghan (no thank you), Ppavey (I am not currently looking)
- 1 hostile second reply: Nicholle (colebeecoaching.com) — "And I said stop emailing me" after receiving case study reply at 5:12 PM
- **4 fresh owned-audiences positives (NOT yet handled):** Dawn RWTX, Lori, Kylie, plus Gina who BOOKED

### 4 Owned Audiences Positives

| Lead | Business | Reply | Sender | Vertical | Status |
|---|---|---|---|---|---|
| Dawn King-Dushane | Renew Wellness (renewwellnesstx.com) | "Sure. Send me more info, please." | Anna | Women's health/hormones | NEW — no case study sent yet |
| Lori Carpenos | 3 Principles Therapy | "Hey Willow, Referrals are definitely key. Always have been." | Willow | Therapy/coaching | NEW |
| Kylie Ryan | My Mind Coach (mymindcoach.com.au) | "Sorry Natalie, what are you suggesting?" | Natalie | Coaching | NEW |
| Gina Tucci | Beyond the Scoreboards | "Thank you. I booked an appointment for next week" | Nova | Mental strength coaching | 🎉 BOOKED — case study sent at 5:12 PM, she replied "booked" at 9:52 PM |

## July 15, 2026 (4:30 PM ET) — Day 2 of Auto-Responder Tail, SILENT Confirmed

### Stats
- 60 inbox entries across pages 0-2 (41 from #3617053, 16 from #3639259, 3 from #3577260)
- #3617053: 35 auto-reply prefixes (85% hit rate), 1 auto-responder (body): Ann Konkoly — "72 business hours"
- 1 hostile/unsub skipped (in state), 3 already handled (Kareem, Shira, Jodie)
- 1 post-booking neutral: Gina — "Looking forward to it too!" (already booked, no action)
- **0 new positives, 0 new negatives** — SILENT run confirmed

### Pattern Confirmed: PAUSED Campaign SILENT Is the Steady State
The auto-responder tail on #3617053 continues into day 2 exactly as predicted. 85% of entries are auto-reply prefixes. The 6 "real" leads that needed message history pulls were all already in state (handled, hostile, or auto-responder). **SILENT runs on PAUSED campaigns during the auto-responder tail are the expected steady state, not a monitoring failure.**

### #3639259 (Podcasters - SpeakerAgent v2) — First Replies
16 entries on this campaign (across 3 pages). All are auto-reply prefixes: info@, hello@, partnerships@, podcast@, team@. Three real-appearing leads (Michael Krigsman cxotalk.com, Ademola Odewade, Rebecca wethrive.live) returned 0 messages from `leads messages` — either vestigial entries or lead-ID mismatch from the inbox `email_lead_id`. None needed action this run. ⚠️ The `partnerships@` prefix was not in the auto-reply filter for this run — added to both the workflow reference and `monitor_pipeline.py`.

### #3577260 (PR Agencies) — Mike Billoni Confirmed Vestigial
Mike Billoni (mike@billoni.com) returned 0 messages from `leads messages` — confirms the forwarded-thread artifact noted in the Instantly-cold-email skill pitfall. Scott (formidable-media.com) not investigated this run.

### Pre-Call Reports: All Caught Up
- Gentry Robles: call at 12:00 PM ET (already passed). Report exists.
- Chris Warrick: tomorrow Jul 16 at 3:30 PM ET. Report exists at `/opt/data/clients/chris-warrick/pre-call-report.md`. ⚠️ Timezone flag: 3:30 PM ET = 5:30 AM Melbourne.
- Gina Karnisovas: Jul 21 at 10:00 AM ET. Report exists.
- Keith Fox (AES): call TBD. Report exists.
- No new bookings found.

## July 15, 2026 (9AM ET) — Campaign PAUSED, Auto-Responder Tail, All Caught Up

### Campaign Status Change
Campaign #3617053 is now **PAUSED** — the 9,457-lead blast completed and the campaign was paused. #3639259 (Podcasters - SpeakerAgent v2) is now the only ACTIVE campaign but has minimal activity.

### Stats
- 60 inbox entries across pages 0-2 (57 from #3617053, 2 from #3639259, 1 from #3577260)
- 15 TODAY entries on #3617053 — 11 auto-reply prefixes (info@/support@/hello@/privacy@/care@), 4 real leads (Ann, Gina, Shira, Kareem)
- All 5 real leads (incl. yesterday's Leslie) already had message IDs in state — zero new additions
- System fully caught up. SILENT run expected.

### PAUSED Campaign Steady State
When a campaign is PAUSED after a large blast:
- Expect [SILENT] cron runs for 48-72 hours during the auto-responder tail
- The email-prefix heuristic catches 75%+ of entries (support@, info@, hello@, privacy@, etc.)
- Remaining real leads should already be in state from prior monitoring runs
- A SILENT run does NOT mean the monitoring is broken — it means the system is caught up

### Real Leads (All In State)
| Lead | Reply | Classification | Status |
|---|---|---|---|
| Ann Konkoly | "All emails will be addressed within 72 business hours" | auto_reply | In state — 72h business auto-responder |
| Gina Tucci | "Looking forward to it too!" | positive_interested | BOOKED — post-booking message, no action |
| Shira Raymond | "I'm going to pass at this time. Thank you." | negative_notfit | Handled (our_replies_after=1), polite decline |
| Kareem | "Where were you three years ago!?!" | positive_interested | Handled (our_replies_after=1), enthusiastic |
| Leslie | "REMOVE!" | hostile | In hostile_senders from previous run |

### #3639259 (Podcasters - SpeakerAgent v2)
- 2 entries today: hello@onetenhundred.vc, podcasts@thenewstack.io
- Both auto-reply prefixes — no real replies yet
- Campaign is ACTIVE but early in the sending cycle

### State Files Healthy
- OA state: 126 msg_ids, 7 hostile_senders, 75 leads tracked
- All 5 new message IDs confirmed in state before processing began
- July 14 state hygiene fix is working — no false re-discovery of already-classified leads

## July 14, 2026 (01:30 AM ET) — State File Gaps + 4 More Misclassifications Confirmed

### Stats
- 40 inbox entries across pages 0-1 (36 from #3617053, 4 from #3577260)
- 8 "new" leads appeared in inbox but NOT in state file → all already processed by prior cron runs
- **Root cause:** Prior cron runs classified these leads but never wrote their message IDs to state
- **4 additional dead leads** confirmed from the 5:12 PM ET batch-send cascade (case studies sent to negatives)
- **No new unhandled positives** on #3617053. Pipeline fully caught up.
- **1 unhandled positive on #3577260:** Tony Berlin — 7+ hours stale, `our_replies_after=0`

### 🚨 State File Gaps — 4 Message IDs Missing From Prior Runs

The 5:12 PM ET cron classified and "handled" these leads (sent case studies) but NEVER added their message IDs to the state file. Every subsequent 30-minute cron re-discovers them as "new":

| Lead | Reply | Classification | MsgID Added Now |
|---|---|---|---|
| Meghan | "No, thank you. Have a great week!" | negative_notfit | ✅ |
| Andrea | "I'm no longer running this business… please remove me" | unsubscribe | ✅ |
| Dhiana | "Not at this time. Thanks" | negative_notfit | ✅ |
| Chris | "I don't own medical practice. Please stop contacting me" | hostile | ✅ |

Plus 2 hostile second-reply IDs also missing:
- Liz's second reply: `<F9432BD7-...@askliz.com>` — added
- Fran's second reply: `<B8AEDC38-...@pureandmindful.com>` — added

**Root cause:** The cron workflow classified these leads, sent case studies anyway (classification-order bug), but the `known_reply_message_ids` append only happened for some leads, not all. Inconsistent state hygiene.

**Fix applied:** All 6 message IDs added to state (total: 68). The monitoring workflow now explicitly requires: "After classifying EVERY lead (positive, negative, hostile, OOO, auto-reply), add their message ID to `known_reply_message_ids`. This prevents false re-discovery on every subsequent run."

### Batch-Send Cascade — 4 More Victims

The classification-order bug (positive before negative) at 5:12 PM ET also caught these 4 — all got case study replies they shouldn't have:

| Lead | First Reply | Got Case Study at 21:12 UTC |
|---|---|---|
| Meghan | "No, thank you. Have a great week!" | ✅ Yes |
| Andrea | "please remove me from your list" | ✅ Yes |
| Chris | "Please stop contacting me" | ✅ Yes |
| Dhiana | "Not at this time. Thanks" | ✅ Yes |

Combined with the earlier 5 (Ppavey, Mike, Jared, Drd, Breathe), that's **9 leads who said "no" and got marketing material.** The hostile cascade response came from Nicholle, Fran, Liz, Breathe, Robyn. Meghan/Andrea/Chris/Dhiana haven't escalated yet but may.

### Tony Berlin — 7+ Hours Stale on PR Campaign

Same stale-positive pattern as Austral HVAC (16 days) and Alpha Mechanical (10 days). Message ID in `known_reply_message_ids` but `our_replies_after=0`. The daemon scanned and marked processed but never generated a draft. He asked "do you charge a fee for referrals?" — a straightforward question that needs operator reply via hardcoded SpeakerAgent template.

### System State After Update

| Metric | Count |
|---|---|
| Total message IDs in state | 68 |
| Total leads tracked | 30 |
| ⭐ Booked | 1 (Gina) |
| 📋 Plan built | 5 |
| ✉️ Replied | 1 (Vivian) |
| 💀 Dead | 23 |

### Gina — Counterexample to "Second Replies = Hostile"

Gina's first reply on July 11 ("Yes, please send that over") was scanned into state but never handled (`our_replies_after=0`, MsgID in `replied_message_ids`). She sat unhandled for 2 days. The July 13 5:12 PM cron finally sent a case study reply ("Circling back..."). Instead of becoming hostile, she **booked an appointment** at 9:52 PM.

This is the rare counterexample: a second reply after a case study follow-up that is POSITIVE, not hostile. Key difference from Fran/Liz/Breathe/Robyn: Gina's first reply was genuinely positive and unhandled. The Fran/Liz pattern is: first reply was negative but misclassified, then case study sent to someone who already said no. Gina's pattern is: first reply was positive but fell through the cracks.

**Lesson:** The "second reply = hostile" heuristic only applies when the FIRST reply was a false-positive classification (negatives getting case studies). When a genuinely positive lead was simply not replied to, the follow-up is welcomed.

### Vertical Mismatch — Cold Email Content

⚠️ Dawn RWTX's original cold email (from Anna) opened with "every restriction pass hits men's health hard" — men's-health framing. Renew Wellness is a women's health / general hormone practice (FNP-C). Dawn replied positively anyway, but the mismatch is awkward. When reviewing campaign #3617053's email templates: the cold email variant for women's health providers should not mention men's health.

### PR Campaign #3577260

- **Anabelle Alarcon** (alarconpr.com): "Hi Violet: Thanks for reaching out. I would welcome the opportunity to jump on a call to discuss further." — strong positive, needs SpeakerAgent template reply.
- **Tony Berlin** (berlinmediarelations.com): "Thank you - do you charge a fee for referrals?" — question about fees. MsgID in state since July 9, `our_replies_after=0` — still unhandled after 4 days.

### 4 Positives Sent (drafted, awaiting operator approval)

All three new positives received case study reply drafts using men's-coaching case study (mindful-acorn-y9bn.here.now/) as fallback — no women's-health-specific case study exists.

Gina already booked — no further email needed beyond a confirmation.

## July 15, 2026 (7:30 PM ET) — Podcast Campaign Day 1 Active, #3617053 Auto-Responder Tail, Pre-Call Flags

### Stats
- 60 inbox entries across pages 0-2 (40 from #3617053, 17 from #3639259, 3 from #3577260)
- #3617053: 40 entries — auto-responder tail continues (support@, info@, compliance@, privacy@, hello@, care@, connect@, consults@, trt@, ask@, help@). 5 real leads (Ann, Gina, Shira, Kareem, Leslie) all already in state. **Zero unhandled.**
- #3639259: 17 entries — first day of active sending. 8 auto-reply prefixes. 9 real leads checked via message history.
- #3577260: 3 entries — Mike Billoni (vestigial), Scott Formidable (vestigial), Sfrontera ("All good!" — polite decline, in state).
- 3 new message IDs added to state (Sean, Nick OOO, Trinity OOO). Total: 391 msg_ids, 30 hostile, 22 unsubs.

### #3639259 Podcast Campaign — Day 1 Results

| Lead | Reply | Classification | Status |
|---|---|---|---|
| Ademola Odewade | "I'd be happy to have a brief conversation and learn more about SpeakerAgent" | `positive_interested` | ✅ Handled — Orin replied same-day |
| Sean (newsales.expert) | "Which of my podcasts are you referring to?" | `neutral` | ✅ Handled — Branson replied |
| Isabel (tumcoeur.com) | "I would love to chat with you, do you have a calendar link?" | `positive_interested` | ✅ Handled — Zayden replied same-day |
| Rebecca (wethrive.live) | "I typically respond to emails on Monday and Friday" | `auto_responder` | ✅ Handled — Branson replied anyway |
| Michael Krigsman (cxotalk.com) | "We publicly blacklist agencies that use AI to send us guests" | `hostile` | 🚫 In hostile_senders. Never re-engage. |
| Chris EI (entrepreneursforimpact.com) | "I'm travelling with limited bandwidth" | `ooo` | Added to state |
| Nick (amazingwave.digital) | "I'm currently taking a very well deserved break" | `ooo` | Added to state |
| Trinity (trinitynewlife.com) | "I'm out of the country with limited access to email" | `ooo` | Added to state |

**Key findings:**
- 3 warm positives handled same-day by the SpeakerAgent reply template (Orin, Branson, Zayden) — all sent within 1-3 hours of the reply arriving. The hardcoded template ("SpeakerAgent is in beta right now. We're new and doing everything pretty custom to each partner. There's no fees — it's a true partnership program.") is working fast.
- Michael Krigsman is a known hostile from prior monitoring — already in state. His "publicly blacklist" reply is the podcast-specific hostile variant. Never re-engage — he can cause public reputation damage.
- 3 OOOs from the first-day blast — normal. Podcast hosts get flooded with cold outreach.
- The `podcasts@` prefix (thenewstack.io) was added to the auto-reply filter.

### Pre-Call Reports
- **Gentry Robles:** Call today 12 PM ET (passed). Report complete.
- **⚠️ Chris Warrick:** Call TOMORROW Jul 16, 3:30 PM ET. Report exists with critical flags:
  - 🚨 Timezone: 3:30 PM ET = **5:30 AM Melbourne** — verify if intentional
  - Game plan not built ("QUEUE NOW")
  - No LinkedIn, no email thread (direct Cal.com booking)
- **Gina Karnisovas:** Jul 21 10 AM ET. Report complete. Lead is HOT.
- **Keith Fox (AES):** TBD. Report exists.

## July 17, 2026 (12:16 PM ET) — Cross-Campaign Positive (Spark #3577260) + CSS Bug Found + All Campaigns Steady

### Stats
- 60 inbox entries across pages 0-2 from 5 campaigns (#3617053, #3639259, #3652624, #3577260, #3652623)
- 40 auto-reply prefixes filtered (67%) — `moreinfo@` and `concierge@` in use
- 20 real leads pulled via message history
- **1 TODAY-positive handled: Spark (Campfire Group, #3577260)** — 5-message deep-funnel, pricing question
- 19 other leads: all already in state, vestigial, or OOO/retirement/unsub
- State: 497 msg_ids, 34 hostile, 27 unsubs | OA: 196 msg_ids, 84 leads

### Campaign Breakdown

| Campaign | Status | Entries | Auto-RP | Real | Positives |
|---|---|---|---|---|---|
| #3617053 Coaching OA | PAUSED | 38 | 34 (89%) | 4 | 0 |
| #3639259 Podcasters v2 | ACTIVE | 11 | 5 | 6 | 0 (all in state) |
| #3652624 Recruiting OA | ACTIVE | 6 | 0 | 6 | 0 |
| #3577260 PR Agencies | COMPLETED | 3 | 1 | 2 | **1 handled** |
| #3652623 HVAC OA | ACTIVE | 2 | 0 | 2 | 0 |

### Spark/Ethan (Campfire Group, #3577260) — 5-Message Deep-Funnel Pricing Question

**Full thread:**
- Jul 1: Eleanor cold email → Jul 1: "Tell me more"
- Jul 3: Eleanor reply + Tony looped
- Jul 15: Case study follow-up
- Jul 16: "Can you tell us what a typical engagement looks like?" → engagement breakdown sent
- Jul 17 10:40 AM: "Makes sense, how do you price?" → Template 4 pricing reply (11:06 AM)
- **Jul 17 11:50 AM: "Want guidance before a call. I think Tony fell off this thread"** → **Replied 12:16 PM**

**Handling:** SpeakerAgent PR Template 4 customized: acknowledged request for framework guidance (no numbers), re-looped Tony, gave model overview (client volume + podcast lanes, accessible range, not enterprise), pushed to call. Signed Eleanor. **26-minute handling time.** This is the 3rd positive reply from the same lead in a week — the most engaged lead in the system, on a COMPLETED campaign (#3577260). **Confirms cross-campaign monitoring on COMPLETED campaigns is essential.**

### 🚨 CSS-Only False Positive Bug Found + Fixed

The `is_auto_responder()` CSS-only check (`len(re.sub(r'[\s{};:#.\-\w"\'=@\(\)\[\],]', '', body)) < 5`) catches **every normal English reply** because standard ASCII text has 0-3 characters that don't match the regex. Spark's 638-char human reply was classified as `auto` and would have been silently skipped. **Fixed:** CSS check now requires explicit CSS syntax patterns (`body {`, `table td {`, etc.) before triggering.

### Pre-Call Reports
All 6 reports current. No calls today (Friday) or tomorrow (Saturday). Next call: Gina Karnisovas (Beyond the Scoreboards), Mon Jul 21 10 AM ET. Report at `clients/beyond-the-scoreboards/`.

### Learnings
- **COMPLETED campaigns produce the hottest deep-funnel leads** — Spark's 5-message thread is the most engaged prospect in the system, on a campaign that stopped sending 2+ weeks ago. Cross-campaign monitoring isn't optional.
- **CSS-only check is a silent pipeline killer** — this bug would have caused every ad-hoc monitoring script to silently skip every human reply. Fixed by requiring explicit CSS syntax patterns.
- **Day 3+ auto-responder tail on #3617053 at 89% prefix rate** — useful monitoring window closed. PAUSED campaign steady state.
- **New OA campaigns (#3652623, #3652624) in day 2 launch wave** — all OOO/retirement/unsub, zero genuine positives. Matches #3617053 launch pattern.
- **New Cal.com bookings appear between cron runs** — the API check (`GET /v2/bookings?status=upcoming`) catches bookings the `cal_bookings.json` snapshot misses. Always run the live API check in Part B.

## July 17, 2026 (6:30 PM ET) — Spark Pricing Close + Drew Targeting Correction + All Campaigns Steady

### Stats
- 60 inbox entries across 5 campaigns (pages 0-2)
- 39 auto-reply prefixes filtered (65%) — `moreinfo@`, `concierge@` in use
- 16 real leads pulled via 4 parallel batches (&& chaining, ~90s total)
- **2 positive replies handled:** Spark (pricing close), Drew (targeting correction)
- 14 OOO/retirement/sabbatical/vestigial — zero unhandled positives remain

### Spark/Ethan — "sure" at 4:55 PM ET = PRICING CLOSED
Full 13-message, 16-day thread from cold email to pricing acceptance. Eleanor gave $1,500-$3,000/mo at 4:37 PM → Ethan "sure" at 4:55 PM (18 minutes). Our closing reply sent within minutes: *"Great. Let's get this moving. Tony can walk you through..."* The most engaged lead in the system, on a COMPLETED campaign. Case study at `references/spark-deep-funnel-case-study-2026-07-17.md`.

### Drew McLellan — Targeting Correction Archetype (NEW)
First reply 4:21 PM: "Hopefully the attached will help." — sent media kit (warm positive). Our reply 4:41 PM: standard SpeakerAgent template via Zayden. **Second reply 4:42 PM: "Agency owners are not typically my guests. It's people who serve agency owners."** — NOT hostile, NOT negative. This is a **targeting correction** from an engaged podcaster refining our understanding of their audience. Replied 6:36 PM via Zayden: acknowledged correction, reframed to "consultants, coaches, software vendors, training platforms," kept SpeakerAgent template. **The lead is MORE qualified after the correction — they told us exactly who they want.** Documented in `references/speakeragent-podcaster-reply-template.md`.

### Campaign Breakdown

| Campaign | Status | Entries | Auto-RP | Real | Positives |
|---|---|---|---|---|---|
| #3617053 Coaching OA | PAUSED | 38 | 34 (89%) | 2 (Kareem, Rose) | 0 — OOO/declined |
| #3639259 Podcasters v2 | ACTIVE | 11 | 4 | 7 | **1 handled** (Drew) |
| #3652624 Recruiting OA | ACTIVE | 6 | 0 | 4 | 0 — all OOO/retirement |
| #3577260 PR Agencies | COMPLETED | 3 | 1 | 2 | **1 closed** (Spark) + 1 (Jodi) |
| #3652623 HVAC OA | ACTIVE | 2 | 0 | 2 | 0 — both OOO |

### Pre-Call Reports: All Caught Up
- Gentry Robles: Jul 15 ✅ passed. Report at `clients/connect-med/`.
- Chris Warrick: Jul 16 ✅ passed. Report at `clients/primary-business/`.
- Gina Karnisovas (Beyond the Scoreboards): **Mon Jul 21 10 AM ET** — next call. Report current at `clients/beyond-the-scoreboards/`.
- No calls today (Friday) or tomorrow (Saturday). No new bookings found.

### State Update
- Daemon: **512 msg_ids** (+3: Drew's both replies + Spark's "sure"), 34 hostile, 27 unsubs
- OA: 196 msg_ids, 84 leads tracked

### Key Learnings
- **Targeting-correction replies are positives, not neutrals.** A podcaster who corrects your guest targeting has ALREADY decided to engage — they're investing time to make the match work. Treat as warm positive with a tailored response that acknowledges the correction.
- **Day 2-3 on new OA campaigns (#3652623, #3652624):** zero genuine positives, all OOO/retirement. This is the EXACT same launch pattern as #3617053. Continue monitoring but expect SILENT runs through the weekend.
- **COMPLETED campaigns produce the deepest-funnel closes.** Spark's 16-day, 13-message thread would have been silently lost without cross-campaign monitoring. #3577260 has been stopped for 15+ days and just produced the highest-value close in the system.

## July 19, 2026 (12:30 PM ET) — Sunday Sweep: Weekend Replies Auto-Handled, System Steady

### Stats
- 60 inbox entries across pages 0-2 from 5 campaigns (#3617053, #3639259, #3652624, #3577260, #3652623)
- 40 auto-reply prefixes filtered (67%) — support@, info@, help@, hello@, privacy@, press@, contactus@, moreinfo@, concierge@, ask@
- 19 real leads pulled — 8 via parallel batches (&& chaining, ~90s)
- Page 2: 20 entries, ALL auto-reply prefixes from #3617053 (days 3-4 of blast)
- **0 new unhandled positives** — system fully caught up

### Campaign Breakdown

| Campaign | Status | Entries | Auto-RP | Real | Positives |
|---|---|---|---|---|---|
| #3617053 Coaching OA | PAUSED | 40 (3 pages) | 36 (90%) | 4 | 0 (all in state) |
| #3639259 Podcasters v2 | ACTIVE | 7 | 2 | 5 | 1 handled (Peter) |
| #3652624 Recruiting OA | ACTIVE | 6 | 0 | 6 | 0 (all OOO/retirement/unsub) |
| #3577260 PR Agencies | COMPLETED | 3 | 1 | 2 | 0 (Spark/Jodi in state) |
| #3652623 HVAC OA | ACTIVE | 2 | 0 | 2 | 0 (both OOO) |

### Peter Vera — Saturday Reply Auto-Handled by Branson

Peter (bizexitgrow.com, #3639259) replied Saturday Jul 18 at 10:45 AM ET: "Got something on the books for Tuesday. Looking forward to it!" — confirming a booked call. Branson auto-replied Sunday Jul 19 3:04 AM ET: "Awesome — looking forward to it, Peter. Talk Tuesday!" — handled within hours on a weekend. **Status: BOOKED.**

### Key Learnings
- **Weekend monitoring runs are viable** — the daemon handles replies across the weekend. This Sunday sweep found nothing unhandled.
- **Page 2 is all auto-reply prefixes** — by day 6 of the #3617053 blast, pages 0-1 contain real leads (already in state) and page 2 is entirely auto-reply prefixes from days 3-4. The monitoring window for real replies on a PAUSED campaign closes after ~72 hours.
- **Cross-campaign steady state confirmed** — 0 unhandled positives across 5 campaigns on a Sunday afternoon is the expected baseline. SILENT runs are the norm, not the exception.
- **Peter Vera → BOOKED** — the SpeakerAgent template closed a podcaster within 3 days of first contact (Jul 15 cold email → Jul 16 "Open to receiving guests" → Jul 18 "Got something on the books for Tuesday").

### Pre-Call Reports: All Caught Up
- Samar: Mon Jul 20, 10:00 AM ET. Report exists at `clients/samar/pre-call-report.md`. Cold-inbound, gmail-only, no research possible — discovery on the call.
- Gina Karnisovas: Tue Jul 21, 10:00 AM ET. Report exists at `clients/beyond-the-scoreboards/pre-call-report.md`. HOT lead from cold email campaign.
- 5 total upcoming bookings on Cal.com, all have reports.

### State Update
- Daemon: 569 msg_ids, 34 hostile, 28 unsubs
- OA: 204 msg_ids, 86 leads tracked

## July 20, 2026 (10:30 PM ET) — 6-Campaign Sweep, Jeff Handled + Nicole Deferred, 2 Classifier Bugs Found

### Stats
- 60 inbox entries across pages 0-2 from 6 campaigns (#3617053, #3639259, #3652624, #3577260, #3652623, #3691319)
- 38 auto-reply prefixes filtered (63%) — support@, info@, hello@, privacy@, contactus@, care@, compliance@
- 22 real leads, 18 already in state from prior runs
- 4 today (Jul 20) leads checked — ALL already handled or non-actionable
- **0 unhandled positives** — system fully caught up

### 4 Today's Replies

| Lead | Campaign | Reply | Classification | Status |
|---|---|---|---|---|
| Jeff Dillon | #3617053 OA | "Yes, I'd be open to see what you have." | `positive_interested` | [HANDLED] Aubrey sent case study within 15 min |
| Nicole Wald | #3577260 PR v2 | "I'll be able to get to this at the start of August." | `positive_deferred` | [HANDLED] Mila replied 19:35 ET |
| Daniel | #3691319 Solar | Extended OOO — absent from office indefinitely | `ooo` | Added to state |
| Isabel | #3639259 Podcasters | "Looking forward to it too!" | `neutral` post-booking | Call was today. No action needed |

### Campaign #3691319 (Solar) — First Day
1 entry (Daniel OOO). Campaign launched Jul 20 — uses SpeakerAgent template, not OA. First-day OOO wave expected. Zero genuine positives so far.

### Jeff Dillon — Strong Positive, Handled Within 15 Minutes
First genuine #3617053 positive in ~4 days (since Kareem/Shira on Jul 15). Aubrey's case study reply sent at 18:05 ET ("Hey Jeff — love the quick yes. Here you go --> aiintegraterz.com/case-studies/mens-health.pdf") — 15 minutes after Jeff's reply at 17:50 ET. The earlier cron that handled him ran outside the monitoring sweep — good coverage overlap.

### Nicole Wald — Operator Already Deferred
7-message thread dating back to Jul 7. Mila sent "Sounds good, Nicole — totally understand. I'll set a reminder to circle back in early August" at 19:35 ET — 96 minutes after Nicole's reply. Total thread: cold email → "Happy to chat" → SpeakerAgent intro → case study follow-up → "Checking in" → "I'll get to this in August" → operator deferral. Handled correctly.

### Campaign Breakdown

| Campaign | Status | Entries | Auto-RP | Real | Positives |
|---|---|---|---|---|---|
| #3617053 Coaching OA | PAUSED | 39 | 35 (90%) | 4 | 1 handled (Jeff) |
| #3639259 Podcasters v2 | ACTIVE | 8 | 6 | 2 | 0 (Isabel post-booking) |
| #3652624 Recruiting OA | ACTIVE | 6 | 0 | 6 | 0 (all Jul 16 OOO/retirement) |
| #3577260 PR Agencies | COMPLETED | 4 | 2 | 2 | 1 deferred (Nicole) |
| #3652623 HVAC OA | ACTIVE | 2 | 0 | 2 | 0 (both Jul 16 OOO) |
| #3691319 Solar | ACTIVE | 1 | 0 | 1 | 0 (OOO) |

### Classifier Bugs Found (Fixed Above)

1. **\r\n quote-extraction failure** — Jeff's Outlook reply with CRLF line endings broke the `\nOn .* wrote:` pattern. Cold email words contaminated classification → false negative. Fix: normalize `\r\n` → `\n` before extracting.

2. **"Yes" first-word positive missed** — "Yes, I'd be open to see what you have" not caught by one-word check (too many words) or any positive regex. Fix: add first-word check for yes/yeah/yep/sure/absolutely/definitely BEFORE negative patterns.

### Pre-Call Reports: All Caught Up
- Samar: Today 10 AM ET — passed. Report at `clients/samar/`.
- Gina Karnisovas: Tue Jul 21 10 AM ET — report current at `clients/beyond-the-scoreboards/`. HOT lead. Game plan QUEUE NOW.
- Peter Vera: Tue Jul 21, time UNKNOWN — report at `clients/bizexitgrow/`. Call time still not in Cal.com.
- Erin Todus (+Amy Crook): Fri Jul 24 11:30 AM ET — report at `clients/strativis/`.
- Johanna Watson: Mon Jul 27 12:30 PM ET — report at `clients/artemis-hou/`.
- Thomas Johnston: Wed Aug 12 11:00 AM ET — report at `clients/synova-search/`.

### State Update
- Daemon: 587 msg_ids (+4), 34 hostile, 28 unsubs
- OA: 204 msg_ids, 87 leads tracked (+1: Jeff)

## July 22, 2026 (11:30 AM ET) — 6-Campaign Sweep, Partner Domination, Cross-Account Booking Found

### Stats
- 40 inbox entries across pages 0-1 from 7 campaigns (#3698110-3698114 Partner CPA, #3692104 Med Spa, #3639259 Podcasters, #3577260 PR, #3617053 Coaching, #3691319 Solar)
- 4 auto-reply prefix filtered, 4 hostile/unsub skipped
- 32 leads needed history — 19 were partner campaigns (#3698110-3698114), overwhelming page 0
- **0 unhandled positives** across all campaigns
- **1 new email-thread booking found:** Jeffrey Bradbury (TeacherCast, #3639259)

### Campaign Breakdown

| Campaign | Status | Entries | Pattern |
|---|---|---|---|
| #3698110-3698114 (Partner CPA) | ACTIVE | 19 (48%) | 85-95% OOO/negative — spot-check confirmed (Larry=OOO, Jeff="not interested"). Page 0 dominated. |
| #3692104 (Med Spa Charm) | ACTIVE (Day 1) | 6 | Launch burst — all auto/hostile (Dave=redirect, Eric=dead, Kala=hostile) |
| #3639259 (Podcasters) | ACTIVE | 3 | 1 handled (Isabel), 1 booked last week (Peter), **1 NEW booking (Jeffrey)** |
| #3577260 (PR v2) | COMPLETED | 2 | Both handled (Steve 9-msg deep funnel, Nicole operator-deferred) |
| #3617053 (Coaching OA) | PAUSED | 1 | Jeff usmenshealth positive → already handled (our_replies_after=1) |
| #3691319 (Solar) | ACTIVE | 1 | Daniel OOO auto-responder |

### Jeffrey Bradbury — Cross-Account Booking (SpeakerAgent Cal.com)
Jeffrey replied Jul 22: "I just grabbed a time on your calendar. Looking forward to the chat!" He booked via `cal.com/speakeragent/15min` (Zayden's account), NOT `cal.com/usingaitoscale` (Justin's). Zero Cal.com records found. Pre-call report generated at `clients/teachercast/pre-call-report.md` with call time/meeting link flagged as UNKNOWN. See `pre-call-report` skill → `references/cross-cal-account-bookings.md`.

### Ad-Hoc Classifier Pitfall Confirmed
Jeff Dillon (#3617053) was classified as `negative_notfit` by the session's ad-hoc `parse_histories.py` because it missed the `\r\n` → `\n` normalization and `From:.*Date:` Outlook forward pattern. His actual reply was "Yes, I'd be open to see what you have" — clearly positive. The canonical `monitor_pipeline.py` catches this correctly. **Always use the canonical pipeline, not ad-hoc classifiers.**

### Pre-Call Reports
- **Josh Hamilton** (School for Men): TODAY 12:30 PM ET — report at `clients/school-for-men/` ✅
- **John Compton** (Agile Search): Thu Jul 23 10:00 AM — report at `clients/agile-search/` ✅
- **Jeffrey Bradbury** (TeacherCast): 🆕 date UNKNOWN — report at `clients/teachercast/` ⚠️ check SpeakerAgent Cal.com
- Erin Todus (Strativis): Fri Jul 24 11:30 AM — report at `clients/strativis/` ✅

### State Update
- Daemon: 618 msg_ids, 38 hostile, 31 unsubs
- Kala (procelltherapies) already tracked as hostile