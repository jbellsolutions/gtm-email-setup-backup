# ListMonk test-send and remote SMTP verification

## Known deployment behavior

The actual SMTP sender is ListMonk on Railway, not the agent's VPS. An SMTP socket probe from the VPS can time out because outbound port 587 is restricted; that does not test ListMonk → Bird. Earlier campaign logs proved the remote path connected when it returned `535 5.7.8 Authentication failed`.

## Correct campaign test payload

`GET /api/campaigns/{id}` returns `lists` as objects. Before `POST /api/campaigns/{id}/test`, convert them to IDs:

```python
campaign = get_campaign(23)
payload = {k: campaign[k] for k in [
    'name', 'subject', 'type', 'content_type', 'body', 'altbody',
    'from_email', 'template_id', 'tags', 'headers'
] if k in campaign}
payload['lists'] = [x['id'] if isinstance(x, dict) else x for x in campaign['lists']]
payload['subscribers'] = ['xander@usingaitoscale.com']
payload['messenger'] = 'email-bird'
post('/api/campaigns/23/test', payload)
```

A minimal subscribers-only payload can fail with `Invalid length for name`, a payload with object-valued lists fails with `Unmarshal type error: expected=int, got=object`, and a complete payload without `messenger` can fail with `Unknown messenger .`.

## Evidence rules

- `{"data":true}` means the API accepted the test request, not that SMTP delivered it.
- Verify `/api/logs` for a transport result. No log entry means the test is inconclusive.
- For a credential change, keep the campaign paused, update the Bird SMTP password, and use the named campaign sender for a bounded verification run if the test endpoint emits no transport evidence.
- Confirm the persisted campaign state after every pause or worker interruption; in-flight batches can overshoot the last observed counter.
- If a bounded run advances the sent counter beyond baseline with no `535`, pause and re-read before continuing. If `535` appears, stop and report the SMTP credential/scope blocker.

## Bird credential split

A Bird HTTP API `202` validates the HTTP API key only. It does not prove the key is valid for ListMonk's SMTP relay. In this deployment the relay settings are `us1.smtp.bird.com:587`, STARTTLS, AUTH LOGIN, username `bird`; the password is masked on ListMonk reads. Preserve the secret, verify only presence, and never paste it into reports.

## Hard-hold rule

If the operator says HOLD or NO SEND, first issue the campaign status pause and GET the campaign until `status: paused` is confirmed. Do not launch a worker before that confirmation. Campaign 24 must remain untouched during Campaign 23 diagnostics or staged sends.

## Post-send reconciliation

Bird account totals are transport-level and may include other messages. Report accepted, delivered, total and out-of-band bounces, deferred, rejected, complaints, and the exact denominator for bounce rate. Do not infer inbox tab placement from Bird data; require recipient confirmation.
