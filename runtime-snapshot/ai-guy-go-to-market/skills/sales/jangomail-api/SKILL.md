---
name: jangomail-api
description: JangoMail email platform — direct classic API integration. Lists, transactional email, mass email (campaigns/newsletters), unsubscribes, bounces, reporting, SMTP relay. 1,435 operations. No CLI dependency.
version: 2.5.0
metadata:
  hermes:
    tags: [jangomail, email, cold-email, newsletter, transactional, campaigns, smtp]
    connector_id: pp-jangomail
---

# JangoMail API (Direct)

Two APIs available — v1 SOAP (classic) and v2 REST (newer). Prefer v2 REST for JSON responses and cleaner endpoint structure.

## v1 SOAP API (Classic)

1,435 operations via XML SOAP.

**API endpoint:** `POST https://api.jangomail.com/api.asmx/{MethodName}`
**Auth:** Form fields `Username` + `Password`
**Response:** XML (`text/xml`)
**Credentials:** From `.env` (`JANGOMAIL_USERNAME`, `JANGOMAIL_PASSWORD`)
**WSDL:** `https://api.jangomail.com/api.asmx?WSDL`

## v2 REST API (Newer — Prefer This)

80+ RESTful endpoints with JSON request/response. Swagger docs at `https://api-v2.jangomail.com/docs` with live Try-It.

**API endpoint:** `https://api-v2.jangomail.com`
**Auth:** Basic Auth (Base64 `username:password`) or Bearer token (user-created API key via `POST /apitokens`)
**Response:** JSON
**Swagger spec:** `https://api-v2.jangomail.com/swagger/v2/swagger.json`
**Full endpoint map:** see `references/v2-api-endpoints.md`
**Swagger-derived path listing:** see `references/v2-swagger-paths.md` (90+ endpoints, discovered 2026-07-16)

### Campaign / Newsletter Quick Start (v2)

**⚠️ Pitfalls:** `from` must be an object, `to_other` is an array of objects, `character_set` and `encoding` are both required. Full working payload with error→fix map: see `references/campaign-creation-payload.md`.

```python
import urllib.request, json, base64

base = 'https://api-v2.jangomail.com'
auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}

# Create campaign
data = json.dumps({
    'name': 'My Newsletter',
    'subject': 'Weekly Update',
    'fromEmail': 'email@scaleverticalwithai.com',
    'fromName': 'Scale Vertical AI',
    'messageHTML': '<h1>Hello</h1>',
    'messagePlain': 'Hello',
    'listIDs': [123],
}).encode()
req = urllib.request.Request(f'{base}/campaigns', data=data, headers=headers, method='POST')
resp = json.loads(urllib.request.urlopen(req).read())

# Send campaign
campaign_id = resp['id']
req = urllib.request.Request(f'{base}/campaigns/{campaign_id}/send', data=b'', headers=headers, method='PUT')
urllib.request.urlopen(req)

# Check stats
req = urllib.request.Request(f'{base}/campaigns/{campaign_id}/stats', headers=headers)
stats = json.loads(urllib.request.urlopen(req).read())
```

## SMTP Relay

For sending via external clients or code that uses SMTP directly:

| Setting | Value |
|---------|-------|
| Server | `express-relay.jangosmtp.net` |
| Username | `UsingAIToScale` |
| Password | `Jango123!` |
| Ports | 25, 2525, 465 (SSL/TLS), 587 (STARTTLS) |

## Quick Start — Python Helper

```python
import urllib.request, urllib.parse, os

def jango(method, **params):
    """Call JangoMail classic API."""
    creds = {
        'Username': os.environ['JANGOMAIL_USERNAME'],
        'Password': os.environ['JANGOMAIL_PASSWORD'],
    }
    data = urllib.parse.urlencode({**creds, **params}).encode()
    url = f'https://api.jangomail.com/api.asmx/{method}'
    req = urllib.request.Request(url, data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.status, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')
```

## Common Operations

### List Management

**List all regular groups:**
```python
status, body = jango('Groups_GetList_String',
    RowDelimiter='\n', ColDelimiter=',', TextQualifier='"')
```

**List all transactional groups:**
```python
status, body = jango('Groups_GetTransactionalList_String',
    RowDelimiter='\n', ColDelimiter=',', TextQualifier='"')
```

**Create a group:**
```python
status, body = jango('AddGroup', GroupName='My List')
# Returns: "0\nSUCCESS\n{GroupID}"
```

**Add member to group:**
```python
status, body = jango('AddGroupMember',
    GroupName='My List',
    EmailAddress='contact@example.com',
    FieldNames='',    # comma-separated custom field names, or empty
    FieldValues='')   # comma-separated custom field values, or empty
```

**Bulk import members from CSV data (v1 — note required field name):**
```python
# ⚠️ The email field MUST be named "EmailAddress" not "Email"
# Using "Email" returns: InvalidGroupFieldsException: The list of fields must include the EmailAddress field.
status, body = jango('ImportGroupMembersFromData',
    GroupName='My List',
    FieldNames='EmailAddress,FirstName,LastName',  # EmailAddress, NOT Email
    ImportData='a@b.com,John,Doe\nc@d.com,Jane,Smith',
    ColumnDelimiter=',',
    RowDelimiter='\n',
    TextQualifier='"')
# Despite returning SUCCESS, the import is asynchronous — member count may show 0
# briefly. Re-check GetGroupMemberCount after 10-15 seconds.
```

**Check if member exists in group:**
```python
status, body = jango('IsMemberInGroup',
    GroupName='My List',
    EmailAddress='contact@example.com')
```

**Get group member count:**
```python
status, body = jango('GetGroupMemberCount', GroupName='My List')
```

**Get members of a group:**
```python
status, body = jango('Groups_GetMembers_String',
    GroupName='My List',
    RowDelimiter='\n', ColDelimiter=',', TextQualifier='"')
```

**Delete a group:**
```python
status, body = jango('DeleteGroupByName', GroupName='My List')
```

**Delete a member:**
```python
status, body = jango('DeleteGroupMember',
    GroupName='My List',
    EmailAddress='contact@example.com')
```

**Rename a group:**
```python
status, body = jango('Groups_Rename',
    OldGroupName='My List',
    NewGroupName='My New List')
```

### Transactional Email (One-Off Sends)

**Send one tracked transactional email:**
```python
status, body = jango('SendTransactionalEmail',
    FromEmail='sender@yourdomain.com',
    FromName='Your Name',
    ToEmailAddress='recipient@example.com',
    Subject='Your Subject',
    MessagePlain='Plain text version',
    MessageHTML='<p>HTML version</p>',
    Options='')  # comma-separated: TrackOpens,TrackClicks,etc.
# Returns: "0\nSUCCESS\n{TransactionalID}"
```

**Send from a template:**
```python
status, body = jango('SendTransactionalEmailFromTemplate',
    FromEmail='sender@yourdomain.com',
    FromName='Your Name',
    ToEmailAddress='recipient@example.com',
    TemplateName='My Template',
    Options='')
```

### Mass Email / Campaigns / Newsletters

**Send mass email to groups (v1 — ALL params required):**
```python
# ⚠️ SendMassEmail requires ALL optional parameters to be passed explicitly.
# Omitting ToGroupFilter, ToOther, or ToWebDatabase — even as empty strings —
# returns "Missing parameter: ToGroupFilter" (or whichever is missing).
# Always pass all three, even when only one is used.
status, body = jango('SendMassEmail',
    FromEmail='sender@yourdomain.com',
    FromName='Your Name',
    ToGroups='Group1,Group2',     # comma-separated group names
    ToGroupFilter='',              # REQUIRED — pass empty string if not used
    ToOther='',                    # REQUIRED — pass empty string if not used
    ToWebDatabase='',              # REQUIRED — pass empty string if not used
    Subject='Newsletter Subject',
    MessagePlain='Plain text',
    MessageHTML='<h1>Newsletter</h1>',
    Options='TrackOpens,TrackClicks')  # comma-separated options
# Returns: 0\nSUCCESS\n{JobID}
```

