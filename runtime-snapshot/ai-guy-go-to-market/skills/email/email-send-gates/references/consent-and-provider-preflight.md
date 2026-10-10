# Consent and provider preflight

Use this evidence table before any email operation:

| Gate | Required evidence | Stop condition |
|---|---|---|
| Audience | Documented opt-in or transactional basis; list identity and count | Known cold/non-opt-in promotional audience for bulk send |
| Artifact | Exact issue, subject, sender, Reply-To, body/hash, draft status | Stale or different campaign is the only loaded artifact |
| Suppression | Recipient-level hard bounce/block/complaint evidence; deduped addresses | User asks to skip known suppressions or evidence is only aggregate |
| Provider | Exactly one persisted SMTP provider enabled; host/port/user re-read | Multiple providers enabled or state cannot be re-read |
| Tracking | `disable_tracking=false`, `individual_tracking=true`; seed evidence for attribution | Tracking claimed from settings or HTTP 200 alone |
| Test | Named internal recipients, arrival/render/link evidence | Production started before test review when no valid pre-approval exists |
| Production approval | Explicit go tied to the exact campaign and audience | Approval is only general content approval, not send authorization |

## Provider reconciliation

Keep application and transport metrics separate:

- ListMonk `sent`, `to_send`, `views`, `clicks`, and `bounces` are application-level.
- Bird/Resend accepted, delivered, bounced, deferred, rejected, and complained values are transport-level.
- Never infer campaign-wide delivery or recipient-level suppression from an account aggregate.

## ZIP image checklist

For a supplied email ZIP, preserve the HTML design and verify all relative references are addressed:

- `<img src="...">`
- HTML `background="..."`
- CSS `background-image:url(...)`
- Outlook conditional `<v:image src="...">`

A source-level count confirms rewriting only. It does not prove an image rendered in Gmail, Outlook, or Apple Mail; that requires received-message or preview evidence.

## Recovery

If API/browser authentication expires, reconnect and re-fetch state. Do not mutate or send based on stale state. If the exact audience, artifact, or provider cannot be verified after retry, stop and report the missing evidence.
