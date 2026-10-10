---
name: generated-copy-qa
description: "Use to audit machine-generated personalized copy at scale."
version: "1.0.0"
---

# Generated Copy QA

Independent editorial + deterministic QA for **machine-generated personalized copy** —
cold email, marketing sequences, newsletters, or any output produced by a deterministic
generator (hash-on-email framework assignment + fixed template strings + `{company}` /
`{city}` / `{name}` merge tags). Verifies fidelity, catches defect classes a human
spot-check misses, and avoids the regex false positives that make automated audits lie.

## When to use

- Auditing per-lead cold-email copy produced by a generator script (JSONL/CSV of bodies)
- Verifying a "fix" actually removed a known defect class (duplicate CTAs, repeated words)
- A second-agent / independent-eyes pass before upload to a sending platform
- Any "does this generated copy pass editorial QA" ask at scale

## The method (5 steps)

1. **Reproduce the generator byte-for-byte** — don't hand-copy template strings; exec the
   source with its output path redirected to /tmp and diff against the shipped artifact.
   Byte-identical ⇒ subjects/cores/follows/closes, framework assignment, and step depth are
   exactly as authored. Any diff is the real defect. (See `references/deterministic-copy-qa.md` §1.)
2. **Full-corpus structural checks** — step depth per framework, unique first bodies,
   word-count bounds, safety/required language present, no Unicode dashes / links /
   unresolved `{token}` / banned claims.
3. **Merge-collision scan** — word-token adjacent-duplicate scan per line to catch the
   "the The gym" defect class (§ below).
4. **Adjudicate claim/regex hits** — every "banned claim" match must be read in context;
   most fires are innocent merges (§ regex false positives below).
5. **Stratified manual sample** — deterministic seed, a few leads per framework ×
   research-status class; read first-touch + follow-up aloud for grammar/tone/reasonableness.

Report a binary **PASS / FAIL with exact counts** for each check; never auto-clear a real
hit, and never invent counts.

## Merge-collision defects (the "the The gym" class)

Merge tags render inside fixed phrases; when the **lead data** starts with a word the
template also ends/prepends with, you get doubled words — the same family as
"personal training training":

| Template phrase | Lead name | Renders |
|---|---|---|
| `the {c} site mentions` | "The GYM" | "the The GYM site mentions" |
| `…landed on {c}` | "On Point Fitness" | "…landed on On Point Fitness" |
| `I found {c}` | "Found Development" | "I found Found Development" |

Detection: word-token adjacent-duplicate scan per line (case-insensitive), then **read**
each hit — most are innocent real names ("Walla Walla", "Yoga Yoga", "R&R"), but
`the The` / `on On` / `found Found` / `in in` are template bugs, not data.

## Regex false positives that make automated audits lie

Banned-claim / spam regexes fire on innocent merges. Adjudicate, don't auto-fail:

- `\bwill (make|earn|generate|profit)\b` → matches `I will make this brief.` (opener), not an income promise.
- `\b(always|never|every member|all members)\b` → fires on lead names ("Never Give Up Fitness", "Always Reddy Athletics").
- `\$\d[\d,]*` → fires on "$3" inside a lead name ("PURPO$3").
- ALL-CAPS run `[A-Z]{3,}` → fires on real names/abbrevs ("YMCA", "BJJ", "LLC"), not copy defects.
- **Banned-word substring trap:** `"solution" in body.lower()` fires on every company/suburb name
  containing "Resolution"/"Resolutions" (44 hits → 0 once word-bounded), `"transform"` fires on
  "transforms/transformation", and `"roi"`/`"hvac"` (case-insensitive) fire inside longer tokens.
  Always match banned words with `\bword\b` (and case-SENSITIVE for acronyms like `ROI`/`HVAC`);
  read any remaining hit in context — company names are data, not copy.
- **Doubled-word substring trap:** never scan doubled words as substrings — `"the the" in body`
  matches "the theater" and `"is is" in body` matches "this is" (lowercased). Use the
  word-token scan with same-line adjacency instead.
- **Doubled-word separator trap:** a word-token scan that drops non-letters (`&`, `/`) turns
  innocent real names like "Pro Cheer Training & Training Center" into a false "training
  training" hit. Prefer the whitespace-adjacent regex `\b([A-Za-z]+)\s+\1\b` (case-insensitive)
  for the named defect class (`the The` / `on On` / `found Found` / `training training`), and
  still read every hit before flagging.

## Fallback-detail redundancy

