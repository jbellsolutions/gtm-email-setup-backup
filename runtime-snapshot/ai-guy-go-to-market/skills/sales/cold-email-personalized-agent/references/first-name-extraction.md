# First-Name Extraction from Lead Data

When lead CSVs lack a `contact_name` field (or it's empty), extract a first name from the company name. This is common in scraped Google Maps / Yelp lead lists.

## Extraction Priority

1. **Use `contact_name` if present.** Split on spaces, take first token. Strip trailing commas.
2. **Fall back to company name.** Apply cleanup rules below.

## Recommended: Permissive Approach (for scale batch processing)

**Tested on 2,854 HVAC leads across 5 states (June 2026).** This approach is looser than the alternative below — it accepts company-name words as greetings, which reads naturally in cold email. "United" as a greeting to United Refrigeration reads like a person's name and doesn't feel like a template error.

### Step 1: Strip common business suffixes
Remove these from the END of the company name:
```
LLC, Inc, Corp, Ltd, Co, Services, Solutions,
Heating, Air Conditioning, Cooling, Plumbing, Mechanical,
& Air, and Air, Heating &, Heating and
```

### Step 2: Take the first remaining word

### Step 3: Only block truly unusable words
```python
UNUSABLE = {"A", "AC", "HVAC", "THE", "ALL", "AAA", "A1", "24", "24/7", "911",
            "PRO", "DR", "MR", "AIR", "COOL", "ECO"}
```
Everything else passes through — including United, Ideal, American, Universal, Precision, Absolute, Elite, etc. These read as plausible first names in context.

### Step 4: Fall back to "there"
If the first word is a single character, purely numeric, or in the UNUSABLE set, use "there".

### Examples (permissive)

| Company Name | → first_name | Why |
|---|---|---|
| United Refrigeration Inc | United | Suffix stripped, "United" passes filter |
| Ideal Conditions Heating & Air | Ideal | Suffixes stripped, "Ideal" passes |
| Anchor Heating and Air Daniel Island | Anchor | Clean extraction |
| AC Brothers | **there** | "AC" is in UNUSABLE set |
| The Air Squad | "The" stripped, "Air" in UNUSABLE → **there** |
| A-1 Plumbing & HVAC | **there** | "A-1" → numeric → there |
| 1st Choice Heating | **there** | Starts with digit |
| Davis Air Conditioning | Davis | Clean extraction |

## Alternative: Aggressive Skip-Word Approach (legacy)

The older approach tries to skip non-name words entirely and use the *second* word when the first is an industry term. This produces more (not fewer) errors at scale because single-word skip decisions cascade — "Air Plus of South Florida" → "Plus" (reads as spam).

**Only use this approach for small batches (≤25 leads) where you can spot-check every extraction.**

### Step 1: Strip prefixes
Remove these prefixes from the start of the company name:
- `The ` / `the `

### Step 2: Skip non-name first words
If the first word (after prefix stripping) is in this set, use the SECOND word:
```
Air, A/C, AC, HVAC, All, A-1, A1, A+, 24, 911, Mr., Dr., Cool
```

### Step 3: Take the first remaining word

## Python Reference Implementation (Permissive)

See `scripts/hvac_state_personalize.py` for the full implementation. Core extraction:

```python
def extract_first_name(company_name):
    if not company_name:
        return "there"
    name = company_name.strip()
    # Remove common suffixes
    for suffix in [" LLC", " Inc", " Corp", " Ltd", " Co", " Services", " Solutions",
                   " Heating", " Air Conditioning", " Cooling", " Plumbing", " Mechanical",
                   " & Air", " and Air", " Heating &", " Heating and"]:
        name = name.replace(suffix, "")
    name = name.strip()
    first = name.split()[0] if name.split() else ""
    if not first or len(first) <= 1:
        return "there"
    UNUSABLE = {"A", "AC", "HVAC", "THE", "ALL", "AAA", "A1", "24", "24/7", "911",
                "PRO", "DR", "MR", "AIR", "COOL", "ECO"}
    if first.upper() in UNUSABLE:
        return "there"
    if first.isdigit():
        return "there"
    first = re.sub(r'[^a-zA-Z\'-]', '', first)
    if len(first) <= 1:
        return "there"
    return first
```

## Quality Check

After extraction, spot-check at least 10 random leads. If more than 2 are "there" when a company-name-as-greeting would have worked, review the UNUSABLE set — it may be too aggressive.
