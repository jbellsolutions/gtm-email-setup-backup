# Session lessons: source verification and Slack attachment handoff

## Mandatory source gate

Delegated research summaries and delegated QA counts are leads, not proof. Before revising or delivering an editorial issue, the primary workflow must independently fetch every final customer-facing news URL with an HTTP GET and inspect the returned page body. A claimed HTTP 200 in a subagent ledger is insufficient. Reject and replace any URL that returns 404, 403, a bot challenge, a homepage, a soft redirect, a login wall, or content that does not contain the exact claim. Never construct a publisher slug from a Google News redirect or infer a live URL from its naming pattern.

For each of the three news cards, preserve a ledger row containing: final direct URL, fetch timestamp, HTTP status, final URL after redirects, publisher/date, exact supporting sentence or figure copied from the fetched page, and permitted wording. If access is blocked, record the non-200 honestly and do not call it verified. The native shared Medium URL may remain a draft link when the user explicitly supplies its content, but its 403/Cloudflare limitation must be disclosed and no direct 200 claim may be made.

Do not deliver all five niche revisions in parallel when the user specifies a checkpoint. Finish Agency Insider, independently verify it, deliver its HTML plus ledger, and stop for review before touching the other four. After that approval, work one niche at a time. If a niche cannot support three verified news stories, report the blocker rather than filling with general industry knowledge or Wikipedia.

## Exact-value revision gate

When the user supplies exact values, patch them literally and scan customer-visible HTML after stripping comments: byline, From local part, Reply-To, CAN-SPAM address, neutral cold-outbound receiving line, CTA text and URL, rating subjects, merge tags, and native-card position. The only permitted ListMonk tags for this niche family are `{{ MessageURL }}` and `{{ UnsubscribeURL }}`. Remove old opt-in language, placeholder fields, internal publisher names, duplicated bylines, and invented case-study metrics. Keep source ledgers and image prompts in HTML comments, but do not let comment text affect customer-facing QA.

## Slack file delivery gate

`functions.send_message` with `MEDIA:/absolute/path` can report success while explicitly omitting Slack attachments. Treat that warning as failed delivery and do not retry the same generic route. The successful historical path was Hermes' native gateway response parser, which detects MEDIA directives in the assistant's final response and calls Slack `files_upload_v2`. When that native path is available, put the exact local paths in the final response and verify the resulting Slack file metadata/cards before claiming delivery. Do not substitute Composio for this path unless the user explicitly asks for it. If the native gateway is not exposed in the current tool surface, report the attachment blocker and preserve the files locally.
