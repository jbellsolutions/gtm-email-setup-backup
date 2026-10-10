# SpeakerAgent Podcast Campaign #3639259

Created July 14, 2026. Mirror of PR campaign #3577260 but targeting podcasters instead of PR agencies.

## Campaign Config

| Setting | Value |
|---|---|
| ID | 3639259 |
| Name | Podcasters - SpeakerAgent v2 - July 2026 |
| Status | DRAFTED (blocked — lead credit limit) |
| Leads | 3,076 (processed, ready to upload) |
| Sequence | Single email, no follow-ups |
| Plain text | true |
| Tracking | DONT_TRACK_EMAIL_OPEN, DONT_TRACK_LINK_CLICK |
| Schedule | Mon-Fri 8AM-5PM ET |
| Max/day | 500 |
| AI ESP matching | true |
| Follow-up % | 100 |
| Stop rules | REPLY_TO_AN_EMAIL |

## Sequence

```
Subject: your podcast

Hey {{first_name}},

Saw your podcast — liked what we saw.

We get people coming to speakeragent.ai who are finding your show and asking about it. We wanted to reach out, get to know you, and be able to accurately tell them about your podcast — what you guys are looking for as far as guests, the kind of people you want to talk to, and potentially even feature you when someone asks for something specific.

We're already getting inquiries from people asking about podcasts like yours, and we'd rather send them to someone we know.

Can we refer people to you? If so let's hop on a quick call. We'll get a feel for what you do, how you pick guests, and make sure we're sending the right people your way.

Worth 15 minutes?

{{sender_name}}
```

## Lead Source

CSV from podcast catalog: `/opt/data/cache/documents/doc_3684c5497d63_updated verified podcast email.csv`
- 3,440 rows, 3,076 unique verified emails
- Fields: `podcast_catalog_id`, `podcast_name`, `podcast_host_id`, `host_name`, `email`, `email_status`, `last_verified_at`
- All emails verified (July 2026)
- Processed leads saved at `/tmp/podcast_leads.json`

## First Name Extraction

`host_name` field often contains literal string `"null"` from DB. Extraction logic:
1. If `host_name` is non-null and not literal "null" string → extract first word before comma/space
2. Skip titles (Dr., Mr., Mrs., Ms.)
3. Fallback: use first reasonable word from `podcast_name` (skip "The", "A", "An")
4. Last resort: use "there"

## Operator Reply Template

Same as PR campaign — SpeakerAgent team operators reply with Tony Calendly link:
```
Even better. I'll drop a link to Tony's calendar. He's the founder and the guy you want to be speaking with. Here's the link — https://cal.com/speakeragent/catch-up

Pick a time that works for you. I've also looped him on this email FYI if you have any questions along the way.
```
CC: tony@speakeragent.ai

## Blockers

- ⚠️ **Lead credit limit reached** — Instantly account needs credit top-up before uploading 3,076 leads