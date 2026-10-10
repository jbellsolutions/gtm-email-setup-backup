---
name: top-1-percent-copywriting
description: "Use when creating, critiquing, or researching direct-response copy and you need the Top 1% Copywriting archive's frameworks, styles, copywriter routing, swipe references, or Brian Kurtz/OverDeliver context. Retrieve task-relevant sources from the locally verified archive instead of loading the full corpus into context."
version: 1.0.0
author: Justin Bellware
license: Private research use only
metadata:
  hermes:
    tags: [copywriting, direct-response, swipes, overdeliver, brian-kurtz, copywriters]
    related_skills: [charm-offensive-foundation, charm-cold-email]
    source: https://github.com/jbellsolutions/top-1-percent-copywriting-archive/releases/tag/v1.0.0
---

# Top 1% Copywriting Archive

## Scope

This skill routes copywriting work through Justin Bellware's private v1.0.0 archive: Brian Kurtz's *OverDeliver* material and bonuses, the Ultimate Swipe File, classic direct-response sources, transcriptions, and copywriting resources. The source package declares 5,492,746,587 bytes across 2,322 files. It is a retrieval corpus, not a prompt to paste wholesale into one model context.

The archive contains third-party copyrighted works. Use it privately and only where authorized. Study principles, structures, and patterns. Do not reproduce or deploy another party's active campaign verbatim.

## Archive access and integrity

The canonical corpus remains in the GitHub release. For this user, the preferred architecture is remote retrieval, not a local mirror: do not download or extract the full archive to the Hermes server during normal use. A bounded remote retrieval MCP service is deployed locally at `/opt/data/tools/copywriting_retrieval_mcp/server.py` and configured in Hermes as `copywriting_retrieval`. It keeps no corpus copy locally. Use its `copywriting_search`, `copywriting_fetch`, `copywriting_context`, and `copywriting_status` tools to search the manifest and fetch bounded excerpts from the remote release. See `references/remote-retrieval-architecture.md`.

Never say the archive is "available," "ingested," or "done" merely because this skill or the MCP config exists. Verify the actual runtime path first: call `copywriting_status`, then perform a real `copywriting_search` and a bounded `copywriting_fetch` or `copywriting_context` test. Clearly distinguish these states in updates: skill installed, MCP service deployed, remote corpus reachable, and full corpus downloaded locally. If a service is only planned, say so directly and continue implementing it rather than summarizing a plan.

The user strongly prefers decisive execution and verified completion. Do not send the user back through unnecessary PAT setup when an existing OAuth connection or public release access is already available. Do not make a private copyrighted archive public as a workaround without explicit approval and a clear rights warning. If a remote connector cannot transfer or range-read release assets, implement or configure the retrieval layer instead of downloading the entire corpus.

A local archive root is optional for offline maintenance or explicit bulk-ingestion work: set `TOP_1_COPYWRITING_ARCHIVE` to the extracted archive directory. Before relying on it:

The archive's GitHub release can be accessed through the connected GitHub OAuth integration when available. Prefer that native OAuth connection over asking Justin for a personal access token. Local `gh` installation is not required for hosted-agent OAuth access.

Before downloading a large release, retrieve live release asset metadata and compare it against `PARTS.json`. A mismatch in reported bytes or checksums is a hard verification gate. Do not claim the corpus is downloaded or ingested until the actual assets and assembled archive pass verification.

For a multi-gigabyte release, perform a disk preflight before downloading or assembling: reserve space for the compressed parts, the assembled ZIP, extraction, and temporary indexes. Do not start an assembly operation unless free space covers the ZIP in addition to the already-downloaded parts. If the release is public, use direct release URLs; if private, use the connected GitHub OAuth integration when it supports binary transfer. Metadata-only OAuth access is not sufficient to claim local availability. Never ask the user to expose a private copyrighted archive publicly merely to work around a connector limitation without clearly flagging the privacy and rights tradeoff.

1. Confirm the release is v1.0.0.
2. Confirm the reconstructed ZIP matches the release SHA-256: `3fd50a303bb122b40f559ff45b0d6f2e095c9d1dd3d487c49e8ec654ad894111`.
3. Run `unzip -tq` on the ZIP.
4. Read `README.md`, `NOTICE.md`, `KNOWN_LIMITATIONS.md`, `AGENT-QUICKSTART.md`, and this skill.
5. Search `MANIFEST.tsv` and `07_Copywriting_Resources/` before opening large trees.

Do not claim the corpus is fully available unless all three release parts are present, their byte sizes and SHA-256 values match `PARTS.json`, the assembled ZIP hash matches, and the ZIP test passes.

## Retrieval workflow

For each writing task, select:

1. One primary framework or voice source.
2. One supporting swipe or transcript set.
3. One proof/reference source where factual claims matter.

Search paths and text first. Load only relevant excerpts. Record the local paths consulted in working notes, not in the user-facing copy unless requested.

Useful searches:

```bash
rg -i 'bencivenga|bullets|headline' "$TOP_1_COPYWRITING_ARCHIVE/MANIFEST.tsv"
rg -i --glob '*.txt' --glob '*.md' 'market sophistication|levels of awareness' "$TOP_1_COPYWRITING_ARCHIVE"
rg -i 'transcript|transcription' "$TOP_1_COPYWRITING_ARCHIVE/MANIFEST.tsv"
```

