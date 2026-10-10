# Instantly auth-failure vs plan-expiry — discrimination guide

Instantly has TWO distinct outage classes that the CLI collapses into the same error string. REST is the discriminator.

## Symptom matrix

| Class | REST response | CLI response | Root cause | Recovery |
|---|---|---|---|---|
| **Plan expiry** | `{"message":"Plan expired!"}` | `Error: Authentication failed. Check your API key.` | Billing — plan lapsed, no credits | Top up plan at app.Instantly → billing; key is still valid. See `plan-expiry-recovery.md`. |
| **API key invalidated** | `{"message":"Invalid API Key"}` | `Error: Authentication failed. Check your API key.` (identical) | Key rotated/revoked/expired on Instantly's side | Generate fresh key at `app.Instantly → Settings → API`; update BOTH `/opt/data/.env` (`Instantly_API_KEY=`) AND `/opt/data/config.yaml` (`mcp_servers.Instantly.env.Instantly_API_KEY`); gateway-restart for MCP. |

**Critical:** The CLI string `Error: Authentication failed. Check your API key.` is AMBIGUOUS — it fires for both classes. Always verify via REST (`curl /api/v1/campaigns?api_key=...`) and read the response body. Do NOT attempt recovery steps for the wrong class.

## Silent-failure mode (both classes)

`owned_audiences_pipeline.py --once` returns:
```
Scanned: 0 inbox entries
New positives this run: 0
Auto-replies sent: 0
Pipeline state: ...
```
with exit code 0. Indistinguishable from a genuinely empty inbox. The production pipeline at `/opt/data/scripts/owned_audiences_pipeline.py` lacks the health check. The bundled `scripts/monitor_pipeline.py` HAS the health check (exit code 2 on API failure). Until the production pipeline is patched, always run the REST pre-check BEFORE invoking it.

## Pre-check (fastest, no CLI ambiguity)

```bash
API_KEY=$(grep "^Instantly_API_KEY=" /opt/data/.env | sed 's/^Instantly_API_KEY=//')
curl -s "https://server.Instantly/api/v1/campaigns?api_key=$API_KEY" | head -c 50
```
- `{"message":"Plan expired!"}` → plan expiry
- `{"message":"Invalid API Key"}` → key invalidated
- `{"ok":true...` / `{"data"...` → healthy, proceed

## What to do when Instantly is down (either class)

1. **SKIP all Part A operations** — inbox monitoring, reply classification, message-history pulls, lead uploads, campaign updates. None will work.
2. **RUN Part B independently** — Cal.com pre-call reports. The Cal.com API (`CALCOM_API_KEY`) is a separate account and credential, unaffected by Instantly outages. Pull live bookings, generate/refresh pre-call reports, flag email-thread bookings, surface timezone anomalies. This is mandatory, not optional.
3. **Report the outage** to the operator immediately — call out the class (plan-expiry vs key-invalidation) and the specific recovery action (billing top-up vs key rotation + dual-file update).
4. **State snapshot via dashboard** — `owned_audiences_dashboard.py` reads only `/tmp/owned_audiences_followups.json` (no API calls). Run it after the health check fails so the operator still gets a state report (lead counts, status distribution, booked count).

## Incident log

**Consolidated detection log:** `owned-audiences-email-reply` skill → `references/Instantly-api-outage-log.md` maintains the full day-by-day table of all detections (detection #, REST response, pipeline output, daemon state, dashboard output, Part B status). New detections should be appended there.

**Summary as of Jul 29, 2026 14:00 UTC (17th detection):**
- Outage began ~Jul 22, 2026 — ongoing for 7+ days
- First ~6 detections were "Plan expired!" (plan expiry class)
- Since Jul 26: "Invalid API Key" (key invalidation class) — even the `/campaigns` endpoint is dead
- Production pipeline still lacks health check — returns false "Scanned: 0" every run
- Daemon state file (`auto_reply_state.json`) stale since Jul 22 — 7 days, secondary confirmation (643 replied_message_ids from pre-outage)
- Pipeline state files (`speakeragent_followups.json`, `owned_audiences_followups.json`) now empty — `leads: {}`, all stats 0
- Cal.com Part B fully independent — unaffected by Instantly outage
- **Recovery NOT yet applied** — Justin needs to generate fresh API key and update both config files
- Key in .env is corrupted: `[REDACTED]` has `_urvd7z9` suffix (not valid UUID format). Even the clean UUID is rejected — key was rotated/revoked on Instantly's side.

- **Jul 26, 2026 06:02 UTC:** Key `6c513257-...-310f55ebe030_urvd7z9` (44 chars, same value in `/opt/data/.env` and `/opt/data/config.yaml` MCP env) rejected on every REST + CLI call. Pipeline returned false `Scanned: 0`. Cal.com Part B confirmed both Jul 27 prospect calls (Johanna Watson 12:30 PM ET, Owais Tariq 1:30 PM ET) with reports already refreshed that day. Dashboard returned: 90 leads, 0 awaiting_followup, 1 booked, 81 dead, 4 plan_built, 4 replied. Distinguished from the 10 prior consecutive plan-expiry detections by the REST `"Invalid API Key"` string.

- **Jul 29, 2026 14:00 UTC:** 17th detection. Same `Invalid API Key` REST response. Daemon state file still stale from Jul 22 (643 replied_message_ids, 40 hostile_senders, 31 unsub_senders). Both pipeline state files now empty — `speakeragent_followups.json` and `owned_audiences_followups.json` show `leads: {}` with all stats at 0. Wednesday positive reply sweep blocked entirely. Cron task specified campaigns 3249954/3249956 — stale IDs not in active campaign list (active: 3577260, 3639259, 3652623, 3652624, 3691319, 3692104, 3607306). Even with API restored, the cron would sweep wrong campaigns. No positives identified — 7 days of replies completely invisible.