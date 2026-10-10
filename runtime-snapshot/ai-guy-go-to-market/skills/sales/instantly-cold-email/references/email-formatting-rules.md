# Email Formatting Rules — Non-Negotiable

These rules apply to EVERY cold email sequence saved to Instantly. If formatting is wrong, emails will not land.

## The Format

Every email body must use **short lines with blank lines between every thought**. Never a block of text.

```
Hey {{first_name}},

saw {{company_name}} does fractional CFO work.

you build clients a thirteen week cash forecast and hold them to it.

your own pipeline?

whoever happens to call.

because client work eats the week.

i build the referral channel itself.

worth 20 minutes?

reply and i'll send the case study of another fractional CFO we ran this exact strategy for.

in-house or with us. yours either way.

justin
```

## The Rules

1. **Every sentence (or very short pair of sentences) on its own line.** No exceptions.
2. **Blank line (`\n\n`) between every paragraph/thought unit.** Not optional.
3. **Lowercase throughout.** Subject lines, body, everything. Never capital letters to start sentences.
4. **No greeting filler.** Never "I hope this finds you well" / "I wanted to reach out" / "I'd love to".
5. **Vary sentence length.** Long one, then a short one. Then a fragment. Never three same-length lines.
6. **No em-dashes.** Zero. Anywhere. Not in subject, not in body, not in follow-ups.
7. **No blocks of text.** If 3+ lines run together without a blank line, it's wrong.
8. **No AI footprint.** No parallel lists, no symmetrical rhythm, no "furthermore/moreover/delve/landscape/robust".
9. **No exclamation marks.** Ever.
10. **Sign-off on its own line.** `justin` alone, preceded by a blank line.

## Saving to Instantly

The `save-sequence` JSON must use `\n\n` between lines. When writing JSON files for CLI, use actual newlines in the `email_body` string value:

```json
{
  "sequences": [{
    "seq_number": 1,
    "seq_delay_details": {"delay_in_days": 0},
    "seq_variants": [{
      "subject": "your pipeline",
      "email_body": "Hey {{first_name}},\n\nsaw {{company_name}} runs fractional CFO engagements.\n\nyou build clients a forecast.\n\nworth 20 minutes?\n\njustin",
      "variant_label": "A"
    }]
  }]
}
```

## Verification

After saving, use `Instantly campaigns get-sequence --id <ID>` to verify. The output should show `\\n\\n` in the JSON repr — that means actual newline characters are stored. The email body should have 10-20 lines with roughly half being blank lines.

## What NOT To Do

❌ Block of text: `"Hey {{first_name}}, saw {{company_name}} does CFO work. You build clients a forecast and hold them to it while your own pipeline runs on whoever happens to call because client work eats the week. I build the referral channel..."`

✅ Proper format: Each thought on its own line, blank lines between.
