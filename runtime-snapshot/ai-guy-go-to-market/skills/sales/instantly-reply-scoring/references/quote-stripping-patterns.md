# Quote-Stripping Patterns for Reply Classification

The single biggest source of false positives in reply classification is **matching keywords from the original cold email** rather than the lead's actual reply. Every cold email body contains positive-sounding language ("send more info," "case studies," "interested," "book a call") — if the quoted original leaks into classification, the classifier will call everything positive.

## Canonical `strip_quotes()` Implementation

```python
import re

def strip_quotes(body):
    """
    Extract only the lead-authored text from a reply body.
    Returns the first non-quoted segment before any quote marker.
    Handles all common email reply formats.
    """
    markers = [
        # Gmail web, Apple Mail, standard clients
        r'On .+ wrote:',
        # Outlook/Exchange classic divider
        r'-----Original Message-----',
        # Outlook format: "From: Name <email> Date: ... To: ... Subject: ..."
        # Uses Date: and To:/Subject: as anchors (not "Sent:" which may be absent)
        r'From:.*?Date:.*?(?:To:|Subject:)',
        # Quoted text in plain-text replies (reply above, quote below)
        r'> On .+',
        # Gmail/Apple Mail compact format: "On Jul 16, 2026, 9:00 AM"
        # No "wrote:" suffix — just the timestamp
        r'On \w{3} \d{1,2}, \d{4},? at? \d{1,2}:\d{2} [AP]M',
        # "From: ... Sent:" (Outlook with Sent field)
        r'From:.*?Sent:',
    ]
    for marker in markers:
        parts = re.split(marker, body, maxsplit=1, flags=re.IGNORECASE)
        body = parts[0].strip()

    # If body is now empty/whitespace-only, the reply was only quoted content
    if not body or body.isspace():
        return ''

    return body
```

## Reply Format Catalog

### Format 1: Gmail Web / Apple Mail (standard)
```
Sure, send me more info.

On Tue, Jul 21, 2026 at 12:08 PM Hazel Adams <hazel@horizonfocusmo.info> wrote:
> Hey Stephen, saw you've been working with owner-led companies...
```
**Marker:** `On .+ wrote:` ✅

### Format 2: Outlook / Exchange
```
Yes, I'd be open to see what you have.

Jeff

From: Aubrey Scott <aubrey@strategybasesc.info>
Date: Thursday, July 16, 2026 at 8:39 AM
To: jeff.dillon@usmenshealth.com <jeff.dillon@usmenshealth.com>
Subject: [Ext] nearby

Been watching what you're building — impressive...
```
**Marker:** `From:.*?Date:.*?(?:To:|Subject:)` ✅  
**⚠️ `From:.*Sent:` does NOT work here** — Outlook uses "Date:" not "Sent:"

### Format 3: Apple Mail (compact, no "wrote:")
```
Sure!

On Thu, Jul 16, 2026, 9:00 AM Julia Castillo <julia@horizonstepfl.info> wrote:
> Looked into what you guys offer — this is the kind of clinic...
```
**Marker:** `On .+ wrote:` ✅ (this format IS caught, but only if HTML stripping preserves `<` brackets)

Actually note: when `email_body` is HTML-stripped with `re.sub(r'<[^>]+>', ' ', body)`, the `<email>` brackets become spaces. So `Julia Castillo < julia@horizonstepfl.info >` becomes `Julia Castillo   julia@horizonstepfl.info  `. The `On .+ wrote:` regex may still match because `.*` is greedy and will span across the extra spaces.

### Format 4: Gmail Mobile (compact)
```
yes

On Wed, Jul 15, 2026 at 8:20 AM Penelope Sanchez <penelope@scaledeskct.info> wrote:
> Looked into what you guys offer...
```
**Marker:** `On .+ wrote:` ✅

### Format 5: HTML-only (no text divider)
Some replies embed the quoted email as HTML without any text divider. In these cases, `strip_quotes()` returns the full body and classification runs on everything. **Mitigation:** classify the FIRST non-quoted sentence if possible.

### Format 6: Forwarded as REPLY
Instantly sometimes labels operator-sent follow-ups as REPLY type. The `email_body` reads like an outbound message ("Hey Mike, wanted to follow up..."). Filter these out by checking `message_id` for our sending domains BEFORE classification.

### Format 7: Ticket system "Please wait while we find someone..."
```
Please wait while we find someone...

On July 16, 2026 05:58 AM, 'Kinsley Morales' via Care Team <kinsley@successcrestco.info> wrote:
> Saw your work in the men's health space...
```
**Marker:** `On .+ wrote:` catches this variant with the `'Name' via Team` format.

### Format 8: Auto-responder acknowledgments
```
Thanks for reaching out! This is an automatic confirmation that we've received your message.
A support representative will be reviewing your request and will be in touch within 1-2 business days.
```
No quote marker — the entire body is the auto-responder's content. Classification must handle this via auto-responder pattern matching (Rule 4) BEFORE any positive keyword matching.

## Common Failure Modes

| Failure | Root Cause | Fix |
|---|---|---|
| Outlook reply body leaks through | `From:.*Sent:` requires "Sent:" in the header but Outlook uses "Date:" | Use `From:.*?Date:.*?(?:To:|Subject:)` as a backup marker |
| iOS Mail "On ... at ..." without "wrote:" leaks | No pattern for compact date-only format | Add `On \w{3} \d{1,2}, \d{4},? at? \d{1,2}:\d{2} [AP]M` |
| HTML-stripped angle brackets break `On .+ wrote:` | `<email@domain>` becomes ` email@domain ` after stripping, `On .+ wrote:` may not span the extra spaces | The `.+` is greedy and usually works, but edge cases with very long names/emails can fail |
| Body is entirely quoted content | `strip_quotes()` returns empty string | Check for empty string and classify as `empty` (skip) |
| "From:" appears in the lead's own reply text | False split — the lead's actual reply gets truncated | Order markers from most-specific to least-specific; `From:.*?Date:` with Date/To/Subject anchors is more specific than bare `From:` |

## Verification Recipe

After classification, spot-check at least 5 positives by reading the raw `email_body` and manually identifying where the lead's reply ends and the quote begins. If any of the 5 have quoted content leaking through, fix `strip_quotes()` and reclassify the entire batch.
