#!/usr/bin/env python3
"""Build the Matcha On Ice Cafe seasonal add-ons booklet.

Reads data/seasonal-add-ons.json, renders a self-contained A4 HTML
document, then prints it to PDF with headless Chromium. Shared brand
system lives in build/common.py.

Usage:
    python3 build/generate_seasonal.py            # write HTML + PDF
    python3 build/generate_seasonal.py --html     # write HTML only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, build  # noqa: E402

DATA = ROOT / "data" / "seasonal-add-ons.json"
HTML_OUT = ROOT / "dist" / "seasonal-add-ons.html"
PDF_OUT = ROOT / "dist" / "Matcha-On-Ice-Cafe-Seasonal-Add-Ons.pdf"


if __name__ == "__main__":
    build(DATA, HTML_OUT, PDF_OUT, html_only="--html" in sys.argv)
