# Fleet Vault Onboarding — Observed Detail (single-brain, 2026-09-03)

Session-specific record of the single-brain onboarding run. The canonical runbook lives
inside the vault at `$SINGLE_BRAIN_DIR/_meta/ONBOARD-A-BOX.md` — that file governs; this
one only records how it played out on this box and the masked command shapes that worked.

## Box facts

- DigitalOcean droplet, hostname `4eef3be79163`, Linux, user `hermes` (uid 1000), `HOME=/opt/data/home`.
- `sudo -n` → no. So the home-path case applies: vault at `$HOME/single-brain`, i.e. `/opt/data/home/single-brain`.
- `hermes` not on tooling-shell PATH; `/opt/hermes/.venv/bin/hermes` v0.20.0 is the binary. `export PATH=/opt/hermes/.venv/bin:$PATH` at the top of every command block.
- Config `/opt/data/config.yaml`, env `/opt/data/.env`, SOUL at `/opt/data/SOUL.md` (beside config.yaml, NOT `~/.hermes/`). Gateway runs manually (s6-supervised in container), not as a system service → never self-restart; ask the human.

## Runbook triage findings

- Supplied file arrived with literal placeholders `x-access-token:<TOKEN>` and `<callsign>` — byte-verified before running anything (`grep -oE 'x-access-token:[^@\s"\'']+@'`, length/shape check). STOP and request the real values; never guess.
- Confirmed no other file on the box carried the clone-URL pattern (count-only `grep -rc`) and zero token-shaped env vars / .env keys before concluding the credential was missing.
- Token then arrived in plaintext Slack → masker pattern for ALL subsequent git output:
  `sed -E 's#ghp_[A-Za-z0-9]{20,}#***#g'`
  Remote verification (assert `***` appears):
  `git -C "$SB" remote get-url origin | sed 's#//.*@#//***@#'`
- Token-in-command triggered a credential-approval scan; assigning it to a shell variable inside the same block kept the flow clean (approved by user in-session).

## Step outcomes

- 2b: appended `SINGLE_BRAIN_DIR=/opt/data/home/single-brain` to `/opt/data/.env` (guarded grep-first append).
- 3: clone verified — `INDEX.md README.md _meta agents skills` (vault also had `knowledge/`, `playbooks/`, `templates/`); identity `single_brain2` / `single_brain2@agents.usingaitoscale.com`.
- 4: `hermes config set skills.external_dirs '["..."]'` stored a STRING (`"[\"...\"]"`) — the runbook's own decision table anticipated this. 4b Case C: both `skills:` (line ~320) and `external_dirs:` existed; converted inline string to block list via targeted `sed -i '321s#.*#...'`, no tabs, backup at `/opt/data/config.yaml.bak-single-brain`. Verified `hermes config get skills.external_dirs --json` → real array.
- 5: RULES.md append to `/opt/data/SOUL.md`. Em-dash grep pattern worked in this locale (test it against RULES.md itself first). Integrity check: md5 of original byte-prefix unchanged; size delta exactly `len(RULES.md)+2`; tail ends on rule 11.
- 6: `hermes gateway status` → "Running manually, not as a system service" → per runbook, do not restart; record `restart: no — asked human`. (Skills/config still loaded fine next session.)
- 7: all three skills (`single-brain-find-skill`, `single-brain-publish-skill`, `single-brain-self-report`) listed enabled; `pull --ff-only` fast-forwarded `d166408..125ce2d` (vault had moved between clone and verify — not a failure row).
