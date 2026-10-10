# Email Infrastructure Handoff: Spaceship + Postal

Session-derived reference for `jbellsolutions/email-infrastructure`.

## Repo state

- Repository: `https://github.com/jbellsolutions/email-infrastructure`
- Built and tested control-app safety systems and Postal adapter: expected `12/12` tests.
- Not deployed: no VM, domain, DNS, or sent mail at handoff.
- Install agent skills from the repo with `cp -R skills/email-infra-* ~/.claude/skills/`.
- Start Claude Code with `/email-infra-orient`, then read `docs/CHECKLIST.md`.

## Architecture decision

- Direct MTA: Spaceship Starlight VM + Mail Bridge + Postal.
- Control app: Railway and/or DigitalOcean only.
- Railway and DigitalOcean are not the direct MTA host for this plan because outbound port 25 is blocked/restricted.
- Mail Bridge opens outbound port 25 and supplies PTR; the VM alone is insufficient.
- Provision VM-1 (CLEAN) first. Do not buy VM-2 (GRAY) until actual isolated re-engagement traffic exists.

## Hard gates

1. Before provisioning: primary CLEAN domain, custom SMTP+IMAP-compatible warming service, Supabase project, out-of-band secrets, and rotated `proxy4smtp` password.
2. Provision one Starlight VM with Mail Bridge.
3. Screen the assigned IP immediately using `infra/scripts/blacklist-check.sh`.
4. If listed on any DNSBL, destroy and reprovision. Do not delist a previously used IP.
5. Publish complete DNS: A, SPF, DMARC, MX, Postal return-path/tracking, then Postal-generated DKIM.
6. Postal HELO/`smtp_hostname` must exactly match the Mail Bridge PTR.
7. Run `infra/scripts/verify-dns.sh`; all critical checks must pass.
8. Send one controlled seed message and require SPF, DKIM, DMARC alignment plus mail-tester >= 9/10 before real traffic.
9. Warm only engaged opt-in recipients; graduation requires complaint <0.1%, hard bounce <1%, acceptable Postmaster reputation, zero DNSBL listings, and the documented stage criteria.

## Critical handoff blockers

- The repo's `START-HERE.md` is the correct handoff entry point.
- Do not represent the repo as deployed merely because its code/tests are complete.
- The actual purchase is not "a port-25 server" in the abstract: it is one Starlight VM plus Mail Bridge, with IP screening as the first post-purchase gate.
- Never purchase or provision infrastructure solely because a card is on file when required domain, warming, secrets, and deployment parameters remain unresolved.

## Related source files

- `docs/START-HERE.md`: concise handoff and Claude kickoff prompt.
- `docs/HANDOFF.md`: architecture, guardrails, blockers, and definition of done.
- `docs/CHECKLIST.md`: ordered steps 0-10 and hard gates.
- `infra/spaceship/provisioning.md`: Starlight/Mail Bridge runbook.
- `infra/scripts/blacklist-check.sh`: assigned-IP screening.
- `infra/scripts/verify-dns.sh`: PTR/HELO/authentication verification.

This repo uses Postal, whereas the separate `email-delivery-edcom` repo uses edcom-ce/Velocity. Do not silently merge their installation or operating commands.