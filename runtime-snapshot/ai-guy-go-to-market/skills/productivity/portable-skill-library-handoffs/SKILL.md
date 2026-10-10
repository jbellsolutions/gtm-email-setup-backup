---
name: portable-skill-library-handoffs
description: Use when packaging a complete skill library for handoff.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, handoff, packaging, documentation, portability]
    related_skills: [hermes-agent-skill-authoring, docx, pdf, google-workspace]
---

# Portable Skill Library Handoffs

## Overview

Use this skill when someone asks to duplicate, export, publish, or hand off a working skill system to another agent or separate account. The deliverable is a complete, portable library, not a short summary of the most visible workflow.

Preserve the target library's class-level shape: rich `SKILL.md` files, supporting `references/` content where needed, and a clear index/load order. Remove account-specific credentials, private IDs, private paths, customer data, private metrics, proprietary campaign history, and assumptions that only hold in the source environment.

## When to use

- Another person or agent lacks access to the current thread.
- The user asks for “all the skills,” a duplicate skill library, or a shareable system.
- A workflow must operate against a separate account or workspace.
- The user requests publishable documents, a Google Doc/Drive package, DOCX, PDF, ZIP, or agent instructions.

## Required workflow

### 1. Inventory before summarizing

List every relevant class-level skill, not only the primary skill. Include adjacent operational skills that make the system work: execution/API, campaign operations, copy, research/personalization, verification, reply handling, scoring, deliverability, cadence, QA, send gates, sourcing, and platform-specific support.

For each skill, capture its name, trigger, role, dependencies, and linked references/scripts. Detect overlaps and retain them in the inventory rather than silently dropping them. Completion criterion: the index accounts for every skill selected for the package.

### 2. Classify portability

For each source item, separate:

- **Portable procedure:** keep and generalize.
- **Account-specific implementation:** replace with placeholders and recipient-owned variables.
- **Private operational history:** exclude unless it teaches a general pitfall.
- **Unverified or stale behavior:** label as unverified or rewrite as a verification step.
- **Credential/private data:** remove completely.

Never copy a source account's API key, campaign ID, mailbox, private URL, local path, customer record, or private metric into the handoff.

### 3. Preserve the skill hierarchy

Prefer a small set of class-level skills over a flat pile of narrow session artifacts. Each skill should have:

- YAML frontmatter with a trigger-focused description.
- A rich body explaining scope, steps, completion criteria, pitfalls, and verification.
- A `references/` pointer for session-specific detail, authoritative excerpts, API notes, or examples that should not stay in the always-loaded body.

Use a top-level `00-SKILLS-INDEX.md` with categories and load order. Add an explicit README explaining that the package is account-independent.

### 4. Write the receiving-agent contract

Include a system operating contract, end-to-end workflow, required inputs before side effects, human approval phrase and scope, stop conditions, exact distinctions between created/paused/imported/rendered/activated/sent/replied/booked, and instructions to operate only on the receiving team's account.

The agent must be able to start with read-only discovery and know what remains missing.

### 5. Produce publishable artifacts

#### Delivery fallback when the recipient cannot download local attachments

Do not stop at a local filesystem path or an opaque sandbox link when the user reports that downloads are unavailable. Provide a browser-accessible artifact URL and verify it before reporting success. Preferred order:

1. Upload to the user's connected Google Drive when the integration can access the staged artifact. Re-fetch metadata and report the returned `webViewLink`; do not claim Drive delivery from an upload response alone.
2. If Drive staging cannot access the local workspace, publish the exact artifact through an authenticated, persistent file-hosting service already configured for the account. Verify the public URL with an HTTP request and report that URL as the download path. Do not describe this as a Google Drive upload.
3. Keep the local ZIP/directory as a secondary artifact and include its checksum for integrity verification.

When the artifact contains many files, prefer a single ZIP for downloading, while also publishing a browsable index only if that adds value. Preserve the original ZIP byte-for-byte between export and upload, and verify the hosted artifact is the same file where the hosting service exposes a checksum or byte count.

Create, as appropriate:

- Full directory/ZIP containing all skills and support files.
- Readable handoff and agent-instructions documents.
- DOCX/PDF or a Google Doc when the user asks for shareability.

The publishable document must contain the complete skill index and actual skill guidance, not merely a statement that the skills exist. If a Google Doc is created, verify its ID, name, MIME type, non-trashed status, and `webViewLink` after creation.

### 6. Verify completeness and sanitation

Run checks for valid frontmatter and non-empty bodies; included or explicitly recipient-side references; absence of private credentials/account identifiers/internal paths/private data; compiling scripts and passing sample QA; archive contents; and substantive content in DOCX/PDF/Google Doc outputs.

Report any artifact that could not be created or uploaded. Do not claim a PDF/Drive upload succeeded without a returned ID or URL and verification fetch.

## Common pitfalls

1. **Condensing “all skills” into three representative skills.** Inventory first and include the complete operational system.
2. **Duplicating only the primary platform skill.** Include QA, verification, copy, reply, scoring, deliverability, cadence, sourcing, and research dependencies.
3. **Publishing a handoff that says a skill exists but omits its body.** Put actual portable guidance in the document or attach the complete skill directory.
4. **Copying private source context into a “sanitized” package.** Scan source and generated documents for sensitive terms and inspect the final artifacts.
5. **Treating a successful creation response as shareability proof.** Re-fetch metadata and verify the returned link.
6. **Mixing source-specific behavior with portable guidance.** Convert incidents into general verification gates and pitfalls; do not present historical IDs or local paths as recipient instructions.
7. **Flattening every issue into a narrow skill.** Keep session-specific detail in `references/` under the relevant class-level umbrella.
8. **Using “Charm Offensive” as a request to reproduce private identity.** Preserve general writing principles, but require the receiving team to supply its own profile, claims, proof, and personality assets.

## Verification checklist

- [ ] Complete skill inventory exists.
- [ ] Class-level hierarchy is preserved.
- [ ] Index includes load order and dependencies.
- [ ] System prompt and workflow are included.
- [ ] Agent instructions are included.
- [ ] Handoff checklist and stop conditions are included.
- [ ] Private credentials and source-account identifiers are absent.
- [ ] Support references are attached or clearly listed.
- [ ] ZIP/package contains all selected skills.
- [ ] DOCX/PDF/Google Doc, if requested, contains the full content.
- [ ] External artifact IDs/URLs were verified before reporting success.
