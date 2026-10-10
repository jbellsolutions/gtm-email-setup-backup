---
name: email-newsletter-creation
description: "Create email newsletters in the My Claw style — emoji headlines, TL;DR story format, sponsor CTA, HTML + plain text dual output."
version: 1.0.0
tags: [newsletter, email, content-creation, myclaw, sponsor]
---

# Email Newsletter Creation

Create email newsletters modeled on the My Claw newsletter format — a clean, scannable style with emoji headlines, TL;DR story summaries, and an integrated sponsor call-to-action. Produces both HTML and plain text versions ready for email sending.

## When to Use

- User asks to create a newsletter (for any topic/sponsor)
- User references "My Claw newsletter" as a format template
- User wants an email newsletter with sponsor CTA
- User mentions "like the My Claw format" or "similar to My Claw"

## The My Claw Format (Deconstructed)

The My Claw newsletter (`newsletter@myclaw.ai`) follows this exact structure:

### Subject Line
```
🦞 Agent Runs Mom's Business
```
Single emoji + punchy headline. No date. No issue number.

### Subtitle (below subject, in email preview)
```
Plus: Netflix Pushes AI Into Production, UnitedHealth Rebuilds Around AI
```
"Plus: " followed by 2-3 secondary story headlines. Appears in email clients as preview text after the subject.

### Header
- Logo area with publication name
- Date line: "July 17, 2026" or "Month DD, YYYY | Issue #N"
- "Read Online | Unsubscribe" links

### Greeting
```
Good Morning, Agent Owners!
```
"Good Morning, [audience name]!" — consistent, warm, specific to the audience.

### Tagline Sentence
```
Your mom's business now has better automation than most enterprises.
```
One provocative sentence that sets the theme. Often slightly cheeky or surprising.

### Story Format (repeated per story)
```
------------------------------
  Story Headline (linked, bold)

TL;DR: 2-3 sentence summary with key numbers. Ends with Read more → (linked)
------------------------------
```

Key elements:
- Horizontal rule separator (`---` in plain text, `<hr>` in HTML)
- Bold linked headline — clickable, descriptive, 5-12 words
- `TL;DR:` label in bold — signals scannability
- 2-3 sentence summary — includes at least one concrete number
- `Read more →` — linked, consistent closing for every story
- 5-7 stories per issue

### Sponsor CTA Section (bottom)
```
MyClaw is a best-in-class AI agent platform...

Run Best-in-Class AI Agents on MyClaw.ai — In Seconds, Always On 👇
[CTA link/button]
```

Structure:
1. One paragraph: what the sponsor does
2. One paragraph: key value prop / differentiation
3. Bold CTA line with link
4. Optional: "Free trial. Cancel anytime." tag

### "Keep Reading" Section
```
Keep reading
🦞 AI Gets Its Own LLC — Plus: Murati's Open AI Challenger
🦞 AI Reaches 80M Workers — Plus: A Fortune 500 AI Win
🦞 Hermes Hits Unicorn Status — Plus: Nurses Fight AI Cuts
```
Previous 2-3 issues as linked headlines with "Plus: " subtitles.

### Footer
```
MyClaw Newsletter © 2026 – Unsubscribe
```
Simple: brand name, copyright year, unsubscribe link.

## HTML Template Structure

See `templates/newsletter.html` for the full HTML template. Key styling decisions:

- **Width:** 600px centered table (standard email width)
- **Background:** `#f4f4f4` page, `#ffffff` card
- **Header:** Dark navy `#0f2740` with white text
- **Accent color:** Amber `#c96f2e` for links, category labels, CTA buttons
- **Category labels:** Small uppercase amber badges above each story (`AUDIENCE OWNERSHIP`, `GROWTH`, etc.)
- **Story separators:** `1px solid #e8e8e8` between stories, `2px` before CTA
- **CTA section:** Cream background `#faf6f1` with amber left border, centered button
- **Font:** System font stack, 14-17px body, Georgia optional for serif flourishes

### Sponsor Branding
When creating for a specific sponsor:
- Replace header colors with sponsor's brand colors
- Replace CTA section with sponsor's messaging
- Keep the My Claw story format unchanged — this is the content chassis, not the brand

## Workflow

1. **Research stories** — use `web-article-research` skill or Google News RSS to find 5-7 current stories relevant to the newsletter's topic
2. **For each story:** extract headline, source link, 2-3 sentence summary with at least one concrete number
3. **Write sponsor section:** 2 paragraphs + bold CTA line matching the sponsor's voice
4. **Generate HTML version:** use `templates/newsletter.html` as starting point, swap in content
5. **Generate plain text version:** extract from HTML or write separately
6. **Save both to `/tmp/`** — HTML for email sending, text for review

## Pitfalls

- **Don't over-explain the format in the newsletter itself.** The user just sees the content.
- **Every story needs a real source link.** No fake or placeholder URLs.
- **At least one concrete number per story.** Stats, dollar amounts, percentages, dates.
- **The sponsor CTA should feel like a natural section of the newsletter,** not a banner ad. It follows the last story directly.
- **No em dashes.** The user's preference (from Skool/Memory) applies here too.
- **The "Plus: " subtitle matters.** It's what email clients show as preview text. Make those 2-3 stories compelling.
- **Keep stories tight.** 2-3 sentences each. The TL;DR format means what it says.