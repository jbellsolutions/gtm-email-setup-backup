# ScraperCity Email Verification — Operational Reference

## Installation & Setup

```bash
npm install -g scrapercity@1.0.4
# Binary: /opt/data/home/.npm-global/bin/scrapercity
# Config: scrapercity config set apiKey YOUR_KEY (camelCase!)
export SCRAPERCITY_API_KEY=90c2ca64-81bc-48ab-a6b2-980abfaea898
export PATH=/opt/data/home/.npm-global/bin:$PATH
```

**⚠️ PATH trap:** Python subprocess and `xargs` do NOT inherit the npm global path. Always set `PATH=/opt/data/home/.npm-global/bin:$PATH` in the environment, or use the full binary path: `/opt/data/home/.npm-global/bin/scrapercity`.

## Key Commands

```bash
scrapercity email-validate user@example.com user2@example.com  # submit batch
scrapercity wallet                                               # check balance
scrapercity status <run_id>                                      # check status (prefer over poll)
scrapercity download <run_id>                                    # download CSV to CWD
```

## CLI Pitfalls

### 1. `--file` flag is broken
```bash
scrapercity email-validate --file /tmp/emails.txt  # FAILS with path error
```
**Workaround:** Use `xargs` or direct arguments:
```bash
cat /tmp/emails.txt | xargs scrapercity email-validate
```

### 2. `scrapercity poll` hangs / is unreliable
The `poll` command sometimes never exits, even after the run is SUCCEEDED. **Do not use it for automated workflows.**
**Instead:** Use a manual loop with `scrapercity status`:
```python
for i in range(40):  # 10 min max
    r = subprocess.run(['scrapercity', 'status', rid], ...)
    if 'SUCCEEDED' in r.stdout:
        break
    time.sleep(15)
```

### 3. `scrapercity download` outputs to CWD
The download command writes to the current working directory, not to a user-specified path. Move the file manually:
```bash
scrapercity download <run_id>
mv <run_id>.csv /tmp/verify_results/batch_N.csv
```

### 4. PATH not inherited by subprocess/xargs
```python
env = {**os.environ, 'PATH': '/opt/data/home/.npm-global/bin:' + os.environ.get('PATH','')}
```

## Scale Verification Workflow (10K+ emails)

1. **Extract + clean:** Remove garbage emails (URLs, encoded strings, no `@`)
2. **Batch into 500:** `split -l 500 emails.txt batch_` 
3. **Submit all batches:** Loop through batch files, pass emails as CLI args
4. **Poll + download manually:** Do NOT use `scrapercity poll`. Check status in a loop, download when SUCCEEDED
5. **Merge back:** Match verified emails to original lead CSV

## Cost & Performance

| Metric | Value |
|---|---|
| Cost per email | $0.0036 |
| 12,500 emails | ~$45 |
| Batch size | 500 (reliable) |
| Time per batch | 45-90 seconds |
| Total for 12,500 | ~30-40 minutes |

## Quality Findings (June 2, 2026 — 12,939 leads @ scale)

**Source:** ScrapeCreators lead database CSV (`local-businesses-2026-06-02.csv`)

| | Count | % of verified |
|---|---|---|
| Total leads | 12,939 | — |
| Clean emails after garbage removal | 12,501 | — |
| Garbage removed (URLs, encoding artifacts) | 512 | 4.0% |
| Valid | 7,187 | 59.9% |
| Invalid | 3,881 | 32.3% |
| Unknown/catch-all | ~932 | 7.8% |

**Cost:** $30.71 spent out of $158.98 balance. Final balance: ~$128 (approx).
**Time:** ~30 minutes for 24/26 batches submitted; 2 batches still running when campaign launched.
**Batches:** 26 batches of 500 emails each (25 × 500 + 1 × 1). Effective batch size: 500 emails in ~90 seconds.

**Early test (100-email sample):** 64 valid (64.6%), 28 invalid (28.3%), 7 unknown (7.1%). Consistent with full-scale results.

**Garbage examples:** Google Maps URLs leaked into email fields (e.g. `//google.com/maps/place/chris+a%2fc+company/@28.3066251`), URL-encoded strings (e.g. `%20info@frigidrefrigeration.com`), coordinate artifacts.

**Key finding:** ScrapeCreators lead database emails are NOT pre-verified. Only 194 of 12,939 leads (1.5%) had any `Email Status` value. The field is cosmetic — 32% of listed emails are actually invalid.

## ScraperCity Output Schema

CSV columns from `scrapercity download`:
- `email` — the input email
- `sc_email_status` — `valid` or `invalid` (binary, no "risky" tier)
- `sc_validation_message` — e.g. "Email is valid." / "Email is invalid."
- `sc_is_catch_all` — true/false
- `sc_mx_record`, `sc_mx_provider`, `sc_mx_security_gateway`
- Company enrichment (included at no extra cost): `sc_company_name`, `sc_company_industry`, `sc_company_size`, `sc_company_founded`, `sc_company_location`, `sc_company_linkedin`, `sc_company_facebook`, `sc_company_twitter`, `sc_company_type`

## MCP Server

Configured in `/opt/data/config.yaml`:
```yaml
scrapercity:
  command: npx
  args: [-y, --package, scrapercity, scrapercity-mcp]
  env:
    SCRAPERCITY_API_KEY: 90c2ca64-81bc-48ab-a6b2-980abfaea898
  timeout: 120
```
Requires gateway restart to activate. CLI works without MCP.
