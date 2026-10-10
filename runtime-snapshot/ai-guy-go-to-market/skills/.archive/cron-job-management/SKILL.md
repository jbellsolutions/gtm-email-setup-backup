---
name: cron-job-management
description: Diagnose, pause, resume, and maintain cron jobs. When cron jobs show error status, use this skill to find root cause quickly.
---

# Cron Job Management

Diagnose and manage cron jobs running on the Hermes agent.

## Triggers

- User asks about cron jobs failing, "why are my cron jobs erroring"
- Cron jobs showing `last_status: error` across multiple entries
- Need to pause, resume, or audit scheduled jobs

## Diagnostic Flow

### 1. List all jobs
```
cronjob(action='list')
```
Look at: schedule frequency, `last_status`, `deliver` target, `enabled` state.

### 2. Check the error log
The canonical source of truth for cron failures. Check all available rotated logs to establish when the problem started:

```
tail -100 /opt/data/logs/errors.log
```

Count total failures to quantify scope:
```
grep -c "HTTP 402" /opt/data/logs/errors.log*
```

Check earlier windows to date the onset:
```
grep "cron.scheduler.*failed" /opt/data/logs/errors.log.1 | head -5
```

Log rotation: `errors.log` (current ~2 days), `errors.log.1` (prior ~2 days), `errors.log.2` (older). Same pattern for `agent.log`.

### 3. Classify the failure
Common root causes, in order of likelihood:

**Provider credits exhausted** (HTTP 402)
- Two distinct patterns: **soft limit** ("can only afford 2534 tokens" — some credits remain, large prompts fail) vs **hard limit** ("Insufficient credits" — complete exhaustion, everything fails)
- Every job fails because each cron run spawns its own agent session needing LLM access
- Early warning in agent.log: `credential pool: no available entries (all exhausted or empty)` appears before the hard 402
- Fix: add credits to the provider dashboard (e.g., openrouter.ai/settings/credits)
- Mitigation: pause high-frequency jobs first — they're hammering a dead account
- See `references/error-patterns.md` for full credit-exhaustion patterns with examples

**Missing environment variables**
- Symptom: `KeyError` or `NoneType` in script output
- The cron session may not inherit shell env vars
- Fix: ensure API keys are in `~/.hermes/.env` or gateway process environment

**Script-level failure**
- Symptom: error occurs even when running script manually
- Isolate: run the script manually from terminal to confirm: `python3 /path/to/script.py`
- If it works manually but not via cron, it's an env issue (see above)

### 4. Triage and shut off worst offenders
High-frequency failing jobs waste credits/rate limits:
```
cronjob(action='pause', job_id='...')
```

Priority order:
1. Jobs running every minute/hour (most wasteful)
2. Jobs delivering to Slack (most noisy)
3. Everything else

## Post-mortem: Verify scripts independently

After fixing the provider, verify scripts still work:
```bash
python3 /opt/data/scripts/<script>.py --once
bash /opt/data/obsidian-vault/scripts/vault-sync.sh
```

## Pitfalls

- **Don't trust `last_status: ok`** — a job may have succeeded on its last run but the next will fail if credits ran out since then
- The legacy email platform-auto-reply job (`2929988f4269`) runs every minute — if credits are out, pause it immediately to stop the hemorrhage
- Session search often won't find recent cron run transcripts; rely on `/opt/data/logs/errors.log` instead
- Scripts in `/opt/data/scripts/` may depend on env vars (`legacy email platform_API_KEY`, `DEEPSEEK_API_KEY`) — always check `echo ${VAR_NAME}` before assuming they're set
