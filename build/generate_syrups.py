#!/usr/bin/env python3
"""Build the Matcha On Ice Cafe syrups & cold foam manual.

Reads data/syrups.json, renders a self-contained A4 HTML document, then
prints it to PDF with headless Chromium. Shared brand system lives in
build/common.py — this document uses the same fonts, palette and page
furniture as the matcha catalogue, with simpler per-item pages (plain
recipe: ingredients + method, no photo, no size split).

Usage:
    python3 build/generate_syrups.py            # write HTML + PDF
    python3 build/generate_syrups.py --html     # write HTML only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, build  # noqa: E402

DATA = ROOT / "data" / "syrups.json"
HTML_OUT = ROOT / "dist" / "syrups.html"
PDF_OUT = ROOT / "dist" / "Matcha-On-Ice-Cafe-Syrups-Cold-Foam.pdf"


if __name__ == "__main__":
    build(DATA, HTML_OUT, PDF_OUT, html_only="--html" in sys.argv)
