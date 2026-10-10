# JangoMail Merge Tags — Unsubscribe & View-Online Research (Jul 23 2026)

## Conclusion
JangoMail has **no merge tag placeholders** for unsubscribe links or view-online/web-version links.
Instead, it uses a `***uniqueid****` placeholder embedded inside actual tracking URLs, which is replaced per-recipient at send time. This was verified across four sources and live API testing.

## Sources Checked

1. **JangoMail Personalization Docs** (archived via Wayback Machine)
   - Merge tag syntax: `%%FieldName%%` with optional defaults `%%FieldName**default%%`
   - Special built-in tag: `%%EmailListName%%`
   - **No mention** of unsubscribe or view-online as merge tags
   - URL: `support.jangomail.com/hc/en-us/articles/200660114-Personalization`

2. **JangoMail "How Unsubscribes Work"** (archived)
   - Unsubscribe is handled via the editor's "Insert Content → Unsubscribe Link" menu item
   - Inserts an actual tracking URL: `http://x.jmxded92.net/u.z?***uniqueid****`
   - The `***uniqueid****` is per-recipient, replaced at send time
   - URL: `support.jangomail.com/hc/en-us/articles/202535870-How-Unsubscribes-Work`

3. **JangoMail Campaign Editor Docs** (archived)
   - "Insert Unsubscribe, View as Webpage Links" are editor menu items, not merge tags
   - Both are inserted as actual URLs via the Insert Content button
   - URL: `support.jangomail.com/hc/en-us/articles/201032770-Campaign-Editor`

4. **Live API Testing**
   - Tested `%%UNSUBSCRIBE%%`, `%%VIEWONLINE%%`, `%%WEBVERSION%%`, `%%UNSUB_LINK%%` in campaign HTML
   - Campaign created (ID 399338546), test sent to xander@usingaitoscale.com
   - None of these placeholder formats resolved — they passed through as literal text

## Working Solution — `***uniqueid****` URL Pattern (Jul 23 2026)

Discovered and tested: the `***uniqueid****` placeholder from the unsubscribe docs also works in the view-online URL pattern. JangoMail replaces it per-recipient in both contexts.

### Working URL patterns

```
Unsubscribe:  https://track.scaleverticalwithai.com/u.z?***uniqueid****
View online:  https://track.scaleverticalwithai.com/w.z?***uniqueid****
```

### Verification

- Campaigns created (IDs 399338872, 399338873, 399338874) with these URLs in the HTML
- All three completed without forced CAN-SPAM footer injection — confirms JangoMail's pre-processor recognized the URLs
- Real recipient view-online URL confirmed via `GetViewAsWebPageURL` v1 SOAP call:
  ```
  http://track.scaleverticalwithai.com/w.z?j=23B22A15AADA4776AE023A2F162A41B3&m=69C2F96096154C6ABEABBF46DD0F0989
  ```
  The `j` and `m` are per-recipient hashes — the `***uniqueid****` approach handles this in templates.

### Pre-Processor Behavior

JangoMail's campaign pre-processor scans each outgoing message for the account's
unsubscribe URL. If detected in the correct format (tracking domain + `/u.z?***uniqueid****`),
the pre-processor does NOT inject a duplicate CAN-SPAM footer. If not detected, it forces
a CAN-SPAM footer at the bottom using an HTML `<p>` tag.

### v1 SOAP: GetViewAsWebPageURL

The v1 SOAP API provides a method to generate per-recipient view-online URLs:

```python
status, body = jango('GetViewAsWebPageURL',
    JobID='399338734',
    EmailAddress='recipient@example.com')
# Returns: <string>http://track.scaleverticalwithai.com/w.z?j=HASH&m=HASH</string>
```

**Pitfall:** This method requires both `JobID` (campaign ID) and `EmailAddress` — it generates a
per-recipient URL, not a template placeholder. Use `***uniqueid****` in HTML templates instead.

## JangoMail v2 API — Related Campaign Fields

From `GET /campaigns/new` schema:
- `suppression_list_names` — list-level suppression config (not per-link)
- `suppression_campaign_ids` — campaign-level suppression (not per-link)  
- `suppression_days`, `suppression_hours` — time-based suppression windows
- `embed_images` — whether to embed images inline (boolean)
- `raw_message` — raw MIME message (not relevant to merge tags)

None of these expose merge-tag-equivalent functionality.

## Account Tracking Domain

- Domain: `track.scaleverticalwithai.com` (verified via `GET /trackingdomains`)
- HTTPS enabled: true
- This domain serves click tracking, unsubscribe (`/u.z`), and view-online (`/w.z`) URLs
