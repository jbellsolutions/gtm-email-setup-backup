# Validated handoff-install reference

## Archive inspection

Extract the ZIP outside the vault into a fresh scratch directory. Normalize archive member names by replacing `\\` with `/` before writing files; the handoff archive used Windows separators. Count actual files after extraction. In the validated run, the archive contained 69 files, with top-level `INSTALL/` and `Newsletters/`; `INSTALL/MANIFEST.md` existed and documented 68 rows because it excluded itself.

## Add-only merge

Parse the guide’s grouped directory headings and file bullets into 60 destination paths. Check all 60 with `exists()` before copying. In the validated run there were zero collisions. Copy the contents of `Newsletters/`, not the directory itself, and do not copy `INSTALL/`. Immediately test the destination for a nested `Newsletters/Newsletters` path; the validated result was `OK`.

## Patch and QA capture

For each patch in order, calculate SHA-256 before copying and compare to the guide’s pre-state. Copy only on a match, then calculate the post-state and compare. The validated run applied P1–P5 with matching pre/post hashes. For P5, run one target per Python invocation from `Revenue Partner Newsletter`, capturing both the final check-count line and exit status:

- Before: template `39 checks, 5 failed` (exit 1); reference Issue 001 `39 checks, 0 failed` (exit 0); built Issue 001 `39 checks, 1 failed` (exit 1).
- After: template `39 checks, 4 failed` (exit 1); reference Issue 001 `39 checks, 0 failed` (exit 0); built Issue 001 `39 checks, 0 failed` (exit 0).

The template’s remaining failures are expected because it contains unfilled slots and slot-valued alt attributes.

## Self-test evidence pattern

The System hub defines three layers: System process/documentation routing, publication operating notes, and the publication portable kit as authority. The read-before-write doctrine requires the same-session authority read, no reliance on memory or summaries, explicit authority paths, brand-specific branching, and locked publication assets except additions/logged patches.

For a Credit Memo Issue 002 dry-run, the issue ledger and original-build source table establish that two separate builds are numbered 001. The plan must exclude both coverage sets, list the actual read order and per-file constraints, and state that future topics require a fresh research session. Never invent topics, statistics, URLs, or HTML in this self-test.

## Common report elements

Report archive count, manifest rows, top-level contents, collision result, copied-file count, nesting guard, each patch status and hashes, six QA lines, verification hashes, the three-layer restatement, read-order evidence, duplicate-build ambiguity, registry open items with owners, human action items, and anything skipped or unverifiable. Then stop without beginning newsletter work.
