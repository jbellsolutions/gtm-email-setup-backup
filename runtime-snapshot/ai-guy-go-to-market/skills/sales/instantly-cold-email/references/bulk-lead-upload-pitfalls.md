# Bulk Lead Upload — MCP vs CLI, Pitfalls, and Patterns

## Upload batch sizes: MCP vs CLI

The MCP `add_leads_to_campaign` tool caps at **100 leads per request** (enforced by the tool's `max_objects_per_request`). For larger lists, use the Instantly CLI:

```bash
~/.local/bin/Instantly leads add --campaign-id <ID> --from-json /tmp/chunk.json
```

The CLI handles **1,000 leads per call** (Instantly API's actual limit). For lists >1,000: combine 100-lead batch files into 1,000-lead chunks and upload via CLI. For 8,000+ leads — ~9 CLI calls instead of 83+ MCP calls.

**Rate:** CLI calls with 1,000 leads take ~3-5 seconds each. Space 0.5s apart when chaining.

## Direct REST API blocked by Cloudflare

Calls to `https://server.Instantly/api/v1/campaigns/{id}/leads` with a Bearer token from Python's `urllib.request` (or curl) return **HTTP 403 — error code 1010** (Cloudflare). The Instantly MCP server and CLI (`~/.local/bin/Instantly`) bypass this. **Never attempt direct REST API calls for lead operations** — use the CLI for bulk uploads and the MCP for interactive/query use.

## `last_name` must be non-empty (API validation)

Instantly's API validates `last_name` as `minLength: 1`. An empty string `""` is rejected with a Zod validation error:

```
"code": "too_small",
"minimum": 1,
"message": "String must contain at least 1 character(s)",
"path": ["lead_list", 0, "last_name"]
```

**Fix:** For leads without a last name, use the company name (or first word of it). Example: `"first_name": "Team", "last_name": "Peakrestorewellness"`.

**Note:** Existing coaching leads in campaign #3617053 have empty `last_name` — those were imported via CSV, not API. The API path enforces this constraint; CSV import bypasses it.

## Mass lead generation with frameworks

When generating per-lead custom email copy at scale (1,000+ leads), the pattern:

1. **Extract names from emails.** For role accounts (info@, support@, admin@, etc.): `first_name: "Team"`. For named accounts: extract from email prefix (e.g., `ecohen@...` → "Ecohen").

2. **Company name from domain.** Split `@domain.tld`, use the domain part, title-case it.

3. **Distribute frameworks randomly.** Use `random.choice(frameworks)` per lead for email 1. Follow-ups (emails 2-4) use a common template with the company name.

4. **Pay attention to last_name.** Fill from company name if missing (see above).

5. **Save in 100-lead JSON batches** for MCP compatibility, then combine into 1,000-lead chunks for CLI upload.

### JSON format

```json
{
  "lead_list": [
    {
      "first_name": "Team",
      "last_name": "Peakrestorewellness",
      "email": "support@peakrestorewellness.com",
      "company_name": "Peakrestorewellness",
      "custom_fields": {
        "email_subject": "second channel",
        "email_body": "Hey Peakrestorewellness team, ...",
        "email2_subject": "different angle",
        "email2_body": "Hey Peakrestorewellness team, ...",
        "email3_body": "Hey Peakrestorewellness team, ...",
        "email4_body": "Hey Peakrestorewellness team, ..."
      }
    }
  ],
  "settings": {
    "ignore_duplicate_leads_in_other_campaign": true,
    "ignore_global_block_list": true,
    "ignore_unsubscribe_list": true
  }
}
```

## Campaign #3617053 specifics (updated July 13, 2026)

Campaign "Coaching Owned Audiences" now contains **9,457 total leads**: 1,202 coaching leads (from July 9) + 8,255 men's health provider leads (added July 13). Both segments share the same sender personas (Arianna, Anna, Grace, Penelope, Kaylee) and the same `custom_fields` merge-tag structure (`email_subject`, `email_body`, `email2_subject`, `email2_body`, `email3_body`, `email4_body`). The campaign sends 1,000/day Mon-Fri 8am-5pm ET.

Men's health lead details at `references/mens-health-frameworks-owned-audience-v1.md`.