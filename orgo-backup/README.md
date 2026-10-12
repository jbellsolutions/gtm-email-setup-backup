# Orgo go-to-market backup

Source: **AI Guy Go To Market**, computer `eed51fbb-8f2e-4b78-8d8f-8aa672b11df5`.
Captured October 10, 2026. This extends the thread/design backup with encrypted
application data from the actual Orgo computer.

The release contains numbered main-archive parts, a vault/database supplement,
a separate consistent primary-state recovery archive, and encrypted directory metadata. Download every listed asset from the
[Orgo backup release](https://github.com/jbellsolutions/gtm-email-setup-backup/releases/tag/orgo-gtm-2026-10-10).
Compare their hashes to the verification report before decrypting.

The private restore key is retained on the owner's Mac in:
`~/Orgo GTM Private Backup 2026-10-10/restore-private-key.pem`.
**It is not stored in GitHub. Preserve that folder; losing the key loses access.**

The main export covers selected application files in `/root`, `/home`, `/opt`,
`/usr/local/bin`, `/usr/local/lib/hermes-agent` and `/etc`. The companion covers
`/srv`, `/workspace`, `/data`, Orgo/Tailscale state, and separately recovered
Hermes historical state. The primary-state recovery archive contains the current
Hermes database. The restore report records exactly what was excluded.
Dependency/cache directories and named historical backup/export directories are
omitted. Runtime sockets are not useful restore artifacts and are recreated.

This is **application-data backup**, not a bootable disk image. Browser state is
captured live and may need fresh logins. SaaS/provider data remains external.
Reinstall omitted dependencies and review scripts, service startup, cron and
webhooks before enabling them. Do not overwrite a running system wholesale.

Read [restore instructions](RESTORE.md). Use [the streaming decryptor](gtm_cms_stream.py)
and [the archive verifier](verify-backup.py). They use Python's `cryptography`
package, available on the owner's Mac. OpenSSL's direct CMS decoder can fail on
archives above its ASN.1 buffering limit, so use the streaming helper for large
files. The small directory metadata companion can use direct OpenSSL.

## Computer replacement on October 11, 2026

The owner explicitly authorized deletion of the source after stating the backup
was verified. The original Orgo computer was deleted and replaced with a fresh
**Demand Gen** computer, `e0edd823-cfd9-44b9-9434-9d8d81f24b0f` (8 GB RAM,
2 CPUs, 80 GB disk). Running state and absence of old GTM paths were checked.
See [reset record](RESET-2026-10-11.json).

The encrypted release assets still matched their recorded GitHub digests.
At this later check, the original Mac key folder was missing and its current
location could not be verified. The original private key remains required to
decrypt those assets. The archives remain the October 10 capture; changes made
afterward were not exported before the owner-authorized deletion.