**Check mass email status:**
```python
status, body = jango('GetMassEmailStatus', JobID='12345')
```

**Pause/Resume a mass email:**
```python
jango('PauseMassEmail', JobID='12345')
jango('ResumeMassEmail', JobID='12345')
```

**Approve a queued mass email:**
```python
jango('ApproveMassEmail', JobID='12345')
```

**Delete a mass email:**
```python
jango('DeleteMassEmail', JobID='12345')
```

**Get campaign details:**
```python
status, body = jango('GetCampaignDetails_XML', JobId='12345', Options='')
```

### Unsubscribes & Bounces

**Check unsubscribe status:**
```python
status, body = jango('CheckUnsubscribe', EmailAddress='user@example.com')
# Returns: "1\nUnsubscribed" or "3\nNot Found"
```

**Get bounces by campaign:**
```python
# ⚠️ Parameter is JobID, NOT CampaignID
status, body = jango('Reports_GetBouncesByCampaign_String',
    JobID='12345',
    RowDelimiter='\n', ColDelimiter=',', TextQualifier='"')
```

**Get unsubscribes by campaign:**
```python
# ⚠️ Parameter is JobID, NOT CampaignID
status, body = jango('Reports_GetUnsubscribesByCampaign_String',
    JobID='12345',
    RowDelimiter='\n', ColDelimiter=',', TextQualifier='"')
```

**Get complaints by campaign:**
```python
# ⚠️ Requires SortBy param (unlike bounces/unsubs reports)
# Parameter is JobID, NOT CampaignID
status, body = jango('Reports_GetComplaintsByCampaign_String',
    JobID='12345',
    SortBy='Date', SortOrder='DESC',  # both required
    RowDelimiter='\n', ColDelimiter=',', TextQualifier='"')
```

## Safety Rules

1. **Prefer read/report commands** unless task explicitly requires sending or mutation
2. **Never call send operations** without explicit confirmation of: recipient, sender, subject, body, and options
3. **No destructive operations without explicit task**: `DeleteGroupByName`, `DeleteGroupMember`, `DeleteMassEmail`, `Groups_DeleteAllMembers`
4. **Store no email addresses** beyond task scope unless user explicitly asks for a saved report
5. **Credentials never in memory/logs/skills** — always from `.env` only
6. **Check sending limits** — if you get "sending limit has been exceeded", the account needs upgrade. Flag this to the user immediately.

## Workflow: SDR Cold Email → Voice Follow-Up

Full SDR outreach flow combining JangoMail email + Vapi voice calls:

1. **Send email** — `SendTransactionalEmail` with personalized message to prospect
2. **Initiate voice call** — Vapi `POST /call` (see `vapi` skill)  
3. **Track both** — note JangoMail TransactionalID + Vapi call ID
4. **Log outcome** — disposition in CRM or group notes

```python
# Combined SDR outreach (email + voice)
import os, urllib.request, urllib.parse, json

# Step 1: Send email via JangoMail
def sdr_send_email(prospect_email, prospect_name, company_name, subject, body_plain, body_html):
    status, response = jango('SendTransactionalEmail',
        FromEmail='email@scaleverticalwithai.com',
        FromName='Scale Vertical AI',
        ToEmailAddress=prospect_email,
        Subject=subject,
        MessagePlain=body_plain,
        MessageHTML=body_html,
        Options='TrackOpens,TrackClicks')
    return response  # contains TransactionalID

# Step 2: Initiate Vapi call (requires vapi skill + VAPI_API_KEY)
def sdr_initiate_call(prospect_phone, prospect_name, assistant_id):
    VAPI_KEY = os.environ['VAPI_API_KEY']
    VAPI_BASE = 'https://api.vapi.ai'
    body = json.dumps({
        'assistantId': assistant_id,
        'customer': {'number': prospect_phone, 'name': prospect_name},
        'phoneNumberId': os.environ['VAPI_PHONE_NUMBER_ID'],
    }).encode()
    req = urllib.request.Request(f'{VAPI_BASE}/call', data=body,
        headers={'Authorization': f'Bearer {VAPI_KEY}', 'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())
```

## Workflow: Campaigns & Newsletters

1. **Prepare list** — `Groups_GetList_String` to verify target group
2. **Add members** — `ImportGroupMembersFromData` for bulk, `AddGroupMember` for singles
3. **Send** — `SendMassEmail` to the group(s) (v1) or `PUT /campaigns/{id}/send` (v2)
4. **Monitor** — `GetMassEmailStatus` (v1) for send completion; `GET /campaigns/{id}/stats` (v2) for delivery metrics
5. **Report** — Prefer v2 `GET /campaigns/{id}/stats` for the full picture in one call (recipients, bounces, blocks, opens, clicks, unsubs, complaints). Use v1 reports only when you need per-address detail (`Reports_GetBouncesByCampaign_String`, `Reports_GetUnsubscribesByCampaign_String`).
6. **Discover campaigns by group** — See "Campaign Discovery" section above (no direct group→campaign query exists).

Full end-to-end deployment checklist (asset prep → HTML rewrite → QA → list import → staggered send → delivery analysis): `references/newsletter-deployment-checklist.md`.
Image CDN cache-busting patterns and upload methods: see "Image CDN Cache-Busting" section in this SKILL.md.
Clone-edit-resend workflow (pull sent campaign HTML, edit text, re-send to new list): `references/clone-edit-resend-workflow.md`.

## Account Configuration

- **Sending domain:** `scaleverticalwithai.com` (authorized)
- **Default From email:** `email@scaleverticalwithai.com`
- **Default From name:** `Scale Vertical AI`
- **Account username:** `UsingAIToScale`
- **Account status:** ✅ API/SMTP operational (verified Jul 16 2026 — both v1 SOAP and v2 REST). Previously confirmed working Jun 3, 2026. bcrypt auth outage (Jul 14) resolved.

## Account Usage / Plan Limits

Check how many emails have been used against the plan cap:

```python
# v2 REST — returns emails_allowed, emails_sent, bytes_allowed, bytes_sent
req = urllib.request.Request(f'{base}/account/usage', headers=headers)
usage = json.loads(urllib.request.urlopen(req, timeout=10).read())
# → {"emails_allowed": 5000, "emails_sent": 464, "bytes_allowed": 500000000, "bytes_sent": 19981400}
```

v1 methods `GetAccountUsage` and `GetEmailUsage` return HTTP 500 — use v2 `/account/usage` instead.

## Verification / Health Check

Before any send operation, verify connectivity:

```python
import urllib.request, json, base64

USER = "UsingAIToScale"
PASS = "Jango123!"
auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()

# Quick v2 health: account info
req = urllib.request.Request("https://api-v2.jangomail.com/account",
    headers={"Authorization": f"Basic {auth}"})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
print(f"User: {resp['username']} — ID: {resp['user_id']}")

# Swagger (full endpoint map)
req = urllib.request.Request("https://api-v2.jangomail.com/swagger/v2/swagger.json",
    headers={"Authorization": f"Basic {auth}"})
spec = json.loads(urllib.request.urlopen(req, timeout=10).read())
print(f"v2 endpoints: {len(spec.get('paths', {}))}")
```

