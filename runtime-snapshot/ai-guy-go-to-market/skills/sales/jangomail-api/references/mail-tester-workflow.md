# Mail-Tester Workflow

mail-tester.com provides free one-shot spam scoring. Each address works once — get a
fresh one for each test.

## Step-by-step

### 1. Get an address
Navigate to https://www.mail-tester.com/ — the page shows a unique email address
like `test-xxxxxxxxx@srv1.mail-tester.com`. Copy it.

### 2. Send your email
Send the test campaign to that address immediately. The address expires after ~30
minutes of no activity.

### 3. Check the score
Navigate to `https://www.mail-tester.com/test-{id}` where `{id}` is the part before
`@` (e.g., `test-kyjoy8pdi` → `https://www.mail-tester.com/test-kyjoy8pdi`).

The page shows a score out of 10 with expandable sections:
- **Click here to view your message** — shows From, Bounce address, HTML/text versions
- **SpamAssassin** — detailed spam rule hits
- **You're properly authenticated** — SPF/DKIM/DMARC pass/fail
- **Your message is safe and well formatted** — formatting issues
- **You're not blocklisted** — blacklist checks
- **No broken links** — link validation

### 4. Extract raw headers (for List-Unsubscribe, SPF, DKIM checks)
Click the "Source" section to expand, then use browser console:

```javascript
document.querySelectorAll('pre')
```

This returns all `<pre>` elements containing the raw email source, SpamAssassin
report, DKIM signature, SPF query results, and DMARC results.

Key headers to check:
- `List-Unsubscribe:` — should be present with URL + mailto
- `List-Unsubscribe-Post: List-Unsubscribe=One-Click` — Gmail/Yahoo Feb 2024 required
- `Received-SPF:` — should show `Pass`
- `Authentication-Results: dkim.mail-tester.com; dkim=pass` — DKIM validation
- `Return-Path` / bounce address

### 5. Multiple tests
Each mail-tester address is single-use. Navigate to mail-tester.com again to get
a fresh address for each subsequent test. The page generates a new address on
each visit.

## Pitfalls

- The address expires if no email arrives within ~30 minutes
- Each address can only be scored once — send to a NEW address for each test
- The "Click here to view your message" → "Source" section must be expanded
  by clicking — browser_snapshot won't show the raw headers until expanded
- Use `browser_console` with `document.querySelectorAll('pre')` to get raw header
  text when the DOM snapshot misses expandable content