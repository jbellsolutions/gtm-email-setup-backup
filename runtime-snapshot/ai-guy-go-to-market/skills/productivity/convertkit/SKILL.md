---
name: convertkit
description: "Kit (ConvertKit) newsletter: broadcasts, subscribers, sequences, tags via v4 API."
version: 1.0.0
author: jbellsolutions
license: MIT
metadata:
  hermes:
    tags: [Kit, ConvertKit, Newsletter, Email Marketing, API]
    homepage: https://developers.kit.com/v4
prerequisites:
  env_vars: [CONVERTKIT_API_KEY]
---

# Kit (ConvertKit) — Newsletter Operations

Justin's Kit account for AI Integraterz newsletters. Use the v4 API for all operations.

## Auth

All requests use the API key header:
```python
headers = {
    "X-Kit-Api-Key": os.environ["CONVERTKIT_API_KEY"],
    "Accept": "application/json",
    "Content-Type": "application/json"
}
```

Base URL: `https://api.kit.com/v4`

## Current Workspace State

### Forms
- **AI Operations Dispatch** (id: 7062108) — main signup form
- **Landing Page for kit to airtable** (id: 7062109)
- **Creator Profile** (id: 7062106)

### Segments
- **All Subscribers** (id: 548239)
- **Email Sequence1** (id: 549871)

### Tags (12)
- SpeakerAgent - Alpha/Beta/Waitlist (18181915/14/13)
- 7-Day Course (17845072)
- Certified Integrator (17748349)
- Business Inquiry (17748348)
- AI Integrator Applicant (17748347)
- Trigger_Flash_Sequence (17563809)
- Client (17431266)
- Lead batch 1 (17028531), Lead batch1 (17023825)
- Imported March 6th (17163709)

### Sequences (10)
- **7-Day Course** (id: 2696341) — main drip sequence
- Client Sequence 2 (2672633), Email Sequence 1 (2672461)
- Welcome new blog subscribers (2049975)
- Plus 6 others

### Recent Broadcasts
- 2 drafts in progress
- 5 published (March-April 2026)

## Common Operations

### Create a Broadcast (Newsletter)
```python
# POST /v4/broadcasts
{
    "subject": "Your Subject Line",
    "content": "<p>HTML content here</p>",
    "description": "Internal description",
    "email_layout_template": "text",  # or "classic", "modern"
    "public": true,  # show on public archive
    "send_at": "2026-05-02T09:00:00Z"  # optional scheduled send
}
```

### Send a Broadcast
Two-step: create draft, then publish:
```python
# 1. Create draft
# POST /v4/broadcasts → returns {broadcast: {id: ...}}

# 2. Draft the broadcast (set content)
# PUT /v4/broadcasts/{id}

# 3. To send immediately or schedule:
# POST /v4/broadcasts/{id}/publish  (sends to all or filtered)
```

### List Broadcasts
```python
# GET /v4/broadcasts?page=1&per_page=50
# Filter by status: GET /v4/broadcasts?status=draft|published
```

### Get Broadcast Stats
```python
# GET /v4/broadcasts/{id}/stats
# Returns: sent_count, open_count, click_count, unsubscribe_count, etc.
```

### Subscriber Management
```python
# List subscribers
# GET /v4/subscribers?page=1&per_page=50&sort_field=created_at&sort_order=desc

# Get subscriber
# GET /v4/subscribers/{id}

# Create subscriber
# POST /v4/subscribers
{"email_address": "user@example.com", "first_name": "Name", "state": "active"}

# Tag a subscriber
# POST /v4/tags/{tag_id}/subscribers
{"email_address": "user@example.com"}

# Add to sequence
# POST /v4/sequences/{sequence_id}/subscribers
{"email_address": "user@example.com"}
```

### Tags
```python
# List tags: GET /v4/tags
# Create tag: POST /v4/tags  {"name": "New Tag"}
# Tag subscriber: POST /v4/tags/{id}/subscribers {"email_address": "..."}
# List tagged: GET /v4/tags/{id}/subscribers
```

### Sequences
```python
# List: GET /v4/sequences
# Get: GET /v4/sequences/{id}
# Subscribe: POST /v4/sequences/{id}/subscribers {"email_address": "..."}
```

### Forms
```python
# List: GET /v4/forms
# Get subscribers: GET /v4/forms/{id}/subscribers
```

## Newsletter Writing Guidelines

Justin's newsletter style (from past broadcasts):
- **Subject lines:** Conversational, story-driven hooks. Not clickbait but curiosity-provoking
- **Content:** Personal narrative → lesson → CTA. Short paragraphs, conversational tone
- **No em dashes** (use commas or periods instead)
- **HTML format** with simple styling — no heavy templates

## Rate Limits
- 120 requests per minute
- Pagination: max 50 per page, use `page` param

## Pitfalls
- Broadcast must be created as draft first, then published separately
- `send_at` schedules future send — omit for immediate on publish
- Subscriber state: "active", "inactive", "bounced", "cancelled"
- Content is HTML — escape special chars, use `<p>` tags
- The API key provides full access — this is not a read-only key