**Endpoint discovery:** v2 swagger at `/swagger/v2/swagger.json` — use this when you need the full API surface. ~90 paths covering campaigns, lists, transactional, domainkeys, tracking domains, unsubscribes, bounces, suppression, users, and account management.

## File & Image Hosting (v2 REST)

JangoMail v2 has a `POST /files` endpoint for uploading images and other assets. Uploaded files get a hosted URL (`https://img.jangomail.com/2606407/Images/<filename>`) usable in email HTML.

**Upload an image (Base64):**

```python
import urllib.request, json, base64

auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/json'
}

with open('image.jpg', 'rb') as f:
    raw = f.read()

data = json.dumps({
    'file_name': 'my-image.jpg',
    'contents_base64': base64.b64encode(raw).decode()
}).encode('utf-8')

req = urllib.request.Request(
    'https://api-v2.jangomail.com/files', data=data, headers=headers, method='POST'
)
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
# → {"file_name": "my-image.jpg", "url": "https://img.jangomail.com/2606407/Images/my-image.jpg", ...}
```

**Pitfalls:**
- Use `POST /files` (image/media library for email), not `POST /attachments` (email attachments).
- `contents_base64` must be standard Base64 (no line breaks). Python's `base64.b64encode()` produces this by default.
- File names must be unique — reusing a name returns 400 "File already exists". Append a timestamp if retrying.
- **Python urllib fails silently with large payloads** (raw image > ~100KB): the upload succeeds server-side but `urllib.request.urlopen()` returns an empty response, causing `JSONDecodeError`. For files >100KB, use curl with file-based payload instead (see reference).
- Response schema: `CreateAssetModel` → `AssetModel` with `file_name`, `url`, `size`, `description`.

**Large image upload via curl (recommended for files >100KB):**

```bash
AUTH=$(echo -n "UsingAIToScale:Jango123!" | base64 -w0)
# Write payload to file to avoid shell argument-too-long errors
python3 -c "
import json, base64
with open('large.jpg', 'rb') as f: raw = f.read()
with open('/tmp/payload.json', 'w') as f:
    json.dump({'file_name': 'large.jpg', 'contents_base64': base64.b64encode(raw).decode()}, f)
"
curl -s -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" \
  -d @/tmp/payload.json "https://api-v2.jangomail.com/files"
```

**List uploaded files & URLs:**
```python
req = urllib.request.Request('https://api-v2.jangomail.com/files', headers=headers)
files = json.loads(urllib.request.urlopen(req).read())
for f in files:
    print(f"{f['file_name']} ({f['size']}B) → {f['url']}")
```

**Delete a file:**
```python
req = urllib.request.Request(
    f'https://api-v2.jangomail.com/files/my-image.jpg', headers=headers, method='DELETE'
)
urllib.request.urlopen(req, timeout=10)
```

Hosted image URLs follow the pattern: `https://img.jangomail.com/2606407/Images/<filename>`.

## DNS Records Required for Sending

### DKIM — System DKIM is a CNAME, not TXT

JangoMail's system DKIM uses a **CNAME record** that points to their key server. When the API returns `public_key: "System Key jmsend.com/jm"`, that's the indicator — the actual RSA key lives on JangoMail's side.

| Field | Value |
|--------|-------|
| **Type** | `CNAME` |
| **Name/Host** | `jm._domainkey` |
| **FQDN** | `jm._domainkey.<yourdomain.com>` |
| **Value/Target** | `jm._domainkey.jmsend.com` |

After the CNAME propagates in DNS, go to JangoMail UI → Settings → Email Settings → DKIM → ENABLE. JangoMail will verify the CNAME resolves before enabling.

**Pitfall:** The API's `enabled: true` flag on a domain key does NOT mean DNS is configured. It means the key is enabled in JangoMail's system. If the CNAME isn't in DNS, receivers get NXDOMAIN and DKIM fails silently.

To use a TXT-based DKIM instead (advanced), see JangoMail support article "Create your own DKIM (Advanced)".

### SPF Record

JangoMail's SPF include mechanism: **`include:jangomail.com`**

If the domain is used by other mail services too, merge into the existing SPF — do NOT replace. Example:

```
# Before (Hostinger-only)
v=spf1 include:_spf.mail.hostinger.com ~all

# After (Hostinger + JangoMail)
v=spf1 include:_spf.mail.hostinger.com include:jangomail.com ~all
```

If the domain is JangoMail-only (dedicated subdomain):
```
v=spf1 include:jangomail.com -all
```

### Custom Tracking Domain

The tracking domain (`track.<yourdomain.com>`) needs its own CNAME pointing to JangoMail's tracking infrastructure. Verify with `GET /v2/trackingdomains`.

## Campaign Creation (v2 REST) — Payload Requirements

Creating a campaign via `POST /campaigns` has format requirements not obvious from the blank schema (`GET /campaigns/new`). A working payload requires:

```python
import urllib.request, json, base64

auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/json; charset=utf-8'
}

data = {
    'from': {                                    # MUST be an object, not a string
        'email': 'email@scaleverticalwithai.com',
        'name': 'Synova Talent Solutions'
    },
    'subject': 'Subject line',
    'reply_to': 'reply@domain.com',
    'message_html': '<h1>HTML content</h1>',
    'message_plain': 'Plain text fallback',
    'to_other': [{'email': 'recipient@example.com'}],  # Array of objects, not strings
    'tracking': {
        'click_track_html': True,
        'track_opens': True
    },
    'character_set': 'UTF-8',                    # REQUIRED — omit → "Unsupported encoding"
    'encoding': 'Quoted Printable',              # REQUIRED — valid values: '7 bit', 'Quoted Printable', 'Base64'
    'create_only': True                          # Create as draft without sending
    # Note: create_only=True still requires at least one recipient (to_other or to_lists)
}

body = json.dumps(data, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    f'{base}/campaigns', data=body, headers=headers, method='POST'
)
resp = json.loads(urllib.request.urlopen(req).read())
# Response: {"campaign_id": 399259736}  — note: campaign_id, not id
```

**Pitfalls:**
- `from` → object `{email, name}`, not a flat string. Using a string returns "The from field is required."
- `to_other` → array of `{email, name}` objects, not array of strings. Strings return a JSON conversion error.
- `character_set` and `encoding` → both required. Omit either and get "Unsupported encoding" (misleading — the HTML is fine, the field is just missing). Valid encodings from `GET /encodings`: `['7 bit', 'Quoted Printable', 'Base64']`.
- `create_only: true` → creates a draft but still requires at least one recipient. Add a placeholder if no real list yet.
- Response field is `campaign_id` (not `id`).
- Use `encoding='utf-8'` when opening HTML files and `ensure_ascii=False` in `json.dumps()`.

## Unsubscribe & View-Online Links — No Merge Tags, Use `***uniqueid****`

JangoMail does **NOT** support merge tag placeholders (`%%UNSUBSCRIBE%%`, `{{UNSUBSCRIBE_LINK}}`, etc.) for unsubscribe or view-as-webpage links. This is verified against their personalization docs, Zendesk help center, and live API testing. Every other major ESP (Mailchimp, ActiveCampaign, SendGrid) has these — JangoMail does not.

**Instead, JangoMail uses a `***uniqueid****` placeholder** within actual tracking URLs. This placeholder is replaced per-recipient at send time (similar to how `%%FieldName%%` works for custom fields, but embedded inside a URL). The pre-processor detects these URLs and does NOT inject a duplicate CAN-SPAM footer when they're present.

**Working URL patterns (this account):**
- **Unsubscribe:** `https://track.scaleverticalwithai.com/u.z?***uniqueid****`
- **View online:** `https://track.scaleverticalwithai.com/w.z?***uniqueid****`

