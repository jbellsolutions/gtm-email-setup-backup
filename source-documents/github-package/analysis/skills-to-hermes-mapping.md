# Skills and MCP connectors → Hermes migration map

Source: `../Grok Bot Backup 2026-10-07/HANDOFF-2026-10-07-v2.md` §5.4, §6, and `~/lead-radar` repo skill. Planning only.

## A. The 15 user skills (+1 repo skill)

Port priority is by how often the source prompts cite each skill.

| Skill | Verdict | Home in Hermes | Notes |
|---|---|---|---|
| `instantly-custom-campaign-formatting` | **Port first** | `instantly` skill (shared with `email-writer`) | Split plain-text custom vars + HTML `<br>` between paragraphs, unsubscribe line, step delays, second-agent QC before upload. Load-bearing for every campaign build. |
| `instantly-unused-inbox-pool` | **Port first** | `instantly` skill | New campaigns take SINs only from the unused pool; reserved tags AI Guy 100 / RevPartners 300 / Agency 100→90 / HomeServices 200 / Influencer 100; AgentMail 149 excluded from cold. Inventory sheet path must be updated to the new store. |
| `overdeliver-email-doctrine` | **Port first** | `editorial` skill (shared with `email-writer`) | List 40–41% / Offer 39–40% / Copy 20%; first touch gives; never fabricate; pay postage. Replaces several duplicated prompt paragraphs. |
| `universal-referral-partner-instantly-build` | **Port first** | `email-writer` skill | ≤120-word main email, five paragraphs + standalone tracked line + call-time line, then the formatting skill. Underlies Agency/RevPartners/HS referral copy. |
| `bill-mueller-email-voice` | **Port first** | `newsletter-flagship` skill (shared warm voice) | Story-lead, plain text, self-deprecating, teach-first. Newsletter voice. |
| `listmonk` | **Port first** | `newsletter-smtp` skill | Listmonk REST API ops; sliding-window throttle (~2,000/h); separate FROM identity. |
| `revenue-partner` | Port | `campaign-revpartners` skill | GTM Money Desk: fit, mapping, campaigns, approval-gated outreach. |
| `instantly-reply-slack-notify` | Port (optional) | `replies` skill | Slack notify on inbound replies; GHL tagging is legacy — retire the GHL push (billing blocked since 2026-09-15, queue parked). |
| `solar-instantly-reply` | Defer | with solar lane | Solar/open-door is paused; it exists only as a Men's Health waterfall source. Revive only if the lane returns. |
| `campaign-manager-daily` | Merge | absorbed into ops **campaign-control skill** | Legacy Caitlyn/Funding/Connected-Med buckets are dead; do not port dead lanes. |
| `chatgpt-image-generation` | Optional | `ops` content skill via Orgo browser seat | Needs signed-in ChatGPT; one new chat per image. Only if content cadence resumes. |
| `pricing-and-payout-reconciliation` | Defer | with peptide project | Peptide-era; dormant. |
| `provider-operations` | Defer | with peptide project | Peptide-era; dormant. |
| `revenue-and-crm` | Merge | absorbed into `crm` profile contracts | Website/provider leads, attribution, partner stages — covered by Attio schema work. |
| `support-and-escalation` | Defer | with peptide project | Peptide-era; dormant. |
| Lead Radar repo skill (`~/lead-radar/skills/lead-radar/SKILL.md`) | **Port first** | `lead-radar` skill | Already repo-portable; read hosted results, do not duplicate the hosted scheduler. |

Six skills were cited by most agent prompts (`instantly-custom-campaign-formatting`, `instantly-unused-inbox-pool`, `overdeliver-email-doctrine`, `universal-referral-partner-instantly-build`, `bill-mueller-email-voice`, `listmonk`) — port those before anything else.

## B. MCP connectors: ~40 listed, ~15 load-bearing

Do not port connector sprawl. Reconnect only what's used, and prefer scoped single-writer adapters (with the API key behind the adapter) over sharing full credentials across research profiles. All MCP/OAuth grants authenticate through Justin's Grok Bot/Cursor account — **none were preserved by the backup**, so everything must be re-authed after standing up Hermes.

| Keep (used) | Notes |
|---|---|
| Instantly | API v2 keyfile path; sole `instantly` writer adapter |
| Attio (+ Official) | sole `crm` writer; schema work after Revenue Engine decisions |
| ClickUp | sole ops adapter; ~300 calls/day shared cap → batch, never poll |
| beehiiv | flagship publication only |
| Notion | one-way mirror from the vault |
| Gmail / Google Calendar / Drive / Sheets | Call Prep one-pagers, calendar scans, dumps |
| Slack | exception notifications; #grokbot-bridge listener decision pending |
| Resend / Bird | SMTP transports; Bird on HOLD, Resend CNAME blocker |
| HeyGen | content/avatar, optional |
| AgentMail | bot inboxes; 149 SINs excluded from cold |
| outflo | replies-only |
| Unipile dashboard (Railway web app, not an MCP) | keep as-is; do NOT replace with a separate Unipile API |
| Treg | data marketplace; needs a top-up; never route GetLeads/MoltSets through it |

| Drop / ignore | Airtable, Apify, Appwrite, Browserstack, Cloudflare bindings (DNS edits stay manual/Justin-scoped), Composio, Context, Finance-xai, Firebase, Gitbook, Higgsfield, Linear, Lovable, Mcp-search, Roboflow, Tavily, Tldraw, Vercel, X, autosize/auto variants, discolike (via data-box HTTP), browser-use/super-browser (replaced by Orgo browser seats), cursor-github/cursor-origin (platform-specific). |

## C. Platform-managed skills that do NOT port

`routines`, `send-on-behalf`, `sign-in`, site playbooks are Grok platform features. Their replacements: Hermes scheduled/webhook/`no_agent` jobs, sole-executor adapters with idempotency keys, and Orgo authenticated browser seats (isolated Chrome profiles per account, serialized per desktop). Grok-managed warmup ("sign-in") habits become documented adapter procedures.

## D. Secrets boundary (unchanged, worth restating)

The backup archive contains live credentials. The planning package must never include secret values, `profile.json` blobs, browser cookies or old agent IDs. Every key gets re-issued or re-granted in the new runtime: rotate `LEAD_WAREHOUSE_DB_PASSWORD` first (it is short, guessable, and doubled as a folder name), then reconnect MCP grants, then move provider keys into the one adapter that needs each.