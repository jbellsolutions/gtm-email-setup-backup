# Newsletter Staging: Zip → ListMonk Draft

End-to-end workflow for converting a JangoMail newsletter zip into a ListMonk draft ready to send. Used 3x: Green Room, Protocol, People Person.

## 1. Extract Zip

```python
import zipfile
z = zipfile.ZipFile("issue-1.zip")
z.extractall("/tmp/draft/")
# Expects: index.html + images/ directory with JPGs and logo.png
```

## 2. Upload Images to JangoMail CDN

Images must have UNIQUE filenames per upload batch — JangoMail CDN caches aggressively. Use timestamp prefix:

```python
ts = str(int(time.time()))
prefix = f"pp-v1-{ts}"  # or gr-, protocol-, etc.
# Upload each image in images/ via POST /files (v2 REST)
# URL pattern: https://img.jangomail.com/2606407/Images/{prefix}-{filename}
```

## 3. Rewrite Image Paths + Convert Merge Tags

```python
html = html.replace('src="images/banner.jpg"', f'src="{cdn_url}/banner.jpg"')
# ... repeat for all 9 images

# Merge tags — these are the ONLY conversions needed:
html = html.replace("{{VIEW_ONLINE_LINK}}", "{{ MessageURL }}")
html = html.replace("{{UNSUBSCRIBE_LINK}}", "{{ UnsubscribeURL }}")
```

Verify: zero remaining `images/` paths, zero `{{VIEW_ONLINE_LINK}}`/`{{UNSUBSCRIBE_LINK}}`, and only `{{ MessageURL }}` + `{{ UnsubscribeURL }}` remain.

## 4. Create ListMonk Draft

```python
payload = {
    "name": "Newsletter — Subject Line",
    "subject": "Subject line",
    "from_email": "The Newsletter <newsletter@send.usingaitoscale.com>",
    "body": processed_html,
    "content_type": "html",
    "template_id": 6,  # Passthrough template — NO default borders/fonts
    "messenger": "email",
    "tags": ["newsletter", "newsletter-name"],
    "lists": [1],  # Default list initially
    "archive": False,
}
# POST /api/campaigns
```

## 5. Link Verification

All editorial links must be RAW (no tracking wrapping). ListMonk's native click tracking wraps them at send time. Verify each resolves:

```python
for link in editorial_links:
    # HEAD request — 200 = good, 403 = bot-blocked (OK), 404 = broken
```

Key link types to verify: Medium articles, source citations, case study PDFs, news articles, government sites.

## Passthrough Template (ID 6)

Created to avoid ListMonk's default template (ID 1) which injects: gray background, Helvetica fonts, max-width container, table borders, and duplicate footer/unsubscribe links. Template 6 renders the campaign body as-is with only the open-tracking pixel injected.

The `{{ MessageURL }}` and `{{ UnsubscribeURL }}` tags in the campaign body get replaced with ListMonk's tracking URLs — this replaces JangoMail's `***uniqueid****` URL pattern with ListMonk's native link handling.
