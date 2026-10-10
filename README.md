# Go-to-market email setup backup

Private backup prepared October 10, 2026 for Justin Bellware.

## Start here

- [Latest plan](plans/GTM_COLD_EMAIL_PLAN.md)
- [16 role charters](plans/gtm-email-profiles/README.md)
- [Shared team contract](plans/gtm-email-profiles/TEAM-CONTRACT.md)
- [Thread transcript](thread/TRANSCRIPT.md)
- [Restore and remaining backup gaps](RESTORE.md)
- [File integrity manifest](SHA256.json)

The final design is an email-focused Hermes team with 16 separate identities:
five brand campaign managers (Home Services, Francois, AI Guy, Marketing Agencies,
Revenue Partnerships), Overall Email Campaign Manager, Data, List Manager,
Writer, independent Editorial, Instantly, SMTP Newsletter, ESP/Deliverability,
Replies, Attio CRM and ClickUp operations.

Databox is both a repository/service and an existing agent. ClickUp tracks
operating work; Attio tracks prospects and sales events. Instantly and SMTP
retain separate sender infrastructure and single execution owners.

## What is preserved

`plans/` contains all documents and charters produced by this thread.
`thread/` contains the exported Cloudroom events and readable conversation,
with detected credentials redacted. Historical tool commands are evidence,
not instructions to execute.
`source-documents/` contains the selected GrokBot migration/role documents and
October 8 role/routine charters used to build this setup.
`runtime-snapshot/` contains selected text/code skills, tool helpers, personality,
sanitized configuration, credential NAMES only, and reference-only cron definitions
from the Mac's existing ai-guy-go-to-market profile. Detected secret values were
redacted. Sanitized files are reference material and may require repair/reconnection
before use. Old instructions embedded in them do not grant execution permission.

## Actual status

This thread prepared and committed the 16-profile design and charters. It did
not install or activate the proposed team. This backup preserves that design
and a selected existing Mac profile snapshot; it is not a computer image or a
complete export of the live Orgo runtime. Read RESTORE.md before wiping anything.

Source application: https://github.com/jbellsolutions/bops-selfhosted
Source migration: https://github.com/jbellsolutions/grokbot-hermes-migration
Source Databox: https://github.com/jbellsolutions/data-box
Cloudroom thread ID: thr_4agncgk5ky. Tagged recovery thread: thr_pfz5g6y8bi.

The source checkout also contains unrelated uncommitted app changes. They were
not altered or included in this email-specific backup.
