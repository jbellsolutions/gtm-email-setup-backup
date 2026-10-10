# Owned Audience Batch Email Generation (July 2026)

Pattern used for consolidating 6,739 leads (4,081 HVAC + 2,658 Recruiting) from old campaigns into new Owned Audience framework campaigns.

## Pattern: Consolidate → Generate → Chunk → Upload

### Step 1: Pull all leads from source campaigns

Use the pattern from `Instantly-cold-email` > `references/Instantly-cli-data-extraction.md`:
```bash
for offset in 0 100 200 ...; do
  Instantly leads list --campaign-id $cid --limit 100 --offset $offset --format json > /tmp/camp_${cid}_p${offset}.json
done
```

Process in Python, deduplicate by email, save as single JSON.

### Step 2: Generate personalized emails with deterministic framework rotation

Use a Python script that:
- Reads the consolidated leads JSON
- Selects framework per lead using `sum(ord(c) for c in company) % 10` (even distribution, no monotony)
- Fills template variables: `{first_name}`, `{company}`, `{city}`, `{state}`
- Generates all 4 emails per lead (Day 0, Day 3, Day 7, Day 14)
- Skips generic emails (info@, hello@, contact@, support@, etc.)
- Skips bad first names ("there", "", null)
- Outputs Instantly-ready CSV with columns: first_name, last_name, email, company, email_subject, email_body, email2_subject, email2_body, email3_subject, email3_body, email4_subject, email4_body

### Step 3: Clean company names before embedding

**Critical:** Company names often contain banned words ("Solutions", "Innovative") that get embedded in the email body via CTAs like "Want me to send a short version for {company}..."

```python
def clean_company(company):
    """Strip banned-word-containing suffixes from company names."""
    c = re.sub(r'\b\w*solutions?\w*\b', '', company, flags=re.IGNORECASE)
    c = re.sub(r'\b\w*innovative\w*\b', '', c, flags=re.IGNORECASE)
    c = re.sub(r'  +', ' ', c).strip()
    if len(c) < 4:
        return company  # don't destroy short names
    return c
```

Apply to company name before any embedding in email body. Raw company name still used for framework hash selection.

### Step 4: Clean first names from garbled ListKit data

Old ListKit extractions produced names like "Idealnditionsnditioning", "Floridaol", "CESmmercial". Fix:

```python
def clean_first_name(name, company):
    bad = {"there", "", "null", "none", "nan"}
    if name.lower().strip() in bad:
        company_words = company.split()
        skip = {"the", "a", "ac", "air", "heating", "conditioning", "hvac", ...}
        bad_indicators = {"conditioning", "commercial", "service", "solutions", ...}
        for w in company_words:
            clean = re.sub(r'[^a-zA-Z]', '', w)
            if clean.lower() not in skip and clean.lower() not in bad_indicators and len(clean) >= 2:
                return clean.title()
        return "there"
    return name.strip()
```

### Step 5: Convert CSV to JSON chunks for Instantly upload

Instantly API accepts max 1,000 leads per request:
```python
chunks = [leads[i:i+1000] for i in range(0, len(leads), 1000)]
for ci, chunk in enumerate(chunks):
    payload = {
        "lead_list": chunk,
        "settings": {
            "ignore_duplicate_leads_in_other_campaign": True,
            "ignore_global_block_list": True,
            "ignore_unsubscribe_list": True
        }
    }
    # Save to /tmp/chunk_N.json
```

Upload via CLI:
```bash
Instantly leads add --campaign-id <ID> --from-json /tmp/chunk_0.json
```

### Step 6: Set up sequences via curl (NOT MCP tool)

The MCP `save_campaign_sequences` tool fails with 400 — it auto-includes `distribution_percentage` which the API rejects. Use:
```bash
curl -s -X POST "https://server.Instantly/api/v1/campaigns/{ID}/sequences?api_key=$Instantly_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sequences":[{"seq_number":1,"seq_delay_details":{"delay_in_days":0},"seq_variants":[{"subject":"{{email_subject}}","email_body":"{{email_body}}","variant_label":"A"}]},...]}'
```

Custom field merge: `{{email_subject}}` (no `custom_fields.` prefix).

## Quality Targets

- 50-100 words per email (aim 85-95)
- Zero banned words in body (pre-clean company names)
- Even framework distribution (hash-based rotation achieves ~10% per framework)
- <2% word count outliers acceptable for batch processing
- Generic emails (info@, hello@, etc.) auto-skipped — they produce near-zero replies

## Results from July 16 consolidation

| | HVAC | Recruiting |
|---|---|---|
| Source campaigns | 13 | 7 |
| Raw leads pulled | 6,520 | 2,661 |
| Unique after dedup | 5,434 | 2,421 |
| Generated (non-generic) | 4,081 | 2,658 |
| Word count OK | 3,623 (88.8%) | 2,654 (99.8%) |
| Banned word issues | 8 (0.2%) | 1 |
| Framework spread | 356-469 even | 227-302 even |