When a research detail falls back to a meta string ("the supplied listing places it in
{City}") and the opener **already** states name+location, the render is redundant and
machine-sounding: "I found The Foundry in Harvard, MA. I checked the site and noted the
supplied listing places it in Harvard, MA." Fix by making the fallback a noun phrase
("its Harvard location") or dropping the location clause when the opener already carries it.

## Grammar & localization merge-rendering defects

A second defect family the structural checks miss: **template slots filled by merge tags
render ungrammatically or in the wrong regional column.** These are per-lead editorial
errors, not structural failures, so machine QA reports "0 hard failures" while the copy is
still not production-ready. Catch them with a stratified manual read first, then quantify
cohort-wide:

| Class | Renders | Detection |
|---|---|---|
| Number agreement | "each have a preferred **plumbers**" (`a preferred {trade_noun}` + plural tag) | `a preferred [a-z ]+` then confirm tail is singular | no banned word, no doubled word, within word count |
| **Trade noun ≠ recipient trade** (cross-field off-by-one) | builder lead → "each have a preferred **plumber**"; electrician → "a preferred **chippy**"; aircon → "a preferred **sparky**" | read the merged noun against the row's own `trade` column — `each have a preferred (.+?)[,.]` and confirm the tail is in that trade's allowed set (`builder`→builder/chippy, `electrician`→sparky, `plumber`→plumber, `aircon`→air con/heat pump, `roofer`→roofer) | de-pluralizing the tag fixes number but NOT the mapping — singular-but-wrong noun passes a "is it singular?" check and still reads as a bot to 100% of leads |
| **Greeting inconsistency across the sequence** | same lead sees "Kia ora Alex," (step 1) → "Hey Alex," (step 3) → "Hi Alex," (step 7) | collect the greeting token (`body.split('<br>')[0]`) per step and per lead; flag a lead whose 12 greetings mix `Kia ora`/`Hey`/`Hi`, and flag lowercase first names ("Kia ora amy,") | structural checks pass; it's a voice/consistency miss only a per-lead read of the whole sequence catches |
| Article a/an | "need **a air con** company" | `\ba (air con\|aircon\|electrician\|insulation\|...)` |
| Lowercase-after-period | "need a builder. **sparkies**, plumbers and roofers." | `\. [a-z][a-z]+s?\b` (confirm it's a list fragment) |
| Regional swap missed | NZ aircon says "air con" not "heat pump"; AU lead "is on **Trade Me**" | count term/platform per `country` column vs the swap table |
| Empty merge tag | "works around **.**" | `around \.|near \.|in \.|for \.` |
| Sanitization fallback leak | "Saw **your place** works around X" | grep the fallback literal; read the relevance line |
| De-contraction drift | "who **is** sending" / "does **not** go" vs "who's"/"doesn't" | `\b(who is\|what is\|does not\|do not\|is not\|they are)\b` |

A systematic defect (100% of leads in one step) is a **FAIL** even with a clean structural
pass — a recipient clocks "a preferred plumbers" instantly. See
`references/grammar-localization-qa.md` for the full table, stratified-sample spec, and the
distinct-opener-count technique for proving openers vary by research.

## Pitfalls

- The generator may be re-run by a cron/gateway between your reads — check file mtime is
  stable before trusting a diff, and pin the artifact you're auditing.
- "0 empty fallback" can still mean the fallback is *rendered badly* — verify the fallback
  string's placement, not just its existence.
- Reproduce-then-diff is cheaper and more trustworthy than re-encoding template strings
  that can silently drift from the source.
- **research_detail label vs key:** generators often emit a *label* derived from a matched
  *key* (`"personal training"` → `"personal training sessions"`, `"climb"` → `"climbing"`,
  `"24/7"` → `"24/7 access"`). Re-map label→key before substring-matching the stored research
  text, or you'll flag thousands of genuinely-traceable details as invented. A detail is only
  "invented" if its *key* is absent AND it isn't an explicitly-labeled fallback (e.g. starts
  with `its listed location` / `the supplied listing`).
- **"No duplicate Reply CTA" = count the CTA word, not one phrasing:** a framework may use a
  valid-but-different CTA ("Reply with the answer"). Matching only `Reply info|math` falsely
  reports a whole framework's worth of bodies as CTA-less. The duplicate check is
  `body.count('Reply') > 1` (and `== 0` is a missing-CTA flag, a different defect).
- **"No duplicate opener" is a separate check from "no duplicate CTA":** assert the first
  body line (the opener/hook) appears exactly once in the body; a duplicated hook and a
  duplicated CTA are different defects. The CTA dup is `body.count('Reply') > 1`,
  case-sensitive, so a step-3 "reply pass and I will stop" breakup line is NOT a CTA.
- **Dollar-figure regex must stop at the number:** use `\$(\d+(?:,\d{3})*|\d+)`, not
  `\$\d[\d,]*`. The greedy form swallows the trailing comma in "The affiliate tier is $0,
  forever" and false-flags the approved `$0` figure thousands of times. Whitelist the exact
  approved figures (`$0`, `$2,000`, `$5,000`); anything else is a data token to read in
  context (e.g. `$3` inside the real name "F!ND YOUR PURPO$3", not a claim).
- **Adjacent-duplicate hits can come from the fallback location string**, not just a lead
  name: "its listed location in Walla Walla, WA" renders a doubled "Walla Walla" that is a
  *city*, not a template collision. Read the surrounding phrase, not just the matched words,
  before classifying any hit.
- **Traceability pool must match the generator byte-for-byte:** page `text` + `title` +
  `description` + every `social_research` entry with `status=='ok'`. A validator that uses
  only `text`+`title` (dropping `description`/social) false-flags details whose keyword
  lives in a page description or a fetched social profile — the shipped `final_fast_qa.py`
  had exactly this defect.
- **Cross-lead template-swap (live 2026-09-06, FAP rewrite batch):** per-body QA can be fully green while every lead in one campaign gets the same skeleton with the company name swapped — opener varies, pain+offer paragraphs identical. Justin's exact complaint ("email 1 says the same thing for everybody, it just personalizes it to their business"). Detect with pairwise Jaccard on word sets (len>3) of bodies, company/city names stripped, compared per framework key across leads; threshold ~0.45 flags true template-swap (genuinely custom copy sharing only the framework angle lands well under 0.40, template-swap lands 0.6-0.9). Two mandatory adjudications before trusting the number: (1) strip framework-CANONICAL sentences (a framework doc's designated lines, e.g. the news line "on July 23 and 24 an FDA panel voted yes on the peptides your {noun} already talk about" — these are ALLOWED to repeat and otherwise inflate similarity to 0.6-0.9 by themselves); (2) token normalization: strip trailing punctuation in the word regex so "BMX." matches the acronym allowlist, and allowlist legitimate all-caps (FDA, NYC, company names like ASTIG, VIP, IV, GLP-1). Script: `scripts/cross_lead_similarity_check.py`. Fix is a full editorial rewrite from fresh per-lead research — never a threshold fudge. Writer briefs reduce but do not eliminate this defect; at least one writer reproduced it despite an explicit "rephrase the offer paragraph every time" rule. Fix workflow (fresh per-lead live research, writer personas with a binding brief, mandatory editor differentiation pass, Instantly PATCH push, review-page delivery): `references/editor-bench-rewrite-workflow.md`.
- **Wall-of-text bodies break platform rendering:** writers on fast models emit some or all emails as a single paragraph. Per-body QA (word count, banned words) is green while the send-platform editor renders one collapsed block (raw \n\n is whitespace in HTML; the verified Instantly fix stores `<br><br>` between paragraphs). Gate: every body must contain \n\n (framework emails are multi-paragraph by design); follow-ups/closers may be intentionally single-paragraph, so assert per-step expectations rather than a blanket count.
- **Traceability sampling on framework email 1:** the opener of fw1 is the canonical news line, not a research detail — naive "do opener tokens appear in the lead's research text" checks false-flag it. Strip canonical lines from paragraph 1 before sampling tokens, and strip punctuation from tokens ('included.' ≠ 'included' in page text).
- **Cross-step collapse & track leakage (live 2026-09-03, 30k-lead build):** per-body QA can
  be fully green while one lead sees the same opener in all 10 framework emails, the same
  close line 6x, and grow-track leads get "no charge for the setup" in shared follow-ups.
  Fix in the composer with per-lead used-opener/used-close sets + pools sized larger than
  the step count, and scan ALL steps (not just framework emails) for track language. Full
  defect table, detection thresholds, banned-word exceptions for lead identity fields
  (company "Synergy Fitness", city "Price, UT"), the company-name scrub, and the
  timed-out-second-agent salvage path: `references/cross-step-collapse-and-track-leakage.md`.

## Verification

- Reproduced artifact byte-identical to shipped artifact.
- Every check returns an exact integer count (not "some", "a few").
- Manual sample read confirms tone/grammar, not just structural pass.

## Support files

- `references/deterministic-copy-qa.md` — full recipe with code snippets and the defect table.
- `references/grammar-localization-qa.md` — grammar/localization merge-rendering defect classes,
  stratified-sample spec, and the distinct-opener-count variation check.
- `references/cross-step-collapse-and-track-leakage.md` — per-lead cross-step component
  collapse, track-language leakage through shared templates, lead-identity banned-word
  exceptions, and second-agent sweep salvage.
- `scripts/cross_lead_similarity_check.py` — runnable gate for the cross-lead template-swap
  defect class: pairwise Jaccard per framework key with canonical-line stripping, name
  removal, and hard-rule checks (word count, dashes, links, tokens). JSON in, exit 1 on flags.
- `references/editor-bench-rewrite-workflow.md` — the fix path when the gate fires: fresh
  per-lead live research, writer-persona bench with a binding brief, mandatory editor
  differentiation pass, QC gates, Instantly PATCH push with byte-exact verification, and
  here-now review-page delivery.
