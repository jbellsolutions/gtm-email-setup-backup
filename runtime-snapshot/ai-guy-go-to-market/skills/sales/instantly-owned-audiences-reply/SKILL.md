---
name: instantly-owned-audiences-reply
description: "Reply to leads who respond to Instantly cold email campaigns. Mirrors owned-audiences-email-reply's Instantly workflow — same classification logic, same reply structure, same tone rules. Current mode: send a vertical-matched case study + booking link instead of building custom plans. Use when an Instantly lead replies with interest, or when new positive replies appear in the Instantly Unibox. Output: a short reply email with case study link and booking CTA. Dormant as of 2026-07-30 — the Owned Audiences / SpeakerAgent reply pipelines stay on Instantly per Justin's migration choice (only the cold-email reply agent moved to Instantly); this is a forward-looking copy for whenever OA-style campaigns run on Instantly too."
---

# Instantly Owned Audiences Email Reply Skill

A lead replied to our cold email. The cold email promised: **"a short version of a partner-backed plan, plus a case study."** Current mode (as of July 13, 2026, on the Instantly side): send a pre-built vertical-matched case study + booking link. Custom plans are suspended — the old plan-building workflow is saved in the `owned-audiences-custom-plan` skill for future use. This applies equally regardless of sending platform.

**Campaign-scoping rule:** on Instantly, this workflow is scoped to specific campaign IDs (Owned Audiences vs. SpeakerAgent vs. PR vs. Solar each use different reply templates — see `owned-audiences-email-reply` for the live Instantly campaign-ID mapping). **No Instantly campaigns exist yet**, so there is no scoping table to give here. When Instantly campaigns launch, build the equivalent table keyed to Instantly campaign IDs before running cross-campaign sweeps — sending an owned-audiences case study reply to a differently-scoped lead is a workflow error regardless of platform.

## Lead Tracking Spreadsheet

See `references/lead-tracking-spreadsheet.md` for the Google Sheets schema (columns: Called 1-5, Booked, Notes/Behaviors), daily cron update workflow, and Composio integration. All OA leads across #3617053, #3652623, and #3652624 tracked in one sheet with campaign tabs sorted by heat.

## What this produces

1. **A reply email** — short, plain text, two sections (custom top + locked bottom). Contains a case study link and booking CTA.
2. **Optionally: a follow-up email** — for leads from prior weeks who replied but never got a response. Same template, "circling back" framing.
3. **Optionally: a flyback email** — for leads who got a low-quality AI plan and called it out. Own the mistake, offer a real call. See `references/flyback-template.md`.

## Tracking Spreadsheet

All Owned Audiences leads are tracked in a Google Sheet updated daily via cron. The sheet has columns for Called 1-5, Booked, and behavior tracking. See `references/tracking-spreadsheet.md` for the full schema, heat scoring, daily update logic, and Composio integration.

## Config

```yaml
site_link: https://aiintegraterz.com/stop-renting
booking_link: https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery
```

## Case Study Library

Match the lead's vertical to the closest case study. All URLs are permanent here.now links.

| Vertical | Case Study URL |
|---|---|
| Men's health / TRT / hormone clinics | https://aiintegraterz.com/case-studies/mens-health.pdf |
| Men's coaching / fitness coaching | https://aiintegraterz.com/case-studies/mens-coaching.pdf |
| Marketing agencies | https://aiintegraterz.com/case-studies/marketing-agency.pdf |
| Solar companies | https://aiintegraterz.com/case-studies/solar.pdf |
| AI agencies / AI automation | https://aiintegraterz.com/case-studies/ai-agency.pdf |
| MCA / alternative lending | https://aiintegraterz.com/case-studies/mca.pdf |
| Recruiting / staffing agencies (general) | https://aiintegraterz.com/case-studies/recruiting.pdf |
| Recruiting — master / full-service | https://aiintegraterz.com/case-studies/recruiting-master.pdf |
| Recruiting — exec search | https://aiintegraterz.com/case-studies/exec-search.pdf |
| Recruiting — IT staffing | https://aiintegraterz.com/case-studies/it-staffing.pdf |
| HVAC / home services | https://aiintegraterz.com/case-studies/hvac.pdf |

If a lead's vertical doesn't match any case study, pick the closest one and flag it to the operator. New case studies are hosted on aiintegraterz.com/case-studies/ — when adding a new one, add it to the table above.

## The workflow

### STEP -1 — Pre-run: Instantly API health check (MANDATORY — same discipline as Instantly)

**⚠️ Before any monitoring run, verify the Instantly API is accessible before trusting a "0 scanned" result.** The Instantly side of this operation learned this lesson the hard way — see `owned-audiences-email-reply` STEP -1 for the full incident history (37+ consecutive outage detections across "Plan expired!" and "Invalid API Key" failure modes, both producing a false "Scanned: 0 inbox entries" all-clear instead of a hard error). The general pattern applies regardless of platform: **a monitoring pipeline that returns "0 found" on an auth failure is indistinguishable from a genuinely empty inbox unless it checks auth explicitly.**

**Instantly health check:**
```bash
curl -s -o /dev/null -w "%{http_code}" "https://api.instantly.ai/api/v2/campaigns" \
  -H "Authorization: Bearer $INSTANTLY_API_KEY"
```
200 → healthy, proceed. 401/403 → key invalid/revoked, stop and report — do not trust any "0 scanned" result from this run. Anything else → assume down, report and skip.

Instantly's specific failure-mode strings (equivalent to Instantly's `"Plan expired!"` / `"Invalid API Key"`) are unverified — this pipeline hasn't run against a real outage yet. When building the actual `instantly_owned_audiences_pipeline.py` (not yet built), give it this same health check as its first step, unlike the Instantly pipeline where the check was bolted on after 9+ silent-failure incidents — don't repeat that gap.

**Part B (Cal.com pre-call reports) is entirely independent of the sending platform** — see below, unaffected by Instantly/Instantly API status either way.

**Full recovery procedure once a real Instantly outage occurs:** document it the same way `owned-audiences-email-reply` → `references/Instantly-api-outage-log.md` does — pattern + recovery steps in the SKILL.md, running day-by-day log in a reference file.

**Dashboard runs independent of the sending-platform API:** `owned_audiences_dashboard.py` (once forked for Instantly) should read only its own state file — no live API calls — same design as the Instantly version. During an outage, the dashboard still produces a full state snapshot **provided the state file still holds prior-run data.** Run it after the health check fails so the operator still gets a state report.

**⚠️ Known failure mode from the Instantly side, worth designing around from day one:** during an extended outage there, the state file was observed reset to all-zeros rather than staying stale-but-populated — see `owned-audiences-email-reply` for the full incident. A "0 leads" dashboard output during an outage can mean "state wiped," not "system empty." If building the Instantly version, cross-reference against the last known-good snapshot before reporting lead counts, and skip the dashboard entirely (report only Part B + outage status) if the state file is empty AND the API is down.

