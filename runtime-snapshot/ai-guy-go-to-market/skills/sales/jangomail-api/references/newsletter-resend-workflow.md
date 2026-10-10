# Newsletter Resend Workflow — Reuse Prior Campaign HTML to New List

When the user wants to resend a newsletter (same content, possibly minor edits like date change) to a new list of leads, follow this exact sequence:

## 1. Pull Prior Campaign HTML

```
jango('GetCampaignDetails_XML', JobId='<prior_campaign_id>', Options='')
```

Parse the XML response for `<HTMLMessage>` and `<PlainTextMessage>` elements. These contain the full email content (HTML-entity-escaped — unescape with `html.unescape()`).

## 2. Make Edits

Common edits: byline date, issue number, minor copy tweaks. Always verify with a count check:

```python
old_date = "Thursday, July 23, 2026"
new_date = "Monday, July 27, 2026"
assert html_content.count(old_date) == 0  # after replace
assert html_content.count(new_date) >= 1
```

Check BOTH HTML and plain text — the date/byline appears in both.

## 3. Create New List + Import CSV

```python
# Create group
jango('AddGroup', GroupName='pr-agencies-MONDAY-250')
# Returns: "0\nSUCCESS\n{GroupID}"

# Import CSV (field name MUST be "EmailAddress", not "Email")
jango('ImportGroupMembersFromData',
    GroupName='pr-agencies-MONDAY-250',
    FieldNames='EmailAddress,FirstName,LastName,CompanyName',
    ImportData=import_data,  # newline-separated, comma-delimited, quote fields with commas
    ColumnDelimiter=',',
    RowDelimiter='\n',
    TextQualifier='"')
```

**Wait 10-15 seconds** for async import to settle, then verify:

```python
jango('GetGroupMemberCount', GroupName='pr-agencies-MONDAY-250')
# Must return exactly the expected count (e.g., 250)
```

Cross-check via v2: `GET /lists` — find the list by name, check `member_count`.

## 4. Send via v1 SendMassEmail (NOT v2 PUT /campaigns/{id}/send)

Per skill pitfalls, v2 campaign-to-list sending is unreliable. Use v1:

```python
jango('SendMassEmail',
    FromEmail='email@scaleverticalwithai.com',
    FromName='Scale Vertical AI',
    ToGroups='pr-agencies-MONDAY-250',
    ToGroupFilter='',      # REQUIRED — pass empty string
    ToOther='',            # REQUIRED — pass empty string
    ToWebDatabase='',      # REQUIRED — pass empty string
    Subject='🎙️ The Long Tail Belongs On Your Media List',
    MessagePlain=plain_content,
    MessageHTML=html_content,
    Options='TrackOpens,TrackClicks')
# Returns: "0\nSUCCESS\n{JobID}"
```

## 5. Verify Send

```python
# v1 status
jango('GetMassEmailStatus', JobID='<new_job_id>')
# Should return "Sending" or "Complete"

# v2 stats (recipient count confirmation)
GET /campaigns/{new_job_id}/stats
# recipients should match group member count (minus suppression removes)
```

## 6. Schedule +2hr Stats Report

Create a one-shot cron job scheduled 2 hours after send time to pull and report bounces/opens/complaints. Deliver back to the originating channel.

## Common Pitfalls

- **v2 `GET /campaigns` includes draft campaigns** created with `create_only: true`. These show `recipients: 0` and status `Preprocessing`. They were never sent. Don't confuse them with actual sent campaigns — the sent one has a higher campaign_id and `recipients > 0`.
- **Suppression removes**: If some list members were previously unsubscribed/hard-bounced on other campaigns, they'll show as `removed_addresses` and won't be in the `recipients` count. `recipients` = group count minus suppressions. Delivered = recipients minus bounces minus blocks.
- **CSV field name**: Must be `EmailAddress` (not `Email`) or import fails with `InvalidGroupFieldsException`.
- **`***uniqueid****` in HTML**: Leave these placeholders intact — JangoMail replaces them per-recipient at send time for unsubscribe/view-online links. Do not touch them when editing HTML.