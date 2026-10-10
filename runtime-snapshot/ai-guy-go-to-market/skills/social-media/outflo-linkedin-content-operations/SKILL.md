---
name: outflo-linkedin-content-operations
description: "Use for OutFlo LinkedIn content, QA, and publishing."
version: "1.0.0"
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [OutFlo, LinkedIn, content, campaigns, publishing, QA]
    related_skills: [outflo-linkedin, linkedin-post-creator, campaign-operations]
---

# OutFlo LinkedIn Content Operations

## Overview

Run a source-backed, review-first content system for multiple LinkedIn profiles connected to OutFlo. Separate internal and client campaigns, create distinct per-profile variants, and track every draft through QA, approval, scheduling, asynchronous delivery, and audit.

The canonical posting API is `https://api.outflo.io/api/public/v1/posting`. Authenticate with `x-api-key`; use `x-workspace-id` only when the key spans multiple workspaces. Keep credentials in environment variables, never in drafts or skill files.

## When to use

- Building a LinkedIn content calendar for OutFlo accounts
- Creating four or more unique profile variants from one source brief
- Preparing or publishing posts through OutFlo's posting API
- Checking whether hashtags, mentions, articles, or newsletters are supported
- Separating internal campaigns from client campaigns

## Required workflow

1. **Discover accounts.** Call `GET /accounts`; map stable local profile keys to returned `accountId` values. Never infer IDs from profile names.
2. **Check allowance.** Call `GET /usage` and `GET /entitlement`. Account for both consumed and reserved capacity.
3. **Build a source brief.** Record the source URL, factual proof, audience, campaign type, campaign key, angle, and candidate people. No source means no publishable draft.
4. **Generate variants.** Create a different hook, framing, proof selection, CTA, and first comment for every profile. Do not copy one body across accounts.
5. **Run QA.** Require 3-5 relevant hashtags, no em dashes, source URLs, truthful claims, 2-3 candidate people for manual review, and no fabricated stories or statistics. Candidate tags are metadata until structured mention support is verified.
6. **Create drafts.** Use `POST /posts` with `title`, `bodyText`, optional `firstCommentText`, and `editorialState: DRAFT`. Store the returned post ID and revision ID.
7. **Approve the exact revision.** Request approval, then approve or request changes. A content edit creates a new revision and requires approval again.
8. **Schedule.** For review-heavy work, prepare a publication intent with `accountId`, `revisionId`, `scheduledFor`, and `sourceTimezone`, verify the returned confirmation token, then commit it. Use `/publications/direct` only for trusted content that has already passed human approval.
9. **Poll delivery.** HTTP `202 Accepted` means queued, not published. Poll `GET /posts/{postId}` or `/calendar` until `SUCCEEDED`, `FAILED_RETRYABLE`, `FAILED_FINAL`, `REQUIRES_VERIFICATION`, or `CANCELED`.
10. **Audit.** Store account ID, post ID, revision ID, request/publication ID, schedule, state transitions, source URLs, approval record, and final result.

Completion means all four drafts have separate bodies, QA passes, account mappings are verified, allowance is checked, human approval exists, and final asynchronous state is recorded.

## Campaign model

Use `campaign_type: internal` or `campaign_type: client`, plus a unique `campaign_key`. Profile keys and account IDs are separate: a profile lane can be remapped without rewriting content history.

Initial internal lanes:

- `ai-integraterz-founder`: founder/operator lessons, AI integration, experiments, owned relationships.
- `affiliate-machine`: partner channels, referrals, attribution, owned audience for recruiting firms.
- `unreplaceable-recruiter`: specialist positioning, visibility, buyer trust, anti-generic recruiting.
- `recruit-assist`: capacity, desk operations, delegation, and throughput.

## Hashtags and people tags

Hashtags can be included as plain text in `bodyText`, so enforce 3-5 relevant tags and keep them natural. The verified OutFlo posting contract does not document a structured people-mention or LinkedIn URN field. Do not claim that `@Name` text creates a real tag. Store 2-3 candidate people with profile URLs for manual validation; only use structured tagging after an endpoint/schema test confirms it.

