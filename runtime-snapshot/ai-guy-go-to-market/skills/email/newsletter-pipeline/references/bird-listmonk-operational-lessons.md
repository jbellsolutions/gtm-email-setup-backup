# Bird / ListMonk operational lessons

## Verified behaviors

- ListMonk campaign status is the authoritative persisted send state. Always GET `/api/campaigns/{id}` after a worker exits or a pause request.
- Native status transition is `PUT /api/campaigns/{id}/status` with `{"status":"running"}` or `{"status":"paused"}`. A status update can overshoot because sends are batched/in flight.
- A long custom monitor can be killed with SIGTERM/exit 143 or lose its PTY while ListMonk continues sending. This is a monitoring failure, not a send result.
- Bird HTTP API and Bird SMTP authentication are separate paths. Bird HTTP can return `202 Accepted` while ListMonk logs `535 5.7.8 Authentication failed`.
- A direct VPS TCP probe to `us1.smtp.bird.com:587` timed out and was not a valid SMTP conclusion; ListMonk/Railway had previously connected and logged SMTP responses.
- ListMonk's test endpoint can accept a complete campaign payload as `{"data":true}` without producing a useful transport log. Do not call that SMTP success.

## Reconciliation recipe

1. GET ListMonk campaign: `status`, `sent`, `to_send`, `bounces`, `views`, `clicks`.
2. GET `/api/logs`; inspect only new/fresh entries for `535`, `authentication failed`, `error sending`, `rejected`, `complaint`, `throttl`, and `rate limit`.
3. GET Bird `https://us1.platform.bird.com/v1/email/stats/summary` with the current HTTP key.
4. Report `delivery.accepted`, `delivered`, `all_bounces`, `bounces.hard`, `oob_bounces`, `deferred`, `rejected`, and `complained`.
5. Calculate `all_bounces / accepted`; explicitly label the result account-wide unless message-level filtering isolates the campaign.
6. If the campaign is running after a monitor interruption, pause via the status endpoint, then GET it again for the final persisted count.

## Credential rotation

After replacing a Bird key, update ListMonk's Bird SMTP password in the full `/api/settings` payload. Preserve the Bird SMTP record's username, host, port, TLS, and auth protocol; keep Resend disabled when Bird is the intended sole provider. Never write back ListMonk's masked password value as the password.

An HTTP `202` health check is not an SMTP test. The only conclusive SMTP test in this environment is a ListMonk-originated campaign send with a fresh log entry showing acceptance/no `535`; direct VPS socket testing is environment-dependent.
