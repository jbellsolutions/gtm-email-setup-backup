# PDF Sizing Guide — Getting to Exactly 5 Pages

The content budget is tight: 5 sections × ~320-370 words each at 8.5pt Georgia on US Letter with 1.3cm/1.5cm margins. You will almost certainly overflow on first render.

## Debugging workflow

1. **Render**: `python3 scripts/build_pdf.py working.md "Name — Partner-Backed Plan.pdf"`
2. **Check page count**: `/usr/bin/python3 -c "import pdfplumber; print(len(pdfplumber.open('/tmp/PDF_NAME.pdf').pages))"`
3. **If >5 pages**, identify which sections overflow:
   ```python
   import pdfplumber
   with pdfplumber.open('/tmp/PDF_NAME.pdf') as pdf:
       for i, p in enumerate(pdf.pages):
           text = p.extract_text() or ''
           print(f'Page {i+1}: {len(text.split())} words')
   ```
4. **Trim the overflowing section(s)**, re-render, repeat.

## Root cause of 10+ page renders

**pandoc `--standalone` breaks page breaks.** Pandoc's standalone mode injects its own CSS (including `max-width` on body) that overrides the `page-break-after: always` rule on `.pagebreak` divs. The fix: drop `--standalone` from the pandoc call entirely. This was the root cause of every 10-page render (July 11, 2026).

## Real session log: Vivian Gale (July 11, 2026)

| Iteration | Font | Margins | Pages | Notes |
|---|---|---|---|---|
| 1 (original) | 10pt | 1.9/2.2cm | 10 | `--standalone` enabled, page breaks ignored |
| 2 (v4) | 9pt | 1.4/1.8cm | 6 | `--standalone` still enabled, h1 breaks added |
| 3 (v5) | 8.5pt | 1.3/1.7cm | 6 | Same — `--standalone` was the culprit, not font size |
| 4 (no standalone) | 8pt | 1.0/1.5cm | 5 | Dropped `--standalone`, instant fix |
| 5 (final v2) | 8.5pt | 1.3/1.5cm | 5 | Restored readable sizing, still 5 pages |

**Lesson:** Before tweaking fonts and margins, check whether pandoc's `--standalone` flag is present. Removing it is a one-character fix that saves multiple trim/render cycles.

## Word-count budget per section

When building the markdown, aim for:
- Page 1 (Overview): ≤330 words
- Page 2 (Power Partners): ≤370 words (the bullet list compresses well)
- Page 3 (Influencer Graph): ≤320 words
- Page 4 (Podcast Game Plan): ≤350 words
- Page 5 (Voice + Newsletter): ≤320 words

Check before rendering: `python3 -c "with open('working.md') as f: md=f.read(); [print(f'Page {i+1}: {len(s.split())} words') for i,s in enumerate(md.split('<!-- PAGE -->'))]"`