## Media attachments

The posting API supports media assets through `POST /assets/upload-intents`, followed by a direct `PUT` to the returned `uploadUrl` using the returned `requiredHeaders`, then `POST /assets/{assetId}/complete`. The completed asset IDs are included in the post/revision `assets` array. The current OutFlo posting client UI accepts images (`image/jpeg`, `image/png`, `image/gif`), one MP4 video (`video/mp4`), or one PDF, with up to nine images per post. Verify size/duration limits from the upload-intent response or current API contract before sending; do not guess limits. Upload and completion must succeed before the post is approved or scheduled, and media changes require approval of the resulting exact revision.

## Articles and newsletters

The verified posting resources cover posts, revisions, assets, comments, approvals, publication intents, accounts, usage, entitlement, and calendar. They do not establish a separate article or newsletter publishing endpoint. Prepare article/newsletter drafts in the local queue or a separately verified CMS integration. Never send long-form content to the post endpoint and call it a newsletter.

## Safety gates

- Default to draft creation, never direct publication.
- Never call `/publications/direct` without explicit human approval recorded against the exact body and account.
- Treat the API key as production publish authority.
- Do not invent tags, statistics, client results, or personal experiences.
- Do not schedule when account status or allowance is unknown.
- Preserve failed and held drafts; do not silently retry or duplicate.
- Use optimistic concurrency: `expectedVersion` or `If-Match` on updates.

## Local artifacts

Use `/opt/data/linkedin-content-system/`:

- `profiles.yaml` for profile lanes and API contract notes
- `content/briefs/` for source briefs
- `content/drafts/` for per-profile drafts
- `content/calendar/` for local schedule records
- `scripts/content_ops.py` for deterministic initialization, brief creation, expansion, and QA
- `scripts/outflo_posting.py` for safe API reads, draft creation, status checks, and explicitly gated direct scheduling
- `tests/` for local regression checks

## Verified API workflow and workspace mapping

The production posting API has been exercised successfully at `https://api.outflo.io/api/public/v1/posting` using the workspace-scoped `OUTFLO_API_KEY` environment variable. The API supports creating drafts, requesting and approving the exact revision, preparing a publication intent, committing it with OutFlo's confirmation token, and polling the calendar or post status. This was verified with 12 posts scheduled successfully across Ella Rapier, Jay Bell, and Johana Buitrago at `20:00` Asia/Manila. HTTP `202` plus `state: SCHEDULED` confirms the publication is queued, not yet delivered.

Verified account mappings:

- Ella Rapier: `[REDACTED]`
- Jay Bell: `909955c8-18c9-4810-a979-696f3295a82a`
- Johana Buitrago: `bc568c39-7214-4e99-a034-dac722294d71`
- Justin Bellware: `65f90157-86b8-4f41-8295-47ef0d2c4326`

Use `sourceTimezone: Asia/Manila` for Philippine-time schedules. Always re-check `GET /accounts`, `GET /usage`, and `GET /entitlement` before a new scheduling batch. Never store the API key in files. Do not use the legacy `live.outflo.in` outreach endpoints for content posting; use the canonical `api.outflo.io` posting API.

## Verification checklist

- [ ] `GET /accounts` returned and mapped all four intended profiles
- [ ] `GET /usage` and `/entitlement` checked
- [ ] Each draft has a source URL and campaign namespace
- [ ] Four bodies are materially distinct
- [ ] Every draft has 3-5 hashtags
- [ ] Candidate people are real and relevant; mentions are not claimed unless verified
- [ ] No em dashes or fabricated proof
- [ ] Exact revision approved
- [ ] Schedule uses ISO 8601 plus explicit source timezone
- [ ] Publication state was polled to a terminal or documented retry state
- [ ] IDs and state transitions were written to the audit log
- [ ] Article/newsletter requests were held unless a separate API was verified
