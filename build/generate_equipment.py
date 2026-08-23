#!/usr/bin/env python3
"""Build the Matcha On Ice Cafe equipment & bar manual.

Reads data/equipment-manual.json, renders a self-contained A4 HTML
document, then prints it to PDF with headless Chromium. Shared brand
system lives in build/common.py.

Usage:
    python3 build/generate_equipment.py            # write HTML + PDF
    python3 build/generate_equipment.py --html     # write HTML only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, build  # noqa: E402

DATA = ROOT / "data" / "equipment-manual.json"
HTML_OUT = ROOT / "dist" / "equipment-manual.html"
PDF_OUT = ROOT / "dist" / "Matcha-On-Ice-Cafe-Equipment-Bar-Manual.pdf"


if __name__ == "__main__":
    build(DATA, HTML_OUT, PDF_OUT, html_only="--html" in sys.argv)
