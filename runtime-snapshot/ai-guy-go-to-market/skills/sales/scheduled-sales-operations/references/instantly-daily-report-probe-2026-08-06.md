# Instantly daily report probe — 2026-08-06

## Live response observations

- `GET /campaigns`: HTTP 200; payload under `data.items`, with `next_starting_after`.
- `GET /campaigns/analytics`: HTTP 200; payload under `data` as a list. It included cumulative campaign fields: `emails_sent_count`, `reply_count_unique`, `bounced_count`, `unsubscribed_count`, and `total_opportunities`.
- `GET /accounts`: HTTP 200; payload under `data.items`, with `next_starting_after`. Account records exposed `status`, `warmup_status`, `stat_warmup_score`, `setup_pending`, and `daily_limit`.
- `GET /emails?i_status=1`: HTTP 200; payload under `data.items`; it may include both sent (`ue_type: 1`) and inbound (`ue_type: 2`) records.
- Email bodies are objects with `text` and `html`. Inbound records expose `id`, `timestamp_email`, `from_address_email`, `campaign_id`, `thread_id`, `subject`, and `is_unread`.

## Reliable report logic

1. Fetch campaigns, analytics, accounts, unread emails, and a bounded all-email snapshot separately.
2. Validate each response before parsing. On retries, deduplicate by email `id`.
3. Count inbound activity only after filtering `ue_type == 2`; never classify sent records returned by the unread endpoint.
4. Use `body.text` first, then `body.html`; strip Gmail/Outlook/Apple quoted content before applying positive-reply rules.
5. Classify only the earliest genuine lead reply in a thread. A body such as “Yes, please” is `positive_interested` after quote stripping; quoted cold-email copy must not influence the label.
6. Treat daemon state as processing/dedup evidence, not delivery evidence. Confirm an operator reply with a distinct SENT message in the same `thread_id` after the inbound timestamp.
7. If a current-day total comes from a bounded email page rather than a provider date-filtered metric, label it as observed, not exact. Keep cumulative analytics in a separate column/section.

## Failure pattern to avoid

A paginated request can intermittently return an error-shaped or incomplete object. If the parser converts that response to an empty list and continues, a later report can show impossible swings (for example, zero email rows after a previous successful 100-row page). Abort that metric, preserve the last successful snapshot, and report scope/uncertainty rather than emitting zeroes.
