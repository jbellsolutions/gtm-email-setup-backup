---
name: cold-email-personalized-agent
description: "Per-lead research + framework-based personalized cold email writer. Researches each lead individually, selects from 10 pain-point frameworks, writes fully custom 4-email sequences with Spintax, outputs legacy email platform-ready CSV. Supersedes the retired static-copy approach."
version: 1.0.0
author: jbellsolutions
metadata:
  hermes:
    tags: [Cold Email, Personalization, Research, Copywriting, legacy email platform]
---

# Cold Email Personalized Agent — Per-Lead Research + Framework Writer

This skill embodies the complete AI cold email agent system — research each lead individually, select the right email framework from 10 proven angles, write fully personalized emails with Spintax, and output legacy email platform-ready CSVs.

**When to use:** Any time you're writing cold email copy for a batch of leads. This replaces the old static-copy approach with per-lead personalization.

## Agent System Prompt (YOUR MANDATE)

When executing this skill, you ARE the cold email research and writing agent. Your job is to take a list of leads, research each one individually, and write a completely unique, personalized cold email for each lead. Every email must read like it was written by a human who spent 10 minutes looking into that specific business.

### Your Workflow

For each lead in the list:

1. **RESEARCH** the lead (see Research Protocol below)
2. **IDENTIFY** their vertical (Insurance, HVAC, Pest Control, Staffing, Real Estate)
3. **SELECT** the best framework based on what you found (see Framework Selection Logic)
4. **WRITE** the email using the selected framework as a skeleton, filling in every detail with real, specific information from your research
5. **EMBED** Spintax in the greeting and CTA for deliverability variation
6. **OUTPUT** the result in the required CSV format

### Research Protocol

For each lead, research and document the following. Use web search, Google Maps, review sites, LinkedIn, social media, job boards, and any available public information.

**Universal Research (all verticals):**
- Company name and what they do (specific services, not generic)
- Owner/contact name and role
- Location(s) and markets served
- How long in business (founding year if findable)
- Google reviews: star rating, review count, any notable recent reviews
- Website: what it looks like, lead capture forms, chat widgets, booking tools
- Social media: last post date, content type, engagement level
- How they get leads: ads visible? On platforms like HomeAdvisor/Zillow? Organic?
- Team size (if visible from website, reviews, or social)
- Any recent news, growth signals, or changes

**Vertical-Specific Research:**

**Insurance:**
- Lines of authority (life, health, P&C)
- Captive agency or independent
- Carrier affiliations
- Book of business size indicators
- Recruiting signals (looking for agents?)

**HVAC:**
- Services: install, repair, maintenance, duct cleaning, indoor air quality
- Maintenance agreement program visible on site?
- Seasonal timing (are we approaching their busy or slow season?)
- Number of trucks/techs (from photos, reviews, team page)
- CRM indicators (ServiceTitan, Housecall Pro, Jobber)

**Pest Control:**
- Services: general pest, termite, mosquito, wildlife, crawl space
- Recurring plan structure visible on site? (monthly, quarterly)
- Seasonal timing
- Team size
- Commercial vs. residential vs. both

**Staffing:**
- Specialization (light industrial, healthcare, IT, admin, etc.)
- ATS/tech stack (Bullhorn, JobDiva, etc. — often in job posts)
- Number of open reqs on their job board
- LinkedIn recruiter activity
- Client types (enterprise/MSP vs. SMB direct)

**Real Estate:**
- Production level (transactions/year from Zillow or Realtor.com)
- Solo agent or team
- Brokerage affiliation
- Specialization (luxury, first-time, investment, commercial)
- Zillow/Realtor.com profile and reviews
- Active listings

### Framework Selection Logic

Based on your research, select ONE framework per lead. Use the strongest signal.

| Research Finding | Framework |
|---|---|
| No visible outbound / all inbound / phones seem quiet | #1: The Phones Are Quiet |
| Running ads, on lead gen platforms, buying leads | #2: Ads Are Broken |
| Established business (10+ years), old-school industry | #3: Before There Were Ads |
| Heavy automation, chatbots, auto-texts on website | #4: People Want a Human |
| Competitive market, everyone has same tech/tools | #5: Everyone Has AI — Nobody Has This |
| Lots of automation, tech-forward company | #6: The Google Problem |
| Long-established, large customer/candidate database | #7: Your List/Book/Database Is a Goldmine |
| Business depends on follow-up (quotes, estimates, applications) | #8: The Silent Bleed |
| Highly competitive local market, many similar businesses | #9: Your Competitors' Phones Are Ringing |
| On lead gen platforms, paying middlemen for leads | #10: Go Direct |

If multiple signals are present, pick the one that creates the most specific, compelling email based on what you found. Avoid generic signals — go with the most concrete finding.

### Email Writing Rules

**Structure (5 variables, in this order):**

1. **Relevance** — one sentence proving this email was meant for them. Reference a specific detail from research.
2. **Pain** — call out their exact situation. Use their industry language.
3. **Value prop** — outcome-focused, one sentence. What they get, not what you do.
4. **Risk reversal** — remove the risk (rotate from the options below)
5. **Soft CTA** — ask a question. Never ask for a call. Never send a link.

