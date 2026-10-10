# JangoMail Newsletter Send Workflow

End-to-end sequence for sending a newsletter issue to a verified list via JangoMail v1 API.

## Prerequisites

- JangoMail account (UsingAIToScale / Jango123!)
- Sending domain: `scaleverticalwithai.com` (SPF + DKIM configured)
- Tracking domain: `track.scaleverticalwithai.com`
- Newsletter HTML built, images uploaded to JangoMail CDN
- Recipient CSV verified (lead_status=COMPLETED in Instantly or equivalent)

## Send Sequence

### 1. Upload Recipient List

```python
# Create group
jango('AddGroup', GroupName='list-name-250')
# → "0\nSUCCESS\n{GroupID}"

# Import CSV (field name MUST be "EmailAddress", not "Email")
jango('ImportGroupMembersFromData',
    GroupName='list-name-250',
    FieldNames='EmailAddress,FirstName,LastName,CompanyName',
    ImportData=csv_data_string,  # newline-delimited, comma-separated
    ColumnDelimiter=',', RowDelimiter='\n', TextQualifier='"')
# → "0\nSUCCESS"

# Wait 15s for async import, then verify count
jango('GetGroupMemberCount', GroupName='list-name-250')
# → must match CSV row count exactly
```

### 2. Prepare HTML

- Replace `{{UNSUBSCRIBE_LINK}}` → `https://track.scaleverticalwithai.com/u.z?***uniqueid****`
- Replace `{{VIEW_ONLINE_LINK}}` → `https://track.scaleverticalwithai.com/w.z?***uniqueid****`
- Replace relative image paths → JangoMail CDN URLs
- Fix byline dates
- Generate plain text version (strip HTML, decode entities)
- Verify: no `{{...}}` remaining, physical address in footer, `***uniqueid****` present

### 3. Send Test

Use `SendTransactionalEmail` (NOT `SendMassEmail` — it 500s for single recipients):

```python
jango('SendTransactionalEmail',
    FromEmail='email@scaleverticalwithai.com',
    FromName='Scale Vertical AI',
    ToEmailAddress='justin@usingaitoscale.com',
    Subject='🎯 Subject Line',
    MessagePlain=plain_text,
    MessageHTML=html_content,
    Options='TrackOpens,TrackClicks')
```

### 4. Send to Full List (after approval)

```python
jango('SendMassEmail',
    FromEmail='email@scaleverticalwithai.com',
    FromName='Scale Vertical AI',
    ToGroups='list-name-250',
    ToGroupFilter='',  # REQUIRED — pass empty string
    ToOther='',        # REQUIRED — pass empty string
    ToWebDatabase='',  # REQUIRED — pass empty string
    Subject='🎯 Subject Line',
    MessagePlain=plain_text,
    MessageHTML=html_content,
    Options='TrackOpens,TrackClicks')
# → "0\nSUCCESS\n{JobID}"
```

### 5. Verify Send

```python
# Check status
jango('GetMassEmailStatus', JobID=job_id)
# → "Sending", "Complete", or "Preprocessing"

# Check stats (v2)
GET https://api-v2.jangomail.com/campaigns/{job_id}/stats
# → recipients, opens, clicks, bounces, blocks, unsubscribes, complaints
```

### 6. Schedule +2hr Stats Report

Create a one-time cron job to pull stats 2 hours after send:

```
Schedule: once at {send_time + 2 hours}
Prompt: Pull stats for JangoMail campaign {job_id} via v2 API...
```

## Delivery Math

- `recipients` = actually sent to (after suppression removes)
- `removed_addresses` = pre-send suppression (global suppression list, duplicates) — NOT in recipients count
- `delivered` = `recipients - bounces - blocks`
- Open rate = `opens / delivered`

## Staggering Sends

When sending multiple newsletters in one day, stagger by 30+ minutes. JangoMail queues and processes sequentially, so actual inbox delivery naturally staggers further.

## People Person (Recruiting) — Special Status

Campaign 399343167 (People Person) is frozen in Preprocessing with 0 recipients. Recruiting is paused on purpose — the list was unverified. Do NOT send it. The list must be re-verified before any recruiting send.

## Newsletter Issue Archive (Jul 27 2026)

| Newsletter | Campaign ID | List | Recipients | Sent |
|---|---|---|---|---|
| Protocol (menshealth) | 399343647 | pr-agencies-batch-01 | 95 | Jul 23 |
| Green Room (PR agencies) | 399344421 | pr-agencies-batch-01 | 100 | Jul 23 |
| Protocol (menshealth) v2 | 399400311 | menshealth-coaching-MONDAY-250 | 250 | Jul 27 |
| Green Room (PR agencies) v2 | 399400061 | pr-agencies-MONDAY-250 | 250 | Jul 27 |
| People Person (recruiting) | 399343167 | — | 0 | FROZEN |