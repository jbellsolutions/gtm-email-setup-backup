# ListMonk file-backed HTML draft update

Use this for a user-requested visual draft when the campaign must contain the actual `index.html`, but nothing may be sent.

## Reproduction-safe sequence

1. Identify the ZIP or extracted `index.html`; do not reconstruct the HTML from a summary.
2. Read the file as text and retain the complete document, including `<!DOCTYPE>`, styles, tables, placeholders, and comments.
3. Convert only the ESP merge fields:
   - `{{VIEW_ONLINE_LINK}}` → `{{ MessageURL }}`
   - `{{UNSUBSCRIBE_LINK}}` → `{{ UnsubscribeURL }}`
4. Raw `{{MEDIUM_URL}}` is parsed by ListMonk as a Go-template function. For a review-only draft where publication is not complete, encode the braces as `&#123;&#123;MEDIUM_URL&#125;&#125;` so the marker remains visible without template compilation failure. Do not use this for a send-ready campaign.
5. GET the named campaign and confirm the exact ID, name, `status: draft`, list, subject, template, and sender metadata.
6. Perform one authenticated REST `PUT` with a JSON-encoded payload that preserves the campaign metadata and replaces only the body/content fields. Use a file-backed or programmatically encoded payload for large HTML. Never interpolate the HTML into a shell command.
7. GET the same campaign immediately afterward and verify:
   - `status == draft`
   - `content_type == html`
   - `sent == 0`
   - body begins with the expected document (`<!DOCTYPE` when present)
   - body is not `<p>test</p>` or another shell placeholder
   - stored body length and SHA-256 equal the intended transformed body
   - expected `MessageURL` and `UnsubscribeURL` fields exist
8. Only then report completion. Do not test-send, schedule, start, or modify recipients.

## Why Issue 001 worked and Issue 002 initially failed

Issue 001 used the complete transformed HTML in the successful API creation payload and was verified afterward. Issue 002 initially created campaign 20 with `body: "<p>test</p>"`; a later browser request returned HTTP 200 but did not persist the replacement. HTTP success is not persistence proof. The post-write GET is mandatory.

## Failure handling

If the post-write GET shows a tiny/stale body, stop claiming completion. Do not repeat the same browser PUT. Use one authenticated file-backed REST update, or report an authentication/persistence blocker. A draft shell is safe; it is not a populated HTML draft until the stored body is verified.
