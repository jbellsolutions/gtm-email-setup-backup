---
name: campaign-operations
description: "Use for outbound campaign builds with QA and launch gates."
version: "1.0.0"
author: hermes
metadata:
  hermes:
    tags: [campaigns, outbound, personalization, QA, Instantly]
---

# Campaign Operations

Use this class-level workflow when building multi-step outbound campaigns in a sending platform with per-lead copy, account/tag routing, campaign chaining, and manual review before launch.

## Operating contract

- Preserve the user's approved or verified email source as the sole send-address authority. Enrichment files provide context only and never replace the verified address.
- Build review-safe: create campaigns paused, never activate or send before explicit approval. A positive reply is not permission to send the next reply.
- Separate source reconciliation, research, copy generation, platform configuration, lead import, and verification.
- Treat an API response as evidence only for the operation it confirms. Creation does not prove lead import, variable rendering, chaining, or delivery.
- Report exact counts for every stage, including held records and rejected batches.
- Scope the offer to the actual campaign and vertical before drafting. Do not reuse a neighboring offer, case study, or campaign identity merely because the reply daemon labeled it that way.
- When the user explicitly confirms a lawful/authorized basis for a supplied list, record that confirmation in the campaign worklog and do not repeatedly re-ask unless new contradictory evidence appears.

## CRM destination and source-access preflight

Use this gate before exporting campaign replies into a CRM or other contact system:

1. Distinguish a **contact-detail URL** from a **location/workspace import destination**. A URL containing a specific contact ID proves only navigation context; it is not evidence of the target location, import route, or write permission.
2. Verify the source platform independently before designing the export. A locally installed CLI is not proof of valid access: run a read-only authenticated health/list request and preserve the exact status. If authentication fails, stop before pulling or transforming records.
3. Verify the CRM credential and destination separately. Do not infer a private integration token from a browser login or from the presence of an app URL. Require the correct location ID, API scope, and documented contact create/update endpoint or an authenticated UI import path.
4. Begin with a **read-only dry run**: identify the exact campaign scope, count replies, inspect the available fields, and produce a field-mapping preview. Do not write contacts until the destination, source, and record scope reconcile.
5. Preserve all source fields in an auditable export, especially phone numbers, sender/recipient addresses, timestamps, campaign IDs, thread/message IDs, reply text, and classification. If a phone is absent or masked, record it as unavailable rather than inventing or silently dropping the field.
6. Import opt-outs, hostile replies, OOO, and negative replies only when the user explicitly requests all replies. Preserve their status/suppression meaning so they are not treated as active prospects or re-enrolled in outreach.
7. After writing, re-query the CRM and reconcile submitted, accepted, updated, skipped, and failed counts. A successful request or UI toast is not proof that every contact or field was persisted.

## References

For the reusable evidence boundaries and dry-run checklist for reply-to-CRM migrations, see `references/reply-crm-migration-preflight.md`.

## Verified Instantly campaign-build workflow

For a user-provided verified-email CSV plus a separate enrichment CSV:

