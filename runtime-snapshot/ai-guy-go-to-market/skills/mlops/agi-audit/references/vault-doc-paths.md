# Vault Documentation Map for AI Integraterz Repos

When local clones are missing, these vault paths provide architecture documentation for documentation-only audits.

## Cold Email Pipeline (ai-integraterz-cold-email)

| Document | Path | Content |
|---|---|---|
| Architecture (full) | `domains/ai-integraterz/cold-email-architecture.md` | Squad topology, pipeline, validation gates, Slack tools, daemons, AGENTS.md, KPIs |
| Systems inventory | `domains/ai-integraterz/systems-inventory.md` | legacy email platform state, Apify, ConvertKit, Retell, cron jobs, platform roles |
| legacy email platform state | `domains/ai-integraterz/legacy email platform-state.md` | Campaign list, active campaigns, unread inbox, mailbox inventory |
| Deliverability audits | `domains/cold-email/audits/deliverability-YYYY-MM-DD.md` | Weekly bounce/reply/auth metrics, domain health, action items |
| Operations Hub | `domains/ai-integraterz/00 - Operations Hub.md` | Platform architecture, connected systems, offers, key links |
| Notion schema | `domains/ai-integraterz/notion-schema.md` | All 25 Notion database schemas |

## Content Flywheel (ai-guy-flywheel)

| Document | Path | Content |
|---|---|---|
| Systems inventory (only source) | `domains/ai-integraterz/systems-inventory.md` | Hosting (Railway), stack (Supabase/Redis), toolchain (yt-dlp/ffmpeg/Unipile/Typefully), model (Sonnet 4.5) |

No dedicated architecture document exists for the flywheel in the vault.

## Expected local clone paths (from systems-inventory.md)

- Cold email: `/tmp/ai-integraterz-cold-email` (GitHub: `jbellsolutions/ai-integraterz-cold-email`)
- Flywheel: `/tmp/ai-guy-flywheel` (GitHub: `jbellsolutions/ai-guy-flywheel`)
- Notion phase 3: `/tmp/notion-super-agent-phase-3` (GitHub: `jbellsolutions/notion-super-agent-phase-3`)

## Vault structure

```
/opt/data/obsidian-vault/
├── domains/
│   ├── agi-1/           # AGI-1 meditations, daily reports, dashboards, audits/
│   ├── ai-integraterz/  # Operations hub, architecture, Notion schema, legacy email platform state
│   └── cold-email/      # Deliverability audits
├── projects/            # Project-specific specs and handshakes
├── hermes/              # Hermes config
└── daily-logs/          # Daily operational logs
```
