# Cross-Campaign Inbox Monitoring Workflow

This reference documents the full cross-campaign inbox monitoring sweep used by the 30-minute cron job. It's the safety net for campaigns not covered by the 1-minute auto-reply daemon (i.e., any campaign not in `CAMPAIGN_CONTEXT`).

**Current state (Jul 15, 2026):** 5 campaigns are missing from daemon CAMPAIGN_CONTEXT — #3577260, #3520103, #3607306, #3617053, #3639259. The cron sweep is the ONLY monitoring for these campaigns.

## Workflow

### 1. Pull inbox pages (pages 0-1 minimum, more for deep scans)

```bash
export Instantly_API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2)
export PATH=/opt/data/home/.local/bin:$PATH

# Page 0
Instantly inbox replies --format json > /tmp/inbox_page0.json

# Page 1
echo '{"offset":20,"limit":20}' > /tmp/iq_p1.json
Instantly inbox replies --from-json /tmp/iq_p1.json --format json > /tmp/inbox_page1.json
```

### 2. Classify entries by campaign and email prefix

Auto-reply prefixes to skip immediately (no message history pull needed):
```
support@, info@, privacy@, contact@, hello@, admin@, help@, noreply@, no-reply@,
team@, connect@, ask@, consult@, trt@, orders@, staff@, frontdesk@, care@,
press@, media@, podcast@, compliance@
```

**Exception:** `info@` from small-business domains CAN be real. Check domain context before auto-skipping.

### 3. For REAL leads (not auto-reply prefixes), batch-pull message history

Use `&&` chaining for parallel pulls (4 leads per batch, 90-120s timeout):

```bash
Instantly leads messages --campaign-id <CID> --lead-id <LID1> --format json > /tmp/msg_a.json 2>&1 && \
Instantly leads messages --campaign-id <CID> --lead-id <LID2> --format json > /tmp/msg_b.json 2>&1 && \
Instantly leads messages --campaign-id <CID> --lead-id <LID3> --format json > /tmp/msg_c.json 2>&1 && \
Instantly leads messages --campaign-id <CID> --lead-id <LID4> --format json > /tmp/msg_d.json 2>&1
echo "DONE: $?"
```

### 4. Classify replies

For each lead's message history:
1. Extract only REPLY-type messages
2. Strip HTML tags, decode HTML entities (`html.unescape`)
3. Strip quoted original email (quote delimiters: `On .* wrote:`, `\n>`, `From:.*Sent:.*To:.*Subject:`)
4. Include INLINE quote patterns (no `\n` prefix) for collapsed-HTML replies
5. Classify the reply body only (not the quoted original)

Classification order (anti-patterns first):
1. Auto-responder (`addressed within`, `business hours`, `out of office`, `vacation`, etc.)
2. Hostile (`remove me`, `stop emailing`, `do not email`, `report you`)
3. "Not sure" → positive_interested (unless followed by rejection)
4. Negative/polite decline (`not interested`, `no thanks`, `I'll pass`, `not a fit`)
5. Positive (`yes`, `sure`, `send info`, `tell me more`, `book`, `schedule`, `calendar`)

### 5. Check `our_replies_after`

For the LAST reply from each lead, count SENT messages with timestamp after the reply:
- Skip standard sequence emails (seq #1, 2, 3) UNLESS they contain reply-like body text (`case study`, `report here`, `here it is`, `plan here`, `circling back`, `love the quick`, `love that`, `got it`)
- `our_replies_after > 0` → already handled, skip
- `our_replies_after == 0` → unhandled, flag to operator

**⚠️ Watch for mislabeled SENT-as-REPLY:** Instantly's `type` field can label operator outbound messages as `REPLY` when a thread is forwarded. Body content check is the signal — if a "REPLY" message body reads like an outbound ("Hi Mike, I wanted to follow up..."), it's actually a SENT. Do NOT count it as a lead reply. Confirmed: Mike Billoni (#3577260, Jul 15 2026) — Tony's follow-up appeared as REPLY type.

### 6. Report unhandled leads

Flag any lead where:
- Reply is `positive_interested` or `positive_soft`
- `our_replies_after == 0`
- Not in hostile_senders or unsub_senders

## State File Hygiene

After processing, add ALL message IDs to state (not just positives). The state file prevents duplicate processing on subsequent cron runs.

## Campaign-Specific Reply Templates

| Campaign | Template |
|---|---|
| #3577260 PR Agencies | Hardcoded SpeakerAgent (no pricing, no white label, no made-up features) — same as #3316611 |
| #3639259 Podcasters | `references/speakeragent-podcaster-reply-template.md` |
| #3617053 Owned Audiences | `owned-audiences-email-reply` skill (case study + booking link) |
| #3520103 AI Guy | AI operator $10/hr offer context |
| #3607306 AI Guy Coaching | AI operator $10/hr offer context |

## Pitfalls Discovered (Jul 15, 2026)

- **Cross-campaign blind spot:** The cron monitoring previously focused on #3617053 only. Scott Kaier (#3577260, 8 days unhandled) and Sam Frontera (#3577260, 13 days unhandled) were invisible until a full cross-campaign sweep.
- **Inline quote delimiters:** When HTML stripping collapses reply + quoted original onto one line, add `On .* at .* wrote:` (without `\n` prefix) as fallback patterns.
- **Compliance@ is an auto-reply prefix** — add to the auto-reply filter list.
- **Podcast@ is an auto-reply prefix** — same.

## ⚠️ Deep-Funnel Pricing Exception (SpeakerAgent) — Jul 17, 2026

**The "no pricing" rule has a breaking point.** When a lead has been in the funnel for 10+ messages over 2+ weeks and explicitly demands specific numbers — not once, but repeatedly — you MUST give a range. Refusing to provide any pricing at this depth sounds evasive and will lose the lead.

**Spark/Ethan (Campfire Group, #3577260) — the canonical case:**
- 11 messages over 16 days on a COMPLETED campaign
- Thread: "Tell me more" → engagement breakdown → "how do you price?" → framework (no numbers) → **"that's not a number. Please provide me with some numbers"**
- At this point, the lead has invested serious time. They're not tire-kicking — they're doing due diligence before committing to a call.

**The exception template (when a lead demands numbers after 3+ engagements):**
```
For a [single-client / boutique-shop] setup like you described: 
SpeakerAgent typically runs in the $[low]–$[high]/month range. 
That covers the full backend — research, vetting, outreach, and booking. 
The spread depends on how many podcast lanes and how aggressive the outreach cadence.

[Name of ops person] can give you a firm quote in 10 minutes — 
he's seen enough setups to know exactly where [company] lands. 
He's already on this thread.

Want me to have him reach out directly with a custom quote?
```

**Decision points before using:**
- How many messages has the lead sent? (threshold: 3+ engagements from their side)
- Did they explicitly say "that's not a number" or "give me numbers"?
- Has a framework/overview been provided already that they rejected?
- If yes to all three → give a range. Not a firm quote — a range that pushes to the call.
- The range should be wide enough to cover real variance ($1,500–$3,000/month for SpeakerAgent boutique).

**Never give pricing on first or second engagement.** This exception only activates when the lead has repeatedly asked and rejected non-numeric answers.