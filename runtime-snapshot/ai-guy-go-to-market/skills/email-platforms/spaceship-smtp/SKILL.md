---
name: spaceship-smtp
description: Use when operating or deploying the self-hosted Spaceship Starlight SMTP and EmailDelivery.com (edcom-ce) platform, including port-25 access, PTR/DNS, IP screening, Velocity MTA, Postal Routes, DKIM, health checks, test sends, warmup, and incident guardrails.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [smtp, email-delivery, spaceship, starlight, edcom, velocity, dns, deliverability]
    related_skills: [email-platforms, email-deliverability-audit, email-delivery-edcom]
---

# Spaceship SMTP for Email Delivery

## Overview

This skill is adapted from the `jbellsolutions/email-delivery-edcom` deployment kit. It covers the owned SMTP/ESP workflow on Spaceship Starlight VMs, using Mail Bridge for port 25 and PTR, EmailDelivery.com Community Edition (edcom-ce) for the ESP layer, and Velocity for MTA sending.

The source repository contains the detailed edcom/Velocity runbooks and scripts:
`https://github.com/jbellsolutions/email-delivery-edcom`

For the separate Postal-based control-app handoff, see `references/email-infrastructure-handoff.md`. It records the repo state, the Starlight/Mail Bridge architecture, purchase prerequisites, hard gates, and the distinction between Postal and edcom/Velocity.

The published source skill is also available at:
`https://grassy-lotus-k454.here.now/`

Never expose or copy credentials from the repository, chat, or generated output. Keep secrets in the password manager or a local ignored environment file.

## When to Use

Use for:
- Deploying a new Spaceship Starlight sending VM
- Opening port 25 and setting PTR through Mail Bridge
- Screening an IP before assigning it to email
- Applying DNS records through the Spaceship API
- Installing or operating edcom-ce and Velocity
- Configuring Velocity servers, Postal Routes, customers, DKIM, and warmups
- Checking health, DNS, blacklists, port 25, or sending a smoke test
- Handling a blacklist, complaint spike, or warmup incident

Do not use as permission to purchase infrastructure, rotate credentials, or send campaigns without explicit authorization and the required account/domain/secrets.

## Non-negotiable architecture facts

- Railway and DigitalOcean commonly block outbound port 25. Do not use them as the default for a direct SMTP server.
- A Spaceship VM alone is not sufficient. Add Mail Bridge, which opens port 25 and sets PTR.
- Use one dedicated IP per VM. More IPs/volume require separate VMs or a provider that explicitly supports additional dedicated mail IPs.
- PTR must equal the HELO hostname exactly, for example `mail.example.com`.
- Screen the IP before trusting it. If listed, replace or reroll the IP before DNS and warmup.
- Keep gray/re-engagement traffic isolated from clean traffic on a separate IP and domain.
- Never re-propose SES, Postmark, Resend, or similar managed providers as the money path when the requirement is owned infrastructure and gray traffic.

## Required inputs before deployment

Confirm all of these before provisioning:

1. Primary sending domain.
2. Spaceship account and billing authorization.
3. A warming service that supports custom SMTP and IMAP. Warmforge and Lemwarm are not suitable if they do not support that requirement.
4. Supabase project, if the control application requires it.
5. Secrets delivered through the password manager, not Slack or repository files.
6. A target recipient for a controlled test email.
7. An approved traffic classification: clean, gray/re-engagement, or separate tenant traffic.

## Deployment sequence

1. Provision a Spaceship Starlight VM with one dedicated IP.
2. Add Mail Bridge and set PTR to `mail.<sending-domain>`.
3. Screen the IP for blacklists and reputation. Stop and replace a listed IP.
4. Publish the complete DNS set: A records, MX, SPF, DMARC, and DKIM. The Spaceship API PUT replaces the listed record set, so include the whole desired zone every time.
5. Run the port-25 gate from an external network and from the VM.
6. Install Docker and the edcom-ce stack, or install Velocity for an MTA-only box.
7. Complete the setup wizard. Set `TERM=xterm`; an unset terminal can cause `clear` to terminate the automation.
8. Configure HTTPS and Let's Encrypt.
9. Configure the domain and verify DNS.
10. Register the Velocity MTA server in edcom-ce.
11. Create a Postal Route from the customer to the correct Velocity server.
12. Create the customer account, domain, list, and campaign configuration.
13. Attach a conservative IP warmup ramp, beginning around 20 messages/day and increasing by approximately 20%/day.
14. Send a controlled DKIM-signed smoke test.
15. Verify acceptance, authentication, DNS, logs, bounce handling, suppression, and monitoring before any campaign volume.

## Operational commands and checks

Run from the cloned repo after loading its ignored environment file:

```bash
set -a && . ./.env.local && set +a

# Platform containers and HTTPS
ssh -p "$VM_SSH_PORT" -i secrets/velocity_gray_ed25519 root@"$VM_IP" 'docker ps --format "{{.Names}} {{.Status}}"'
curl -s -o /dev/null -w 'https %{http_code}\n' https://<esp-host>/login

# Deliverability checks
./scripts/blacklist-check.sh "$VM_IP"
./scripts/verify-dns.sh --domain <domain> --ip "$VM_IP" --helo "$VM_PTR" --dkim-selector s1
ssh -p "$VM_SSH_PORT" -i secrets/velocity_gray_ed25519 root@"$VM_IP" 'bash /root/port25-check.sh'

# Controlled direct smoke test
ssh -p "$VM_SSH_PORT" -i secrets/velocity_gray_ed25519 root@"$VM_IP" 'python3 /root/send_test.py'
```

