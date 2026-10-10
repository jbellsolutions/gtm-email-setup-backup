# Instantly API Key — .env vs config.json Sync

## Two Key Sources

| Source | Path | Reader | Updated By |
|---|---|---|---|
| CLI config | `~/.Instantly/config.json` | `Instantly` CLI | `Instantly config set apiKey` |
| Environment | `/opt/data/.env` (line 404) | Scripts: `followup_engine.py`, `auto_reply_daemon.py`, `monitor_inbox.py`, pipelines | Manual edit |

Scripts read from `.env` via `grep Instantly_API_KEY /opt/data/.env | cut -d= -f2`.

## The Problem

When the Instantly web UI generates a new API key, operators may run `Instantly config set apiKey <new_key>` — this updates ONLY `~/.Instantly/config.json`. Scripts sourcing from `.env` continue using the stale key.

## Symptoms of Key Mismatch

- CLI works: `Instantly campaigns list` succeeds
- Scripts fail: `followup_engine.py`, daemon, and pipelines all return auth errors
- Environment: `Instantly_API_KEY` env var (set from `.env`) is stale

## Fix

```bash
# 1. Read working key from CLI config
jq -r '.apiKey' ~/.Instantly/config.json

# 2. Update .env line 404
sed -i '404s/=.*/=NEW_KEY_HERE/' /opt/data/.env

# 3. Verify both work
Instantly campaigns list --format json 2>&1 | head -1
export Instantly_API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2)
curl -s -4 "https://server.Instantly/api/v1/campaigns?api_key=$Instantly_API_KEY" | head -1
```

## History

- **Jul 25, 2026:** Config had `[REDACTED]` (updated Jul 24). .env line 404 had `6c513257-5f44-4ad1-a654-b3bedd2a36b6` (stale). Both returned plan-expired so mismatch was harmless this time — but would cause silent failures on renewal if only one is updated.