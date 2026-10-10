# Slack file-attachment recovery

## Symptom

Hermes posts the message text but returns:

`MEDIA attachments were omitted for slack; native send_message media delivery is currently only supported for ...`

Slack then shows no downloadable file card.

## Root cause

`MEDIA:/absolute/path` is parsed by Hermes, but the generic `send_message` abstraction is not uploading local files through Slack. The older successful behavior used the native Slack adapter and Slack's `files_upload_v2` endpoint.

A second blocker is a revoked or insufficient Slack connection. A Composio connection may report `token_revoked`; do not retry uploads with that connection.

## Recovery sequence

1. Stop treating a successful text-message response as attachment success.
2. Check whether the delivery result explicitly says media was omitted. If so, do not repeat the same call.
3. Reconnect the Slack app/token with at least:
   - `files:write`
   - `chat:write`
   - `im:write` for direct messages when required
   - `files:read` for verification
4. Restart Hermes after credentials or gateway configuration change:

   ```bash
   hermes gateway restart
   ```

5. Use the native Slack upload operation, equivalent to:

   ```python
   await client.files_upload_v2(
       channel=chat_id,
       file=file_path,
       filename=os.path.basename(file_path),
       initial_comment=caption,
       thread_ts=thread_ts,
   )
   ```

6. Test with one small known-good HTML or text file.
7. Verify the response contains a Slack file ID and downloadable permalink/metadata. Only then upload batches.
8. Keep batches small, such as 8 files, if the user requested batching. Upload one at a time if Slack or the gateway is unstable.

## Do not do

- Do not repeatedly retry `send_message` with the same `MEDIA:` paths after an explicit omission warning.
- Do not claim files are attached based on a successful message ID alone.
- Do not substitute sandbox links when the user asked for attachments.
- Do not ask the user to redo research or regenerate files when the artifact already exists and the blocker is transport.

## Evidence from the Hermes implementation

The native Slack adapter implements local-file upload through `files_upload_v2`, while the generic `send_message` path can omit media. The relevant implementation is in `gateway/platforms/slack.py`, method `_upload_file`.