1. Preserve the verified CSV as the sole send-address authority. Match enrichment by exact email first, then exact domain only as labeled context. Never replace a verified address with a public email found in enrichment.
2. Hold generic role addresses and records without a defensible company/domain match. Do not research or personalize from an email local-part alone.
3. Create the campaign with the requested account tag, explicitly pause it, and re-fetch it. Creation status is not evidence of a paused state.
4. Upload personalized leads through `POST /api/v2/leads/add` in batches of 50 or fewer. Include `email`, `first_name`, `last_name`, `company_name`, `website`, and `custom_variables`.
5. Verify with `POST /api/v2/leads/list` using the filter key `campaign` (not `campaign_id`) and cursor pagination via `starting_after`. Assert every returned lead belongs to the new campaign and the final count equals the accepted count.
6. Use complete per-lead custom variables only after a controlled render check. Preserve paragraph breaks as `<br><br>` when needed.
7. If a campaign is created with incorrect state or content, delete it with `DELETE /api/v2/campaigns/{campaign_id}` and verify `GET /campaigns/{campaign_id}` returns 404 before recreating. Never continue uploading to a stale campaign ID.
- Leave the campaign paused for review. Activation is a separate explicit action and must never be inferred from upload completion.
- Before activation, complete Instantly UI render-preview verification on sampled records. If the UI cannot be authenticated or preview evidence cannot be captured, stop and report the blocker; do not activate merely because API persistence checks pass.
- When a daily target is specified, allocate the smallest disjoint set of explicitly authorized, ready inboxes per campaign that meets the target. Re-fetch and verify exact tag membership, readiness, disjointness, per-campaign capacity, Draft/Paused state, and no-send status before activation. A useful pattern is to partition a tagged pool deterministically into disjoint groups and verify each group's sum of actual per-account limits meets the campaign target.
- Treat user activation approval as necessary but not sufficient: machine/editorial QA, sampled render verification or explicit operator review of the rendered copy, account readiness, and campaign configuration must all pass first. Record which evidence satisfied the render-review gate.
- After activation, re-fetch every campaign and verify `status == 1`; then query message-level records separately. Active status confirms launch, not delivery. Report the campaign as queued/not yet confirmed until an `/emails` record proves an actual outbound message.
- For a ten-campaign target of 50/day, five disjoint inboxes can be sufficient when each group has at least 50/day aggregate capacity. Do not attach the entire tagged pool when smaller disjoint groups satisfy the target.
- A successful activation batch may partially activate before a later response/parser error. Always audit all target campaign IDs after any interruption and treat already-active campaigns as idempotently complete rather than retrying blindly.
- Pause and campaign-listing evidence shapes, plus the verified 22-step one-campaign sequence payload (ten frameworks + ten follow-ups + two closers), are recorded in `references/pause-listing-and-22step-evidence-2026-09-03.md`: pause requires re-fetch status 2 AND `sending-status` = `campaign_paused`; `GET /campaigns` caps at 100 and silently hides campaigns beyond page one (assert the expected target count); `POST /campaigns/list` is not a route; paginate via `?limit=100&starting_after=`; escape the literal `|` in campaign-name regexes.
- Same-lead-list rebuilds may reuse a prior research corpus only after exact reconciliation (union counts must match with zero missing and zero extra). Re-crawl only unreachable/thin pages, then classify each lead individually (vertical, one verifiable detail, offer-track flags such as already-reselling) before generating framework copy.
- For the re-crawl step, run `scripts/refresh_research_corpus.py` (bundled): it takes the lead CSVs + research JSONL, retries only unreachable/thin pages with HTTPS→www→http fallback and a browser UA, and rewrites the corpus in place.
- To hit hard word bands from a component-pool composer, run `scripts/component_pool_composer.py` (bundled): deterministic combo search (opener × pain × offer × close → first in band, shortest-combo fallback) plus the company-name scrub and the banned-token QA exception pattern.

Reference: `references/instantly-campaign-build-2026-08.md` contains the verified endpoint shapes, reconciliation pattern, and evidence boundaries from the marketing-agency build. For approval-gated reply sending, duplicate prevention, `ue_type` interpretation, rate-limit-safe verification, and minimal QC edits to user-supplied copy, see `references/instant-reply-send-verification.md`. See `references/instanty-charles-msp-build-lessons.md` for tagged-account selection, campaign-wide pause consequences, and the hard pre-upload QA gate. For the nine-step partner-sequence rebuild pattern and QA checks, see `references/mamas-and-minis-9-step-rebuild.md`; for the twelve-step single-campaign shape (10 frameworks + 2 follow-ups, per-lead country swap, sanitization pitfalls, and QA threshold math), see `references/multi-framework-12-step-rebuild.md`.

## Solar affiliate / power-partner campaigns

Use this workflow when a solar installer is being offered Main Street Affiliates rather than an Owned Audience service:

