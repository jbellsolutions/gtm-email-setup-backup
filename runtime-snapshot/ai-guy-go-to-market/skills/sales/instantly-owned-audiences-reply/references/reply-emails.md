# Reply Email Templates

**Rules for every variant:** plain text · no banned words · no pricing. Never sign as Justin — sign as the persona the lead originally replied to. **Never echo the lead's exact words back in your greeting** (e.g., if they wrote "Surely," do NOT write "Surely love that" — use "Thanks — here it is" instead).

## ⚠️ BANNED PHRASES (Justin, July 15 2026)

These phrases must NEVER appear in any reply:

| Banned | Why | Use Instead |
|---|---|---|
| "No rush" / "No pressure" | Kills urgency entirely | "We're here now — the window is perfect" |
| "When you're ready" | Passive, defers action indefinitely | "Go book in a time now" |
| "Thank you for the reply" / "Thanks for the reply" | Makes us sound grateful they bothered | "Love the quick yes" / "Got it" / Skip entirely |
| "The door's open" | Implies we'll wait forever | "Let's get this moving" |
| "Grab some time" | Too casual, implies optional | "Book in a time now" |
| "If you're interested" | Invites them to defer | "Here's the link — jump on it" |

## Required Tone (every reply)

- **Create urgency.** Every reply should make them feel like now is the moment.
- **Direct commands, not suggestions.** "Go book..." not "feel free to..."
- **Push to next step immediately.** Never end a reply without a clear booking directive.
- **Confident, not deferential.** We're offering something valuable. Act like it.

## Case Study Library

Match the lead's vertical to the closest case study. All URLs are permanent here.now links.

| Vertical | Case Study URL |
|---|---|
| Men's health / TRT / hormone clinics | https://aiintegraterz.com/case-studies/mens-health.pdf |
| Men's coaching / fitness coaching | https://aiintegraterz.com/case-studies/mens-coaching.pdf |
| Marketing agencies | https://aiintegraterz.com/case-studies/marketing-agency.pdf |
| Solar companies | https://aiintegraterz.com/case-studies/solar.pdf |
| AI agencies / AI automation | https://aiintegraterz.com/case-studies/ai-agency.pdf |
| MCA / alternative lending | https://aiintegraterz.com/case-studies/mca.pdf |
| Recruiting / staffing agencies (general) | https://aiintegraterz.com/case-studies/recruiting.pdf |
| Recruiting — master / full-service | https://aiintegraterz.com/case-studies/recruiting-master.pdf |
| Recruiting — exec search | https://aiintegraterz.com/case-studies/exec-search.pdf |
| Recruiting — IT staffing | https://aiintegraterz.com/case-studies/it-staffing.pdf |
| HVAC / home services | https://aiintegraterz.com/case-studies/hvac.pdf |

## Mandatory email structure

Every reply has TWO sections — the custom top and the locked bottom template.

### TOP — Custom per lead

