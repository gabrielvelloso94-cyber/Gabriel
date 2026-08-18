#!/usr/bin/env python3
"""Build the Matcha On Ice Cafe coffee bar manual.

Reads data/coffee-bar-manual.json, renders a self-contained A4 HTML
document, then prints it to PDF with headless Chromium. Shared brand
system lives in build/common.py.

Usage:
    python3 build/generate_coffee.py            # write HTML + PDF
    python3 build/generate_coffee.py --html     # write HTML only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, build  # noqa: E402

DATA = ROOT / "data" / "coffee-bar-manual.json"
HTML_OUT = ROOT / "dist" / "coffee-bar-manual.html"
PDF_OUT = ROOT / "dist" / "Matcha-On-Ice-Cafe-Coffee-Bar-Manual.pdf"


if __name__ == "__main__":
    build(DATA, HTML_OUT, PDF_OUT, html_only="--html" in sys.argv)
