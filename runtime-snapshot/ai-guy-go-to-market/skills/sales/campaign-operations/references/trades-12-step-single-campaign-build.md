# Twelve-step single-campaign framework build (Trades Referral Partners AU/NZ, 2026-09-03)

Session evidence for a multi-framework sequence built as ONE Instantly campaign with 12
sequential steps, per-lead custom variables, and a per-domain research pass over ~5.6K
domains. Every lesson below was hit live.

## Sequence clarification (user decision)
- Request: "each framework is its own custom email, there's a follow-up to it, the next
  framework is a custom email follow-up." Ambiguous between 22 steps and 12. Asked; Justin
  ruled: **12 emails total** — Frameworks 1-10 each as its own researched email, then the
  Day-3 "different thought" follow-up, then the Day-14 breakup. All in one campaign.
- Contrast with GYMS Connect Med One (10 separate per-framework campaigns): partitioned
  campaigns fit cohort testing; when the user wants every lead to receive every framework
  in sequence, build ONE campaign with N variable-only steps
  (`{{email_1_subject}}` … `<div>{{email_12_body}}</div>`), `stop_on_reply: true`.

## Reconciliation rules (user-confirmed)
- Two CSVs describe the same companies: a public-email-only list and a personal-contact
  list. **Send to every address supplied (union)**; a personal contact and the public
  address at the same company are separate recipients.
- Verified numbers: public 5,495 + personal 372, overlap 138 → union 5,729 unique
  addresses across 5,646 domains.
- Country swap (AU vs NZ column) per lead: domain TLD (.nz/.au) → then AU/NZ state names
  (auckland, wellington, canterbury…) → then phone prefix (+61/+64). TLD alone missed
  132 NZ leads.
- Never mint a first name from role mailboxes (Info/Office/Hr/Minning/Team) or from Name
  fields containing URLs/emails — strip junk, fall back to neutral "Hi there,".
  Local-part guessing only for clean `firstname.` patterns.

## Per-domain research pass
- Fetch each unique domain once (https → www → http), thread pool of 40, checkpointed
  done-file so the run resumes. 5,469/5,646 (96.9%) returned usable content.
- Harvest only structured signals: title/meta text + keyword inventory (years in business,
  renos/extensions, new builds, hiring, family-run, review mentions, lead platforms
  Hipages/Builderscrack/Oneflare/NoCowboys/Trade Me). Unreachable domains fall back to
  city/area relevance lines — never invented specifics.
- **Bug that cost a full 5.6K-domain pass:** the loop-continuation condition
  `if body and '<html' in body.lower() or (body and len(body) > 200)` — precedence
  rejected small valid pages AND left `err=None`, so `err[:120]` crashed every worker
  into the except path. Fix: accept any successful response; guard `(err or 'no response')`.
  Always smoke-test 3 domains before the bulk run.

