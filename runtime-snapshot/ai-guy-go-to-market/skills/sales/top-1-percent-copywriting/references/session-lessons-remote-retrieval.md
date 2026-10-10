# Session lessons: remote retrieval over bulk ingestion

## User expectation

The user wanted the GitHub-hosted archive to be readily available on demand without consuming server disk. The correct architecture is a remote retrieval layer, not a local download, ZIP assembly, extraction, or full-corpus vectorization on the Hermes VPS.

## Failure modes to avoid

- Do not treat a skill file as ingestion.
- Do not claim an MCP service exists until its server file, Hermes configuration, tool discovery, and real search/fetch calls are verified.
- Do not repeatedly ask the user for a PAT when an existing OAuth connection can authorize access.
- Do not ask the user to expose private copyrighted material publicly just to work around a connector limitation without explicit approval and a rights warning.
- Do not start multi-gigabyte downloads before calculating disk requirements for parts, assembled ZIP, extraction, and indexes.
- Do not report "done" while only release metadata has been inspected.

## Proven implementation pattern

1. Inspect the actual repository/release metadata and determine the archive layout.
2. Prefer a thin MCP service that stores no full corpus locally.
3. Cache only the small manifest and service metadata.
4. Use HTTP range requests against remote split ZIP assets.
5. Open the remote split ZIP as a seekable stream and read only the central directory plus requested members.
6. Expose bounded tools: `copywriting_search`, `copywriting_fetch`, `copywriting_context`, and `copywriting_status`.
7. Normalize archive paths, including an optional top-level `Top 1% Copywriting/` directory.
8. Test through the actual MCP stdio protocol, not only direct Python imports.
9. Configure the server under Hermes `mcp_servers`, then restart/reload Hermes before claiming availability.
10. Distinguish skill, service, connectivity, and local-corpus states in every status update.

## Validation checklist

- `python3 -m py_compile /opt/data/tools/copywriting_retrieval_mcp/server.py`
- MCP `list_tools()` returns all four tools.
- Search returns expected archive paths for a known query such as Bencivenga bullets.
- Fetch returns real text from a known text member.
- Context returns bounded excerpts and source paths.
- `copywriting_status` reports `local_corpus: false`.
- Hermes config contains `mcp_servers.copywriting_retrieval`.
- Disk usage confirms no downloaded archive parts remain.

## Future improvement

Manifest search is lexical, not a true embedding/vector database. If semantic retrieval becomes necessary, build embeddings from metadata and bounded remote chunks in a separate low-storage index, while retaining GitHub as the canonical source and never mirroring the full archive by default.
