# Campaign 3617053 — Coaching Owned Audiences (July 2026)

Launched July 9, 2026. Active and sending.

## Strategy

**Referral-based cold email** — "people who already have your clients' trust" angle. Positions AI Integraterz as building partner maps and referral networks, not AI automation. Different from the standard $10/hr AI operator offer used in other campaigns.

## Sender Personas

Sends from operator personas: Anna, Brielle, Willow, Lucy, Mila, Madeline, Brooklyn, Julia, Emilia, Bella, Violet. Each uses a domain from the operator pool (elevatedeskin.info, growthmapar.info, successcrestco.info, etc.).

## Reply Routing

**This is the OWNED AUDIENCES campaign.** Positive replies route through the `owned-audiences-email-reply` skill:
- Match lead vertical to case study library
- Draft short reply with case study link + booking link
- Booking: https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery
- Site: https://aiintegraterz.com/stop-renting
- Do NOT use the standard AI operator $10/hr offer or SpeakerAgent Calendly

## Positive Replies (as of July 13)

| Date | Lead | Company | Reply | Status |
|---|---|---|---|---|
| Jul 13 | Dawn King-Dushane | Renew Wellness (TX) | "Sure. Send me more info, please." | Drafted — hormone case study |
| Jul 13 | Team TRU Wellness | TRU Wellness Charlotte (NC) | "sure, lets see what you come up with?" | Drafted — hormone case study |
| Jul 13 | Lori Carpenos | 3 Principles Therapy | "Referrals are definitely key. Always have been." | Borderline — engaged, no explicit ask |
| Jul 9 | (2 positives) | — | — | First 24h after launch |

## Daemon

⚠️ NOT in auto_reply_daemon.py CAMPAIGN_CONTEXT dict. This is intentional — replies route through the owned-audiences workflow, not the standard daemon. The daemon should NOT auto-draft for this campaign.

## Monitoring

State file: `/opt/data/scripts/owned_audiences_reply_state.json`
Format: `{"last_run": "ISO timestamp", "processed_message_ids": ["<msgid@domain>", ...]}`

Run the `owned-audiences-email-reply` skill for all positive replies on this campaign. The skill handles all drafting — this reference file is for campaign context only.