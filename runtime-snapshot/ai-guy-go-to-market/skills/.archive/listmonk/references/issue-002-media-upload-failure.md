# Issue 002 media-upload failure and recovery notes

## What happened

The Dealmaker Issue 002 ZIP contained Windows-style archive member names such as `images\\banner.jpg`, `images\\s1.jpg`, and `images\\s2.jpg`. A normal extraction created filenames containing literal backslashes rather than an `images/` directory. Normalize member paths immediately after extraction.

The HTML referenced relative assets (`images/banner.jpg`, etc.). ListMonk media hosting requires a separate authenticated multipart request to `POST /api/media` with `file=`. Starting a local HTTP server only proves local serving, not ESP hosting. The browser fetch also failed when the local server was not reachable from the browser context, so do not use that as the upload verification mechanism.

## Required verification loop

1. Extract ZIP entries and replace `\\` with `/` in member names.
2. Confirm each expected image exists and inspect dimensions/format.
3. Authenticate to ListMonk via a valid API token or logged-in same-origin browser session.
4. Upload each image individually with multipart `file=` to `POST /api/media`.
5. Record the returned hosted URL and fetch it, checking HTTP success and image content type.
6. Rewrite the HTML `src` attributes to those hosted URLs.
7. Create/update the campaign as HTML, preserving From display name `The Dealmaker` and Reply-To `xander@usingaitoscale.com`.
8. GET the campaign and verify draft status, non-empty body, body hash/length, hosted URLs, and both `{{ MessageURL }}` and `{{ UnsubscribeURL }}`.
9. Only then send the controlled test to exactly `xander@usingaitoscale.com` and `justin@usingaitoscale.com`.
10. Verify delivery in the real inboxes before requesting approval for any list send.

Never claim image hosting or test delivery without API response and post-send evidence.