1. Build a one-page explainer around a 100-level-deep partner map: Tier 1 complementary home services (roofing, electrical, HVAC, remodeling, windows, insulation, batteries/generators); Tier 2 property and transaction professionals (real estate, mortgage, inspectors, property managers, builders); Tier 3 trusted homeowner-adjacent businesses (landscaping, tree service, pools, pest control, security, insurance, restoration); Tier 4 scalable channels (associations, employers, credit unions, chambers, developers, local media, nonprofits).
2. Explain the operating sequence plainly: research and map businesses → recruit affiliate partners → create scheduled/orchestrated email, text, newsletter, or event promotions → run campaigns → route leads to the installer → installer closes → commissions are paid only on agreed closed sales.
3. The offer may state a guarantee of at least five referral partners in the first 90 days and a 5x return or no payment only when those terms are explicitly supplied by the user. Put measurement, attribution, tracking window, and return definition into the final commercial terms.
4. Research the recipient's actual company, service area, and local market before inserting statistics, named businesses, or projections. If the service area cannot be verified, use explicit placeholders and say what remains unverified; never invent local numbers.
5. Keep the one-pager useful as a review artifact: include a market snapshot table with source/method fields and label projections as illustrative assumptions, not guaranteed lead counts.
6. For positive-reply drafts in this offer, use direct language such as “Thanks for the quick reply.” Never use “thank you for getting back to me,” apologetic/sensitive language, or the Owned Audience framing. Do not send or auto-reply while the user asks to review first.

Reference: `references/solar-power-partner-workflow.md` contains the reusable one-pager structure, category map, research gates, and reply-copy rules.

## Source reconciliation

1. Normalize verified-source emails to lowercase.
2. Match enrichment/company files by exact email first.
3. Use domain matching only as a labeled fallback. Never present a domain-only match as an exact contact match.
4. Assert source count equals unique count, output union equals the source set, partitions have zero overlap, no output email is outside the source, and syntax is valid.
5. Preserve unmatched records separately. If later research resolves them from the domain or website, keep the original verified email unchanged.
6. **Dual supplied lists are not enrichment.** When the user supplies two lists of the same companies (e.g. a personal-contact list and a public-email list) and instructs that every address be sent, the union is the send-address authority — a personal contact and the public address at the same company are separate recipients. The "never public enrichment emails" rule applies only to third-party enrichment appended by research, not to addresses the user explicitly supplied for sending. Confirm the send-every-address interpretation once, record it, and report overlap counts.

## Research and personalization

- Use one concrete, verifiable research detail per first-touch email.
- Never infer authority, city, service area, company identity, or business model from an email local-part alone.
- Domain research is acceptable for unmatched records, but mark it as website/domain research and hold unresolved, parked, unrelated, blocked, or ambiguous websites.
- Generate a copy-ready file containing the original verified email, context, website, research status, and all subjects/bodies.
- Never invent partner counts, revenue, conversion rates, installations, or case-study results.

## Copy QA

For every email, enforce the active framework's word range, reject em dashes and prohibited words, enforce lowercase 1–4 word subjects, require a question ending when specified, and allow only intentional platform merge tags. Run machine QA, manually inspect exact-email, domain-only, and held/researched cohorts, fix failures, and rerun complete QA.

**Uniqueness is not enough.** A deterministic rotation can create unique strings while repeating one obvious skeleton. When Charm-style variation is requested, vary the opening, middle argument, close/CTA, sentence rhythm, and pattern interrupt, while retaining one verified lead-specific fact. Measure both unique bodies and structural/template diversity; a nonzero QA issue count is a hard stop.

**Framework-specific sequence QA.** For multi-framework (multi-angle) sequence builds, run the full machine + editorial + second-agent design in `references/framework-sequence-qa.md` (machine script: `qa_sequence_machine.py`). Hard-block that bit us live: assert the shared fixed-close line appears **exactly once** per follow-up — a follow string that already ends in the fixed close will double it when the close is appended.

**QA the final rendered copy.** Scan again after inserting company/research fields and after every cleanup pass. Recheck word count, banned terms, subject casing/length, no-link policy, paragraph breaks, and merge tags across the full cohort. HTTP 200 updates do not prove copy quality.

**Sender identity gate:** Never assume `{{sender_name}}` resolves in Instantly. Verify the supported sender-name variable or obtain each selected mailbox's actual `from_name` through a rendered preview. Until then, do not call the campaign send-ready. If the requested campaign has no links, preserve that policy and use plain text such as `Check us out at SpeakerAgent dot AI`, not a URL or HTML anchor.

