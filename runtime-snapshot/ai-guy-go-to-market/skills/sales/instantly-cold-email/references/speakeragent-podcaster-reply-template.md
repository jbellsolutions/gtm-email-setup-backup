# SpeakerAgent Podcast Campaign Reply Template

For campaign #3639259 (Podcasters - SpeakerAgent v2). Uses a hardcoded template similar to #3316611 (PR agencies) but adapted for podcasters who are being invited to the SpeakerAgent guest-matching network.

**Campaign context:** Referral angle — "people finding your podcast on speakeragent.ai, we want to send referrals and make sure we represent you accurately." Single email. Sends from operator personas (Orin, etc.) via domains like tamrois.info, valmuc.info.

## Hardcoded Reply Template

Do NOT use DeepSeek for this campaign. Use this template verbatim, only swapping `{lead_name}` and the sender signoff:

```
Hey {lead_name} — thanks for the response.

SpeakerAgent is in beta right now. We're new and doing everything pretty custom to each partner. There's no fees — it's a true partnership program. We're building a network where podcasters get matched with the right guests, and guests find the right shows.

Let's hop on a quick call to see what we can do together. Here's a link to book in: https://cal.com/speakeragent/15min

Or if you'd rather, just give me a couple of times that work for you and I'll give you a call.

{sender_name}
```

