---
name: retell-ai
description: "Retell AI voice SDR fleet: agents, calls, phone numbers, campaigns via REST API."
version: 1.0.0
author: jbellsolutions
license: MIT
metadata:
  hermes:
    tags: [Retell, Voice AI, SDR, Sales, Call Center, API]
    homepage: https://docs.retellai.com
prerequisites:
  env_vars: [RETELL_API_KEY]
---

# Retell AI — SDR Voice Agent Fleet

Justin's AI call center for lead generation and sales outreach.

## Auth

```python
headers = {
    "Authorization": f"Bearer {os.environ['RETELL_API_KEY']}",
    "Content-Type": "application/json"
}
```

Base URL: `https://api.retellai.com`

## Current Fleet

### 17 Agents (key ones)

**Sales — "Using AI To Scale" brand:**
| Agent | Direction | Voice | ID |
|---|---|---|---|
| Sales Agent (Inbound) | Inbound | Kate | agent_24b1bc9bf66f297c4892d50b0d |
| Sales Agent (Outbound) | Outbound | Nina | agent_79ccddf5eab966fa22c7a30a5c |
| SMS Sales Agent (Inbound) | Inbound | Kate | agent_7710150200bd8cd4ba383c7eb0 |
| SMS Sales Agent (Outbound) | Outbound | Kate | agent_f00974c179aac337a1ef922487 |
| Cold Email Sales Agent (Inbound) | Inbound | Kate | agent_68c0920c4ddd8192f4cb316540 |

**Lead Qualification:**
| Agent | Voice | ID |
|---|---|---|
| Lead Qual (Multi-Prompt) | Anna | agent_173c23b0e989fa3502060684cd |
| Lead Qual (Multi-Prompt) v2 | Anna | agent_48a22c2379ea3437fca998f5ad |

**Recruiter:**
| Agent | Direction | Voice | ID |
|---|---|---|---|
| Recruiter (Outbound) | Outbound | Marissa | agent_b350ccdcddc1340118c350e8f9 |
| Recruiter (Inbound) | Inbound | Marissa | agent_29e386e62f1ecbb2ad8c5aea56 |

**Insurance:**
| Agent | Direction | Voice | ID |
|---|---|---|---|
| Jill (Outbound Life Insurance) | Outbound | Paola | agent_9971f8735f90d8ab8b4ac6825c |
| Jill (Inbound Life Insurance) | Inbound | Paola | agent_0e81e6d0eb36d1faa92cbcea82 |

**Original / Template:**
| Agent | Voice | ID |
|---|---|---|
| Outbound Agent Jessica | Marissa | agent_284994846ca161571e6e08a415 |
| Inbound Agent Alex | Marissa | agent_8b03554b4e42ff961319b0c2d4 |
| Dental Outbound Sales | Grace | agent_3e68361fb82c2b4dcd6ae47b5e |
| Conversation Flow Agent (x2) | Cimo | agent_fc25381e19.../agent_efb3a090cd... |
| Single-Prompt Agent | Myra | agent_0cf571ae36f80433f34810975e |

### Phone Numbers (5)
- +18135475969 → HVAC Florida - Outbound (retell-twilio, purchased via API May 11)
- +168****3833 → SMS Sales Agent (Inbound)
- +168****3116 → SMS Sales Agent (Inbound)
- +131****1299 → Unassigned (retell-twilio, not recognized by outbound API)
- +181****0921 → Unassigned (retell-telnyx, not recognized by outbound API)

### HVAC Florida Outbound Agent
- **Agent ID:** agent_c690451e9e4c0a5cfccfb5a4af
- **Voice:** 11labs-Nina
- **LLM ID:** llm_867e07843974ce80446716f928b6
- **Phone:** +18135475969
- **Booking link:** https://cal.com/usingaitoscale/aiintegraterz

### LLMs: 19 configured (mostly GPT-4.1 and GPT-4.1-mini)

## API Operations

### Phone Number Management

```python
# LIST v2 phone numbers (returns full details with agent assignments)
req = urllib.request.Request(f"{BASE}/v2/list-phone-numbers", method='GET', headers=headers)

# CREATE a new Twilio voice number (works via v1 endpoint)
payload = {"area_code": 813, "inbound_agent_id": "agent_xxx", "outbound_agent_id": "agent_xxx"}
req = urllib.request.Request(f"{BASE}/create-phone-number", data=json.dumps(payload).encode(), method='POST', headers=headers)
# Returns: phone_number, phone_number_pretty, inbound/outbound agent assignments

# UPDATE v2 phone number
payload = {"inbound_agent_id": "agent_xxx", "outbound_agent_id": "agent_xxx"}
encoded = urllib.parse.quote("+18135475969", safe='')
req = urllib.request.Request(f"{BASE}/v2/update-phone-number/{encoded}", data=json.dumps(payload).encode(), method='PATCH', headers=headers)
```