**Direct SpeakerAgent/Conference Alpha brief:** When the operator supplies the three-month podcasting proof point, five-agency Alpha cohort, and agency-partner framing, preserve those as approved offer facts. Default CTA is site discovery, Conference Alpha selection, and a reply for details. Do not invent a booking link, card requirement, or extra product feature.

## Platform configuration

- Discover current platform documentation before relying on old notes. For Instantly v2, documented endpoints include campaign creation, bulk lead add (`POST /api/v2/leads/add`, max 1,000/request), campaign pause, campaign subsequences, campaign variables, custom tags, and account filtering by tag.
- **Hard pre-upload gate:** do not upload leads until machine and editorial QA both pass. A generated file with unresolved banned-word, word-count, placeholder-name, research-quality, or formatting violations must remain local and the campaign must remain draft/paused. Never upload a "review batch" merely because the API accepts it. **Explicit user override:** if the user directly instructs you to upload the full supplied CSV despite held/generic/unresearched records, obey the upload instruction, but preserve the source rows, label the campaign as not fully researched/verified, report the held-risk counts, and do not describe the upload as personalized, verified, or send-ready. Keep the campaign paused unless activation is separately requested.
- For account ownership, use `GET /api/v2/custom-tags` to resolve exact tag IDs, `GET /api/v2/custom-tag-mappings` with pagination to enumerate tagged accounts, and `POST /api/v2/custom-tags/toggle-resource` with `resource_type: 1` to assign the campaign tag to an explicit account list. Re-fetch mappings and assert count and set equality.
- **Explicit user override:** if the user separately confirms that role-based addresses, catch-all addresses, and the platform's prior verification status are acceptable, record that authorization and include those records, while still reporting the composition accurately. Keep the campaign paused unless activation is separately requested.
- **Multi-angle campaign partitioning:** when a user requests several framework campaigns from one list, deduplicate the union, preserve first occurrence/source authority, deterministically partition recipients across angle campaigns, and report bucket counts and overlap removal. This avoids ten simultaneous threads from the same sender to one recipient while still testing all angles.
- **Exact campaign identity:** if one parent name is requested for multiple campaigns, use a stable parent prefix plus explicit framework suffixes and state that Instantly represents them as separate campaigns. Do not claim independent campaigns chain automatically unless native chaining is configured and verified.
- For campaign creation, use the documented `POST /api/v2/campaigns` schema. Set `email_list` explicitly, use a dedicated campaign tag in `email_tag_list`, configure variable-only sequence bodies, and verify the returned campaign status. Instantly status `0` is Draft, `1` Active, `2` Paused, and `3` Completed. Draft is the correct state for an approval handoff.
- **Activation is a separate endpoint action:** do not rely on `PATCH /campaigns/{id}` with `status: 1` to start a campaign. First PATCH the configuration (exact `email_list`, `email_tag_list`, and daily limits), then call `POST /api/v2/campaigns/{id}/activate`, and finally re-fetch the campaign to verify `status == 1`. A successful PATCH proves configuration persistence, not activation. Use `POST /api/v2/campaigns/{id}/pause` for the inverse action.
- **Campaign-wide pause warning:** `POST /api/v2/campaigns/{id}/pause` pauses the entire campaign, not only selected accounts. Before moving accounts out of active campaigns, enumerate each selected account's mappings with `GET /api/v2/account-campaign-mappings/{email}`, record every affected campaign, and state that all accounts in those campaigns will stop. Never describe this as pausing only selected mailboxes.
- Filter sending accounts by the exact user-specified tag, include tags in the response, assert every selected account carries that tag, and verify all pagination pages. Do not equate a provider code or a broad provider family with a custom tag: reconcile exact tag mappings and account records first. Disable tracking unless explicitly required. Keep schedules and sequences visible for review.
- Before attaching or launching, classify each selected inbox by `status`, `warmup_status`, `setup_pending`, `stat_warmup_score`, `daily_limit`, and `status_message`. A connected account is not necessarily send-ready. Treat disabled/error accounts, SMTP 550 access-denied status messages, warmup status 0, zero warmup score, or a daily limit of 1 as non-ready.
- For explicit warmup enrollment, use the documented background-job endpoint `POST /api/v2/accounts/warmup/enable` with the exact email list, poll the returned `/background-jobs/{id}` record to success, then set the requested warmup cap with `PATCH /api/v2/accounts/{email}` using `{"warmup":{"limit":N}}`. Re-fetch every account afterward. Warmup enrollment is not pre-warm completion: do not activate the campaign unless the selected inboxes already meet the stated pre-warm/readiness threshold.
- Configure auto-reply behavior separately from human reply behavior. Set `stop_on_auto_reply` according to the user's OOO rule while keeping human-reply suppression enabled when requested.

