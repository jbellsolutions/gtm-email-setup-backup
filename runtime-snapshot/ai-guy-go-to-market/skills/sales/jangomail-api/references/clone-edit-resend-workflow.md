# Clone-Edit-Resend: Re-sending a Campaign to a New List

Session-proven workflow for pulling a sent campaign's HTML, editing it, and
sending to a fresh list. Used Jul 27 2026 for Green Room + Protocol re-sends.

## When to Use

- Newsletter needs minor text edits (date change, tense fix) before re-sending
- Same content, different recipient list
- No need to rebuild from scratch — clone the existing campaign

## Full Python Recipe

```python
import urllib.request, urllib.parse, json, base64
import xml.etree.ElementTree as ET
import html as html_module

USER = "UsingAIToScale"
PASS = "Jango123!"

def jango(method, **params):
    creds = {"Username": USER, "Password": PASS}
    data = urllib.parse.urlencode({**creds, **params}).encode()
    url = f"https://api.jangomail.com/api.asmx/{method}"
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    resp = urllib.request.urlopen(req, timeout=30)
    return resp.read().decode("utf-8", errors="replace")

# 1. Pull original campaign XML
details_xml = jango("GetCampaignDetails_XML", JobId="<source_job_id>", Options="")

# 2. Parse XML — HTMLMessage and PlainTextMessage are HTML-entity-escaped
root = ET.fromstring(details_xml)
campaign = root.find(".//Campaign")
html_content = html_module.unescape(campaign.find("HTMLMessage").text)
plain_content = html_module.unescape(campaign.find("PlainTextMessage").text)
subject = campaign.find("SubjectLine").text
from_email = campaign.find("FromEmail").text

# 3. Apply edits (example: date change)
html_content = html_content.replace("Thursday, July 23, 2026", "Monday, July 27, 2026")
plain_content = plain_content.replace("Thursday, July 23, 2026", "Monday, July 27, 2026")

# 4. Sweep for related references
import re
for m in re.finditer(r"Thursday", html_content):
    start = max(0, m.start() - 80)
    end = min(len(html_content), m.end() + 80)
    print(f"  Remaining 'Thursday': ...{html_content[start:end]}...")
# Fix any remaining instances as needed

# 5. Create new list and import members
jango("AddGroup", GroupName="new-list-name")
# ... ImportGroupMembersFromData, wait 15s, verify count ...

# 6. Send via v1 SendMassEmail (NOT v2 — more reliable for list sends)
result = jango("SendMassEmail",
    FromEmail="email@scaleverticalwithai.com",
    FromName="Scale Vertical AI",
    ToGroups="new-list-name",
    ToGroupFilter="",
    ToOther="",
    ToWebDatabase="",
    Subject="🧬 New Subject Line",  # Unicode emoji, not shortcode
    MessagePlain=plain_content,
    MessageHTML=html_content,
    Options="TrackOpens,TrackClicks")
# Returns: 0\nSUCCESS\n{new_job_id}
```

## Key Pitfalls

1. **HTML escaping in XML response**: `GetCampaignDetails_XML` wraps the HTML
   in `<HTMLMessage>` with all `<`, `>`, `&` escaped as entities. You MUST
   `html.unescape()` before editing or your find-and-replace won't match.

2. **Unicode characters after unescape**: After `html.unescape()`, entities
   like `&ndash;` become actual `–` (U+2013). Match the real character in
   your find-and-replace, not the entity.

3. **Multiple instances of headline text**: A headline string can appear in
   multiple places — linked headline text, image `alt` attribute, masthead,
   TOC bullet, plain-text version. Replace ALL instances in both HTML and
   plain text. Always do a post-fix `re.finditer()` sweep.

4. **v1 SendMassEmail vs v2 for re-sends**: Use v1 `SendMassEmail` with
   `ToGroups`. v2 `POST /campaigns` + `PUT /campaigns/{id}/send` is
   unreliable for list-based sends (known issue documented in SKILL.md).

5. **Stagger multiple sends**: When sending two newsletters in one session,
   wait at least 8-10 minutes between `SendMassEmail` calls so JangoMail
   processes them sequentially and inbox providers don't see a burst.

6. **Subject line emoji**: Use real Unicode emoji (🧬, 🎙️), not Slack-style
   shortcodes (`:dna:`, `:studio_microphone:`).

## Pre-send Verification Checklist

- [ ] New group member count == expected (e.g., 250)
- [ ] No remaining instances of old date/tense phrases in HTML or plain text
- [ ] Subject line uses Unicode emoji
- [ ] `From` email is `email@scaleverticalwithai.com`
- [ ] Unsubscribe link uses `***uniqueid****` placeholder (carried from original)
- [ ] Tracking options: `TrackOpens,TrackClicks`

## +2 Hour Follow-up

After sending, schedule a one-time cron job (~2 hours out) to pull
`GET /campaigns/{id}/stats` and report: recipients, bounces, blocks,
delivered, opens, clicks, unsubscribes, complaints, open rate %.