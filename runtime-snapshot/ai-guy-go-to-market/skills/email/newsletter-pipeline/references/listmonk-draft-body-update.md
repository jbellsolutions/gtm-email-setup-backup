# ListMonk draft body update

## Scope
Use this when putting a review HTML artifact into an existing ListMonk draft. This workflow does not send anything.

## Known facts
- The ListMonk instance is the Railway deployment documented in the listmonk/email-platform skills.
- Existing draft updates can be performed through the authenticated browser session when API credentials are unavailable or rejected.
- `PUT /api/campaigns/{id}` accepts the campaign fields and validates the body as a Go template.

## Placeholder conversion
Before upload:

```text
{{VIEW_ONLINE_LINK}}  ->  {{ MessageURL }}
{{UNSUBSCRIBE_LINK}}  ->  {{ UnsubscribeURL }}
```

Do not upload literal `{{MEDIUM_URL}}`. Go-template parsing interprets the token as a function call and returns an error like:

```text
function "MEDIUM_URL" not defined
```

Resolve the Medium article first and replace the token with the confirmed URL. Do not invent a publication URL. If the user explicitly requests a visual-only draft before publication, use an approved temporary URL and label the draft accordingly.

## Safe update procedure

1. Open the campaign and confirm its ID, name, subject, target list, and `status: draft`.
2. Read the local HTML artifact and apply only the two ListMonk merge-field substitutions above plus any explicitly approved Medium URL resolution.
3. Update through the authenticated browser session or REST API with `content_type: html`, preserving the existing draft metadata.
4. Do not click Start campaign, schedule it, send a test, or alter its status.
5. Fetch the campaign record after saving.
6. Verify all of these:
   - `status` remains `draft`.
   - `content_type` is `html`.
   - body is non-empty.
   - body length is close to the source artifact length after substitutions.
   - body begins with the expected HTML document and contains the logo, placeholder blocks, source links, CTA, `MessageURL`, and `UnsubscribeURL`.
7. If the body is empty, tiny, or still contains `<p>test</p>`, report failure and do not claim completion.

## Failure modes

- **400 `function "MEDIUM_URL" not defined`:** unresolved generic token reached ListMonk's Go-template compiler. Replace it before retrying.
- **403 invalid API credentials:** API credentials are not the same as the logged-in admin UI session. Reuse the authenticated browser session or obtain a valid dedicated API token. Do not keep retrying a known-invalid token.
- **UI appears to save but API body remains empty/stale:** treat the campaign as incomplete. Verify the persisted record, not the editor state.
- **Large HTML body:** avoid shell interpolation and hand-typed JSON. Use a file-backed JSON payload with `curl --data-binary`, a correctly escaped base64 transport, or browser-side fetch with the full body. Always verify persistence afterward.

## Hard stop
A draft with no body is not a completed draft. The only valid completion claim is a persisted ListMonk campaign record with a non-empty HTML body and `status: draft`.