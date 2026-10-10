---
name: cold-email-editorial-workflow
description: "5-stage editorial pipeline for cold email copy: Research → Strategy Bullets → Charm Draft → Spam Check → QC Gate. Run when creating or updating cold email campaigns, writing per-lead copy, or when Justin says 'run the editorial workflow' or 'use the editorial team process.'"
version: "1.0.0"
---

# Cold Email Editorial Workflow

A 5-stage pipeline that mirrors an editorial team: research, strategy, copy, spam QA, and final QC. Each stage feeds the next. Nothing ships without passing all gates.

## When to use

- Creating new cold email campaigns
- Writing per-lead copy for Owned Audiences campaigns
- Updating existing campaign sequences
- Justin says "use the editorial workflow" or "run the team process"

## The 5 Stages

### Stage 1 — Research Agent

Research the vertical, the industry, and if applicable the specific lead/company. Focus on:
- Industry pain points and language
- What business owners in this space actually talk about
- Partnership/referral ecosystem (who already has their customers?)
- Ad fatigue / rising ad costs in the industry
- Real numbers if available (not invented)

Tools: web_search, browser_navigate, apify, scrapercity. For per-lead research, use Instantly lead data + company website.

**Output:** A research brief (bullet points) with industry insights, pain points, and partnership angles.

### Stage 2 — Strategy Agent

Convert the research brief into marketing bullet points for the email copywriter. Each bullet should be:
- A specific angle or hook
- Grounded in the research (not generic)
- Framed for Charm Offensive voice (disarming, human, no jargon)
- Tied to the J. Abraham partnership methodology

**Output:** 5-8 strategy bullets that a copywriter can turn into Charm Offensive email copy.

### Stage 3 — Copy Agent (Charm Offensive)

Write the email copy from the strategy bullets. Must follow:
- **Charm Offensive voice** — load `charm-offensive-foundation` + `charm-cold-email`
- **OA template structure** — load `Instantly-cold-email` → `references/oa-charm-template.md`
- **No events, no home shows, no trade shows**
- **J. Abraham framing**: "We execute proven partnership strategies. You show up and close."
- **Banned phrases** from `charm-qc-gate`: no "thank you for the reply," no "no rush," no "when you're ready"
- **Banned words** from `spam-word-checker`

**MANDATORY FORMATTING (non-negotiable, Justin-enforced):**
- **No text blocks.** Break every thought into its own line. Short fragments, not paragraphs.
- **Blank line between every section.** Every sentence group separated by `\n\n`.
- **Varied sentence length.** Long line, then a short one. Then a fragment. No symmetrical rhythm.
- **Lowercase throughout.** Subject lines and body. Reads like a peer, not a pitch.
- **No AI footprint.** No parallel three-item lists. No "furthermore," "moreover," "delve." If it sounds like a nurture sequence, rewrite until it sounds like a voicemail.
- **Read out loud.** If you can't say it naturally between two client calls, it's wrong.

For campaigns with merge tags: write 4 emails (Intro, Value Angle, Nudge, Breakup).
For campaigns with hardcoded sequences: write 4-8 emails following the Charm 8-part arc.
For campaigns with hardcoded sequences: write 4-8 emails following the Charm 8-part arc.

**Human formatting rules (mandatory — non-negotiable):**
- Each thought/sentence on its own line. Never run two different ideas together on one line.
- Blank line between every section (opener, body, CTA, sign-off)
- Varied line lengths — some one-word lines ("seriously."), some two-word ("worth 20?"), some longer. No uniform paragraph blocks.
- Lowercase throughout. This isn't a press release.
- Never more than 2 sentences before a line break. Never a 3-line paragraph.
- The close always gets its own section with blank line above.
- Sign-off on its own line at the bottom.
- Read it aloud. If it sounds like a nurture sequence, rewrite until it sounds like a voicemail.
- Count blank lines: a 4-email short sequence should have 5-8 blank lines in email 1, 3-5 in emails 2-4.

### Stage 4 — Spam QA Agent

Run every email through the `spam-word-checker` skill. Flag and fix:
- Banned single words (get, now, open, free, new, etc.)
- Banned short phrases
- High-risk promotional wording
- Em dashes (replace with regular dashes)
- ALL CAPS, multiple exclamation marks
- "Hi Name," greetings (use "Name," directly)

**Output:** Clean copy with all spam flags resolved, or a list of issues to fix.

### Stage 5 — QC Gate Agent

Run every email through `charm-qc-gate`. Three-part check:

**Formatting:**
- Blank lines present and correct
- No collapsed paragraphs
- Links use HTML tags where applicable
- No trailing punctuation on standalone lines

**Language & Tone:**
- Zero banned words (corporate jargon, banned phrases)
- Confident tone, not deferential
- Direct commands, not suggestions
- Urgency present
- Human and warm

**Grammar & Mechanics:**
- No typos
- Consistent punctuation
- Proper casing (AI, Cal.com, etc.)
- Persona name correct

**Verdict:** PASS / PASS WITH FIXES / FAIL. If FAIL, fix and re-verify.

## Execution Modes

### Full Pipeline (for new campaigns)

Run all 5 stages sequentially. Stage 1 (research) can be delegated to a subagent for complex verticals.

### Fast Pipeline (for per-lead copy)

Skip Stage 1 if research already exists. Run Stages 2-5. Use existing vertical knowledge.

### Batch Pipeline (for multiple campaigns)

Run Stages 1-2 once per vertical, then Stage 3-5 per campaign variant.

## Real Execution

When Justin says "use the editorial workflow," execute as follows:

1. Load `charm-offensive-foundation` (voice rules)
2. Load `charm-cold-email` (templates)
3. Load `spam-word-checker` (spam rules)
4. Load `charm-qc-gate` (QC rules)
5. Research → brief (use subagent if complex)
6. Brief → strategy bullets (inline)
7. Bullets → Charm copy (inline)
8. Run spam check (Python script)
9. Run QC gate (manual review against checklist)
10. Deliver final copy with all checks passed

## Quality Standards

- Every email must pass spam check AND QC gate before shipping
- No banned words, no banned phrases, no junk
- Charm voice must be authentic — if it sounds like a template, rewrite it
- J. Abraham framing must be clear: partnerships, not ads
- "We handle setup, conversations, campaigns. You show up and close."

## Related Skills

- `charm-offensive-foundation` — voice and humor toolkit
- `charm-cold-email` — email templates and sequence structure
- `charm-qc-gate` — mandatory pre-send quality control
- `spam-word-checker` — deliverability guardrails
- `Instantly-cold-email` — Instantly campaign management and OA template
