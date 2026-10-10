---
name: cold-email-weekly-rhythm
description: "Monday/Wednesday/Friday operational playbook for cold email. Monday = deliverability audit, Wednesday = reply scoring sweep, Friday = campaign retrospectives. Biweekly inbox rotation, monthly spam tests, quarterly reviews. Use this as the ongoing cadence once campaigns are live."
version: 1.0.0
source: Adapted from GrowthEngineX coldoutboundskills
---

# Cold Email Weekly Rhythm

## Monday — Deliverability Audit (15 min)

Pull campaign stats for the last 7 days using Instantly CLI (analytics endpoints return 0 when tracking is off, but they capture reply/bounce counts). **Always pull stats for ALL campaigns** — don't hardcode IDs. Stopped campaigns return no analytics data, but the call won't error; it just omits them from the response.

```bash
Instantly analytics campaign-stats --from YYYY-MM-DD --to YYYY-MM-DD --campaign-ids <all_active_ids> --format json
Instantly analytics overall --from YYYY-MM-DD --to YYYY-MM-DD --format json
```

**Campaign status (as of June 15, 2026):** HVAC - Texas (#3442703) is the only ACTIVE campaign. HVAC - Florida v2 (#3442743), NC (#3442704), SC (#3442705), TN (#3442706), and 5 regional campaigns are DRAFTED. All pre-June campaigns are STOPPED. **Always pull `Instantly inbox replies` for ALL campaigns** — stopped campaigns still receive residual replies.

Check against the **1% rule**: after 200+ sends in 7 days, overall reply rate must be ≥1%. (200-send threshold per `email-deliverability-audit` skill.)

**If ≤1%:** load `email-deliverability-audit` skill and triage.
**If clean:** log to Obsidian vault daily-logs: `cold-email-health-YYYY-MM-DD.md`.

## Wednesday — Positive Reply Sweep (15 min)

**SpeakerAgent campaign #3577260 is automated — skip manual sweep for it.** The pipeline (cron `148920b114d6`, script `/opt/data/scripts/speakeragent_pipeline.py`) runs every 30 minutes, detecting, classifying, and generating DRAFTS for approval. It does NOT auto-send — Justin approves each draft before it goes out. Check the dashboard for pending approvals: `python3 /opt/data/scripts/speakeragent_dashboard.py`. Focus Wednesday time on non-SpeakerAgent campaigns (HVAC TX #3442703 + any active regionals).

For non-automated campaigns, follow the manual sweep process below.

### Manual Sweep (non-SpeakerAgent campaigns)

1. Pull ALL inbox replies via Instantly CLI. Use `Instantly inbox replies --format json`, post-filter by `last_reply_time` for the 7-day window.
2. Classify using inline rules from `positive-reply-scoring/references/campaign-slack-push.md` (NOT `scripts/classify.py` — ~30% error rate).
3. Cross-reference against pipeline state (`/tmp/speakeragent_followups.json`) for SpeakerAgent replies, or daemon state (`/opt/data/scripts/auto_reply_state.json`) for other campaigns. **SpeakerAgent #3577260 is handled by the pipeline (cron 148920b114d6) — skip manual classification for it.**
4. **Spot-check classifier accuracy.** As of July 8, 2026, the classifier maintains a **31% error rate** (12/39 false positives in the July 8 sweep, same as 4/13 in June 24). This is a maintenance-class problem — exhaustive pattern lists will always miss edge cases. **Always apply manual corrections** before reporting. Quick audit checklist for every sweep:
   - Every `positive_referral` → scan for OOO/auto-reply language ("away from email", "taking time off", "I will reply...")
   - Every `positive_interested` → scan for OOO signals ("back in office", "away from")
   - Every `unsubscribe` → scan for hostile language ("psycho", "fuck", personal insults)
   - Every `neutral_question` on short bodies → check for "no interested" typo
   - Check `our_replies_after` for EVERY positive — daemon state ≠ reply sent

| Label | Meaning | Positive? |
|---|---|---|
| positive_interested | "Yes, tell me more" / booked meeting | ✅ |
| positive_soft | "Send info" / "reach out in Q3" | ✅ |
| positive_referral | "Not me, but talk to X" | ✅ |
| negative_notnow | "Not right now" | ❌ |
| negative_notfit | "Not a fit" | ❌ |
| negative_hostile | Angry, complaint, report | ❌ (risk signal) |
| unsubscribe | Opt-out | ❌ |
| ooo | Out-of-office | ❌ (exclude from math) |
| bounce | Technical bounce | ❌ (exclude from math) |

**Positive reply rate** = (interested + soft + referral) / total_sent

**Critical:** Respond to every positive_interested reply within 30 seconds of seeing it. A fast reply converts 3× better.

## Friday — Campaign Retrospectives (20 min/campaign)

For campaigns hitting 21-day mark:
1. Pull analytics via MCP
2. Compare positive reply rate against baseline
3. Decision:
   - **Winner (≥2× baseline):** keep running, consider scaling
   - **Middling:** iterate — run experiment-design to plan next variant
   - **Loser (<50% baseline):** kill it, log why
4. Log outcome to Obsidian: `campaigns/<name>-retrospective-YYYY-MM-DD.md`

## Biweekly (Every Other Monday) — Inbox Rotation (30 min)

1. Pull all email accounts via Instantly MCP
2. Check: any accounts with blocked warmup? Reputation "bad"?
3. Retire failures, promote insurance inboxes to active
4. If insurance pool <5 inboxes: trigger new domain purchase cycle

## Monthly (1st) — Spam Placement Test

Run spam placement test via Instantly Smart Delivery. Target ≥85% inbox placement.

## Quarterly — Experiment Review (90 min)

Review all experiment logs from the quarter. Output to Obsidian:
- Top 3 campaigns + what worked
- Bottom 3 + what to avoid
- 3-5 hypotheses for next quarter
- Adjusted ICP if data suggests different segment

## What to Skip
- Don't check Instantly every day (Wednesday sweep catches everything)
- Don't obsess over daily fluctuations (wait for 7-day averages)
- Daily pokes are procrastination, not performance
## Pitfalls (Refreshed July 2026)

- **User/cron may request sweep on campaign IDs that don't exist (July 22, 2026).** Campaign IDs 3249954 and 3249956 were specified in a cron task but aren't in `Instantly campaigns list`. These mapped to legacy recruiters campaigns (power-partner-A, direct-value-A) that were never created — their DRAFT siblings (3249955, 3249957) exist but the A-variants don't. When asked about specific campaign IDs, verify existence with `Instantly campaigns list --format json` before spending time on them. Report the gap, then sweep the campaigns that ARE active in the inbox instead.
- **SpeakerAgent #3577260 (July 14, 2026):** Pipeline generates DRAFTS only — NO auto-send. Cron `148920b114d6` runs `speakeragent_pipeline.py` every 30 min. Positives get a `draft_status: "pending_approval"` entry in state. Justin must approve before any reply is sent. Template is now platform-perspective (not Mila persona): referrals/directory/Tony's calendar. Full template at `/opt/data/scripts/speakeragent_template.txt`. Review pending drafts via `python3 /opt/data/scripts/speakeragent_dashboard.py`. Old cron `06848dd70c52` is paused.
- **For non-SpeakerAgent campaigns:** `scripts/classify.py` has ~30% error rate. Use inline rules from `positive-reply-scoring/references/campaign-slack-push.md` instead. Always spot-check classifier output.
- **Daemon `replied_message_ids` does NOT mean the daemon replied.** For non-SpeakerAgent campaigns, always check `our_replies_after`. For SpeakerAgent, the pipeline handles this.
- **`Instantly analytics campaign-stats` silently drops campaigns with no activity.**
- **Never hardcode campaign IDs in cron jobs.**

## What to Do Next
This IS the loop. Next action = next calendar event.