### Make an Outbound Call

```python
# POST /v2/create-phone-call
# The from_number must be a phone number owned by your Retell account
# Use the FULL E.164 format: +18135475969 (NOT just digits or masked format)
payload = {
    "from_number": "+18135475969",
    "to_number": "+13051234567",
    "override_agent_id": "agent_c690451e9e4c0a5cfccfb5a4af",
    "retell_llm_dynamic_variables": {
        "prospect_name": "Paul",
        "company_name": "Watsco Inc",
        "market_type": "coastal"
    }
}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(f"{BASE}/v2/create-phone-call", data=data, method='POST', headers=headers)
```

### List/Get Calls

```python
# POST /v2/list-calls
payload = {"limit": 50, "sort_order": "descending"}
# Filter by agent: "filter_criteria": {"agent_id": ["agent_xxx"]}
req = urllib.request.Request(f"{BASE}/v2/list-calls", data=json.dumps(payload).encode(), method='POST', headers=headers)
# Returns: items with call_id, call_type, call_status, agent_name, retell_llm_dynamic_variables, start_timestamp, duration
```

### Create an Agent

### Update an LLM

```python
# PATCH /update-retell-llm/{llm_id}
payload = {"model": "gpt-4.1", "general_prompt": "...", "begin_message": "...", "general_tools": [...]}
req = urllib.request.Request(f"{BASE}/update-retell-llm/{llm_id}", data=json.dumps(payload).encode(), method='PATCH', headers=headers)
```
# POST /list-calls (note: POST not GET)
{
    "limit": 50,
    "sort_order": "descending",
    "filter_criteria": {
        "agent_id": ["agent_xxx"],
        "call_type": ["outbound"],
        "after_start_timestamp": 1717100000000,
        "before_start_timestamp": 1717200000000
    }
}

# GET /get-call/{call_id}  — full transcript, analysis, recording
```

### Get Call Recording
```python
# GET /get-call/{call_id}
# Response includes: recording_url, transcript, call_analysis, metadata
```

### Phone Numbers
```python
# POST /create-phone-number  {"area_code": "212", "inbound_agent_id": "agent_xxx"}
# GET /list-phone-numbers
# GET /v2/list-phone-numbers  (returns outbound_agent_id, agent assignments)
# PATCH /update-phone-number/{phone_id}  — UNRELIABLE, IDs not exposed in list response
# DELETE /delete-phone-number/{phone_id}
```

**Purchasing a new number:** The v1 `POST /create-phone-number` endpoint WORKS and is the only programmatic way to get a voice-capable outbound number. Existing numbers listed in the API may not work for outbound voice calls — they often need dashboard configuration for Telnyx/Twilio voice enablement.

```python
payload = {
    "area_code": 813,
    "inbound_agent_id": "agent_xxx",
    "outbound_agent_id": "agent_xxx"
}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(f"https://api.retellai.com/create-phone-number", 
                              data=data, method='POST', headers=headers)
