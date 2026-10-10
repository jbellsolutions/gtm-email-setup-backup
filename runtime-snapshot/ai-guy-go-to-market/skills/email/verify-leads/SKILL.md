---
name: verify-leads
description: >-
  On-demand email verification for the cold-email agent, through the self-hosted
  Reacher gateway using the agent's OWN revocable key under ONE shared 10k/24h cap
  with the dashboard. Use ONLY when explicitly asked to verify/check a list of
  addresses that landed directly in the agent (lists are normally verified on the
  dashboard BEFORE they reach the agent). Returns the SENDABLE addresses
  (deliverable + accept-all). Triggers: "verify these leads", "check this list
  before I send", "are these emails good", "clean these addresses". This does NOT
  send email and is NOT an automatic pre-send step.
---

# Verify Leads (agent gateway → self-hosted Reacher)

Verifies deliverability **without sending mail** by SMTP-probing each address
through the droplet gateway at `verify.usingaitoscale.com/verify*`. Authenticates
with the **agent's own `x-consumer-key`** — a separate, revocable key — and every
check counts against the **same hard 10,000 / 24h budget** as the dashboard.

**When to use:** only when Justin explicitly hands the agent a raw list and asks it
to verify. Lists are normally verified on the dashboard *before* entering the
agent, so this is an occasional on-demand capability — **not** a step to run
automatically before sending.

## One command

```bash
python3 tools/verify_leads.py leads.csv --json
```

- Input can be a **CSV/TXT file** (auto-extracts + de-dupes email addresses),
  **emails as arguments**, or **`-` for stdin**.
- `--json` prints a machine-readable result (use this when the agent consumes it):
  `{ok, job_id, status, total, processed, summary, sendable_count, sendable:[...]}`.
- Without `--json` it prints a human summary and lists the sendable addresses.
- `-o out/sendable.csv` also writes the sendable list to a file.
- `--status <job_id>` re-checks a job later (e.g. if a big list timed out the poll).

## Auth (already configured)

The consumer key is set in the `REACHER_CONSUMER_KEY` env var in `/opt/data/.env`.
Endpoint defaults to `https://verify.usingaitoscale.com`; override with `REACHER_URL`.

## What the result means

| In `summary` | Reacher verdict | Sendable? | Meaning |
|--------------|-----------------|-----------|---------|
| `deliverable` | `safe` | ✅ yes | Mailbox exists and accepts mail |
| `accept_all` | `risky` (catch-all / role) | ✅ yes | Domain accepts everything or it's `info@`-style — still receives your mail |
| `undeliverable` | `invalid` / disposable | ❌ no | Dead mailbox or throwaway — **hard bounces**, excluded |
| `retry` | `unknown` (greylisted / blocked) | ❌ not yet | Provider blocked the probe — re-run later with `--status` or resubmit |

## The shared cap (why 429 happens)

There is **one** 10,000-checks-per-rolling-24h budget for the whole stack, enforced
server-side. The dashboard and this agent draw from the **same pool**. 429 = pool used up.

## Performance & timeouts

- **Small lists (<200):** ~15-30 seconds
- **Medium lists (200-500):** ~60-120 seconds  
- **Large lists (500-1,000):** ~2-5 minutes
- **XL lists (1,000+):** 5-15 minutes. 300s default timeout WILL cut off — use `timeout 900` or background the process with `notify_on_complete`.
- Always background for 500+ emails to avoid Slack timeout.

## Anti-triggers (do NOT use this skill for)

- **Automatic pre-send verification** — do not wire this into the send pipeline;
  lists are verified on the dashboard before they reach the agent.
- Sending email / running campaigns (this only verifies).
- Finding or guessing addresses (no enrichment here).
- Bulk-processing a list the agent has no permission to handle.
