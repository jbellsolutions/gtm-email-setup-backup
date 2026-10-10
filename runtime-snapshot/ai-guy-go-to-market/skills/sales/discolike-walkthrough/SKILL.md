---
name: discolike-walkthrough
description: Interactive DiscoLike teaching mode. Use when the user wants to learn the platform, master the filter grammar, build confidence before spending money, or says things like "walk me through it", "teach me", "show me how this works", "I want to master this". Uses ONLY free MCP tools — counts, match-contacts, saved-query CRUD. No money spent, ever.
---

# DiscoLike — Walkthrough

Master the platform on the user's OWN queries using only FREE tools. Goal: build the count-before-pull reflex.

## Hard Rule

**Do not call any paid tool.** No `run-discogen`, no `discover-similar-companies`, no `business-profile`, nothing paid. Only tools from the FREE cost class.

## Sequence

### 1. Get the target from the user
Ask plainly: "What's a target ICP you actually care about?"

Suggested starters:
- "merchant cash advance brokers, US small"
- "virtual-assistant agencies in the Philippines"
- "content creators / influencers in <niche>"

### 2. Draft initial filters together (no tool call yet)
Talk through what fields you'd set:
- `phrase_match` — what's the keyword shape? Explain bare-OR vs `+forced-AND` distinction
- `country` / `state` — narrow the geography
- `employee_range` or `min_digital_footprint` / `max_digital_footprint` — what size company
- `category` — any obvious industry constraint
- `tech_stack` — does the ideal customer use a specific tool?

Digital footprint (0-800) is DiscoLike's proxy for company size — derived from SSL cert issuance volume + age. Lower the max to find smaller players.

### 3. Run the first count (FREE)
```
mcp__discolike__count-matching-domains
  phrase_match: <draft>
  country: <draft>
  ...
```
Show the number. Explain whether it's too big (loose filters), too small (over-constrained), or in the sweet spot (typically 1K-50K for a real campaign).

### 4. Tighten and re-count — multiple times
This is the LEARNING. Each adjustment teaches one filter:
- Add `+keyword` to `phrase_match` → user watches the number shrink
- Drop `max_digital_footprint` from 800 to 400 → user watches big-company noise drop
- Add `negate_category` → user sees how exclusions work
- Add a `tech_stack` constraint → user sees the SaaS-detection power

Each count is FREE. Run as many as they want.

### 5. Demonstrate free contact lookup
Pick any one company from a count result. Run:
```
mcp__discolike__match-contacts
  name: "<a common name like 'Sarah'>"
  company_name: "<that company>"
```
Show that contact text-matching is always free.

### 6. Save the query (FREE)
```
mcp__discolike__save-mcp-query
  query_name: "<descriptive>"
  ... (include the full filter set)
```
Now it's persisted with a `query_id`. Tag it:
```
mcp__discolike__add-tags-to-query
  query_id: <id>
  tags: ["walkthrough", "<topic>"]
```

### 7. Hand off
Tell the user:
- They've designed a real query, spent $0, and learned the filter grammar by watching counts move.
- Next: `discolike-design` for deeper architect-driven refinement, or `discolike-validate` to spend ~$1 confirming fit % before any real pull.

## What good looks like
By the end the user can answer:
- What's the difference between bare keywords and `+forced` keywords?
- Why use `digital_footprint` instead of `employee_range`?
- What's the cheapest way to check if a contact exists?
- Where do my saved queries live?
- What will it cost to actually pull this list?