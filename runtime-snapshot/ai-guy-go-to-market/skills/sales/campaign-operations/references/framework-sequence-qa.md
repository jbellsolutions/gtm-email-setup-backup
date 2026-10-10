# Framework-Specific Sequence QA (machine + editorial + second-agent review)

Concrete QA design for multi-framework cold-email sequences — each framework is a
distinct angle/sequence rendered per-lead. Produced for the GYMS Connect Med One build
(10 frameworks, `Framework 1..10`), but the check taxonomy is reusable for any
multi-angle sequence build.

Reference implementation: `/opt/data/qa_sequence_machine.py` (deterministic, no-network
self-test on canonical copy; `--input rendered.json` for real per-lead bodies; `--json`
for machine-readable report). Design doc: `/opt/data/QA_DESIGN_sequence_frameworks.md`.

## Canonical sequence shape (single source of truth = the build script's strings)
- Step 1 (intro): `hook` + blank + `core` + blank + `close`
- Step 2 (follow-up): `hook` + blank + (`follow` + `" Worth a look?"`) + blank + `FIXED_CLOSE`
- Step 3 (breakup): `hook` + blank + (`follow` + `" If it is not relevant, reply pass and I will stop."`) + blank + `FIXED_CLOSE`
- `FIXED_CLOSE` is one shared close line. Step depth varies per framework — verify against
  the build, never assume a uniform N (an earlier audit script wrongly assumed 3 steps for all).

## Check taxonomy
### Framework fidelity (HARD_BLOCK)
Step depth per framework; subject exact (`X` / `re: X`, lowercase, ≤4 words); body opens
with the verbatim hook (company+city merged); step-1 body contains `core[i]` and `close[i]`
verbatim; step 2/3 contains `follow[i]` + correct suffix; `FIXED_CLOSE` appears **exactly
once**; three sections separated by exactly two blank lines; no unrendered merge tokens
(`{c}`, `{place}`, `{{email_*_*}}`).

### Spam rules
- Banned single words → REVIEW (context-dependent; `get/medical/now/new` fire but are
  descriptive, not promotional — adjudicate, never auto-clear).
- Banned phrases + high-risk promo wording → HARD_BLOCK.
- Formatting bans → HARD_BLOCK: em dash `—`/`–`, `!!`, greeting prefix `Hi <Name>,`,
  any URL/anchor `https?:// | www. | <a` (text-only campaigns). ALL-CAPS runs → REVIEW with
  a whitelist (`MyConnectedMed, GLP-1, US, LegitScript, FDA, AI, TRT`).

### Word counts (measure from canonical copy, don't guess)
intro 60–110, follow-up 45–95, breakup 45–95, subject ≤4 words. Out-of-range → REVIEW
(padding to a floor is worse than a short honest line); 0 words / missing section → HARD_BLOCK.

