# Bird Email API — Schema Reference

## Transmission Request (full)

```json
{
  "content": "<InlineContent | RFC822Content>",
  "recipients": "<Recipient[] | RecipientList>",
  "campaign_id": "string (max 64 chars)",
  "metadata": { "key": "value" },
  "description": "string (max 1024 chars)",
  "substitution_data": { "key": "value" },
  "options": {
    "start_time": "ISO 8601 datetime",
    "open_tracking": true,
    "initial_open": true,
    "click_tracking": true,
    "transactional": false,
    "sandbox": false,
    "skip_suppression": false,
    "ip_pool": "string",
    "inline_css": false,
    "perform_substitutions": true
  }
}
```

## InlineContent

```json
{
  "from": "sender@domain.com",
  "subject": "Subject line (UTF-8, no RFC2047)",
  "html": "<h1>HTML body</h1>",
  "text": "Plain text body",
  "amp_html": "<AMP HTML>",
  "reply_to": "reply@domain.com",
  "headers": { "X-Custom": "value" },
  "attachments": [
    {
      "name": "file.pdf",
      "type": "application/pdf",
      "data": "base64-encoded-content"
    }
  ],
  "inline_images": [
    {
      "name": "logo",
      "type": "image/png",
      "data": "base64-encoded-content"
    }
  ]
}
```

- `from` can be a string or `{"email": "...", "name": "Display Name"}`
- At least one of `html` or `text` is required
- `reply_to` sets the Reply-To header
- `headers` — custom headers (no Content-Type, Content-Transfer-Encoding, or To)
- `inline_images[].name` — used as Content-ID, referenced in HTML as `<img src="cid:NAME">`

## RFC822Content

```json
{
  "email_rfc822": "Full RFC822 message string"
}
```

- Substitutions applied to top-level headers and first text/plain, text/html, text/x-amp-html parts only
- Line endings auto-converted to CRLF
- Should NOT be dot-stuffed
- Should NOT contain SMTP terminator `\r\n.\r\n`
- Content headers must be provided in the RFC822 content

## Recipient

```json
{
  "address": {
    "email": "recipient@example.com",
    "name": "Display Name"
  },
  "tags": ["tag1", "tag2"],
  "metadata": { "key": "value" },
  "substitution_data": { "first_name": "John" },
  "return_path": "bounce@domain.com",
  "rcpt_type": "to"
}
```

- `rcpt_type`: `"to"` (default), `"cc"`, or `"bcc"`
- `return_path`: domain must be CNAME-verified sending domain

## RecipientList (stored list)

```json
{
  "list_id": "stored-list-id"
}
```

## Transmission Response (200)

```json
{
  "results": {
    "id": "unique-transmission-id",
    "total_accepted_recipients": 100,
    "total_rejected_recipients": 0
  },
  "errors": [
    {
      "message": "Human readable error",
      "code": "MACHINE_CODE",
      "description": "Detailed description",
      "rcpt_to_errors": [
        {
          "message": "Recipient error",
          "description": "Detail",
          "code": "RECIPIENT_ERROR_CODE"
        }
      ]
    }
  ]
}
```

## Error Response (400/420/422)

```json
{
  "errors": [
    {
      "message": "Human readable error message",
      "code": "MACHINE_CODE",
      "description": "Detailed error description"
    }
  ]
}
```

## Sending Domain Status

```json
{
  "ownership_verified": true,
  "dkim_status": "valid",
  "cname_status": "valid",
  "mx_status": "unverified",
  "spf_status": "unverified",
  "abuse_at_status": "unverified",
  "postmaster_at_status": "unverified",
  "verification_mailbox_status": "unverified",
  "verification_mailbox": "local-part",
  "compliance_status": "valid"
}
```

Status values: `"unverified"`, `"pending"`, `"invalid"`, `"valid"`
Compliance status: `"valid"`, `"blocked"`

## DKIM Configuration

```json
{
  "signing_domain": "domain.com",
  "public": "public-key-string",
  "private": "private-key-string",
  "selector": "dkim-selector",
  "headers": "ignored-field"
}
```

## Key Metrics (partial list)

| Metric | Definition |
|--------|-----------|
| `count_targeted` | Messages injected + rejected |
| `count_injected` | Messages injected into system |
| `count_sent` | Attempted deliveries |
| `count_accepted` | Accepted by ISP (less OOB bounces) |
| `count_delivered` | Successfully delivered |
| `count_rendered` | Total renderings |
| `count_clicked` | Total link clicks |
| `count_unique_clicked` | Unique messages clicked |
| `count_bounce` | Total bounces (hard + soft + block + admin) |
| `count_spam_complaint` | ISP spam complaints |
| `count_unsubscribe` | Unsubscribes |
| `total_delivery_time_first` | First-attempt delivery time (ms) |
| `total_msg_volume` | Total bytes delivered |

Data retention: 6 months.

## Regional DNS Verification

### CNAME (US)
| Hostname | Type | Value |
|----------|------|-------|
| example.com | CNAME | sparkpostmail.com |

### CNAME (EU)
| Hostname | Type | Value |
|----------|------|-------|
| example.com | CNAME | eu.sparkpostmail.com |

### DKIM requirements
- PKCS #1 and PKCS #8 supported
- No password-protected keys
- Public/private key pair must match single format
- DNS record: `p=` tag with public key
- `k=` tag must be `rsa` if defined
- `h=` tag must be `sha256` if defined

## Bounce Domain

A sending domain can be used as a bounce domain if verified via CNAME or MX (Enterprise). Set via transmission's `return_path` field or SMTP `MAIL FROM`.
