# Lead Quality Filtering Rules

Discovered during Solar Installers campaign (#3691319) audit — the prospect scraper produces systematic garbage that causes bounces and wastes verification credits. Apply these filters at lead import time or during list cleaning.

## Automatic Rejection Patterns

### Role-Based / Generic Emails (ALWAYS bounce or hit spam traps)
- `estimating@`, `cshelp@`, `customer.care@`, `customer.service@`
- `info@`, `sales@`, `support@`, `admin@`, `contact@`, `hello@`
- `produce@`, `billing@`, `accounting@`, `hr@`, `jobs@`
- `office@`, `mail@`, `inquiries@`, `help@`, `service@`

### Username-As-Name (scraper failed to find a real person)
When `first_name` matches these patterns, the lead is bad:
- Contains the email username verbatim (e.g., `gafsolarshingle@gmail.com` → first_name = "Gafsolarshingle")
- Contains "solar" concatenated (e.g., `Diysolarforu`, `Solarupdate`)
- Is a domain-like string, all lowercase, or multiple words concatenated without spaces

### Wrong Company Types (not local solar installers)
Exclude by domain/company name:
- **Marketplaces/Platforms:** energysage.com, solarreviews.com, sunrun.com (national), tesla.com/solar
- **Finance Companies:** sunfunder.com, sunlightfinancial.com, dividendsolar.com
- **Trade Associations:** mnseia.org, seia.org, [state]seia.org
- **Manufacturers:** trinasolar.com, canadian-solar.com, q-cells.com, longi.com
- **Media/Content:** solarenergyworld.com, solarpowerworldonline.com

## Pre-Verification Cleaning

Before running Reacher verification, strip these patterns to conserve the shared 10K/24h cap:

```bash
# Remove role-based emails
grep -viE '^(estimating|cshelp|customer\.care|info|sales|support|admin|contact|hello|produce|billing|accounting|hr|jobs|office|mail|inquiries|help|service)@' leads.csv > cleaned.csv

# Remove gmail addresses with username-as-name patterns (optional, manual review)
grep -v '@gmail\.com' leads.csv >> cleaned.csv  # skip consumer gmails, keep business domains
```

## Verification Results Pattern
- Bad lists typically show 15-30% undeliverable
- Good lists typically show <5% undeliverable
- Solar Installers campaign (#3691319) had 10/70 = 14.3% bounce rate on first send — indicative of poor list quality

## Session Reference
July 21, 2026 — Solar Installers #3691319 audit: 1,433 leads, 10 blocked (bounced). Root cause: 5 role-based/wrong-fit + 5 stale addresses. Sending infrastructure healthy (44 PuzzleInbox accounts, 92-100% warmup).