The tracking domain (`track.scaleverticalwithai.com`) is account-specific — verify with `GET /v2/trackingdomains`. The `/u.z` and `/w.z` paths are the action endpoints; `***uniqueid****` is the placeholder JangoMail replaces with a per-recipient tracking ID.

**How to use in campaign HTML:**
```html
<!-- Unsubscribe link (one-click, JangoMail replaces ***uniqueid**** per recipient) -->
<a href="https://track.scaleverticalwithai.com/u.z?***uniqueid****">Unsubscribe</a>

<!-- View online / web version link -->
<a href="https://track.scaleverticalwithai.com/w.z?***uniqueid****">Read Online</a>
```

**Detecting the pre-processor:** When the unsubscribe URL is present in the correct format, JangoMail's pre-processor recognizes it and skips the forced CAN-SPAM footer injection. If you get a "forced footer" notification on send, the URL format is wrong or the domain doesn't match the account's tracking domain.

**Fallback options (if the URL pattern approach fails):**
- **Option A:** Hardcode a generic link to your own preference center and let JangoMail inject its CAN-SPAM footer
- **Option B:** Use the actual unsubscribe URL from a previously-sent campaign (copy from the editor UI)
- **Option C:** Leave `{{UNSUBSCRIBE_LINK}}` / `{{VIEW_ONLINE_LINK}}` placeholders and let JangoMail auto-inject — user must accept the JangoMail footer

