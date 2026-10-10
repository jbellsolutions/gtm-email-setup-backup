# Bird SMTP/API credential diagnostic

Use this reference when the Bird HTTP API works but ListMonk's Bird SMTP path fails. This is a diagnostic-only workflow. Keep campaigns paused.

## Evidence pattern from the August 2026 incident

- Bird HTTP API accepted an internal-seed diagnostic with HTTP `202` and `accepted_count: 1`.
- ListMonk had previously logged: `535 5.7.8 Authentication failed: invalid or revoked API key`.
- ListMonk settings showed:
  - host `us1.smtp.bird.com`
  - port `587`
  - TLS `STARTTLS`
  - auth protocol `LOGIN`
  - username present (`bird`)
  - password field present but masked
- A direct raw TCP/STARTTLS probe from the VPS timed out before the SMTP greeting, so it could not independently confirm SMTP AUTH. The earlier ListMonk 535 remained the usable SMTP evidence.
- Bird account metrics showed no rejection or complaint signal and approximately 1.49% account-level bounce rate. These metrics were not campaign-isolated and must not be presented as campaign-only statistics.

## Safe probe sequence

1. GET the named ListMonk campaign. Require `status: paused`; do not start or test it.
2. Run a single Bird HTTP API diagnostic to the named internal seed. Use a minimal valid current Bird payload with top-level `from`, `to`, `subject`, `html`, `text`, and `reply_to` as an array. Record response status and message ID.
3. Read ListMonk `/api/settings`. Never print the password. Report host, port, TLS, auth protocol, username presence, password presence/masking, and enabled state.
4. Test SMTP connectivity/auth separately. A valid test must observe the SMTP greeting, EHLO capabilities, STARTTLS negotiation, AUTH LOGIN, and final acceptance. A connection timeout is a network test failure, not evidence of valid or invalid credentials.
5. Query Bird account/domain health and metrics. Separate account-wide totals from campaign-specific totals.
6. Stop. Do not resume, test-send, or modify campaign settings as part of the diagnostic.

## Interpretation

- HTTP `202` + SMTP `535`: HTTP credential works; SMTP credential, SMTP permission/scope, or ListMonk's stored SMTP secret is wrong/revoked.
- HTTP `202` + SMTP connection timeout: HTTP works; SMTP status is unverified from this environment. Investigate network egress/firewall and retain any prior ListMonk 535 evidence.
- SMTP greeting/STARTTLS/AUTH success: only then is the relay credential proven. A standalone internal message acceptance is still not permission to resume a campaign.

## Known relay settings

For the current US Bird relay, documented settings are `us1.smtp.bird.com`, port `587`, STARTTLS, username `bird`, and a valid Bird key with the provider's SMTP-send permission. Do not assume every HTTP API key is valid for SMTP AUTH. Generate or retrieve a credential explicitly authorized for SMTP relay if the provider distinguishes scopes.

## Reporting template

- Campaign status and sent baseline:
- HTTP API diagnostic: status, accepted/rejected/bounced, message ID:
- SMTP probe: greeting/STARTTLS/AUTH result, or exact timeout/535 evidence:
- ListMonk SMTP fields: host, port, TLS, auth, username/password presence, enabled provider:
- Bird health: suspension/abuse/rate-limit/rejection/complaint evidence:
- Decision: remain paused until SMTP is independently verified.
