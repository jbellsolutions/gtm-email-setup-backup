# PR Agency Scrape & Verification — May 12, 2026

## Apify PipelineLabs Scrape

- **Actor:** `kVYdvNOefemtiDXO5` (PipelineLabs)
- **Run ID:** `JNY7lyCllGQC29sHT`
- **Dataset ID:** `aWVXdhcnqwMS25JSb`
- **Results:** 5,000 leads in 32 seconds

### Payload
```python
{
    "companyKeywordIncludes": [
        "public relations", "PR agency", "PR firm",
        "communications agency", "media relations", "public affairs",
        "strategic communications"
    ],
    "seniorityIncludes": ["owner", "c_suite", "partner", "director"],
    "companySizeIncludes": ["1-10", "11-50", "51-200", "201-500"],
    "hasEmail": True,
    "emailStatusIncludes": ["verified"],
    "personLocationCountryIncludes": ["United States"],
    "totalResults": 5000,
}
```

Keyword search required because "Public Relations" is not in PipelineLabs' industry enum.

## Qualification

- **Script:** `scripts/qualify_leads.py`
- **Input:** 5,000 raw leads
- **Output:** 4,981 qualified (99%)
- **Rejected:** 16 generic emails (info@, contact@, etc.), 3 bad company names, 0 duplicates

## Anymail Finder Verification

- **API:** `POST /v5.1/verify-email`
- **Verified:** 4,981 emails
- **Credits used:** 996

### Results

| Status | Count | % |
|---|---|---|
| Valid | 2,402 | 48.2% |
| Risky | 82 | 1.6% |
| Invalid | 2,459 | 49.4% |

### Key Finding

**PipelineLabs `emailStatus: "verified"` / `"deliverable"` is wrong 49.4% of the time.** 

Sample invalids PipelineLabs called "deliverable":
- `josh@lacknerandrews.com`
- `levi.thornton@720strategies.com`
- `gventura@spinshoppe.com`
- `mcadwallader@rainierco.com`

This same pattern repeats across all campaigns:
- recruiters-direct-value-A: 35.9% invalid
- ai-operator-10hr-broad: 42.2% invalid
- ai-operator-10hr-niche: 34.2% invalid

## Instantly Upload

- **Campaign:** `SA-PowerPartners-PR-Wave1` (3316611)
- **Uploaded:** 5 batches of ~1,000 each
- **New leads added:** 4,768 (179 duplicates, 23 blocked)
- **Campaign total:** 5,247

### Cleanup

After Anymail Finder verification, 2,459 invalid leads were unsubscribed from the campaign.
Clean leads remaining: ~2,484 (valid + risky).