## Chaining

Prefer native subsequences or move-lead triggers on campaign completion without reply so OOO/autoreplies continue while human replies stop progression. Do not claim independent campaigns feed automatically merely because they were created. Verify the actual chaining objects. If chaining is not configured, say so and leave everything paused.

### Long partner-sequence correction

When the user asks for an ongoing partner campaign with three angles plus two follow-ups per angle, model it as **nine total email steps per lead**, not three campaigns or the default four-step sequence. Store a distinct per-lead subject/body pair for each step (`email_1_*` through `email_9_*`) and use variable-only campaign steps. Configure `stop_on_reply: true` and `stop_on_auto_reply: false` when the user wants human replies to stop the sequence but OOO/automatic replies to be ignored. Keep the campaign paused until the nine-step structure and rendered fields are verified.

A long sequence must still feel conversational: each angle gets a fresh initial message and two follow-ups that add a different question or practical detail. Do not pad short follow-ups with generic filler merely to hit a word-count range; instead, write a useful, lead-specific point and then run the framework's exact word-count rules.

## Lead import and variables

- Upload in documented-size batches with checkpoints.
- Store complete per-lead bodies in documented custom variables, preserving paragraph breaks as `<br><br>` where the renderer needs them.
- Upload only verified-source emails, never public enrichment emails.
- Re-query after every upload and compare accepted versus submitted counts. A 200 response alone is insufficient.
- Treat workspace lead-limit or plan-limit errors as hard stops. Do not retry blindly or claim completion; report the exact quota and partial state. The 403 carries the exact remaining count ("Lead limit reached. Reamining uploads: N." — typo in the live response); a **partial upload of exactly N leads succeeds** even inside a 50-lead batch (slice the batch to N, checkpoint it separately, e.g. "14p5"). The cap is **workspace-wide across all campaigns**, not per-campaign. Accepted shapes for the create payload that hit 400s live (schedules array, `timing: {from: "HH:MM", to: "HH:MM"}`, `steps[].type/delay/variants`, org-specific timezone enum) are in `references/instantly-v2-schema-quirks-2026-09.md`.

## Performance reporting

When asked for campaign statistics, separate the metric definitions before counting: messages/emails sent, unique recipients, replies/connected conversations, positive or buyer-intent signals, and confirmed meetings booked are different measures. Always state the reporting window and source freshness, and provide campaign-level and aggregate totals when available. Do not count a positive reply, a suggested meeting time, or a calendar-link mention as a booked meeting unless the booking is independently confirmed in the calendar/CRM. If the live platform query fails or authentication is stale, report that limitation plainly and label any locally cached report with its exact date range; never present cached figures as current or silently infer all-time totals from a partial-period report.

## Review handoff

Include campaign names/IDs, fresh paused status, selected tag and exact account count, copy path and QA results, submitted/accepted/held/rejected counts, verified versus unverified chaining and rendering, and an explicit no-send statement. Never activate or send when the user says they will review first.

## Separate-account handoff packages

When documenting or duplicating this operating system for another team, produce a portable package rather than modifying the originating account. Keep it account-independent: exclude API keys, account/campaign IDs, internal filesystem paths, private lead data, customer names, private metrics, and organization-specific claims. Include five explicit artifacts: skills, system/operating contract, end-to-end workflow, handoff/setup document, and copy-paste instructions for the receiving agent. State that the recipient supplies its own Instantly workspace, credentials, mailboxes, domains, offer, sender profile, suppression list, compliance basis, and approval owner. Provide read-only discovery and a starter API/client recipe, while keeping destructive operations and activation behind human approval. Verify the package by compiling scripts, checking skill frontmatter, running a sample QA fixture, scanning for credential leakage, and creating a checksumed archive. A copied document is not evidence of access or deployment in the recipient's account.

