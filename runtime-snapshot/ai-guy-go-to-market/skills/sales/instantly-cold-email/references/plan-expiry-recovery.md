# Instantly Plan Expiry — Detection & Recovery

## Detection — TWO distinct failure modes

There are two Instantly API failure modes with identical downstream symptoms (pipeline returns false "Scanned: 0 inbox entries"). Both render all monitoring dead. Detect BOTH every run:

### Mode 1 — Plan expired (billing)
Every API endpoint returns:
```json
{"message":"Plan expired!"}
```
**The CLI symptom is misleading:** `Instantly` reports `Error: Authentication failed. Check your API key.` This is a RED HERRING — the API key is valid, the plan is expired. Do NOT waste time debugging auth. Recovery = billing top-up (renew plan in Instantly dashboard).

### Mode 2 — Invalid API Key (key rejected) — confirmed Jul 26-27, 2026
Every API endpoint returns:
```json
{"message":"Invalid API Key"}
```
CLI also reports `Error: Authentication failed. Check your API key.` — **same misleading symptom as plan expiry.** Recovery differs: Justin must generate a fresh key at `app.Instantly → Settings → API` and update BOTH `/opt/data/.env` (Instantly_API_KEY=) AND `/opt/data/config.yaml` (mcp_servers.Instantly.env.Instantly_API_KEY), then gateway-restart for MCP. This is NOT a billing top-up — the key itself is being rejected (rotated, revoked, or expired on Instantly's side). **Jul 26, 2026:** key `6c513257-...-310f55ebe030_urvd7z9` (44 chars, same in .env and config.yaml) rejected on every REST + CLI call even though non-empty and previously valid — Instantly-side revocation, not a parsing bug.

### Unified detection check (catches both)
```bash
API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2)
BODY=$(curl -s -4 "https://server.Instantly/api/v1/campaigns?api_key=$API_KEY")
# Check BOTH failure modes
if echo "$BODY" | grep -q '"Plan expired'; then
  echo "PLAN_EXPIRED"
elif echo "$BODY" | grep -q '"Invalid API Key"'; then
  echo "INVALID_API_KEY"
elif echo "$BODY" | grep -q 'Authentication failed'; then
  echo "AUTH_FAILED_UNKNOWN"
fi
```
A check that only greps for "Plan expired" will miss the auth-failure variant and report a false all-clear. Both modes have identical downstream impact: skip Part A, run Part B independently.

## Impact When Expired

| Component | Status | Impact |
|---|---|---|
| Auto-reply daemon | DEAD | All positive replies silently missed |
| Monitoring pipeline | DEAD | No inbox sweeps, no classification |
| Cross-campaign sweeps | DEAD | 9+ active campaigns unmonitored |
| Follow-up cadence engine | DEAD | All scheduled follow-ups fail silently (`followup_engine.py` exits with all ❌) |
| Instantly CLI | DEAD | All commands return auth error |
| Instantly MCP | DEAD | All MCP tools fail |
| cron jobs | DEAD | Silent runs, no work done (daemon, sweep, follow-up all impacted) |

## Recovery — Mode 1 (Plan expired)

1. Renew the plan at [Instantly dashboard](https://app.Instantly) — login: `Instantly@usingaitoscale.com` / `Instantly2026$`
2. Verify renewal: `curl -s -4 "https://server.Instantly/api/v1/campaigns?api_key=$KEY"` → should return JSON data, not "Plan expired!"
3. Re-auth CLI: `Instantly config set apiKey "$Instantly_API_KEY"`
4. Verify CLI: `Instantly campaigns list --format json` → should return campaign list
5. Re-run the daemon: `python3 /opt/data/scripts/auto_reply_daemon.py --once`
6. Run a full inbox sweep to catch any replies missed during the outage (see `cross-campaign-monitoring.md`)

## Recovery — Mode 2 (Invalid API Key) — added Jul 26, 2026

1. Justin generates a fresh API key at `app.Instantly → Settings → API`
2. Update `/opt/data/.env`: replace `Instantly_API_KEY=` value with new key
3. Update `/opt/data/config.yaml` under `mcp_servers.Instantly.env.Instantly_API_KEY`: replace with same new key
4. Gateway-restart (`/restart`) for MCP to pick up the new key
5. Re-auth CLI: `Instantly config set apiKey "$NEW_Instantly_API_KEY"`
6. Verify: `curl -s -4 "https://server.Instantly/api/v1/campaigns?api_key=$NEW_KEY"` → should return JSON data, not "Invalid API Key"
7. Verify CLI: `Instantly campaigns list --format json` → should return campaign list
8. Re-run the daemon and full inbox sweep (same as Mode 1 step 5-6)

**Key sync bug (latent):** `~/.Instantly/config.json` can have a different key than `.env` if the key was rotated via `Instantly config set apiKey` without also updating `.env`. Both must stay in sync. During the Jul 22-27 outage this didn't matter (both keys were rejected), but on future recovery this is a latent sync bug.

## Pre-Check for ALL Instantly-Touching Cron Jobs

**As of Jul 27, 2026:** The pre-check mandate is broadened from "monitoring pipelines" to ANY cron job that calls Instantly CLI, MCP, or REST — including the daily-report cron (`059d56c4dfc4`, `cold-email-daily-report`), the auto-reply daemon (`2929988f4269`), the SpeakerAgent pipeline (`148920b114d6`), the follow-up cadence engine (`ac18c07f72f9`), the OA pipeline (`9be604c0cbce`), the Wednesday reply sweep (`84d1b41ab987`), the Monday deliverability audit (`dc8f48392fc1`), and the Notion sync (`13dd6ded3007`). **Every one of these must run the unified detection check as STEP -1 before any Instantly call.** If the API is down, skip all Instantly operations and deliver the operator-action report directly — do NOT spend calls rediscovering the auth failure.

**Built-in health checks (already wired):**
- `monitor_pipeline.py` in the `owned-audiences-email-reply` skill — exits code 2 if API is down. Calling `python3 scripts/monitor_pipeline.py --pages 3` is safe.
- The combined reply-monitoring + pre-call-report cron (`2929988f4269`) has the pre-check documented in its prompt and reference.

**⚠️ GAP (Jul 23 2026, still open Jul 27):** The cron job at `/opt/data/scripts/owned_audiences_pipeline.py` does NOT have the same health check as `scripts/monitor_pipeline.py`. It still silently returns `Scanned: 0 inbox entries` with exit code 0 when the API is down. Until `owned_audiences_pipeline.py` is updated with the health check, cron agents MUST run the manual health check (STEP -1) BEFORE invoking the pipeline — not after. A second false all-clear at 02:01 UTC confirmed the gap still exists.

**⚠️ GAP (Jul 27, 2026):** The daily-report cron (`059d56c4dfc4`) prompt instructs the agent to call `mcp_Instantly_get_campaign_analytics_by_date` and `mcp_Instantly_get_campaign_statistics` as step 1-2, with NO pre-flight auth check. On Jul 27 21:00 UTC (day 6 of the Mode 2 outage), the daily-report agent spent ~10 tool calls rediscovering the auth failure (CLI auth error → REST probe → wrong base URL → correct base URL → 401 → consulting this reference) before reaching the known-outage conclusion. **Fix for the cron agent:** before step 1, run the unified detection check below. If `INVALID_API_KEY` or `PLAN_EXPIRED`, skip to the operator-action report (the recovery steps are already documented here) — do NOT call MCP/CLI analytics endpoints, they will all fail. Update the cron prompt to include this pre-flight if the curator can edit `jobs.json`.

For ad-hoc cron agents or manual sweeps, run the detection check manually. If plan is expired or key is invalid, report immediately and skip all Instantly operations:

```python
import subprocess, json

api_key = ... # from .env
result = subprocess.run(['curl', '-s', 
    f'https://server.Instantly/api/v1/campaigns?api_key={api_key}'],
    capture_output=True, text=True, timeout=10)
try:
    data = json.loads(result.stdout)
    if data.get('message') == 'Plan expired!':
        print('🚨 Instantly PLAN EXPIRED — all monitoring blocked')
        # Skip all Instantly operations, report to operator
        return
except json.JSONDecodeError:
    pass  # Normal response — plan is active
```

## What Still Works During Expiry (Cron Agent Instructions)


### ⚠️ IPv6 Connectivity — Always Use `-4` for Instantly Curl Calls

This VPS has **IPv6 disabled** (`Network is unreachable`). `server.Instantly` resolves to IPv6 addresses first, so plain `curl` hangs/fails. Always force IPv4:

```bash
curl -s -4 "https://server.Instantly/api/v1/campaigns?api_key=$API_KEY"
```

The Instantly CLI (`Instantly`) and MCP (`npx Instantly-mcp`) are unaffected — they use Node.js's HTTP client. But manual curl-based health checks, REST API probes, and Python `subprocess.run(['curl', ...])` calls MUST include `-4`. **Jul 24, 2026:** health check returned empty string with `curl -s` (IPv6 fail), correctly returned `{"message":"Plan expired!"}` with `curl -s -4`.

When the combined cron job (reply monitoring + pre-call reports) hits a plan expiry:

1. **Skip Part A entirely** — no Instantly inbox, no classification, no reply handling. Don't retry or waste time.
2. **Proceed to Part B** — pre-call reports from Cal.com are independent of Instantly. Use the live Cal.com REST API (`CALCOM_API_KEY`, curl via subprocess) and `cal_bookings.json` as supplement. Check existing reports under `clients/*/pre-call-report.md`.
3. **Report the expiry prominently** — a plan expiry is NEVER a [SILENT] event. Always include the expiry alert as the primary finding, with recovery steps.
4. **Don't go [SILENT] just because Part A produced nothing** — if Part B found reports to verify or generate, report them. If all reports already exist and are current, include that status alongside the expiry alert.
5. **Pre-call reports that depend on Instantly thread data** (campaign leads, message history) will have incomplete Section 1. That's fine — flag it in Open Items and note "Instantly unavailable — thread data incomplete." Direct/inbound Cal.com bookings don't need Instantly at all and can be generated fully.

## History

- **Jul 27, 2026 21:00 UTC (daily-report cron `059d56c4dfc4`):** Fifteenth+ consecutive detection (Mode 2 — Invalid API Key). The daily-report cron agent had NO pre-flight auth check in its prompt — it spent ~10 tool calls rediscovering the outage (CLI `Error: Authentication failed` → REST probe with wrong base URL `api.Instantly` (404) → correct base `server.Instantly` → 401 `{"message":"Invalid API Key"}` → consulting this reference) before reaching the known conclusion. Root cause: the cron prompt jumps straight to `mcp_Instantly_get_campaign_analytics_by_date` as step 1. **Fix applied to this reference:** broadened the pre-check section to cover ALL Instantly-touching cron jobs (not just monitoring pipelines) and documented the daily-report cron gap explicitly. Recovery unchanged: Justin must regenerate the key (Mode 2), not renew the plan. CLI symptom (`Authentication failed`) is identical for Mode 1 and Mode 2 — only the REST body distinguishes them (`Plan expired!` vs `Invalid API Key`).

- **Jul 27, 2026 11:02 UTC:** Fourteenth+ consecutive detection (Mode 2 — Invalid API Key). REST + CLI both dead. Same pattern as Jul 22-26. Daemon state file (`auto_reply_state.json`) still Jul 22 — 5 days stale (secondary confirmation). OA state file (`owned_audiences_followups.json`) updated 07:01 UTC but pipeline found 0 entries (false all-clear — 14th confirmation the pipeline lacks the health check). Dashboard ran from state file: `90 leads, 0 awaiting_followup, 1 booked, 81 dead, 4 plan_built, 4 replied` — steady state. Part B (Cal.com) ran independently with dual validation pull (identical responses): 3 upcoming prospect bookings confirmed live — Johanna Watson (Mon Jul 27 12:30 PM ET, ~1.5h to call), Owais Tariq (Mon Jul 27 1:30 PM ET / 11 PM IST, ~2.5h, timezone anomaly STILL unresolved), Thomas K. Johnston (Wed Aug 12, far-future). All three pre-call reports exist and current — both same-day reports refreshed at 07:30 UTC, re-verified at 11:02 UTC. Owais timezone anomaly (11 PM IST Monday night) flagged in report for immediate operator action: if Justin has not sent a confirmation email, DO SO NOW. No new bookings, no cancellations. No new reports generated — all existing. Recovery: Justin must regenerate the API key (Mode 2 recovery), not renew the plan.

- **Jul 25, 2026 12:32 PM ET:** Tenth consecutive detection. Plan still expired (no renewal since Jul 22 — 3+ days). REST API returns `{"message":"Plan expired!"}` HTTP 401 on all endpoints (campaigns, inbox, leads, message history). OA pipeline (`owned_audiences_pipeline.py`) again returned false `Scanned: 0 inbox entries` exit code 0 — still lacks health check (10th confirmation). Daemon state file (`auto_reply_state.json`) last updated Jul 22 19:08 UTC — 3 days stale. No drafts file present. Part B (Cal.com) ran independently: live API pulled twice (validation pass — both consistent, 5 bookings). All 4 prospect-facing reports already fresh (artemis-hou 2h old, salesrobot 2h old, synova-search 4h old, agentmail 4h old). Zoom links verified HTTP 200. Two internal meetings correctly skipped (Evan Dantes Customer Support Sync, Binoy Perera 30 Min Meeting — but Binoy's IS a peer/partnership call per agentmail report, not truly internal). Timezone anomaly on Owais Tariq persists (11 PM IST Mon night). No new bookings, no cancellations. No new reports generated — all existing. Recovery unchanged: plan renewal required.

- **Jul 25, 2026 09:00 AM ET:** Ninth consecutive detection. Plan still expired (no renewal since Jul 22). Follow-up cadence engine ran — all 10 sends failed (9 SpeakerAgent + 1 Owned Audiences). SpeakerAgent leads now 4+ business days overdue for follow-up #3 (last contact Jul 20): Kyle Wolfe (3 follow-ups, at risk of going cold), Nicole Wald, Scott Kaier, Spark (deep-funnel, 13-message thread, already agreed to pricing). Owned Audiences: Jeff Dillon's first follow-up blocked; Vivian, Scaledown, Ember Medical have never been contacted. Gina Karnisovas remains the sole booked lead (Jul 21 call). No new Cal.com bookings. Cal.com v2 API note: status filter must use `upcoming`/`recurring`/`past`/`cancelled`/`unconfirmed` — `accepted` is not valid for the /v2/bookings endpoint (returns BadRequestException). Engine's `Instantly_API_KEY` sourced from `.env` line 404 (stale key `6c513257-5f44...`) while `~/.Instantly/config.json` had updated key (`...310f55ebe030_urvd7z9` updated Jul 24) — both keys return plan-expired so key mismatch didn't matter this time, but is a latent sync bug for future renewals. Plan still expired (no renewal since Jul 22). Pre-check via REST API caught it immediately. Part A (reply monitoring) fully blocked — all 9+ active campaigns unmonitored. Part B (Cal.com pre-call reports) ran independently: light-refreshed Johanna Watson (artemis-hou, Mon Jul 27 12:30 PM) and Owais Tariq (salesrobot, Mon Jul 27 1:30 PM, timezone anomaly re-verified at 11 PM IST). Thomas K. Johnston (Aug 12) far-future, no refresh needed. Two TBD reports (teachercast, aes-recruitment) still unconfirmed — cannot scan Instantly threads for updates. DDG research blocked by rate limit from earlier pipe-to-interpreter attempts (new pitfall: security-scanner blocks on `curl | python3` still fire curl, consuming DDG quota). Reports refreshed using existing research only. `owned_audiences_pipeline.py` still lacks health check — cron agents MUST run manual pre-check. No cancellations detected between two API validation calls.

- **Jul 23, 2026 18:04 UTC:** Fifth detection. Plan still expired (no renewal since Jul 22). Health check (STEP -1) caught it immediately — no false all-clear produced. Part B (Cal.com pre-call reports) ran independently: all 4 upcoming calls verified ready (Erin Todus Jul 24, Johanna Watson Jul 27, Tom Johnston Aug 12; John Compton Sunray Councils cancelled between API calls). Erica Todus game plan still "QUEUE NOW" — deadline passed (was due Jul 23). Confirmed again: when Instantly is down, Part B operates normally with Cal.com data independent of Instantly. The `owned_audiences_pipeline.py` at `/opt/data/scripts/` STILL lacks the health check (5th confirmation of the gap). Cron agents MUST run STEP -1 manual pre-check before invoking it.

- **Jul 23, 2026 02:01 UTC:** Second false all-clear confirmed. `owned_audiences_pipeline.py` ran again, same result: `Scanned: 0 inbox entries`, exit code 0. Confirmed 401 from both CLI and MCP — plan still expired. Part B (Cal.com) ran independently: 3/4 pre-call reports confirmed ready (John Compton today Jul 23, Erin Todus Jul 24, Tom Johnston Aug 12). Johanna Watson (Jul 27) is missing a pre-call report — needs generation once Instantly is restored for Section 1 thread data, or can be generated with "Instantly unavailable — thread data incomplete" flag. Pipeline still lacks health check — cron agents must run manual pre-check before invoking.

- **Jul 23, 2026 02:01 UTC:** Second false all-clear confirmed. `owned_audiences_pipeline.py` ran again, same result: `Scanned: 0 inbox entries`, exit code 0. Confirmed 401 from both CLI and MCP — plan still expired. Part B (Cal.com) ran independently: 3/4 pre-call reports confirmed ready (John Compton today Jul 23, Erin Todus Jul 24, Tom Johnston Aug 12). Johanna Watson (Jul 27) is missing a pre-call report — needs generation once Instantly is restored for Section 1 thread data, or can be generated with "Instantly unavailable — thread data incomplete" flag. Pipeline still lacks health check — cron agents must run manual pre-check before invoking.

- **Jul 23, 2026 00:00 UTC:** Pipeline false all-clear confirmed. `owned_audiences_pipeline.py` ran, scanned 0 inbox entries, exit code 0, output `"Scanned: 0 inbox entries | New positives: 0 | 0 awaiting"`. Dashboard showed 90 tracked leads with 0 awaiting follow-up — completely normal. But every Instantly API call (CLI, MCP, REST) was failing. The pipeline's `sl()` function silently returned `None` on non-zero exit codes, making `inbox_page()` return `[]` — indistinguishable from a genuinely empty inbox. **No alert was raised.** The "0 new positives" report was a false all-clear. New replies since the plan expired are invisible. This is a critical monitoring blind spot: any cron job or pipeline that wraps Instantly CLI calls must detect API failures and report them, not silently return zeros.

- **Jul 22, 2026:** Plan expired mid-week. 9 active campaigns unmonitored for unknown duration. All monitoring sweeps blocked. Daemon silent (no Slack notifications to alert operator). Detected during routine cron sweep when inbox pull returned auth error. Pre-call reports from Cal.com continued working independently — all 4 upcoming calls (John Compton Jul 23, Erin Todus Jul 24, Johanna Watson Jul 27, Thomas Johnston Aug 12) had reports already generated by prior runs. Josh Hamilton's same-day call (Jul 22, 12:30 PM ET) was confirmed and accurate. No new bookings found. Cron adapted: skipped Part A (Instantly-dependent monitoring), completed Part B (Cal.com pre-call report verification), reported expiry prominently.