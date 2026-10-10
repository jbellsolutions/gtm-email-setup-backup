# Local Business Partner & Influencer Lead Generation

Playbook for building large referral-partner graphs for brick-and-mortar service businesses. First executed for Gameday Men's Health (Owings Mills, MD), July 2026.

## Deliverable Structure

Three deliverable documents per client:

1. **Power Partners (01-power-partners.md)** — 100 partner categories across 3 degrees of separation with named local businesses to approach
2. **Local Influencers (02-local-influencers.md)** — Tiered creator list with handles, follower counts, and outreach plays
3. **Deliverable Package (PDF)** — Client-facing summary

## The 3-Degree Referral Graph

Map every business that touches the target customer's life:

| Degree | Scope | Categories | Example |
|--------|-------|-----------|---------|
| 1 — Same customer | Different service, adjacent to health/appearance | 20 cats | Gyms, PT, chiropractors, dentists, med spas, country clubs, custom clothiers, barbers |
| 2 — His lifestyle | Where he spends discretionary time & money | 30 cats | Cigar lounges, steakhouses, auto detailers, gun ranges, wealth managers, breweries |
| 3 — His household/affiliations | Reaches through spouse, employer, clubs | 50 cats | Chambers, Rotary, American Legion, BNI, youth sports, faith groups, unions |

## ICP Fit Test (for every lead)

Three questions, all must be "yes" for Tier 1 pursuit:

1. Is the audience **local** to the service area? (Baltimore County for this client)
2. Does it skew **male 30-65**?
3. Does the partner already talk about **health/fitness/performance** (so the mention isn't a swerve)?

Three yes = pursue. Two = awareness only. One = pass.

## Outreach Protocol

**Rule 1 — Help first.** Never open with "will you refer to us." Lead with what the client can do for THEM (free talk, co-branded offer, patient referrals).

**Rule 2 — Score before pitch.** Rate each target on Overlap (1-5), Volume (1-5), Reachability (1-5). Work highest total score first.

**Rule 3 — Reciprocal referral card/code.** Their clients get a first-visit perk; the client's patients get a perk at the partner business.

**Rule 4 — One partner, one owner.** Assign each active partner to one person on the client's team.

**Rule 36 — Original source is everything.** Tag every new patient with which partner referred them.

## Influencer Tier Structure

| Tier | Purpose | Play | Examples |
|------|---------|------|----------|
| Tier 1 — Best fit | Content collab + affiliate | Community perk, "what my labs said" episode | Dr. Baltimore, Crazy 88 MMA |
| Tier 2 — Awareness reach | Brand awareness at scale | Sponsored "day in the life" collab | EatMoreBeMore, The Baltimore Foodie |
| Tier 3 — Micro creators | Chair-side referral engine | Cross-promo cards + code | Barbers with 1K-12K followers |
| Tier 4 — Athlete halo | Aspirational, high recognition | Event appearance, podcast crossover | Ryan Ripken, Torrey Smith |

## Data Extraction

### Primary: Browser-Based Google Maps Scraping

The ONLY working approach (July 2026). Pattern:

```
browser_navigate → https://www.google.com/maps/search/<category>+<city>+<state>
                → browser_snapshot
                → parse article→link→StaticText pattern
                → click into detail view for phone + website
```

Yields: name, rating, category, address, hours (sidebar). Phone + website (detail view).

### Directory Sources (for Degree 3 organizations)

- Chamber of Commerce member directories (northwestchambermd.com, greaterbaltimorechamber.com)
- Rotary Club finder (rotary.org/en/search/club-finder)
- American Legion post finder (legion.org/posts)
- BNI chapter directories
- Specific org websites (libertypost122.org, pikesvillerotarymd.org)

### Influencer Discovery

- DuckDuckGo/Google: "[city] fitness influencers Instagram [year]"
- Feedspot top-N lists (e.g., feedspot.com/baltimore_fitness_instagram_influencers/)
- Instagram handle verification
- Competitor following lists

## Scaling Targets

| Campaign size | Categories | Cities | Results/search | Total leads | Method |
|--------------|-----------|--------|----------------|-------------|--------|
| Local (1 clinic) | 100 | 3-5 | 5 | 1,500-2,500 | Sequential browser |
| Regional (3-5 clinics) | 100 | 8-12 | 5 | 4,000-6,000 | Browser Use Cloud parallel |
| National franchise | 100 | 50+ | 5 | 25,000+ | Apify (with valid token) |

## Session Notes (Gameday Owings Mills, July 2026)

- Client: Gameday Men's Health, Owings Mills
- Territory: Baltimore County (Owings Mills, Reisterstown, Pikesville, Timonium, Towson, Hunt Valley)
- ICP: Men 30-65, cash-pay, vitality-minded
- Priority anchors: Caves Valley Golf Club, Rehab 2 Perform, Davidus Cigars, Crazy 88 MMA, ISI Elite Training, Woodholme CC, The Suburban Club, Northwest Chamber
- Top influencer: Justin Inman "Dr. Baltimore" (IG @dr.baltimore, ~101K)
- Deliverables saved to: `/opt/data/hermes/leads/power-partners.csv` (107 leads), `/opt/data/hermes/leads/local-influencers.csv` (13 influencers)
- Scraping plan: `/opt/data/hermes/plans/gameday-owings-mills-lead-gen.md`
