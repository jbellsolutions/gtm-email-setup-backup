# Campaign-Specific Positive Reply → Slack Push

Reusable pattern: monitor a specific Instantly campaign for positive replies and push them to a dedicated Slack channel in near real-time.

## Recipe

1. **Verify bot has channel access** — use `send_message(action='list')` to check that the target Slack channel appears in available targets. If `channel_not_found` when posting, the bot hasn't been invited. The user must invite `@Hermes` to the channel before the cron can deliver.
2. Identify the campaign ID (`Instantly campaigns list`)
3. Create a cron job that:
   - Fetches master inbox replies (paginated, `--offset 0,20,40...` up to ~200)
   - Filters for target campaign ID
   - Deduplicates against `/tmp/<campaign>_posted_ids.json` (tracks already-posted lead IDs by `email_lead_id`)
   - **Filters out operator-sent REPLY messages BEFORE classification.** After fetching message history, skip any REPLY whose `message_id` contains our sending domains (speakeragent.ai, horizonedgenv.info, successcrestco.info, growthmapar.info, progressdeskks.info, strategyvistaaz.info, advanceaxisnm.info, successliftia.info, progressaxismd.info, growthsignalmn.info, elevatedeskin.info, scaledeskct.info, growthliftwa.info, prosperliftwi.info, nextedgemi.info, horizonvistaky.info, horizonfocusmo.info, prosperstepms.info, visiondesknj.info, operatorspeaker.info). Classify only non-operator REPLY messages, and use the EARLIEST one (not the latest — operator follow-ups push the latest REPLY to be an operator message). If after filtering all REPLY messages are operator-sent, skip the lead entirely (the lead's original reply was already processed). See `references/campaign-slack-push.md#pitfalls` for the full domain list.
   - Classifies each NEW reply using INLINE classification rules (NOT `scripts/classify.py` — the classifier has ~30% error rate)
   - **Before classification, filters out operator-sent REPLY messages** by checking `message_id` for our domains (speakeragent.ai, horizonedgenv.info, successcrestco.info, growthmapar.info, progressdeskks.info, useaiintegraterz.com, joinaiintegraterz.com, meetaiintegraterz.com, strategyvistaaz.info, advanceaxisnm.info, successliftia.info, progressaxismd.info, growthsignalmn.info, elevatedeskin.info, scaledeskct.info, growthliftwa.info, prosperliftwi.info, nextedgemi.info, horizonvistaky.info, horizonfocusmo.info, prosperstepms.info, visiondesknj.info, operatorspeaker.info). The latest REPLY in history may be an operator follow-up, not the lead's original reply — classify only non-operator REPLY messages, using the EARLIEST one.
   - Posts verified positives to Slack via `send_message` tool
   - Saves posted lead IDs to dedup file
4. Seed the dedup file with all existing positives before first run to avoid reposting

## Slack Post Format

```
🔥 BOOKED: {first_name} {last_name}
📧 {email}
🏢 {company_name}
💬 "{reply_text (first 400 chars, stripped of HTML)}"
```

Use 🔥 BOOKED for `positive_interested`, 📩 INFO for `positive_soft`.

## Inline Classification Rules (use these, NOT the script)

Check in order — first match wins:

- **OOO**: "out of office", "on vacation", "away from", "maternity leave", "death in the family", "taking time off", "retired", "retirement", "due to a high volume", "we appreciate your patience", "I will reply to your email as soon", "closed for the holiday", "back in the office on", "thank you for your email!" + no follow-up interest signals, "thanks for your email" + no interest, "out of town", "parental leave", "this is an auto-generated reply", "thanks for reaching out" + no interest signals (form auto-responders often say "Thanks for reaching out... your email will be responded to"), "traveling" + "limited access", "will be ooo", "i will be ooo", "currently away", "at the beach", "beach with"
- **UNSUBSCRIBE**: "unsubscribe", "remove me", "take me off", "stop mail", "stop email", "please remove", standalone "Stop" or "Stop.", "Stop Get Outlook for iOS" (mobile signature)
- **HOSTILE**: "psycho", "slop", "delete whatever AI", "work on your own writing", "stop contacting me", "spam", "do your research", "fuck off"
- **NOT FIT**: "not interested", "no thank you", "no thanks", "not looking for", "all set for now", "no money", "not a prospect", "not really", "no not", "don't think I fit", "would you hire", "I am not looking"
- **POSITIVE_INTERESTED (BOOK)**: "happy to chat", "suggest some times", "suggest a time", "let's talk", "book a call", "book an appointment", "feel free to book", "set up a call", "calendar link", "I'd love to connect", "love to connect", "definitely looking for", "open to hearing what", "how can we connect", standalone "Sure." / "Sure!" / "Yes," / "Absolutely" as first words
- **POSITIVE_SOFT (INFO)**: "send me some info", "send more info", "tell me more", "how does it work", "how it works", "piqued my interest", "sounds interesting", "send over the details", "send some links", "additional info", "what's your website", "your website?", "can you let me know the fees", "let me know the fees", "upfront payment", "give me more info", "I'm interested", "I am interested", "send me info", "demo video", "case studies", "examples", "what I am looking for", "that's what I am looking for", "what is the business angle", "looking to charge", "charge for the services", "business model", "percentage split"
- **REFERRAL**: "no longer with" + "contact" or "reach" in same sentence — **BUT exclude "reaching out"** (as in "thanks for reaching out") and "please reach out" (politeness, not referral). Also exclude dead-email redirects to the SAME person at a different address (e.g., "no longer active... please resend to [same_person@new.email]"). Only count as referral when redirecting to a DIFFERENT person.
- **BOUNCE**: "mail delivery failed", "undeliverable", "mailer-daemon", "address not found"
- Everything else → SKIP (not positive)

**⚠️ Keywords that MUST be gated — check context before flagging as positive:**
These substrings are dangerously greedy and will produce false positives if matched blindly:
- `learn more` — only positive if NOT preceded by form-auto language ("check out our website to learn more", "learn more about us"). If the body has auto-responder signals, "learn more" is boilerplate, not interest.
- `price` / `pricing` / `cost` / `fees` — only positive in QUESTION/REQUEST format ("what's your pricing?", "can you let me know the fees?"). Declarative statements about own prices ("my prices are reasonable", "our pricing is competitive") are NOT positive — they're explaining why they don't need help.
- `call` — only positive with positive-intent proximity ("book a call", "hop on a call", "let's jump on a call"). Bare "call" in skeptical context ("before I hop on any calls, is this automated?") is neutral.
- `website` — only positive in question format ("what's your website?"). In form CTAs ("visit our website", "complete this form on our website") it's boilerplate.
- `calendly` / `meeting` — only positive in buyer inquiry context, not in seller counter-pitch. If the body reads like a sales pitch (multiple service offerings, "we offer", "we organize"), the keywords are in the seller's boilerplate, not the buyer's inquiry.

## Manual Correction Edge Cases

| Pattern | Likely Misclassified As | Correct |
|---|---|---|
| "The office is closed for the [holiday]" | soft/referral | OOO |
| "I've officially retired" | soft | OOO |
| "Thank you for reaching out. Can you send me info about X?" | OOO (form_auto triggers) | positive_soft |
| "Thanks for reaching out. This sounds interesting. Give me more info." | OOO | positive_soft |
| "delete whatever AI agent / slop" | referral | hostile |
| "You need to work on your own writing" | referral | hostile |
| "Stop contacting me psycho!" | unsubscribe | hostile (check hostile BEFORE unsub) |
| "Stop [Name] [Signature]" | neutral_question | unsubscribe |
| "What work did you see?" | neutral_question | neutral_question (correct — curiosity, not interest) |
| "No not really" | neutral_question | negative_notfit |
| "I don't think I fit your target profile" | neutral_question | negative_notfit |
| "Read over what you wrote. Would you hire you?" | neutral_question | negative_notfit |
| "Stop Get Outlook for iOS" | neutral_question | unsubscribe (Outlook mobile signature auto-appended) |
| "This is an auto-generated reply. Please give me 2-3 days..." | positive_soft | OOO (auto-responder) |
| "we do pretty well on our own, but demo video / case studies?" | neutral_question | positive_soft (interest masked by mild pushback) |
| "Fuck off and do not contact me again" | neutral_question | hostile |
| **"Thanks for reaching out! This email is no longer active... please resend to [same_person@new.email]"** (July 9, 2026) | referral | **bounce/dead** (same person, different address — NOT a referral to someone else) |
| **Dead-email redirect to SAME person at new address** — "This email is no longer active... please resend to [same_person@new.email]" (July 9, 2026) | referral | **bounce/dead** (same person, different address — NOT a referral to someone else) |
| **OOO with Calendly booking link in signature** — "I'm traveling and will have limited access to email. If you'd like to book a call, use this link: https://calendly.com/..." (July 11, 2026) | positive_interested | **OOO** — "book a call" / "calendar link" matched in auto-reply context. OOO patterns MUST be checked BEFORE positive patterns. Add "traveling" and "will have limited access" to OOO. |
| **Empty reply body after quote stripping** — reply only contains the quoted operator message, no original text (July 11, 2026) | positive_interested (one-word match on operator's quoted text) | **SKIP** — no lead-authored content. After stripping quoted text, if body is empty, skip. |
| **Holiday OOO with "will be OOO"** — "The office is closed... I will be OOO checking email periodically" (July 11, 2026) | positive_referral | **OOO** — "will be OOO" didn't match "i am ooo" pattern. Add "will be ooo" and "i will be ooo" to OOO patterns. |
| **Temp OOO coverage (2-day absence)** — "I am out of the office Thursday and Friday... please contact [colleague]" (July 11, 2026) | positive_referral | **OOO** — the person still works there, just out for 2 days. Contacting a colleague for urgent coverage ≠ referral to a different decision maker. |
| **Vacation OOO with temp coverage** — "I am out of the office until Tuesday... please contact [colleague]" (July 11, 2026) | positive_referral | **OOO** — same as above. Temporary coverage ≠ referral. |
| **Form auto-responder with generic contact fallback** — "We've received your message... you are welcome to contact [person]" with `canned.response` in from address (July 11, 2026) | positive_referral | **OOO** — form auto-responder. Canned "contact [person]" is generic template language, not a personalized referral. |
| **Operator follow-up reply classified as lead reply** (July 11, 2026) | positive_interested/soft | OOO (lead's original reply was an auto-responder; operator followed up later — the latest REPLY was the operator's) |
| **"Thanks for reaching out... your email will be responded to"** (July 9, 2026) | positive_soft | OOO (form auto-responder — `"thanks for"` didn't match `"thank you for"` pattern) |
| **"check out our website to learn more about us" in form auto-responder** (July 11, 2026) | positive_soft | **OOO** — "learn more" keyword matched in form-auto boilerplate. Gate: if body has auto-responder signals ("thank you for reaching out", "we will respond"), "learn more" is NOT positive. |
| **"my prices are reasonable because I moved" (not-fit context)** (July 11, 2026) | positive_soft | **negative_notfit** — "price" keyword matched in declarative statement about own prices. Gate: "price"/"cost"/"fees" only counts as positive when it's a QUESTION about OUR pricing. |
| **"Before I hop on any calls, is this an AI agent campaign?" (skeptical)** (July 11, 2026) | positive_interested | **neutral_question** — "call" keyword matched but context is skeptical/defensive, not booking. |
| **Unsolicited counter-pitch "We publish 300+ articles... we organize 100+ awards" with calendly in signature** (July 11, 2026) | positive_interested | **neutral_question** — prospect is pitching HER service back. "calendly"/"meeting" in seller's boilerplate, not buyer's inquiry. |
| **"I'm at the beach with my family" vacation OOO with "sure" in quoted original** (July 11, 2026) | positive_interested | **OOO** — "beach" vacation not caught by "vacation" pattern. Add "beach" to OOO patterns. |
| **"please complete this form to request a custom proposal" with "website"** (July 11, 2026) | positive_soft | **OOO** — form auto-responder. "website" in CTA context, not question format. |
| **"Not sure if this means you help with sales but that's what I am looking for" (adjacent-service interest)** (July 11, 2026) | neutral_question | **positive_soft** — "what I am looking for" indicates active need, just for a different service than pitched. Adjacent-service interest IS positive. |
| **"Thank you. So what is the business angle? Are you looking to charge for the services and we work out a percentage split?" (July 12, 2026)** | neutral_question | **positive_soft** — pricing/business-model follow-up after operator responded with Calendly + Tony. Second reply after operator engagement = deepened interest. "what is the business angle" and "looking to charge" are pricing-inquiry variants equivalent to "what are the fees". |
| **Standalone "I'm interested" from previously-silent lead — reply arrived AFTER lead was tracked in bulk sweep (July 12, 2026)** | skipped (in tracking) | **positive_soft** — lead had zero replies when ID was tracked in bulk sweep (July 11). Reply arrived after tracking with just "I'm interested" as the entire body. Caught because `last_reply_time` was more recent than sweep timestamp. Always check reply recency before trusting tracking. |

## Live Instance

- **Campaign**: PR Agencies - SpeakerAgent v2 (#3577260) — 4,512 leads, ACTIVE
- **Slack**: C0AFU5EH56X (#speakeragent-ai)
- **Cron**: `06848dd70c52` — every 30 min (`*/30 * * * *`)
- **Dedup file**: `/tmp/speakeragent_posted_ids.json`
- **Deliver**: `local` (posts go to Slack via send_message, cron response stays local)

## Pitfalls

- Master inbox paginates at 20 per page. Iterate `--offset 0 20 40 ...` until empty or ~200 deep.
- `Instantly leads messages --lead-id` requires `email_lead_id` from inbox, NOT `email_lead_map_id`. Using the wrong ID returns `{"history": []}` silently.
- Large campaign lead lists (4,512 leads) can cause JSON parse errors when pulling 100 at a time. Use smaller page sizes (20-50) or filter by specific lead IDs.
- Always seed the dedup file before first cron run so existing positives aren't reposted.
- **⚠️ Verify the tracking file against the skill's campaign table after each sweep.** On July 9, 2026, `/tmp/speakeragent_posted_ids.json` had 34 IDs — all from inbox page 0. Scanning pages 20-100 found 3 known positives (Ron, Ben Bloch, Spark) that were in the skill's campaign table but missing from the tracking file. These were identified in the July 8 sweep but never added to the file. After any deep-page monitoring run, verify: are all positives listed in `Instantly-cold-email`'s campaign table present in the tracking file?
- **⚠️ TRACKING FILE BLIND SPOT: posted_ids tracks lead IDs, NOT reply timestamps — new replies from already-tracked leads get skipped.** A lead can be in `/tmp/speakeragent_posted_ids.json` from a prior bulk sweep or classification, but have a genuinely NEW reply arrive later. Example: Kyle Wolfe (kyle@kylewolfemedia.com, #3577260) had his ID tracked on July 11 during the 148-lead sweep, but his "I'm interested" reply arrived July 12 at 00:58 UTC — AFTER the tracking. The `posted_ids` skip rule would have silently dropped this positive. **Fix:** Before trusting the tracking file, check `last_reply_time` on all entries. If any already-tracked lead has a `last_reply_time` more recent than the last cron run (or more recent than when they were first posted), fetch their message history and check if there's a genuinely new REPLY message (new `message_id`, not just updated `last_reply_time`). Only skip tracked leads whose last reply timestamp predates the previous sweep.
- **⚠️ Cold-start detection — posted_ids file may be nearly empty after a reset.** On July 11, 2026, the tracking file had only 5 entries after a prior process wrote metadata keys (`"posted_ids"`, `"last_run"`) alongside numeric IDs. When posted_ids has fewer than 10% of expected entries (e.g., <15 for a campaign with 148 known entries), treat this as a cold-start condition. The parser must handle both formats: a pure list `[id1, id2, ...]` and a mixed list containing string metadata keys. After a reset, seed the file with all previously identified positive lead IDs from the skill's campaign table to avoid mass re-processing. Format: store ONLY numeric IDs, no metadata strings — `[4102212564, 4102213724, ...]`.
- The classifier script (`scripts/classify.py`) has ~30% error rate. For real-time monitoring, use inline rules instead.
- Extract reply-only text by splitting on quote markers (`On ... wrote:`, `-----Original Message-----`, `Sent from my iPhone`) before checking one-word agreements.
- **⚠️ Deep pages contain unprocessed replies from launch bursts.** On campaign #3577260 (July 2026), pages 4-7 (offsets 80-160) contained ~38 replies from the July 1-2 launch that were never processed by the daemon's 1-minute cron. Among them: 2 positives (Ron "book an appointment", Spark "Tell me more") that sat unhandled for 7 days. Always paginate deep enough to cover the launch window — replies cluster near the campaign start date, and the daemon can't keep up with burst volume. **Full-sweep paginate at least to offset 180 (10 pages) for campaigns with 4,500+ leads. Confirmed July 11, 2026: ~148 #3577260 entries across 10 pages (offsets 0-180), each page ~20 entries. Page 200+ may be empty.**
- **Skip generic emails on first pass** — `info@`, `support@`, `admin@`, `press@`, `contact@`, `hello@`, `help@`, `podcast@`, `hi@` are 99% auto-responders/unsubscribes. Classify them only after all individual emails are checked, and only if time permits.
- **"Please give me [timeframe]" is NOT positive_soft** — the pattern `"please give me"` triggers on auto-responders asking for patience ("please give me 2-3 business days"). Gate: if "please give me" is followed by time-related words, skip.
- **⚠️ Operator replies fool the classifier — filter by domain FIRST.** When an operator has replied to a lead (e.g., acknowledging their OOO or following up after vacation), the latest REPLY message in the history is the OPERATOR'S reply, not the lead's. Example: Lynn (lynn@pkpublicrelations.com) replied with an OOO auto-reply on July 1, our operator followed up on July 6 asking about the guest idea — the July 6 REPLY was classified as `positive_interested` instead of the OOO. **Fix:** Before classification, skip all REPLY messages whose `message_id` contains our sending domains (`speakeragent.ai`, `horizonedgenv.info`, `successcrestco.info`, `growthmapar.info`, `progressdeskks.info`, `useaiintegraterz.com`, `joinaiintegraterz.com`, `meetaiintegraterz.com`). Classify only the remaining REPLY messages, and use the EARLIEST (original) lead reply, not the latest.
- **"Thanks for reaching out" ≠ "thank you for reaching out"** — form auto-responder patterns must match both `"thank you for"` and `"thanks for"`. Segal Communications replied with "Thanks for reaching out... your email will be responded to by a member of the team" — correctly an OOO/auto-responder, but classified as `positive_soft` because `"thanks for reaching out"` didn't match `"thank you for reaching out"`. **Fix:** OOO patterns include `"thanks for reaching out"` and `"thanks for your email"` (without follow-up interest signals).
- **⚠️ Silent delivery failure — bot not in channel.** When the cron uses `send_message` to push to a Slack channel the bot hasn't been invited to, it fails silently. The dedup file grows (lead IDs get tracked) but no messages reach the channel. There is no error surfaced to the operator — the cron run status shows `ok` and the positives file is empty. **Fix (July 9, 2026):** Run `send_message(action='list')` as a pre-flight check. If the target channel doesn't appear, the bot needs to be added. The user must invite `@Hermes` to the channel. Until then, the cron will silently drop all positives.