---
name: newsletter-documentation-installs
description: Use when installing newsletter docs in Obsidian.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, obsidian, installation, documentation, qa, hash-verification]
    related_skills: [newsletter-pipeline, obsidian]
---

# Newsletter Documentation Package Installation

## Trigger

Use this workflow when a ZIP or directory adds newsletter system documentation, process notes, publication scaffolding, kits, or controlled patches to an Obsidian vault. This is documentation/process installation, not newsletter production.

## Safety boundary

1. Never send, schedule, publish, or test-send email.
2. Take no external actions and make no network/API calls to sending platforms.
3. Do not generate images. Agents may write prompts only.
4. Do not alter, reformat, retitle, or tidy existing vault files except explicitly listed, hash-guarded patches.
5. Never overwrite an add-only collision. Stop and report it.
6. Apply a patch only when the destination SHA-256 equals its recorded pre-state. If it differs, skip it and report the mismatch.
7. Keep extraction scaffolding in scratch. Write only to the authorized vault subtree and scratch directory.

## Procedure

1. Extract into a fresh scratch directory outside the vault. Normalize Windows backslash separators, then count actual files.
2. Read the manifest and guide. Confirm expected archive count and manifest row count according to the manifest’s own semantics, which may exclude itself.
3. Parse the complete add-only destination list and preflight every path against the vault before copying. Any collision stops the merge.
4. Merge the **contents** of the package’s `Newsletters/` directory into the destination `Newsletters/` directory. Never copy the source directory itself or `INSTALL/`.
5. Run the nesting guard immediately after merge. If `Newsletters/Newsletters` exists, remove only that newly nested tree, redo the content merge, and re-run the guard.
6. Apply patches one at a time in specified order. Hash current destination, compare pre-state, copy only on match, hash again, and compare post-state. Record both hashes and the result.
7. For executable QA patches, run each target separately before and after from the guide’s required working directory. Capture the actual `N checks, N failed` line and exit status.
8. Verify installed counts and every guide verification hash. Report mismatches; never repair them opportunistically.
9. Self-test from the installed vault: read the System hub, six generic skills (exclude README), publication hub/ledger, kit authority files, issue records, and registry open items. Restate the architecture in one paragraph.
10. For a dry-run issue plan, list exact read order and one constraint learned from every file. Explicitly distinguish duplicate prior builds. Do not invent future topics, statistics, URLs, or research claims. Say that topics require a fresh research session.
11. Report all phases, skips, unverifiable files, QA results, blockers with owners, and human action items. Stop; do not begin issue work.

## Context capture and onboarding briefs

When a user is still deciding whether to onboard a publication, capture their supplied context in a clearly marked working brief before creating a brand pack. Keep decisions, corrections, assumptions, pending URLs, approvals, and supplied operational context separate. If the user corrects an earlier answer (for example, audience scope or edition structure), preserve the corrected state and remove ambiguity rather than carrying both versions forward.

Do not treat a working brief as a brand pack, authority file, or issue brief. Do not register or build the publication until the user has supplied or explicitly resolved the required onboarding fields. For sequential decision-making, ask one material question at a time and explain the decision's operational impact before requesting an answer; maintain a concise pending-decision list.

After writing a context brief, perform independent checks for: factual capture, corrected decisions, pending destinations and CTA status, format and compliance boundaries, and file integrity/collision safety. Report the check results and any unresolved ambiguity. Do not create newsletter content as part of context capture.

## Pitfalls

- ZIP entries may use backslashes; naïve extraction can create literal-backslash filenames.
- A manifest can have fewer rows than package files because it excludes itself.
- A nested copy can pass a simple file-count check; the explicit guard is mandatory.
- The System layer routes and summarizes but is not authority for brand-specific values.
- If two builds share an issue number, exclude both coverage sets during duplicate checking.
- A template intentionally has unfilled slots, so its QA failures may be expected.
- Do not preserve superseded audience or CTA decisions as if they are still active; label historical context and state the current decision.
- Do not silently convert conceptual destinations into URLs or claim approvals that were not documented.

## References

See `references/documentation-handoff-install.md` for the validated command pattern, QA capture format, and self-test evidence.

---
Tags: [[newsletter]] [[newsletter-system]] [[obsidian]] [[installation]] [[qa]]
