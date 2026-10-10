---
name: standalone-html-redesign
description: "Use when redesigning standalone HTML artifacts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [html, css, ui, ux, redesign, verification]
    related_skills: [claude-design, popular-web-designs, dogfood]
---

# Standalone HTML Redesign

## Overview

Use this workflow when a user provides a self-contained HTML document and asks for a stronger visual direction or alternate version. Produce a complete, openable artifact, not a mockup description. Preserve substantive content and working interactions unless content changes are explicitly requested.

## When to Use

- Redesign an existing checklist, dashboard, playbook, or prototype in standalone HTML.
- Produce a polished version while keeping the original intact.
- Transform dense content into a more usable operating surface.

## Workflow

### 1. Establish the surface

Name the primary surface before choosing colors or decoration. Checklists and playbooks are usually **Operate** or **Monitor** surfaces: action affordances, progress, phase state, and next actions should dominate. Do not default to a marketing hero-plus-card grid.

Completion criterion: the composition can be described in one sentence and every major region supports that surface.

### 2. Read and model the source

Read the complete supplied HTML. Identify headings, repeated content units, stateful controls, persistence behavior, warnings, gates, exclusions, gaps, responsive rules, and accessibility needs. Prefer structured extraction or a DOM parser over broad regexes. Broad patterns can capture attributes and leak strings such as `class="...">` into visible output or accessible labels.

Record source counts for major units before generating the redesign, such as phase count, checklist-item count, and gap count.

### 3. Design the system

Choose a restrained visual language: one primary accent, a small semantic palette, deliberate display/body typography, consistent spacing/radii, clear state colors, visible focus, and mobile hit targets of at least 44px. Use CSS variables and embedded CSS/JS. Avoid decorative gradients, arbitrary metrics, icon toppers, and filler sections.

### 4. Preserve behavior

Keep checklist state persistent, make labels clickable, update progress and per-phase counts immediately, and provide a safe reset. Add search, filters, phase navigation, or a next-action panel only when they reduce friction. Use a new namespaced localStorage key for a new version.

### 5. Generate safely

Keep extraction/build scripts separate from the final HTML. JSON-serialize extracted data when embedding it into JavaScript and protect closing script sequences when needed. Never leave placeholder tokens such as `__DATA__`. Preserve the original and use a versioned output name.

### 6. Verify beyond appearance

1. Confirm the output exists and is non-empty.
2. Compare source/output counts for phases, checklist items, and gaps.
3. Search for placeholder tokens and parser leakage (`class=`, `input...>` or similar accidental text).
4. Open in a browser and inspect headings, labels, buttons, and readable checklist text in the accessibility snapshot.
5. Check console output after navigation and meaningful interactions.
6. Toggle a checkbox and confirm completed count/progress changes.
7. Exercise disclosure/navigation, search/filter, and reset.
8. Inspect desktop and narrow/mobile layouts when tooling permits.

Completion criterion: all checks pass, or every limitation is explicitly reported.

## Common Pitfalls

1. **Regex captures attributes as content.** Split item attributes from inner HTML or use a DOM parser, then inspect accessible names.
2. **Content gets dropped.** Treat the source as a content contract and compare counts.
3. **A polished screen hides broken state.** Test a real checkbox, persistence, and reset.
4. **The source gets overwritten.** Preserve it and write a versioned artifact.
5. **Extracted data breaks JavaScript.** Serialize it safely.
6. **Visual novelty harms operations.** Keep phase state and controls scannable.
7. **No mobile strategy.** Reflow navigation, controls, score panels, and phase content.

## Verification Checklist

- [ ] Surface named and reflected in composition
- [ ] Source content read completely
- [ ] Source/output counts compared
- [ ] Original preserved and output versioned
- [ ] No placeholder tokens or leaked parser markup
- [ ] Accessible headings and checklist labels verified
- [ ] Checkbox updates counts/progress and persists
- [ ] Disclosure/navigation works
- [ ] Search/filter and reset work
- [ ] Console checked after navigation and interaction
- [ ] Desktop/mobile layouts inspected when possible
- [ ] Final response gives exact path and honest verification status
