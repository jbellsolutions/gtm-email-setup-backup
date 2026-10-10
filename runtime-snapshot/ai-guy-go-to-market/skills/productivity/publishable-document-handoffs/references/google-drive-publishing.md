# Google Drive Publishing Reference

## Verified text-document recipe

Use Composio's connected Google Drive/Docs account. Search or resolve the destination folder first when the user names one. Folder operations require the opaque folder ID, not its display name.

For a complete text handoff, call `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` with:

- `file_name`: a human-readable title
- `mime_type`: `application/vnd.google-apps.document`
- `text_content`: the complete sanitized handoff
- `parent_id`: the verified folder ID, if applicable

Capture the returned file ID. Then call `GOOGLEDRIVE_GET_FILE_METADATA` with `fields` set to:

`id,name,mimeType,webViewLink,webContentLink,trashed,parents`

Return `webViewLink` as the primary link. The verified response should show the intended name, Google Docs MIME type, non-trashed state, and expected parent.

## Permission boundary

Creation normally leaves the file private. Do not broaden access unless the user explicitly requests it and gives the intended audience. For named sharing, use the least-privileged reader/writer role required. For link sharing, verify policy allows it, create the permission, then re-fetch metadata and optionally list permissions. Never infer sharing from a file ID or display URL alone.

## Binary artifact boundary

Binary upload tools may require a staged, cloud-backed `s3key`, not a local filesystem path. A local path that exists in the agent environment may not exist in the remote connector sandbox. If staging cannot be verified, do not claim the binary is in Drive. Publish a text-based Google Doc as the verified shareable artifact and provide the local DOCX/PDF/archive path separately.

## Final reporting template

- **Verified Google Doc:** `<webViewLink>`
- **Local files:** absolute paths
- **Sanitized:** credentials, private IDs, internal paths, customer data, organization-specific history
- **Verified:** file identity, MIME type, non-trashed state, metadata link
- **Not verified:** permission scope or binary Drive upload, if applicable