Green criteria: expected containers are up, HTTPS returns 200, DNS checks pass, the IP is clean, PTR equals HELO, port 25 passes, and the receiving provider accepts the signed test.

## edcom configuration flow

1. Add the IP under **MTA → Velocity MTA Servers → Add Server**.
2. Set the header domain and link domain.
3. On the VM, generate the link certificate and restart Velocity.
4. Attach an IP warmup ramp.
5. Create a Postal Route mapping the customer to the Velocity server.
6. Create the customer account and assign its domain and lists.
7. Publish the exact DKIM selector shown by edcom. Do not assume the selector is `s1`.
8. Log in as the customer, build the campaign, and send only within the approved warmup limits.

## DNS rules

The desired zone normally includes:

- `mail.<domain>` A → sending IP
- ESP host A → sending IP or designated application endpoint
- MX → mail host
- SPF with the sending IP and a restrictive policy appropriate to the approved senders
- DMARC beginning at monitoring mode, then tightening only after authentication and alignment are verified
- DKIM TXT at the selector shown by the MTA

Spaceship API details from the source kit:
- Base: `https://spaceship.dev/api/v1/dns/records/<domain>`
- Headers: `X-Api-Key`, `X-Api-Secret`
- TXT uses `value`, A uses `address`, and MX uses `exchange` plus `preference`.
- PUT with `force:true` replaces the listed records. Always submit the complete desired set.

## Warmup and safety

- Start with engaged recipients and a low daily limit.
- Increase volume gradually, approximately 20% per day unless the approved warmup service specifies otherwise.
- Suppress dormant, invalid, bouncing, or complaining recipients before re-engagement.
- Monitor complaint rate, bounces, block responses, queue depth, deferrals, authentication failures, and blacklist status.
- Treat verification as separate from trap defense and engagement quality.
- Keep complaints below the agreed operational threshold; the source runbook calls out 0.1% as the ceiling.
- Open a breaker and stop sending on blacklist listing, complaint spikes, authentication failure, abnormal bounces, or provider blocks.

## Incident response

1. Stop all campaign sends and disable the Postal Route or warmup.
2. Preserve logs, message IDs, headers, bounce responses, and DNS state.
3. Identify whether the issue is IP reputation, domain reputation, authentication, content, list quality, or infrastructure.
4. Confirm the IP, PTR, SPF, DKIM, and DMARC state.
5. Remove or suppress the triggering audience and investigate acquisition/source quality.
6. Do not resume until the condition is resolved and a controlled test passes.
7. Resume at a lower volume with engaged recipients only.

## Credential and repository guardrails

- The proxy4smtp password was exposed in chat and must be rotated before use.
- Never commit `.env.local`, SSH keys, DKIM private keys, admin passwords, root passwords, API secrets, or live SMTP credentials.
- Never paste live credentials into Slack, tickets, prompts, or source files.
- Back up the edcom config and database volume, including DKIM keys. Losing signing keys breaks authentication.
- Keep the control app's secrets in the password manager and supply them only through the approved local runtime mechanism.

## Common pitfalls

1. **Choosing Railway or DigitalOcean for direct port 25.** Use a provider with confirmed port-25 support; Spaceship Mail Bridge is the current path.
2. **Provisioning a VM without Mail Bridge.** The port remains blocked and PTR may be unavailable.
3. **Trusting an unscreened IP.** Screen and reroll before publishing DNS.
4. **Sending a partial DNS PUT.** Spaceship replaces the submitted set; send the entire desired zone.
5. **Assuming the DKIM selector.** Publish the selector actually generated by edcom or Velocity.
6. **Running setup automation without `TERM=xterm`.** Terminal clearing can terminate the wizard.
7. **Using coordinate clicks on custom UI dropdowns.** Prefer programmatic element clicks/value setters when browser automation is required.
8. **Treating a direct smoke test as a campaign.** It bypasses edcom tracking and suppression; use the customer UI for real campaigns.
9. **Rushing a cold IP.** Warmup takes about 30 days by design. Do not force volume on day two.
10. **Confusing verification with deliverability.** Verification does not protect against traps, complaints, or poor engagement.

## Verification checklist

- [ ] Domain, billing authorization, warming service, Supabase project, and recipient are confirmed.
- [ ] Mail Bridge is active and PTR equals HELO.
- [ ] IP blacklist screening is clean.
- [ ] Complete DNS set is published and independently verified.
- [ ] Port 25 passes from an external network.
- [ ] edcom/Velocity services are healthy.
- [ ] HTTPS is valid and admin access works without exposing credentials.
- [ ] DKIM selector is published and a received message passes SPF, DKIM, and DMARC alignment.
- [ ] Postal Route maps the intended customer to the intended IP.
- [ ] Warmup ramp is configured and volume limits are enforced.
- [ ] Bounce, suppression, complaint, queue, and blacklist monitoring is active.
- [ ] A backup of config, database, and DKIM keys exists.
- [ ] The proxy4smtp password has been rotated.
