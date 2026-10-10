# Cron Dashboard Session Reference

## Reusable pattern

For a cron inventory dashboard, read the authoritative current export (for this session, `/opt/data/cron/jobs.json`) rather than manually reconstructing records from a prior chat response. Preserve all 24 stable IDs, current state, schedule, delivery target, status, skills, and raw prompt text.

Translate each prompt into a detailed plain-language description covering purpose, cadence, inputs, processing, outputs, destinations, safeguards, and limitations. For blank name/prompt records, use an explicit unidentified label and state that the purpose is not inferable from current configuration.

## Verification checklist

- Parse source JSON and assert the expected record count.
- Embed the source records into the HTML and compare stable-ID sets.
- Assert counts by state and count records with blank names/prompts.
- Assert every record has a detailed description or explicit unknown explanation.
- Run `node --check` on the extracted JavaScript.
- Open the file with the browser and inspect title, search, state/cadence filters, enabled/paused grouping, detailed cards, expandable raw context, and visible totals.
- Send the resulting absolute path using the platform's native attachment syntax.

## Important correction

The first dashboard used a manually typed list and short descriptions. When the user said the descriptions were too brief, the reliable fix was to rebuild from the current JSON source and generate descriptions from each live prompt, not to pad the old prose. Historical backup entries can be useful context but must not override current blank or changed fields.
