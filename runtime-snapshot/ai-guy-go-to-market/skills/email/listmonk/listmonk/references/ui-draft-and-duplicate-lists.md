# Listmonk UI draft workflow and duplicate-list guard

## Validated workflow

When API environment variables are absent or API credentials fail, but the user supplied working admin UI credentials and explicitly authorized a draft-only campaign:

1. Open the Listmonk admin login page and authenticate with the supplied UI username/password.
2. Navigate to Campaigns → Create new.
3. Inspect the list picker before entering campaign details. Record exact list IDs and subscriber counts through the same-origin `/api/lists?per_page=100` request or the UI.
4. If multiple lists have the same display name, do not guess. Ask the user which exact list ID to target.
5. Use the campaign’s **Raw HTML** format for an existing email HTML file.
6. Preserve the HTML’s media references only if they are absolute HTTPS URLs reachable by recipients. Local relative paths such as `images/hero.jpg` will not work when the campaign is viewed outside the local folder; host the assets and update the HTML first.
7. For draft-only work, save/continue the campaign but do not activate Send, test-send, schedule, publish, or start controls.

## Evidence and boundaries

- Successful admin UI login proves browser-session access, not API credential validity.
- A 403 `invalid API credentials` response means the supplied credentials were not accepted for the API path; it does not prove the instance is unavailable.
- Duplicate list names are an ambiguity requiring user selection by exact ID.
- Draft creation is a write operation and should be performed only after explicit user authorization.