**Word Count:** 50–100 words. COUNT THEM. No exceptions.

**Banned Words** — NEVER use any of these:
- pay, price, cost, investment, fee, spend, budget
- affordable, cheap, expensive, ROI
- leverage, synergy, innovative, cutting-edge, solution, revolutionary
- "I hope this finds you well"
- "I'd love to"
- "I wanted to reach out"
- "I came across your company"
- "pick your brain"

**Tone Rules:**
- Sound like a friend, not a salesperson
- Short sentences. Short paragraphs. Max 3-4 sentences per paragraph.
- Write like you talk. If you wouldn't say it out loud, don't write it.
- No corporate speak. No buzzwords. No filler.
- 8th grade reading level

**Risk Reversal Options (rotate — don't use the same one twice in a row):**
1. "If the appointments aren't coming in, you don't owe us anything."
2. "If you're not seeing better results than before, we keep going at no charge until you do."
3. "We guarantee someone is on your phones every single day. If we don't deliver, we work for free until we do."
4. "No contracts. No lock-in. If it's not working, you leave."
5. "If your pipeline/calendar isn't stronger than before we started, we keep working until it is — on us."

**Subject Line Rules:**
- 1–4 words ONLY
- ALL LOWERCASE
- Must look like a coworker or friend sent it
- Vague enough they don't know what's inside
- Never sell in the subject line
- Good examples: "{first_name}, quick thought" | "your phones" | "question for you" | "different angle" | "quick idea"

## Spintax Embedding Rules

**⚠️ CRITICAL: legacy email platform does NOT process Spintax natively.** `{Hey|Hi|Hello}` sent through legacy email platform arrives as raw literal text — the recipient sees the curly braces and pipe characters. This killed the Florida HVAC campaign (June 2026): 1,097 emails went out with visible Spintax syntax. Zero replies.

**The fix:** Pre-resolve all Spintax at generation time. For each lead, randomly pick one variant per Spintax block before uploading. The emails arrive clean — the recipient sees "Hey Fontana" not "{Hey|Hi|Hello} Fontana."

Python implementation:
```python
import re, random

def resolve_spintax(text):
    """Replace {opt1|opt2|opt3} with randomly chosen option."""
    def _replace(match):
        options = match.group(1).split('|')
        return random.choice(options)
    return re.sub(r'\{([^}]+)\}', _replace, text)
```

Apply this to ALL email bodies before uploading to legacy email platform. Generate with Spintax in the template, resolve just before writing the output.

### Spintax Placement (after resolution, the variants provide natural variation across leads)

**Greeting:** Rotate between Hey, Hi, Hello per lead.
**CTA:** Rotate between 4 patterns per lead.

Each lead gets ONE randomly chosen greeting and ONE randomly chosen CTA. Across 1,000+ leads, the variation is natural and sufficient for deliverability.

### Do NOT Spintax in:
- The relevance/research line (must be 100% unique per lead)
- The pain callout (must be specific to their situation)
- The value prop (must match the framework)
- The risk reversal (rotate manually between leads, don't Spintax it)

**CTA Spintax (pick one pattern per email and embed):**
- `{Worth a look|Something worth exploring|Would this be helpful}?`
- `{Is that something you'd want to hear more about|Would you want more info on how that works|Want me to send over some details}?`
- `Is {follow-up|outbound|keeping the pipeline full|filling the calendar} something {you've got handled|that's on your radar|that's slipping right now}?`
- `{How are you handling|What does your process look like for} {follow-up|outbound|customer outreach|candidate sourcing} right now?`

**Do NOT use Spintax in:**
- The relevance/research line (must be 100% unique per lead)
- The pain callout (must be specific to their situation)
- The value prop (must match the framework)
- The risk reversal (rotate manually between leads, don't Spintax it)

### Vertical-Specific Language

Use the correct terminology for each vertical:

**Insurance:** book of business, write policies, renewals, carriers, quotes (not estimates), prospects, annual review, lapsed policies, cross-sell, multi-line, production

**HVAC:** tune-ups, maintenance agreements, system replacement, techs, installers, service calls, demand calls, shoulder season, change-outs, dispatching

**NOTE: HVAC & Staffing now use Owned Audience frameworks (not anti-AI).** These are fundamentally different — positioning around partnerships and borrowed trust, not phone teams/AI operators. See `references/hvac-owned-audience-frameworks-v1.md` and `references/recruiting-staffing-owned-audience-frameworks-v1.md`. Key differences from anti-AI:
- Offer: "I set up referral partnerships with the people who already have your customers' trust" — NOT an AI operator
- Positioning: The partnership guy, peer-to-peer, not a vendor
- CTA: "Want me to send a short version + case study?" — never ask for a call on first touch
- No risk reversal section needed (Owned Audience doesn't use them)
- Subject lines: 1-4 words, lowercase, vague
- Word count: 50-100, aim 85-95 (same)

**Pest Control:** routes, recurring plans, treatments, one-time customers, quarterly service, termite inspection, general pest, cancellations, crawl space

**Staffing:** fill rate, job orders, placements, reqs, submittals, speed-to-fill, redeployment, temp-to-perm, passive candidates, candidate pipeline, ATS

**Real Estate:** SOI/sphere, expireds, FSBOs, circle prospecting, ISA, listings, buyer leads, CMA, GCI, drip campaigns, portal leads, farming

### Output Format

For each lead, output a row with these exact columns:

`first_name, last_name, email, company, vertical, framework_used, research_notes, email_subject, email_body`

**Column Definitions:**
- **first_name:** Lead's first name
- **last_name:** Lead's last name
- **email:** Lead's email address
- **company:** Company name
- **vertical:** One of: insurance, hvac, pest_control, staffing, real_estate
- **framework_used:** Which framework number was selected (1-10) and short name
- **research_notes:** 2-3 bullet points of key findings from research
- **email_subject:** The subject line (lowercase, 1-4 words)
- **email_body:** The full email body with Spintax embedded in greeting and CTA

---

## Follow-Up Email Instructions

### Email 2 (Day 3) — Different Framework, Completely New Angle

Select a DIFFERENT framework than Email 1. Do NOT reference Email 1. Do NOT say "just following up." Write a completely new email with a completely new angle as if Email 1 never existed.

Use the same research but apply a different framework. Same rules: 50-100 words, specific detail from research, risk reversal, soft CTA, Spintax in greeting and CTA.

### Email 3 (Day 7) — Short Bump, 2-3 Sentences Max

Email 3 is a short bump. 2-3 sentences maximum. No framework structure needed. Quick, human check-in that references the core pain point.

Template: `{Hey|Hi} {first_name}, did that last note land? {Curious if|Wondering whether} {pain_point_reference} is {still on your radar|something you're thinking about|still a priority}.`

Keep it under 30 words. Subject line: `re: {{email_subject}}` (threading with Email 1)

### Email 4 (Day 14) — Breakup Email

Polite, final, no pressure. Give them an easy out while leaving the door open.

Template: `{Hey|Hi} {first_name}, I'll leave you alone after this. If {pain_point} isn't {a priority|top of mind} right now, totally get it. But if it is, {this would be worth 5 minutes|I think this could help}. Either way, no hard feelings.`

Keep it under 40 words. Subject line: "last one"

---

## legacy email platform-Ready Output CSV

Final output columns for legacy email platform upload:

`first_name, last_name, email, company, email_subject, email_body, email2_subject, email2_body, email3_body, email4_body`

### Column Mapping in legacy email platform:

| CSV Column | legacy email platform Field | How It's Used |
|---|---|---|
| first_name | {{first_name}} | Standard merge field |
| last_name | {{last_name}} | Standard merge field |
| email | Email | Required for sending |
| company | {{company}} | Standard merge field |
| email_subject | {{email_subject}} | Custom field — used as Subject in template |
| email_body | {{email_body}} | Custom field — used as Body in template |
| email2_subject | {{email2_subject}} | Custom field — Email 2 subject |
| email2_body | {{email2_body}} | Custom field — Email 2 body |
| email3_body | {{email3_body}} | Custom field — Email 3 body |
| email4_body | {{email4_body}} | Custom field — Email 4 body |

### legacy email platform Email Template Setup:

**Email 1 (fully custom per lead):**
- Subject: `{{email_subject}}`
- Body: `{{email_body}}`

**Email 2 (fully custom, different framework — Day 3):**
- Subject: `{{email2_subject}}`
- Body: `{{email2_body}}`

**Email 3 (short follow-up — Day 7):**
- Subject: `re: {{email_subject}}`
- Body: `{{email3_body}}`

**Email 4 (breakup — Day 14):**
- Subject: `last one`
- Body: `{{email4_body}}`

---

## Batch Processing Workflow

**⚠️ VERIFY BEFORE PERSONALIZING.** Do not write emails for unverified leads. Verification catches 28-49% invalid emails (depending on source). Writing copy for invalid emails wastes time and credits.

**⚠️ BATCH BY STATE, NOT METRO.** Justin's directive (June 2026): organize campaigns by state (e.g. "HVAC - Florida - June 2026"), not by metro. States keep campaign volumes manageable (500-2,000 leads) and let copy reference state-specific market conditions. Start with the largest lead-count states first.

0. **CHECK FOR EMAILS FIRST.** Google Maps scrapers and ScrapeCreators exports often contain **zero email addresses** — they return business names, phones, addresses, and websites, but no email column is populated. The `emails` field will be empty for 100% of rows. If the CSV has no emails, stop and switch to domain-to-email extraction (see `references/domain-to-email-extraction.md`). Do NOT proceed through the verification step with an empty list — it's a dead end.

1. **Verify all emails** via ScraperCity `email-validate` (see `legacy email platform-cold-email` skill). Discard all `invalid` results. ScrapeCreators lead database emails are NOT pre-verified — 32% invalid in June 2026 test.
2. **Filter validated CSV** to one state at a time, valid emails only. Delete invalid rows before personalization — never let invalid leads sneak into a campaign.
3. **Feed leads in batches of 25-50** — larger batches degrade quality (see volume limit pitfall below). Use delegate_task subagents to parallelize across batches.
4. **Research each lead** — web search, reviews, website. Even with scripted templates, pull at least one specific detail per lead.
5. **Select framework and write all 4 emails per lead**
6. **Output legacy email platform-ready CSV** with columns: first_name, last_name, email, company, email_subject, email_body, email2_subject, email2_body, email3_body, email4_body
7. **Post-process first names** — many leads lack contact names. Run the first-name extraction rules (see `references/first-name-extraction.md`). Business names like "Fontana Brothers Heating & Air Conditioning" → "Fontana" is acceptable. Numeric-only or acronym names like "4", "M3" → replace with "there".
8. **Upload CSV to legacy email platform** — map custom fields (email_subject, email_body, etc. as `{{email_subject}}`, `{{email_body}}` in sequence template). Per-lead custom field emails work safely up to ~750 chars. Max batch: 1000 leads per upload.

### Quality Control Checklist (per batch):

- [ ] Every email is 50-100 words (count a few randomly)
- [ ] No banned words appear
- [ ] Every email contains at least one specific research detail
- [ ] Subject lines are 1-4 words, lowercase
- [ ] Risk reversals are rotated
- [ ] Spintax is in greeting and CTA only
- [ ] Vertical-specific language is correct
- [ ] Email 2 uses a different framework than Email 1 for each lead
- [ ] Email 3 is under 30 words
- [ ] Email 4 is under 40 words

### Volume Guidelines:

| Batch Size | Agent Processing Time | Notes |
|---|---|---|
| 10 leads | ~15-20 min | Good for testing and dialing in quality |
| 25 leads | ~30-45 min | Standard daily batch |
| 50 leads | ~60-90 min | Max recommended per session for quality |
| 100+ leads | Split into batches of 25-50 | Don't sacrifice research depth for volume |

### ⚠️ Spintax Kill Pitfall (June 2026)

**legacy email platform does NOT support Spintax natively.** `{Hey|Hi|Hello}` is sent as literal text — curly braces, pipes, and all. The recipient sees `{Hey|Hi|Hello} Mike` in their inbox. This killed the initial Florida HVAC launch (1,097 emails sent with raw Spintax, zero replies).

**Fix:** Pre-resolve all Spintax at generation time. For each lead, randomly pick one variant per block before upload:

```python
def resolve_spintax(text):
    def _replace(match):
        options = match.group(1).split('|')
        return random.choice(options)
    return re.sub(r'\{([^}]+)\}', _replace, text)
```

This turns `{Hey|Hi|Hello} Mike` into `Hey Mike` (or `Hi Mike`, or `Hello Mike`) — one clean variant per lead, no legacy email platform processing needed.

**Where Spintax still appears:** Only in pre-resolved templates. The `{{` in Python f-strings becomes `{` in the output, so `{{Hey|Hi|Hello}}` in a template becomes `{Hey|Hi|Hello}` in the generated text. Always run `resolve_spintax()` on the final output before uploading.

### Volume Limit Pitfall (Real Example)

**Do NOT process 400+ leads in a single session**, even when using scripted template generation. The June 2026 Florida HVAC batch (421 leads) demonstrated exactly why:

- **First pass had 277 banned-word violations** across all 10 frameworks because templates were written inline and never individually audited against the banned-word list before running at scale.
- **Word counts drifted** from 64-109 (target: 50-100), with 30 emails exceeding 100 words.
- **First-name extraction failures** (e.g., "The Air Squad" → first_name="The", "AC Brothers" → first_name="AC") went undetected because 421 rows is too many to spot-check effectively.

**Lesson:** The 50-lead max exists for a reason. When a user requests a batch larger than 50, push back — offer to split into sessions of 25-50 leads each. If they insist, warn them that quality will degrade and they should budget time for a second review pass.

### ⚠️ DIY Domain Scraping Pitfall (June 2026)

**Scraping homepages for emails via HTTP GET has a ~78% false-positive rate.** When we scraped 4,390 law firm domains (direct urllib, no proxy, 5s timeout, 30 workers), the regex extracted 1,839 emails. After ScraperCity verification, only 26 were valid (4.3%). The rest were:
- WordPress theme author emails embedded in templates
- GoDaddy/default hosting placeholder emails (`filler@godaddy.com`, `name@email.com`)
- Pattern-matched strings that look like emails but aren't
- Guessed first-name patterns that don't exist (`sribera@riberalaw.com`)

**Bottom line:** DIY scraping is cheap (~$0 for scraping, ~$2.16 for 599 verifications) but yields <5% real emails. For 4,390 domains → 26 valid contacts. For larger lists, use purpose-built email finders (Apify, Hunter.io) instead of raw regex scraping.

### ⚠️ Scripted Template Pitfall

When generating emails programmatically (Python scripts with f-string templates), every template string must be individually verified against the banned-word list BEFORE execution. The most common offenders in HVAC templates:
- "ad spend" → replace with "ad dependency", "ad money", or "cash on ads"
- "leverage" → replace with "use", "put to work", "tap into"
- "budget" → just remove the concept ("biggest ad budgets" → "biggest ad campaigns")
- "fee" / "pay" → replace with "sending money" or rephrase ("No per-lead nonsense")
- "solution" → replace with "approach" or remove

See `references/anti-ai-campaign-angle.md` for pre-verified, banned-word-clean template variants of all 10 frameworks.

### ⚠️ Company Name Banned-Word Contamination (July 2026)

When company names are embedded in email bodies (e.g., "Want me to send a short version for {company}?"), the company name itself can contain banned words. "Staffing Solutions" → contains "solution". "Innovative Air" → contains "innovative". Clean company names before embedding:

```python
def clean_company(company):
    c = re.sub(r'\b\w*solutions?\w*\b', '', company, flags=re.IGNORECASE)
    c = re.sub(r'  +', ' ', c).strip()
    if len(c) < 4:
        return company
    return c
```

Apply this before any `{company}` placeholder in email bodies. "Staffing Solutions" → "Staffing " which reads fine in context.

### Owned Audience Framework Sets (July 2026)

Two new vertical-specific framework sets using the "Owned Audience" partnership angle. Different positioning from anti-AI — these sell referral partnerships, not phone teams.

**HVAC Owned Audience (10 frameworks):** Reference at `/tmp/hvac_email_gen.py`. Core angle: "the roofers, plumbers, and realtors already in your customers' homes." CTA pattern: "Want me to send a short version for {company}, plus how it played out for another AC company in a different market?" Jay Abraham credential as trust anchor.

**Recruiting Owned Audience (10 frameworks):** Reference at `/tmp/recruiting_email_gen.py`. Core angle: "the advisors, bankers, and placed execs who already sit next to hiring decisions." CTA pattern: "Want me to send a short version for {company}, plus how it played out for another search firm in a different niche?"

Key differences from anti-AI frameworks:
- Never ask for a call on first touch
- Framework selection: deterministic company-name hash (`sum(ord(c) for c in company) % 10`)
- 4-email sequence using custom field merge tags: `{{email_subject}}`, `{{email_body}}`, through `{{email4_body}}`
- Word count: 50-100 words strictly enforced per email

### ⚠️ Signal Extraction Pitfalls (July 2026 PR Agency Campaign)

When extracting per-lead signal details from ListKit Description fields:
- **Skip generic first sentences** — most descriptions start with "[Company] is a public relations agency that..." which is useless as a signal. Look at sentences 2-4 for industry-specific details.
- **Strip trailing punctuation** — regex captures often end with commas or semicolons mid-list. Always rstrip `,.;:` before embedding in "Saw X." lines.
- **Enforce minimum length** — signals under 15 characters are too vague ("Saw ghostwriting."). Fall back to broader description fragments.
- **"including/specializing in/focusing on" patterns** are the most reliable for unique signals. Match these first.

### ⚠️ Generic Email First-Name Fallback (July 2026)

~55% of PR agency lead lists use generic email addresses (info@, hello@, contact@, etc.). The user rejected "there" as a greeting. **Company-name-derived greeting is acceptable:** extract the first meaningful word from the company name (skip: the, a, agency, PR, media, group, communications, etc.). "Firecracker" for Firecracker PR is fine. Never use company acronyms or single-letter fallbacks.

### ⚠️ Framework Monotony Problem

When most leads in a list share similar descriptions (common in niche verticals like PR agencies), framework selection based purely on keyword signals produces 80%+ same-framework campaigns. **Fix:** use deterministic hash-based rotation for leads without strong differentiating signals. Company name `sum(ord(c)) % N` spreads leads across N frameworks. This creates genuine variety while keeping strong-signal leads (podcast, LinkedIn, newsletter keywords) on their best-fit framework.

---

## Scripted Batch Personalization (Scale Approach — June 2026)

For large batches (200+ leads), use the scripted template approach instead of per-lead LLM research. Two scripts cover different verticals:

### HVAC: `scripts/hvac_state_personalize.py`
State-agnostic personalization engine for HVAC leads.

- **Pre-verified templates** — All 10 anti-AI framework templates are pre-screened against the banned-word list. No inline template writing at scale.
- **Deterministic framework rotation** — Each lead gets framework `idx % 10` for Email 1 and `(idx + 3) % 10` for Email 2.
- **Automated first-name extraction** — See `references/first-name-extraction.md`.
- **Review text formatting** — Dynamically formats rating + review count into natural references.

### MCA/Lending: `scripts/mca_email_generator.py`
Programmatic website analysis + framework selection for MCA/business lending leads.

- **Website curling** — Fetches each lead's homepage, strips HTML, extracts text signals.
- **Keyword-based framework selection** — Matches website text against MCA-specific signals (hiring → empty_seats, UCC/aged → aged_data, SMS → sms_broken, etc.). See `references/mca-lending-frameworks.md` for the full 10-framework catalog.
- **Lead filtering** — Automatically skips non-US domains (.za, .co.uk, etc.), consumer lending (payday/installment), and private equity/VC (unless MCA keywords present).
- **First-name cleanup** — Filters submissions@, info@, etc. from being used as greeting names.
- **Output:** JSON + legacy email platform-ready CSV with `first_name, email, company_name, email_subject, email_body`.

**Usage:**
```bash
python3 scripts/hvac_state_personalize.py /tmp/{state}_hvac_leads.json /tmp/{state}_hvac_personalized.json
```

## MCA Scripted Batch Generator

For MCA/business lending leads, use `scripts/mca_email_generator.py` — a reusable script that curls each lead's website, extracts signals via keyword matching, selects from 10 MCA-specific pain-point frameworks, and generates personalized emails.

```bash
python3 scripts/mca_email_generator.py /tmp/mca_leads.json /tmp/mca_output.csv
```

**Input format** (JSON array):
```json
[{"first_name": "Brian", "email": "brian@company.com", "company": "ABC Capital", "domain": "abccapital.com", "website": "https://abccapital.com", "notes": "MCA funder"}]
```

**What it does:**
1. Curls each website (8s timeout, first 5000 chars of text)
2. Keyword-matches for framework selection (careers→Empty Seats, UCC→Aged Data, SMS→SMS Broken, etc.)
3. Extracts lending type, location, and filters out consumer lending + non-US domains
4. Generates email with rotated risk reversals and framework-matched CTA
5. Outputs legacy email platform-ready CSV

**Pitfalls observed (June 2026):**
- Multi-email semicolons in ListKit CSVs: split `avigail@x.com; chaim@x.com` before processing
- First names from email local parts: clean `mmarkowitz`→Mark, `brianroe`→Brian, `customerservice`→"there"
- Location extraction often returns garbage from website text — validate format before using
- ScraperCity was cancelled — ListKit enrichment was used as fallback (less reliable than ScraperCity verification)

**Word count tradeoff:** Scripted templates average 85-95 words with most emails staying under 100. Occasional outliers at 96 words are acceptable for batch processing.

## legacy email platform Campaign Setup (Post-Writing)

After generating the CSV, use the `legacy email platform-cold-email` skill for campaign creation and lead upload:

1. **Create Campaign** — name by vertical and date: "HVAC - Phoenix - May 2026"
2. **Upload Lead CSV** with custom fields mapped
3. **Save email sequences** using custom field merge tags
4. **Configure sending settings** — see `legacy email platform-cold-email` for compliance rules
5. **Verify emails** via Anymail Finder before upload (mandatory)

### Important: Custom Fields & Lead Duplication Pitfalls

**⚠️ CRITICAL: legacy email platform silently drops duplicate leads across campaigns.** Even with `ignore_duplicate_leads_in_other_campaign: true`, leads that exist in ANY other campaign are silently rejected. `upload_count` shows the full batch size but `total_leads` shows 0 — the leads simply disappear with no error. This is NOT a bug you can work around with settings.

**Implication:** You get ONE shot per email address across all campaigns. If a campaign sends with bad copy and you need to resend, you MUST use completely new email addresses. The original emails are burned in legacy email platform's system.

**For resending:** Export leads from the bad campaign, source NEW verified emails for the same companies, or contact legacy email platform support to clear the block. Do NOT waste time trying different ignore flags — they don't work.

**For fresh campaigns:** Always verify Spintax is resolved, copy is clean, and sequences are set BEFORE uploading leads. There is no undo.

### Custom Fields Body Size

**⚠️ CRITICAL: Do NOT use `{{custom_fields.X}}` to store the entire email body (900+ characters).** legacy email platform's render engine cannot handle large custom field values as sequence email body content. All leads will stay "STARTED" with zero sends. This killed the HVAC Florida campaign on May 11, 2026.

**Fix:** When uploading personalized emails, store the full email body directly in the campaign sequence template using standard merge tags wherever possible. For per-lead personalization, store only SHORT hooks (1-2 sentences) in custom fields and reference them within the template body.

**Alternative approach:** Upload leads with custom fields for `email_body`, `email2_body`, etc., but test with a single lead first to confirm legacy email platform renders them correctly before uploading the full batch. Custom field emails up to ~750 chars have been confirmed safe (June 2026 Florida campaign).

---

## Input Format

Minimum input per lead:

| Field | Required? | Notes |
|---|---|---|
| first_name | Yes | Lead's first name |
| last_name | Yes | Lead's last name |
| email | Yes | Verified email |
| company | Yes | Company name |
| website | Recommended | Dramatically improves research quality |
| vertical | Recommended | insurance, hvac, pest_control, staffing, real_estate |
| city | Recommended | Helps with market-specific references |
| state | Recommended | Helps with market-specific references |

Example input CSV:
```
first_name,last_name,email,company,website,vertical,city,state
Mike,Johnson,mike@mikeshvac.com,Mike's HVAC,mikeshvac.com,hvac,Chandler,AZ
Sarah,Williams,sarah@swinsurance.com,SW Insurance Group,swinsurancegroup.com,insurance,Dallas,TX
```

---

## Supported Verticals

This skill ships with framework sets for 6 verticals:

| Vertical | Frameworks | Source |
|---|---|---|
| Insurance | 10 anti-AI frameworks | `references/anti-ai-campaign-angle.md` |
| **HVAC** | **10 Owned Audience frameworks (partnerships/borrowed trust)** | `references/hvac-owned-audience-frameworks-v1.md` |
| Pest Control | 10 anti-AI frameworks | `references/anti-ai-campaign-angle.md` |
| **Staffing** | **10 Owned Audience frameworks (partnerships/borrowed trust)** | `references/recruiting-staffing-owned-audience-frameworks-v1.md` |
| Real Estate | 10 anti-AI frameworks | `references/anti-ai-campaign-angle.md` |
| **PR Agencies** | 7 SpeakerAgent-first frameworks (v3) + **Referral Angle (Trojan Horse)** | `references/pr-agency-frameworks-v3.md` |
| **Marketing Agencies** | 10 Owned Audience frameworks | `references/marketing-agencies-owned-audience-frameworks-v1.md` |
| **Solar Installers (NEW)** | **10 Owned Audience frameworks (Jay Abraham partnership angle)** | `references/solar-owned-audience-frameworks-v1.md` |
| **Men's Health & Hormone Clinics (NEW)** | **6 JV frameworks (Jay Abraham partnership + podcast engine)** | `references/mens-health-hormone-jv-frameworks-v2.md` |
| **Med Spas / Owner-Led Businesses (NEW)** | **10 Relationship Offer frameworks (industry-agnostic, partnership channel)** | `references/relationship-offer-service-frameworks-v1.md` |

**PR Agency generator v3 (Referral Angle — July 2026):** Use `scripts/pr_referral_generator.py` for the Trojan Horse referral approach. See "PR Agency Referral Network Angle" section below for full template and usage.

### ⚠️ Signal Banned-Word Contamination (July 2026)

When signals are extracted from ListKit/third-party descriptions and embedded in email bodies (e.g., "Saw {signal_detail} — liked what we saw."), the signal text itself can contain banned words from the original description. On the 4,567-lead PR referral campaign: 30 leads (0.7%) had banned words (leverage, innovative, investment, budget, solution) in their signals. **Fix:** clean signals before embedding — phrase-level replacement first (e.g., "return on investment" → "measurable results"), then word-level (e.g., "leverage" → "use", "innovative" → "creative"). See `scripts/pr_referral_generator.py` for the `clean_signal()` function.
- 7 rotated frameworks with 3 pain + 3 value variants each
- Company-name hash-based framework rotation for variety when descriptions lack strong signals
- Signal extraction from ListKit Description field — skips generic opening sentences
- First-name extraction from email local part with company-name fallback for generic addresses
- Zero-link enforcement and banned-word scanning built in
- Outputs legacy email platform-ready CSV with 6 custom fields (subject+body × 3 emails)
- Typical distribution: ~36% reply rates, ~35% exec pivot, ~17% recurring, ~6% podcast, ~3% LinkedIn, ~2% newsletter, ~1% fractional
- Processes 4,500+ leads in ~30 seconds (pure regex + template, no LLM calls)

### PR Agency Referral Network Angle (Trojan Horse — July 2026)

A completely different approach from the SpeakerAgent pitch. Instead of selling a service to agencies, frame as: "We get referral requests from people looking for PR agencies. Your name came up. Can we refer people to you? Let's hop on a call so we can vet you." Single-email campaign. Mentions SpeakerAgent as the managed backend service that connects agencies with clients. Goal: book a call, not pitch a service.

Use `scripts/pr_referral_generator.py` — reads the existing personalized CSV with signals, generates a single referral-angle email per lead. Template (~93 words):

> {greeting} {first_name},
>
> Saw {signal_detail} — liked what we saw.
>
> We get dozens of inquiries every month from people looking for a PR agency. Your name came up in some searches. We have a managed service called SpeakerAgent that connects agencies with the right clients.
>
> Can we refer people to you? If so let's hop on a quick call. We'll get a feel for what you do, vet you out a little, and make sure we're clear on how to hand clients off to you.
>
> Worth 15 minutes?

Subjects rotated: "referral question" | "your name came up" | "quick question" | "referring clients". Zero links. No banned words. Processes full 4,500+ list in seconds.

**⚠️ Cross-campaign pitfall:** legacy email platform blocks duplicate emails across campaigns — you cannot upload the same leads to a new campaign if they exist in another. To switch a lead list from one angle to another, see the lead-recycling workflow in the `legacy email platform-cold-email` skill (`references/lead-recycling-workflow.md`).

MCA is the only vertical with its own distinct framework set — the other five share the anti-AI angle frameworks. MCA has different pain points (empty seats, aged data, SMS broken, speed kills, etc.) and different language conventions.

### Marketing Agencies — Owned Audience Angle (July 2026)

A completely different framework set from the anti-AI angle. Positions around **partnerships and borrowed trust** — getting the people who already have the target clients' trust (podcast hosts, newsletter operators, consultants, communities) to send them clients. A simple show or newsletter is the engine that makes partners want to promote them.

**Key differences from anti-AI frameworks:**
- Different offer: "I set up partnerships with the people who already have your ideal clients' trust" — NOT an AI operator or phone team
- Different positioning: The partnership guy — ran his own agency for 15 years — peer, not vendor
- Different CTA rules: Primary CTA is "Want me to send a short version + case study for another agency owner?" — never ask for a call on first touch
- Subject lines: 1–4 words, lowercase, vague (e.g., "podcast idea," "same page," "who feeds you")
- Follow-ups: Generic templates — Email 2 (Day 3), Email 3 (Day 7), Email 4 (Day 14)
- 10 frameworks: See `references/marketing-agencies-owned-audience-frameworks-v1.md`

### ⚠️ Lead Quality Ratio from Raw Scraped CSVs (July 2026)

Marketing Agencies CSV: 10,000 leads → 2,922 with any email → 680 with personal-looking emails and score >200 in US states = **6.8% usable rate**. Breakdown: 27% no email at all, 56% generic-only (info@/hello@/contact@), 7% personal-looking but low score or non-US. Generic emails had 100% hostile/unsub rate on PR campaigns. Always filter aggressively before writing copy — do NOT write emails for leads with `info@`, `hello@`, `contact@`, `support@`, `sales@`, `privacy@`, `engage@`, `brand@`, `connect@`, `compliance@` addresses.

- **Email verification:** Run ALL leads through ScraperCity `email-validate` before research and personalization (see `legacy email platform-cold-email` skill, `references/scrapercity-verification.md`). ScrapeCreators leads are NOT pre-verified — test batch showed 28% invalid.
- **Domain-to-email extraction:** When the lead CSV has no emails (common with Google Maps data), use domain-to-email extraction tools. See `references/domain-to-email-extraction.md` for the Firecrawl vs Apify vs ScraperCity comparison and workflows.
- **Personalization script (HVAC):** Use `scripts/hvac_state_personalize.py` for programmatic per-lead email generation with resolved Spintax. Input: JSON array of leads with company/city/state/email/rating/reviews. Output: legacy email platform-ready JSON with 4-email custom fields.
- **Personalization script (MCA):** Use `scripts/mca_email_generator.py` for MCA/lending leads. Curls each lead's website, extracts keyword signals, selects from 10 MCA-specific frameworks, generates personalized emails. See `references/mca-lending-frameworks.md` for the full framework catalog and selection logic.
- **Campaign creation:** Use `legacy email platform-cold-email` skill for legacy email platform CLI/MCP commands
- **Weekly rhythm:** Use `cold-email-weekly-rhythm` skill for ongoing monitoring
- **Spam checks:** Use `spam-word-checker` skill to validate copy before sending
- **Reply handling:** Use `positive-reply-scoring` skill for classification
- **Sending rules:** Mon-Fri 8AM-5PM ET, plain text only, no open/link tracking, AI ESP matching ON
- **First-name extraction:** When lead CSVs lack contact names, use `references/first-name-extraction.md` for the rules and Python implementation

## Campaign Angles (reusable positioning)

### Anti-AI Angle (current — June 2026)

Full positioning and banned-word-clean templates for all 10 frameworks:
→ `references/anti-ai-campaign-angle.md`

Core tagline: *"If you're tired of the AI hype and all the headaches with ads, content, etc — guess what, your customers are as well. They want you to call them and connect with them."*

This angle attacks the AI/automation status quo and positions the service as refreshingly human. Pre-verified against the full banned-word list. Use these templates as the starting point for any new campaign using this positioning.

### Compliance Rules (from legacy email platform-cold-email)

| Rule | Setting |
|---|---|
| NO open tracking | `track_settings: ["DONT_TRACK_EMAIL_OPEN", "DONT_TRACK_LINK_CLICK"]` |
| Reply tracking only | `stop_lead_settings: "REPLY_TO_AN_EMAIL"` |
| Plain text only | `send_as_plain_text: true` |
| No URLs in emails 1-3 | Copy review required |
| 25-30 sends/day per mailbox | Sending config |
| 3-5 min between emails | Sending config |
| Spintax in greeting + CTA | This skill already embeds it |

---

## Example Output (for reference)

See the complete 5-lead example in the source document. Key pattern:

- Email 1: Framework-driven, 50-100 words, one specific research detail, risk reversal, soft CTA
- Email 2: Different framework, new angle, same research
- Email 3: 2-3 sentence bump, references pain point
- Email 4: Breakup, under 40 words, human tone