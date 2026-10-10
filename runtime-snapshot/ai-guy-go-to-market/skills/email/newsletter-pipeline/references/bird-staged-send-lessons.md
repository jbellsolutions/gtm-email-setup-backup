# Bird staged-send lessons from Campaign 23

## Verified operational facts

- ListMonk is the sender. Its native worker continues server-side even when an external monitor exits, loses a PTY, or is killed. A monitor must never pause solely because its own process failed.
- Bird account summary is useful for transport monitoring when ListMonk bounce processing is disabled. Always label it account-wide. Key fields: `accepted`, `delivered`, `all_bounces`, `bounced`, `bounces.hard`, `oob_bounces`, `deferred`, `rejected`, `complained`.
- Compute the account-level bounce rate as `all_bounces / accepted * 100`. Accepted and delivered are different denominators; do not call accepted delivered.
- Re-read Campaign 23 after every status transition. In-flight sends can make the final persisted `sent` count exceed the last poll.

## Failure and recovery evidence

- At 5 connections and about 5-8 messages/second, Bird/ListMonk showed repeated `535 5.7.8 Authentication failed: invalid or revoked API key` and occasional `EOF` errors.
- At low concurrency, including 2 connections around 3 messages/second, the campaign advanced without 535 for a meaningful interval. This supports testing low concurrency before concluding the key is unusable, but it does not prove a 535 can be ignored indefinitely.
- The Bird HTTP API accepted internal health checks with HTTP 202 while the ListMonk SMTP path separately failed at times. HTTP success is not SMTP AUTH proof.
- ListMonk's `/api/campaigns/{id}/test` can accept a complete payload and return `{"data":true}` without a useful transport log. Treat that response as inconclusive unless logs or provider records confirm delivery.
- A direct VPS socket test to `us1.smtp.bird.com:587` timed out before the SMTP greeting. That is a network-path test failure, not evidence that Railway/ListMonk cannot connect.

## Safe execution sequence

1. Verify the named campaign is paused and confirm its persisted sent baseline.
2. Confirm Bird is the only enabled ListMonk SMTP messenger. Re-sync the Bird password after key rotation, never printing the secret.
3. Set low concurrency first: 1-2 connections, approximately 2-3 messages/second, bounded batch size.
4. Resume via `PUT /api/campaigns/{id}/status` with `{"status":"running"}` and verify a post-start GET shows `running` and advancing `sent`.
5. Run a simple observational poller. It may die and be restarted; it must not change campaign state on monitor failure.
6. Pause only after independently confirmed complaints, provider rejection, recurring authentication failure at low concurrency, agreed bounce threshold, or sustained EOFs. Then verify the persisted paused state.
7. At completion or pause, capture both ListMonk and Bird snapshots and explicitly note account-wide versus campaign-specific scope.

## Do not repeat

- Do not use a custom long-running worker as the sender when ListMonk's native worker is available.
- Do not make a monitor responsible for pausing because its own output stalled or its local state file broke.
- Do not infer that ListMonk `bounces: 0` means zero bounces when bounce ingestion is disabled.
- Do not use a high-concurrency 535 as sole proof that the HTTP key is revoked; first preserve the evidence and test the low-concurrency relay path once.
- Do not claim a campaign is finished from a background-process exit, a `data:true` test response, or a running status alone.
