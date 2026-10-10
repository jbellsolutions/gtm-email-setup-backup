---
name: instantly-prospect-pipeline
description: "End-to-end pipeline: source leads via Apify PipelineLabs (no legacy email platform-Prospector equivalent exists on Instantly — Apify is the only sourcing path here) → auto-verify via Reacher → research + Charm Offensive / framework-based custom emails → create Instantly campaign → upload → test. Use when the user wants to build a lead list, create personalized cold emails, and push to an Instantly campaign. Mirrors smart-prospect-pipeline's legacy email platform workflow, minus the legacy email platform-Prospector-specific sourcing step which has no Instantly equivalent."
version: 1.0.0
metadata:
  hermes:
    tags: [Instantly, Cold Email, Sales, Outreach, Pipeline]
    related_skills: [instantly-cold-email, smart-prospect-pipeline, cold-email-personalized-agent, charm-cold-email, charm-offensive-foundation, verify-leads]
prerequisites:
  env_vars: [INSTANTLY_API_KEY, APIFY_API_KEY]
  commands: []
---

# Instantly Prospect → Campaign Pipeline

End-to-end pipeline that sources leads via Apify, verifies them via Reacher, researches each lead, creates personalized emails using Charm Offensive or framework-based approaches, and pushes everything to an Instantly campaign.

**Key difference from `smart-prospect-pipeline`:** legacy email platform has a built-in Prospector (paid lead-sourcing sub-service, CLI-only). No Instantly equivalent has been found in the v2 API surfaced so far — assume none exists. This pipeline sources leads via Apify PipelineLabs exclusively, which was already legacy email platform-Prospector's own fallback for poorly-covered niches (see `smart-prospect-pipeline` Step 0) — here it's simply the only path, not a fallback.

## When to Use

- User wants to source leads (via Apify) and create an Instantly campaign
- User asks to go from a niche/filter set → verified list → personalized emails → Instantly campaign

## Prerequisites

- `INSTANTLY_API_KEY`, `APIFY_API_KEY` in environment
- For Charm Offensive emails: `charm-profile.md` must exist or be created

## Step 0: Source Leads via Apify PipelineLabs

Actor ID `kVYdvNOefemtiDXO5`. Key in env (`APIFY_API_KEY`). Setup:
- `totalResults: N` (up to 50,000)
- `hasEmail: true`
- `emailStatusIncludes: ["verified"]` (deliverable emails only)
- `companyKeywordIncludes: [...]` — keywords for the niche
- `companyIndustryIncludes: [...]` — MUST use exact industry names (check schema via `https://api.apify.com/v2/acts/kVYdvNOefemtiDXO5/builds/default`)
- `seniorityIncludes: ["owner", "c_suite", "vp", "director"]` (underscore format, lowercase)
- `companySizeIncludes: ["1-10", "11-50"]`
- `personLocationCountryIncludes: ["United States"]`

Output includes `firstName`, `lastName`, `email`, `title`, `companyName`, `companyWebsite`, `companyCity`, `companyState`, `emailStatus` — all verified. $0.001/lead, no separate verification needed. Poll via `/v2/actor-runs/{run_id}`, fetch dataset at `/v2/actor-runs/{run_id}/dataset/items?format=json`.

**⚠️ Industry values must be exact** — PipelineLabs rejects unknown industries with a 400 error listing allowed values. Common valid industries: "Renewables & Environment", "Medical Practice", "Construction", "Health, Wellness and Fitness". When unsure, use only `companyKeywordIncludes` and omit `companyIndustryIncludes`.

**Coverage note:** legacy email platform Prospector's coverage data (73% for Staffing, 0% for Renewables, etc. — see `smart-prospect-pipeline` Step 0) was specific to Prospector's own database and has no bearing on Apify PipelineLabs coverage, which draws from a different underlying dataset. Don't assume the same niches will be well/poorly covered here — validate with a small test run (a few hundred results) before committing to a full 50K-lead pull on an unfamiliar niche.

## Pipeline Steps

### Step 1: Verify Emails

Apify's `emailStatus: "verified"` flag is cosmetic (see `instantly-cold-email` — PipelineLabs' "verified" tag runs 40-50% false-positive rate against a real verifier). **Reacher is the mandatory, only verification step here** — there's no legacy email platform-Prospector-style native verification in this pipeline to treat as primary:

```bash
python3 /opt/data/skills/email/verify-leads/tools/verify_leads.py <file>.csv --json
```
Endpoint: `verify.usingaitoscale.com`. Shared 10k/24h cap with dashboard. Discard all `invalid` results, upload `valid` only.

### Step 2: Save the Verified List

Write sendable leads to CSV:
```
/opt/data/cache/cold-email/<campaign-name>-verified.csv
```

Minimum columns: `first_name, last_name, email, company, title, city, state, verification_status`

### Step 3: Research + Create Custom Emails

Two paths — the user specifies which cold email framework to use:

**Path A: Cold Email Personalized Agent** (framework-based, good for scale)
- Load `cold-email-personalized-agent` skill
- Per-lead research → framework selection (10 anti-AI or Owned Audience frameworks)
- 4-email sequences with resolved Spintax
- Output: CSV with custom fields, ready for Instantly upload (exact field names unverified — see Step 4)

**Path B: Charm Offensive** (disarming/honest/funny, good for lower volume)
- Load `charm-offensive-foundation` skill → voice rules + profile
- Load `charm-cold-email` skill → templates
- Per-lead research → draft in Charm voice
- Structure: funny opener → value → risk reversal → low-pressure CTA → pet photo → 3-title signature

