# July 13, 2026 Monitoring Run — Key Findings

8:30 PM ET monitoring run. Full sweep: pages 0-1 (40 inbox entries), 19 from #3617053, 3 from #3577260.

## Auto-Reply Filter Effectiveness

**Email-prefix heuristic saved 9/19 page-0 API calls (47%).** Entries matching `support@`, `info@`, `contact@`, `privacy@`, `hello@` were auto-replies (ZenDesk tickets, privacy confirmations, ticket systems). These are NEVER human replies — classify as `auto_reply` and add to state silently.

| Email | Type |
|---|---|
| info@everwellusa.com | auto-reply |
| contact@newportmd.com | auto-reply |
| support@risingstarswellness.com | auto-reply |
| support@gamedaymenshealth.com | auto-reply |
| privacy@simplepractice.com | auto-reply |
| support@wellsync.com | auto-reply |
| contact@truwellnesscharlotte.com | auto-reply |
| hello@getopt.com | auto-reply |
| support@stallion.com | auto-reply |
| support@welmhealth.com | auto-reply |
| info@telewellnessmd.com | auto-reply |
| support@myadvice.com | auto-reply |
| support@honehealth.com | auto-reply |
| info@strivepharmacy.com | auto-reply |

## Batch Case-Study Sends

Prior cron run at ~5:12 PM ET sent case-study replies to all 12 leads that had replied today. The batch used the Willow persona template (standard case-study reply). **Finding: the 5:12 PM cron caught everything — the 8:30 PM run had zero unhandled owned-audiences replies.**

Batch sent to: Ppavey, Meghan, Mike H, Lori C, Jared, Drd, Kylie, and others. Lori C also received a custom plan (present-valley-mc2j.here.now) at 3:27 PM ET in addition to the case study template.

## Hostile Second Reply — Robyn (mindfulnessathletics.com)

**Pattern confirmed:** Second reply after case study follow-up = hostile.

Timeline:
- July 10: Cold email from Penelope → Robyn replies positively ("Yes please send it over")
- July 10: Penelope sends custom plan (marine-crest-26w6.here.now) + booking link
- July 13 7:40 PM: Penelope sends "circling back" follow-up with case study + new custom plan
- July 13 8:11 PM: Robyn replies "I'm not interested thanks, the AI plan is super generic. Please remove me from your mailing list."

Added to hostile_senders + state file. This is the exact pattern from the skill's pitfall: "Second replies after case study follow-ups are almost always hostile."

## PR Campaign — Tony Berlin (berlinmediarelations.com) ⚠️ STALE

- Replied July 13 6:23 PM ET: "Thank you - do you charge a fee for referrals?"
- Message ID: `<SJ0PR12MB6760D406888DF1C2396B9001B6FA2@SJ0PR12MB6760.namprd12.prod.outlook.com>` — in `replied_message_ids` (scanned by daemon)
- **our_replies_after = 0** — no SENT reply exists in message history
- Campaign #3577260 (PR Agencies — SpeakerAgent v2), human-operated
- **Needs human operator reply** via Instantly web UI with SpeakerAgent template (Calendly → Tony, no pricing in email)

## Prior Cron Run Effectiveness

The 5:12 PM ET batch case-study sends handled 100% of today's replies. The 30-minute monitoring cadence is redundant during active sending windows — the batch cron catches everything. Consider reducing to hourly outside sending windows.

## State File

Updated: `replied_message_ids` now 352 (+1 Robyn hostile), `hostile_senders` now 28 (+1 Robyn).