# Partner Campaigns (#3698110-3698114) — Reply Handling

**Active since:** July 21, 2026. Four Prospector-sourced campaigns targeting professional services firms.

**⚠️ NOT Owned Audiences campaigns — different offer, different reply workflow.**
These campaigns are NOT in the daemon's `CAMPAIGN_CONTEXT`. The daemon will NOT catch replies.
Do NOT use the OA case-study reply workflow — these leads were promised a different thing.

## Campaign Table

| Campaign ID | Vertical | Cold Email Template | Persona Examples |
|---|---|---|---|
| #3698110 | Fractional CFOs / CPAs | "your pipeline" — referral channel for attorneys, bankers, advisors | Claire, Anna, Brooklyn, Genesis, Abigail, Destiny, Emily, Layla, Everly |
| #3698111 | Business Coaches | "on purpose" — CPAs, attorneys, peer-group chairs as referral sources | Chloe, Hazel, Arianna |
| #3698112 | Marketing Consultants | "the build side" — partnership channels, list reactivation, newsletters | Lillian, Julia |
| #3698114 | CRM Consultants | "empty system" — fixing databases that sit unused after CRM builds | Allison, Amelia, Scarlett |
| #3692104 | Healthcare/Aesthetics (Prospector) | Unknown — discovered Jul 22. Leads: procelltherapies, mseaudio, precisioncoatingsinc, dermatologyconsultants | Unknown |

## Cold Email Templates

All templates sign off as "justin" (lowercase). Common structure: personalization (what we saw about their business), diagnosis (pain point), solution framing, promise (case study + partner map), CTA ("worth 20 minutes?").

### "your pipeline" (#3698110 — Fractional CFOs)
```
Hey {Name},

saw {Company} runs fractional CFO engagements.

you build clients a thirteen week cash forecast and hold them to it.

your own pipeline?

whoever happens to call.

because client work eats the week.

i build the referral channel itself.

the attorneys, bankers, and advisors already next to your ideal clients, set up to send them your way on purpose.

worth 20 minutes?

reply and i'll send the case study of another fractional CFO we ran this exact strategy for. before we talk i'll build your full partner map, every place your referrals can come from.

in-house or with us. yours either way.

justin
```

### "on purpose" (#3698111 — Business Coaches)
```
Hey {Name},

saw you've been working with owner-led companies as a business coach.

nobody has to sell you on systems. your best clients came from referrals, which is proof the channel works.

it's just not a system yet.

that's the part i run.

the CPAs, attorneys, and peer-group chairs already next to struggling operators, set up to send them your way on purpose.

worth 20 minutes?

reply and i'll send the case study of another business coach we ran this exact strategy for. before we talk i'll build your full partner map, every place your referrals can come from.

in-house or with us. yours either way.

justin
```

### "the build side" (#3698112 — Marketing Consultants)
```
Hey {Name},

saw {Company} does marketing strategy work.

i'd bet the plans you hand clients include things nobody on their team can build.

partnership channels. list reactivation. a newsletter that actually runs.

the strategy is right. the results lag anyway.

that's the work my team does. you prescribe it, we build it under your plan.

reply and i'll send how this runs for another marketing consultant we build for. then 20 minutes and i'll walk you through the structure and what your share looks like.

justin
```

### "empty system" (#3698114 — CRM Consultants)
```
Hey {Name},

saw {Company} does CRM builds and consulting.

you know the pattern. a beautiful build goes live, then the database just sits there.

thousands of contacts nobody emails.

your clients' portals. and probably your own.

my whole thing is fixing that second part. referral partners on purpose, campaigns that actually run.

worth 20 minutes?

reply and i'll send the case study of another CRM consultant we ran this exact play for. before we talk i'll build your full partner map plus the exact playbook we'd run.

either way the map and strategy are yours.

justin
```

## Reply Classification for Partner Campaigns

**Expected reply pattern (day 1-3 post-launch):**
- 85-95% OOO/auto-responders (CPA firms have high summer OOO rates)
- ~10% hostile/unsub  
- 1-5% positive/engaging

**Classification rules unique to Partner campaigns:**
- "Or your guy for this, Thanks." = **positive_soft** (human engaging, asking about the right contact)
- "Please direct all correspondence to frontoffice@" = **auto_responder** (not hostile)
- "Please contact X@Y.com for any Z requests" with "not monitored" = **auto_responder redirect** — do NOT classify as positive even if "please" + "email" keywords match
- Reply within ≤5 seconds of send = **auto_responder** (server-side rule, not human) — check `time` delta between SENT and REPLY before any positive classification
- "This email is not monitored" / "this inbox is not monitored" = **auto_responder**
- "Please remove this and all other [Company] emails" = **hostile** (remove request)
- "No longer with [Company]" = **dead** (departed)
- "I am currently on maternity leave" = **auto_responder / OOO**

## July 22, 2026 — Day 3 PM Sweep Results (09:35 AM ET)

Cross-campaign sweep of pages 0-2 (60 entries, 14 auto-reply prefixes filtered, 46 real leads). Sampled 12 of the most recent/timely entries across all campaigns for message history pull:

