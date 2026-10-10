# Instantly Prospector — Filter Field Reference

## Correct Filter Names (July 2026 verified)

The `prospect search` and `prospect fetch` JSON use **string-based filter values**, NOT numeric IDs:

```json
{
  "country": ["United States"],
  "companyHeadCount": ["0 - 25"],
  "companyRevenue": ["$0 - 1M", "$1 - 10M"],
  "companySubIndustry": ["Accounting", "Marketing and Advertising"],
  "companyKeyword": ["Fractional CFO", "Bookkeeper"],
  "level": ["C-Level", "VP-Level", "Director-Level"],
  "limit": 200,
  "dontDisplayOwnedContact": true
}
```

## Field Reference

| Field | Type | Values/Examples |
|-------|------|----------------|
| `country` | string[] | `["United States"]` (use `prospect countries` to list) |
| `companyHeadCount` | string[] | `"0 - 25"`, `"25 - 100"`, `"100 - 250"`, `"250 - 1000"`, `"1K - 10K"`, `"10K - 50K"`, `"50K - 100K"`, `"> 100K"` |
| `companyRevenue` | string[] | `"$0 - 1M"`, `"$1 - 10M"`, `"$10 - 50M"`, `"$50 - 100M"`, `"$100 - 250M"`, `"$250 - 500M"`, `"$500M - 1B"`, `"> $1B"` |
| `companyIndustry` | string[] | Broad categories. Use `prospect industries` to list. Optional if `companySubIndustry` is set. |
| `companySubIndustry` | string[] | Specific. Use `prospect sub-industries --industry-id <ID>` to list. **Names must be exact** (e.g., `"Professional Training & Coaching"` with `&`, not `and`). |
| `companyKeyword` | string[] | Searches company NAME + DESCRIPTION text. Best for niche targeting when industry enums don't match. |
| `level` | string[] | `"C-Level"`, `"VP-Level"`, `"Director-Level"`, `"Manager-Level"`, `"Staff"` |
| `limit` | int | 1-500 for `search`, 1-10000 for `fetch` |
| `dontDisplayOwnedContact` | bool | Set `true` to exclude leads already in your Instantly database |

## CRITICAL Pitfalls

1. **These are STRING field names, not `_ids`**: `companyHeadCount`, NOT `headcount_id` or `headcount_ids`.
2. **Ampersands in sub-industry names**: `"Professional Training & Coaching"` breaks shell `echo` commands. Use pre-written JSON files (`write_file` tool or `cat << 'EOF'` heredoc).
3. **Ampersands in industry values are REQUIRED**: `"Staffing & Recruiting"` not `"Staffing and Recruiting"`. The API rejects wrong variants.
4. **`seniorityIncludes` does NOT include `"founder"`**: Use `["owner", "c_suite", "partner"]` for SMB decision makers. Adding `"founder"` causes 400 Bad Request.
5. **`companyKeyword` searches name + description**, not just company name. This is the escape hatch when exact industry enum values don't cover your niche (e.g., "Fractional CFO" isn't a sub-industry).

## Search vs Fetch — The Reality Gap

`prospect search` `total_count` is the full database match count — often 20-25K+. `prospect fetch` returns FAR FEWER (1K-6K typically) — only contacts where the enrichment system can find email addresses.

### Why This Happens
- Many database contacts lack discoverable emails
- The enrichment pipeline filters out unreachable contacts
- `dontDisplayOwnedContact` excludes contacts already in your leads
- Different keyword combos probe different segments of the pool

### The Pattern
1. Search → note `total_count` (aspirational)
2. Fetch → check `fetched-searches` for actual `totalContacts`, `verifiedEmails`
3. The REAL pool is `verifiedEmails`, not `total_count`
4. To maximize coverage: create multiple searches with complementary keyword combos, fetch each
5. Track credit usage: ~1 credit per fetched contact. Verified emails are ~50-70% of fetched.

### Keyword effectiveness
- `["Fractional CFO", "Marketing Consultant", "Marketing Strategist"]` — high email match rate
- `["Marketing Agency"]` — WHEN USED ALONE may produce 6K+ contacts with zero emails. BUT when paired WITH `companySubIndustry: ["Marketing and Advertising"]`, it works: 2,270 contacts → 1,567 verified (filter 4478758, Jul 22). The sub-industry filter constrains the keyword search, preventing the broad-match spam problem.
- `["AI Agency", "AI Automation Agency", "Artificial Intelligence Agency"]` — works against `Computer Software` + `Information Technology and Services` sub-industries: 5,000 contacts → 2,100+ verified (filter 4478761, Jul 22).
- `["Growth Marketing"]` — may produce contacts with zero emails
- `["Outsourced Marketing"]` — unreliable
- Rule of thumb: generic keywords need a sub-industry guardrail. Niche professional-service keywords (Fractional CFO, CRM Consultant) work standalone.

### Batch Fetching
Max single fetch: 10,000 contacts. Max daily: 100,000. Credits: starts at 50,000/month.

### CLI Command Formats (ALL use --from-json)

**`prospect search`** — discover contacts (no credit cost):
```bash
Instantly prospect search --from-json filters.json
# filters.json: {country, companyHeadCount, companySubIndustry, companyKeyword, level, limit, dontDisplayOwnedContact}
```
Returns `total_count` (aspirational) and a `filter_id` for later fetch.

