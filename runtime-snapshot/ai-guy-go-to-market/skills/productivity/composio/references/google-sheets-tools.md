# Google Sheets Tools (Composio MCP)

Full tool schemas discovered via `COMPOSIO_SEARCH_TOOLS` on July 20, 2026. Connected account: `justin@usingaitoscale.com`.

## GOOGLESHEETS_CREATE_GOOGLE_SHEET1

Creates a new Google Spreadsheet.

```json
{
  "title": "My Spreadsheet",
  "folder_id": "optional-drive-folder-id",
  "folder_name": "optional-folder-name"
}
```

Returns: `{"display_url": "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit", "properties": {...}}`

## GOOGLESHEETS_VALUES_UPDATE

Write values to a range. **This is the primary tool for populating sheets.**

Required fields:
- `spreadsheet_id` — from URL
- `range` — A1 notation, e.g. "Sheet1!A1:S200"
- `values` — 2D array `[["Name","Email",...], ["Alice","alice@...",...]]`
- `value_input_option` — "USER_ENTERED" (parses formulas/numbers) or "RAW" (strings only)

Optional:
- `auto_expand_sheet` — default true; expands grid beyond 1000 rows / 26 columns
- `major_dimension` — "ROWS" (default) or "COLUMNS"

Returns: `{"updatedRange": "...", "updatedRows": N, "updatedCells": N}`

**Pitfall:** values must be rectangular (all rows same length). NaN/Infinity values fail with "Out of range float values are not JSON compliant."

## GOOGLESHEETS_ADD_SHEET

Add a new worksheet tab.

```json
{
  "spreadsheet_id": "...",
  "title": "Tab Name"
}
```

**Pitfall:** Writes immediately after tab creation can fail with "sheet-not-found." Re-check titles via `GOOGLESHEETS_GET_SHEET_NAMES` then retry.

## GOOGLESHEETS_GET_SHEET_NAMES

List all worksheet names.

```json
{
  "spreadsheet_id": "...",
  "exclude_hidden": false
}
```

Returns: `{"sheet_names": ["Sheet1", "Coaching", "HVAC"], ...}`

**Pitfall:** May return 429 (rate limit). Retry with backoff.

## GOOGLESHEETS_GET_SPREADSHEET_INFO

Get spreadsheet metadata without grid data.

```json
{
  "spreadsheet_id": "..."
}
```

## GOOGLESHEETS_VALUES_GET

Read values from a range.

```json
{
  "spreadsheet_id": "...",
  "range": "Sheet1!A1:D10"
}
```

## GOOGLESHEETS_UPDATE_VALUES_BATCH

Write to multiple non-contiguous ranges in one API call.

## GOOGLESHEETS_SPREADSHEETS_VALUES_BATCH_CLEAR

Clear ranges before overwriting.

## Rate Limits

- 60 reads/minute
- 60 writes/minute
- 10M cell limit per spreadsheet

Exceeding limits causes 429 errors. Batch operations through MULTI_EXECUTE to minimize calls.

## Typical Workflow

1. `COMPOSIO_SEARCH_TOOLS` → find tools for "google sheets create spreadsheet write"
2. `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` → get `spreadsheet_id`
3. `GOOGLESHEETS_ADD_SHEET` × N → create tabs
4. `GOOGLESHEETS_GET_SHEET_NAMES` → verify tab names (use exact titles in ranges)
5. `GOOGLESHEETS_VALUES_UPDATE` × N → populate each tab with `value_input_option: "USER_ENTERED"`
6. `GOOGLESHEETS_VALUES_GET` → spot-check a small region

All steps 2-6 can be batched through `COMPOSIO_MULTI_EXECUTE_TOOL`.