## Copy generator pitfalls (all hit live)
- **Company names inject banned tokens into rendered copy:** "10X CONSTRUCTIONS" → banned
  `10x`; "Central HVAC Services" → `hvac`; "Absolute Fire Solution" → `solution`;
  "Fair Dinkum Builds" → `fair dinkum`; "Cost Solution" → `cost`. Sanitize the display
  name against the banned-token list before use; fall back to a neutral name ("your
  place") when nothing clean remains. These QA hits are data bugs, not copy bugs.
- **Word counts include greeting + signoff.** 90-word cores overflow the 50-100 range
  whenever the company name is long. Use a deterministic trim ladder (CTA contraction →
  drop fixed optional phrases → shorter pain sentence), then a force-short fallback for
  the worst framework. Verify with the ladder ON.
- **Doubled words:** AU/NZ has real double-barrelled place names — Wagga Wagga, Kurri
  Kurri, Gol Gol, Hei Hei (NZ) — whitelist them. Everything else is source-data
  duplication ("Drummoyne Drummoyne", "Muttaburra Muttaburra") — collapse. Also collapse
  "and and" in fmt. Word-token adjacent scan with same-line adjacency; never substring.
- **Subjects:** lowercase 1-4 words; hyphens valid ("the quote-off"). Do not QA a charset
  regex stricter than the doc — `[a-z0-9 ']`-style patterns false-fail hyphens.
- **Canonical framework phrases need QA whitelists:** the doc's own "I'm not a marketing
  agency and I don't sell leads" is legal; only flag other uses of "leads" outside
  whitelisted contexts ("buying leads", "better leads").
- **Patching f-string-heavy generator strings via search/replace repeatedly broke
  apostrophe quoting** (single-quoted f-strings + contractions → SyntaxError chains).
  Write copy strings double-quoted from the start. When repairing compile errors, rewrite
  the whole line; a heuristic "escape apostrophes followed by a letter" loop mangled a
  line before a targeted single-line rewrite fixed it.
- **Fixed-CTA per-step dedupe:** within one lead, 12 subjects must be unique (rotate the
  framework's subject options; on collision pick the next unused option from that step's
  list, fallback "quick one N").

## Second-agent review outcome (independent editorial QA)

Machine QA reached 0/68,748 (5729 leads × 12 steps) after five generator fix rounds,
but the independent second-agent review returned **FAIL** with cohort-wide grammar and
country-swap defects the machine gate missed. All fixed and verified cohort-wide:

- **"a air con company"** (205 leads): collapsed trade nouns break article agreement
  before vowel-initial nouns. Fix: article() helper in the generator + cohort-wide
  `\ba\s+[aeiou]` QA check (adjudicate real company names like "Zarama Air").
- **"a preferred sparkies"** (step-11 follow-up): singular/plural agreement when a
  list item is singularized. Fix: singular() transform, verified cohort-wide.
- **Step-1/7 opener collisions** (19 leads): platform-hint leads got the identical
  "Noticed X is on Hipages." opener in two steps. Fix: variant index per step;
  QA asserts pairwise opener equality == 0 across all step pairs per lead (per-lead
  distinct counts alone hide this).
- **"the footy" to NZ leads** (978): country-swap must cover idioms, not just
  platform/council terms. Step 6 now says "the rugby" for NZ.
- **Empty-city artifacts** ("works around ."): junk CSV city fields survived cleaning
  and rendered empty details. Fix: validate the cleaned place hint before adding it;
  sentence-level `city or "your area"` fallbacks everywhere.
- **Thin-research opener repetition** (357 leads at 2 distinct openers over 10 steps):
  rotate 2-4 phrasing variants per signal kind indexed by step number; assert a
  minimum distinct-opener count per lead. Post-fix: 0 leads below 3 distinct openers.

QA-scan false positive worth remembering: the artifact regex "around," matched the
legitimate phrase "I'm around, and I'll..." in the breakup email (5,729 false hits) —
read artifact hits in context before counting them as defects.

## Session end state

Upload payloads (115 batches × 50 leads, per-lead custom_variables) were rebuilt with
the final copy, but the campaign had NOT been created and no leads were uploaded when
the session ended — the paused-campaign creation + batch upload + leads/list
reconciliation remained to be run. Editorials: never upload between a FAIL verdict and
its verified fixes; rebuild upload payloads after every copy regeneration.

## Instantly API notes
- `GET /campaigns` returns 403 with default urllib UA — same Cloudflare behavior as
  `/emails`; send a browser-like User-Agent on every call.
- List campaigns before creating; the account had 20 existing campaigns, none for this
  vertical. Name-check to avoid duplicates.
- Build order (reconciliation verified, upload not yet executed at session end):
  create paused → 12 variable-only steps → upload ≤50-lead batches with per-lead
  `custom_variables` (`email_N_subject`, `email_N_body` with `<br><br>` breaks) →
  after EVERY batch reconcile via `POST /leads/list` with the `campaign` filter key and
  cursor pagination → campaign stays paused → sampled UI render preview before any
  activation. Activation is a separate explicit approval.
