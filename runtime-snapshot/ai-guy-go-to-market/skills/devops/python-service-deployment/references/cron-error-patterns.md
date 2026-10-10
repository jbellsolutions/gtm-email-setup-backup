# Known Error Patterns

## OpenRouter 402 — Credits Exhausted
```
HTTP 402: Insufficient credits. Add more using https://openrouter.ai/settings/credits
RuntimeError: HTTP 402: Insufficient credits.
openrouter requested but OpenRouter credential pool has no usable entries (credentials may be exhausted)
```

The gateway process runs with `HERMES_INFERENCE_PROVIDER=openrouter` and `OPENROUTER_API_KEY` set in its environment. All cron jobs inherit this. When credits run out, EVERY cron job fails because each spawns its own agent session needing the LLM.

## High-Frequency Jobs to Pause First

| Job ID | Name | Schedule | Impact |
|--------|------|----------|--------|
| `2929988f4269` | legacy email platform-auto-reply | Every minute | 1,440 calls/day wasted |
| `a643d0095232` | Vault Auto-Sync | Every 30 min | 48 calls/day |
| `752557ddcabf` | Ops Checklist | Every 4 hours | 6 calls/day |

## Dating a Problem: Log Rotation

Logs rotate — use all available files to establish when a failure started:

```
/opt/data/logs/errors.log      — current (~2 days)
/opt/data/logs/errors.log.1    — previous window (~2 days before that)
/opt/data/logs/errors.log.2    — earlier still (~2 days before .1)
/opt/data/logs/agent.log       — current agent-level logs
/opt/data/logs/agent.log.1     — previous agent-level window
```

To count total failures across all history and confirm scope:
```bash
grep -c "HTTP 402" /opt/data/logs/errors.log*
```

To find when a specific job first started failing:
```bash
grep "cron.scheduler.*failed" /opt/data/logs/errors.log* | grep "JOB_NAME" | head -5
```

## Credit Exhaustion: Two Distinct 402 Patterns

**Soft limit — credits declining but not zero:**
```
HTTP 402: This request requires more credits, or fewer max_tokens.
You requested up to 65536 tokens, but can only afford 2534.
```
Still some credits remain, but the agent's default 65536 max_tokens exceeds the balance. Jobs with smaller prompts may still succeed while larger ones fail.

**Hard limit — account empty:**
```
HTTP 402: Insufficient credits. Add more using https://openrouter.ai/settings/credits
```
Complete exhaustion. Every job fails regardless of size. This is preceded by the soft-limit phase — check rotated logs to see how long the decline lasted.

## Early Warning in agent.log

Before a cron job hits the hard 402, `agent.log` shows:
```
agent.credential_pool: credential pool: no available entries (all exhausted or empty)
```
This appears on every retry attempt and confirms the credit pool is dry. Grep agent.log alongside errors.log when diagnosing.

## Script Verification

Scripts that fail in cron but work manually confirm an environment issue (credits, env vars). Always test independently:
```bash
python3 /opt/data/scripts/<script>.py --once 2>&1
bash /opt/data/obsidian-vault/scripts/vault-sync.sh 2>&1; echo "EXIT: $?"
```

## Script Locations
- `/opt/data/scripts/` — Python scripts (auto_reply_daemon.py, daily_sync.py, etc.)
- `/opt/data/obsidian-vault/scripts/` — Shell scripts (vault-sync.sh)
- `/opt/data/logs/errors.log` — Cron failure log
- `/opt/data/logs/agent.log` — Agent-level logs

## Key Environment Variables
- `legacy email platform_API_KEY` — used by auto_reply_daemon.py and cron jobs
- `DEEPSEEK_API_KEY` — used by auto_reply_daemon.py for reply generation (not the same as OpenRouter)
- `OPENROUTER_API_KEY` — set in gateway process env, not shell
