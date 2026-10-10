# Campaign 3617053 — Coaching Owned Audiences (July 2026)

**Status:** ACTIVE (sending)  
**Leads:** 1,215  
**Instantly ID:** 3617053  
**Discovered:** July 9, 2026

## Strategy

"Partner-backed plan" cold email offering coaches/consultants a free 5-page personalized plan + case study. Sends from multiple personas (Bella, Penelope, Anna, Willow, etc.).

## Reply Workflow

Uses `owned-audiences-email-reply` skill — NOT the daemon. When a lead replies with interest ("yes send it over", "tell me more"), the cron monitor builds a 5-page PDF plan, hosts it via here.now, and drafts a reply email. The human operator sends from their own address.

## State File

`/tmp/owned_audiences_state.json` — tracks processed lead_ids and positive reply status per campaign.

## Positive Replies (as of July 11, 2026)

| Lead | Email | Reply | Status |
|---|---|---|---|
| Kareem El Sayed | kareem@kareemelsayed.com | "Sure" | ✅ Plan built |
| Jared Callahan | jaredc@monalihealth.com | "Yes, I would be interested. Send it over - Thanks!" | ✅ Plan built |
| Wendy Carder | wendy@thesensiblewoman.com | "I work mostly with women. Send over your information" | ✅ Plan built |
| Robyn Kenney | robyn@mindfulnessathletics.com | "Yes please send it over for me to look at." | ✅ Plan built |

Plans at `/tmp/{Name} — Partner-Backed Plan.pdf`.

## Classification Results (July 10-11 spot-check)

17 leads processed as non-positive — 6 spot-checked, all confirmed correct:
- Anti-spam challenge-response (Joanne)
- AI-detected rejection (Julianne)
- Maternity leave OOO (Sarah)
- Dead email (Monique)
- Unsubscribe (Nicholle)
- OOO (Ashley)

No false negatives found.

## Daemon Status

⚠️ NOT in daemon CAMPAIGN_CONTEXT — but replies are handled by owned-audiences workflow, not the daemon. This is by design.