## Rules
- No pricing, no fees, no dollar amounts
- No white label mentions
- No made-up features
- Booking link: `https://cal.com/speakeragent/15min`
- Sign off with the sender persona (extract from the original SENT message's quoted sender line)
- The `stats_id` for the reply comes from the SENT message in the lead's message history

## First Use
- **Ademola Odewade** (k-demsconsulting.com, Jul 15, 2026): "I'd be happy to have a brief conversation and learn more about SpeakerAgent and how you qualify and match guests." — Reply sent at ~4:20 PM ET using Orin as signoff.

## Domain-Persona Mapping

These are the `from` addresses and corresponding sender personas for campaign #3639259. When signing replies, extract the persona name from the SENT message's `from` field (e.g. `branson@mirvoes.info` → "Branson"). The `from_name` field on SENT messages is often `null`/empty — always use the email domain to determine persona.

| Domain | Persona |
|---|---|
| `mirvoes.info` | Branson |
| `tamrois.info` | Orin |
| `valmuc.info` | Camila |
| `dalkus.info` | Zayden |
| `ravlui.info` | ⚠️ UNKNOWN — needs mapping (sent to Pamir, hello@onetenhundred.vc, Jul 15) |

**⚠️ If the reply body's quoted text is absent** (no "On ... wrote:" line), fall back to the SENT message's `from` field to determine the persona. Rebecca Fleetwood Hession (Jul 15, 2026) had no quoted sender line in her reply — persona was extracted from `"from": "branson@mirvoes.info"` on the SENT message.

## Recent Monitoring Activity

**July 15, 2026 — First-day sending, 10 real replies across inbox pages 0-1:**

Key findings:
- **Daemon IS replying to podcaster leads despite lacking CAMPAIGN_CONTEXT.** Isabel (isabel@tumcoeur.com) replied "I would love to chat with you, do you have a calendar link" at 22:11 UTC and got the hardcoded template reply within 22 minutes. Reply quality: "SpeakerAgent is in beta right now. We're new and doing everything pretty custom..." — decent, no pricing violations.
- **Ademola Odewade** (k-demsconsulting.com): "I'd be happy to have a brief conversation and learn more about SpeakerAgent" — reply sent using Orin signoff.
- **Sean (sean@newsales.expert)**: "Which of my podcasts are you referring to?" — handled by daemon.
- **Classified as OOO (not actionable)**: Chris (entrepreneursforimpact.com — travelling), Trinity (trinitynewlife.com — out of country), Nick/AmazingWave (vacation).
- **Classified as auto-responder**: Startupradio (ticket system), NewStack (automated response), Rebecca (Mon/Fri response schedule).
- **Negative/blacklist**: Michael Krigsman (cxotalk.com) — "We publicly blacklist agencies that use AI to send us guests" — do NOT re-engage.
- **New domain-persona mapping needed**: `dalkus.info` → Zayden (Isabel's sender). Not yet in the domain-persona table above. Add if new replies from this domain appear.

**Verdict:** Daemon is functional for podcaster campaign even without explicit CAMPAIGN_CONTEXT. Reply template is being used correctly. No unhandled positives found. Monitor for new `from` domains and add to domain-persona table as they appear.

**July 16, 2026 — Day 2 monitoring, 1 new positive across pages 0-1:**

Key findings:
- **Steve** (steve@ecommercefastlane.com, eCommerceFastlane Podcast): Replied 8:11 PM ET — "Hi Zayden 👋 Thanks for your email today! We have many opportunities to connect with entrepreneurs, founders, and marketers in ecommerce and retail. 1. Be a guest on the eCommerceFastlane Podcast... 2. Sponsor the podcast... 3. Sponsor the Fastlane Insider newsletter... 470+ podcast episodes with 3M+ downloads... published in 45 languages." — **Reciprocal-pitch archetype.** Steve is pitching his own sponsorship/guest opportunities rather than just saying "yes, interested." Reply sent using standard SpeakerAgent template via Zayden (tamrois.info). Stats: 470 episodes, 3M+ downloads, 45-language distribution — substantial show. Flag to operator: follow-up may need a different angle than pure guest-matching.
- **Peter** (peter@bizexitgrow.com): "Open to receiving guests! Any business owner with an exit, or anyone with an M&A background would be a fit." — Branson handled within 2.5 hours. Now in daemon state.
- **Isabel** (isabel@tumcoeur.com): Booked Jul 29 after receiving calendar link. Follow-up reply confirmed scheduling.
- **Sean** (sean@newsales.expert): Tony D sent follow-up — already handled within 24h.
- New campaigns #3652623/#3652624 launched same day — first-day auto-responder wave, zero genuine positives yet (normal).

**Reciprocal-pitch archetype (new):** Some podcasters reply by pitching their OWN show's guest/sponsorship slots rather than expressing interest in SpeakerAgent's guest-matching. The standard template still works ("SpeakerAgent is in beta...") but these leads need operator awareness — they may be more interested in promoting their show than receiving guests. When a podcaster lists sponsorship tiers, episode counts, and download stats, flag to operator as potential partner, not just guest-match candidate.

**July 17, 2026 — Day 3, 4 replies across pages 0-2, 1 new archetype discovered:**

Key findings:
- **Drew McLellan** (drew@agencymanagementinstitute.com, Agency Management Institute): First reply at 4:21 PM ET — "Hopefully the attached will help." — sent media kit (warm positive, attachment-sharing pattern). Our reply at 4:41 PM ET with standard SpeakerAgent template via Zayden. **Second reply at 4:42 PM ET — "Agency owners are not typically my guests. It's people who serve agency owners."** — This is a NEW archetype: **targeting correction.** The podcaster is engaged, sent their materials, saw our reply, and is now refining the targeting. This is NOT hostile, NOT negative — it's a deeply engaged lead correcting our understanding of their audience. Reply sent at 6:36 PM ET via Zayden: acknowledged the correction, reframed to "people who serve agency owners — consultants, coaches, software vendors, training platforms," kept the SpeakerAgent template. **This is a better-qualified lead AFTER the correction than before — they told us exactly who they want.**

**Targeting-correction archetype (new — Jul 17):** An engaged podcaster who has already sent materials and gotten a standard reply, then replies again to refine who their actual guests are. The reply must: (1) thank them for the clarification, (2) explicitly acknowledge the corrected audience, (3) show why it's actually better for our network, (4) keep the SpeakerAgent template spirit. Do NOT treat this as a negative or neutral — the lead is MORE engaged after the correction, not less. They've invested time in making sure we get it right.

**July 20, 2026 — Day 5 monitoring, 1 new positive on page 0:**

Key findings:
- **Jeffrey Bradbury** (info@teachercast.net, TeacherCast Educational Network): Replied 9:31 AM ET — "Hi Zayden, Thank you for the update. Can you share links to my show so I can check for accuracy?" — **Verification-request archetype.** Jeffrey is a real podcast host (470+ episodes) using info@ as his primary inbox. He received the SpeakerAgent cold email 5 days prior and is now engaging — he wants to verify his show's listing before committing. Reply sent within 90 min via Zayden (dalkus.info) using an adapted SpeakerAgent template that acknowledged the verification request specifically ("Happy to pull up your listing and walk you through it on a quick call") while keeping the core template message. **⚠️ The standard "positive_interested" classifier patterns missed this reply** — "share links" and "check for accuracy" don't match "send more info" or "interested" patterns. The reply was correctly handled manually by the monitoring cron after classification as `neutral`.

**Verification-request archetype (new — Jul 20):** A podcaster who received the SpeakerAgent cold email but is asking to SEE their listing before engaging further. Key signals: "share links to my show," "check for accuracy," "verify my listing," "see how I'm represented." These are NOT negative — they're methodical hosts doing due diligence. The reply must: (1) acknowledge the verification request specifically, (2) offer to walk through the listing on a call (don't just send a bare link — use the call as the vehicle), (3) keep the "no fees, partnership program" message. The standard template works with a one-line customization in the second paragraph.

**⚠️ Podcaster `info@` addresses are frequently real humans — do NOT auto-filter.** Unlike the owned-audiences campaigns where `info@` = ticket system 95% of the time, podcaster campaigns have a much higher rate of real humans at `info@` addresses. TeacherCast (Jeffrey), Deconstructor of Fun, and Startup Radio all use info@ as their primary inbox. If the reply body is substantive and relevant (not boilerplate), pull message history and classify normally — do NOT skip as auto-responder based on prefix alone. This is the same exception as small businesses in owned-audiences but at a higher frequency for podcasters.