# Editor-Bench Rewrite Workflow (fixing cross-lead template-swap)

The companion to the cross-lead template-swap DEFECT in SKILL.md pitfalls: how to actually
fix a corpus that failed the similarity check. Proven live 2026-09-06 on a 10-lead x 10-email
cold-email batch (100 emails, all gates green, pushed + verified in Instantly).

## Trigger

User reads the campaign and says "each email says the same thing, it just personalizes it to
their business" — or the Jaccard gate fires. The fix is a full editorial rewrite from fresh
per-lead research. Never a threshold fudge, never a paraphrase pass over the same skeleton.

## Phase 1 — Fresh live research per lead (do not reuse stored research)

Re-fetch each lead's site the day of the rewrite: homepage plus /about, /about-us, /pricing,
/schedule subpages (threads of ~5, browser UA, gzip decode, strip script/style, collapse
whitespace). Rich homepage text (>=800 chars) = researchable lead. Grab contact emails from
raw HTML for owner-name candidates. Store as {email: {pages: {home:..., about:...}, ...}}.

The goal is material an editor can actually use: programs, neighborhoods, mottos, team
pages, community events, pricing models. "Keeps coming up in muay thai circles" is not
research; "Wednesday night dinner rides through West Burlington" is.

## Phase 2 — Writer bench (personas, not one mega-prompt)

Build per-writer packets: {lead: {company, city, state, vertical, track, framework_order,
slots: [{step, fw, angle, pain, signature-line rules}], research_pages}}. Slots carry the
framework doc's angle + pain + which signature lines are allowed where.

Writer brief must be BINDING and include: sender persona (who is "I"), offer facts with
usage budgets (revenue line only in frameworks X/Y/Z, full safety stack only in its home
framework, dated news line only in its designated slot), track discipline (grow-track leads
get ZERO setup language), hard rules (50-100 words, one research detail + one pain per
email, no dashes/exclamation marks/links, lowercase 1-4 word subjects, no parallel
three-item lists, every email stands alone), banned-word list, the "one ask, reply-trigger
close" pattern, and the paragraph contract (1-3 sentence paragraphs separated by blank
lines — this becomes <br><br> on the platform).

Output contract: one JSON file per writer, {lead_email: {fw_key: {subject, body}}}.

Assign 2-3 leads per writer. A 4-lead assignment on a fast/cheap subagent model stalled and
timed out twice (600s leaf limit); 2-3 leads completed cleanly. Demand incremental file
writes (after each lead, not one dump at the end). Salvage path when a writer dies: the
orchestrator writes the missing leads itself — it already has the research packets in
context, and one consistent editor voice beats a re-dispatch gamble.

## Phase 3 — Editor differentiation pass (the step that actually kills sameness)

Writers will STILL converge on framework-canonical pain/offer blocks (one of three writers
reproduced template-swap despite an explicit "rephrase the offer paragraph every time" rule;
another landed 0.9 similarity on fw1/fw7). So the orchestrator re-reads every flagged pair
and rewrites by hand, keeping the research-anchored opener and replacing the shared
middle/close with business-specific phrasing (their programs, their town, their words —
"clients" for trainers, "students" for pilates, "fighters" for boxing, "the academy" for
martial arts, "the pack" for a community-brand gym).

Then mechanical trims via exact-substring replaces (word counts 50-100), banned-word
scrubs, and paragraphization of any wall-of-text body (writers on some models emit
single-paragraph emails; split on the logical beats: opener / pain+offer / close).

## Phase 4 — QC gates (all must be green before push)

Run scripts/cross_lead_similarity_check.py plus:
- word counts 50-100, no em/en dashes, no exclamation marks, no links, no ALL-CAPS except
  an allowlist (FDA, NYC, drug codes like BPC-157/TB-500, the lead's own brand tokens
  compared against the company name with punctuation stripped)
- framework-canonical line budgets: dated news line in exactly its designated framework,
  revenue line only in allowed slots, full safety stack only in its home framework
- track discipline (grow leads: zero setup language anywhere)
- no sentence >=8 words reused within a lead; no wall-of-text bodies (every body has \n\n)
- traceability: opener detail traces to that lead's research text (strip canonical lines
  and trailing punctuation before token-matching)

## Phase 5 — Push to the sending platform (Instantly)

UPDATE stored copy via `PATCH /api/v2/leads/{id} {"custom_variables": {...}}` — never
delete-then-re-add (bulk DELETE only unassigns; duplicate leads/add is silently ignored
with `duplicated_leads` counting them, stored payload unchanged). Convert \n\n to <br><br>
and single \n to <br> in every body. Keep framework emails from the writer output,
follow-ups/closers from the existing corpus with the same <br> conversion. Then verify
byte-exact: re-fetch each lead's payload and compare every subject and body to expected.
Campaign stays PAUSED throughout; zero sends until user approval.

## Phase 6 — Review page, not chat dump

100 emails do not go into the chat (user: "publish to here.now, not in this thread").
Render an HTML review page grouped by business (company header, track/vertical/city tags,
each email labeled with step number + framework angle, paragraphs as <p>), publish via
here-now, verify the live URL serves all leads, drop only the link in chat. Keep the URL
slug + claimToken in a local state file for updates.

## Pitfalls

- writer-bench QA cannot replace the orchestrator read: writers self-report "all clean"
  while sharing skeletons across leads. Always run the cross-lead gate and READ the pairs.
- verification expectations must match the design: if follow-ups are intentionally
  single-paragraph, "all 22 bodies have <br><br>" fails 10/10 good leads. Assert per-step
  expectations, not a blanket count.
- PATCH is per-lead (id from leads/list search). Rate is fine (~0.5s spacing, 10 leads).
- here-now publish.sh needs jq; if absent use the Python flow (POST /api/v1/publish with
  files manifest + hash -> PUT each upload.url -> POST finalizeUrl WITH Authorization
  header; update existing slug via PUT /api/v1/publish/{slug}).
