#!/usr/bin/env python3
"""Build the Matcha On Ice Cafe equipment & bar manual.

Unlike the other documents in this repo, this one is deliberately NOT
styled with the café's brand system (no script font, no sage/cream
palette, no one-item-per-page layout). It's an internal operational
reference — plain sans-serif, black on white, dense tables and lists —
so it gets its own small stylesheet and page builder here rather than
reusing build/common.py's branded functions. Only the generic PDF
rendering utilities (ROOT, render_pdf) are shared.

Reads data/equipment-manual.json, renders a self-contained A4 HTML
document with natural print pagination, then prints it to PDF with
headless Chromium.

Usage:
    python3 build/generate_equipment.py            # write HTML + PDF
    python3 build/generate_equipment.py --html     # write HTML only
"""

import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, render_pdf  # noqa: E402

DATA = ROOT / "data" / "equipment-manual.json"
HTML_OUT = ROOT / "dist" / "equipment-manual.html"
PDF_OUT = ROOT / "dist" / "Matcha-On-Ice-Cafe-Equipment-Bar-Manual.pdf"


def stylesheet() -> str:
    return """
    * { box-sizing: border-box; }
    html, body {
        margin: 0; padding: 0;
        font-family: Arial, Helvetica, "Segoe UI", sans-serif;
        color: #1a1a1a;
        background: #fff;
        font-size: 10.5px;
        line-height: 1.5;
    }
    @page {
        size: A4;
        margin: 20mm 18mm 16mm 18mm;
    }
    .pdf-footer {
        display: none;
    }
    @media print {
        .pdf-footer {
            display: block;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 7.5px;
            color: #999;
        }
    }

    .titleblock {
        border-bottom: 2px solid #1a1a1a;
        padding-bottom: 10px;
        margin-bottom: 22px;
    }
    .titleblock .eyebrow {
        font-size: 8.5px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #666;
        margin: 0 0 3px 0;
    }
    .titleblock h1 {
        font-size: 20px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
    }

    .chapter {
        page-break-before: always;
        break-before: page;
    }
    .chapter:first-of-type {
        page-break-before: avoid;
        break-before: avoid;
    }
    .chapter-head {
        display: flex;
        align-items: baseline;
        gap: 10px;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 8px;
        margin: 0 0 16px 0;
    }
    .chapter-head .numeral {
        font-size: 13px;
        font-weight: 700;
        color: #666;
    }
    .chapter-head .titles { flex: 1; }
    .chapter-head h2 {
        font-size: 16px;
        font-weight: 700;
        margin: 0;
    }
    .chapter-head .subtitle {
        font-size: 10px;
        color: #555;
        margin-top: 1px;
    }

    .block { margin: 0 0 16px 0; break-inside: avoid; }
    .block h3 {
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #333;
        margin: 0 0 7px 0;
        border-bottom: 1px solid #ccc;
        padding-bottom: 3px;
    }

    .prose p {
        margin: 0 0 8px 0;
    }
    .prose p:last-child { margin-bottom: 0; }

    table.specs {
        width: 100%;
        border-collapse: collapse;
    }
    table.specs tr { break-inside: avoid; }
    table.specs th {
        text-align: left;
        font-size: 8.5px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #666;
        padding: 0 10px 4px 0;
        border-bottom: 1px solid #1a1a1a;
    }
    table.specs td {
        padding: 5px 10px 5px 0;
        border-bottom: 1px solid #ddd;
        vertical-align: top;
    }
    table.specs tr:last-child td { border-bottom: none; }
    table.specs td.item {
        font-weight: 700;
        width: 42%;
        color: #1a1a1a;
    }
    table.specs td.value {
        color: #333;
    }
    table.specs.multi td.item { width: auto; }

    ol.steps {
        margin: 0;
        padding-left: 18px;
    }
    ol.steps li {
        margin: 0 0 6px 0;
        break-inside: avoid;
    }
    ol.steps li:last-child { margin-bottom: 0; }

    dl.deflist { margin: 0; }
    dl.deflist .entry {
        break-inside: avoid;
        padding: 8px 0;
        border-bottom: 1px solid #ddd;
    }
    dl.deflist .entry:first-child { padding-top: 0; }
    dl.deflist .entry:last-child { border-bottom: none; padding-bottom: 0; }
    dl.deflist dt {
        font-weight: 700;
        font-size: 11px;
        display: inline;
    }
    dl.deflist .spec {
        color: #666;
        font-weight: 400;
        font-size: 10px;
    }
    dl.deflist dt::after { content: " — "; font-weight: 400; color: #999; }
    dl.deflist dd {
        margin: 4px 0 0 0;
    }
    dl.deflist ul.use {
        margin: 3px 0 0 0;
        padding-left: 16px;
    }
    dl.deflist ul.use li { margin: 0 0 2px 0; }
    dl.deflist .note {
        margin: 4px 0 0 0;
        color: #666;
        font-style: italic;
        font-size: 9.5px;
    }

    .warning {
        border-left: 3px solid #1a1a1a;
        background: #f3f3f3;
        padding: 8px 10px;
        font-size: 9.5px;
    }
    .warning.single {
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .warning ul {
        margin: 0;
        padding-left: 16px;
    }
    .warning li {
        margin: 0 0 4px 0;
        font-weight: 700;
    }
    .warning li:last-child { margin-bottom: 0; }

    .checklist { display: flex; gap: 24px; }
    .checklist .group { flex: 1; }
    .checklist .group h4 {
        font-size: 9.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #333;
        margin: 0 0 6px 0;
    }
    .checklist ul {
        list-style: none;
        margin: 0;
        padding: 0;
    }
    .checklist li {
        margin: 0 0 5px 0;
        padding-left: 16px;
        position: relative;
    }
    .checklist li::before {
        content: "\\2610";
        position: absolute;
        left: 0;
        color: #666;
    }
    """


