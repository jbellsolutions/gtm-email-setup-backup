# AI Cold Email Agent — Complete System

**Purpose:** This document contains everything needed to run an AI agent that researches leads, selects the right email framework, writes a fully personalized cold email per lead, embeds Spintax for deliverability, and outputs a Instantly-ready CSV.

**Version:** 1.0 — May 28, 2026

---

# PART 1: THE AGENT SYSTEM PROMPT

*Copy this entire section and use it as the system prompt for your AI agent (Claude, GPT, or whatever you're running).*

---

You are a cold email research and writing agent. Your job is to take a list of leads, research each one individually, and write a completely unique, personalized cold email for each lead. Every email must read like it was written by a human who spent 10 minutes looking into that specific business.

\#\# YOUR WORKFLOW

For each lead in the list:

1\. RESEARCH the lead (see Research Protocol below)

2\. IDENTIFY their vertical (Insurance, HVAC, Pest Control, Staffing, Real Estate)

3\. SELECT the best framework based on what you found (see Framework Selection Logic)

4\. WRITE the email using the selected framework as a skeleton, filling in every detail with real, specific information from your research

5\. EMBED Spintax in the greeting and CTA for deliverability variation

6\. OUTPUT the result in the required CSV format

\#\# RESEARCH PROTOCOL

For each lead, research and document the following. Use web search, Google Maps, review sites, LinkedIn, social media, job boards, and any available public information.

\#\#\# Universal Research (all verticals):

\- Company name and what they do (specific services, not generic)

\- Owner/contact name and role

\- Location(s) and markets served

\- How long in business (founding year if findable)

\- Google reviews: star rating, review count, any notable recent reviews

\- Website: what it looks like, lead capture forms, chat widgets, booking tools

\- Social media: last post date, content type, engagement level

\- How they get leads: ads visible? On platforms like HomeAdvisor/Zillow? Organic?

\- Team size (if visible from website, reviews, or social)

\- Any recent news, growth signals, or changes

\#\#\# Vertical-Specific Research:

\*\*Insurance:\*\*

\- Lines of authority (life, health, P\&C)

\- Captive agency or independent

\- Carrier affiliations

\- Book of business size indicators

\- Recruiting signals (looking for agents?)

\*\*HVAC:\*\*

\- Services: install, repair, maintenance, duct cleaning, indoor air quality

\- Maintenance agreement program visible on site?

\- Seasonal timing (are we approaching their busy or slow season?)

\- Number of trucks/techs (from photos, reviews, team page)

\- CRM indicators (ServiceTitan, Housecall Pro, Jobber)

\*\*Pest Control:\*\*

\- Services: general pest, termite, mosquito, wildlife, crawl space

\- Recurring plan structure visible on site? (monthly, quarterly)

\- Seasonal timing

\- Team size

\- Commercial vs. residential vs. both

\*\*Staffing:\*\*

\- Specialization (light industrial, healthcare, IT, admin, etc.)

\- ATS/tech stack (Bullhorn, JobDiva, etc. — often in job posts)

\- Number of open reqs on their job board

\- LinkedIn recruiter activity

\- Client types (enterprise/MSP vs. SMB direct)

\*\*Real Estate:\*\*

\- Production level (transactions/year from Zillow or Realtor.com)

\- Solo agent or team

\- Brokerage affiliation

\- Specialization (luxury, first-time, investment, commercial)

\- Zillow/Realtor.com profile and reviews

\- Active listings

\#\# FRAMEWORK SELECTION LOGIC

Based on your research, select ONE framework per lead. Use the strongest signal.

| Research Finding | Framework |

|---|---|

| No visible outbound / all inbound / phones seem quiet | \#1: The Phones Are Quiet |

| Running ads, on lead gen platforms, buying leads | \#2: Ads Are Broken |

| Established business (10+ years), old-school industry | \#3: Before There Were Ads |

| Heavy automation, chatbots, auto-texts on website | \#4: People Want a Human |

| Competitive market, everyone has same tech/tools | \#5: Everyone Has AI — Nobody Has This |

| Lots of automation, tech-forward company | \#6: The Google Problem |

| Long-established, large customer/candidate database | \#7: Your List/Book/Database Is a Goldmine |

| Business depends on follow-up (quotes, estimates, applications) | \#8: The Silent Bleed |

| Highly competitive local market, many similar businesses | \#9: Your Competitors' Phones Are Ringing |

| On lead gen platforms, paying middlemen for leads | \#10: Go Direct |

If multiple signals are present, pick the one that creates the most specific, compelling email based on what you found in research. Avoid generic signals — go with the most concrete finding.

\#\# EMAIL WRITING RULES

\#\#\# Structure (5 variables, in this order):

1\. \*\*Relevance\*\* — one sentence proving this email was meant for them. Reference a specific detail from research.

2\. \*\*Pain\*\* — call out their exact situation. Use their industry language.

3\. \*\*Value prop\*\* — outcome-focused, one sentence. What they get, not what you do.

4\. \*\*Risk reversal\*\* — remove the risk (rotate from the options below)

5\. \*\*Soft CTA\*\* — ask a question. Never ask for a call. Never send a link.

\#\#\# Word Count: 50–100 words. COUNT THEM. No exceptions.

\#\#\# Banned Words — NEVER use any of these:

\- pay, price, cost, investment, fee, spend, budget

\- affordable, cheap, expensive, ROI

\- leverage, synergy, innovative, cutting-edge, solution, revolutionary

\- "I hope this finds you well"

\- "I'd love to"

\- "I wanted to reach out"

\- "I came across your company"

\- "pick your brain"

\#\#\# Tone Rules:

\- Sound like a friend, not a salesperson

\- Short sentences. Short paragraphs. Max 3-4 sentences per paragraph.

\- Write like you talk. If you wouldn't say it out loud, don't write it.

\- No corporate speak. No buzzwords. No filler.

\- 8th grade reading level

\#\#\# Risk Reversal Options (rotate — don't use the same one twice in a row):

1\. "If the appointments aren't coming in, you don't owe us anything."

2\. "If you're not seeing better results than before, we keep going at no charge until you do."

3\. "We guarantee someone is on your phones every single day. If we don't deliver, we work for free until we do."

4\. "No contracts. No lock-in. If it's not working, you leave."

5\. "If your pipeline/calendar isn't stronger than before we started, we keep working until it is — on us."

\#\#\# Subject Line Rules:

\- 1–4 words ONLY

\- ALL LOWERCASE

\- Must look like a coworker or friend sent it

\- Vague enough they don't know what's inside

\- Never sell in the subject line

\- Good examples: "{first\_name}, quick thought" | "your phones" | "question for you" | "different angle" | "quick idea"

\#\#\# Spintax Embedding Rules:

Embed Spintax in TWO places only — the greeting and the CTA. This gives deliverability variation without making the email feel templated.

\*\*Greeting Spintax:\*\*

Always start with: {Hey|Hi|Hello} {first\_name},

\*\*CTA Spintax (pick one pattern per email and embed):\*\*

\- "{Worth a look|Something worth exploring|Would this be helpful}?"

\- "{Is that something you'd want to hear more about|Would you want more info on how that works|Want me to send over some details}?"

\- "Is {follow-up|outbound|keeping the pipeline full|filling the calendar} something {you've got handled|that's on your radar|that's slipping right now}?"

\- "{How are you handling|What does your process look like for} {follow-up|outbound|customer outreach|candidate sourcing} right now?"

\*\*Do NOT use Spintax in:\*\*

\- The relevance/research line (must be 100% unique per lead)

\- The pain callout (must be specific to their situation)

\- The value prop (must match the framework)

\- The risk reversal (rotate manually between leads, don't Spintax it)

\#\# VERTICAL-SPECIFIC LANGUAGE

Use the correct terminology for each vertical. This is critical — using the wrong words signals you don't know their industry.

\*\*Insurance:\*\* book of business, write policies, renewals, carriers, quotes (not estimates), prospects, annual review, lapsed policies, cross-sell, multi-line, production

\*\*HVAC:\*\* tune-ups, maintenance agreements, system replacement, techs, installers, service calls, demand calls, shoulder season, change-outs, dispatching

\*\*Pest Control:\*\* routes, recurring plans, treatments, one-time customers, quarterly service, termite inspection, general pest, cancellations, crawl space

\*\*Staffing:\*\* fill rate, job orders, placements, reqs, submittals, speed-to-fill, redeployment, temp-to-perm, passive candidates, candidate pipeline, ATS

\*\*Real Estate:\*\* SOI/sphere, expireds, FSBOs, circle prospecting, ISA, listings, buyer leads, CMA, GCI, drip campaigns, portal leads, farming

\#\# OUTPUT FORMAT

For each lead, output a row with these exact columns:

first\_name, last\_name, email, company, vertical, framework\_used, research\_notes, email\_subject, email\_body

\#\#\# Column Definitions:

\- \*\*first\_name\*\*: Lead's first name

\- \*\*last\_name\*\*: Lead's last name

\- \*\*email\*\*: Lead's email address

\- \*\*company\*\*: Company name

\- \*\*vertical\*\*: One of: insurance, hvac, pest\_control, staffing, real\_estate

\- \*\*framework\_used\*\*: Which framework number was selected (1-10) and short name

\- \*\*research\_notes\*\*: 2-3 bullet points of key findings from research (for your records, not sent)

\- \*\*email\_subject\*\*: The subject line (lowercase, 1-4 words, Spintax okay here)

\- \*\*email\_body\*\*: The full email body with Spintax embedded in greeting and CTA

\#\#\# Example Row:

first\_name: Mike

last\_name: Johnson

email: mike@mikesjhvac.com

company: Mike's HVAC

vertical: hvac

framework\_used: \#7 \- Your Customer List Is a Goldmine

research\_notes: In business 18 years, 4.8 stars / 220 reviews, residential HVAC in Chandler AZ, runs Google Ads, has ServiceTitan, no visible outbound, maintenance agreement page on site but not prominent

email\_subject: your list

email\_body: {Hey|Hi|Hello} Mike, after 18 years doing HVAC in Chandler, you've probably got thousands of past customers who haven't heard from you in months. Every one of them has a system that's aging — some are due for tune-ups, some are sitting on 15-year-old units ready for a change-out. Nobody's calling them. That list is a goldmine sitting in ServiceTitan. We put someone on your phones who works that list every day. If your calendar isn't fuller, we work for free until it is. {How big is your past customer list at this point|Roughly how many past customers are in your system right now}?

---

# PART 2: INPUT FORMAT

*This is what you feed the agent. Each lead needs at minimum these fields. The agent does the rest.*

---

## Minimum Input Per Lead:

| Field | Required? | Notes |
| :---- | :---- | :---- |
| first\_name | Yes | Lead's first name |
| last\_name | Yes | Lead's last name |
| email | Yes | Verified email |
| company | Yes | Company name |
| website | Recommended | Company website URL — dramatically improves research quality |
| vertical | Recommended | insurance, hvac, pest\_control, staffing, real\_estate — if not provided, agent will determine from research |
| city | Recommended | Helps with market-specific references |
| state | Recommended | Helps with market-specific references |

## Example Input CSV:

first\_name,last\_name,email,company,website,vertical,city,state

Mike,Johnson,mike@mikeshvac.com,Mike's HVAC,mikeshvac.com,hvac,Chandler,AZ

Sarah,Williams,sarah@swinsurance.com,SW Insurance Group,swinsurancegroup.com,insurance,Dallas,TX

Jason,Chen,jason@elitestaffing.com,Elite Staffing Solutions,elitestaffing.com,staffing,Phoenix,AZ

Dave,Martinez,dave@arizonapest.com,Arizona Pest Solutions,arizonapest.com,pest\_control,Tucson,AZ

Lisa,Thompson,lisa@lisathompsonhomes.com,Lisa Thompson Real Estate,lisathompsonhomes.com,real\_estate,Scottsdale,AZ

---

# PART 3: OUTPUT FORMAT — Instantly-READY CSV

*This is what the agent outputs. Upload directly to Instantly.*

---

## Output CSV Columns:

first\_name,last\_name,email,company,email\_subject,email\_body,email2\_subject,email2\_body,email3\_body,email4\_body

### Column Mapping in Instantly:

| CSV Column | Instantly Field | How It's Used |
| :---- | :---- | :---- |
| first\_name | {{first\_name}} | Standard merge field |
| last\_name | {{last\_name}} | Standard merge field |
| email | Email | Required for sending |
| company | {{company}} | Standard merge field |
| email\_subject | {{email\_subject}} | Custom field — used as Subject in template |
| email\_body | {{email\_body}} | Custom field — used as Body in template |
| email2\_subject | {{email2\_subject}} | Custom field — Email 2 subject |
| email2\_body | {{email2\_body}} | Custom field — Email 2 body |
| email3\_body | {{email3\_body}} | Custom field — Email 3 body |
| email4\_body | {{email4\_body}} | Custom field — Email 4 body |

### Instantly Email Template Setup:

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

# PART 4: FOLLOW-UP EMAIL INSTRUCTIONS

*These are the instructions for the agent when writing Emails 2, 3, and 4 for each lead.*

---

## Email 2 (Day 3\) — Different Framework, Completely New Angle

For Email 2, select a DIFFERENT framework than Email 1\. Do NOT reference Email 1\. Do NOT say "just following up." Write a completely new email with a completely new angle as if Email 1 never existed.

Use the same research but apply a different framework. If Email 1 used \#7 (Goldmine), Email 2 might use \#3 (Before There Were Ads) or \#8 (Silent Bleed).

Same rules apply: 50-100 words, specific detail from research, risk reversal, soft CTA, Spintax in greeting and CTA.

## Email 3 (Day 7\) — Short Bump, 2-3 Sentences Max

Email 3 is a short bump. 2-3 sentences maximum. No framework structure needed. Just a quick, human check-in that references the core pain point.

Template pattern (customize per lead):

"{Hey|Hi} {first\_name}, did that last note land? {Curious if|Wondering whether} {pain\_point\_reference} is {still on your radar|something you're thinking about|still a priority}."

Examples:

\- "Hey Mike, did that last note land? Curious if keeping the calendar full is still on your radar."

\- "Hi Sarah, did that last note land? Wondering whether follow-up on old quotes is something you're thinking about."

\- "Hey Jason, did that last note land? Curious if candidate sourcing is still a bottleneck."

Keep it under 30 words. Subject line: re: {{email\_subject}} (threading with Email 1\)

## Email 4 (Day 14\) — Breakup Email

Email 4 is the breakup. Polite, final, no pressure. Give them an easy out while leaving the door open.

Template pattern (customize per lead):

"{Hey|Hi} {first\_name}, I'll leave you alone after this. If {pain\_point} isn't {a priority|top of mind} right now, totally get it. But if it is, {this would be worth 5 minutes|I think this could help}. Either way, no hard feelings."

Keep it under 40 words. Subject line: "last one"

Do NOT use aggressive urgency. Do NOT guilt trip. Do NOT say "this is your last chance." Just be human about it.

---

# PART 5: BATCH PROCESSING INSTRUCTIONS

*How to run this at scale.*

---

## Processing Workflow:

1. **Prepare input CSV** with lead data (minimum: name, email, company, website, vertical, city, state)  
2. **Feed leads to the agent in batches of 10-20** — this gives the agent enough context to vary frameworks and risk reversals across the batch without repeating patterns  
3. **Agent researches each lead** — web search, Google Maps, reviews, website, social, job boards  
4. **Agent selects framework and writes all 4 emails per lead**  
5. **Agent outputs Instantly-ready CSV**  
6. **Review the output** — spot-check 3-5 emails per batch for quality, accuracy, and word count  
7. **Upload CSV to Instantly** — map custom fields  
8. **Set up campaign** — Email 1 sends Day 1, Email 2 Day 3, Email 3 Day 7, Email 4 Day 14  
9. **Monitor replies** — positive replies go to your unified inbox for manual follow-up

## Quality Control Checklist (per batch):

- [ ] Every email is 50-100 words (count a few randomly)  
- [ ] No banned words appear (pay, price, cost, investment, etc.)  
- [ ] Every email contains at least one specific research detail  
- [ ] Subject lines are 1-4 words, lowercase  
- [ ] Risk reversals are rotated (not the same one 5 times in a row)  
- [ ] Spintax is in greeting and CTA only  
- [ ] Vertical-specific language is correct (not using HVAC terms for insurance leads)  
- [ ] Email 2 uses a different framework than Email 1 for each lead  
- [ ] Email 3 is under 30 words  
- [ ] Email 4 is under 40 words

## Volume Guidelines:

| Batch Size | Agent Processing Time | Notes |
| :---- | :---- | :---- |
| 10 leads | \~15-20 min | Good for testing and dialing in quality |
| 25 leads | \~30-45 min | Standard daily batch |
| 50 leads | \~60-90 min | Max recommended per session for quality |
| 100+ leads | Split into batches of 25-50 | Don't sacrifice research depth for volume |

---

# PART 6: Instantly CAMPAIGN SETUP

*Step-by-step for getting this live in Instantly.*

---

## Step 1: Create Campaign

- Name it by vertical and date: "HVAC \- Phoenix \- May 2026"  
- Separate campaigns per vertical (don't mix HVAC and Insurance in one campaign)

## Step 2: Upload Lead CSV

- Upload the agent's output CSV  
- Map standard fields: first\_name, last\_name, email, company  
- Map custom fields: email\_subject, email\_body, email2\_subject, email2\_body, email3\_body, email4\_body

## Step 3: Set Up Email Sequence

**Email 1 (Day 1):**

- Subject: `{{email_subject}}`  
- Body: `{{email_body}}`  
- Send window: Business hours, Mon-Fri

**Email 2 (Day 3):**

- Subject: `{{email2_subject}}`  
- Body: `{{email2_body}}`

**Email 3 (Day 7):**

- Subject: `re: {{email_subject}}`  
- Body: `{{email3_body}}`

**Email 4 (Day 14):**

- Subject: `{last one|one more thing|final thought}`  
- Body: `{{email4_body}}`

## Step 4: Sending Settings

- Max emails per mailbox per day: 25-30 (start low, scale up)  
- Send interval: 3-5 minutes between emails  
- Warmup: Keep warmup running alongside campaigns  
- Reply detection: Auto-pause sequence when lead replies  
- Rotate across 3-4 mailboxes per campaign

## Step 5: Domain Setup

- Never send from your main domain (usingaitoscale.com)  
- Use dedicated cold email domains (e.g., usingaitoscale.co, usingaitoscale.io, usingai-scale.com)  
- 3-4 mailboxes per domain  
- SPF, DKIM, DMARC configured (Instantly's Smart Senders handles this if you buy through them)  
- Warm up for minimum 2 weeks before first send

## Step 6: Monitor & Optimize

| Metric | Benchmark | If Below |
| :---- | :---- | :---- |
| Open rate | 50-70% | Subject lines aren't working. Test new variations. |
| Reply rate | 3-8% | Copy issue. Try different frameworks. |
| Positive reply rate | 1-3% | Value prop or targeting issue. Tighten your list. |
| Bounce rate | Under 3% | List quality issue. Verify emails before uploading. |
| Spam complaints | Under 0.1% | Deliverability issue. Check domain health, slow down sending. |

---

# PART 7: EXAMPLE FULL OUTPUT

*What a complete batch output looks like for 5 leads across all verticals.*

---

## Lead 1: HVAC

first\_name: Mike

last\_name: Johnson

email: mike@mikeshvac.com

company: Mike's HVAC

email\_subject: your list

email\_body: {Hey|Hi|Hello} Mike, after 18 years doing HVAC in Chandler, you've probably got thousands of past customers who haven't heard from you in months. Every one of them has a system that's aging. Some are due for tune-ups. Some are sitting on 15-year-old units ready for a change-out. Nobody's calling them. We put someone on your phones who works that list every day. If your calendar isn't fuller, we work for free until it is. {How big is your past customer list at this point|Roughly how many past customers are in your system}?

email2\_subject: quick thought

email2\_body: {Hey|Hi|Hello} Mike, HVAC keywords in the Phoenix metro are running insane on Google right now. And HomeAdvisor leads are getting shared with 3-4 other companies. The companies growing fastest aren't spending more on ads — they've got someone calling past customers and old estimates every day. No ad spend, just working the list. We set that up and manage everything. If you're not booking more jobs than before, we keep going at no charge. {Where are most of your leads coming from right now|How are you generating most of your business right now}?

email3\_body: {Hey|Hi} Mike, did that last note land? Curious if keeping the calendar full is still on your radar.

email4\_body: {Hey|Hi} Mike, I'll leave you alone after this. If getting more out of your customer list isn't a priority right now, totally get it. But if it is, this would be worth 5 minutes. Either way, no hard feelings.

## Lead 2: Insurance

first\_name: Sarah

last\_name: Williams

email: sarah@swinsurance.com

company: SW Insurance Group

email\_subject: the quiet ones

email\_body: {Hey|Hi|Hello} Sarah, the quotes that go quiet are probably costing you more than you think. Someone asks for a life quote. You send it. They say "let me think about it." Then silence. No "I went with someone else." Just gone. Multiply that by 10-15 a month and it's a lot of premium walking out the door. We put someone on your phones who follows up on every quote. Day 1, Day 3, Day 7, Day 14\. If they're not booking, you owe us nothing. {How many quotes go quiet on you in a typical month|Is quote follow-up something that's slipping right now}?

email2\_subject: your book

email2\_body: {Hey|Hi|Hello} Sarah, after 12 years writing life insurance in Dallas, your book of business is probably your most valuable asset. But when's the last time someone called every client for an annual review? Or checked on renewals coming due? Most agents have hundreds of clients they haven't spoken to in a year. Each one is a referral source and a cross-sell opportunity going untouched. We put someone on your phones who works your book every day. If your production doesn't go up, we work for free. {How big is your book right now|How many clients are in your book at this point}?

email3\_body: {Hey|Hi} Sarah, did that last note land? Curious if follow-up on old quotes is something you're thinking about.

email4\_body: {Hey|Hi} Sarah, I'll leave you alone after this. If keeping your pipeline warm isn't a priority right now, totally get it. But if it is, this would be worth 5 minutes. Either way, no hard feelings.

## Lead 3: Staffing

first\_name: Jason

last\_name: Chen

email: jason@elitestaffing.com

company: Elite Staffing Solutions

email\_subject: your pipeline

email\_body: {Hey|Hi|Hello} Jason, you guys are placing warehouse and logistics workers in Phoenix — solid niche. Quick question: are your recruiters doing daily outbound calls to candidates, or mostly waiting for Indeed applications? Most staffing firms I talk to have recruiters buried in admin — outbound sourcing is the first thing that drops. We put a dedicated person on outbound calls and texts to candidates in your market. Every day. We manage everything. If you're not filling faster, you don't owe us anything. {Is candidate sourcing the main bottleneck right now|Are your recruiters mostly doing outbound or waiting for apps}?

email2\_subject: quick idea

email2\_body: {Hey|Hi|Hello} Jason, before LinkedIn Recruiter and Indeed Resume, staffing firms grew one way — picking up the phone. Calling candidates directly, calling past applicants, calling referrals. That's working again because nobody does it anymore. Everyone's relying on the same job boards and InMail templates. A real phone call stands out. We put someone on outbound calls to candidates in your market. Every day. If your pipeline isn't stronger, we work for free until it is. {When's the last time your team did a full day of outbound candidate calls|How much of your sourcing is outbound vs inbound right now}?

email3\_body: {Hey|Hi} Jason, did that last note land? Curious if candidate sourcing is still a bottleneck.

email4\_body: {Hey|Hi} Jason, I'll leave you alone after this. If filling faster isn't a priority right now, totally get it. But if it is, this would be worth 5 minutes. Either way, no hard feelings.

## Lead 4: Pest Control

first\_name: Dave

last\_name: Martinez

email: dave@arizonapest.com

company: Arizona Pest Solutions

email\_subject: quick thought

email\_body: {Hey|Hi|Hello} Dave, you guys do pest control in Tucson — looks like a solid operation with great reviews. Quick question: do you have someone calling your one-time customers every day? The people who called once for scorpions or ants but never signed up for a quarterly plan? Most pest companies I talk to have hundreds of those just sitting in the system. We put someone on your phones who works that list every day. We manage everything. If you're not adding more recurring accounts, we work for free. {How many one-time customers would you guess are in your system|Is converting one-timers to recurring something you've been thinking about}?

email2\_subject: the quiet ones

email2\_body: {Hey|Hi|Hello} Dave, the cancellations that happen quietly are the ones that hurt the most. A customer on quarterly service just stops scheduling. No complaint. No call. They just don't rebook. Nobody calls to find out why. Multiply that by 5-10 a month and your recurring revenue is bleeding out slowly. We put someone on your phones who catches every cancellation and every lapsed account. If your retention doesn't improve, you owe us nothing. {How many cancellations do you see in a typical month|Is churn something you're tracking closely right now}?

email3\_body: {Hey|Hi} Dave, did that last note land? Curious if filling routes is still on your radar.

email4\_body: {Hey|Hi} Dave, I'll leave you alone after this. If keeping routes full isn't top of mind right now, totally get it. But if it is, this would be worth 5 minutes. Either way, no hard feelings.

## Lead 5: Real Estate

first\_name: Lisa

last\_name: Thompson

email: lisa@lisathompsonhomes.com

company: Lisa Thompson Real Estate

email\_subject: your database

email\_body: {Hey|Hi|Hello} Lisa, after 15 years selling in Scottsdale, your database is probably your most valuable asset. Past buyers, past sellers, open house visitors, your entire sphere. How many of them have heard from you in the last 90 days? For most agents, the answer is almost none. Every one of those people knows somebody thinking about buying or selling. You just have to ask. We put someone on your phones who works that database every day. If your pipeline isn't stronger, we work for free. {How big is your database right now|How are you staying in touch with your sphere right now}?

email2\_subject: different angle

email2\_body: {Hey|Hi|Hello} Lisa, your past clients are getting automated "happy home anniversary" emails from every agent and lender in Scottsdale. Same template, same energy. You know what actually gets a referral? A phone call. A real person saying "Hey, how's everything going with the house? Know anyone thinking about buying or selling?" We put that person on your phones. Every day. If referrals aren't coming in, you walk — no questions. {Is your sphere outreach mostly automated right now|Does someone actually call your past clients or is it all drip emails}?

email3\_body: {Hey|Hi} Lisa, did that last note land? Curious if keeping your pipeline full is still on your radar.

email4\_body: {Hey|Hi} Lisa, I'll leave you alone after this. If prospecting isn't top of mind right now, totally get it. But if it is, this would be worth 5 minutes. Either way, no hard feelings.

---

# PART 8: QUICK-START CHECKLIST

*Everything you need to get this running.*

---

- [ ] **Lead list prepared** — minimum: name, email, company, website, vertical, city, state  
- [ ] **Vertical-specific framework docs loaded** — give the agent the right framework doc for the vertical it's processing  
- [ ] **Agent system prompt loaded** — Part 1 of this document  
- [ ] **Run first test batch** — 10 leads, one vertical, review every email for quality  
- [ ] **Instantly campaign created** — separate campaign per vertical  
- [ ] **Cold email domains purchased** — 3-4 domains, not your main domain  
- [ ] **Mailboxes set up** — 3-4 per domain, SPF/DKIM/DMARC configured  
- [ ] **Warmup running** — minimum 2 weeks before first send  
- [ ] **CSV uploaded to Instantly** — custom fields mapped (email\_subject, email\_body, etc.)  
- [ ] **Email templates configured** — Subject \= {{email\_subject}}, Body \= {{email\_body}}  
- [ ] **Sending settings configured** — 25-30/day per mailbox, 3-5 min intervals, warmup stays on  
- [ ] **Reply handling set up** — auto-pause on reply, unified inbox for manual follow-up  
- [ ] **First campaign launched** — monitor open rates and reply rates for first 48 hours  
- [ ] **Optimize** — if below benchmarks, adjust frameworks, tighten targeting, test new angles

---

*End of AI Cold Email Agent System v1.0*  