## Canonical reading order

1. `01_OverDeliver_Book/extracted_pdf_text/` — the seven high-signal bonus PDFs.
2. `01_OverDeliver_Book/combined/overdeliver_official_bonus_pdf_text_combined.txt` — cross-bonus search.
3. `01_OverDeliver_Book/transcripts_audio/session-XX-transcript-pdf.txt` — the 12 sessions. Sessions 1–4 cover philosophy, ethics, and the four pillars; sessions 5–12 cover tactics, lists, copy, monetization, and backend.
4. `03_Brian_Kurtz/ceo-brian-kurtz-agent/AGENTS.md` — Kurtz persona and voice.
5. `04_Ultimate_Swipe_File/SWIPE_FILE_CONTEXT.md` — master swipe map.
6. A relevant `05_Other_Swipe_Files/Brenn_*/` collection.

## Task routing

| Task | Start here |
|---|---|
| Long-form sales letter | `04_Ultimate_Swipe_File/codex/` plus the Lost Chapters text |
| VSL | OverDeliver session 7 plus `04_Ultimate_Swipe_File/swipe-file-content/` |
| Short advertorial or Facebook ad | `04_Ultimate_Swipe_File/swipe-file/` plus Dan Kennedy material |
| Email sequence | `04_Ultimate_Swipe_File/swipe-file-content/brian_kurtz/` plus the AI Newsletter Swipe CSV |
| Bullet stack | `02_OverDeliver_Bonuses/extracted_text/bencivenga-bullets-pdf.txt` |
| Headline | Jay Abraham material plus the Ultimate Swipe research tree |
| Lead/opening | Ultimate Swipe content plus Breakthrough Advertising Lost Interviews |
| CTA/close | Jay Abraham's *How to Get From Where You Are to Where You Want to Be* plus close variations in the 12-session set |
| Lead magnet/free report | *Confessions of a Direct Mail Guy* plus *Secrets of Successful Direct Mail* |

## Voice and style index

- **Brian Kurtz:** evidence-obsessed, ethical, conversational, mid-form, truth-first. Use for skeptical prospects and ethical-bridge copy.
- **Gary Halbert:** urgent, direct, contrarian, high-energy, classical direct response. Use for front-end offers and list-mailing promotions.
- **Gary Bencivenga:** restrained, proof-driven, bullet-led, every word earned. Use for skeptical health and financial offers and bullet stacks.
- **Dan Kennedy:** no-BS, practical, system-builder, anti-fluff. Use for B2B, info-products, and high-ticket consulting.
- **Jay Abraham:** strategic, calm authority, preeminence, 80/20, ethics of the deal. Use for strategy, positioning, and JV copy.
- **Eugene Schwartz:** levels of awareness, mass desire, market sophistication. Use as the strategic diagnosis before drafting.
- **Joseph Sugarman:** slippery-slide, image-driven, psychological triggers, soft-sell narrative. Use for continuity and story-led B2C offers.
- **David Ogilvy:** fact-based, respectful, headline-led, specific. Use for brand-level and advertorial copy.
- **Perry Marshall:** engineering-flavored, systems-thinking, ROI-defensible. Use for technical B2B and marketing-to-engineers.

Do not blend voices by accident. If the user names a copywriter, retrieve that writer's sources and identify the distinguishing mechanisms before drafting. If no voice is requested, choose based on offer, audience sophistication, format, and desired emotional temperature, and state the selected framework internally.

## Drafting rules

- Diagnose audience awareness, market sophistication, desire, mechanism, proof, offer, and risk reversal before writing.
- Apply the selected writer's principles without impersonating or copying living writers verbatim.
- Synthesize new copy. Never paste an archive campaign unchanged.
- Preserve evidence, specificity, and ethical claims. Do not invent proof, testimonials, results, scarcity, or guarantees.
- For direct-response work, produce a clear structure: promise, mechanism, proof, objections, offer, risk reversal, CTA, and next action where appropriate.
- For critique, identify the current mechanism, missing proof, awareness mismatch, and the highest-leverage revision.

## Known archive distinctions

- `01_OverDeliver_Book/` is session-organized book content; `02_OverDeliver_Bonuses/` is bonus-organized content. They overlap but are not interchangeable.
- The Ultimate Swipe File has distinct `codex/`, `swipe-file/`, `swipe-file-content/`, `swipe-file-research/`, and `web_swipe_file/` lenses.
- Prefer one Brenn collection consistently when using the duplicated Jay Abraham sessions.
- `codex/jon_buchan/` is London/UK/EU copy and should not be confused with US direct response.

## Verification checklist

- [ ] Archive root exists and is readable.
- [ ] Release parts and assembled ZIP are complete and cryptographically verified.
- [ ] Relevant source paths were searched before drafting.
- [ ] One primary framework, one supporting swipe set, and one proof source were selected.
- [ ] New copy is original and claims are supported.
- [ ] The requested format, audience, offer, CTA, and voice were followed.
