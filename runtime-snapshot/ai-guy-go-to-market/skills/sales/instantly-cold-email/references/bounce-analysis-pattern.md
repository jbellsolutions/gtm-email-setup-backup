# Bounce & Block Analysis Pattern

Framework for categorizing blocked/bounced leads in Instantly campaigns.
Built from Solar Installers campaign #3691319 analysis (July 21, 2026).

## Quick Diagnostic Commands

```bash
# 1. Get campaign stats - check bounce_count vs blocked
Instantly campaigns get --id <ID> --format json | jq '{bounce_count,block_count,status,sent_count,total_leads}'

# 2. Export all leads for analysis
Instantly campaigns export --id <ID> --out /tmp/campaign_leads.csv

# 3. List bounced emails with details
Instantly leads list-by-status --campaign-id <ID> --status bounced --format json | jq '.data[] | {email: .lead.email, company: .lead.company_name, first_name: .lead.first_name}'

# 4. Check sending infrastructure health
Instantly email-accounts list --campaign-id <ID> --format json | jq '.[] | {email: .from_email, warmup: .warmup_details.warmup_reputation, smtp: .is_smtp_success, imap: .is_imap_success}'
```

## Bounce Triage Flow

1. **Check sending infrastructure first** — warmup reputation, SMTP/IMAP status. If accounts are healthy (94%+ rep, SMTP/IMAP green), the problem is the lead data, not your setup.
2. **Categorize every bounce** into one of three buckets:

### Category 1: Role-Based / Generic Emails
Addresses that don't belong to a person. These will ALWAYS bounce or go to spam.

**Patterns to detect:**
- `estimating@`, `info@`, `sales@`, `support@`, `cshelp@`, `admin@`, `customer.care@`, `produce@`, `billing@`
- Garbage first names in lead data (company name used as person name, city used as name, username used as name)

**Examples from Solar #3691319:**
| Email | First Name | Issue |
|---|---|---|
| `estimating@kvlsolar.com` | "KVL" | Company name as first name |
| `cshelp@goodenergy.com` | "Lackawanna" | City name as first name |
| `customer.care@smartenergy.com` | "Care" | Garbage parse of department |

**Fix:** Filter these at lead source. Exclude role-based email patterns before upload.

### Category 2: Wrong Company Type
The company isn't a fit for the campaign. These may be valid email addresses but the recipient isn't a target.

**Solar installer campaign mismatches:**
- Marketplaces (EnergySage) — not an installer
- Finance companies (SunFunder) — not an installer  
- Trade associations (MNSEIA) — not an installer
- Manufacturers (Trina Solar) — not an installer

**Fix:** Add company-type filtering to lead sourcing pipeline.

### Category 3: Dead/Invalid Addresses at Real Companies
The company looks right, but the email hard-bounced. Employee left, address typo, or mailbox deleted.

**Fix:** Email verification before upload. These are unavoidable in scraping but should be caught by verification, not by Instantly bounces.

## Expected Quality from PipelineLabs

PipelineLabs `emailStatus: "verified"` / `"deliverable"` is NOT reliable. Expect 40-50% rejection from any PipelineLabs scrape. The Reacher verification step is mandatory — do not skip it.

On a clean list (post-Reacher verification), expect <3% bounce rate. If bounce rate exceeds 10%, the list wasn't properly verified or the lead source has systemic quality issues.
