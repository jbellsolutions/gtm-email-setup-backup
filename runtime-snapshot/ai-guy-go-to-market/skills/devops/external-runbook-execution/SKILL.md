---
name: external-runbook-execution
description: "Run supplied runbooks safely: mask secrets, stop on error."
version: 1.0.0
author: Hermes background curator
license: MIT
metadata:
  hermes:
    tags: [runbooks, onboarding, credentials, security, verification]
---

# Executing Supplied Runbooks Safely

Use when the user supplies a multi-step operational runbook to execute on this box — onboarding docs, setup scripts, migration checklists, usually as a file attachment with rules like "follow exactly, stop on any failure" — especially when it embeds credentials, credential placeholders, or privileged operations (config edits, service restarts, git clones with tokens).

## Workflow

1. **Read the file on disk, not just the pasted copy.** Attachments land under `/opt/data/cache/documents/`. Diff intent between paste and file; the file is authoritative.
2. **Credential triage BEFORE running anything.** Byte-level scan for:
   - Literal angle-bracket placeholders (`<TOKEN>`, `<callsign>`) inside credential-bearing lines → **STOP and ask for real values.** Never guess, never "run it anyway to see the error."
   - Real token shapes (`ghp_…`, `github_pat_…`, `AKIA…`, `sk-…`) → treat as live secrets: mask everywhere, recommend rotation if they reached chat in plaintext.
3. **Masking discipline for every command that could echo the secret.** Pipe git/curl output through `sed -E 's#ghp_[A-Za-z0-9]{20,}#***#g'` (extend the pattern per token shape). Verify remotes only via `git remote get-url origin | sed 's#//.*@#//***@#'` and confirm `***` appeared. Never `git remote -v`, never `cat .git/config`.
4. **Execute steps in order, no improvisation.** Substitute only values the user actually supplied. Run each verification the runbook states; treat its "expected output" as a hard gate.
5. **STOP on first mismatch.** Report `FAILED AT STEP <n>` plus the exact command and masked error text. Do not attempt workarounds the runbook forbids, do not skip ahead, do not partially verify.
6. **Verify through the domain tool, not the file.** E.g. after YAML edits, `hermes config get <key> --json` is the authority, not `cat config.yaml`.
7. **Report with the runbook's own template if it has one.** Confirm the exact change-set bounds ("nothing changed beyond items a–e") and that no secret was printed. List anything self-assigned (e.g. a callsign you had to choose) so the user can override.

## Pitfalls

- **`hermes config set` on list-valued keys stores a JSON string**, not an array (`config get --json` returns `"[\"...\"]"`). Fix by direct YAML edit after backup: block-style list, two-space indent for the key, four for items, spaces only (a tab anywhere breaks YAML). Then re-verify with `config get <key> --json`.
- **`hermes` not on a tooling shell's PATH** is usually a PATH artifact, not a missing install. Fix: `export PATH=/opt/hermes/.venv/bin:$PATH` (binary there; config `/opt/data/config.yaml`, env `/opt/data/.env` on this box).
- **SOUL.md / config.yaml may live beside `/opt/data`**, not `~/.hermes/`, on this deployment — check both (plus `hermes config path`) before assuming a file is missing.
- **Pasting a real token into a command triggers credential-approval scans.** Keep the token in a shell variable assigned inside the same command block, output masked; approval then proceeds cleanly.
- **`hermes gateway status` may show "Running manually, not as a system service."** That means do NOT self-restart; record `restart: no — asked human`. Config/skills changes take effect on the next session anyway.
- **Announce disruptive actions before running them** (e.g. "Restarting my gateway now — I will drop for a few seconds") when the runbook says to announce first, even if you end up not acting.
- **Fleet/shared skill vaults are mounted, not imported.** Do NOT clone→adapt→publish their skills into the local library; put `<vault>/skills` on `skills.external_dirs` and follow the vault's own `_meta/ONBOARD-A-BOX.md`-style runbook verbatim. (Detail belonged in import-external-skills too, but that skill is user-owned — noted for adoption.)

## References

- `references/fleet-vault-onboarding.md` — observed single-brain onboarding specifics: path resolution, verification outputs, masked command patterns (session detail; the canonical runbook lives inside the vault at `_meta/ONBOARD-A-BOX.md`).