Reference: `references/separate-account-handoff.md` for the reusable package checklist and evidence boundaries.

## Research, personalization, and editorial gates

- A successful HTTP fetch is not the same as usable research. Inspect page content and classify it as a business-relevant detail, generic/parked/template content, unrelated domain, or fallback-only.
- Use social URLs only after entity classification. Skip personal profiles, platform placeholders, app-store links, tracking-only URLs, and unrelated accounts. Record fetched URL, evidence text, confidence, and whether the detail was actually used in copy.
- If the brief requires website/social research, a company name, city, or domain interpolation does not satisfy the requirement. Hold fallback-only records or label them explicitly as low-confidence instead of presenting them as researched.
- Uniqueness must be measured on final rendered bodies and follow-ups. Company/city insertion can make strings technically unique while leaving one obvious shared skeleton. Require structural variation and inspect representative records manually.
- Do not silently relax the user's requested copy constraints to make a machine gate green. If the source says 50–100 words or requires a question CTA, enforce it and report exceptions before upload.
- The second-agent review must be independent: sample every framework and both successful-research and fallback cohorts, trace each research detail to evidence, and block upload on unresolved hard failures.

## Pitfalls

- Campaign creation may default to non-paused. Explicitly pause and re-fetch.
- Use a documented allowed timezone if the API rejects a preferred timezone, and report it.
- A quota can reject a batch before any records are added. Preserve files for resumption.
- Variable persistence is not rendered-preview verification.
- **Observed live payload shape (2026-09-01):** lead custom variables returned by `POST /api/v2/leads/list` were under `payload`, not `custom_variables` or `customVariables`; audits must inspect `lead.payload`.
- **Duplicate CTA:** appending a fixed close to a follow string that already ends in that same close doubles the CTA. Assert the fixed-close line occurs exactly once per rendered follow-up body.
- **Relevance-line duplication:** an opener/hook template that already contains a fixed "I checked X before writing"-style phrase, then unconditionally appends that phrase again, doubles it (hit 90% of one rebuilt cohort). Assert every fixed opener phrase occurs **exactly once** per rendered body.
- **Thin-research opener repetition:** leads with only one research signal repeated the identical relevance line across all framework emails (357/5729 in one build). Fix: rotate 2-4 phrasing variants per signal kind, indexed by step number, so even single-hint leads get varied openers. Assert a minimum distinct-opener count per lead across the multi-step cohort.
- **Rendered word count includes greeting + signoff:** machine QA must count the full rendered body ("Hey Dave," + "Cheers,"). A paras-only target of exactly the max (e.g. 100) lands at 101 rendered. Set the per-paragraph trim target to max minus 3-4 words.
- **Source-field junk guards:** city/name/company fields from lead CSVs can contain URLs, "linkedin.com/...", doubled suburb names ("Drummoyne Drummoyne"), and country suffixes. Sanitize every interpolated field (URL/mailbox guard, adjacent-token dedupe with a whitelist for genuine double-barrelled towns like Wagga Wagga, trailing country strip).
- **Multi-token duplicated city strings:** "Smeaton Grange Smeaton Grange Australia" survives a single adjacent-dedupe pass. Loop the dedupe until the token list stops changing, then strip trailing country tokens (Australia, Zealand, NZ, AU).
- **De-pluralizing can hide a wrong-referent defect:** fixing "a preferred plumbers" to "a preferred plumber" passes grammar QA but is still wrong if the noun names a partner trade instead of the recipient's own trade. After any agreement fix, verify the referent semantically (a second-agent caught this after the grammar fix passed machine QA).
- **One greeting per lead, not per step:** randomizing the greeting inside the per-step generator mixes "Kia ora / Hey / Hi" across a single lead's 12-step sequence (91/91 NZ named leads in one build). Draw the greeting once per lead and reuse it in every step; capitalize lowercase-sourced first names ("amy" to "Amy") as the final name-cleaning pass.
- **Defaulted getters defeat presence checks:** a `city_or(lead)` helper that substitutes "your area" makes city truthy, rendering "runs jobs around your area" and inflating word counts. Presence-check the raw source field, not the defaulted getter.
- **QA false-positive whitelists:** word-boundary "a air" fires on company names ("Zarama Air", "Messina Air Conditioning"); doubled-word checks need whitelists for genuine double-barrelled towns (Wagga Wagga, Kurri Kurri, Gol Gol, Hei Hei) and letter-spaced initialisms ("G P P" yields "P P"). A subject character-class fullmatch `[a-z0-9 ']` false-fails hyphenated subjects like "the quote-off" — compare `s != s.lower()` instead. Read every hit before flagging.
- **Merged-detail grammar:** when a per-lead research detail is dropped into a template slot, the sentence can break if the detail is a bare noun ("stood out because {Company} in {City}.") or a "the site lists {kw}" string. Render-check every opener variant × every detail tier, not one aggregate sample.
- **Machine-QA blind spot:** a script that only scans banned words/dashes/tokens/word-count reports "0 hard issues" while missing duplicated phrases, duplicate CTAs, and broken merged-slot grammar. The independent second-agent must grep for repeated phrases + duplicate CTAs and read a stratified sample itself; never trust the machine count alone.
- **Intra-lead follow-up repetition (distinct from thin-research opener repetition):** long per-lead sequences (10 frameworks × email + follow-up) built from fixed follow-up templates produce "Hey there, following up" ×4-5 inside ONE lead's sequence even when every lead's copy is unique. Fix: rotate opening connectives per slot index (Quick one. / Circling back. / One more. / ...) and strip the greeting before rotation; machine QA asserts opener uniqueness within a lead, not just across leads.
- **Catastrophic regex freezes bulk crawls (GIL):** one unbounded regex (e.g. `<meta[^>]+name="description"[^>]+content=...` under `re.S`) goes quadratic on multi-megabyte tag-sparse pages and freezes an entire ThreadPoolExecutor that otherwise looks healthy (threads alive, sockets open, zero output for minutes; ~83% of one core). Small test batches pass because they miss the pathological page. Fix: bound inputs (`html[:60000]` head window, `[:400000]` body), string-`find` for meta extraction, bounded tag matches (`<[^<>]{0,200}>`), and time extract on the largest real pages before relaunch. Diagnosis path + validated resumable budgeted-crawl pattern (checkpoint JSONL, skip-done, `FETCH_BUDGET` clean exit; 23,707 domains in 8.8 min): `references/resumable-research-crawler.md`.
- Account results may be capped at 100. Verify cursor pagination and totals.
- When the user provides a daily target, use the smallest disjoint tagged-inbox groups that meet it rather than attaching the full tagged pool. See `references/account-allocation-and-api-evidence.md`.
- **When the user stresses per-lead individuality ("go through each lead individually, that's the most important thing"), that is a hard gate, not a tone preference.** Reusing prior research is allowed only after proving the corpus matches the current lead union exactly; re-crawl unreachable/thin pages; classify every lead individually (vertical, one verifiable detail from its own site, offer-track flags) before any copy generation. Do not substitute company/city interpolation or template rotation for per-lead research.
- **Framework-campaign step count is a user decision, and "all ten frameworks and two more follow-ups" means 12 sequential steps in ONE campaign** (Justin, 2026-09-03). When a count is ambiguous (10 frameworks vs 12 steps vs one campaign per framework), ask once before building; the GYMS one-campaign-per-framework partitioning pattern above is the fallback for separate-campaign requests only.
- **Smoke-test generators and bulk fetchers on a handful of records before the full run.** A research pass over 5,646 domains was wasted by a loop-precedence bug (`err=None` after a success-branch break) that a 3-domain dry run would have caught in seconds. Same for string-replace patches: assert the new substring exists and the old one is gone before regenerating.
- **Hit word bands by construction, not trimming.** When composing from component pools against a hard band (e.g. 50-100 words), do a deterministic combo search per email over (opener × pain × offer × close) variants and pick the first combination inside the band (85-100 target), falling back to the shortest combo and to a progressively-shorter close pool. Post-hoc string trimming cannot converge a component-pool composer (six QA cycles were needed before switching to combo search; it landed 1,999/2,000 in band on the first try). Keep a 3rd compact offer/close variant in every pool so long company+city names still fit, and re-run the FULL rebuild + QA after any pool change.
- **Banned-word QA false positives from the lead's own identity fields:** company names ("Synergy Fitness", "Price's Academy") and cities ("Price, UT") inject banned tokens into copy legitimately. Exception rule: strip possessives (`'`/`'`) and match the token against company + City + State before flagging. Related scrub: company names need punctuation cleanup before interpolation (`!`, `$`→S, split on en/em-dash/hyphen, strip `dba/LLC/Inc`/`&`-clauses/` of ` tails, cap at ~4-5 words) — raw names leaked 17 exclamation-mark and 14 dash failures and inflated word counts past the band on 280 leads.
- **User-dictated copy is verbatim-protected (Justin, 2026-09-03):** when the user dictates exact CTA/proof copy, insert it word-for-word and shield it from automated rewriters — a global contraction pass rewrote "I will get you" to "I'll get you" in every body until the CTA was swapped for a placeholder before rewrites and restored after. Grep the full cohort (all steps) for any invented proof/case-study line the user rejects ("solar company in the States", "short version" offers) and remove everywhere, then re-run word-count QA: a 4-word-longer CTA pushed 4,611 step-8 bodies over a 100-word cap and needed three targeted TRIMS entries to converge.

