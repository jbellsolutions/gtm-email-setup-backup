---
name: charm-qc-gate
description: "Mandatory quality-control gate for every outbound email. Verifies formatting, language, tone, and grammar against Charm Offensive standards before ANY email is sent. Must be run before every legacy email platform reply, cold email, or follow-up."
---

# Charm QC Gate — Mandatory Pre-Send Verification

**This gate is NON-NEGOTIABLE. Every outbound email — reply, cold, follow-up — must pass through this verification before sending. If ANY check fails, fix the draft and re-verify.**

This skill acts as the Charm Offensive quality-control agent. It loads the Charm Offensive voice rules and applies them rigorously to every draft before it leaves the outbox.

## Step 1 — Load the Charm Offensive standard

Always start by loading:

```
skill_view(name='charm-offensive-foundation', file_path='references/voice-and-humour.md')
```

This gives you the ten humour formulas, the banned corporate language, and the voice rules every draft must follow.

## Step 2 — Run the three-part verification

### PART A: Formatting (visual structure)

- [ ] **Blank lines present and correct.** Every section separated by a blank line. Count them — there should be exactly 5 blank lines in a reply email. No collapsed paragraphs, no wall of text.
- [ ] **No compressed text blocks.** The email must NOT be a single dense paragraph. Every thought gets its own line. Maximum 2 sentences before a line break. A 4-line block = FAIL.
- [ ] **Human rhythm.** Varied line lengths. Some 1-word lines, some 3-word, some full sentences. No uniform paragraph blocks. Read aloud — it should sound like a voicemail, not a nurture sequence.
- [ ] **Opener + first link on SAME LINE.** "Here you go --> <a href=...>" must be one continuous line. Link does NOT go on a separate line.
- [ ] **All links use HTML `<a>` tags.** No bare URLs, no markdown links, no parenthetical URLs. Every link is wrapped in `<a href="URL">display</a>`.
- [ ] **"Check out the report here" is a link,** not bare text. No colon, no punctuation after it.
- [ ] **Persona signature on its own line** with site link on the line below (or same line in cold emails). Not buried in a paragraph.
- [ ] **No trailing punctuation on link lines.** Lines that are just a link (`<a href="...">text</a>`) must not end with a period or comma.

### PART B: Language & Tone (Charm Offensive rules)

- [ ] **Zero corporate jargon.** Banned words: unlock, 10x, synergy, leverage, innovative, cutting-edge, solution, game-changer, transform, revolutionize, scale, disrupt, guaranteed, optimization, ecosystem, paradigm.
- [ ] **Zero banned phrases.** "No rush," "no pressure," "when you're ready," "the door's open," "grab some time," "if you're interested," "feel free to," "zero obligation," "thank you for the reply," "thanks for getting back."
- [ ] **Tone is confident, not deferential.** We're offering value — we don't thank people for replying. "Love the quick yes" ✓ — "Thanks for the reply" ✗.
- [ ] **Direct commands, not suggestions.** "Book in a time now" ✓ — "Feel free to book" ✗.
- [ ] **Urgency present.** Every email pushes to the next step immediately. No passive endings.
- [ ] **Human and warm.** Not corporate, not robotic. Reads like a real person wrote it.
- [ ] **No echoing the lead's exact words.** If they said "Surely," don't say "Surely love that." Use a fresh opener.

### PART C: Grammar & Mechanics

- [ ] **No typos.** Every word spelled correctly. No missing spaces, no doubled words.
- [ ] **Consistent punctuation.** Em dashes (—) not hyphens (-) for breaks. Oxford comma optional but consistent.
- [ ] **No sentence fragments** unless clearly intentional for voice (e.g., "15+ booked consults in 30 days." is fine as a hook line).
- [ ] **Subject-verb agreement.** Read every sentence aloud mentally.
- [ ] **Proper casing.** "Cal.com" not "cal.com." "AI" not "ai." Brand names capitalized.
- [ ] **Persona name spelled correctly.** Cross-check against the domain-persona mapping.

## Step 3 — Verdict

Return one of:

- **✅ PASS** — all checks clear. Safe to send.
- **⚠️ PASS WITH FIXES** — minor issues fixed inline (typos, punctuation). List what was changed. Safe to send.
- **❌ FAIL** — structural or tone issues that require rewrite. Return the draft with specific line-by-line corrections and the reason for each. DO NOT send until re-verified.

## Step 4 — If FAIL, fix and re-verify

Do not just flag the issue — fix it. Rewrite the problematic sections, then run the full three-part check again. Only proceed to send after a clean PASS.

## Integration with email workflows

### For owned-audiences-email-reply

After drafting any reply, run through this QC gate BEFORE calling `legacy email platform inbox reply`. The gate is the final step — if it fails, the email does not get sent.

### For cold email campaigns

After drafting campaign sequences, run each variant through this gate before saving to legacy email platform. Gate check is per-variant.

### For cron jobs

Cron jobs that auto-draft and send replies MUST include a QC gate step. If the gate fails, the cron should log the failure and NOT send — the draft gets flagged for manual review.

## Verification checklist (copy-paste into every draft review)

```
FORMATTING:
[ ] No compressed text blocks (every thought its own line)
[ ] Varied line lengths (some short, some long, some fragments)
[ ] Blank lines between sections
[ ] Lowercase subject and body
[ ] Reads aloud like a voicemail, not a template
[ ] Opener + link on same line
[ ] All links HTML <a> tags
[ ] Persona on own line
[ ] No AI footprint (no parallel lists, no "furthermore")

LANGUAGE:
[ ] Zero banned words
[ ] Zero banned phrases
[ ] Confident tone
[ ] Direct commands
[ ] Urgency present
[ ] Human/warm
[ ] No echoing lead's words

GRAMMAR:
[ ] No typos
[ ] Consistent punctuation
[ ] No bad sentence fragments
[ ] Subject-verb agreement
[ ] Proper casing
[ ] Persona name correct

VERDICT: PASS / PASS WITH FIXES / FAIL
```