**The user specifies the framework for the campaign.** Do not choose — ask if unclear.

**⚠️ Critical rules for ALL emails:**
- **Resolve Spintax before upload.** legacy email platform does NOT process `{Hey|Hi}` — sends literal curly braces. Instantly's Spintax support is unverified — treat as unsupported until confirmed. Pre-resolve at generation time regardless.
- **No banned words:** pay, price, cost, investment, fee, spend, budget, affordable, cheap, expensive, ROI, leverage, synergy, innovative, cutting-edge, solution
- **Filter generic emails:** `info@`, `hello@`, `contact@`, `support@`, `sales@` had 100% hostile/unsub rate on past campaigns
- **Company-name fallback for greeting:** when lead has no first name, extract meaningful word from company name (skip: the, a, agency, PR, media, group, communications)
- **Batch in chunks of 50 max** per session for quality

### Step 4: Create Campaign, Upload, Test, Notify

**4a. Create the campaign** — no create-endpoint verified for Instantly yet; create via the Instantly web UI (see `instantly-cold-email`). Check `GET /campaigns` for existing campaigns first.

**4b. Upload leads** via `POST /api/v2/leads` — payload shape unverified. legacy email platform's format required `last_name` explicitly or leads silently became unlinked "orphan" records blocking all future uploads of that email (see `smart-prospect-pipeline` for the full incident and recovery workflow at `references/orphan-leads-recovery.md`). Whether Instantly has an analogous orphan-record failure mode is unknown, but the defensive habit transfers: always populate every field the API accepts as required (don't omit optional-looking fields), and verify the lead actually landed in the campaign after upload rather than trusting a 200 response — same rule as `instantly-cold-email`'s Upload Verification section.

Fields likely to carry over: `first_name`, `last_name`, `email`, `company_name`, plus whatever custom-field mechanism Instantly uses for `email_subject`/`email_body`/sequence content (unverified — confirm before relying on merge-tag syntax).

**4c. Save email sequences** — merge-tag syntax unverified (see `instantly-cold-email`'s "Per-Lead Email Personalization" unverified note).

**4d. Configure campaign settings** — target the same compliance intent as legacy email platform (no open tracking, reply-only stop condition, plain text, conservative schedule/volume) via the Instantly UI until settings-update endpoints are confirmed.

**4e. Test with ONE lead first.** Same discipline as legacy email platform: confirm merge tags render correctly, email body displays properly (no raw Spintax, no truncated text), and the lead actually starts sending — before uploading the full batch. legacy email platform's specific duplicate-email-silently-dropped behavior may or may not apply to Instantly; test with a fresh/throwaway email regardless.

**4f. Notify Justin** with:
- Campaign ID and name
- Lead count (total uploaded, verified, filtered)
- Email samples (2-3)
- "Ready to add mailboxes and send"

## Key Pitfalls

| Pitfall | Impact | Prevention |
|---|---|---|
| Spintax sent as literal text | Zero replies, burned leads | Pre-resolve all Spintax before upload (legacy email platform confirmed unsupported; Instantly unverified — treat as unsupported) |
| Duplicate emails across campaigns | Leads possibly silently dropped (confirmed on legacy email platform; unverified on Instantly) | Fresh emails only; test with one first |
| **Lead upload payload gaps** | On legacy email platform, a missing `last_name` created unlinked "orphan" leads that blocked all future uploads of that email — see `smart-prospect-pipeline` for the incident + recovery workflow. Instantly's required-field behavior is unverified. | Populate every field the API accepts; verify the lead landed in the campaign after upload, don't trust a 200 alone |
| Generic emails (info@, hello@) | 100% hostile/unsub rate (confirmed pattern, platform-independent) | Filter aggressively before writing copy |
| Batch >50 leads in one pass | Quality degrades, banned words slip through | Chunk in 50, review samples each chunk |
| Company name contains banned words | "Staffing Solutions" triggers "solution" filter | Clean company names before embedding in email bodies |

### Plain-text rendering — verify actual output, don't trust the preview

legacy email platform's render engine does NOT preserve normal line breaks in custom-field merge tags — `\n\n` paragraph formatting collapses into one blob in the actual sent email even when the preview looks fine (fix: one sentence per line, single `\n`, no blank lines — see `smart-prospect-pipeline` for the full example). Whether Instantly's rendering has the same quirk is unverified. The lesson that transfers regardless: **test with one lead and check the actual received email, not just whatever preview the platform's UI shows.**

## References

- `smart-prospect-pipeline` → `references/orphan-leads-recovery.md` — the legacy email platform orphan-lead incident and recovery workflow (context for the pitfall above, not directly applicable until Instantly's upload behavior is tested)
- `references/scrapecreators-enrichment.md` — cross-reference ScrapeCreators source CSVs (company data) against Reacher-verified email lists to create enriched lead CSVs (platform-agnostic)

```
User defines filters
        ↓
Apify PipelineLabs run (source + built-in verification tag)
        ↓
Reacher verify (mandatory — Apify's tag is cosmetic)
        ↓
Save: /opt/data/cache/cold-email/<campaign>-verified.csv
        ↓
Research + Charm Offensive / Framework emails (batch of 50)
        ↓
Resolve Spintax + banned-word scan + generic email filter
        ↓
Create campaign (UI) + upload leads + save sequences (endpoints unverified)
        ↓
Test single lead → verify renders correctly
        ↓
Notify Justin: "Ready — add mailboxes and send"
```