**Opener:** Acknowledge what the lead specifically said in their reply. Don't just say "here it is" — reference their words. Options:
- "Ask and ye shall receive. Here you go —>" (Justin's approved variant)
- "You got it. Here you go —>"
- "Love the quick yes. Here you go —>"
- "Right on. Here you go —>"

The opener MUST be followed by the case study link on the SAME line, then a line break, then the one-sentence results hook, then "Check out the report here" on its own line. The case study link and "Check out the report here" MUST use HTML `<a>` tags — bare URLs are NOT clickable in email clients.

**Results hook:** One sentence about the case study result (pick the most relevant stat). Do NOT attach any PDF — the link IS the delivery.

**After the hook, new paragraph:** "Check out the report here" as a clickable HTML link.

### BOTTOM — Locked template (MUST be verbatim, DO NOT edit a single character)

```html
When we take this on, we build a complete custom plan for you at no charge — your partner map, your voices, your shows — and we'll review it together live on a call so you know exactly what it means and how to use it.

<a href="{booking_link}">Book in some time with our founder here</a>

{SenderPersona}
<a href="{site_link}">More on the approach</a>
```

The only variables are `{booking_link}` and `{site_link}` — everything else is verbatim. `{SenderPersona}` is the name from the `from` field of the original sent email (e.g., Willow, Bella, Anna, Audrey, Penelope).

---

## ⛔ FORMATTING: Blank lines are MANDATORY — never strip them

The email body MUST have 5 blank lines separating 6 sections. Without blank lines, the email renders as one unreadable blob (Jeff incident, July 20, 2026). **Always verify blank lines before sending.**

## Example (warm yes — approved July 16, 2026)

Justin, a men's health / TRT clinic lead, replied to Paisley with a warm yes.

```
Ask and ye shall receive. Here you go --> <a href="https://aiintegraterz.com/case-studies/mens-health.pdf">aiintegraterz.com/case-studies/mens-health.pdf</a>
                                            ↑ BLANK LINE ABOVE — do not collapse
This one clinic we worked with turned their gyms and barbershops into a referral engine — 15+ booked consults in their first 30 days.
                                            ↑ BLANK LINE ABOVE
<a href="https://aiintegraterz.com/case-studies/mens-health.pdf">Check out the report here</a>
                                            ↑ BLANK LINE ABOVE
When we take this on, we build a complete custom plan for you at no charge — your partner map, your voices, your shows — and we'll review it together live on a call so you know exactly what it means and how to use it.
                                            ↑ BLANK LINE ABOVE
<a href="https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery">Book in some time with our founder here</a>
                                            ↑ BLANK LINE ABOVE
Paisley
<a href="https://aiintegraterz.com/stop-renting">More on the approach</a>
```

**In JSON for Instantly, this means:** `email_body` must contain `\\n\\n` (escaped double-newline) between every section. Count them: there should be 5 occurrences of `\\n\\n` in the body string. If you see a wall of text with no breaks, the `\\n\\n` sequences are missing.

**Common failure:** Single `\\n` instead of `\\n\\n` — renders as one blob. Always double-check.

**Structure (every first reply follows this exactly):**

1. `[Opener] {case_study_link}` — opener + hyperlinked case study URL on the SAME line, using HTML `<a>` tag
2. Blank line
3. `{One-sentence results hook}` — most relevant stat from the case study
4. Blank line
5. `<a href="{case_study_url}">Check out the report here</a>` — HTML hyperlink on its own line
6. Blank line
7. `When we take this on, we build a complete custom plan for you at no charge — your partner map, your voices, your shows — and we'll review it together live on a call so you know exactly what it means and how to use it.`
8. Blank line
9. `<a href="{booking_link}">Book in some time with our founder here</a>` — HTML hyperlink
10. Blank line
11. `{SenderPersona}`
12. `<a href="{site_link}">More on the approach</a>` — HTML hyperlink

**Variables per lead:**
- `[Opener]`: acknowledge their specific reply — "Ask and ye shall receive. Here you go -->" (default), "You got it. Here you go -->", "Love the quick yes. Here you go -->", "Right on. Here you go -->"
- `{case_study_url}`: full URL to the vertical-matched case study (used in TWO places — opener line AND "Check out the report here" link)
- `{case_study_display}`: the URL without https:// for display text (e.g., "aiintegraterz.com/case-studies/mens-health.pdf")
- `{results_hook}`: one sentence with the most relevant stat from the matched case study
- `{booking_link}`: always `https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery`
- `{booking_display}`: always `cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery`
- `{SenderPersona}`: persona matching the original FROM address domain
- `{site_link}`: always `https://aiintegraterz.com/stop-renting`
- `{site_display}`: always `aiintegraterz.com/stop-renting`

**Rules:**
- ALL links use HTML `<a href="URL">display text</a>` tags — NEVER bare URLs
- Display text is the URL without `https://` prefix (e.g., `aiintegraterz.com/case-studies/mens-health.pdf`)
- No "thanks for the reply" / "thank you" — ever
- No "no rush" / "when you're ready" / "if you're interested" / "zero obligation"
- Opener MUST acknowledge what the lead specifically said — reference their words
- Bottom template is verbatim — only links change
- Sender persona MUST match the domain that originally emailed them

## Domain → Persona Mapping (complete)

| Domain | Persona |
|---|---|
| prosperliftwi.info | Audrey |
| growthliftwa.info | Emilia |
| successcrestco.info | Willow |
| progressaxismd.info | Lucy |
| horizonstepfl.info | Julia |
| growthmapar.info | Mila |
| horizonvistaky.info | Natalie |
| elevatedeskin.info | Anna |
| progressdeskks.info | Madeline |
| prosperaxisma.info | Aaliyah |
| growthsignalmn.info | Violet |
| growthliftaz.info | Bella |
| progressvistasc.info | Penelope |
| scaledeskct.info | Penelope |
| horizonlineva.info | Allison |

## Flyback Template

See `references/flyback-template.md` for the recovery email variant used when a lead calls out a low-quality AI-generated plan.