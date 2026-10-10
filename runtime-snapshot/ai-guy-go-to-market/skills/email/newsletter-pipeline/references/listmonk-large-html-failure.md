# ListMonk large HTML draft failure pattern

## Reproduction

A campaign draft can return HTTP 200 from the browser-side `PUT /api/campaigns/{id}` while the persisted record still contains an earlier tiny body such as `<p>test</p>`. Always GET the campaign after every update and compare the stored body length/hash with the source.

## Known causes

- Browser navigation destroys the page-scoped variable holding the HTML.
- The browser session can remain authenticated while the HTML variable is lost.
- An unresolved `{{MEDIUM_URL}}` token is parsed as a Go-template function and produces `function "MEDIUM_URL" not defined`.
- The direct API token may be invalid even while the admin UI session works.
- Shell interpolation of raw JSON containing CSS/HTML can split the command at semicolons, quotes, or redirects and corrupt the update request.

## Correct handling

1. Extract `index.html` from the ZIP; do not upload the ZIP itself.
2. Convert only generic ESP merge fields:
   - `{{VIEW_ONLINE_LINK}}` to `{{ MessageURL }}`
   - `{{UNSUBSCRIBE_LINK}}` to `{{ UnsubscribeURL }}`
3. Resolve `{{MEDIUM_URL}}` before upload. For a visual-only draft, use an explicitly approved temporary URL and label the draft as a review draft.
4. Keep the ListMonk campaign in `status: draft`; never click Start, schedule, or send a test for this request.
5. Prefer a file-backed JSON payload with `curl --data-binary` and a valid dedicated API token. Do not hand-type or shell-interpolate the body.
6. If API credentials are unavailable, use the authenticated browser session, but load the complete HTML immediately before the update and verify persistence immediately afterward. Do not navigate away between loading the body and sending the PUT.
7. If the GET remains stale after one verified retry, stop. Do not repeatedly claim success or loop the same browser update.

## Completion gate

The draft is complete only when the GET response proves:

- `status: draft`
- `content_type: html`
- `sent: 0`
- body is non-empty
- body length/hash matches the transformed source HTML
- expected logo, placeholder blocks, source links, CTA, `MessageURL`, and `UnsubscribeURL` are present

## Error evidence from Issue 2

- Campaign 20 retained `<p>test</p>` with body length 11 despite successful browser-side update responses.
- Direct API update using the recorded API token returned `403 invalid API credentials`.
- An earlier raw update with literal `{{MEDIUM_URL}}` returned `400 function "MEDIUM_URL" not defined`.
- One shell-interpolated update caused CSS/HTML fragments to be interpreted as shell commands. This is why raw HTML must be transported file-backed or through a correctly escaped payload, never pasted into a shell command string.
