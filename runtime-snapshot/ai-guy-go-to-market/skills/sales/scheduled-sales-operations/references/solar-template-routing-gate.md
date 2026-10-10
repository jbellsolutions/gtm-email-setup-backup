# Solar-template routing gate

Use this gate before sending any reply that an operator describes as a positive solar-lead response.

1. Treat the source reply and cron/Slack summary as discovery context, not sufficient send authority.
2. Resolve the current live Instantly inbound record and verify, together: recipient, exact campaign ID, inbound `ue_type`, message `id` (`reply_to_uuid`), `eaccount`, and subject.
3. The auto-send exception applies only to campaign `dbd68956-2dc6-47e4-a56e-5a518db39381` (`solar | open door`) and eligible ordinary positive inbound replies. A different campaign, including a campaign whose label or reply sounds solar-related, must not use the solar template automatically.
4. If the live record cannot be recovered, stop. Never reconstruct `reply_to_uuid` from a stale report, cached snapshot, or an unrelated thread.
5. If routing is valid, run the full template hard-stop checks: no question, objection, pricing/custom-plan/service-area/technical request, negative/unsubscribe/OOO/auto-responder/referral routing, or other unusual factual request.
6. POST the unchanged approved template using the verified inbound `id`, verified `eaccount`, original subject, and both text/HTML bodies. Confirm HTTP 200 and a distinct outbound record before claiming success.

Incident pattern: a positive-soft reply from Mike Munter was reported on campaign `6ed22f69-b848-4d9f-aa7c-4cdbb8c74973` (`the roster`), not the authorized solar campaign. The correct action was to refuse the solar auto-send and request confirmation for the normal approval-gated roster reply because the current inbound record could not be safely recovered. This is a routing failure, not evidence that the solar template should be broadened.
