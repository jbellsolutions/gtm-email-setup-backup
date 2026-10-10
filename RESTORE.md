# Restore instructions and backup boundaries

## Restore the preserved setup

1. Clone this private repository with your GitHub account.
2. Verify SHA256SUMS against every listed file before restoring.
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

## Restore the Orgo computer

Use [the encrypted application backup guide](orgo-backup/RESTORE.md).
The private release preserves application files, credential files, Hermes
history/state, uploaded data and GTM vault content from the identified Orgo
computer. Sensitive contents are encrypted; the key remains on the Mac.
Keep that key somewhere independent of any computer you wipe.

## Backup boundaries

- This is an application export, not a full bootable disk image. See the exact
  roots and cache/dependency/historical-duplicate exclusions in the Orgo report.
- Instantly, Listmonk, Attio, ClickUp and Databox service-side records remain
  external; GitHub does not snapshot those services.
- Mac keychain data, unrelated Mac files and unrelated uncommitted Bops app
  changes are outside this Orgo backup.
- The full raw GrokBot machine image is outside this email-specific repository;
  selected role sources and the current Orgo application files are preserved.
- A live file export spans time. SQLite online snapshots were used for supported
  application databases; browser files were copied live and may need new logins.

Follow the verification report when deciding what to restore. Review all restored
jobs and sending infrastructure before activation to avoid duplicate sends.