**Programmatic view-online URL generation (v1 SOAP):** The v1 SOAP API has `GetViewAsWebPageURL` which returns the per-recipient URL for a given campaign:
```python
status, body = jango('GetViewAsWebPageURL', JobID='399338734', EmailAddress='recipient@example.com')
# Returns XML: <string>http://track.scaleverticalwithai.com/w.z?j=HASH&m=HASH</string>
```
This is useful for post-send reporting but not for HTML templates (the `j` and `m` hashes are per-recipient, so you can't embed them in a template). Use the `***uniqueid****` URL pattern in templates instead.

Full research notes and source citations: `references/merge-tags-research.md`.

## Campaign Send Returns 400 But Sends Anyway

When sending a campaign via `PUT /campaigns/{id}/send`, the API may return HTTP 400 with no response body — but the campaign **does** send. Check the campaign status via `GET /campaigns/{id}` after the call; if `status` is `"Sending"`, the send succeeded. The 400 appears to be a race condition or ambiguous validation response. Do not retry on 400 without checking campaign status first.

## Zip Extraction — Windows Backslash Paths

Zip files created on Windows may extract with literal backslash paths (e.g., `images\s0.jpg` as a single filename, not a directory tree). On Linux, these become flat files with backslashes in the name. Fix by renaming into proper directory structure:

```python
import os, shutil
for f in os.listdir(base_dir):
    if '\\' in f and f.endswith('.jpg'):
        proper_name = f.split('\\')[-1]
        shutil.move(os.path.join(base_dir, f), os.path.join(img_dir, proper_name))
```

## Email Headers & Deliverability Compliance

JangoMail emits full List-Unsubscribe headers compliant with Gmail/Yahoo Feb 2024 one-click requirements. Verified from raw message source on mail-tester Jul 23 2026.

**Headers emitted (confirmed):**
```
List-Unsubscribe: <https://track.scaleverticalwithai.com/u.z?j={job}&m={hash}>, <mailto:UsingAIToScale@jangomail.com?Subject=Unsubscribe>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

Both the URL one-click and mailto fallback are present. The `List-Unsubscribe-Post` header is the critical Feb 2024 addition — without it, Gmail and Yahoo penalize bulk senders.

**Authentication headers to verify after DNS changes:**
- **SPF:** Should show `SPF_PASS` with `include:jangomail.com` mechanism
- **DKIM:** Should show `DKIM_VALID` with `d=scaleverticalwithai.com` and `s=jm`
- **DMARC:** `dmarc=pass` (policy is `p=none` unless tightened)
- **Return-Path (bounce address):** `email@scaleverticalwithai.com`

**How to verify headers:** Send a test to mail-tester.com (see `references/mail-tester-workflow.md`), expand the "Source" section, or use `browser_console` to run `document.querySelectorAll('pre')` and extract the raw message including all headers.

**Spam score improvement:** The hidden preheader (`<div style="display:none">`) triggers `FONT_INVIS_LONG_LINE` / `FONT_INVIS_MSGID` spam flags worth ~2.5 points. Use `max-height:0px;overflow:hidden;` without `font-size:1px` to avoid these. Also remove `LOTS_OF_MONEY` trigger words from body copy.

## Account Usage (v2 REST)

**GET** `/account/usage` — return plan limits and current usage.

```python
req = urllib.request.Request(f'{base}/account/usage', headers=headers)
stats = json.loads(urllib.request.urlopen(req).read())
# Returns: {
#   "emails_allowed": 5000,       # plan cap
#   "emails_sent": 214,           # used this cycle
#   "bytes_allowed": 500000000,   # bandwidth cap
#   "bytes_sent": 9333542         # bandwidth used
# }
```

Use this instead of v1 `GetAccountUsage` or `GetEmailUsage` — both return HTTP 500. Also note that `GET /account` returns user/profile info but NOT usage data; the usage sub-endpoint is separate.

## Campaign Stats & Delivery Analysis (v2 REST)

### All-Time Reporting Workflow

For a complete current report, always re-fetch `GET /campaigns` and then query each campaign's `/stats` endpoint rather than relying on an older export or dashboard snapshot. Exclude drafts and campaigns with `recipients: 0` from sent totals, but retain one-recipient diagnostic sends when the report explicitly asks for all-time history. Treat `recipients` as sent attempts; calculate delivered as `recipients - bounces - blocks`. Calculate open and click percentages against delivered, and show both counts and percentages.

When presenting a historical report, group campaigns by the user's operational batch labels and date, then include per-batch subtotals and a grand total. Keep test campaigns in a clearly labeled diagnostic section. The campaign subject is the primary mapping key; maintain the newsletter mapping separately from the batch grouping because the same newsletter can occur in multiple sets. A reusable mapping and calculation example is in `references/all-time-reporting.md`.

### Important Reporting Caveat

JangoMail's `recipients` field is not necessarily the original list size: `removed_addresses` were suppressed before sending, while `blocks` and `bounces` occur during/after delivery. Do not add `removed_addresses` to sent or delivered counts. Report blocks separately when useful, even if the requested table only asks for bounces.


The v2 API provides a clean stats endpoint per campaign — use this over the v1 XML reports for quick numbers. Get it via `GET /campaigns/{id}/stats`.

**Stats refresh over time:** The `opens`, `clicks`, `unsubscribes`, etc. in the stats response are live counts that accrue as recipients interact. Re-pulling the same endpoint hours or days later gives updated numbers. This is useful for scheduled re-pulls to track open-rate maturation.

**Inspecting sent HTML — `GET /campaigns/{id}/stats/content`:** Returns the actual HTML and plain text that was sent, including any link wrapping JangoMail applied at send time. Use this to verify click tracking was applied (see "Click Tracking Verification" below). Response shape:
```json
{
  "campaign_id": 399400061,
  "subject": "...",
  "text_content": "...",
  "html_content": "<!DOCTYPE html>..."
}
```

**v1 `GetCampaignDetails_XML` returns only 4 content fields:** JobId, SubjectLine, FromEmail, PlainTextMessage, HTMLMessage. No tracking configuration, no Options string, no recipient count — use v2 endpoints for those.

**Timestamps are UTC:** All `send_date`, `completed_date`, and stat timestamps in both v1 and v2 are UTC. Convert to ET (EDT = UTC-4 in summer, EST = UTC-5 in winter) before reporting to users.

```python
req = urllib.request.Request(f'{base}/campaigns/{campaign_id}/stats', headers=headers)
stats = json.loads(urllib.request.urlopen(req).read())
# Returns: {
#   "campaign_id": 399343647,
#   "subject": "...",
#   "recipients": 95,          # number actually sent to (after suppression removes)
#   "opens": 16,               # unique opens
#   "clicks": 0,               # unique clicks
#   "unsubscribes": 0,
#   "bounces": 19,             # hard + soft bounces
#   "complaints": 0,
#   "blocks": 3,               # SMTP-level blocks (separate from bounces)
#   "connection_fails": 0,
#   "removed_addresses": 5,    # pre-send suppression (global list, duplicates)
#   "links": { "opens": "/campaigns/{id}/stats/opens", ... }
# }
```

**Key distinction — blocks vs bounces vs removed:**
- `removed_addresses`: Pre-send — addresses suppressed from the global suppression list (previous unsubscribes, hard bounces from other campaigns). These never got a send attempt. Drill in with `GET /campaigns/{id}/stats/removed_addresses`.
- `blocks`: SMTP-level rejection during delivery attempt (e.g., "relay not permitted", "Recipient rejected — OXSUS001_403"). Drill in with `GET /campaigns/{id}/stats/blocks`.
- `bounces`: Mailbox-level rejection after SMTP acceptance (e.g., "mailbox does not exist", "user unknown"). Hard bounces have `hard_bounce: true`; soft bounces (like Office 365 "Access denied") have `hard_bounce: false`. Drill in with `GET /campaigns/{id}/stats/bounces`.

**Delivery math:** `recipients - bounces - blocks = delivered`. The `removed_addresses` were never in the `recipients` count to begin with — they were stripped before sending.

**Investigating missing recipients:** When a list has 100 but the campaign shows 95 recipients, 5 were removed pre-send. Check `removed_addresses` to identify them — they'll be under `"Global Suppression List"`. These should be permanently excluded from all future batches.

## Click Tracking Verification — Critical Pitfall

**JangoMail does NOT automatically wrap raw URLs in campaign HTML for click tracking.** If click tracking is not explicitly enabled at send time, all editorial links (source citations, Medium articles, case study PDFs, etc.) remain raw URLs pointing directly to their destinations. JangoMail's tracking domain (`track.scaleverticalwithai.com`) is only used for system links: unsubscribe (`/u.z`) and view-online (`/w.z`). The click-tracking redirect path is `/c.z` — if zero `/c.z` links appear in the sent HTML, click tracking was NOT applied and all click counts will be zero regardless of actual reader behavior.

**How to verify after sending:**
1. Pull sent content: `GET /campaigns/{id}/stats/content` (v2) — inspect `html_content`
2. Extract all `href` values via regex
3. Check for `/c.z` in any href — if absent, click tracking failed
4. Only system links (`/u.z`, `/w.z` with `***uniqueid****`) should go through the tracking domain when click tracking is off

**How to enable click tracking — v2 API ONLY:**
- **v2 `POST /campaigns` with `tracking.click_track_html: True`** is the ONLY method proven to track clicks. See the "Mandatory: Click Tracking on Every Campaign" section above for the exact payload. v2 wraps editorial links at SMTP delivery time using per-recipient hash-based URLs.
- **v1 `SendMassEmail` with `Options='TrackOpens,TrackClicks'`** does NOT wrap editorial links. Opens are tracked, clicks are not. Do not use v1 for campaigns requiring click tracking.
- **Manual `/c.z` wrapping is BROKEN — do NOT use.** The `/c.z` endpoint returns HTTP 500 with literal `***uniqueid****` and hangs with valid hashes. `***uniqueid****` is NOT replaced for `/c.z` URLs (only for `/u.z` and `/w.z` system links). Links may appear to redirect (because `u=` param has destination) but clicks are NOT registered in JangoMail reporting.

**Symptom:** 0 clicks across 100+ opens is almost always a tracking gap, not a real signal. Verify by sending a test via v2, clicking a link, and checking `GET /campaigns/{id}/stats/clicks` for a click record. If clicks=0 after a confirmed click, tracking is broken.

Full investigation method and findings: `references/jangomail-click-tracking-investigation.md`

## Reply Tracking — Not Natively Supported

**JangoMail does not track inbound replies.** The v2 API has zero reply-related endpoints (confirmed via swagger spec — 90+ paths, none mention replies). The v1 method `Reports_GetReplies_String` exists and accepts a `JobID` parameter, but returns empty even when replies may exist. Replies land in the reply-to inbox (`email@scaleverticalwithai.com`) and are invisible to JangoMail's reporting layer.

**Implication:** To check for replies, you must check the reply-to inbox directly (via IMAP/SMTP or a separate email client), not via JangoMail's API. Do not report "0 replies" as definitive based on JangoMail alone — always caveat that replies are not tracked by the platform.

## Campaign Discovery — Finding JobIDs by Group

There is no direct v1 or v2 endpoint to query "campaigns sent to group X." To find which campaigns targeted a specific group:

1. **List all v2 campaigns:** `GET /campaigns` (returns all, ~5-10 typically)
2. **Check each campaign's subject/content** via `GetCampaignDetails_XML` — match by known newsletter name (Protocol → "FDA Panel", People Person → "AI Firms", Green Room → "Long Tail")
3. **Pull stats** via `GET /campaigns/{id}/stats` to confirm the campaign was actually sent (`recipients > 0`)
4. **Cross-check status** with v1 `GetMassEmailStatus`

**Pitfall:** v2 campaigns created with `create_only: true` show up in the list but have `recipients: 0` and `GetMassEmailStatus: "Preprocessing"` — they were never sent. The actual sent campaign has a later (higher) `campaign_id`. This is the most common misidentification: confusing a draft campaign with the actual send.

**Finding "stuck in preprocessing" campaigns:** A campaign stuck in Preprocessing for hours means it was created as a draft in v2 but never pushed to send. The group members are still waiting. To fix: either send the existing campaign via `PUT /campaigns/{id}/send` or create a new one targeting the group.

**v1 `GetMassEmailReport_Multiple_String` is unreliable:** Despite accepting BeginDate/EndDate params, this method returns empty `<string />` even when campaigns exist on those dates. Do not rely on it for campaign discovery. Use v2 `GET /campaigns` + v1 `GetMassEmailStatus` instead.

**Newsletter resend workflow:** When resending a prior campaign's HTML to a new list (with minor edits like date changes), see `references/newsletter-resend-workflow.md` for the full step-by-step: pull prior HTML via `GetCampaignDetails_XML`, edit, create new group, import CSV, send via v1 `SendMassEmail`, verify, and schedule a +2hr stats cron.

§

**v1 `Reports_GetMassEmailInformation_String` SortBy trap:** This method requires both `SortBy` and `SortOrder` params. Most SortBy values (Date, Subject, JobId, Status, etc.) return "Invalid Option specified." The valid SortBy values are undocumented by JangoMail. Avoid this method for campaign discovery — use v2 REST instead.

## Account Usage / Plan Cap (v2 REST)

`GET /account/usage` returns plan usage — emails sent vs cap, bandwidth used.

```python
req = urllib.request.Request(f'{base}/account/usage', headers=headers)
usage = json.loads(urllib.request.urlopen(req).read())
# Returns: {"emails_allowed": 5000, "emails_sent": 214, "bytes_allowed": 500000000, "bytes_sent": 9333542}
```

Use this for "how many emails have we used against the plan cap" questions. The v1 methods `GetAccountUsage` and `GetEmailUsage` both return HTTP 500 (broken/unsupported) — use v2 only.

## Clone-Edit-Resend Workflow

When you need to re-send an existing campaign to a new list with text changes (e.g., updating the date, fixing tense):

1. **Pull the original campaign** via v1 `GetCampaignDetails_XML(JobId=..., Options="")`.
2. **Parse the XML** — the response has `<HTMLMessage>` and `<PlainTextMessage>` elements whose text content is **HTML-entity-escaped** (e.g., `&lt;`, `&amp;mdash;`). Use `html.unescape()` (Python `html` module) to decode before editing.
3. **Apply find-and-replace edits** to both the HTML and plain text. For Unicode characters like en-dashes (`–`, `\u2013`), match the actual character, not the `&ndash;` entity (the unescape step converts entities to characters).
4. **Sweep for related references** — if you changed a headline date, grep the full HTML for every instance of the old date phrase, "Thursday", "this week", present-tense verbs ("meets", "weighs") that reference the event. Fix tense throughout.
5. **Re-send via v1 `SendMassEmail`** with the modified HTML/plain, new subject line, and the new group name. This is more reliable than v2 `POST /campaigns` + `PUT /campaigns/{id}/send` for re-sending to a different list.
6. **The response** is `0\nSUCCESS\n{new JobID}` — a brand new campaign, fully independent of the original.

### Import Timing

- `ImportGroupMembersFromData` is async. For batches of 250 records, 15 seconds is reliably sufficient. For larger batches (500+), use 30s.
- Verify with `GetGroupMemberCount` after waiting. Cross-check via v2 `GET /lists` (look for `member_count` on the matching list).

## Account Usage / Quota

Check email usage against plan cap via v2 REST:

```python
req = urllib.request.Request(f'{base}/account/usage', headers=headers)
usage = json.loads(urllib.request.urlopen(req, timeout=10).read())
# Returns: {"emails_allowed": 5000, "emails_sent": 464, "bytes_allowed": 500000000, "bytes_sent": 9333542}
```

The v1 methods `GetAccountUsage` and `GetEmailUsage` both return HTTP 500 — use v2 `/account/usage` instead.

## HTML Edit + Resend Workflow (Re-sending a Newsletter to a New List)

When re-sending an existing newsletter campaign to a different lead list with minor edits (date change, tense fix, etc.):

1. **Pull original HTML** via v1 `GetCampaignDetails_XML` — parse XML, unescape HTML entities from `HTMLMessage` and `PlainTextMessage` fields
2. **Apply text edits** with string replacement — search for exact strings, count occurrences before and after to verify
3. **Sweep for related references** — after targeted fixes, regex-scan for related terms (e.g., "Thursday", "this week", present-tense verbs) that refer to the same event but weren't in the explicit fix list
4. **Upload CSV as new JangoMail group** — `AddGroup` → `ImportGroupMembersFromData` (field names: `EmailAddress,FirstName,LastName,CompanyName`) → wait 15s → verify `GetGroupMemberCount`
5. **Send via v1 `SendMassEmail`** — pass the modified HTML/plain text, new group name, new subject line. ALL params required including empty `ToGroupFilter`, `ToOther`, `ToWebDatabase`.
6. **Verify recipient count** via v2 `GET /campaigns/{id}/stats` — `recipients` should match group member count
7. **Stagger multiple sends** — 8-10 minutes between SendMassEmail calls. JangoMail queues sequentially so actual inbox delivery staggers further.

### HTML Entity Handling

The v1 `GetCampaignDetails_XML` response has double-escaped HTML:
- XML parses to escaped strings (e.g., `&lt;html&gt;`)
- Use `html.unescape()` to get the actual HTML
- HTML entities like `&middot;` and `&ndash;` are preserved in the unescaped output
- When replacing strings, match the exact entity-encoded form (e.g., `&middot;` not `·`)

### Spam Complaints on Re-sends

When re-sending to a new list of the same vertical, watch for spam complaints in the first 30 minutes. A complaint rate above 0.4% (1 per 250) on a fresh verified list may indicate the content triggers spam filters, not a list quality issue. Check mail-tester score if complaints appear.

## Account Usage

**GET** `https://api-v2.jangomail.com/account/usage` (Basic Auth)

```json
{
  "emails_allowed": 5000,
  "emails_sent": 464,
  "bytes_allowed": 500000000,
  "bytes_sent": 9333542
}
```

The v1 methods (`GetAccountUsage`, `GetEmailUsage`) return HTTP 500 — use the v2 endpoint instead. The v2 `/account` endpoint returns user/company info but NOT usage counts; `/account/usage` is the correct path.

## Sending a Test Email (Single Recipient)

**Use `SendTransactionalEmail` (v1), NOT `SendMassEmail`.** `SendMassEmail` returns HTTP 500 when `ToOther` has a single recipient and `ToGroups` is empty. `SendTransactionalEmail` works reliably for one-off test sends:

```python
status, body = jango('SendTransactionalEmail',
    FromEmail='email@scaleverticalwithai.com',
    FromName='Scale Vertical AI',
    ToEmailAddress='justin@usingaitoscale.com',
    Subject='🎯 Test Subject',
    MessagePlain=plain_content,
    MessageHTML=html_content,
    Options='TrackOpens,TrackClicks')
# Returns: "0\nSUCCESS\n{TransactionalID}"
```

## Campaign Reuse Workflow (v1 HTML → v2 Re-send with Click Tracking)

When re-sending an existing campaign's HTML to a new list via the **v2 API with click tracking** (the only method that tracks editorial link clicks):

1. **Pull original HTML via v1** `GetCampaignDetails_XML(JobId=..., Options="")` — parse XML, `html.unescape()` the `HTMLMessage` and `PlainTextMessage` fields. This gives you the RAW HTML with unwrapped editorial links.
2. **Do NOT use the v2 `stats/content` endpoint** to pull HTML for reuse — if the original was sent via v2 with click tracking, the stored content shows link-wrapped HTML (tracking URLs instead of raw editorial URLs). You need the raw links so v2 can wrap them fresh at delivery time.
3. **Create new campaign via v2** `POST /campaigns` with `tracking.click_track_html: true`, `create_only: true` (draft), and the raw HTML from step 1.
4. **Send via** `PUT /campaigns/{id}/send` — may return HTTP 204 (success, no body) or 400 (race condition — check campaign status to confirm it actually sent).
5. **Verify click tracking was applied**: After send completes, check `GET /campaigns/{id}/stats/content` — tracked links will contain `track.scaleverticalwithai.com/c.z?***uniqueid****&u=...`. If links are still raw, the tracking setting wasn't saved (rare).
6. **Spam score** is available in `GET /campaigns/{id}` response under `spam_score.score` — values below 0 are good (negative = less spammy).

### v2 Send Response Codes
- `204 No Content` — send queued successfully (confirmed Jul 29, 2026)
- `400 Bad Request` with empty body — race condition; campaign may have sent anyway. Check `GET /campaigns/{id}` for `status: "Sending"` or `"Complete"`.
- `400` with error JSON — genuine failure. Read the error message.

### Account Usage Check (Pre-send)
Before sending a batch, verify remaining capacity:
```python
req = urllib.request.Request(f'{base}/account/usage', headers=headers)
usage = json.loads(urllib.request.urlopen(req, timeout=10).read())
remaining = usage['emails_allowed'] - usage['emails_sent']
# Also check bandwidth: bytes_allowed - bytes_sent
```

## Newsletter HTML Preparation Workflow

When building a campaign from an external HTML file (e.g., from a zip), these steps are required before sending. Full end-to-end sequence documented in `references/newsletter-send-workflow.md`.

1. **Fix Windows backslash paths** — Zips from Windows may extract with literal `images\s0.jpg` as a single filename. Rename to proper `images/s0.jpg` directory structure.
2. **Upload images to JangoMail CDN** — Use `POST /files` (v2) with `contents_base64`. Files must have unique names — re-uploading returns 400 "File already exists". Use a timestamp prefix if re-uploading.
3. **Replace relative image paths** — Change `src="images/s0.jpg"` to `src="https://img.jangomail.com/2606407/Images/{prefix}-s0.jpg"`.
4. **Replace template placeholders** — Newsletter templates may use `{{UNSUBSCRIBE_LINK}}` and `{{VIEW_ONLINE_LINK}}`. Replace with JangoMail tracking URLs:
   - `{{UNSUBSCRIBE_LINK}}` → `https://track.scaleverticalwithai.com/u.z?***uniqueid****`
   - `{{VIEW_ONLINE_LINK}}` → `https://track.scaleverticalwithai.com/w.z?***uniqueid****`
5. **Date updates** — Find/replace any stale byline dates before sending.
6. **Generate plain text** — Strip HTML tags, decode entities, collapse whitespace. Required by `SendMassEmail`'s `MessagePlain` parameter.
7. **Verify** — Check that `***uniqueid****` placeholders are present (JangoMail replaces these per-recipient), physical address is in the footer, and no `{{...}}` placeholders remain.

## Image Upload — urllib vs curl

Python `urllib.request` may silently fail on `POST /files` (returns empty response → `JSONDecodeError`). Use **curl** for image uploads:

```bash
AUTH=$(echo -n "UsingAIToScale:Jango123!" | base64 -w0)
python3 -c "import json,base64; ..."
curl -s -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" \
  -d @/tmp/payload.json "https://api-v2.jangomail.com/files"
```

List existing uploaded files via `GET /files` (v2) to check for duplicates and find previously uploaded image URLs.

## Image CDN Cache-Busting (Critical)

JangoMail's image hosting (`img.jangomail.com/2606407/Images/`) serves stale cached versions when you reuse filenames. If you upload `pp-s0.jpg` and it already exists from a previous campaign, JangoMail returns "File already exists" on re-upload — but even if you delete and re-upload, the CDN edge cache may continue serving the OLD image for hours.

**Rules:**
1. **Always use unique filenames** for every upload — append a timestamp or version suffix: `pp-v3-{timestamp}-s0.jpg`, never reuse `pp-s0.jpg` across versions
2. **Never assume re-uploading to the same filename refreshes the CDN** — it does not. The upload API says "File already exists" (400) before you even get to re-upload
3. **When a user says "wrong images rendered," it's almost always stale CDN cache** — the fix is new filenames, not re-uploading
4. **Verify image identity before sending** — compare file sizes between versions. If v2's `s5.jpg` is 22,723 bytes and v3's is 30,611, the files are confirmed different. Same-size files are likely identical

**Upload method:** Python `urllib.request` silently fails on JangoMail's `POST /files` — the upload succeeds server-side but `urlopen()` returns an empty response, causing `JSONDecodeError`. Use **curl** for all image uploads, or construct the URL from the known pattern (`https://img.jangomail.com/2606407/Images/{filename}`) when urllib returns empty but HTTP 200.

## SendTransactionalEmail for Test Sends

`SendMassEmail` returns HTTP 500 when `ToGroups` is empty and `ToOther` contains a single address. For one-off test sends (mail-tester, seed inbox, approval copy), use **`SendTransactionalEmail`** instead:

```python
jango('SendTransactionalEmail',
    FromEmail='email@scaleverticalwithai.com',
    FromName='Scale Vertical AI',
    ToEmailAddress='test-xxx@srv1.mail-tester.com',
    Subject='🎯 Subject Line',
    MessagePlain=plain_text,
    MessageHTML=html_content,
    Options='TrackOpens,TrackClicks')
# Returns: "0\nSUCCESS\n{TransactionalID}"
```

This works reliably for single-recipient sends. `SendMassEmail` is only for group/list sends.

## Mail-Tester Broken Links: False Positives

Mail-tester's link checker crawls URLs server-side. Sites with bot protection (Medium, news sites, etc.) return 403 to the crawler but work fine for real human readers. This costs -1 point per broken link but is **not a real problem**:

- `medium.com/@...` → 403 Forbidden (bot detection, works in browser)
- `gethrbrief.com/story/...` → 403 Forbidden (same)
- Other news/blog sites with Cloudflare or bot protection

Do not chase these. The links work when recipients click them. A 9/10 with only "broken links" deductions from bot-protected sites is effectively a 10/10.

## Newsletter HTML Pre-Processing: Placeholder Replacement

Newsletter HTML from external builders (zip archives) arrives with template placeholders, not JangoMail tracking URLs. Three replacements are always needed before sending:

| Placeholder | Replace With |
|---|---|
| `{{UNSUBSCRIBE_LINK}}` | `https://track.scaleverticalwithai.com/u.z?***uniqueid****` |
| `{{VIEW_ONLINE_LINK}}` | `https://track.scaleverticalwithai.com/w.z?***uniqueid****` |
| `src="images/sN.jpg"` | `https://img.jangomail.com/2606407/Images/{unique-filename}.jpg` |

After replacement, verify: zero `{{` remaining, zero `images/s` remaining, correct count of `***uniqueid****` (should be 2 per link type = 4 total for unsubscribe + view online).

## Newsletter HTML: Date Corrections

Newsletter packages often arrive with a stale byline date from when the issue was drafted. Always check for and correct the date before sending. The date appears in the masthead byline as plain text (e.g., "By The Protocol · Thursday, July 23, 2026") — replace with the actual send date.

Also sweep the entire HTML for tense issues when the date changes — if the content references "this week" or "Thursday" in body text relative to the old date, those need updating too (e.g., "meets July 23-24" → "met July 23-24", "this week" → "last week", "Thursday" → "last Thursday").

## Mandatory: Click Tracking on Every Campaign

**Click tracking is mandatory on ALL campaigns.** Without it, editorial links in newsletters are sent as raw URLs and clicks are invisible in reporting.

### CRITICAL: Only v2 API supports click tracking. v1 SendMassEmail does NOT.

Tested extensively on July 28, 2026. Results:

| Method | Click Tracked? | Details |
|---|---|---|
| v1 `SendMassEmail` with `Options='TrackOpens,TrackClicks'` | ❌ NO | v1 does NOT wrap editorial links at delivery time. Links stay raw. Opens tracked, clicks not. |
| v2 `POST /campaigns` with `tracking.click_track_html: True` + `PUT /campaigns/{id}/send` | ✅ YES | v2 wraps editorial links at SMTP delivery time. Stored HTML shows raw links (expected — wrapping happens at send time, not in template). Clicks tracked with email, IP, user agent, timestamp, link position. |
| Manual `/c.z?***uniqueid****&u=URL` wrapping via v1 | ❌ NO | `/c.z` is NOT a valid JangoMail endpoint (times out). `***uniqueid****` is NOT replaced for `/c.z` URLs (only for `/u.z` and `/w.z` system links). Links redirect (because `u=` param has destination) but clicks NOT registered. Do NOT use this approach. |

### Correct approach (MANDATORY for all campaigns):

```python
# v2 campaign creation with click tracking
campaign_data = {
    'from': {'email': 'email@scaleverticalwithai.com', 'name': 'Scale Vertical AI'},
    'subject': 'Subject line',
    'message_html': raw_html_with_editorial_links,  # RAW links, do NOT manually wrap
    'message_plain': plain_text,
    'to_lists': [{'id': list_id}],  # or to_other for single recipients
    'tracking': {
        'click_track_html': True,   # THIS IS THE KEY — enables SMTP-level link wrapping
        'track_opens': True
    },
    'character_set': 'UTF-8',
    'encoding': 'Quoted Printable',
    'create_only': False  # Send immediately (or True to create draft)
}
# POST /campaigns → returns campaign_id
# PUT /campaigns/{id}/send → triggers send
```

### Key rules:
1. **Use v2 API only** for campaigns requiring click tracking. v1 SendMassEmail does NOT wrap editorial links.
2. **Use RAW editorial links** in the HTML — do NOT manually wrap them. v2's pre-processor wraps links at SMTP delivery time (per-recipient, using hash-based tracking URLs, not `***uniqueid****`).
3. **Set `tracking.click_track_html: True`** in the v2 campaign creation payload. If omitted, click tracking is disabled.
4. **Stored HTML will show raw links** — this is expected. The wrapping happens at delivery time, not in the stored template. Verify by checking `GET /campaigns/{id}/stats/clicks` after recipients click.
5. **Do NOT use `/c.z` manual wrapping** — this endpoint does not exist in JangoMail and will prevent tracking.

### How v2 click tracking works:
When `click_track_html: True` is set, JangoMail's SMTP pre-processor rewrites all `href` URLs in the HTML at send time, wrapping them through `track.scaleverticalwithai.com` with per-recipient hash-based tracking URLs (similar to the `j=HASH&m=HASH` format used by `/w.z` view-online links). The stored template remains unchanged — wrapping is only in the delivered email.

### Pre-send verification:
After creating the campaign via v2 (before or after sending), verify click tracking is enabled:
- Pull `GET /campaigns/{id}` and check that `tracking.click_track_html` is present
- After send, check `GET /campaigns/{id}/stats/clicks` — if recipients have clicked, click records will appear with email, IP, timestamp, and link position
- The stored content (`GET /campaigns/{id}/stats/content`) will show RAW editorial links — this is normal and does NOT indicate a problem

Full investigation log (3 methods tested, root cause analysis, v1 vs v2 comparison): see `references/jangomail-click-tracking-investigation.md`

### Known Issues

## Known Issues

- **Method names (v1):** Use PascalCase with underscores (e.g., `SendTransactionalEmail`, `Groups_GetList_String`). Hyphenated names don't work.
- **v1 SendMassEmail requires all params:** `ToGroupFilter`, `ToOther`, `ToWebDatabase` must ALL be passed (even as empty strings). Missing any returns "Missing parameter" — see Mass Email section for working example.
- **v1 ImportGroupMembersFromData field name:** The email column must be `EmailAddress` (not `Email`). Using `Email` returns `InvalidGroupFieldsException`.
- **v2 list creation:** Use lowercase `name` field: `{"name": "list-name"}`. The `GET /lists/new` schema shows uppercase `Name` but API only accepts lowercase `name`.
- **v2 campaign `to_lists`:** Use `[{"id": list_id}]` format (key is `id`, not `list_id`). `PUT /campaigns/{id}` with updated `to_lists` is unreliable — prefer v1 `SendMassEmail` with `ToGroups='group-name'` for sending to lists.
- **v2 campaign send returns 400 but works:** `PUT /campaigns/{id}/send` may return HTTP 400 with empty body, but the campaign may still send. Check `GET /campaigns/{id}` for `status: "Sending"` before assuming failure.
- **WSDL:** Full WSDL at `https://api.jangomail.com/api.asmx?WSDL` — 1,435 operations documented.
- **bcrypt auth outage (Jul 14-16 2026, RESOLVED):** There was a .NET Framework `bcrypt` assembly loading error affecting all auth paths — v1 SOAP, v2 REST, and SMTP relay. This was resolved as of Jul 16 2026. If auth fails again with `FileLoadException`, check the JangoMail site for a banner before assuming credentials are wrong.
- **Dashboard vs API credentials:** The WordPress login on jangomail.com is a separate user system from the JangoMail API account. API credentials do not work for WordPress login. `app.jangomail.com` returns 403. If UI access is needed, the actual dashboard URL may differ from both — check jangomail.com homepage for current login link.
- **Large payload urllib pitfall:** When uploading files >~100KB via `urllib.request` to `POST /files`, the upload may succeed server-side but `urlopen()` returns an empty response (causing `JSONDecodeError`). Use curl with `-d @payload.json` instead for large uploads. See File & Image Hosting section above for the curl recipe.
- **SMTP section credentials:** The username/password documented in the SMTP Relay section above are the same credentials for v1 and v2 API access — not SMTP-only.
- **v1 bounce/unsubscribe/complaint report param names:** Use `JobID` not `CampaignID`. `Reports_GetBouncesByCampaign_String`, `Reports_GetUnsubscribesByCampaign_String`, and `Reports_GetComplaintsByCampaign_String` all take `JobID`. Passing `CampaignID` returns "Missing parameter: JobID."
- **v1 `Reports_GetComplaintsByCampaign_String` requires SortBy:** Unlike the bounces and unsubs report methods, the complaints report requires `SortBy` and `SortOrder` params. Omit them and get "Missing parameter: SortBy."
- **v1 `GetMassEmailReport_Multiple_String` returns empty:** Accepts BeginDate/EndDate params and returns HTTP 200, but the response body is always `<string />` (empty) even when campaigns exist on those dates. Do not use for campaign discovery.
- **v1 `Reports_GetMassEmailInformation_String` SortBy is undocumented:** Requires both SortBy and SortOrder, but nearly all intuitive SortBy values (Date, Subject, JobId, Status, etc.) return "Invalid Option specified." Valid values are undocumented by JangoMail. Avoid this method.
- **No native reply tracking:** JangoMail does not track inbound replies. The v2 API has zero reply-related endpoints (confirmed via swagger). The v1 method `Reports_GetReplies_String` accepts `JobID` but returns empty even when replies may exist. Replies land in the reply-to inbox (`email@scaleverticalwithai.com`), invisible to JangoMail's reporting. Never report "0 replies" as definitive — always caveat and check the inbox directly via IMAP if reply tracking matters.
- **v2 `GET /campaigns/{id}/stats/content` endpoint:** Returns the actual sent HTML (`html_content`) and plain text (`text_content`) including any link wrapping. Not in the swagger summary but confirmed working. Use to verify click tracking was applied (check for `/c.z` in hrefs). See "Click Tracking Verification" section.
- **v1 `GetCampaignDetails_XML` returns only 4 content fields:** JobId, SubjectLine, FromEmail, PlainTextMessage, HTMLMessage. No tracking config, no Options string, no recipient count. Use v2 endpoints for those.
- **All timestamps are UTC:** Both v1 and v2 return timestamps in UTC. Convert to ET (EDT = UTC-4 summer, EST = UTC-5 winter) before reporting to users.
- **Click tracking — v2 API only, no manual wrapping:** JangoMail does NOT auto-wrap editorial URLs when using v1 SendMassEmail (proven Jul 28, 2026). v2 API with `tracking.click_track_html: True` is the ONLY method that tracks clicks — it wraps links at SMTP delivery time. Manual `/c.z` wrapping is BROKEN: `/c.z` returns 500, `***uniqueid****` is NOT replaced for `/c.z` URLs, clicks not registered. Do NOT manually wrap links. Use v2 API with raw editorial links. See "Mandatory: Click Tracking" section and `references/jangomail-click-tracking-investigation.md`.
