#!/usr/bin/env python3
"""Render the partner-backed plan to a branded PDF (2-3 pages, visual, CTA-focused).

Usage: python3 build_pdf.py working.md "Business Name - Partner-Backed Plan.pdf"

The markdown should contain <!-- PAGE --> markers between sections;
each section is forced onto its own page. Requires pandoc + weasyprint.
Uses /usr/bin/python3 (where weasyprint is installed).
"""

import subprocess, sys, tempfile, os, shutil

CSS = """
@page {
  size: letter;
  margin: 2cm 2.2cm;
  @bottom-center {
    content: "AI Integraterz  ·  usingaitoscale.com";
    font-size: 7.5pt;
    color: #999;
    font-family: Helvetica, Arial, sans-serif;
  }
  @bottom-right {
    content: counter(page);
    font-size: 7.5pt;
    color: #999;
    font-family: Helvetica, Arial, sans-serif;
  }
}

body {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #1d1d1f;
  -webkit-font-smoothing: antialiased;
}

/* ── Headlines ── */
h1 {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 22pt;
  line-height: 1.15;
  color: #0f2740;
  margin: 0 0 6pt 0;
  letter-spacing: -0.4pt;
  font-weight: 700;
  page-break-before: always;
}
h1:first-of-type {
  page-break-before: avoid;
}

h2 {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 14pt;
  color: #0f2740;
  border-bottom: 2px solid #c96f2e;
  padding-bottom: 3pt;
  margin: 14pt 0 8pt 0;
  font-weight: 700;
  letter-spacing: -0.2pt;
}

h3 {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 12pt;
  color: #c96f2e;
  margin: 10pt 0 6pt 0;
  font-weight: 600;
}

/* ── Body emphasis ── */
strong {
  color: #0f2740;
  font-weight: 700;
}

p {
  margin: 0 0 8pt 0;
  orphans: 2;
  widows: 2;
}

/* ── Pull quotes / callout boxes ── */
blockquote {
  border-left: 3px solid #c96f2e;
  margin: 10pt 0 10pt 0;
  padding: 8pt 0 8pt 12pt;
  color: #333;
  background: #faf6f1;
  font-size: 11.5pt;
  line-height: 1.45;
  border-radius: 0 3px 3px 0;
}
blockquote p {
  margin: 0;
}

/* ── CTA box (last page) ── */
section.cta-box, div.cta-box {
  border: 2px solid #c96f2e;
  background: #faf6f1;
  padding: 14pt 18pt;
  margin: 16pt 0;
  border-radius: 4px;
  text-align: center;
}
section.cta-box h2, div.cta-box h2 {
  border-bottom: none;
  margin-top: 0;
  font-size: 16pt;
  color: #0f2740;
}
section.cta-box p, div.cta-box p {
  font-size: 11.5pt;
  margin-bottom: 6pt;
}
.cta-button {
  display: inline-block;
  background: #c96f2e;
  color: #fff !important;
  padding: 8pt 28pt;
  font-family: Helvetica, Arial, sans-serif;
  font-size: 13pt;
  font-weight: 700;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 6pt;
}

/* ── Tables ── */
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 10.5pt;
  font-family: Helvetica, Arial, sans-serif;
  margin: 10pt 0;
}
th {
  background: #0f2740;
  color: #fff;
  text-align: left;
  padding: 6pt 8pt;
  font-weight: 600;
  font-size: 10.5pt;
}
td {
  border: 1px solid #d9d9d9;
  padding: 5pt 8pt;
  vertical-align: top;
  line-height: 1.4;
}

/* ── Lists ── */
ul, ol {
  margin: 4pt 0;
  padding-left: 16pt;
  line-height: 1.5;
}
li {
  margin: 3pt 0;
}

/* ── Stat / number callout ── */
.stat {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 32pt;
  font-weight: 700;
  color: #c96f2e;
  line-height: 1;
  margin: 0;
}

/* ── Section divider ── */
hr {
  border: none;
  border-top: 1px solid #e0d5c5;
  margin: 12pt 0;
}

/* ── Page break marker ── */
.pagebreak {
  page-break-after: always;
}
"""

SYS_PYTHON = "/usr/bin/python3"

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]

    # Install weasyprint to system python if needed
    try:
        subprocess.run([SYS_PYTHON, "-c", "import weasyprint"], check=True,
                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        subprocess.run(["pip", "install", "weasyprint", "--break-system-packages", "-q"],
                       check=True)

    md = open(src, encoding="utf-8").read()
    md = md.replace("<!-- PAGE -->", '\n\n<div class="pagebreak"></div>\n\n')

    with tempfile.TemporaryDirectory() as td:
        mdf = os.path.join(td, "in.md")
        htmlf = os.path.join(td, "in.html")
        cssf = os.path.join(td, "s.css")
        open(mdf, "w", encoding="utf-8").write(md)
        open(cssf, "w", encoding="utf-8").write(CSS)
        pandoc = shutil.which("pandoc") or sys.exit("pandoc not found")
        # CRITICAL: do NOT use --standalone — pandoc's injected CSS overrides page-break rules
        subprocess.run([pandoc, mdf, "-f", "markdown", "-t", "html5",
                        "-o", htmlf], check=True)
        subprocess.run([SYS_PYTHON, "-m", "weasyprint", "-s", cssf, htmlf, out], check=True)

    try:
        import pdfplumber
        with pdfplumber.open(out) as pdf:
            n = len(pdf.pages)
        if 1 <= n <= 3:
            print(f"OK: {out} ({n} pages)")
        else:
            print(f"WARNING: {out} ({n} pages) — expected 1-3 pages")
    except Exception:
        print(f"OK: {out} (page count unverified)")

if __name__ == "__main__":
    main()