# Coaching Owned Audiences Campaign (#3617053)

Discovered: July 10, 2026 | Created: July 9, 2026 | Status: ACTIVE

## Campaign Details

- **Name:** Coaching Owned Audiences 
- **Instantly ID:** 3617053
- **Offer:** Joint-venture partnership setup — "partners each putting your work in front of their own audience. The therapist mentions it. The podcast has you on. The newsletter runs a note. Same launch, several rooms at once, none of them paid placements."
- **Target:** Coaches (health, life, business, nutrition, wellness) with existing audiences
- **Compliance:** `send_as_plain_text: true`, `DONT_TRACK_EMAIL_OPEN` + `DONT_TRACK_LINK_CLICK`, `max_leads_per_day: 1000`

## Sender Personas

All from info domains (operator email infrastructure):

| Persona | Email | Domain |
|---|---|---|
| Arianna | arianna@strategypointil.info | strategypointil.info |
| Anna Turner | anna@elevatedeskin.info | elevatedeskin.info |
| Grace | grace@growthpathut.info | growthpathut.info |
| Penelope Sanchez | penelope@scaledeskct.info | scaledeskct.info |
| Kaylee Long | kaylee@elevateaxisca.info | elevateaxisca.info |

## Original Email Copy (sample)

Variant A (to Robyn, from Penelope):
> Hello Robyn,
> 
> Most coaches fill programs alone — their list, their posts, their effort. Every single time.
> 
> The stronger play: partners each putting your work in front of their own audience. The therapist mentions it. The podcast has you on. The newsletter runs a note. Same launch, several rooms at once, none of them paid placements.
> 
> Want me to send a short version of a partner-backed plan, plus a case study?

Variant B (to Wendy, from Anna):
> Hey Wendy,
> 
> Been following your work with men — respect what you're building.
> 
> Here's a thought. Your clients are already gathered in rooms you don't own — therapists' offices, gyms, other practitioners' books, communities. Those people have your clients' trust, and most of them have no coach to send people to.
> 
> I set those partnerships up — introductions, not ads.
> 
> Want me to send over a short version of what this would look like for your practice, plus a case study of how we did it for another coach?

## First-Day Results (July 10, 2026)

13 inbox replies within first 24 hours of sending:

**Positives (2):**
- **Wendy** (wendy@thesensiblewoman.com) — "Hello Anna, I work mostly with women. Send iver your information and let me take a look." → needs info + case study
- **Robyn Kenney** (robyn@mindfulnessathletics.com) — "Hi Penelope, Yes please send it over for me to look at." → needs info + case study

**Negative/Quality (1):**
- **Julianne Kanzaki** (julianne@juliannekanzaki.com) — "This was clearly written by AI, which is an instant 'no thank you'." → copy quality flag

**Anti-spam challenge-response (2):**
- Joanne Cipressi (joanne@joannecipressi.com) — BoxTrapper
- Perry (perry@purposedrivenmastery.com) — BoxTrapper

**OOO/Auto (7):**
- Lara Birk (vacation til July 20), Ashley (Fridays off), Jillie Johnston (til July 12), Cindy Schmidt (til July 13), Michelle Baker (career pause — "returning in a few years"), Monique (dead email — "will soon be deleted"), Siobhan Gallagher (til July 13), Dan Neitz (vacation til July 13)

**Maternity leave (1):**
- Sarah (livewellenhanceyou.com) — returning Aug 2

## Anti-Spam Challenge-Response Rate

**10% (2/20 inbox entries on July 10).** Both from shared hosting (HostGator). BoxTrapper/cPanel challenge-response. These are NOT deliverability failures — email got through, just required human verification. Treat as `anti_spam_challenge`, add to state silently, do not notify operator.

## Men's Health Provider Batch (July 13, 2026)

8,255 men's health provider leads added to this campaign alongside the original 1,202 coaching leads (9,457 total). These use a different set of 10 cold email frameworks adapted for men's health (TRT, hormone, peptide clinics). Details at `references/mens-health-frameworks-owned-audience-v1.md`.

Men's health leads use `first_name: "Team"` for role accounts (info@, support@, etc.) and extracted-name for named accounts. `company_name` derived from email domain. All 4-sequence copy baked into `custom_fields` identically to the coaching leads — same merge tag structure, different copy.

## CAMPAIGN_CONTEXT Gap

⚠️ NOT in daemon's `CAMPAIGN_CONTEXT` dict. Any positive replies processed by the auto-reply daemon will get mismatched drafts using the generic fallback. Add to daemon before replies accumulate.

```python
CAMPAIGN_CONTEXT = {
    # ... existing ...
    3617053: {
        "name": "Coaching Owned Audiences",
        "offer": "JV partnership setup for coaches — partner-backed launches, introductions not ads",
        "persona_senders": ["Arianna", "Anna", "Grace", "Penelope", "Kaylee"],
        "template": "hardcoded"  # Use template, not DeepSeek
    }
}
```

**See also:** `references/bulk-lead-upload-pitfalls.md` (MCP vs CLI, last_name validation, Cloudflare), `references/mens-health-frameworks-owned-audience-v1.md` (10 frameworks for men's health providers used in the July 13, 2026 batch of 8,255 leads).

## Reply Template

When a coach replies positively, use this template pattern (modeled on what worked for Wendy/Robyn):

> Hey [name] — [acknowledge their specific interest]. Want me to send the breakdown here or is there a better email? Quick call works too if you prefer. Either way, no pressure.

Keep it short, casual, no pitch. The offer sells itself — they already said yes to seeing more info. Don't re-sell.
