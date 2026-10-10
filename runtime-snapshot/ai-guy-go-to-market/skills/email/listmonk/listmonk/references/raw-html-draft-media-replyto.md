# Raw HTML draft creation with hosted media and Reply-To

Use this sequence when creating multiple ListMonk drafts from ZIP-packaged HTML. It is draft-only: never call `/status` with `running` and never call `/test`.

1. Run `GET /api/health`, then inventory lists and confirm the intended master list ID and subscriber data. The native first-name field is derived from the subscriber's parsed name; inspect sample subscribers and always keep a fallback in the template.
2. Extract each ZIP's complete `index.html` and every file under `images/`. Upload each image through `POST /api/media` as multipart. Use unique upload filenames per campaign (for example `dealmaker-banner.jpg`) rather than reusing a basename already in media storage; otherwise a filename lookup can accidentally reference another issue's image.
3. Rewrite every image occurrence, not only `<img src>`: HTML `src`, `background`, CSS `background-image:url(...)`, and Outlook VML `<v:image src=...>`. Preserve comments only when useful, but verify the stored body has no relative `images/` references in actual markup or style attributes.
4. Convert only platform placeholders to `{{ MessageURL }}` and `{{ UnsubscribeURL }}`. For first-name personalization use `{{ .Subscriber.FirstName }}` with a Go-template fallback, e.g. `{{ if .Subscriber.FirstName }}{{ .Subscriber.FirstName }}{{ else }}there{{ end }}`.
5. Create with a file-backed JSON payload: `type=regular`, `content_type=html`, `template_id=8`, exact `from_email`, subject, list ID, and complete transformed body. Then GET the campaign.
6. Persist Reply-To as the campaign header, not merely an unsupported top-level `reply_to` field: `headers: [{"name":"Reply-To","value":"xander@usingaitoscale.com"}]`. Re-read and require that header to be present.
7. GET-after-write verification must require: `status=draft`, `sent=0`, `content_type=html`, `template_id=8`, expected list, exact sender/subject, nonempty body, body hash equal to the transformed source, Reply-To header present, and no relative image markup. Keep the source and transformed body on disk until verification finishes.

A raw substring search for `images/` can match instructional comments or image prompts. Distinguish comments from actual markup when diagnosing; the stronger gate is to inspect `src`, `background`, and CSS `url(...)` attributes while separately recording any comment-only occurrences.