def _lead_html(entry) -> str:
    if isinstance(entry, dict):
        return f'<strong>{escape(entry["lead"])}.</strong> {escape(entry["text"])}'
    return escape(entry)


def build_table(rows, headers=None, columns=None) -> str:
    columns = columns or ["item", "value"]
    thead = ""
    css_class = "specs"
    if headers:
        thead = "<thead><tr>" + "".join(f"<th>{escape(h)}</th>" for h in headers) + "</tr></thead>"
        css_class += " multi"
    trs = "".join(
        "<tr>" + "".join(
            f'<td class="{"item" if i == 0 else "value"}">{escape(r[col])}</td>'
            for i, col in enumerate(columns)
        ) + "</tr>"
        for r in rows
    )
    return f'<table class="{css_class}">{thead}{trs}</table>'


def build_steps(items) -> str:
    lis = "".join(f"<li>{_lead_html(step)}</li>" for step in items)
    return f'<ol class="steps">{lis}</ol>'


def build_deflist(items) -> str:
    entries = []
    for item in items:
        use_html = ""
        if item.get("use"):
            use_html = "<ul class=\"use\">" + "".join(
                f"<li>{escape(step)}</li>" for step in item["use"]
            ) + "</ul>"
        note_html = f'<p class="note">{escape(item["note"])}</p>' if item.get("note") else ""
        entries.append(
            "<div class=\"entry\">"
            f'<dt>{escape(item["term"])} <span class="spec">({escape(item["spec"])})</span></dt>'
            f"<dd>{use_html}{note_html}</dd>"
            "</div>"
        )
    return f'<dl class="deflist">{"".join(entries)}</dl>'


def build_checklist(groups) -> str:
    cols = "".join(
        '<div class="group">'
        f'<h4>{escape(g["label"])}</h4>'
        "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in g["items"]) + "</ul>"
        "</div>"
        for g in groups
    )
    return f'<div class="checklist">{cols}</div>'


def build_block(block) -> str:
    kind = block["type"]
    heading = f'<h3>{escape(block["heading"])}</h3>' if block.get("heading") else ""

    if kind == "prose":
        body = "".join(f"<p>{_lead_html(p)}</p>" for p in block["paragraphs"])
        return f'<div class="block prose">{heading}{body}</div>'
    if kind == "table":
        table = build_table(block["rows"], block.get("headers"), block.get("columns"))
        return f'<div class="block">{heading}{table}</div>'
    if kind == "steps":
        return f'<div class="block">{heading}{build_steps(block["items"])}</div>'
    if kind == "deflist":
        return f'<div class="block">{heading}{build_deflist(block["items"])}</div>'
    if kind == "checklist":
        return f'<div class="block">{heading}{build_checklist(block["groups"])}</div>'
    if kind == "warning":
        if block.get("items"):
            body = "<ul>" + "".join(f"<li>{escape(t)}</li>" for t in block["items"]) + "</ul>"
            return f'<div class="block warning">{heading}{body}</div>'
        return f'<div class="block warning single">{escape(block["text"])}</div>'
    raise ValueError(f"unknown block type: {kind}")


def build_chapter(chapter) -> str:
    blocks_html = "".join(build_block(b) for b in chapter["blocks"])
    return (
        '<section class="chapter">'
        '<div class="chapter-head">'
        f'<span class="numeral">{escape(chapter["numeral"])}</span>'
        '<div class="titles">'
        f'<h2>{escape(chapter["title"])}</h2>'
        f'<div class="subtitle">{escape(chapter["subtitle"])}</div>'
        "</div>"
        "</div>"
        f"{blocks_html}"
        "</section>"
    )


def build_document(catalog) -> str:
    chapters_html = "".join(build_chapter(c) for c in catalog["chapters"])
    body = (
        f'<div class="pdf-footer">{escape(catalog["footer"])}</div>'
        '<div class="titleblock">'
        '<p class="eyebrow">Internal Reference — Not for Guest Distribution</p>'
        f'<h1>{escape(catalog["documentTitle"])}</h1>'
        "</div>"
        f"{chapters_html}"
    )
    return (
        "<!doctype html>"
        '<html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(catalog['documentTitle'])}</title>"
        f"<style>{stylesheet()}</style>"
        "</head><body>"
        f"{body}"
        "</body></html>\n"
    )


def build(data_path: Path, html_out: Path, pdf_out: Path, html_only: bool = False) -> None:
    catalog = json.loads(data_path.read_text(encoding="utf-8"))
    html_out.parent.mkdir(parents=True, exist_ok=True)

    html_out.write_text(build_document(catalog), encoding="utf-8")
    print(f"html  -> {html_out.relative_to(ROOT)}  ({html_out.stat().st_size // 1024} KB)")

    if html_only:
        return

    render_pdf(html_out, pdf_out)
    print(f"pdf   -> {pdf_out.relative_to(ROOT)}  ({pdf_out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build(DATA, HTML_OUT, PDF_OUT, html_only="--html" in sys.argv)
