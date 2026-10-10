# Instantly Sequence JSON Template

**Delivery method:** Use `curl` to POST directly to the API. The MCP tool `mcp_Instantly_save_campaign_sequences` fails with a 400 error because it auto-includes `distribution_percentage` which the API rejects. The CLI `Instantly campaigns save-sequence` also has issues with custom field merge tags.

**Working pattern (curl):**
```bash
curl -s -X POST "https://server.Instantly/api/v1/campaigns/{CAMPAIGN_ID}/sequences?api_key=$Instantly_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sequences": [...]}'
```

**IMPORTANT:** The JSON must be wrapped in `{"sequences": [...]}`, NOT a bare array. Do NOT include `distribution_percentage` in seq_variants — it's not an allowed field.

## 4-Email Per-Lead Custom Field Sequence

This template assumes each lead has these custom fields:
- `email_subject`, `email_body` (email 1)
- `email2_subject`, `email2_body` (email 2)
- `email3_body` (email 3 — short bump)
- `email4_body` (email 4 — breakup)

```json
{
  "sequences": [
    {
      "seq_number": 1,
      "seq_delay_details": {"delay_in_days": 1},
      "seq_variants": [
        {"subject": "{{email_subject}}", "email_body": "{{email_body}}", "variant_label": "a"}
      ]
    },
    {
      "seq_number": 2,
      "seq_delay_details": {"delay_in_days": 3},
      "seq_variants": [
        {"subject": "{{email2_subject}}", "email_body": "{{email2_body}}", "variant_label": "a"}
      ]
    },
    {
      "seq_number": 3,
      "seq_delay_details": {"delay_in_days": 7},
      "seq_variants": [
        {"subject": "re: {{email_subject}}", "email_body": "{{email3_body}}", "variant_label": "a"}
      ]
    },
    {
      "seq_number": 4,
      "seq_delay_details": {"delay_in_days": 14},
      "seq_variants": [
        {"subject": "last one", "email_body": "{{email4_body}}", "variant_label": "a"}
      ]
    }
  ]
}
```

## Merge Tag Convention

Custom fields on leads are referenced WITHOUT the `custom_fields.` prefix:
- ✅ `{{email_subject}}` — resolves to `custom_fields.email_subject`
- ❌ `{{custom_fields.email_subject}}` — DO NOT use; documented to silently kill sends for large field values

## Static-Subject / Static-Body Variant

If you don't need per-lead personalized subjects/bodies:

```json
{
  "sequences": [
    {
      "seq_number": 1,
      "seq_delay_details": {"delay_in_days": 1},
      "seq_variants": [
        {"subject": "your AI person", "email_body": "Hey {{first_name}},\n\nJust putting something on your radar...\n\n{{sender_name}}", "variant_label": "a"}
      ]
    }
  ]
}
```
