# Session Search Query Playbook

Use the report date in both ISO and compact forms. Run independent searches because a date may appear in timestamps, tool arguments, or prose rather than in the same message.

## Query set

1. `"YYYY-MM-DD" OR YYYYMMDD`
2. `YYYYMMDD skill_manage OR skill_created OR skill_updated OR skill_patched`
3. `YYYYMMDD memory add OR memory replace`
4. `YYYYMMDD lesson OR workaround OR bug OR fix OR patch OR workflow OR solved OR discovered`

## Evidence handling

- Discovery results provide candidate sessions and real `match_message_id` values.
- Scroll only with a message ID returned by discovery or a prior scroll window.
- Include `tool` role messages when operation names or exact write results are absent from prose.
- Deduplicate repeated evidence from the same event and favor the final tool result.
- Record failed or rejected operations as lessons/attempts, not successful state changes.

## Report shape

The vault report must have exactly these top-level sections: `Skills`, `Memories`, and `Lessons Learned`. The delivery message is an index, not a second copy of the report.
