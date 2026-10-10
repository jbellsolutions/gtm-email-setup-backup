# Pre-send suppression reconciliation reference

## Evidence matrix

| Evidence | Acceptable proof | Not sufficient |
|---|---|---|
| Provider campaign scope | Exact sender + subject + send window, or provider export | Account aggregate or approximate date alone |
| Recipient failure | Recipient-level message record with status/reason | Aggregate bounce rate |
| Complete retrieval | Exhausted cursor pagination or verified export total | First API page |
| List suppression | Re-fetched suppression/blocklist record | HTTP 200 or UI toast |
| List removal | Before/after per-list subscriber records and counts | Claimed bulk operation |
| Test delivery | Recipient confirmation or mailbox access | Provider acceptance alone |
| Tracking | Raw message pixel/link plus attributable counter movement | Tracking setting enabled |
| Approval | Explicit current go from designated approver | Silence or older approval |

## Recommended CSVs

Detailed evidence ledger:

`email,provider,campaign_id,campaign,subject,send_window,status,reason,message_id,observed_at`

Owner-facing suppression file:

`email,providers,campaigns,statuses,reasons,first_observed_at,last_observed_at`

Keep the detailed ledger for auditability and deliver the deduplicated owner-facing file. Normalize only the address matching key; retain original provider evidence in the detailed file.

## Safe stopping conditions

Stop before list mutation when any required campaign cannot be isolated, a provider credential returns an auth error, pagination is incomplete, or a local bounce file cannot be mapped to a specific campaign/provider. Report the missing evidence and avoid guessing counts.

Stop before production send when image hosting, provider isolation, tracking proof, test review, or explicit approval is incomplete.

## HTML image check

Count and inspect every image reference. For a hero used as a CSS background and Outlook VML fallback, verify both references were rewritten. No relative `src`, `background-image`, `background`, or VML `src` references may remain in the final send body.

## Operational note

ListMonk’s native bounce-processing settings do not prove Bird or Resend webhook synchronization. Confirm provider-side events and ListMonk-side persistence separately.