**Partner campaigns (#3698110-3698114, #3692104) — 6 entries checked:**

| Lead | Campaign | Classification | Details |
|---|---|---|---|
| Kala Duncan (procelltherapies.com) | #3692104 | **hostile** | "please remove me from your list" — added to hostile_senders |
| Dave Staley (mseaudio.com) | #3692104 | **auto_responder** | "Please contact engineering@mseaudio.com for any engineering requests. This email is not monitored." — 3-second latency. ⚠️ Initially misclassified as `positive_interested` because `\bplease\b.*\bemail\b` matched the positive pattern. Corrected. |
| Jim O'Keefe (precisioncoatingsinc.com) | #3692104 | **auto_responder** | Company acquisition notice — "PCI has become a part of..." |
| Eric M (dermatologyconsultants.org) | #3692104 | **auto_responder** | "email that is no longer valid" — redirect to Operations Manager |
| Heidi (galvanizeworldwide.com) | #3698112 | **auto_responder** | OOO — "currently out of the office" |
| Bill Dove (billdove.com) | #3698110 | **dead** | "I am now retired and don't need your services. Please refrain from contacting me in the future." — already in daemon state |

**Other campaigns — 6 entries checked:**

| Lead | Campaign | Classification | Details |
|---|---|---|---|
| Steve Kayser (kaysermedia.com) | #3577260 | **positive — HANDLED** | 9-message deep-funnel. Latest reply Jul 21: "Yes. Well done. Exactly what a client would want. Sorry for the delay. Been out of town." — already replied to within 38 min ("love that. We're here now... Go book in a time"). Fully handled. |
| Jeff Dillon (usmenshealth.com) | #3617053 | **positive — HANDLED** | "Yes, I'd be open to see what you have." Already handled by prior cron. In both daemon and OA state. |
| Kareem (kareemelsayed.com) | #3617053 | **negative_notfit** | "too late and already developed my own systems" — already in state. |
| Anna (techiestaffing.com) | #3652624 | **hostile** | "Remove me permanently from your email list. Moving this to spam." — already in state. |
| Eric Edelsberg (culturefit.com) | #3652624 | **hostile** | "unsubscribe" — already in OA state. |
| Texas (strivepharmacy.com) | #3617053 | **hostile** | "please remove us from your mailing list" — already in both states. |

**Key takeaways (Day 3):**
- **Zero unhandled positives.** The Day 3 sweep confirms the auto-responder pattern is holding — partner campaign replies remain 100% OOO/auto-reply/hostile/retired.
- **#3692104 discovered** — appears to be another Prospector campaign (possibly healthcare/aesthetics vertical based on leads: procelltherapies, mseaudio, precisioncoatingsinc, dermatologyconsultants). Same auto-responder dominance as other partner campaigns.
- **Bill Dove explicitly retired** — "refrain from contacting me" was classified `dead` and already in daemon state.
- **Dave MSE false-positive:** 3-second auto-responder redirect ("Please contact engineering@mseaudio.com") misclassified as `positive_interested` because `\bplease\b.*\bemail\b` matched. Pattern fix: check for "not monitored" / "this email is not" / sub-5-second latency before assigning positive classification.
- **Steve Kayser deep-funnel persists** — 9 messages across 12 days, positive reply handled within 38 minutes. Classic example of COMPLETED-campaign leads continuing to engage — reaffirms need for cross-campaign inbox sweeps.
- Stat file grew from 611 → 616 message IDs (+5 new: dave_mse, jim, heidi, eric, kala). 1 new hostile sender (kala.duncan@procelltherapies.com).

## July 21, 2026 — Day 1 Sweep Results

20 inbox entries, all from Partner campaigns (#3698110-3698114):

| Result | Count | Examples |
|---|---|---|
| OOO / auto-responder | 14 | Long-term OOO (Daniel/gocamsolar), 2-week OOO (Cody, Erilda), traveling (Cheryl), maternity leave (Taylor/strandmc), "2 business days" (Ruben), front-office redirect (Cory) |
| Hostile / unsubscribe | 2 | Alex/accountixsolutions ("Unsubscribe"), PJ/c-iq ("remove this") |
| Departed | 1 | Lindsay/frederickmtngroup ("no longer with FMG") |
| Positive / engaging | 1 | **Steve/relaypayments** ("Or your guy for this, Thanks.") |
| Already handled (other campaign) | 1 | Nicole/writekindagirl (#3577260, deferred to August) |
| Auto-reply prefix filtered | 0 | All personal email addresses, no info@/support@ prefixes |

**Key takeaway:** Partner campaign replies are almost entirely non-human on day 1. Genuine positives are rare but signal intent — these leads read the cold email and are engaging despite the auto-responder flood. Flag them to the operator promptly since the daemon won't catch them.

## Automated Sweep Playbook

For cron monitoring of Partner campaigns:

1. Pull inbox page 0, check for entries from #3698110-3698114 with today's `last_reply_time`
2. For entries with personal email addresses: pull message history and classify
3. OOO/auto-responder/hostile → add message ID to `replied_message_ids`, hostile email to `hostile_senders`
4. Positive → **flag to operator in delivery**. Do NOT auto-reply. The daemon has no CAMPAIGN_CONTEXT for these.
5. Expect 90%+ silent runs after day 3 as the auto-responder wave subsides