### Banned claims — approved-offer-facts whitelist + regex rules
Whitelist only the approved facts (e.g. "licensed providers make every clinical call",
"US pharmacies", "LegitScript certification", "$0 forever", "$2,000 to $5,000 or more a
month" framed as "built to add"). HARD_BLOCK: `guarantee[ds]?`, `will (make|earn|generate|profit)`,
`(no risk|risk[- ]free|zero risk)`, `cures?/treats/clinically proven`, `fda[- ]approved`,
`\d+% (weight|fat|loss)`. REVIEW: gym-practices-medicine inversions, unapproved numeric
metrics, absolute outcome qualifiers, unapproved dollar figures.

### Uniqueness + structural diversity (uniqueness is not enough)
- Within-framework: bodies unique iff no `(company, city)` collision per framework.
- Cross-framework: `CORES/CLOSES/FOLLOWS/SUBJECTS` pairwise disjoint; distinct subjects.
- Near-duplicate cores: Jaccard word 2-shingle ≤ 0.6 (REVIEW 0.4–0.6, HARD_BLOCK >0.6).
- Rhythm: per-email sentence-length variance > 0 (no uniform block).
- Template shape: count distinct `(hook_len, core_len, close_len)` signatures — report,
  don't hide (10 distinct shapes = genuine variation, not one skeleton with swapped words).

### Second-agent review sampling
Run after machine QA is green and the writer fixed its own flags. A separate agent that did
NOT write the copy re-runs the machine script + editorial judgment. Stratified: all
frameworks × 1 lead + `max(2, ceil(0.5%))` random per framework (cap 10). Reproducible
primary seed from `sha256(sorted(campaign_ids))` + one fresh random redraw. Verdict
PASS / PASS-WITH-FIXES / FAIL; FAIL blocks upload and escalates; the reviewer never
auto-overrides a HARD_BLOCK.

## Pitfalls (all observed live)
1. **Duplicate CTA:** a `follow` string that already ends in the fixed close, plus the
   appended `FIXED_CLOSE`, renders the CTA twice. Assert "fixed close appears exactly once."
2. **Step-depth mismatch:** stale audit scripts assume a uniform step count; the actual
   build may differ per framework. Read the build's step depth.
3. **Banned-word false positives:** `get/medical/now/new` are descriptive here; classify
   REVIEW and adjudicate, don't auto-block.
4. **Dollar whitelist:** strip trailing commas and approve the exact range
   `$2,000 to $5,000 or more a month` plus `$0`, else `$0,` / `$2,000` falsely flag.
5. **Absolute-qualifier false positives:** "every clinical call" is an approved offer fact,
   not an overclaim — whitelist approved phrasing rather than banning bare `every/all`.
6. **Relevance-line phrase duplication:** an opener/hook template that already contains a
   fixed phrase (e.g. `I checked {domain} before writing`) plus an unconditional append of
   that same phrase renders it twice. Observed live on 90% of one rebuilt cohort (5 of 8
   opener variants already carried the phrase; the append doubled it). Assert every fixed
   opener phrase occurs **exactly once** per rendered body.
7. **Merged research-detail grammar:** dropping a per-lead detail into a template slot can
   break the sentence when the detail is not a complete clause. A CSV fallback
   `"{Company} in {City}"` yields fragments (`"stood out because {Company} in {City}."`), and
   a `"the site lists {kw}"` detail yields `"The page points to the site lists X."` /
   `"I saw the site lists X on the {Company} site."`. Render-check a sample of **every opener
   variant × every detail tier** (site-keyword vs CSV fallback), not one aggregate sample.
8. **Machine-QA blind spot:** scripts that only scan banned words, dashes, tokens, and word
   counts (e.g. a `qa_*.py` checking those four) cannot catch duplicated phrases, duplicate
   CTAs, or broken merged-slot grammar. The independent second-agent must explicitly grep for
   repeated fixed phrases and duplicate CTAs, and read a stratified sample itself. Do not trust
   a "0 hard issues" machine report as proof of editorial soundness.

9. **Article agreement before vowel-initial nouns:** collapsing trade nouns into templates rendered "a air con company" (205/5729 leads in one build) and passed a word/dash/token scan silently. Add a cohort-wide `\ba\s+[aeiou]` check plus an article() helper in the generator; adjudicate hits that are real company names ("Zarama Air") before flagging.
10. **Singular/plural agreement in collapsed examples:** "a preferred {plural_partner_type}" (follow-up class). Any sentence that singularizes a list item needs a singular() transform, verified cohort-wide.
11. **Per-lead pairwise opener collisions across steps:** aggregate distinct-opener counts hide small collisions (19 leads had identical step-1 and step-7 openers because both hit the same platform-hint variant). Assert pairwise opener equality == 0 across all step pairs per lead, not just per-lead distinct counts.
12. **Country-swap idioms leak past structural checks:** NZ leads received "the footy" because only platform/council terms were swapped. Grep the swap table's idiom rows (sport, greetings, air con vs heat pumps) against each country cohort.
13. **Silent no-op patches:** a string replace that doesn't match leaves the defect in place while the session believes it fixed it (cost one full regen cycle). After every generator patch, assert the new substring exists AND the old substring is gone before regenerating.
14. **Artifact-scan false positives:** "around," matched the legitimate phrase "I'm around, and I'll..." in a breakup email (5,729 false hits). Read regex artifact hits in context before counting them as defects.
15. **Thin-research opener repetition:** leads with only one research signal repeated the identical relevance line across all framework emails (357/5729 in one build). Fix in the generator: rotate 2-4 phrasing variants per signal kind, indexed by step number. Assert a minimum distinct-opener count per lead across the multi-step cohort. (Also recorded in SKILL.md pitfalls.)
16. **Rendered word count includes greeting + signoff:** count the full rendered body ("Hey Dave," + "Cheers,"). A paras-only target of exactly the max lands at max+3 rendered. Set the per-paragraph trim target to max minus 3-4 words.
17. **Sentence-start caps after merged list fragments:** templates like "...need a {noun}. {joinlist(p)}." render lowercase partner lists after a full stop ("...need a builder. sparkies, plumbers and roofers." — 100% of leads in one build). Capitalize interpolated lists that open a sentence; grep `\. [a-z]{2,}` cohort-wide (ignore initials/abbreviations).
18. **De-contraction tone drift:** template strings written in full form ("do not", "what is", "they are") shipped 40k+ robotic constructions vs the framework doc's contracted voice. Run a contraction pass in the formatter (preserve sentence-start caps, watch for double-contraction artifacts like "don't't"), then grep each full form to zero, case-insensitive.
19. **Sanitized company names read templated:** banned-token stripping turned real names into "your place" in rendered copy ("Saw your place works around Nunawading."). Prefer a natural fallback ("your business"), keep the count low, and flag sanitized leads explicitly in the review handoff.
20. **Re-review scoping after fixes:** re-verification does not need a full re-read of the framework doc. Dispatch a fresh leaf reviewer scoped EXACTLY to the flagged defect classes (each as a cohort-wide regex check, expected count 0) plus a small regression battery (word count incl. greeting+signoff, subjects, banned words, dash/link/exclamation) and 3-4 full lead spot-reads (mix named/generic/fallback cohorts). Fast, and it closes the loop the FAIL opened.
21. **Company/city identity fields inject banned tokens legitimately** ("Synergy Fitness", "Price's Academy", "Price, UT"): QA exceptions must check the token against the lead's company (possessives stripped) and City/State before flagging; the composer must scrub `!`, `$`, en/em dashes, and `dba/LLC/&`/`of`-clause tails from interpolated names, else punctuation bans and word-count bands fire on hundreds of leads.
22. **Hit word bands by construction, not trimming:** with component-pool composers, run a deterministic combo search per email (opener × pain × offer × close variants → first in band, fallback shortest + compact close variant). Post-hoc trimming took six QA cycles; combo search landed 1,999/2,000 on the first pass. Re-run the full rebuild + QA after any pool change.
23. **QA the QA script after any format change:** when the corpus gains a field or a step type changes (e.g. empty subjects on even reply-in-thread steps), rerun a known-good fixture through the QA script — stale assumptions produced 30k identical false positives that masked real defects in the noise.

## Baseline findings (2026-09-01, canonical copy)
4 hard blocks (duplicate CTA in Framework 1 step 2, Framework 5 step 2, Framework 10 steps
2 & 3); 9 review flags (`get` fw1,7; `medical` fw3,7,9,10; `now` fw7; `new` fw6);
diversity 10/10/10/10/10 distinct subjects/hooks/cores/closes/follows; 0 near-duplicate
core pairs; 10 distinct template shapes.

## Second-agent rebuild findings (2026-09-01) — why the machine gate was NOT enough
The rebuilt per-lead generator (a research-detail injected into the opener + a per-step
CTA close) passed a word/dash/token/banned-word-only machine scan with "0 hard issues", yet
an independent second-agent pass found two systemic failures across the full 7,825-lead
cohort:

- **Duplicate "I checked {domain} before writing"** in ≥1 step: 7,061 / 7,825 (90.3%) — the
  opener template appended the phrase even though 5 of 8 opener variants already contained it.
- **Duplicate CTA "Reply info and I will send the one pager"** in the follow-up: 3,145 / 7,825
  (40.2%), i.e. every lead in frameworks 1/3/5/7 — the follow-up suffix list AND the step-2
  close both began with the same CTA string (a different mechanism from pitfall #1, but the
  same class). Only 424 leads (5.4%) had neither defect.
- Broken merged-slot grammar on a large share of CSV-fallback openers (pitfall #7).

Verdict: **FAIL — do not upload.** The mechanical fixes live in the generator, not the QA
script: remove the double append of the fixed opener phrase; don't append a CTA suffix when
the close already opens with that CTA; make the CSV-fallback opener read grammatically when
the "detail" is just `{Company} in {City}, {State}`.