```

**Key discovery (May 11, 2026):** Numbers purchased this way appear as `phone_number_type: retell-twilio` and work for outbound calling immediately via `v2/create-phone-call`. Existing numbers in the account (purchased via dashboard) returned `"Item +1XXX not found from phone-number"` even when assigned to the correct agent. New numbers purchased via API bypass this.

### Update Agent
```python
# PATCH /update-agent/{agent_id}
{"agent_name": "New Name", "voice_id": "11labs-Nina"}
```

### Update LLM
```python
# PATCH /update-retell-llm/{llm_id}
{"general_prompt": "Updated prompt...", "model": "gpt-4.1"}
```

## Outbound Call Setup Checklist

1. **Check phone numbers** — `GET /v2/list-phone-numbers`. Confirm numbers have `phone_number_type: retell-telnyx` and are configured for outbound in the Retell dashboard.
2. **Create LLM** — `POST /create-retell-llm` with `general_prompt`, `begin_message`, and `general_tools`.
3. **Create agent** — `POST /create-agent` linking the LLM via `response_engine.llm_id`. Use `voice_id: "11labs-Nina"` for outbound.
4. **Assign phone to agent** — Must be done in the Retell dashboard UI (API assignment unreliable for Telnyx numbers). Go to Phone Numbers → click number → assign outbound agent.
5. **Build and fire batch calls** — `POST /v2/create-phone-call` (singular) with 50 calls max per request. Use `override_agent_id` if the phone's default agent differs.

### Outbound Call API (v2)

```python
# POST /v2/create-phone-call
{
    "from_number": "+18131234567",          # must be a phone number configured for outbound in dashboard
    "to_number": "+13035551234",
    "override_agent_id": "agent_xxx",       # optional: use this agent instead of phone's default
    "retell_llm_dynamic_variables": {       # optional: injected into LLM prompt as {{var_name}}
        "prospect_name": "John",
        "company_name": "Acme Inc",
        "market_type": "coastal"
    }
}
```

**Batch calls:** No dedicated batch endpoint in v2. Loop `create-phone-call` individually (50 max per batch, add 1-2s delay between calls).

### LLM Tool Schema

Retell uses oneOf validation for `general_tools`. Only these tool types are supported:

| Type | Required fields | Notes |
|---|---|---|
| `end_call` | `name`, `type` | Simple call termination |
| `transfer_call` | `name`, `type` — complex schema | Rarely works via API — use dashboard |
| `check_availability_cal` | `cal_api_key`, `event_type_id` | Cal.com integration |
| `book_appointment_cal` | `cal_api_key`, `event_type_id`, `cal_fields` | Cal.com booking |
| `custom` | `url`, `parameters` | Webhook for custom actions |
| `press_digit` | — | DTMF-based IVR |

When creating an LLM via API, start with `end_call` only and layer in other tools through the dashboard UI.

### v1 vs v2 API

| Endpoint | v1 | v2 |
|---|---|---|
| Create call | ❌ `/create-phone-call` (404) | ✅ `/v2/create-phone-call` |
| Batch create | ❌ `/batch-create-phone-call` (404) | ❌ No batch endpoint — loop singles |
| List calls | ❌ (no endpoint) | ✅ `POST /v2/list-calls` |
| List phone numbers | ✅ `GET /list-phone-numbers` | ✅ `GET /v2/list-phone-numbers` |
| Update phone number | ❌ `PATCH /update-phone-number/{id}` (no ID in response) | ❌ No update endpoint |
| Create phone number | — | ❌ No create endpoint |

**Rule:** Use v2 for call operations, v1 for LLM/agent management. Phone number configuration requires the Retell dashboard.

1. **Define ICP** — who are we calling
2. **Build/clone agent** — pick voice, write prompt with dynamic variables
3. **Import lead list** — names, numbers, company, personalization
4. **Assign phone number** — use unassigned numbers or buy new
5. **Batch call** — schedule or fire immediately
6. **Monitor** — pull call logs, transcripts, outcomes
7. **Route to Notion** — log results in Clients DB (leads) + Tasks (follow-ups)
8. **Iterate** — refine prompt based on call transcripts

## Notion Integration

All call outcomes should be logged:
- **New leads** → Clients DB (Status: Lead, Source: Retell)
- **Follow-up tasks** → Tasks DB (Source: Agent, linked to Client)
- **Call logs** → Agent Logs DB (Agent: Retell SDR, Action: outbound_call)
- **Campaign metrics** → Intel Briefings DB (Type: Daily, campaign stats)

## Pitfalls
- **Phone numbers must be outbound-configured in the Retell dashboard** — Even if a number appears in `list-phone-numbers`, it may not work for outbound calls. Numbers listed as `phone_number_type: retell-telnyx` need explicit outbound enablement in the Retell dashboard UI. The API cannot configure this. Error: `"Item +1XXX not found from phone-number"` means the number isn't recognized by the outbound call system. **Workaround:** Purchase a new number via `POST /create-phone-number` — API-purchased Twilio numbers work for outbound immediately.
- **Phone number IDs are NOT exposed in API responses** — Both v1 and v2 `list-phone-numbers` return phone objects without an `id` or `phone_number_id` field. Use the `phone_number` string (E.164 format) directly in API calls.
- **Booking links must use FULL Cal.com URLs** — Never direct prospects to a bare domain like `usingaitoscale.com`. Always use the full Cal.com URL (e.g., `https://cal.com/usingaitoscale/aiintegraterz`). Justin was explicitly frustrated by this mistake (May 11, 2026). The LLM prompt must contain the complete URL in every call-to-action.
- **Create phone number endpoint is v1 only** — `POST /create-phone-number` (no version prefix) works. `POST /v2/create-phone-number` returns 404.
- **Outbound calling uses v2** — `POST /v2/create-phone-call` is the only working call endpoint. v1 returns 404.
- **to_number must be full E.164 format** — `+1XXXXXXXXXX` (12 characters including +). Numbers scraped from Apify often need cleanup — strip non-digits, ensure 11 digits including country code, prefix with +. Retell rejects invalid formats with "not a valid number in e.164 format."
- **From number format is sensitive** — new API-purchased numbers work with `+1XXXXXXXXXX`. Existing dashboard-purchased numbers may fail even with correct format — purchase a new number as a workaround.
