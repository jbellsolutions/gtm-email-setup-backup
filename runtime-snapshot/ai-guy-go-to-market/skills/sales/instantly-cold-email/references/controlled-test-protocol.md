# Controlled Instantly Migration Test

Use this protocol before committing to an Instantly upgrade or migration.

## Scope

Test only controlled recipients owned by the operator. Confirm the exact recipient address before sending. A corrected address replaces any earlier address in the thread. In the August 2026 test, the authoritative address was `justin@usingaitoscale.com`; do not use the earlier `justin@usingai.scale.com` or the unrelated `AI@scala.com` address.

## Safety sequence

1. Confirm the Instantly API credential or active integration. Do not require a separate Composio OAuth connection if the existing raw REST credential is already live and verified.
2. Select or create a paused test campaign. Preserve the campaign ID and fetch its full configuration before editing.
3. Confirm connected sender mailboxes and choose an available sender.
4. Create two controlled leads, using the exact approved recipient addresses.
5. Add a scalar custom variable containing a complete per-lead email body, for example `custom_email`. Do not assume Instantly's custom-field syntax. Confirm Instantly's actual merge-tag syntax from the campaign response or UI.
6. Configure the first sequence step to render the custom variable. Keep the campaign paused while editing.
7. Preview the resolved message for each lead. Verify recipient, sender, subject, body, personalization, plain-text mode, and tracking settings.
8. Send only after the operator explicitly authorizes the controlled test. If the platform cannot safely send one controlled message from the paused campaign, stop and report the blocker rather than guessing at an endpoint.
9. Confirm send status through the Instantly email list/API.
10. Have the operator reply. Poll Unibox and record the actual response fields, thread identifier, and message UUID.
11. Confirm the monitor creates the expected Slack draft notification. Do not claim Slack delivery without a verified Slack post or message metadata.
12. Wait for explicit approval. Run the reply through the outbound QC gate, send via the verified reply endpoint, and confirm the sent reply appears in the same thread.
13. Have the operator reply again and confirm the second inbound message is detected without duplicate processing.

## Hard stops

- No active sender mailbox.
- Campaign is not confirmed paused before variable/sequence edits.
- Custom-variable syntax or payload shape is unverified.
- No safe preview of the resolved body.
- Reply endpoint or `reply_to_uuid` cannot be tied to the actual inbound message.
- Slack integration is unavailable or token-revoked.

## Evidence to capture

Save campaign ID, lead IDs, custom-variable key, rendered preview, send response, inbound message shape, daemon output, Slack message timestamp/permalink, reply API response, and second-reply detection result. Redact API keys and message secrets.
