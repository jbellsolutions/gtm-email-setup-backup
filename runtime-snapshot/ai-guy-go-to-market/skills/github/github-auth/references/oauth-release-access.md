# Connected GitHub OAuth and Private Release Assets

## Proven workflow

1. Search the available integration/tool registry for GitHub OAuth capabilities before asking for a personal access token.
2. Validate the connection with `GITHUB_GET_THE_AUTHENTICATED_USER` using an explicit empty argument object when required.
3. Retrieve private release metadata by tag through the authenticated GitHub API. The REST endpoint is:

```text
GET /repos/{owner}/{repo}/releases/tags/{tag}
```

4. Inspect asset names, sizes, and download URLs. For large split archives, do not download until the manifest (`PARTS.json` or equivalent) has been compared against the live asset metadata.
5. Treat any size or checksum mismatch as a hard verification gate. Report it clearly and do not claim full ingestion.

## Case study: Top 1% Copywriting archive

The connected OAuth account authenticated successfully for `jbellsolutions`. The private `v1.0.0` release was found with release ID `363587425` and three split ZIP assets:

- `Top-1-Percent-Copywriting.zip.part-00`: expected/live 1,887,436,800 bytes
- `Top-1-Percent-Copywriting.zip.part-01`: expected/live 1,887,436,800 bytes
- `Top-1-Percent-Copywriting.zip.part-02`: manifest expected 1,200,707,550 bytes; live GitHub release metadata reported 1,200,760,731 bytes

The 53,181-byte discrepancy means the release must not be presented as verified until the downloaded asset's actual SHA-256 is checked against `SHA256SUMS` and the assembled archive is checked against `PARTS.json`. The repository manifest may be stale, or the release asset may have changed.

## Messaging rule

When the user asks for one-click OAuth, answer that path directly. Do not repeatedly send PAT instructions. Explain that local `gh` availability is separate from the hosted agent's connected OAuth integration. Never expose tokens or full profile payloads.

## Pitfalls

- `GITHUB_LIST_RELEASES` may require explicit `owner` and `repo`; if a wrapper drops arguments, use a direct authenticated REST request or a tool with a complete schema.
- A public `git ls-remote` result does not prove private release-asset access.
- Repository source metadata and release assets can disagree. Verify the live asset, not only the checked-in manifest.
- Do not silently substitute the compressed ZIP size for extracted corpus size. Report both units and both states.