## References

- `references/instantly-v2-build-notes.md` contains verified API shapes and operational evidence from the first campaign-build run.
- `references/instantly-v2-schema-quirks-2026-09.md` contains the accepted `POST /campaigns` payload shapes discovered by iterating live 400 errors (schedule/timing/timezone, `sequences[].steps[].variants`), plus the workspace lead-limit 403 partial-upload behavior and a verified end-to-end 5,729-lead pattern.
- `references/instantly-v2-api-gotchas-2026-09.md` contains the verified workflow for replacing copy on already-uploaded leads (no update route exists — delete + re-add with count verification) and the verbatim-CTA protection pattern for user-dictated copy.
- `references/live-account-error-triage-2026-08-25.md` records the verified all-account pagination, grouped SMTP error signatures, and remediation boundaries from the first live Instantly account-error audit.
- `references/framework-sequence-qa.md` contains the machine + editorial + second-agent QA design for multi-framework sequence builds (fidelity, spam, word counts, banned claims, uniqueness, structural diversity, sampling) plus the duplicate-CTA and false-positive pitfalls.
- `references/research-personalization-gates.md` contains the evidence thresholds for website/social research, fallback handling, and the distinction between technical uniqueness and genuinely varied copy.
- `references/resumable-research-crawler.md` contains the catastrophic-regex/GIL debugging narrative, the isolation method (DNS → connect → fetch-only → extract on largest pages), the bounded-extract fix, and the validated resumable checkpoint/budget crawl pattern.
- `references/peptide-wave-22-touch-build.md` is the working state for the in-progress Fitness Affiliate Program build (30,331 leads, 24,710 with live-site research, 161 grow-track, copy engine + machine QA files, pending: word-count trim re-run → second-agent QA → upload → render verification). Resume there; do not re-litigate framework decisions.
- `references/trades-12-step-single-campaign-build.md` records the Trades Referral Partners (AU/NZ) build where the user explicitly ruled **12 emails total** (Frameworks 1-10 as researched emails + Day-3 + Day-14 follow-ups) in ONE campaign — the 12-step counterpart to the 22-step evidence file above. Covers dual-list union reconciliation (public vs personal emails as separate recipients, 5,495+372 with 138 overlap → 5,729), per-domain research-pass bugs (loop-precedence `err=None` crash that wasted a full 5.6K-domain pass — smoke-test 3 domains before bulk), banned-token company-name injection ("10X CONSTRUCTIONS", "Central HVAC Services" → `10x`/`hvac` in rendered copy), genuine doubled place names (Wagga Wagga, Hei Hei) vs source-data doubles, greeting+signoff word-count inflation, and `GET /campaigns` 403 without a browser UA. The second-agent FAIL on this build added QA taxonomy items 9-20 to `references/framework-sequence-qa.md` (article/plural agreement, sentence-start caps, country-swap idiom leakage, un-contracted tone, opener collisions, re-review scoping).