**⚠️ Dashboard display mismatch — `plan_built` leads shown as "Replied — awaiting response" (Jul 28, 2026):** The dashboard lists leads with `plan_built` status (already handled — custom plan built and sent) under the "REPLIED — AWAITING RESPONSE" section. This is misleading: it makes already-handled leads look like they need action. The actual `replied` status leads (genuinely awaiting action) are a DIFFERENT set. When reading the dashboard output, cross-reference each lead against the state file to check their actual `status` field:
- `plan_built` = already handled, no action needed (dashboard shows them as "replied" — ignore)
- `replied` = may need action (check `notes` field — if notes say "handled" or "case study sent," they're done)
- `awaiting_followup` = genuinely awaiting action

**⚠️ Leads with status `replied` but no handling notes — potential unhandled positives (Jul 28, 2026):** When the Instantly API is down, you cannot pull message history to verify whether a reply was handled. Some leads in the state file have `status: replied` with a `positive_interested` or `positive_soft` classification but NO `notes` field indicating a case study or plan was sent. These are potential unhandled positives. Flag them in the report as "⚠️ Potential unhandled — verify when API restored." Example: Angelina Laforteza (moreinfo@embermedicalservices.com, Ember Medical Services) — `positive_interested`, detected Jul 17, no notes. Cannot verify whether a case study was sent while API is down.

### Part B — Cal.com API for Pre-Call Reports (runs independently when Instantly is down)

**⚠️ Cal.com API v2 status enum pitfall (Jul 25, 2026):** The v2 bookings endpoint uses `status=upcoming` (NOT `status=accepted`). Using `status=accepted` returns `BadRequestException` with the message `"Invalid status. Allowed are upcoming, recurring, past, cancelled, unconfirmed"`. Always query with `status=upcoming`:

```bash
# Correct:
curl -s "https://api.cal.com/v2/bookings?status=upcoming&sortStart=asc&take=20" \
  -H "Authorization: Bearer $CALCOM_API_KEY" \
  -H "cal-api-version: 2024-08-13"
```

**⚠️ Cal.com API v2 response shape (Jul 27, 2026 correction):** The v2 bookings response is `{"status":"success","data":[<booking objects>]}` — a **dict** with `status` and `data` keys, where `data` is the list of bookings. It is NOT a bare list at the top level (earlier note was wrong — confirmed Jul 27 by actual API response). Defensive parse that handles all observed shapes:
```python
d = json.loads(r.stdout)
bookings = d if isinstance(d, list) else (
    d.get('data', {}).get('bookings', []) if isinstance(d.get('data'), dict)
    else d.get('data', [])
)
```
This works because `isinstance(d, list)` is False (it's a dict), `isinstance(d.get('data'), dict)` is False (`data` is a list), so it falls through to `d.get('data', [])` which returns the booking list. **If writing a fresh script, just use `d.get('data', [])` directly** — the nested `.get('bookings')` branch crashes with `AttributeError: 'list' object has no attribute 'get'` on the actual response shape.
Per-booking fields (v2): `id`, `uid`, `title`, `start` (ISO, the start time — NOT `startTime`), `end`, `duration`, `status`, `hosts` (list of {id, name, email, timeZone}), `attendees` (list of {name, email, timeZone}), `meetingUrl`, `eventTypeId`, `eventType.slug`. Attendee name/email live in `attendees[0]`, NOT in a top-level `responses` dict. Title format: `"<Event Name> between <Host> and <Attendee>"` — the attendee name is also embedded in the title string.

**⚠️ Internal-meeting filtering for pre-call cross-check (Jul 27, 2026 update):** Cal.com returns ALL upcoming bookings, including internal staff syncs. Before cross-referencing against pre-call reports, filter out:
- "Customer Support Sync" — host `evan@Instantly` (Instantly support, not a client)
- "30 Min Meeting" where `justin@usingaitoscale.com` is the attendee AND the host is also internal staff — BUT verify the host email first. Some "30 Min Meeting" bookings are real peer/partnership calls where Justin is the attendee (e.g., Binoy Perera/AgentMail, Jul 27 2026 — host `binoy@agentmail.cc`, a real external partner). **Filter rule:** only skip "30 Min Meeting" if the host is a known internal address; keep it if the host is external.
Keep "AI Integraterz Gameplan Session," "Power Partnerships" / "SpeakerAgent" bookings — those are client/lead calls. Also keep "30 Min Meeting" bookings with external hosts — those are peer/partnership meetings that need pre-call reports too.

**⚠️ Security scan blocks `curl | python3` pipe-to-interpreter.** Write a Python script to disk that calls curl via `subprocess.run()`, then run the script. The API key is in `/opt/data/.env` as `CALCOM_API_KEY`. Use `line.startswith('CALCOM_API_KEY=')` line-by-line parsing to avoid the SQL TRUNCATE false positive from `.env`-file `.split()` patterns.

**⚠️ `cal_bookings.json` snapshot can be empty/stale.** Always fall back to the live Cal.com REST API as primary source. The snapshot file is a supplement only.

**Pre-call report cross-check workflow:**
1. Query live Cal.com API for upcoming bookings
2. List existing pre-call reports: `ls /opt/data/clients/*/pre-call-report.md`
3. Cross-reference: any booking without a report → generate one via `pre-call-report` skill
4. Skip internal meetings (Customer Support Sync, "30 Min Meeting" between operator and staff) — only generate reports for client/lead bookings (AI Integraterz Gameplan, Power Partnerships, SpeakerAgent)
5. Check existing report headers for stale dates — refresh if the call is within 24h and the report predates the booking confirmation

**Automated cross-check:** `python3 scripts/cal_cross_check.py` in this skill's bundle does the full v2-API parse + internal-meeting filter + on-disk report listing in a single run. Use it in cron sessions to quickly identify missing/stale reports without hand-writing the Cal.com API + glob logic each time. Handles the bare-list response shape, `status=upcoming` enum, and attendee-info-in-`attendees[0]` field layout.

**✅ `cal_cross_check.py` fixed (Jul 28, 2026):** The script now reads pre-call report headers to fuzzy-match attendee names rather than relying on directory slugs (which are company names, not person names). Falls back to directory-name matching if header parsing fails. No more false "NO REPORT" flags for bookings that already have reports under company-named directories.

### STEP 0 — Check if already handled (monitoring cron safety net)

**Before drafting anything**, check whether the lead's reply has already been handled. Pull message history via `GET /api/v2/emails` filtered to the thread (exact filter mechanism unverified — see `instantly-cold-email`'s "Unverified" list). If the history contains a SENT message AFTER the reply's timestamp that looks like a reply (starts with "Thanks for the reply", "Thanks — here it is", etc.) → the lead was already handled by a previous cron run. Skip it and note "already handled."

The key signal: any SENT message with `time` after the REPLY's `time` whose body matches a human reply pattern. **State-file membership alone does NOT confirm handling.** The daemon marks message IDs in state when *scanned*, not when *replied to*. 

**Human reply detection patterns (keep expanding as new variants appear):**
- Case study template: "thanks for the reply", "thanks — here it is", "check out the report", "book in some time"
- Custom plan variant: "here's exactly what I promised", "built out a plan", "here's your custom"
- Explanation-first variant: "in a nutshell", "we work hand-in-hand", "as a partner in the backend"
- Operator follow-up: "wanted to follow up", "hop on a quick call", "circling back"
- SpeakerAgent reply: "speakeragent.ai", "a platform that connects podcast hosts"
- Any SENT with `email_seq_number` that is NOT 1, 2, or 3 (seq=`?` or seq>3 is always a human reply)

**⚠️ `email_seq_number` can be `"?"` (string) on forwarded/operator replies.** Always handle non-numeric seq values as human replies.

If a message ID is in state but `our_replies_after = 0` (no SENT reply after the REPLY timestamp), the lead was scanned but never acted upon. Surface these as ⚠️ "Scanned — Still Unhandled" and process them as new. **July 13, 2026:** Tony Berlin (PR campaign #3577260) — message ID in state, `our_replies_after=0`, 2+ hours stale. **Resolved Jul 14 2:34 AM ET:** operator sent reply "No, we don't charge a fee for referrals."

**July 17, 2026:** Jodi Fleisig (#3577260) — daemon replied within 14 min with "In a nutshell, we work hand-in-hand with you as a partner in the backend to help you fulfill all your client's needs for podcast bookings..." The original classifier missed this as a human reply because "in a nutshell" wasn't in the detection patterns. Pattern now added.

### STEP 1 — Identify the lead and vertical

Extract: lead name, email, niche/vertical from the campaign or reply context. Determine which case study matches their vertical.

### STEP 2 — Draft the reply

Every reply follows a fixed two-section structure (see `references/reply-emails.md` for exact wording and examples):

**TOP section — custom per lead:**

1. **Opener + case study link on SAME line.** Acknowledge what the lead specifically said — reference their words, don't just say "here it is." Use HTML <a> tags for the link. The display text is the URL without https://.
   - "Ask and ye shall receive. Here you go --> <a href=\"...\">aiintegraterz.com/case-studies/...</a>"
   - "You got it. Here you go --> ..."
   - "Love the quick yes. Here you go --> ..."
   - "Right on. Here you go --> ..."

2. **Blank line, then one sentence results hook** — most relevant stat from the case study.

3. **Blank line, then** `<a href="{case_study_url}">Check out the report here</a>` — HTML hyperlink on its own line. The anchor text is ALWAYS exactly "Check out the report here." Do NOT attach any PDF.

**⚠️ TONE RULES (Justin, July 15 2026) — these override everything above:**

All replies — whether warm-yes, follow-up, or flyback — must follow these tone rules. Justin's actual reply examples are the template. Violations cause hostile escalations and lost bookings.

**BANNED PHRASES (never use, ever):**
- "No rush" / "No pressure" / "When you're ready" / "The door's open" — passive language kills urgency
- "Thank you for the reply" / "Thanks for the reply" / "Thanks for getting back" — makes us sound grateful they bothered
- "Grab some time" — too casual, implies optional
- "If you're interested" / "When it makes sense" — invites them to defer

**REQUIRED TONE:**
- Create urgency: "We're here now," "the window is perfect," "jump on right away," "let's get this moving"
- Direct commands, not suggestions: "Go book in a time now" → NOT "grab some time" or "feel free to book"
- Push to next step immediately: every reply must end with a clear booking directive
- Confident, not deferential: we're offering something valuable, not asking for a favor

**Greeting rules:**
- "Hey {Name} — love the quick yes. Here it is." ✓ (warm yes replies)
- "Hey {Name} — love that. Here it is." ✓ (enthusiastic replies)
- "Hey {Name} — thanks for the reply. Here it is." ✗ (BANNED — "thanks for the reply" kills urgency)
- Instead, for neutral replies: "Hey {Name} — got it. Here it is." or similar no-thanks version

**The two-part structure for second-stage replies (after plan/case study sent, lead says they love it):**
```
Hey {Name} — love that. We're here now and the window is perfect with everything shifting in {industry}. Go book in a time now that works for you with Justin our founder. He'll build out a full system and come to the call with ideas you can jump on right away. <a href="{booking_link}">Here's the link</a>

{SenderPersona}
<a href="{site_link}">More on the approach</a>
```

**BOTTOM section — locked template (verbatim, DO NOT EDIT):**
```
When we take this on, we build a complete custom plan for you at no charge — your partner map, your voices, your shows — and we'll review it together live on a call so you know exactly what it means and how to use it.

<a href="{booking_link}">Book in some time with our founder here</a>

{SenderPersona}
<a href="{site_link}">More on the approach</a>
```

- `{booking_link}` and `{site_link}` are the only variables — everything else is verbatim.
- All links use HTML `<a>` tags. Display text is URL without `https://`.
- `{SenderPersona}` is the name from the `from` field of the original sent email (e.g., Willow, Bella, Anna, Penelope) — NOT Justin.

### STEP 3 — For follow-ups (prior week leads)

Use the same template with a different TOP section — "circling back" framing:

> Circling back — last week I mentioned a case study of what this looks like for another {vertical descriptor}.
>
> <a href="{case_study_url}">{case_study_display}</a>
>
> {one-sentence results hook}
>
> <a href="{case_study_url}">Check out the report here</a>
>
> {locked bottom template unchanged}

### STEP 4 — Batch mode

When handling multiple replies at once:
1. Pull all replied leads from campaign statistics via `GET /api/v2/emails` / `GET /api/v2/campaigns/analytics`
2. Filter out auto-replies (reply time within 30s of send = OOO/bounce)
3. Separate into: new replies (today) vs. follow-ups (prior days not yet handled)
4. **Check what each lead was promised.** Read the original `email_message` from campaign statistics. If the cold email promised them a specific custom plan for their business (e.g. "a short version of the system for [business], plus a case study"), you MUST deliver both — a custom plan AND the case study. If it only promised a case study, case-study-only is fine. Leads who were promised something specific are testing whether you deliver. Do NOT send case-study-only to a lead who was promised a custom plan.
5. For leads needing custom plans: build a simplified one-page HTML plan (business name, partner map categories, influencer types, podcast types, booking CTA) and publish to here.now. See `references/custom-plan-template.md` for the HTML template.
6. Draft all emails with the matching case study per vertical, plus custom plan links where promised
7. Return the full batch to the operator, or send via the Instantly reply endpoint (see Sending Replies below)

### STEP 5 — QC Gate (MANDATORY before any send)

**⚠️ DO NOT SEND without passing this gate. This is non-negotiable as of July 20, 2026.**

Before calling Instantly to send, run the draft through the Charm QC Gate:

```
skill_view(name='charm-qc-gate')
```

The QC gate checks three categories:
1. **Formatting** — blank lines, link structure, visual layout
2. **Language & Tone** — zero banned words/phrases, confident tone, urgency
3. **Grammar & Mechanics** — typos, punctuation, casing, persona name

Three possible verdicts:
- **✅ PASS** → proceed to STEP 6 (send)
- **⚠️ PASS WITH FIXES** → minor corrections made, proceed to send
- **❌ FAIL** → rewrite the problematic sections and re-verify — DO NOT send until clean PASS

If FAIL: fix the draft, re-run the gate. Never skip the gate because "it's just one email" or "we're in a hurry." Every email sent without QC erodes sender reputation.

### STEP 6 — Sending Replies

Use `POST /api/v2/emails/reply` (see `instantly-cold-email`'s "Auto-Reply Recipe" for the verified request shape):

```python
import json, os, urllib.request

payload = {
    "reply_to_uuid": "uuid-of-the-email-being-replied-to",
    "body": {"text": "Email body here"}   # exact body field name unverified — confirm on first real send
}
req = urllib.request.Request(
    "https://api.instantly.ai/api/v2/emails/reply",
    data=json.dumps(payload).encode(),
    headers={"Authorization": f"Bearer {os.environ['INSTANTLY_API_KEY']}", "Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    print(json.load(resp))
```

Not yet exercised against a real send — no mailboxes connected. Confirm the payload shape and response format on first real use, same as noted in `instantly-cold-email`.

## ⚠️ FORMATTING QA GATE — MANDATORY BEFORE EVERY SEND

**This gate is non-negotiable. If ANY check fails, DO NOT send. Fix the formatting first.**

Every reply email MUST have exactly this structure with blank lines between every section. The email body must render as distinct paragraphs, not one wall of text:

```
[Line 1] Opener + case study link on SAME line
[Line 2] (blank — this is the empty line between sections)
[Line 3] One-sentence results hook
[Line 4] (blank)
[Line 5] <a href="{case_study_url}">Check out the report here</a>
[Line 6] (blank)
[Line 7] When we take this on, we build a complete custom plan for you at no charge — your partner map, your voices, your shows — and we'll review it together live on a call so you know exactly what it means and how to use it.
[Line 8] (blank)
[Line 9] <a href="{booking_link}">Book in some time with our founder here</a>
[Line 10] (blank)
[Line 11] {SenderPersona}
[Line 12] <a href="{site_link}">More on the approach</a>
```

### Formatting checklist (every send):

- [ ] **Blank lines present** — count them. There must be exactly 5 blank lines in the email body, separating the 6 content sections. If the email body has 0 blank lines, it will render as one blob — STOP AND FIX.
- [ ] **No collapsed paragraphs** — every section is on its own line with a blank line above and below (except first/last). The JSON payload must use `\n\n` (double newline) between sections, NOT single `\n`.
- [ ] **Visual preview passed** — before sending, render the email body to a temp file and visually verify: distinct paragraphs, links on their own lines where specified, no text running together.
- [ ] **Opener + link on SAME LINE** — "Here you go --> <a href=...>display</a>" must be one continuous line. The link does NOT go on a new line.
- [ ] **"Check out the report here" is a link, NOT bare text** — it must be wrapped in `<a href="...">` tags. It must NOT have a colon or any punctuation after it.

### If formatting is broken (July 20, 2026 incident — Jeff reply sent as one blob):

The most common failure mode (confirmed on Instantly, applies to any JSON-payload API including Instantly): the API receives the JSON with `\\n` (escaped single newline) instead of `\\n\\n` (escaped double newline), and the email renders as one continuous paragraph.

**Fix:** Always double-check the `email_body` in the JSON payload. Count the `\\n` sequences — there should be 5 pairs of `\\n\\n` between the 6 content sections. If you see a wall of text with no blank lines in the preview, the newlines are wrong.

### How to verify before sending:

```bash
# Write the email body to a temp file and check visually
echo "EMAIL_BODY_HERE" > /tmp/reply_preview.txt
cat -A /tmp/reply_preview.txt  # shows $ for line endings, confirms blank lines
wc -l /tmp/reply_preview.txt   # should be ~12 lines
```

### Quality gate

- [ ] Correct case study matched to vertical
- [ ] Original cold email checked — if it promised a custom plan, one was built and linked
- [ ] ⚠️ ALL links use HTML <a href="URL">display</a> tags — NEVER bare URLs (they won't be clickable in email)
- [ ] Case study display text is URL without https:// (e.g., "aiintegraterz.com/case-studies/mens-health.pdf")
- [ ] Case study link anchor text is "Check out the report here" exactly (not "here," "check it out here," etc.). Custom plan link anchor text is "check out your plan here."
- [ ] Bottom template verbatim (did not edit the locked paragraph)
- [ ] Signed as sender persona (not Justin)
- [ ] Opener acknowledges what the lead specifically said — references their words, not "Hey {Name} — here it is"
- [ ] ⚠️ Persona matches the FROM address's domain — cross-check against the domain-persona mapping table below. The sign-off name MUST match the persona whose email account is actually sending. Kylie's July 13 reply was sent from `natalie@horizonvistaky.info` but signed "Willow" — wrong.
- [ ] Booking link and site link present and using HTML <a> tags
- [ ] No echoing the lead's exact words in opener
- [ ] Zero banned words: unlock, 10x, synergy, leverage, innovative, cutting-edge, solution, game-changer, transform, revolutionize, scale, disrupt, guaranteed

### Pitfalls

### "Thank you" followed by a rejection is NOT positive — read past the first word
The word "Thank you" at the start of a reply body triggers positive classification, but it's frequently followed by a polite rejection. **Read the full reply body before classifying.** Key rejection patterns that follow "Thank you":

- "Thank you, [Name]. I am not currently looking for assistance..." (Ppavey, July 13)
- "Thanks for thinking of me. But I must decline." (Mike, July 13)
- "Thank you but no thanks"
- "Thanks, not interested at this time"
- "Appreciate the note but we're good"

**Classification rule:** Strip "Thank you" / "Thanks" from the start AND check the remainder for rejection signals BEFORE classifying as positive. The classifier must see the full reply, not just the opening pleasantry.

**Real incident (July 13, 2026 PM):** Ppavey (ppavey@ttdcoaching.com) replied "Thank you, Hailey. I am not currently looking for assistance. I have a couple of personal things going on..." — clearly negative_notfit. A prior cron run classified it as positive_interested based on the opening "Thank you" and sent a full case study reply. The case study ended up in the inbox of someone who explicitly said no. This erodes sender reputation.

### ⚠️ Polite-decline classifier blind spot — "too late" / "already have my own" (Jul 17, 2026)

The `negative_patterns` list in `classify_reply()` requires "not," "no," or "don't" trigger words. Polite declines that omit these — e.g. "Unfortunately it's too late and I've already developed my own systems and plans" — slip through as `neutral`. 

**Added patterns (Jul 17, 2026):**
- `\btoo late\b` — catches "it's too late," "a bit too late"
- `\balready\b.*\b(?:own|have)\b` — catches "already developed my own," "already have my own," "already built my own"

These are safe — they won't match positive replies (no one says "too late, but I'm interested!" or "already have my own, but please send more!"). They're unambiguous polite-decline signals.

**Real incident (July 17, 2026):** Kareem (kareem@kareemelsayed.com, #3617053) replied "Unfortunately it's too late and I've already developed my own systems and plans." — a polite decline after seeing the case study. The pipeline classified it as `neutral` because none of the existing negative patterns matched. Kareem was already tracked in state as `dead/negative_notfit` from a prior manual classification, so no harm — but a brand-new lead with this reply pattern would have been silently skipped, wasting future API calls on every monitoring run.

### Duplicate sends from overlapping cron runs — check for ANY SENT reply, not just case-study template
Two monitoring cron runs within a few hours can both draft and send replies to the same lead. The STEP 0 check must look for ANY SENT message after the REPLY timestamp where the body looks like a human-drafted reply (not an auto-sequence email). This includes:

- The standard case-study template ("Thanks for the reply — here it is...")
- The custom-plan variant ("Thanks for the reply — here's exactly what I promised...")
- The explanation-first variant ("In a nutshell, Kylie, we generate new leads...")
- Any SENT message with `email_seq_number` that is NOT a standard sequence number (1, 2, 3)

**Real incident (July 13, 2026 PM):** Lori (lori@3principlestherapy.com) got TWO replies: a custom-plan reply at 3:27 PM ET (from an earlier cron run) AND a case-study template reply at 5:12 PM ET (from a later cron run). The second run's STEP 0 check only looked for the case-study template pattern — missed the custom-plan variant and sent a duplicate. Both replies were from "Willow" with Calendly links. Pattern to detect: `our_replies_after` count (SENT messages after REPLY time, excluding seq#1/2/3 auto-emails) > 0 = already handled.

### ⚠️ CRITICAL: Never batch-send case studies without per-lead classification

The 5:12 PM ET cron on July 13 sent case study replies to ALL 12+ leads who replied that day — including 5 who had clearly said "no" (Ppavey, Meghan, Mike, Jared, Drd). All 5 were misclassified as `positive_interested` because the classifier checked positive patterns before negative ones. Within hours, 4 of those leads replied with hostility ("stop emailing me", "remove me", "report it", "i said no").

**The cascade pattern:** false-positive classification → case study sent to someone who said no → lead replies hostile → must be added to hostile_senders → sender reputation damage.

**Fix:** ALWAYS run per-lead classification BEFORE any batch send. If even one lead in a batch is `negative_notfit`, don't send to them. The `our_replies_after` check in STEP 0 only tells you if a reply was already sent — not whether it SHOULD have been sent. For batch operations: classify first, filter out negatives/hostiles/OOO, then send only to confirmed positives.

### ⚠️ Message-history calls can timeout on leads with large threads — design for it from the start

On the Instantly side, `leads messages` calls for leads with long threads have been observed timing out at 30s (see `owned-audiences-email-reply` for the incident — a lead who turned out to be the first booking was nearly missed this way). Whether Instantly's `/emails` endpoint has the same slowness under similar conditions is unverified — it hasn't been tested at any real scale. Build the Instantly pipeline with a generous timeout (90-120s) and a skip-and-flag fallback for consistently-slow lookups from the start, rather than discovering the need the same way Instantly did.

### State file stats must include all valid statuses

The state file at `/tmp/owned_audiences_followups.json` tracks leads with a `status` field. The `stats` recalculation function must include ALL status values that appear in the data, or leads with unrecognized statuses disappear from dashboard counts.

**Current valid statuses:** `new`, `awaiting_followup`, `replied`, `booked`, `dead`, `plan_built`

**July 14, 2026:** The stats dict only had `awaiting_followup`, `replied`, `booked`, `dead` — the 5 `plan_built` leads (Kylie, Kareem, Lori, Dawn RWTX, Truwellness) showed as 0 in all categories. Dashboard displayed correctly because it counted by status directly, but the stats summary was misleading. Added `plan_built` to the stats dict.
The reply email greeting must NOT mirror the lead's phrasing. If they replied "Surely," do NOT write "Surely love that" — it reads as parroting. Instead use a simple acknowledgment: "Thanks — here it is," "Got it — here you go," or "Great — here it is."

### Classify reply text ONLY — strip quoted original email FIRST
When a lead replies, their email body includes the full quoted original message (e.g. "On Mon, Jul 13, 2026 at 10:25 AM..."). The quoted section often contains words like "not," "no thanks," "don't need," etc. from our cold email copy. Classifying the FULL body (reply + quoted text) will misclassify positive replies as negative and vice versa.

**Before classification, strip everything after the first quote delimiter:**
```python
import re
def extract_reply_body(full_body):
    # Common quote markers
    patterns = [
        r'\n>', r'\r\n>',  # inline quoting
        r'\nOn .* wrote:', r'\r\nOn .* wrote:',  # Outlook/Apple Mail
        r'\nOn .* at .* wrote:', r'\r\nOn .* at .* wrote:',
        r'\nFrom:.*\nSent:.*\nTo:.*\nSubject:',  # forwarded
    ]
    for pat in patterns:
        m = re.search(pat, full_body)
        if m:
            return full_body[:m.start()].strip()
    return full_body.strip()
```

**Real incident (July 13, 2026 AM):** Dawn King-Dushane replied "Sure. Send me more info, please." — clearly positive. But the quoted original cold email contained "I'm not going to tell you to stop..." and the classifier hit "not" → `negative_notfit`. She already got a reply from a prior cron run, but if she hadn't, this would have been a missed positive. Always classify only the reply portion.

**⚠️ HTML entities break quote-delimiter regex matching (confirmed on Instantly, whose reply bodies are stored as HTML — whether Instantly's are too is unverified, but the fix is cheap insurance either way):** The simple `re.sub(r'<[^>]+>', ' ', body)` strips HTML tags but leaves HTML entities like `&#x202F;` (narrow non-breaking space) and `&nbsp;` intact. These entities appear INSIDE quote delimiters (e.g. `"On Mon, Jul 13, 2026 at 7:58&#x202F;AM Anna Turner wrote:"`) and cause `r'\nOn .* wrote:'` to fail to match — the `.*` stops at the `&` before expanding. The quoted original email remains in the body, and cold-email words like "not" and "stop" contaminate classification.

**Fix — decode HTML entities before stripping quotes:**
```python
import html as _html
# Strip HTML tags first
body = re.sub(r'<[^>]+>', ' ', body)
# Then decode any remaining HTML entities
body = _html.unescape(body)
# Now strip quoted original
body = extract_reply_body(body)
```

**Confirmed July 13 PM:** Dawn RWTX's reply was misclassified as `negative_notfit` because `&#x202F;` in the quote delimiter kept the original email body in scope, and `\bnot\b` matched "I'm not going to tell you..." from the cold email copy. The `html.unescape()` fix resolves this. Dawn's reply was already handled by a prior cron run, but future positives with HTML entities in their reply bodies will be missed without this fix.

### ⚠️ Quote delimiter fails when HTML stripping collapses newlines — "REMOVE!" misclassified as positive

When a reply body is stored as HTML (confirmed for Instantly; unverified for Instantly), stripping tags with `re.sub(r'<[^>]+>', ' ', body)` can collapse the entire message (reply + quoted original) onto a single line. The standard quote-delimiter patterns (`\nOn .* wrote:`) require a newline prefix — they won't match inline quote text like `"REMOVE! On Mon, Jul 13, 2026 at 6:53 AM Emilia Edwards <emilia@...> wrote: ..."`. The entire quoted cold email remains in scope, contaminating classification.

**Fix — add inline (no-newline) quote delimiter patterns as fallback:**
```python
r'On .* at .* wrote:',     # matches without requiring \n
r'On .*, .* wrote:',       # simpler pattern for "On Tue, Jul 14, ... wrote:"
```

**Real incident (July 14, 2026 6:34 PM ET):** Leslie (leslie@drlesliek.com) replied "REMOVE!" from a Gmail client. After HTML stripping: `"REMOVE! On Mon, Jul 13, 2026 at 6:53 AM Emilia Edwards <emilia@growthliftwa.info> wrote: ..."`. The `\nOn .* wrote:` pattern failed to match because everything was on one line. The classifier saw `"\binterested\b"` in the cold email copy and classified Leslie as `positive_interested`. The one-word hostile check (`len(body_words) <= 2`) also missed because the unstripped quoted text added dozens of words. Added inline quote patterns (`On .* at .* wrote:` without `\n` prefix) to `monitor_pipeline.py`.

### "Not sure I understand" is NOT negative — it's a genuine question

Leads who reply "Not sure I understand what you are looking for" or "Not sure what this is about" are asking for clarification, not rejecting the offer. The word "not" triggers negative classification, but the intent is positive. These leads want MORE information — sending a case study is appropriate.

**Classification fix:** "Not sure" phrases → `positive_interested` UNLESS followed by explicit rejection signals like "not interested" or "don't need."

**⚠️ "not sure" vs "not quite sure" — regex adjacency gap (Jul 20, 2026):** The `\bnot sure\b` pattern fails on "not quite sure" or "not entirely sure" because "not" and "sure" aren't adjacent words. Use `\bnot\b.*\bsure\b` as a broader catch. Gina Tucci replied "Yes, please send that over. I'm not quite sure I understand your service fully." — the `\bnot sure\b` regex missed it, classifying her as `neutral_question` when she was clearly positive (she went on to BOOK). Qualified uncertainty with no explicit rejection = positive signal.

**Real incident (July 14, 2026):** Jodie (jodie@vikingalternative.com) replied "Not sure i understand what you are looking for." A prior cron classified her as `negative_notfit` based on the word "not." She was actually asking what we do — a case study reply was correctly sent by a later cron that overrode the classification. Added `not sure` → `positive_interested` bypass to `classify_reply()` in `monitor_pipeline.py`.

### "Sorry. Do I know you?" is neutral confusion — classify as `neutral`, do NOT engage further

Some leads reply "Sorry. Do I know you?" or "Sorry, do we know each other?" after receiving follow-up emails. This is polite bafflement, not hostility and not interest. They don't remember the first email and are genuinely confused about who you are.

**Classification:** `neutral` — do NOT send a case study. If already handled by a prior cron with a "we've emailed before" response, mark as handled and move on. If unhandled, add to state silently. Do not re-engage.

**Real incident (July 14, 2026):** Lisa (lisa@lisagarber.com) replied "Sorry. Do I know you?" to Allison's follow-up email. Allison (via prior cron) replied with "It feels like it. We've emailed back and forth a few times." — already handled, no further action needed.

### ⛔ "Circling back" MUST NOT go to leads whose first reply was hostile/unsubscribe

The pipeline's follow-up logic ("circling back" case study to prior-week positives) has a critical blind spot: **it doesn't check what the lead's original reply said.** If the lead's first reply was "Remove me from your list" or "Stop," sending a "circling back" follow-up days later is a guaranteed hostile trigger.

**Before sending ANY follow-up, check the lead's prior reply classification:**
- If status is `dead` with classification `hostile` or `unsubscribe` → NEVER send follow-up
- If the lead's reply text contains "remove me", "stop", "unsubscribe", "take me off" → classify as hostile immediately
- Only send follow-ups to leads where the prior reply was classified `positive_interested` or `positive_soft`

**Real incident (July 14, 2026 AM):** Nicholle (nicholle@colebeecoaching.com) replied "Remove me from your list" on Jul 10. Pipeline classified her as hostile. But on Jul 13, the "circling back" logic sent her a case study anyway. She replied "And I said stop emailing me" — hostile escalation. The circling-back check only looked at whether the lead had a SENT reply, not whether they had explicitly told us to stop.

**Fix:** The follow-up logic must cross-reference the lead's status in the state file. If `status == "dead"` with `classification in ("hostile", "unsubscribe")`, skip the follow-up entirely and do not re-engage.

### ⚠️ State file entries MUST include email field — missing email breaks deduplication

When adding a lead to the state file, always populate the `email` field. Without it, subsequent cron runs cannot match inbox entries by email address, causing already-classified leads to reappear as "new." The matching logic checks both `lead_id` and `email` — if neither matches, the lead is treated as unprocessed.

**Real incident (July 14, 2026):** Drd (drd@coachinglifestrategies.com, lead_id 4136967049) was in state as `dead/negative_notfit` but lacked an `email` field. The inbox scan saw `drd@coachinglifestrategies.com` as new because `ldata.get('email')` returned None. The lead was already correctly classified — just invisible to the email-based dedup check.

**Fix:** Ensure every lead entry has `email` populated at creation time. When patching existing entries, add missing email fields retroactively.

### ⚠️ State file hygiene — add ALL message IDs, not just positives

After classifying a lead (any classification — positive, negative, hostile, OOO, auto-reply), their message ID MUST be added to `known_reply_message_ids`. If only positives are added, negative/hostile leads will appear as "new" on every subsequent cron run, wasting API calls and risking re-engagement.

**Real incident (July 14, 2026 01:30 AM ET):** 4 leads (Meghan, Andrea, Dhiana, Chris) appeared as "new" in the inbox scan because prior cron runs classified them but never wrote their message IDs to state. All 4 had already been processed (case studies wrongly sent at 21:12 UTC). This created a false "8 new leads" alarm every 30 minutes.

**Fix:** After classification, always append to state:
```python
known_ids.append(msg_id)  # for ALL classifications, not just positives
state['known_reply_message_ids'] = known_ids
```
The `known_reply_message_ids` list should grow with every lead the pipeline touches, regardless of outcome. It's a "seen it" list, not a "handled positives" list.

### Second replies after case study follow-ups — three distinct categories (not all hostile)

The monitoring workflow sends case study replies to positive leads. When those leads reply AGAIN, there are THREE distinct categories — don't treat them all the same:

#### 1. HOSTILE — add to hostile_senders immediately, never re-engage
- "Remove me from your email list" 
- "I said no. Email me again and I will report it."
- "Stop contacting me"
- "Do not email me again"
**Action:** Classify as `hostile`, add to `hostile_senders`, mark `dead`. Never send follow-up. **July 13, 2026:** Fran (pureandmindful.com), Liz (askliz.com), Breathe (thewaythru.com), and Nicholle (colebeecoaching.com) all replied "remove me" / "report it" after receiving case study replies.
**July 14, 2026:** Leslie (drlesliek.com) replied "REMOVE!" — hostile, one-word hostile check caught it after inline quote-delimiter fix.

#### 2. POLITE DECLINE — mark dead, do NOT add to hostile_senders
- "I'm going to pass at this time. Thank you for thinking of me."
- "Thanks for sending this over, but it's not for me right now."
- "Appreciate the info — I'll pass for now."
- "Unfortunately it's too late and I've already developed my own systems and plans." — lead saw the plan/case study and decided it's not needed; polite, not hostile. (Kareem, kareem@kareemelsayed.com, Jul 16 2026: was initially positive — "Sure" → "Where were you three years ago!?!" — then declined after seeing the plan. Marked `negative_notfit`, no re-engagement.)
These are genuinely positive leads who read the case study and politely declined. They are NOT angry — they just decided it wasn't a fit. **Do NOT add to hostile_senders.** Classification: `negative_notfit`, status `dead`. No further engagement.
**Real incident (July 15, 2026):** Shira (shira@shiraraymond.com) replied "Sure" at 11:25 PM ET, got case study at 12:04 AM, then replied again at 12:47 AM: "I'm going to pass at this time. Thank you for thinking of me." — polite decline, not hostile. Marked `dead / negative_notfit` without adding to hostile_senders.

#### 3. FLYBACK — quality complaint about content, not about being contacted
- "I'm not interested thanks, the AI plan is super generic. Please remove me from your mailing list."
These leads were initially positive but are complaining about the **content quality** of what was sent (generic, AI-generated, template, not relevant), NOT about being contacted. This is a **flyback** candidate — own the bad plan, offer a real call. Do NOT add to hostile_senders. See `references/flyback-template.md`.
**Real incident:** Robyn (mindfulnessathletics.com, July 14) said "I'm not interested thanks, the AI plan is super generic. Please remove me from your mailing list." She was initially positive ("Yes please send it over") and her complaint is about quality. Removed from hostile_senders after misclassification.

**Classification decision tree for second replies:**
1. Contains "stop"/"remove me"/"report"/"do not email"/"unsubscribe" → HOSTILE (unless combined with quality complaint, then FLYBACK). **⚠️ Standalone "unsubscribe" (even as the only word) is hostile** — add to `unsub_senders` immediately. Do not classify as `neutral`. Real incident: Eric Edelsberg (eedelsberg@culturefit.com, Jul 16 2026) replied with just "unsubscribe" — classifier missed it as `neutral`, required manual fix.
2. Contains "generic"/"template"/"AI-generated"/"not relevant" → FLYBACK
3. "Pass"/"not for me"/"decline" with "thank you" tone → POLITE DECLINE
4. Asks a question or raises practical concern → GENUINE POSITIVE (handle normally)

**Rare counterexample — genuine positive, just has a practical concern:**
- **⭐ Gina** (beyondthescoreboards.com, July 11-14): first reply "Yes, please send that over" scanned into state but unhandled for 2 days. Belated case study follow-up → she BOOKED an appointment (confirmed Jul 14 01:52 UTC). **First confirmed booking from this campaign.**
- **Kylie** (mymindcoach.com.au, July 13-14): first reply "Sorry Natalie, what are you suggesting?" → case study sent within hours. Second reply: "thank you. I'll consider this and discuss with my partner. All your call times are in the middle of the night for AEST Australia time." — genuinely wants to book, just needs timezone accommodation (auto-reply sent offering early-morning ET slots).

The difference: genuinely positive leads who want the info will engage with the reply, even if belated. The hostile "second replies" come from leads whose first reply was actually negative (misclassified as positive). **A lead who asked a real question or said "send more info" in their first reply is almost certainly in the positive camp**, even if their second reply raises a practical concern (timezone, pricing, timing).

### Auto-replies masquerade as real replies — email-address heuristic catches 90%, but info@ can be real

Inbox monitoring (any platform) surfaces reply entries for support@, info@, privacy@, contact@, hello@, and similar shared inbox addresses. These are NEVER real human replies — they're ZenDesk ticket auto-responders, privacy request confirmations, CSAT surveys, or OOO messages.

**⚠️ Exception: info@, contactus@, AND hello@ addresses CAN be real replies from small businesses.** Everwellusa (info@everwellusa.com) replied "Sure" — a genuine positive from a small clinic using their info@ as the main inbox. Bellobella (contactus@bellobella.com, July 16 2026) replied "Sure, but also some info on your company please" — a weight loss / GLP-1 clinic using contactus@ as their main inbox. **Pamir Sevincel (hello@onetenhundred.vc, Jul 15 2026, #3639259)** replied "What was my podcast about?" — a solo VC/Managing Partner using hello@ as his main inbox. All three are real humans using shared-prefix addresses as primary inboxes because they run small businesses. If the domain is a small business (not SaaS, not enterprise), pull message history to verify before classifying as auto-reply. The body content is the final signal — if it's short, relevant, and contains no auto-responder boilerplate, treat as human.

**Pre-filter by email address BEFORE pulling message history:**
```python
AUTO_REPLY_DOMAINS = ['support@', 'info@', 'privacy@', 'contact@', 'contactus@', 'hello@',
                       'admin@', 'help@', 'noreply@', 'no-reply@', 'team@',
                       'connect@', 'ask@', 'consult@', 'trt@', 'orders@',
                       'staff@', 'frontdesk@', 'care@', 'press@', 'media@', 'podcast@',
                       'compliance@', 'moreinfo@', 'concierge@']
def is_likely_auto_reply(email):
    email_lower = email.lower()
    return any(email_lower.startswith(d) for d in AUTO_REPLY_DOMAINS)
```

This saves 10+ API calls per monitoring run. Pull message history only to confirm (for completeness), but classify as `auto_reply` and add to state immediately.

**Enterprise domain filtering:** For `info@`/`contactus@` exceptions, maintain a list of known enterprise/SaaS domains whose info@ addresses are guaranteed auto-responders. See `references/enterprise-domain-filter.md` for the domain list and filtering logic. **July 17, 2026:** 33 of 60 inbox entries were auto-reply prefixes (55% filter rate). Added `moreinfo@` and `concierge@` to the prefix list after discovering them in the wild.

**July 13, 2026:** 9 of 19 page-0 entries on campaign #3617053 were support@/info@/privacy@/contact@/hello@ — all auto-replies. Only 10 needed actual message history pulls.

### ⚠️ Auto-responder flood after large blasts — SILENT runs are expected, not broken

When a campaign sends to thousands of leads in a single burst, the first 24-72 hours of monitoring will be dominated by ticket-system auto-responders. Support@, info@, contact@, and similar addresses will fill pages 0-2 of the inbox. This is NORMAL — not a monitoring failure and not a sign that real replies are being missed.

**This applies to ALL Owned Audience campaigns, not just #3617053:**
- #3617053 (Coaching): 9,457 leads, sent Jul 14 — tail persists through Jul 18+
- #3652623 (HVAC): ACTIVE since Jul 16 — same auto-responder pattern, same prefix heuristic
- #3652624 (Recruiting & Staffing): ACTIVE since Jul 16 — same pattern, plus high retirement rate (recruiters retiring, on sabbatical, medical leave)

**What to expect:**
- Page 0: 15-20 auto-responders, 0-2 real replies
- Page 1: 10-15 auto-responders, 2-5 real replies (some already handled by prior crons)
- Page 2+: tapering auto-responders as the blast ages

**The cron job is working correctly when:**
- Auto-responders are classified by email prefix and added to state silently
- Already-handled leads are skipped (STEP 0 `our_replies_after` check)
- The run ends in [SILENT] because there are no unhandled positives

**Do NOT:** pull message history for every auto-responder "just to be sure." The email prefix heuristic catches 95%+ — only pull history for `info@` addresses from small-business domains (per the exception above) and for genuinely ambiguous personal addresses. **July 14, 2026:** 20 of 20 page-0 entries and 11 of 20 page-1 entries were auto-responders from the 9,457-lead blast. Only 6 leads across both pages needed message history pulls. **July 14 6PM ET (same-day follow-up):** 41 of 60 entries across 3 pages were auto-reply prefixes — the flood persists through the first 24 hours. Of 17 real leads pulled, 10 were already handled, 6 were hostile/unsub, and 1 was a retirement OOO. Zero new positives found. **July 18, 2026 (3 AM ET):** Cross-campaign sweep of pages 0-1 (40 entries across all campaigns): 21 auto-reply prefixes, 12 already-handled or hostile/unsub, 7 checked via message history — all OOO/retirement/auto-responder. Zero new positives. [SILENT] runs are the expected steady state during the auto-responder wave across all active Owned Audience campaigns. **July 18, 2026 (2 PM ET):** Same-day follow-up sweep of pages 0-1 confirmed same pattern: 21 auto-reply prefixes (55% filter rate), 19 real leads all already in state. Coaching (#3617053) still producing support@/info@/care@ auto-responders 4 days after the 9,457-lead blast. Recruiting (#3652624) elevated retirement/OOO rate confirmed. HVAC (#3652623) tail winding down. Zero new unhandled positives — steady state maintained. Podcaster campaign #3639259: Peter Vera confirmed booking ("Got something on the books for Tuesday. Looking forward to it!").

### ⚠️ Efficiency: batch message history pulls with `&&` chaining

When you have 4-8 real leads to check, pull message histories in parallel batches of 2-4 using `&&` chaining in a single terminal call. This is ~3x faster than sequential individual calls:

```python
# Illustrative — GET /api/v2/emails filter mechanism is unverified (see instantly-cold-email).
# Once confirmed, batch the same way: fire N requests concurrently rather than one at a time.
import concurrent.futures, urllib.request, os

def fetch_thread(thread_id):
    req = urllib.request.Request(
        f"https://api.instantly.ai/api/v2/emails?thread_id={thread_id}",  # param name unverified
        headers={"Authorization": f"Bearer {os.environ['INSTANTLY_API_KEY']}"}
    )
    return urllib.request.urlopen(req, timeout=90).read()

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(fetch_thread, thread_ids))
```

The underlying lesson (batch 2-4 lookups concurrently rather than sequentially — confirmed ~3x faster on Instantly) applies regardless of platform. Use a 90-120s timeout per call until Instantly's actual latency is known.

### ⚠️ Retirement / permanent vacation OOO — classify as `dead`, not `auto_responder`

Some leads reply with a personal retirement or "permanently on vacation" announcement from a named email address (e.g., `denise@drbnaples.com`). These are NOT standard OOO auto-responders — they're human-sent farewell messages. They don't match the email-prefix heuristic because they come from personal addresses.

**Classification:** `dead` with `negative_notfit` — the person is no longer in business and cannot be a lead. Do NOT send a case study or follow-up. Add to state as `dead` with a note about retirement.

**Signal patterns:**
- "I will be on vacation permanently! Retirement."
- "I've retired and am no longer in practice"
- "I have retired from [company]" — non-contracted form, equally common (jc@kindredpartners.com, Jul 16 2026: "Please note that I have retired from Kindred Partners, LLC")
- "I am now retired and don't need your services. Please refrain from contacting me in the future." — explicit retirement + opt-out (Bill Dove, bill@billdove.com, partner CPA campaign #3698110, Jul 22 2026)
- "This isn't your average OOO—I've officially retired" — retirement-with-flair variant (angela@spherion.com, Jul 16 2026: Spherion franchise owner)
- "Permanently closed / retired / no longer seeing clients"
- "no longer with [company]" / "no longer at [company]" — departed, not retired, but same dead-lead outcome

**Classifier patterns to catch these:**
```python
r'\bretired\b|\bretirement\b'                          # retirement announcements
r'\brefrain from contacting\b'                          # explicit opt-out (often paired with retirement)
r'\bno longer (?:with|at)\b'                            # departed from company
r'\bdon\'?t need\b'                                     # "don't need your services"
```

**⚠️ Recruiting campaign (#3652624) has elevated OOO/retirement rates.** Recruiters are often senior professionals — expect sabbaticals, medical leaves, retirements, and departures at 2-3x the rate of coaching/wellness campaigns. This is normal, not a targeting failure. These are all dead leads — classify and move on.

**Real incident (July 14, 2026):** Denise (denise@drbnaples.com, lead_id 4163804171) replied to the cold email with a retirement announcement. The email prefix heuristic missed it (personal address), and the reply wasn't hostile — just permanently unavailable. Classified as `negative_notfit / dead` rather than `auto_responder`.

### ⚠️ Two auto-responder body patterns missed by classifier — "72 business hours" and CSS-only bodies (Jul 15, 2026)

The `classify_reply()` function in `monitor_pipeline.py` has two additional blind spots:

1. **Customer-service auto-responders with timeframes** — e.g. "Thank you for your email. All emails will be addressed within 72 business hours. Take Care." — these contain no OOO keywords and get classified as `neutral`. Added patterns: `\baddressed within\b`, `\bbusiness hours\b`, `\bbusiness days\b`, `\bwe will respond\b`, `\bwe.ll get back\b` → classify as `auto_responder`.
2. **CSS-only / HTML-cruft bodies** — broken auto-replies that strip to just CSS rules (e.g., `table td { border-collapse: collapse; } body[dir=rtl]...`). These have <20 chars of actual readable text and match a regex of only `[\s{};:#.\-\w]+` → classify as `auto_responder`.

**Real incidents (July 15, 2026):** Ann (ann@annkonkolycnm.com, "72 business hours") and Team (care@tryeden.com, CSS cruft) both classified as `neutral` instead of `auto_responder`. Added patterns to `monitor_pipeline.py`.

### ⚠️ "Please contact X@Y.com" redirects — auto-responder, NOT positive (Jul 22, 2026)

Some auto-responders use a polite redirect format: "Please contact engineering@company.com for any engineering requests. This email is not monitored." The `\bplease\b.*\b(?:send|share|forward|email)\b` positive pattern matches this because "please" + "email" are present, falsely classifying it as `positive_interested`.

**Detection signals (any one = auto_responder):**
- Reply latency < 5 seconds from the SENT email
- "This email is not monitored" / "this inbox is not monitored"
- "for any [department] requests" / "for all [department] inquiries"
- The redirect email is a shared/department address (engineering@, sales@, etc.)
- The body has no greeting, no signature, and reads like a server rule

**Fix:** Check for these signals BEFORE running positive interest patterns. If any match, classify as `auto_responder` immediately.

**Real incident (July 22, 2026):** Dave Staley (dstaley@mseaudio.com, #3692104) replied 3 seconds after the SENT email with "Please contact engineering@mseaudio.com for any engineering requests. This email is not monitored." — classified as `positive_interested` because `\bplease\b.*\bemail\b` matched. Corrected to `auto_responder`.

The `positive_soft` pattern `\bnot sure\b.*\b(?:what|you mean|understand)\b` requires "not" and "sure" to be adjacent. It does NOT match "not quite sure" or "not quite understand" because "quite" sits between them.

**Fix:** Add `\bnot quite sure\b` and `\bnot quite understand\b` as standalone positive_soft patterns:
```python
r'\bnot quite (?:sure|understand)\b'  # "not quite sure I understand"
```

These are safe — no one says "not quite sure" followed by a rejection. It's always a request for clarification, which is a soft positive.

**Real incident (July 20, 2026):** Gina (gina@beyondthescoreboards.com) replied "Yes, please send that over. I'm not quite sure I understand your service fully." The one-word positive check didn't catch "Yes, please send that over" (too many words), `\bnot sure\b` didn't match "not quite sure", and `\bsend (?:me )?(?:more |some )?info\b` didn't match "send that over." Classified as `neutral_question` instead of `positive_soft`. She booked an appointment 3 days later — the most valuable lead in the campaign was nearly missed by the classifier.

### ⚠️ "will get back to you" auto-responder gap — `we.ll` vs `will` (Jul 20, 2026)

The auto-responder pattern `\bwe.ll get back\b` matches "we'll get back" (apostrophe matches `.`) but NOT "will get back" ("wi" ≠ "we"). Customer-service auto-replies often use "will get back to you" without the contraction.

**Fix:** Add `\bwill get back\b` and `\b(?:we have )?safely received\b` (a common prepend: "we have safely received your email") to auto-responder patterns:
```python
r'\bwill get back\b'              # "will get back to you" (non-contracted)
r'\b(?:we have )?safely received\b'  # "safely received your email and will get back"
r'\bassisting other\b'            # "assisting other patients/customers"
```

**Real incident (July 20, 2026):** Florida Strivepharmacy (florida@strivepharmacy.com) replied: "Thank you for contacting Strive Rx! We truly care about your health journey and are here to help! We're currently assisting other patients via phone and message, but please know we have safely received your email and will get back to you." The `\bthank you for contacting\b` pattern matched, but the human-signal check on the after-split text found no matches, so it correctly fell through to `auto_responder` in the monitor pipeline classifier. However, ad-hoc classifiers that don't gate auto patterns BEFORE positive checks will match "care about" / "help" / "phone" as positive signals and misclassify this as `positive_interested`. **Lesson:** always run auto-responder detection FIRST, before any positive keyword matching.

### ⚠️ One-word positive reply blind spot — ellipsis `…` not in strip characters (Jul 17, 2026)

The one-word classifier's strip set is `rstrip('.!?,;')` — it does NOT strip the Unicode ellipsis character `…` (U+2026). A reply like "Sure… let me know when you're available" becomes 2+ words after stripping (`['sure…', 'let']`), so `len(body_words) <= 2` fails and the one-word override never fires. The word "sure…" with trailing ellipsis also won't match `in ('sure', 'ok', ...)` because the ellipsis remains attached.

**Fix — add `…` to strip characters AND check substring match:**
```python
body_words = body_text.strip().split()
if len(body_words) <= 2:
    word = body_text.strip().lower().rstrip('.!?,;… \t\n\r')
    # Also try the first word alone (handles "Sure… let me know")
    first_word = body_words[0].lower().rstrip('.!?,;…')
    if word in POSITIVE_ONE_WORDS or first_word in POSITIVE_ONE_WORDS:
        return 'positive_interested'
```

**Real incident (July 17, 2026):** Jodi Fleisig (jodi@jodifleisig.com, #3577260 PR v2) replied "Sure… let me know when you're available" — a clear positive. The classifier returned `neutral` because: (1) `len(body_words) = 10` (not ≤ 2), (2) "sure…" with ellipsis didn't match any positive pattern regex. The daemon still caught and replied within 14 minutes, but ad-hoc classifiers used in monitoring sweeps would silently miss this. Jodi is a COMPLETED-campaign lead (#3577260) — same pattern as Spark and Scott Kaier where engaged leads keep replying to stopped campaigns.

### ⚠️ ALWAYS use the canonical `monitor_pipeline.py` — ad-hoc classifiers silently miss positives (Jul 22, 2026)

When writing ad-hoc classification scripts in a monitoring session, the `extract_reply_body()` function is frequently incomplete — missing patterns that are already fixed in `scripts/monitor_pipeline.py`. This causes false negatives on real positive replies.

**Three canonical patterns that ad-hoc scripts consistently miss:**

1. **`\r\n` → `\n` normalization** (CRLF line endings from Outlook/iOS). Must be the FIRST operation in `extract_reply_body()`:
   ```python
   body = full_body.replace('\r\n', '\n').replace('\r', '\n')
   ```

2. **`From:.*\n(?:Sent|Date):` Outlook forward pattern** — the simplest variant (`From:` with `Date:` not `Sent:`) catches Outlook forwards that don't use the full `From:\nSent:\nTo:\nSubject:` format. This is the #1 missed pattern.

3. **Inline (no newline) quote delimiters** — `On .* at .* wrote:` without `\n` prefix catches Gmail/iOS replies where HTML stripping collapsed everything onto one line.

**Never write ad-hoc classifiers for monitoring sweeps.** Always use `python3 scripts/monitor_pipeline.py --pages 3`. If the pipeline needs a new pattern, patch it there first.

**Real incident (Jul 22, 2026):** Jeff Dillon (#3617053) — "Yes, I'd be open to see what you have" from Outlook with `From: Aubrey Scott <...>\r\n Date: Thursday...` forward footer. Ad-hoc `parse_histories.py` missed both the `\r\n` normalization AND the `From:.*Date:` pattern → classified as `negative_notfit`. Jeff was a strong positive (handled by a separate cron), but the bug would have silently killed an unhandled positive. The canonical `monitor_pipeline.py` with `\r\n` normalization + `\nFrom:.*\n(?:Sent|Date):` pattern catches this correctly (added Jul 20, verified Jul 21).

### ⚠️ "Yes" first-word positive — classify BEFORE running negative patterns (Jul 20, 2026)

The naive CSS-only / empty-body check used in ad-hoc monitoring scripts:
```python
if len(re.sub(r'[\s{};:#.\-\w"\'=@\(\)\[\],]', '', body)) < 5:
    return True, 'auto'
```
This catches **every normal English reply** because standard ASCII text has 0-3 characters that don't match the regex. Spark's 638-char human reply ("Oh i totally get that. Could you give me some guidance...") was classified as `auto` and would have been silently skipped — **a 5-message deep-funnel pricing question from the most engaged lead in the system, nearly missed.**

**Similarly: `len(body.strip()) < 10` or `len(body.strip()) < 20` catches ALL one-word positive replies** (sure, ok, yes, yep, absolutely, please) as `auto_responder`. "sure" is 4 chars — every acceptance reply gets silently dropped.

**Fix — TWO required guards (both must be present):**

1. **One-word override MUST run BEFORE the length check.** Check for single-word positive replies first:
```python
body_words = body_text.strip().split()
if len(body_words) <= 2:
    word = body_text.strip().lower().rstrip('.!?,;')
    if word in ('sure', 'ok', 'okay', 'yes', 'yep', 'yeah', 'absolutely', 'definitely', 'indeed', 'please'):
        return 'positive_interested'
    if word in ('stop', 'unsubscribe', 'remove'):
        return 'hostile'
```

2. **CSS-syntax patterns required BEFORE triggering `auto_responder`:**
```python
has_css_syntax = bool(re.search(r'[{].*[:].*[;].*[}]', body)) or \
                 bool(re.search(r'body\s*[{]|table\s+[{]|\.\w+\s*[{]|#\w+\s*[{]', body))
if has_css_syntax and css_count < 5 and len(body) < 300:
    return True, 'auto'
# Only THEN: truly empty/whitespace-only bodies
if len(body.strip()) < 10 and has_css_syntax:
    return True, 'auto'
```

**The `monitor_pipeline.py` script has the one-word override (guard #1). Always use it rather than writing ad-hoc classifiers.** If you must write one, copy both guards from the script — never use `len(body) < N` alone.

**Real incidents:**
- Jul 17, 2026: Spark/Ethan (#3577260) — "sure" (4 chars) classified as `auto_responder` by ad-hoc classifier. 13-message deep-funnel pricing close, the most engaged lead in the system. The `monitor_pipeline.py` one-word override would have correctly returned `positive_interested`.
- Jul 17, 2026: CSS-only regex stripped every character from Spark's 638-char human reply containing pricing questions — all standard ASCII, 0 non-matching chars → classified as `auto`. Would have been silently skipped.

### Always paginate inbox — page 0 is not enough

Instantly's inbox endpoint hard-caps at 20 entries/page. Instantly's `/emails` pagination limit is unverified (unlikely to be unlimited — test before assuming any page size works). Always paginate rather than assuming a single call returns everything. For a 30-minute cron: pull the first couple pages. For a monitoring sweep: continue until entries older than 48 hours or an empty page.

### Case study vertical mismatch
Don't send a men's health clinic the coaching case study. Match aggressively. If no case study exists for a vertical, use the closest one and tell the operator a new case study is needed. The men's coaching case study (aiintegraterz.com/case-studies/mens-coaching.pdf) was used for a women's health coach on July 13 with an explicit note — a women's-coaching-specific case study would be better.

### Here's what we have and don't have (case study coverage)
- ✅ Men's health / TRT / hormone clinics — https://aiintegraterz.com/case-studies/mens-health.pdf
- ✅ Men's coaching / fitness coaching — https://aiintegraterz.com/case-studies/mens-coaching.pdf
- ✅ Marketing agencies — https://aiintegraterz.com/case-studies/marketing-agency.pdf
- ✅ Solar companies — https://aiintegraterz.com/case-studies/solar.pdf
- ✅ AI agencies / AI automation — https://aiintegraterz.com/case-studies/ai-agency.pdf
- ✅ MCA / alternative lending — https://aiintegraterz.com/case-studies/mca.pdf
- ✅ Recruiting / staffing (general) — https://aiintegraterz.com/case-studies/recruiting.pdf
- ✅ Recruiting — master / full-service — https://aiintegraterz.com/case-studies/recruiting-master.pdf
- ✅ Recruiting — exec search — https://aiintegraterz.com/case-studies/exec-search.pdf
- ✅ Recruiting — IT staffing — https://aiintegraterz.com/case-studies/it-staffing.pdf
- ✅ HVAC / home services — https://aiintegraterz.com/case-studies/hvac.pdf
- ❌ Weight loss / GLP-1 / hormone wellness clinics — NONE (used men's health as fallback Jul 15-16: Bellobella — semaglutide/tirzepatide clinic, **ScaleDown Weight Loss** — `info@scaledownweightloss.com`, replied "Sure feel free to send it." Sent men's health case study since hormone/wellness-adjacent, handled within 23 min. This vertical is generating real replies — build a dedicated case study.)
- ❌ Women's health / wellness coaching — NONE (used men's coaching as fallback July 13)
- ❌ Mindfulness / meditation — NONE

### Case study pages are web pages on aiintegraterz.com — stats can be extracted directly
The case study URLs (e.g. `https://aiintegraterz.com/case-studies/mens-health.pdf`) now open as rendered HTML pages — not raw PDF downloads. Stats and hooks can be extracted by fetching the page content via curl or browser. Use the actual stat from the case study for the TOP section hook line (e.g. "15+ booked consults in 30 days"). If the page content can't be fetched or the stat isn't visible, use a directional hook without a hard number and flag to the operator.

### Cold email vertical mismatch — check what the lead was actually sent
The cold email templates in campaign #3617053 vary by niche. A lead may reply positively even if the email wasn't perfectly matched to their business. **July 13, 2026:** Dawn RWTX (Renew Wellness, women's health/hormones FNP-C) received a men's-health-framed cold email ("every restriction pass hits men's health hard") from Anna. She replied positively anyway ("Sure. Send me more info, please."), but the mismatch is awkward. When reviewing the original email: if the framing doesn't match the lead's actual vertical, adapt the case study selection and reply tone accordingly.

### Sender persona comes from the original SENT message — extract it from the reply body
When a lead replies, their email includes the quoted original message showing the original sender (e.g. "On Mon, Jul 13, 2026 at 10:25 AM Julia Castillo <julia@horizonstepfl.info> wrote:"). Extract the sender's first name from this quoted text — that's the {SenderPersona} for the reply. Never sign as "Justin" for owned audiences replies.

**⚠️ Persona mismatch — {SenderPersona} MUST match the FROM address's persona.** When sending in batch mode, the locked template's `{SenderPersona}` must match the persona whose email account is actually sending. **July 14, 2026:** Kylie's case study reply was sent from `natalie@horizonvistaky.info` but the locked template signed "Willow" — the prior cron used the wrong persona name. Domain `horizonvistaky.info` maps to Natalie, not Willow. Before sending, cross-check: the sign-off name must match the persona for the `from` address domain per the domain-persona mapping table. This is especially easy to get wrong in batch mode when iterating through multiple leads with different sender personas.

**⚠️ Instantly's `from_name` field on SENT messages is unreliable** — it often shows `null` or empty even when the message was sent from a named persona. Always extract the sender name from the quoted sender line in the reply body (e.g., `"On ... Julia Castillo <julia@...>"` → "Julia") — this technique is platform-agnostic and works regardless of whether the `from_name` field itself is reliable. The domain-to-persona mapping table in `owned-audiences-email-reply` (`prosperliftwi.info` = Audrey, etc.) is tied to Instantly's current warmed sending domains — do NOT assume Instantly sends from the same domains. Build the equivalent mapping once Instantly mailboxes are connected and their sending domains are known; until then, rely on extracting the name from the quoted reply text rather than a domain lookup.

### Leads promised a custom plan MUST get one — not just a case study
When a lead replies to a cold email that promised them a specific custom plan (e.g. "a short version of the system for [their business], plus a case study"), sending only the case study is a broken promise. These leads are testing whether you deliver what you said you would. Read the original `email_message` from campaign statistics BEFORE drafting — if it contains language like "a short version of what this would look like for [business]" or "a short version of the system for [business]," you MUST build AND include a custom plan link in the reply. The custom plan can be a simplified one-page HTML (partner categories, influencer types, podcast types, booking CTA) — it doesn't need to be the full 3-page research-heavy version. Publish to here.now and include the link alongside the case study.

### ⚠️ Phone number masking — verify before relying on it

Instantly masks ALL phone numbers for leads added via scraping/API (`phone_number` returns `+120****3289` — useless for calling); real phones only come from email reply signatures. Whether Instantly does the same is unverified. Check before assuming either way — don't waste time chasing unmasked phones from the API if it turns out Instantly masks them too.

### Google Sheet tracker (Jul 20, 2026)

A master tracking sheet exists at `https://docs.google.com/spreadsheets/d/1Pnllx-9B9QWUZYa-3Bj36nbve_dhBfCmx2mt5ZhHYrs/edit` (authenticated as `justin@usingaitoscale.com` via Composio MCP). It tracks ALL Owned Audiences campaigns plus Solar (#3691319) across 5 tabs. Use `composio` skill → `COMPOSIO_MULTI_EXECUTE_TOOL` → `GOOGLESHEETS_VALUES_UPDATE` to add/update rows. Columns include Called 1-5 and Booked tracking. See `references/sheet-workflow.md` for the full pipeline.

### Sending — cosmetic errors are a known pattern, verify by outcome not exit code

Instantly's CLI reply command returns a non-JSON success response that a strict JSON parser chokes on — a false error where the email was actually sent (see `owned-audiences-email-reply`). Whether Instantly's `POST /emails/reply` has an equivalent quirk is unverified. The general lesson applies regardless: after a send call, don't trust a parse error or non-200 status at face value without checking whether the action actually happened (e.g. re-querying the thread for the new outbound message).

A duplicate copy of the Google Sheet tracker note (`https://docs.google.com/spreadsheets/d/1Pnllx-9B9QWUZYa-3Bj36nbve_dhBfCmx2mt5ZhHYrs/edit`, Composio MCP, `references/sheet-workflow.md`) appeared here in the original — see the "Google Sheet tracker" section above for the live version; this is 100% platform-agnostic (the sheet doesn't care which ESP sent the email) and not duplicated further here.

### Hostile/unsub sender management — state file at `/opt/data/scripts/auto_reply_state.json`

The `hostile_senders` and `unsub_senders` arrays in the state file prevent the pipeline from re-engaging blocked leads. To remove a lead from either list:

```python
import json
STATE_PATH = '/opt/data/scripts/auto_reply_state.json'
with open(STATE_PATH) as f:
    state = json.load(f)
email = 'lead@domain.com'
if email in state['hostile_senders']:
    state['hostile_senders'].remove(email)
if email in state['unsub_senders']:
    state['unsub_senders'].remove(email)
with open(STATE_PATH, 'w') as f:
    json.dump(state, f, indent=2)
```

**July 14, 2026:** Robyn (robyn@mindfulnessathletics.com) was removed from both lists — she was misclassified as hostile when her complaint was about plan quality, not about being contacted. The circling-back email (case study + plan) triggered her, but her first reply was genuinely positive.
The permanent API key for `justin@usingaitoscale.com` is saved at `~/.herenow/credentials` (chmod 600). All publishes default to permanent — no 24h anonymous expiry.

### Cron job instructions may be outdated — the skill is authoritative
The cron job's embedded instructions in the user message may reference the old workflow ("Build the 5-page partner-backed plan PDF", "Research the lead — 15 min max"). **The SKILL.md is the source of truth.** Current mode (July 2026): case study + booking link. Custom plans are suspended. If cron instructions conflict with the skill, follow the skill.

### Duplicate sends happen — detect "already handled" replies first
Multiple cron runs within a short window can each draft and send replies to the same lead. Before drafting, always pull message history (`GET /api/v2/emails`, filter mechanism unverified) and check if a SENT message after the REPLY timestamp matches the case-study reply pattern (starts with "Thanks for the reply", "Thanks — here it is", contains booking link). If already handled, skip and note it.

### Vestigial inbox entries — leads deleted from campaign but inbox entries persist
Confirmed on Instantly: when a lead is deleted from a campaign, their inbox reply entry remains visible even though the lead no longer exists — the ID lookups return empty history silently, no error. Whether Instantly has the same ghost-entry behavior is unverified, but the detection principle transfers: if a message-history lookup returns empty for an entry that clearly has reply metadata, check whether the lead still exists before assuming a bug in your own code.

**Detection:** If `leads messages` returns `{"history":[]}` for a lead, try searching for the email in the campaign leads list. If the email doesn't appear in any paginated lead listing, the lead was deleted and the inbox entry is vestigial. Do NOT waste additional API calls trying alternate lead IDs — both failed means the lead is gone.

**July 14, 2026:** Lori (lori@3principlestherapy), Jared (jared@actionpactcoaching), Drd (drd@coachinglifestrategies) — all three had inbox entries on page 1 of #3617053 with `last_reply_time` July 13 but returned empty history via both ID types. Leads were not found in the campaign lead listing.

### Periodic remediation audit — cron can miss positives for days
The 30-minute monitoring cron is a best-effort safety net, not a guarantee. Prior cron runs have missed positive replies that sat unhandled for 3-4 days (Jared/MONALI Health, Wendy/The Sensible Woman, Robyn/Mindfulness Athletics — all July 9-10, rescued July 13). Run a deep-scan audit weekly: pull inbox pages 0-3, check EVERY lead with a REPLY and `our_replies_after == 0`, classify manually. See `references/monitoring-workflow.md` → "Periodic Remediation Audit" for the full workflow and the July 13 rescue details.

### ⚠️ Cross-campaign awareness — always check ALL campaigns in the inbox, not just #3617053

The core lesson from the Instantly side (see `owned-audiences-email-reply` for the full incident history — multiple genuine positives sat unhandled for 8-13 days because monitoring tunnel-visioned on one campaign while others accumulated replies unwatched): **inbox monitoring must cover every active campaign, not just the one it was originally built for.** When Instantly has multiple campaigns live, the cross-campaign sweep must classify entries by campaign ID and check for unhandled positives everywhere, the same discipline Instantly needed after getting burned. Not yet relevant with 0 Instantly campaigns live, but build the pipeline with this from day one rather than relearning it the same way.

### ⚠️ Cross-campaign classification — podcaster replies have DIFFERENT signal patterns than owned-audiences

The monitoring pipeline's `classify_reply()` was built for owned-audiences coaching/wellness replies. The podcaster campaign (#3639259, sending since Jul 15) generates replies with distinct patterns that the existing classifier mishandles:

**Pattern 1: "Thank you for your email. I would love to chat..." — human positive, NOT auto-responder**
The OOO/auto-responder check catches `\bthank you for your email\b` and classifies as `auto_responder`, but when followed by "I would love to chat with you" or "do you have a calendar link," it's a real human expressing genuine interest. **Fix:** check for positive signals (chat, call, calendar, book, schedule) AFTER the "thank you" opener before committing to `auto_responder` classification.

**Pattern 2: "I'm out of the country / I'm travelling with limited bandwidth" — OOO, NOT positive**
Podcast hosts and media professionals frequently reply with travel OOO messages that don't contain standard OOO keywords ("office," "returning [date]"). The classifier's OOO patterns miss "out of the country" and "travelling with limited bandwidth." These replies often end with "Happy summer!" or similar — they're friendly but automated. **Fix:** add `\bout of the country\b`, `\btravell?ing with limited\b` → `auto_responder` / OOO.

**Pattern 3: Ticket-system auto-responders from partnerships@ / podcasts@ / media@ addresses**
The auto-reply prefix list catches `podcast@`, `partnerships@`, and `media@`, but when these addresses aren't pre-filtered (e.g., when the prefix list isn't applied first), their bodies ("Your message has been received and entered into our review system," "The following is an automated response") contain words like "review," "looking forward," and "connect" that trigger false positive classifications. **Fix:** check for "automated response," "review system," "we've received your," "thank you for contacting" BEFORE running positive signal patterns.

**Pattern 4: "We publicly blacklist agencies that use AI to send us guests" — negative, NOT neutral**
Michael Krigsman (mkrigsman@cxotalk.com, #3639259) replied with a polite but firm blacklist warning. The classifier saw no hostile or negative keywords and defaulted to `neutral`. This is a `negative_notfit` — do NOT re-engage. **Fix:** add `\bblacklist\b`, `\bdo not include\b`, `\burge you not to\b` → `negative_notfit`.

**Real incidents (July 15, 2026):**
- Isabel (isabel@tumcoeur.com): "Thank you for your email. I would love to chat with you, do you have a calendar link" → misclassified as `auto_responder`. Actually a genuine positive (already handled by daemon within 22 min).
- Chris (chris@entrepreneursforimpact.com): "I'm travelling with limited bandwidth. If it's urgent, please text me. Happy summer!" → misclassified as `positive_interested`. Actually an OOO.
- Trinity (clayton@trinitynewlife.com): "I'm out of the country with limited access to email" → misclassified as `positive_interested`. Actually an OOO.
- Startupradio (partnerships@startuprad.io): "Your message has been received and entered into our review system" → misclassified as `positive_interested`. Ticket-system auto-responder.
- NewStack (podcasts@thenewstack.io): "The following is an automated response" → misclassified as `positive_interested`. Auto-responder.
- Michael Krigsman (mkrigsman@cxotalk.com): "We publicly blacklist agencies that use AI to send us guests, so I urge you not to include us" → classified as `neutral`, should be `negative_notfit`.

### ⚠️ Forwarded/operator threads can misread as a lead reply — check direction, not just the type label

Confirmed on Instantly: when an operator manually replies via the web UI, or an automated follow-up goes out through a forward, the outbound message can appear mislabeled as an inbound reply in the API response. Whether Instantly's `/emails` response has the same mislabeling risk is unverified, but the detection technique below doesn't depend on trusting the label either way — it reads content, not the type field.

**Detection:** if the REPLY body reads like an outbound message FROM our side (greeting the lead by name, pitching the product, asking for thoughts, starting with "Hi/Hey [LeadName]"), it's NOT a real lead reply. Signature: the body opens addressing the lead ("Hi Sean,", "Hey Jodi,"), which a lead would never write to themselves. Check the `from` address domain — if it's a speakeragent.ai or known operator domain, skip. Also check `reply_details.from[0].address` if available.

**Real incidents:**
- **Jul 15, 2026:** Mike Billoni (#3577260) — `type: REPLY` from `ephraim.elleazar@speakeragent.ai` (Tony D) with body "Hi Mike, I wanted to follow up..." — operator follow-up, not a lead reply.
- **Jul 17, 2026:** Sean O'Shaughnessey (#3639259, sean@newsales.expert) — message [4] was `type: REPLY` from a Gmail message ID with body "Hi Sean, Thanks for your reply. We came across your work while researching podcasts for SpeakerAgent AI..." — automated SpeakerAgent follow-up sent via forward, mislabeled as REPLY. Sean's only real reply was message [1] ("Which of my podcasts are you referring to?"), which was already handled by message [2]. The false REPLY at [4] was classified as `positive_interested` because the body contained "would love" and "set up," creating a false lead-reply alarm.
- `templates/custom-plan.html` — men's health/TRT clinics (original)
- `templates/custom-plan-womens-health.html` — women's health/wellness coaches (added July 13)

If neither fits (e.g., mindfulness/fitness coaching, general coaching), adapt the closest one. The partner map categories and voice/airwaves sections are the only things that change — keep the structure identical.