# Bird + ListMonk send diagnostics

Session-derived operational notes for Bird SMTP campaigns.

## Credential split

Bird's HTTP API and SMTP relay are separate paths. A successful HTTP API health check returns HTTP 202 with an accepted message, but this does not prove ListMonk's SMTP credential works. ListMonk uses the global SMTP configuration, typically:

- host: `us1.smtp.bird.com`
- port: `587`
- TLS: STARTTLS
- auth: LOGIN
- username: `bird`
- password: current Bird credential with SMTP-send permission

A VPS-side socket probe to port 587 may time out because outbound SMTP is blocked by the host network. Do not use that as the campaign-path test. ListMonk is on Railway and its logs are the authoritative SMTP-path evidence.

## Safe credential repair

1. Confirm Campaign 23 or the named campaign is paused by GET, not assumption.
2. Run one Bird HTTP health check to an internal seed. Record HTTP status and accepted/rejected counts.
3. GET ListMonk settings. Update the complete settings payload, preserving all SMTP entries, and replace only Bird's password with the current credential. Keep Resend disabled when Bird is the intended provider. Never write ListMonk's masked password bullets back as the real password.
4. Read back host, port, TLS, auth protocol, username, enabled state, and password presence without printing the secret.
5. Use a small native campaign resume to test ListMonk → Bird SMTP. A test endpoint returning `{"data":true}` without a transport log is inconclusive. A campaign log with `535 5.7.8 Authentication failed` is a hard stop and indicates the credential is not usable for ListMonk SMTP, even if HTTP works.
6. If the sent counter advances past baseline with fresh logs showing no 535, pause the small verification batch and only then decide whether to continue.

## Native sender and monitor design

Use ListMonk's status endpoint to resume/pause. Set a conservative pace for a warming Bird domain, commonly 2 connections and 2–3 messages/sec; higher rates produced transient `EOF` transport errors in this campaign. Native ListMonk should remain the sender. Do not build a custom Python worker as the delivery mechanism.

A circuit breaker should be separate from the sender, restart-safe, and use fresh provider snapshots. It must:

- poll Bird independently of ListMonk, approximately every five minutes;
- stop on complaints, provider rejection, recurring 535/authentication errors, or bounce rate at/above 3%;
- tolerate an isolated EOF only when counters advance and no repeated EOF pattern exists;
- stop on a sustained EOF pattern, e.g. 5+ recent EOFs;
- stop and pause the campaign if its own log bookkeeping fails, its PTY is lost, or its process is terminated, unless a separately verified circuit breaker remains active;
- after any monitor failure, GET and pause the campaign before reporting a final count because sends may be in flight and the persisted count may overshoot.

Do not use a string-copy log baseline that assumes `cp "$L" "$BASE"` when `$L` contains JSON content. Write snapshots to actual files, compare structured records by timestamp or stable line identity, and retain a local state file. A broken monitor is not evidence of a failed sender, but it is a reason to pause until monitoring is trustworthy.

## Reporting

Bird aggregate metrics are account-wide and may lag ListMonk. Report the snapshot timestamp/period and distinguish:

- accepted vs delivered;
- hard bounces vs out-of-band bounces and total bounces;
- deferred and rejected;
- complaints;
- bounce-rate denominator.

ListMonk's campaign `bounces` counter is not authoritative when Bird bounce processing/webhooks are disabled. Never claim inbox-tab placement from transport data alone; recipient confirmation is required.

## Failure signatures

- `535 5.7.8 Authentication failed: invalid or revoked API key`: stop; do not keep retrying the campaign. Re-sync once or obtain a Bird credential explicitly enabled for SMTP relay.
- HTTP API `202` plus ListMonk SMTP `535`: API credential works but the ListMonk SMTP path is not authenticated.
- ListMonk test endpoint `{"data":true}` with no SMTP log: inconclusive; do not authorize a bulk resume.
- `EOF` during `manager.go:548 error sending message`: indeterminate transport drop. It is not automatically a bounce or auth failure. Track recurrence and pause on a sustained pattern.
- Process exit `-15`, `143`, or PTY `tcsetattr` warning: monitor/process termination, not proof of delivery failure. Immediately verify and pause the campaign; account for in-flight messages.
