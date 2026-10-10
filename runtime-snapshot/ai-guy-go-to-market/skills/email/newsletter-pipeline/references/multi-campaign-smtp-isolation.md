# Multi-campaign SMTP isolation in ListMonk

ListMonk v6.2.0 exposes SMTP messengers globally. A campaign does not independently pin itself to Bird or Resend merely because its payload or test request includes a messenger name. When two campaigns require different transports:

1. Health-check the ListMonk API.
2. Load and verify each campaign as a draft using the blank raw template (`{{ template "content" . }}`), hosted media URLs, converted merge tags, and persisted Reply-To headers.
3. For the first campaign, fetch full settings, disable every other SMTP, explicitly restore the real password for the selected provider because API output masks passwords, enable the intended provider, PUT the full settings object, wait for restart, and verify `/api/logs` contains the selected initialization line.
4. Send the complete test payload with exactly `xander@usingaitoscale.com` and `justin@usingaitoscale.com`, plus the explicit messenger name. A minimal test payload is invalid; a complete payload without `messenger` can produce `Unknown messenger .`.
5. Verify transport delivery using provider-level status: Bird `/v1/email/messages`, or Resend `/emails` / message status. ListMonk returning `{"data":true}` is acceptance only, not delivery proof.
6. Repeat the provider switch and verification for the next campaign. Do not run the two tests concurrently.
7. Restore the designated default provider and verify the final initialization log. Record that SMTP state is global.

Do not claim a campaign was sent through its intended provider until the provider log and provider-level delivery status both confirm it. Keep all real provider passwords out of source files, logs, and reports.

## Known successful Issue 001 sequence

- Referral Channel campaign 23: Bird, From `The Referral Channel <referral@send.usingaitoscale.com>`, Test-Xander list, blank template 8, Reply-To header set, two recipients delivered.
- Dealmaker Issue 1 campaign 24: Resend, From `The Dealmaker <dealmaker@send.usingaitoscale.com>`, Test-Xander list, blank template 8, Reply-To header set, two recipients delivered.
- Both campaigns remained `draft` with `sent: 0`; no master-list send occurred.
