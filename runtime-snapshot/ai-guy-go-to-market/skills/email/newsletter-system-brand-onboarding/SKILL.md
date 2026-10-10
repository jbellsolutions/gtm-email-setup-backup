---
name: newsletter-system-brand-onboarding
description: Use when handling newsletter brand onboarding from the canonical Obsidian workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, obsidian, bridge]
    related_skills: [newsletter-documentation-installs]
---

# Brand Onboarding Skill Bridge

## Canonical source

The authoritative workflow is maintained in the Obsidian vault at:

`/opt/data/obsidian-vault/Newsletters/00 - Newsletter System/skills/Brand Onboarding Skill.md`

This Hermes skill is an execution bridge, not a duplicate of that workflow. The Obsidian file is the single source of truth. Do not reconstruct, summarize, or override it from memory.

## Required behavior

1. Read the canonical Obsidian file above before acting.
2. Read `/opt/data/obsidian-vault/Newsletters/00 - Newsletter System/00 - System Hub.md` and `/opt/data/obsidian-vault/Newsletters/00 - Newsletter System/doctrine/01 - Read Before Write.md` when the canonical workflow directs you to do so.
3. Follow the canonical file’s read order, authority paths, gates, and completion criteria exactly.
4. Re-read any publication authority file named by the workflow before using its values.
5. Treat changes in the Obsidian file as authoritative on the next tool call; never use stale copied instructions.
6. If a required file is missing, a gate fails, or the workflow is ambiguous, stop and report the blocker rather than guessing.
7. Never send, schedule, publish, or test-send email. Never generate images; prompts only where authorized.

## Fresh-session note

Hermes may cache a loaded skill during a conversation. After changing the canonical Obsidian file, start a new Hermes session or reset the session before relying on changed workflow text. The validator can detect missing files and stale bridge references, but it cannot reload an already-running model context.

## Verification checklist

- [ ] Canonical Obsidian file was read before action.
- [ ] Authority files named by it were read before using their values.
- [ ] No copied workflow content was added to this bridge.
- [ ] All applicable gates passed or blockers were reported.
- [ ] No send, schedule, publish, test-send, or image-generation action occurred.

---
Tags: [[newsletter]] [[newsletter-system]] [[obsidian]] [[bridge-skill]]
