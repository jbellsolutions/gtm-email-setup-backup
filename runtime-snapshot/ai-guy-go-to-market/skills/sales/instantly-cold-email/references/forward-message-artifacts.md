# FORWARD Message Artifacts in Instantly History

**When to watch for this:** Any time you're scanning `leads messages` history for unprocessed replies.

## The Problem

When a human operator forwards a lead's reply to someone else (e.g., a colleague), Instantly creates a **FORWARD-type message entry** in the lead's message history. This FORWARD:

- Has the **same body content** as the original REPLY
- Has a **different message ID** from the original REPLY
- Is a **system artifact**, not a new human reply

## Consequences

- Ad-hoc sweep scripts that match on any message with a non-empty body (rather than filtering strictly by `type == "REPLY"`) will flag these as "unprocessed"
- The FORWARD's message ID won't be in the state file, causing re-detection on every subsequent scan
- Can create false positives in monitoring reports if not filtered

## Detection Pattern

```python
# WRONG — catches FORWARD artifacts:
if mtype in ('REPLY', 'FORWARD') or body.strip():
    latest_reply = m

# RIGHT — only processes actual human replies:
if mtype == 'REPLY' and 'mailer-daemon' not in sender.lower():
    latest_reply = m
```

## State File Handling

When a FORWARD artifact is discovered, add its message ID to `replied_message_ids` in `auto_reply_state.json` to suppress future re-detection. Do NOT generate a draft or report it as a new reply.

## Confirmed Instance

**July 9, 2026 — Mike Billoni (mike@billoni.com), campaign #3577260:**
- Original REPLY: `DM4PR19MB78822FC5F4868B077B15561DDCFE2@DM4PR19MB7882.namprd19.prod.outlook.com` — "Yes. Call me at 716.578.8948" — already in state, operator already replied
- FORWARD artifact: `<3d0a2417-b620-slf50-4d87-9072-aad33b706734-fjscz9f@advanceaxisnm.info>` — same content, different msg_id — added to state to suppress