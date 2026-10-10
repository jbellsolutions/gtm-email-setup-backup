# ListMonk Multi-Draft Persistence

## Purpose

Use this sequence when creating multiple HTML review-draft campaigns. It prevents the common false-positive where ListMonk shows a draft row but the HTML body was never persisted.

## Known-good operating sequence

1. Open the authenticated admin UI at `/admin/campaigns/new`.
2. Fill one campaign only: publication name plus issue number, subject, `Newsletter <newsletter@send.usingaitoscale.com>` as From address, and the `Test-Xander` list (list ID 6 in the current instance).
3. Select **Raw HTML**, not Rich text.
4. Click **Continue** and complete the Content step with the full HTML body. Do not assume the Campaign tab's successful navigation saved content.
5. Save the campaign.
6. Return to `/admin/campaigns`, identify the new campaign, and inspect/fetch its record.
7. Verify all of: `status: draft`, `sent: 0`, `content_type: html`, target list correct, body non-empty, and body length/hash equal to the ListMonk-safe source HTML.
8. Only then start the next issue.

## HTML normalization before persistence

Convert generic merge placeholders before sending HTML to ListMonk:

- `{{VIEW_ONLINE_LINK}}` → `{{ MessageURL }}`
- `{{UNSUBSCRIBE_LINK}}` → `{{ UnsubscribeURL }}`

For an unresolved Referral Channel Medium URL in a visual draft, encode the braces as HTML entities so ListMonk's Go-template parser does not treat `MEDIUM_URL` as a function. Never pass raw `{{MEDIUM_URL}}` to a ListMonk campaign.

## Credential boundary

The current admin login can authenticate the browser UI, but admin username/password may be rejected by the REST API. A REST 403 with `invalid API credentials` does not prove the instance is unavailable. Prefer same-origin browser-console requests from the authenticated admin session or create/use a dedicated API user token. Do not repeatedly retry the admin password as an API token.

## Failure evidence to preserve

A campaign row containing Name, Subject, From, and list but no verified body is an uncompleted shell. Record the attempted name and do not report it as a completed draft. If the content editor or browser automation fails, diagnose that step before creating additional shells.

## Send boundary

Creating a draft never sends email. Do not invoke test-campaign or start-campaign for this review-draft request. Test sends require the separate approval gate and both internal recipients.

## Chat attachment boundary

When the user asks for attached HTML files, respond with actual `MEDIA:/absolute/path/to/file.html` attachments. Do not substitute sandbox links or claim files were attached when the response contains no MEDIA paths.
