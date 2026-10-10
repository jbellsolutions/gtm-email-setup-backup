# Release ingestion incident reference

## What happened

The v1.0.0 GitHub release was initially inspected through the connected GitHub OAuth integration. OAuth could validate the account and enumerate the private release assets, but the available connector path did not provide a usable multi-gigabyte binary stream to local storage. After the repository was made public, direct release URLs worked with `curl`.

## Verified live asset facts

The live release assets reported:

- `Top-1-Percent-Copywriting.zip.part-00`: 1,887,436,800 bytes
- `Top-1-Percent-Copywriting.zip.part-01`: 1,887,436,800 bytes
- `Top-1-Percent-Copywriting.zip.part-02`: 1,200,760,731 bytes

The repository metadata had initially described a different Part 02 size. The live `SHA256SUMS` downloaded from the public release was authoritative for the downloaded assets, and all three live part checksums passed:

- `5b8f99f60c2ceceb2682b8b1a3a754d4e7ed5d8aad1c170eeba8867d4d672792`
- `1b5fd97ac17336c52ef0d266a83dc57475adb831e306f5df0d70cc3eadaf0a80`
- `50ca730a069fa56ce5908e4a00e4874d1e0606ac1b9738084cc21cb23147b4c9`

The live metadata reported assembled archive size `4,975,634,331` bytes and assembled SHA-256 `8751005e4c200fcb783b9d4c7b4eeb7f33c28d4330cae90c699978f0bdc86102`.

## Failure mode

The parts occupied about 4.7 GB. Concatenating them into a separate ZIP requires another 4.98 GB before extraction. The server had only about 4.2 GB free, so `cat part-* > archive.zip` failed with `No space left on device`. The failed partial ZIP must be deleted before retrying. Do not delete session history or project data without approval. Disposable browser and package caches may be reclaimed first, but verify scope before removal.

## Correct procedure

1. Download release metadata and all parts.
2. Verify each part against the **live** `SHA256SUMS` file.
3. Check free disk space before assembly. Required space is approximately: existing parts + assembled ZIP + extracted source tree + temporary working room.
4. Assemble only when the preflight passes.
5. Verify assembled ZIP size and SHA-256.
6. Run `unzip -tq`.
7. Extract to a destination with sufficient capacity.
8. Build a lightweight text/path index, not a second full duplicate of the archive unless storage allows it.
9. Point the copywriting skill at the extracted root and record the verified release facts.

## User-facing status rule

Do not say “downloaded,” “ingested,” or “done” when only release metadata, partial assets, or verified split parts exist. State the exact completed layer and the exact blocker. When an action is needed, give one concrete action, not a menu.