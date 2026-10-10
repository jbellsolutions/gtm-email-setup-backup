# Cross-Campaign Monitoring Sweep — July 15, 2026

## Summary

Ran pages 0-1 (40 inbox entries) across all campaigns at ~11 PM ET. Three active/recent campaigns represented:
- #3617053 (Coaching Owned Audiences, PAUSED): 19 entries — auto-responder tail from 9,457-lead blast
- #3639259 (Podcasters SpeakerAgent v2, ACTIVE): 17 entries — first-day replies, daemon handling within minutes
- #3577260 (PR Agencies v2, COMPLETED): 4 entries — closing messages from previously unhandled leads

**Result: ZERO genuinely unhandled positive replies requiring action.** [SILENT] run.

## Campaign-by-Campaign Breakdown

### #3617053 — Coaching Owned Audiences (PAUSED, auto-responder tail)
19 entries total. 15 auto-responders (support@, info@, compliance@, privacy@, care@, hello@). 4 real leads:

| Lead | Reply | Classification | Status |
|---|---|---|---|
| Ann (ann@annkonkolycnm.com) | "Thank you for your email. All emails will be addressed within 72 business hours." | auto_responder | In state, skip |
| Gina (gina@beyondthescoreboards.com) | "Looking forward to it too!" | positive_interested | Already booked (Jul 21), skip |
| Shira (shira@shiraraymond.com) | "I'm going to pass at this time. Thank you for thinking of me." | negative_notfit | Polite decline, already handled |
| Kareem (kareem@kareemelsayed.com) | "Where were you three years ago!?!" | positive_interested | Already handled (case study sent) |

### #3639259 — Podcasters SpeakerAgent v2 (ACTIVE since Jul 15 morning)
17 entries total. 7 auto-reply prefixes (hello@, info@, team@, podcast@). 10 real leads:

| Lead | Reply | Classification | Actual | Status |
|---|---|---|---|---|
| Isabel (isabel@tumcoeur.com) | "Thank you for your email. I would love to chat with you, do you have a calendar link..." | auto_responder (misclassified) | **Positive — human reply** | Handled by daemon in 22 min |
| Michael (mkrigsman@cxotalk.com) | "We publicly blacklist agencies that use AI to send us guests..." | neutral (misclassified) | **negative_notfit** | In state, no re-engage |
| Ademola (ademola.odewade@...) | "Thank you for reaching out... I really appreciate..." | positive_interested | Positive | Already handled |
| Rebecca (rebecca@wethrive.live) | "I typically respond to emails on Monday and Friday" | auto_responder | OOO/auto-responder | Already handled |
| Chris (chris@entrepreneursforimpact.com) | "I'm travelling with limited bandwidth. Happy summer!" | positive_interested (misclassified) | **OOO/travel** | No action |
| Startupradio (partnerships@startuprad.io) | "Your message has been received and entered into our review system" | positive_interested (misclassified) | **Ticket-system auto-responder** | No action |
| Trinity (clayton@trinitynewlife.com) | "I'm out of the country with limited access to email" | positive_interested (misclassified) | **OOO** | No action |
| Sean (sean@newsales.expert) | "Which of my podcasts are you referring to?" | positive_interested | Positive — genuine question | Already handled |
| Nick / AmazingWave (jo@amazingwave.digital) | "I currently taking a very well deserved break (trust me)!" | auto_responder | Vacation OOO | Skip |
| NewStack (podcasts@thenewstack.io) | "The following is an automated response" | positive_interested (misclassified) | **Auto-responder** | No action |

**Misclassification rate on podcaster replies: 5/10 (50%).** The classifier was built for owned-audiences coaching/wellness replies and systematically misreads podcast/media reply patterns.

### #3577260 — PR Agencies v2 (COMPLETED)
4 entries total. 1 auto-responder (info@). 3 real:

| Lead | Reply | Classification | Status |
|---|---|---|---|
| Scott Kaier (scott@formidable-media.com) | "I still don't understand exactly what it is that you do" | neutral | `our_replies_after=1`, someone replied. Previously unhandled for 8 days. Now closing. |
| Sam Frontera (sfrontera@exclusivepr.biz) | "All good! Best, Sam" | neutral | `our_replies_after=0`. Previously unhandled for 13 days. Closing message — too late. |
| Mike Billoni (mike@billoni.com) | "Hi Mike, I wanted to follow up..." | positive_interested (FALSE) | **NOT a lead reply** — operator Tony's follow-up forwarded through thread. Mike's actual reply "Yes. Call me at..." was Jul 9, already handled. |

## Key Findings

1. **Daemon IS handling podcaster replies despite lacking CAMPAIGN_CONTEXT.** Isabel got a reply in 22 minutes: "SpeakerAgent is in beta right now. We're new and doing everything pretty custom to each partner. There's no fees — it's a true partnership program." Quality was decent — mentioned beta, no pricing, Cal.com link. Not perfect but functional.

2. **Classifier needs podcaster-specific patterns.** 50% misclassification rate on podcaster replies. "Thank you for your email" + "I would love to chat" = human positive (not auto-responder). "Out of the country" / "travelling with limited bandwidth" = OOO (not positive). Ticket-system acknowledgements = auto-responder.

3. **FORWARD type messages appear as REPLY in message history.** When an operator replies in a forwarded thread, Instantly labels the operator's outbound as `type: REPLY`. The monitoring pipeline must check `from` domain before classifying.

4. **Auto-responder flood on #3617053 is tapering.** Day 2 of auto-responder tail from the 9,457-lead blast. 15 of 19 entries were auto-reply prefixes. Expected to continue through ~Jul 17.

5. **Zero unhandled positives across all campaigns.** The monitoring system is catching everything. The daemon handles #3639259 within minutes. #3617053 auto-responders are correctly skipped. The remaining #3577260 leads (Scott, Sam) have aged out — closing messages, too late for meaningful re-engagement.
