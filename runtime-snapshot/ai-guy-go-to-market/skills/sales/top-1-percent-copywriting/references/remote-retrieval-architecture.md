# Remote Retrieval Architecture

## Purpose

Keep the full 5.49 GB source corpus in private GitHub storage. Do not mirror the ZIP or extracted corpus onto the Hermes server. The installed skill is the routing and synthesis layer; the archive remains the source of truth.

## Runtime flow

1. Identify the requested format, audience, offer, market sophistication, awareness level, desired emotional temperature, and named writer or style.
2. Select one primary framework, one supporting swipe set, and one proof/reference source using the routing table in `SKILL.md`.
3. Query the private archive's manifest and context maps first.
4. Fetch only small, relevant text files or byte ranges through an authenticated GitHub retrieval tool.
5. Extract bounded excerpts, deduplicate overlapping sources, and use them as task context.
6. Draft original copy. Apply principles and structures; do not reproduce copyrighted campaigns verbatim.
7. Internally record source paths used and disclose them when useful.

## Recommended implementation

Use a thin retrieval service or MCP server with these operations:

- `copywriting_search(query, writer, format, limit)` — searches `MANIFEST.tsv`, context maps, and indexed text metadata.
- `copywriting_fetch(path, start, end)` — retrieves a bounded excerpt from an authorized source file.
- `copywriting_context(task, writer, format, audience)` — returns a compact, deduplicated context pack.

The service should maintain a small local metadata cache only: manifest, file paths, sizes, hashes, and optional embeddings of short metadata/chunks. Do not cache full copyrighted source files locally unless explicitly requested.

## Storage options

Preferred: private object storage or a private GitHub release as the source, plus a retrieval service that can authenticate server-side and stream only requested ranges.

Avoid: publicizing the archive merely to work around a connector limitation; downloading the complete release to the agent VPS; putting the corpus in prompt memory; or embedding full source text into the skill file.

## Operational safeguards

- Keep credentials server-side and read-only.
- Enforce path allowlists and bounded response sizes.
- Log query and source path, not full copyrighted excerpts.
- Rate-limit and cache metadata/results briefly.
- Verify release tag, per-file hashes, and source version before use.
- If remote retrieval is unavailable, say so and use the installed framework index without claiming full-corpus access.
