# ListMonk UI raw-HTML editor persistence

## Why this matters

The campaign metadata form can create a valid-looking draft shell while the body remains empty or stale. Do not treat selecting a list and clicking Continue as content persistence.

## One-campaign sequence

1. Log in through `/admin/login` and navigate to `/admin/campaigns/new`.
2. Enter campaign name, subject, From address, and select the intended list.
3. Select **Raw HTML** in the Format dropdown before clicking Continue.
4. Click Continue to create the draft shell.
5. In the Content tab, confirm the format still says **Raw HTML**.
6. Locate the CodeMirror editor (`.cm-content[contenteditable="true"]`). Insert the complete HTML through the editor's supported input path, not by changing an unrelated hidden textarea. After insertion, read back `innerText`/editor content and require a length close to the source length.
7. Click **Save changes**.
8. Reopen the campaign or GET `/api/campaigns/{id}` from the authenticated same-origin session.
9. Verify: `status == "draft"`, `sent == 0`, expected list ID, `content_type == "html"`, non-empty body, and source/body hash match after approved ListMonk placeholder conversions.
10. Only then start the next campaign.

## Failure evidence

- The Rich Text editor may appear blank after a failed insertion even when a textarea contains `{}`.
- `document.execCommand('insertText', ...)` can return successfully while CodeMirror retains only a one-character value or stale state. Read the editor value after insertion and before saving.
- Direct REST calls with admin credentials can return `403 invalid API credentials`; do not assume the UI session credentials are valid API credentials.
- If the body cannot be persisted and verified, delete the empty shell and report the blocker. Never leave a misleading draft record or claim completion.

## Content requirements

Before insertion, convert generic placeholders for ListMonk:
- `{{VIEW_ONLINE_LINK}}` → `{{ MessageURL }}`
- `{{UNSUBSCRIBE_LINK}}` → `{{ UnsubscribeURL }}`
- Do not pass raw `{{MEDIUM_URL}}`; for an explicitly unfinished visual draft, encode its braces as HTML entities so the marker remains visible without Go-template parsing failure.
