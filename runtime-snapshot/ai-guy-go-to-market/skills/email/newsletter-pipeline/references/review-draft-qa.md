# Newsletter review-draft QA

Use this when a stakeholder asks for designed HTML before images or publication assets are available.

## Two statuses

- **Review draft:** layout and copy can be reviewed; styled image placeholders are permitted; no send.
- **Send ready:** actual reviewed images, real logo, resolved/approved links, Medium HTML plus five tags, packaged research ledger, merge fields, and final render QA.

## Review-draft checks

- Preserve exact future image filenames: `images/banner.jpg`, `images/s1.jpg` through `images/s5.jpg`.
- Use styled placeholder cells rather than broken image icons, but label the file and handoff as `REVIEW DRAFT — NOT SEND READY`.
- Keep the real logo requirement even in a draft. A text tile such as `LOGO PLACEHOLDER` is a wireframe exception, not a compliant draft.
- Remove `href="#"` links. Either supply a real destination or remove the control.
- Keep unresolved merge fields explicit: `{{MEDIUM_URL}}`, `{{VIEW_ONLINE_LINK}}`, and `{{UNSUBSCRIBE_LINK}}`.
- Do not run a test send from a placeholder draft.

## Final promotion gate

Before calling the issue send-ready, verify:

1. Six required image files exist and render; dimensions match banner 600px and stories 594px.
2. `images/logo.png` exists and is used in the masthead.
3. No dead/hash links remain.
4. Medium article HTML exists and exactly five tags are handed over.
5. Research/stat ledger is in the self-contained issue folder.
6. From display name, Reply-To, subject, target recipients, and merge fields are configured outside the HTML body.
7. Card skeleton/style parity is rechecked after image insertion.
8. Browser render is checked at desktop and mobile widths.

## Common false passes

- Counting placeholder text as image wiring: it is not.
- Counting `class="card"` as story-card parity without separating utility and house-blurb cards.
- Treating a successful HTML parse as email QA.
- Calling a file complete because the copy matches the Markdown while logo, Medium, links, and packaging remain incomplete.
