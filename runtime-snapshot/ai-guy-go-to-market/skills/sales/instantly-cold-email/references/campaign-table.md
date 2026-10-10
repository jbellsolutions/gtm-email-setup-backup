# Instantly Campaign Table

Last updated: July 20, 2026. Active campaigns, drafts, and stopped legacy campaigns.

## Active

| Campaign | Status | Leads | Instantly ID | Strategy |
|---|---|---|---|---|
| **PR Agencies - SpeakerAgent v2 - July 2026** | COMPLETED | 4,512 | 3577260 | Referral angle ("referral question" subject). Human operators (SpeakerAgent team) managing replies. Reply template → Tony's Calendly (`cal.com/speakeragent/catch-up`), CCs tony@speakeragent.ai. 8+ positive replies. Nicole Wald deferred to "start of August" Jul 20. |
| **Podcasters - SpeakerAgent v2 - July 2026** | ACTIVE | 3,076 | 3639259 | 🆕 Created July 14, sending began Jul 15. Referral angle: "people finding your podcast on speakeragent.ai, we want to send referrals." Single email, same settings as PR campaign #3577260. ⚠️ Reply template: `references/speakeragent-podcaster-reply-template.md`. NOT in daemon CAMPAIGN_CONTEXT — add hardcoded template (same pattern as #3316611). Booking: cal.com/speakeragent/15min. Isabel booked Jul 29, Peter Vera booked Tue Jul 21, Jeffrey Bradbury (TeacherCast) booked Jul 22 — call time TBD on SpeakerAgent Cal.com. |
| **AI Guy — Organic Outreach - June 2026** | ACTIVE | — | 3520103 | AI Integraterz outbound. 3-email sequence. Sends from `john@useaiintegraterz.com` and `aaron@joinaiintegraterz.com`. 500 max leads/day. Not in daemon CAMPAIGN_CONTEXT. |
| **AI Guy - Coaching/Consulting - July 2026** | ACTIVE | 1,215 | 3607306 | Sends from `jay@meetaiintegraterz.com` with niche-personalized emails. $10/hr AI operator offer. Not in daemon CAMPAIGN_CONTEXT. |
| **Coaching Owned Audiences - July 2026** | PAUSED | 9,457 | 3617053 | 🆕 Launched July 9, blast completed ~Jul 14. Referral-based — "people who already have your clients' trust" angle. 10+ operator personas. Auto-responder tail through ~Jul 18. First booking: Gina (beyondthescoreboards.com, Jul 21). **Owned Audiences campaign** — positive replies route through `owned-audiences-email-reply` skill. Booking: cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery. Full context: `references/campaign-3617053-owned-audiences.md`. Jeff Dillon (usmenshealth.com) replied positive Jul 20 — case study sent same-day. |
| **HVAC Owned Audience - July 2026** | ACTIVE | — | 3652623 | Sending since Jul 16. Zero genuine positives through Jul 20 — all OOO/auto-responders. **Owned Audiences campaign** — replies route through `owned-audiences-email-reply` skill. |
| **Recruiting & Staffing Owned Audience - July 2026** | ACTIVE | — | 3652624 | Sending since Jul 16. Zero genuine positives through Jul 20. Elevated retirement/OOO rate (recruiters). 1 hostile: Anna (anna@techiestaffing.com) "Remove me permanently" Jul 17. **Owned Audiences campaign** — replies route through `owned-audiences-email-reply` skill. |
| 🆕 **Solar - Local Installers - July 2026** | ACTIVE | — | 3691319 | Discovered Jul 20. Sends from Emilia @ growthliftwa.info. Cold email: roofers as front door to solar customers ("Every time a roof goes on without a solar conversation, someone lost a deal"). First reply: OOO from Daniel Moyer (GoCam Solar, Denver). NOT in daemon CAMPAIGN_CONTEXT. ⚠️ This is a SpeakerAgent-style cold email campaign, NOT an Owned Audiences campaign — replies should use SpeakerAgent template, not OA case study workflow. |
| 🆕 **Med Spa - Charm Offensive - July 2026** | ACTIVE | — | 3692104 | 🆕 Discovered Jul 22. New vertical campaign with hardcoded Charm sequences deployed directly to Instantly. Sending began ~Jul 22 morning ET. Cold email uses disarming honesty/humor ("You don't know me. I got your details from a list. Not the most romantic origin story..."). Targets dermatology/med spa decision-makers. Day 1 (Jul 22): 6 replies checked — 1 hostile (Kala Duncan, Procell Therapies), 1 OOO (Stephen Hendrickson: out until 1/26/26), 1 departed (John Kuntz, Blackpine), 1 acquisition (Jim O'Keefe, Precision Coatings → Rainguard), 1 invalid email (Eric Mask, Dermatology Consultants), 1 auto-redirect (Dave Staley, MSE Audio). Zero positives — normal for Charm Offensive day 1. NOT in daemon CAMPAIGN_CONTEXT. ⚠️ Charm Offensive reply handling TBD — NOT an Owned Audiences campaign. |

## Stopped / Completed

| Campaign | Status | Leads | Instantly ID | Notes |
|---|---|---|---|---|
| **HVAC - Texas - June 2026** | COMPLETED | 1,012 | 3442703 | 4-email sequence complete ~June 29. 20 lifetime replies. 2 unhandled positives (Alpha Mechanical + Source Rentals). Positive reply rate: 0.074% — FAIL below benchmark. |
| **HVAC - Florida - June 2026** | PAUSED | 1,097 | 3441343 | **PAUSED after Spintax incident** — ~850 emails sent with raw `{Hey\|Hi\|Hello}` literal. All emails burned (Instantly dedup). |
| **recruiters-power-partner-A** | STOPPED | — | 3249954 | Legacy recruiter campaign (Apr 2026). |
| **recruiters-direct-value-A** | STOPPED | — | 3249956 | Legacy recruiter campaign (Apr 2026). |
| **SpeakerAgent PR - Legacy - May 2026** | STOPPED | — | 3337105 | Legacy. 15 replies on deep pages (140-159), 1 positive (Jim, 41 days stale). |
| **SpeakerAgent v1 - Legacy - May 2026** | STOPPED | — | 3316611 | Legacy. 2 residual replies. |
| **ai-operator-10hr-niche** | STOPPED | 1,948 | 3287518 | Med-spa niche. Stopped May 14. |
| **home-services-hvac-florida** | STOPPED | 1,170 | 3318534 | Legacy FL HVAC. ⚠️ `send_as_plain_text: false`. |

## Drafted (Not Yet Launched)

| Campaign | Status | Leads | Instantly ID | Notes |
|---|---|---|---|---|
| HVAC - Florida v2 | DRAFTED | 1,090 | 3442743 | Replacement for #3441343. ⚠️ Needs fresh emails. |
| HVAC - North Carolina | DRAFTED | 356 | 3442704 | Ready — needs inboxes. |
| HVAC - South Carolina | DRAFTED | 192 | 3442705 | Ready — needs inboxes. |
| HVAC - Tennessee | DRAFTED | 197 | 3442706 | Ready — needs inboxes. |
| HVAC - Southwest (AZ/OK) | DRAFTED | 0 | 3442816 | Needs leads. |
| HVAC - Deep South (LA/AL/MS) | DRAFTED | 0 | 3442817 | Needs leads. |
| HVAC - West (NV/CA) | DRAFTED | 0 | 3442818 | Needs leads. |
| HVAC - Great Lakes | DRAFTED | 0 | 3442819 | Needs leads. |
| HVAC - Northeast | DRAFTED | 0 | 3442820 | Needs leads. |
| MCA - DialDesk | DRAFTED | 56 | 3523676 | MCA/business lending. Needs inboxes. |
| PR Agency Referral Network | DRAFTED | 0 | 3601938 | Empty — cross-campaign dedup blocked upload. |

## CAMPAIGN_CONTEXT Gaps (P0 — daemon misses positive replies)

As of July 22, 2026: **9 campaigns missing from daemon's CAMPAIGN_CONTEXT dict.** Any positive reply to these campaigns gets mismatched drafts or silently dropped.

| Campaign | ID | Reply Template |
|---|---|---|
| PR Agencies v2 | 3577260 | SpeakerAgent PR template (`references/speakeragent-pr-reply-template.md`) |
| AI Guy | 3520103 | AI operator $10/hr offer |
| AI Guy - Coaching | 3607306 | AI operator $10/hr offer |
| Coaching Owned Audiences | 3617053 | OA case study (`owned-audiences-email-reply` skill) |
| Podcasters - SpeakerAgent v2 | 3639259 | Podcaster template (`references/speakeragent-podcaster-reply-template.md`) |
| HVAC Owned Audience | 3652623 | OA case study (`owned-audiences-email-reply` skill) |
| Recruiting & Staffing Owned Audience | 3652624 | OA case study (`owned-audiences-email-reply` skill) |
| 🆕 Solar - Local Installers | 3691319 | SpeakerAgent template (same pattern as podcaster/PR) |
| 🆕 Med Spa - Charm Offensive | 3692104 | Charm Offensive reply handling TBD — NOT OA, NOT SpeakerAgent. New vertical. |

**Confirmed impact:** Peter Vera (#3639259, Jul 16) sat 2.5h unhandled. Scott Kaier (#3577260, Jul 7) sat 8 days. Sam Frontera (#3577260, Jul 2) sat 13 days. Spark (#3577260, Jul 16) second reply missed entirely. Cross-campaign monitoring sweeps are the only safety net until CAMPAIGN_CONTEXT is populated.

1. Med-spa groups ✅ DONE
2. Home services — HVAC (Florida) ✅ DONE
3. Personal injury law firms
4. Family law firms
5. Immigration law firms
6. IP / patent law firms
7. Estate planning & probate firms
8. Tax / CPA / accounting firms (multi-partner)
9. Wealth management / RIA firms
10. B2B sales coaching & consulting firms
11. SMB marketing agencies (5–25 employees)
12. Property management firms
13. Online course creators / business coaches / sales trainers
14. Health & fitness coaches / career coaches
15. YouTube channel operators / Skool community owners
16. Copywriters / ghostwriters / digital product creators
17. Affiliate marketers / DTC solo founders

**Sending rules:** Mon-Fri 8AM-5PM ET, 1,000 leads/day, plain text, AI ESP matching ON, reply-only tracking.