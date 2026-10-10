# ScrapeCreators Enrichment — Email-Only Lists to Full Campaign

When the user provides a ScrapeCreators source CSV (with company names, descriptions, cities) AND a separate verified email list (from Reacher), cross-reference them to create enriched lead CSVs ready for personalization.

## Cross-Reference Process

### 1. Load the verified email list (Reacher output - email column only)

### 2. Load the ScrapeCreators source CSV (encoding='utf-8-sig' for BOM)

ScrapeCreators columns: Domain, Name, Industry Groups, Keywords, Description, City, State, Public Emails, Revenue Range, Employees, etc.

The `Public Emails` column contains comma-separated emails. Match against verified set.

### 3. Extract first names from email local parts

Filter out known non-name patterns (info, contact, support, sales, admin, office, team, wecare, careteam, scheduling, patient, doctor, provider, customer, client, service, billing, help, marketing, etc.)

### 4. Match rates

Solar: 77% (1,270/1,642). Men's Health: 90% (1,152/1,273). Unmatched are companies not in the ScrapeCreators export or with empty Public Emails field.

### 5. Output enriched CSV

firstName, email, company, city, state, description — feeds directly into email personalization generators.