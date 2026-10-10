# Peptide Wave 22-touch build — Fitness Affiliate Program (final state, 2026-09-03)

Consolidated end state of the one-campaign, per-lead-customized build from "Cold Email Frameworks - The Peptide Wave (Unbranded) v1". **Built, QA'd, uploaded, reconciled, paused.** Campaign sends nothing until Justin activates.

## Platform state (verified live, end of session)

- Campaign: **Fitness Affiliate Program**, ID `572c363c-d2d9-40fe-ad11-9a7891fa3a95`, **Paused** (status 2).
- Leads: **30,331 uploaded** (batches of 50, `POST /leads/add` with `custom_variables`), reconciliation via `POST /leads/list` (`campaign` filter, 305 pages): **30,331 returned, 30,331 unique emails, 0 missing, 0 extra, 0 duplicates**. Sampled `lead.payload` carries `email_1_subject`..`email_22_body`.
- **The ten `GYMS Connect Med One | Framework N` campaigns were DELETED** (Justin-directed consolidation: "just this one campaign with one set of leads"). Each was asserted paused + exact-name regex before `DELETE /campaigns/{id}`; re-list confirmed 0 remaining and exactly one FAP campaign. Do not recreate them.
- Open question left with Justin: campaign `daily_limit` was configured at 100/day; he earlier spoke about ~1,000/day across the 100 puzzle inboxes now that all leads are in the single campaign. Bump on request; activation is separately gated.

## QA state at upload

- Machine QA (`fap_machine_qa.py`): **0 issues across 30,331 leads, exit 0** (structure 22/22, word bands, subjects, dashes/links/banned words with company+city exception, tokens, brand leak, safety element, track consistency, duplicate CTA, news-line cap, revenue placement).
- Independent sweep (`fap_qc_independent.py` — authored by a second-agent subagent, executed directly after it hit its 600s timeout): 0 duplicate full sequences, 0 exact-duplicate framework emails across leads, grow-language 0/161 after the FU10 fix.
- Traceability: 100% of personalization details verified against `fap_research_final.jsonl` page text (15,815 discipline/program + 3,998 fallback signals + 37 retail, 0 untraced). Research coverage 24,710/30,331 (81.5%); 5,621 dead domains use location-based openers.
- **Known cosmetic residual (accepted, disclosed to Justin):** a few leads see the same short CTA line ("reply setup for the rundown.") in 2-3 of their 10 follow-ups. Only detectable by cross-email sentence diffing; normal for template-assisted follow-ups. If Justin objects, fix is per-lead used-close tracking extended into FU bodies (it currently covers framework-email closes only).

## Framework decisions (unchanged, do not re-litigate)

- 22 touches: 10 framework emails + 10 follow-ups + 2 closers, one campaign. Grow-track leads (site advertises peptides/GLP-1s/medical weight loss, 161) get Alt C first + grow-variant language; #9 (the map) swapped out everywhere (map counts never researched); Alt A for parent-heavy verticals, Alt B for wellness/recovery/medspa. Only the framework email carries the lead's research detail.
- Client rules: no em/en dashes, no exclamation marks, no links, no brand names, banned-words list with lead-identity exception, lowercase 1-4 word subjects, framework emails 50-100 words, follow-ups 30-50, closers <50/<100, news line ≤3 framework emails, revenue line only in #7/#8/#10/Closer 2.

## File map (all /opt/data)

`fap_roster.jsonl` (30,331-lead union, source-labeled) · `fap_research_final.jsonl` (24,710 ok) · `fap_facts.jsonl` (vertical/detail/grow per lead) · `fap_copy_lib.py` (component pools + variant-indexed offer/close) · `fap_compose.py` (combo-search composer, per-lead used-opener/used-close sets, FU opener rotation, company scrub) · `fap_copy.jsonl` (shipped corpus) · `fap_machine_qa.py` · `fap_qc_independent.py` (second-agent's own sweep) · `fap_upload_final.py` + `fap_upload_checkpoint.txt` (upload, complete) · `fap_reconcile.py` (POST leads/list reconciliation) · `fap_campaign_state.json`.

## What remains (only on Justin's word)

1. Possible `daily_limit` bump 100 → ~1,000/day (PATCH config; FAP currently 100/day).
2. Render verification (API has none; UI or controlled send) and activation — separate explicit approval; report sends from `/emails` records, never from activation 200.
