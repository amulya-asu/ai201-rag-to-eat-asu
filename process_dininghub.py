#!/usr/bin/env python3
"""
Extract text from the ASU dining-hub PDFs into documents/dininghub/.

These pages are the official baseline (venue names / categories) used for
spatial-aware "what options exist" answers. Text only — a sub-agent will add
per-location descriptions later.
"""

from pathlib import Path

import pdfplumber

RAW = Path("raw/dininghub")
OUT = Path("documents/dininghub")
OUT.mkdir(parents=True, exist_ok=True)

for pdf_path in sorted(RAW.glob("*.pdf")):
    with pdfplumber.open(pdf_path) as pdf:
        n_pages = len(pdf.pages)
        text = "\n\n".join(p.extract_text() for p in pdf.pages if p.extract_text())
    out_path = OUT / f"{pdf_path.stem}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"{pdf_path.name} -> {out_path}  ({n_pages} pages, {len(text)} chars)")

print("\n[OK] Dining-hub text extracted to documents/dininghub/")
