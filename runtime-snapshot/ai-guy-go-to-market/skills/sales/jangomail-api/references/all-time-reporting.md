# JangoMail all-time reporting reference

## Retrieval

1. Load `JANGOMAIL_USERNAME` and `JANGOMAIL_PASSWORD` from the environment, never hardcode credentials.
2. `GET https://api-v2.jangomail.com/campaigns` with Basic Auth.
3. Exclude campaigns with `recipients == 0` from sent totals. These are drafts or failed/no-send records.
4. For each included campaign, use the stats fields from the response or refresh `GET /campaigns/{campaign_id}/stats`.

## Calculations

- `delivered = recipients - bounces - blocks`
- `open_rate = opens / delivered * 100`
- `click_rate = clicks / delivered * 100`
- Never include `removed_addresses` in either sent or delivered. They were suppressed pre-send.
- Sum counts first, then calculate subtotal/grand-total percentages from subtotal delivered, not by averaging campaign rates.

## Grouping

Use operational batch labels supplied by the user, such as SET 1, SET 2, diagnostics, SET 3b, and SET 4. Map subjects to newsletter names separately:

- FDA Panel subjects → The Protocol
- AI Firms subjects → People Person
- Long Tail subjects → Green Room
- Testosterone subjects → Men's Health

Keep one-recipient tracking/link diagnostics in a distinct diagnostic section. Include campaign IDs in the detailed table so the report can be audited.

## Presentation

Use clean tables with: batch, campaign/newsletter, campaign ID, sent, delivered, opens/count + %, clicks/count + %, bounces, unsubs, complaints. Include subtotals per batch and a grand total. If blocks materially affect delivery, state the delivery formula and optionally show blocks in a note or supplemental column.

## ListMonk/Bird reconciliation

ListMonk may show campaign-level sent/delivery counters that differ from Bird's transport-level results. For Bird SMTP campaigns, use Bird for accepted/delivered/bounced transport counts and ListMonk for native opens/clicks when Bird tracking is disabled. State the source of each metric and do not silently present ListMonk's `sent / total` as delivered if Bird reports a bounce.
