---
name: vapi
description: Vapi voice AI platform — outbound calls, assistants, phone numbers. Used for SDR voice follow-up after emails. Bearer token auth.
version: 1.0.0
metadata:
  hermes:
    tags: [vapi, voice, calls, sdr, outbound, phone]
---

# Vapi Voice AI

Vapi is a voice AI platform for making and receiving AI-powered phone calls. Used here for SDR outbound call follow-up after JangoMail emails.

**Base URL:** `https://api.vapi.ai`
**Auth:** `Authorization: Bearer <VAPI_API_KEY>`
**Content-Type:** `application/json`

## Environment Variables

| Variable | Required | Notes |
|----------|----------|-------|
| `VAPI_API_KEY` | Yes | From Vapi dashboard → Settings → API Keys |
| `VAPI_PHONE_NUMBER_ID` | No | Default outbound phone number ID |

Store credentials in `.env` — never in memory, skills, or logs.

## Quick Start — Python Helper

```python
import urllib.request, json, os

VAPI_KEY = os.environ['VAPI_API_KEY']
VAPI_BASE = 'https://api.vapi.ai'

def vapi(method, path, body=None):
    """Call Vapi API."""
    url = f'{VAPI_BASE}{path}'
    headers = {
        'Authorization': f'Bearer {VAPI_KEY}',
        'Content-Type': 'application/json',
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
```

## Common Operations

### List Phone Numbers

```python
status, data = vapi('GET', '/phone-number')
for pn in data:
    print(f"{pn['id']}: {pn['number']} ({pn.get('provider', '?')})")
```

### List Assistants

```python
status, data = vapi('GET', '/assistant')
```

### Create Outbound Call

```python
status, data = vapi('POST', '/call', {
    'assistantId': 'assistant-id-here',
    'customer': {
        'number': '+15551234567',
        'name': 'Prospect Name',
    },
    'phoneNumberId': os.environ.get('VAPI_PHONE_NUMBER_ID', 'phone-number-id-here'),
})
# Returns call object with 'id' for tracking
```

### Get Call Details

```python
status, data = vapi('GET', f'/call/{call_id}')
print(f"Status: {data.get('status')}, Duration: {data.get('duration')}s")
```

### End Active Call

```python
status, data = vapi('PATCH', f'/call/{call_id}', {'status': 'ended'})
```

## SDR Workflow: Email → Voice Follow-Up

When an SDR has sent a JangoMail email and wants to follow up with a call:

1. **Prepare context** — gather prospect name, company, email content
2. **Create assistant** (or use existing) — configure with SDR script/persona
3. **Initiate call** — `POST /call` with customer number
4. **Monitor** — check call status and transcript
5. **Log result** — capture disposition (connected, voicemail, no answer, etc.)

```python
# Full SDR outreach flow
def sdr_outreach(prospect_name, prospect_phone, prospect_email, 
                 company_name, email_subject, assistant_id=None):
    # 1. Send email via JangoMail (use jangomail-api skill)
    # 2. Initiate Vapi call
    call = vapi('POST', '/call', {
        'assistantId': assistant_id,
        'customer': {
            'number': prospect_phone,
            'name': prospect_name,
        },
        'phoneNumberId': os.environ['VAPI_PHONE_NUMBER_ID'],
    })
    return call
```

## Setup Needed

Before Vapi works, the user must:
1. Create a Vapi account and get API key
2. Purchase/configure a phone number in Vapi
3. Create an assistant with the SDR calling script
4. Set `VAPI_API_KEY` and `VAPI_PHONE_NUMBER_ID` in `.env`
