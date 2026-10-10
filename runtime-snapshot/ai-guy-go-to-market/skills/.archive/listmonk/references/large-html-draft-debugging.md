# Large HTML draft debugging

## Scope
Use when a user wants to inspect an unfinished newsletter HTML artifact in ListMonk without sending it.

## Known-good draft boundary

A visual draft is allowed to contain image placeholders, an unresolved Medium destination, and other unfinished copy when the user explicitly requests a preview. Do not impose send-ready gates on draft creation. Still preserve `status: draft`, `sent: 0`, and no schedule or test send.

## Upload preparation

1. Read the actual HTML file from disk. Do not reconstruct it from a summary or replace it with a tiny editor placeholder.
2. Replace generic tokens ListMonk cannot compile:
   - `{{VIEW_ONLINE_LINK}}` → `{{ MessageURL }}`
   - `{{UNSUBSCRIBE_LINK}}` → `{{ UnsubscribeURL }}`
3. Never pass literal `{{MEDIUM_URL}}`: Go-template compilation treats it as an undefined function. For a visual-only draft, use a clearly labeled approved temporary URL, or leave the article link as a normal non-template placeholder only if the user accepts the preview limitation.
4. Set `content_type: html` and preserve the campaign metadata.

## Persistence verification

After every create/update, GET `/api/campaigns/{id}` and compare:

- `status == "draft"`
- `content_type == "html"`
- `sent == 0`
- body is non-empty
- body length is close to the transformed source HTML length
- body begins with the expected document marker (`<!DOCTYPE` or the source's actual beginning)
- logo, image placeholder labels, source links, CTA, and ListMonk merge fields are present

A successful PUT response or a visible editor state is not enough. In the Issue 2 failure pattern, the UI returned HTTP 200 while the campaign record continued to contain `<p>test</p>` (11 bytes). Treat that as failure.

## Transport strategy

- Prefer a valid dedicated API token with `curl --data-binary @payload.json`.
- If API credentials are unavailable, use the authenticated browser session and absolute API URLs.
- Avoid shell interpolation of raw HTML: quotes, backticks, braces, and CSS frequently corrupt the request.
- For browser transport, keep the full body in one browser-side variable fetched from a local HTTP server or injected from a correctly escaped base64 payload. Do not rely on a contenteditable editor's visible DOM state unless the GET verification confirms persistence.
- For very large bodies, use a two-step update only if the API supports it, and verify after each step.

## Failure classification

- `400 function "MEDIUM_URL" not defined`: unresolved generic token reached Go-template compilation.
- `403 invalid API credentials`: the API token is invalid or differs from the admin UI session. Do not blindly retry the same token.
- HTTP 200 but stale/empty GET body: browser/editor persistence failure. Re-authenticate, reload the source, retry a file-backed or browser-side update, then verify again.

## Hard stop
Never claim that the HTML draft was uploaded until the persisted campaign record contains the actual body. A draft shell with `<p>test</p>` is not the newsletter draft.
