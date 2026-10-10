---
name: shared-calendar-access-verification
description: "Use when locating events on a shared Google calendar."
version: 1.0.0
---

# Shared Calendar Access Verification

Use this workflow when a user asks for events from a named calendar shared to an email address, especially when the calendar is not necessarily the authenticated account's primary calendar.

## Workflow

1. **Verify the active Google connection** before searching. Record the authenticated identity if the integration exposes it; do not infer the identity from the requester's email address.
2. **Enumerate visible calendars** using the calendar-list endpoint. Capture each calendar's ID, display name, and access role.
3. **Resolve the target calendar** by matching both display name and calendar ID. A user-facing name such as “Justin Bellware” is not itself a safe API calendar ID.
4. **Search only after resolution** using timezone-aware ISO 8601 boundaries. Make the start inclusive and set the end beyond the current instant. Use both event query terms and, when needed, a bounded full-calendar listing followed by local filtering for names, companies, and participants.
5. **If the target is absent**, do not claim that the target calendar was searched. Report the visible calendar list, the date range checked, and the exact search terms used on any accessible fallback calendar. State that the invitation may target another Google identity or may not have been accepted/propagated, and request identity/invitation verification.
6. **Keep the result concise and evidence-based**: requested event dates first, then limitations and one concrete next step.

## Common Pitfalls

- Do not substitute a similarly named calendar or the primary calendar without saying so.
- Do not treat an empty event query as proof that the target calendar has no events when the target calendar is not visible.
- Do not guess calendar IDs from display names or email addresses.
- Shared-calendar visibility and event visibility are separate checks: an account can be authenticated successfully while lacking access to the requested calendar.

## References

- `references/shared-calendar-checklist.md` — concise evidence checklist and reporting template for shared-calendar investigations.
