# Multi-framework single-campaign rebuild (10 frameworks + 2 follow-ups = 12 steps)

Session pattern from the Trades Referral Partners AU/NZ build (Sept 2026). Extends the
nine-step partner-sequence rebuild (`mamas-and-minis-9-step-rebuild.md`) to a
twelve-step shape where every framework is its own sequential email in ONE campaign.

## When this shape applies
User instruction: "each framework is its own custom email, there's a follow-up to it,
the next framework is a custom email follow-up to it, all ten frameworks and two more
follow-ups." Clarified to mean 12 emails TOTAL per lead, one campaign, NOT ten
campaigns partitioned by framework. Ask which shape when the user says "each
framework its own email" — the two readings differ 10x in send volume per recipient.

## Verified structure
- 12 custom variables per lead: `email_1_subject` … `email_12_subject`, `email_1_body` … `email_12_body`.
- Campaign sequences: 12 variable-only steps, subject `{{email_N_subject}}`, body `<div>{{email_N_body}}</div>`.
- Steps 1-10 = the framework doc's frameworks 1-10 verbatim in structure (each with its
  own subject pool, bucket, and CTA type: short-version CTA on ≥6, diagnostic question
  on #8, first-look on #9, free-map on #10). Step 11 = doc's Day-3 "different thought"
  follow-up. Step 12 = doc's Day-14 breakup.
- Country swap (AU Hipages/council approvals vs NZ Builderscrack/consents/Kia ora)
  resolved per-lead from domain TLD, then phone (+61/+64), then state, in that order.

## Cheap research pattern that made per-lead relevance possible at 5,646 domains
Threaded (40 workers) single-URL fetch per domain (https → www → http fallback), 12s
timeout, harvest only structured signals: title, meta description, keyword hits
(years-in-business, family-run, hiring, new builds, renos, platforms), city-in-text.
Checkpoint every domain to a done-file so reruns resume. Got 96.9% coverage of 5,646
domains in ~10 minutes. Unreachable domains fall back to city/area relevance lines —
never invent details. Do NOT put city/state strings into custom variables; regenerate
copy from them instead, so sanitization happens before text exists.

## Data sanitization pitfalls (hit live)
- Company names containing banned tokens: "Central HVAC Services" trips the HVAC ban,
  "Absolute Fire Solution" trips "solution", "10X Constructions" trips "10x". Sanitize
  the display name at generation time (drop banned tokens; if nothing usable remains,
  fall back to a neutral phrase like "your place") — don't fail QA and hand-fix.
- 119/5,729 leads had gmail/outlook/icloud domains and no usable company name →
  "your place" fallback; copy reads naturally around it. Report the count in the handoff.
- Name and City columns can contain URLs, "Unknown", "Traffic Manager", email addresses.
  Guard first_name against @/http/www/slash. Degenerate single-letter cities must be dropped.
- AU/NZ place-name doubling is real: Wagga Wagga, Kurri Kurri, Gol Gol, Hei Hei are
  legitimate; "Smeaton Grange Smeaton Grange Australia" and "Drummoyne Drummoyne" are
  data defects. Collapse adjacent duplicate tokens except a small genuine-towns
  whitelist; strip trailing country tokens.

## Word-count QA threshold trap
The framework cap (50-100 words) applies to the FULL rendered email including greeting
and sign-off. If the generator trims paragraph bodies to 100, "Hey Dave," + "Cheers,"
pushes it to 103. Trim target must be cap minus fixed scaffold words (2-word greeting +
1-word "Cheers," = 3, so trim paragraphs to 97). Sixteen QA "failures" on the first
clean-looking pass were exactly this.

## Initialism and doubled-word false positives in the machine scan
- The word-token doubled-word regex fires on initialisms: "G P P Industries" renders
  "P P" inside the CTA. Skip single-letter repeats.
- Keep the genuine-towns whitelist in QA too, or the scan re-flags fixed copy.

## Singular/plural partner-type grammar
Partner Map rows are plural ("sparkies, plumbers, roofers"). Step 4 template rendered
"A sparkies, a plumbers…" — drop the articles for plural types. Step 5's example
sentences need a singular() helper ("the removalist who walks into a house").

## Gate sequence actually used
Machine QA to zero hard failures → independent second-agent editorial review
(stratified sample: ≥2 per country, named + generic greetings, every framework step
read in full, sanitized-name leads, Kia ora leads; plus cohort-wide greps) → only then
create campaign paused → build batches (≤50 leads, 24 custom vars each, checkpointed)
→ upload → reconcile via leads/list with `campaign` filter → UI render preview →
activation only on explicit user approval. Upload was gated behind the editorial
verdict, not run in parallel with it.
