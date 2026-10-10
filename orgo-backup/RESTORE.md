# Restore the Orgo application backup

Source computer: AI Guy Go To Market, `eed51fbb-8f2e-4b78-8d8f-8aa672b11df5`.

## Download and verify

Clone this private repository. Download all assets from the
[private release](https://github.com/jbellsolutions/gtm-email-setup-backup/releases/tag/orgo-gtm-2026-10-10)
to a private directory. Copy `restore-private-key.pem` from the owner's Mac
`~/Orgo GTM Private Backup 2026-10-10/`. Keep its permissions at 600.
Do not upload this key to GitHub or a ticket.

Check the individual asset SHA-256 values against `VERIFICATION.json` here.
Assemble the two multipart archives in numeric filename order:

```sh
cat orgo-gtm-application-backup.tar.gz.cms.part-* > orgo-gtm-application-backup.tar.gz.cms
cat orgo-gtm-vault-and-database-supplement.tar.gz.cms.part-* > orgo-gtm-vault-and-database-supplement.tar.gz.cms
```

Compare each assembled archive's SHA-256 with the same report. The primary-state
recovery and directory metadata are single-file assets.

## Verify and decrypt

Use Python 3 with `cryptography` installed. From the cloned repository:

```sh
python3 orgo-backup/verify-backup.py --backup-dir "/absolute/path/to/private-backup"
python3 orgo-backup/verify-backup.py --backup-dir "/absolute/path/to/private-backup" --archive-name orgo-gtm-vault-and-database-supplement.tar.gz.cms
python3 orgo-backup/verify-backup.py --backup-dir "/absolute/path/to/private-backup" --archive-name orgo-gtm-primary-state-recovery.tar.gz.cms
```

The verifier compares every member against its encrypted embedded hash manifest
and checks captured primary/profile state databases using SQLite `quick_check`.
Original capture failures remain in the first two manifests; the final combined
report explains the later recovery of both missing databases. Runtime sockets
are intentionally recreated by the restored services.

Use the streaming decoder for each archive, substituting its name:

```sh
umask 077
python3 orgo-backup/gtm_cms_stream.py orgo-gtm-application-backup.tar.gz.cms --key restore-private-key.pem > main.tar.gz
python3 orgo-backup/gtm_cms_stream.py orgo-gtm-vault-and-database-supplement.tar.gz.cms --key restore-private-key.pem > supplement.tar.gz
python3 orgo-backup/gtm_cms_stream.py orgo-gtm-primary-state-recovery.tar.gz.cms --key restore-private-key.pem > primary.tar.gz
openssl cms -decrypt -binary -inform DER -in directory-metadata.json.cms -inkey restore-private-key.pem -out directory-metadata.private.json
```

Large CMS archives exceed some OpenSSL ASN.1 buffering limits; use the included
streaming helper rather than direct OpenSSL decryption for them. The helper is
specific to this single-recipient RSA/AES-256-CBC envelope. Compare encrypted
archive hashes before decryption; CBC encryption alone is not authentication.

## Restore into a staging directory

Extract into an isolated staging directory, with services and sending jobs off.
Apply **main, then supplement, then primary** in that order. Paths in the archives
are relative copies of the original filesystem. Review `/etc` before importing
configuration into a different OS. Review ownership, mode and directory symlink
entries from the decrypted directory metadata before applying them.

Restore `/root/.hermes/state.db` from the primary archive; do not overlay old WAL
or SHM sidecars onto this consistent SQLite snapshot. The dated branch database
is historical and must retain its archival filename. It was byte/hash verified;
a full SQLite health check of that historical database was not completed.

Reinstall omitted dependencies and browser runtimes from the preserved source
and lockfiles. Browser login files were captured live and may need reconnection.
Reconcile active campaigns, suppressions, platform IDs and scheduled work with
Instantly, SMTP, Attio and ClickUp before enabling jobs. Keep sending disabled
until duplicate execution and connector checks pass.

This backup does not restore the OS or snapshot external SaaS account data.
See `VERIFICATION.json` for exact coverage and exclusions. The Mac's unrelated
files and credentials are outside this Orgo backup.