**`prospect fetch`** — enrich contacts with emails (consumes credits, async):
```bash
Instantly prospect fetch --from-json fetch.json
# fetch.json: {"filter_id": 4478758, "limit": 5000}
```
**Async behavior**: Initial response shows `completed: 0` and `metrics` all zeros. Emails enrich over 2-5 minutes. Poll `fetched-searches` to track progress. The `list` in the initial response shows previously cached contacts — ignore it for metrics.

**`prospect get`** — download enriched contacts (paginated):
```bash
Instantly prospect get --from-json get.json
# get.json: {"filter_id": 4478758, "limit": 1000, "offset": 0}
```
Max 1,000 per call. Paginate with `offset`. Filter downloaded contacts to `status == "found"` AND `verificationStatus == "valid"` before using.

For bulk extraction of verified emails across all pages, use the bundled script:
```bash
python3 scripts/pull_verified_emails.py <filter_id> --csv output.csv
```
This handles pagination, filters to only verified+found contacts, and writes a clean CSV of (email, name, company).

**Naming quirks in `get` output vs `search`/`fetch` output:**
- `totalCount` (camelCase) in `get`, but `total_count` (snake_case) in `search` and `fetch`. These are different API endpoints — don't assume consistent casing.
- `get` contacts have `firstName` + `lastName` only (no `fullName`). `search` results have `fullName`.
- `get` contacts include `emailSource` field; `search`/`fetch` results do not.

### Navigating `fetched-searches` Metrics

The metrics live at `item.fetch_details.metrics`, **NOT** `item.metrics`:
```
item.fetch_details.metrics.verifiedEmails   ← correct
item.fetch_details.metrics.totalContacts
item.fetch_details.metrics.completed         ← tracks async enrichment progress
```

**Also useful at the `fetch_details` level:**
- `leads_found` — how many contacts were found
- `email_fetched` — how many emails were successfully found (sometimes differs from `verifiedEmails`)

### Background Process PATH

When running `Instantly` commands as background processes (`terminal background=true`), the PATH is stripped. Always use the full path:
```bash
/opt/data/home/.local/bin/Instantly prospect fetch --from-json fetch.json
```
Not just `Instantly prospect fetch ...`.

### Piping `Instantly` output — stderr is the enemy

Every `Instantly prospect` command prints a warning to **stderr**:
```
Warning: API response shape changed — CLI output may be incomplete
  data: Expected array, received object
```

**❌ NEVER use `2>&1`** (merge stderr into stdout) when piping to `jq`, `python3 -c`, or any JSON parser. The warning lines will corrupt the JSON.

**✅ ALWAYS use `2>/dev/null`** to suppress stderr:
```bash
# CORRECT — warning goes to /dev/null, stdout is clean JSON
Instantly prospect get --from-json query.json 2>/dev/null | python3 -c "..."

# WRONG — warning lines poison the JSON stream
Instantly prospect get --from-json query.json 2>&1 | python3 -c "..."
```

To save to file for later processing:
```bash
Instantly prospect get --from-json query.json 2>/dev/null > data.json
```

**If you must capture both streams**, save stderr separately:
```bash
Instantly prospect get --from-json query.json > data.json 2>warnings.log
```

### Execute-code sandbox truncation

The `execute_code` sandbox truncates `terminal()` output at ~20KB. For large contact lists (1000 contacts ≈ 300KB JSON), use `terminal` directly with output redirection to a file, then process the file. Do NOT rely on `execute_code` + `terminal()` for large paginated pulls — the JSON will be truncated mid-object.

### `companyHeadCount` Bucket Note
The smallest bucket is `"0 - 25"`. There is no `"1 - 10"` bucket. To target 1-10 employee companies, use `"0 - 25"` and accept the wider range.

## Recent Fetch Examples (July 2026)

Marketing Agency niche (`["Marketing Agency"]`, Marketing and Advertising sub-industry, 0-25 headcount):
- Filter 4478758: 2,270 contacts → 2,219 emails → 1,567 verified (69% yield)
- Combined sub-industry constraint makes "Marketing Agency" keyword viable (vs standalone use which fails)

AI Agency niche (`["AI Agency", "AI Automation Agency", "Artificial Intelligence Agency"]`, Computer Software + IT Services sub-industries, 0-25 headcount):
- Filter 4478761: 5,000 contacts → 3,565 emails → 2,138 verified (43% yield, still enriching at time of recording)

CFO/Accountant niche (`["Fractional CFO", "Bookkeeper", "Outsourced CFO", "CPA"]`, Accounting sub-industry):
- Filter 4438306: 1,843 contacts → 1,567 emails → 1,089 verified

Business Coach niche (`["Business Coach", "EOS Implementer", "Fractional COO", "Executive Coach"]`):
- Filter 4438326: 2,000 contacts → 1,638 emails → 973 verified

CRM Consultant niche (`["HubSpot Consultant", "GoHighLevel", "Keap Consultant", "ActiveCampaign Partner", "CRM Consultant"]`):
- Filter 4438310: 772 contacts → 582 emails → 380 verified

CMO/Marketing niche — required 7 fetches across keyword variations to accumulate:
- Effective keywords: `"Fractional CMO"`, `"Marketing Consultant"`, `"Marketing Strategist"`
- Ineffective (standalone): `"Growth Marketing"`, `"Marketing Advisor"`, `"Outsourced Marketing"`
- Context-dependent: `"Marketing Agency"` — fails when used without sub-industry, works (2,270→1,567 verified) when scoped to `"Marketing and Advertising"` sub-industry (see filter 4478758 above)
- Total across working filters: 9,695 contacts → 5,094 emails → 3,946 verified