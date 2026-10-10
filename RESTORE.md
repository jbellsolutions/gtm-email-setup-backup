# Restore instructions and backup boundaries

## Restore the preserved setup

1. Clone this private repository with your GitHub account.
2. Verify SHA256.json against every listed file before restoring.
3. Read plans/GTM_COLD_EMAIL_PLAN.md, the profile-pack index, and TEAM-CONTRACT.md.
4. Audit the new machine's installed Hermes version and actual supported profile,
   skill and gateway commands. These charters are not executable profile installs.
5. Create the 16 profiles using their charters, separate state directories and
   least-privilege tool access. Reuse the curated skills only after reviewing paths,
   redactions, current provider APIs and source dependencies.
6. Reconnect credentials securely. The credential-names file contains names,
   never values. Recreate needed browser logins rather than importing this backup
   as authenticated browser state.
7. Reconcile existing platform campaign IDs, suppression history, contact records,
   sender pools and active/paused status before importing batches or enabling jobs.
8. Validate the experiment plan's replay/shadow and connector checks. Keep jobs,
   sending and messaging consumers disabled until their appropriate release.
9. If installing Better Than GrokBot, follow its current INSTALL.md and startup
   checklist. This backup does not establish those checks have passed.

## Not included: preserve separately before a computer wipe

- Secret values, .env files, OAuth tokens, keychain credentials and browser cookies.
- Hermes session/state/memory databases, private contact datasets, uploaded files,
  complete run outputs and live Orgo filesystem contents.
- A full machine snapshot, all Mac files, or the 6.7 GB existing profile tree.
- Unrelated uncommitted Bops application changes in the source checkout.
- The entire 1.8 GB raw GrokBot machine backup and all later source-project files.
- External Instantly, Listmonk, Attio, ClickUp and Databox SaaS/server data. A Git
  repository does not snapshot those services or their current configuration.

For an Orgo wipe, capture a provider-supported snapshot or an independently
verified private export of that specific computer's files and live configuration.
For a Mac wipe, preserve the local source projects, raw backups, keychain access,
Hermes history and other required files in a separately verified encrypted backup.
Keep decryption credentials somewhere that will survive the wipe.

This repository is a verified sanitized setup/thread backup. It does not establish
that either computer is safe to wipe. The backup request's computer choice was
still awaiting clarification when this package was prepared.
