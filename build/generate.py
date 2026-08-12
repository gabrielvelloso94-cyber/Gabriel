#!/usr/bin/env python3
"""Build the Matcha On Ice Cafe drink catalogue.

Reads data/catalog.json, renders a self-contained A4 HTML document
(fonts and photos embedded as data URIs), then prints it to PDF with
headless Chromium.

Usage:
    python3 build/generate.py            # write HTML + PDF
    python3 build/generate.py --html     # write HTML only
"""

import base64
import json
import mimetypes
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "catalog.json"
FONTS = ROOT / "assets" / "fonts"
PHOTOS = ROOT / "assets" / "photos"
BRAND = ROOT / "assets" / "brand"
DIST = ROOT / "dist"

HTML_OUT = DIST / "catalog.html"
PDF_OUT = DIST / "Matcha-On-Ice-Cafe-Catalog.pdf"

PHOTO_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".avif")


# --------------------------------------------------------------------------
# assets
# --------------------------------------------------------------------------

def data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if mime is None:
        mime = "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def font_face(family: str, filename: str, weight: str, style: str = "normal") -> str:
    path = FONTS / filename
    if not path.exists():
        raise SystemExit(f"missing font: {path}")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        "@font-face{"
        f"font-family:'{family}';"
        f"font-style:{style};"
        f"font-weight:{weight};"
        "font-display:block;"
        f"src:url(data:font/ttf;base64,{b64}) format('truetype');"
        "}"
    )


def find_photo(name: str | None) -> Path | None:
    """Resolve a photo by exact filename, or by stem with any known extension."""
    if not name:
        return None
    exact = PHOTOS / name
    if exact.exists():
        return exact
    stem = Path(name).stem
    for ext in PHOTO_EXTS:
        candidate = PHOTOS / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def find_logo() -> Path | None:
    if not BRAND.exists():
        return None
    for ext in PHOTO_EXTS + (".svg",):
        for candidate in sorted(BRAND.glob(f"logo{ext}")):
            return candidate
    return None


# --------------------------------------------------------------------------
# stylesheet
# --------------------------------------------------------------------------

def stylesheet() -> str:
    faces = "".join([
        font_face("Brand Script", "Allura-Regular.ttf", "400"),
        font_face("Brand Serif", "CormorantGaramond-Variable.ttf", "300 700"),
        font_face("Brand Serif", "CormorantGaramond-Italic-Variable.ttf", "300 700", "italic"),
        font_face("Brand Sans", "Jost-Variable.ttf", "300 700"),
    ])

    return faces + """
:root{
  --sage:#8a9b6e;
  --sage-deep:#5d6b45;
  --sage-soft:#b6c19d;
  --sage-mist:#e4e8d8;
  --cream:#f6f2e8;
  --cream-deep:#efe9db;
  --ink:#2f3328;
  --ink-soft:#6b6f5f;
}

*{box-sizing:border-box;margin:0;padding:0;}

@page{size:A4;margin:0;}

html,body{
  background:var(--cream);
  color:var(--ink);
  font-family:'Brand Sans',sans-serif;
  -webkit-font-smoothing:antialiased;
  -webkit-print-color-adjust:exact;
  print-color-adjust:exact;
}

.page{
  position:relative;
  width:210mm;
  height:297mm;
  background:var(--cream);
  overflow:hidden;
  display:flex;
  flex-direction:column;
  page-break-after:always;
  break-after:page;
}
.page:last-child{page-break-after:auto;break-after:auto;}

/* ---------- shared type ---------- */

.caps{
  font-family:'Brand Sans',sans-serif;
  font-weight:400;
  text-transform:uppercase;
  letter-spacing:.34em;
}

.script{
  font-family:'Brand Script',cursive;
  font-weight:400;
  line-height:.95;
}

.serif{font-family:'Brand Serif',serif;}

.rule{height:1px;background:var(--sage-soft);border:0;}
.rule-dark{height:1px;background:var(--sage);border:0;}

/* ---------- cover ---------- */

.cover{padding:14mm;}
.cover-frame{
  flex:1;
  border:1px solid var(--sage-soft);
  padding:13mm 14mm 10mm;
  display:flex;
  flex-direction:column;
}

.lockup{text-align:center;padding-top:4mm;}
.lockup-logo{max-width:78mm;max-height:42mm;margin:0 auto 4mm;display:block;}
.lockup .script{
  font-size:70pt;
  color:var(--sage-deep);
  margin-bottom:-4mm;
}
.lockup .on-ice{
  font-family:'Brand Serif',serif;
  font-weight:400;
  font-size:27pt;
  letter-spacing:.18em;
  text-transform:uppercase;
  color:var(--ink);
}
.lockup-bar{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:5mm;
  margin-top:3.5mm;
}
.lockup-bar span.caps{font-size:8.5pt;color:var(--sage-deep);}
.lockup-bar i{display:block;width:16mm;height:1px;background:var(--sage-soft);}

.cover-meta{
  text-align:center;
  margin-top:7mm;
  padding-bottom:8mm;
  border-bottom:1px solid var(--sage-soft);
}
.cover-meta .tagline{
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-weight:400;
  font-size:14.5pt;
  color:var(--ink-soft);
}
.cover-meta .edition{
  margin-top:3mm;
  font-size:7.2pt;
  color:var(--sage-deep);
}

/* ---------- index ---------- */

.index{flex:1;display:flex;flex-direction:column;justify-content:center;gap:8mm;padding:6mm 0;}

.index-block-head{
  display:flex;
  align-items:baseline;
  gap:4mm;
  margin-bottom:3.5mm;
}
.index-numeral{
  font-family:'Brand Serif',serif;
  font-weight:400;
  font-size:10pt;
  letter-spacing:.12em;
  color:var(--sage);
  min-width:9mm;
}
.index-block-head .label{
  font-size:9pt;
  color:var(--ink);
}
.index-block-head .count{
  margin-left:auto;
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:9.5pt;
  color:var(--sage);
}

.index-list{list-style:none;padding-left:13mm;}
.index-row{
  display:flex;
  align-items:baseline;
  gap:2mm;
  padding:1.35mm 0;
}
.index-row .no{
  font-family:'Brand Sans',sans-serif;
  font-size:7pt;
  letter-spacing:.1em;
  color:var(--sage);
  min-width:7mm;
}
.index-row .name{
  font-family:'Brand Serif',serif;
  font-weight:400;
  font-size:13pt;
  color:var(--ink);
  white-space:nowrap;
}
.index-row .dots{
  flex:1;
  border-bottom:1px dotted var(--sage-soft);
  transform:translateY(-1mm);
}
.index-row .pg{
  font-family:'Brand Sans',sans-serif;
  font-size:8pt;
  color:var(--ink-soft);
}
.index-row.pending .name{color:var(--ink-soft);font-style:italic;}

.cover-foot{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding-top:5mm;
  border-top:1px solid var(--sage-soft);
  font-size:6.6pt;
  color:var(--sage-deep);
}

/* ---------- section divider ---------- */

.divider{
  background:var(--sage);
  color:var(--cream);
  text-align:center;
  padding:14mm;
}
.divider-inner{
  flex:1;
  border:1px solid rgba(246,242,232,.42);
  padding:20mm 16mm;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
}
.divider .numeral{
  font-family:'Brand Serif',serif;
  font-size:11pt;
  letter-spacing:.4em;
  opacity:.85;
}
.divider .script{
  font-size:60pt;
  margin:6mm 0 5mm;
  color:var(--cream);
}
.divider .blurb{
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:13.5pt;
  line-height:1.6;
  max-width:138mm;
  margin:0 auto;
  opacity:.92;
  text-wrap:balance;
}
.divider .divider-mark{
  position:absolute;
  left:0;
  right:0;
  bottom:24mm;
  font-size:6.8pt;
  opacity:.8;
}

/* ---------- drink page ---------- */

.drink{padding:15mm 17mm 12mm;}

.drink-head{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  font-size:6.8pt;
  color:var(--sage-deep);
  padding-bottom:3mm;
  border-bottom:1px solid var(--sage-soft);
}

.drink-title{text-align:center;padding:7mm 0 6mm;}
.drink-title .eyebrow{
  font-size:6.8pt;
  color:var(--sage);
  display:block;
  margin-bottom:3.5mm;
}
.drink-title .script{
  font-size:47pt;
  color:var(--sage-deep);
  padding:0 4mm;
}

/* photo / placeholder block */

.shot{
  position:relative;
  width:116mm;
  height:124mm;
  flex-shrink:0;
  margin:0 auto;
}
.shot-keyline{
  position:absolute;
  inset:-3.5mm;
  border:1px solid var(--sage-soft);
  pointer-events:none;
}
.shot-inner{
  width:100%;
  height:100%;
  overflow:hidden;
  background:var(--cream-deep);
}
.shot-inner img{
  width:100%;
  height:100%;
  object-fit:cover;
  display:block;
}

.shot-placeholder{
  width:100%;
  height:100%;
  background:var(--sage);
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  text-align:center;
  padding:10mm;
}
.shot-placeholder.cream{background:var(--sage-mist);}
.shot-placeholder .script{
  font-size:33pt;
  color:var(--cream);
  line-height:1.06;
}
.shot-placeholder.cream .script{color:var(--sage-deep);}
.shot-placeholder .stamp{
  margin-top:7mm;
  font-size:6pt;
  letter-spacing:.32em;
  color:rgba(246,242,232,.72);
}
.shot-placeholder.cream .stamp{color:var(--sage);}
.shot-placeholder .flourish{
  width:14mm;
  height:1px;
  background:rgba(246,242,232,.55);
  margin-top:6mm;
}
.shot-placeholder.cream .flourish{background:var(--sage-soft);}

/* recipe columns */

.recipe{
  flex:1;
  display:flex;
  gap:11mm;
  padding-top:9mm;
  margin-top:8mm;
  border-top:1px solid var(--sage-soft);
  min-height:0;
}
.col-ingredients{flex:0 0 62mm;}
.col-method{flex:1;}

.col-label{
  font-size:7pt;
  color:var(--sage-deep);
  padding-bottom:2.5mm;
  margin-bottom:4mm;
  border-bottom:1px solid var(--sage);
}

.ing{list-style:none;}
.ing li{
  display:flex;
  align-items:baseline;
  gap:1.5mm;
  padding:1.7mm 0;
}
.ing .item{
  font-family:'Brand Serif',serif;
  font-size:11.5pt;
  color:var(--ink);
  white-space:nowrap;
}
.ing .dots{
  flex:1;
  border-bottom:1px dotted var(--sage-soft);
  transform:translateY(-1mm);
}
.ing .qty{
  font-family:'Brand Sans',sans-serif;
  font-weight:400;
  font-size:7.6pt;
  letter-spacing:.06em;
  color:var(--sage-deep);
  white-space:nowrap;
}

.serves{
  margin-top:5mm;
  padding-top:3.5mm;
  border-top:1px solid var(--sage-soft);
  font-size:6.6pt;
  color:var(--sage);
}

.method{list-style:none;counter-reset:step;}
.method li{
  counter-increment:step;
  position:relative;
  padding-left:9mm;
  padding-bottom:4.2mm;
  font-family:'Brand Serif',serif;
  font-size:11.5pt;
  line-height:1.5;
  color:var(--ink);
}
.method li::before{
  content:counter(step,decimal-leading-zero);
  position:absolute;
  left:0;
  top:.5mm;
  font-family:'Brand Sans',sans-serif;
  font-size:7pt;
  letter-spacing:.08em;
  color:var(--sage);
}

.note{
  margin-top:auto;
  padding-top:4mm;
  border-top:1px solid var(--sage-soft);
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:9.5pt;
  line-height:1.5;
  color:var(--ink-soft);
}

.drink-foot{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-top:7mm;
  padding-top:3.5mm;
  border-top:1px solid var(--sage-soft);
  font-size:6.4pt;
  color:var(--sage-deep);
}
.drink-foot .mark{
  font-family:'Brand Script',cursive;
  font-size:15pt;
  letter-spacing:0;
  text-transform:none;
  color:var(--sage);
  line-height:1;
}

/* ---------- expandable end card ---------- */

.endcard{
  padding:14mm;
  text-align:center;
}
.endcard-inner{
  flex:1;
  border:1px solid var(--sage-soft);
  padding:20mm 16mm;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
}
.endcard .endcard-mark{
  position:absolute;
  left:0;
  right:0;
  bottom:24mm;
  font-size:6.4pt;
  color:var(--sage-deep);
}
.endcard .script{font-size:46pt;color:var(--sage-deep);margin-bottom:7mm;}
.endcard .body{
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:13.5pt;
  line-height:1.65;
  color:var(--ink-soft);
  max-width:118mm;
  margin:0 auto 9mm;
  text-wrap:balance;
}
.endcard .rule{width:88mm;margin:0 auto;}
.endcard .slots{
  display:flex;
  gap:6mm;
  justify-content:center;
  width:100%;
  max-width:132mm;
  margin:10mm auto 0;
}
.endcard .slot{
  flex:1;
  height:34mm;
  border:1px dashed var(--sage-soft);
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:5.6pt;
  letter-spacing:.2em;
  color:var(--sage);
}
"""


# --------------------------------------------------------------------------
# page builders
# --------------------------------------------------------------------------

def build_cover(brand, sections, logo, page_map) -> str:
    if logo:
        lockup = f'<img class="lockup-logo" src="{data_uri(logo)}" alt="">'
    else:
        lockup = (
            f'<div class="script">{escape(brand["scriptName"])}</div>'
            f'<div class="on-ice">{escape(brand["serifName"])}</div>'
        )

    blocks = []
    for section in sections:
        rows = []
        for index, drink in enumerate(section["drinks"], start=1):
            page = page_map.get(id(drink))
            pending = " pending" if section.get("expandable") else ""
            rows.append(
                f'<li class="index-row{pending}">'
                f'<span class="no">{index:02d}</span>'
                f'<span class="name">{escape(drink["name"])}</span>'
                f'<span class="dots"></span>'
                f'<span class="pg">{page}</span>'
                "</li>"
            )
        if section.get("expandable"):
            rows.append(
                '<li class="index-row pending">'
                '<span class="no">&mdash;</span>'
                '<span class="name">More to come each season</span>'
                '<span class="dots"></span>'
                '<span class="pg">&nbsp;</span>'
                "</li>"
            )
        count = len(section["drinks"])
        count_label = "Open chapter" if section.get("expandable") else f"{count} drinks"
        blocks.append(
            '<div class="index-block">'
            '<div class="index-block-head">'
            f'<span class="index-numeral">{escape(section["numeral"])}</span>'
            f'<span class="caps label">{escape(section["label"])}</span>'
            f'<span class="count">{escape(count_label)}</span>'
            "</div>"
            f'<ul class="index-list">{"".join(rows)}</ul>'
            "</div>"
        )

    return f"""
<section class="page cover">
  <div class="cover-frame">
    <div class="lockup">
      {lockup}
      <div class="lockup-bar"><i></i><span class="caps">{escape(brand["capsName"])}</span><i></i></div>
    </div>
    <div class="cover-meta">
      <div class="tagline">{escape(brand["tagline"])}</div>
      <div class="caps edition">{escape(brand["edition"])} &nbsp;&middot;&nbsp; {escape(brand["year"])}</div>
    </div>
    <div class="index">{"".join(blocks)}</div>
    <div class="cover-foot">
      <span class="caps">Contents</span>
      <span class="caps">{escape(brand["footer"])}</span>
    </div>
  </div>
</section>
"""


def build_divider(section, brand) -> str:
    return f"""
<section class="page divider">
  <div class="divider-inner">
    <div class="numeral">{escape(section["numeral"])}</div>
    <div class="script">{escape(section["label"])}</div>
    <div class="blurb">{escape(section["blurb"])}</div>
    <div class="caps divider-mark">{escape(brand["footer"])}</div>
  </div>
</section>
"""


def build_shot(drink) -> str:
    photo = find_photo(drink.get("photo"))
    if photo:
        inner = f'<img src="{data_uri(photo)}" alt="{escape(drink["name"])}">'
    else:
        variant = " cream" if drink.get("placeholder") == "cream" else ""
        inner = (
            f'<div class="shot-placeholder{variant}">'
            f'<div class="script">{escape(drink["name"])}</div>'
            '<div class="flourish"></div>'
            '<div class="caps stamp">Photography to follow</div>'
            "</div>"
        )
    return (
        '<div class="shot">'
        '<div class="shot-keyline"></div>'
        f'<div class="shot-inner">{inner}</div>'
        "</div>"
    )


def build_drink(drink, section, brand, defaults, number, page_no) -> str:
    ingredients = drink.get("ingredients") or defaults["ingredients"]
    method = drink.get("method") or defaults["method"]
    serves = drink.get("serves") or defaults["serves"]
    note = drink.get("note") or defaults["notes"]

    ing_html = "".join(
        '<li>'
        f'<span class="item">{escape(row["item"])}</span>'
        '<span class="dots"></span>'
        f'<span class="qty">{escape(row["qty"])}</span>'
        "</li>"
        for row in ingredients
    )
    method_html = "".join(f"<li>{escape(step)}</li>" for step in method)

    singular = section["label"].rstrip("s") if section["label"].endswith("s") else section["label"]

    return f"""
<section class="page drink">
  <div class="drink-head">
    <span class="caps">{escape(section["label"])}</span>
    <span class="caps">{escape(section["numeral"])} &middot; {number:02d}</span>
  </div>
  <div class="drink-title">
    <span class="caps eyebrow">{escape(singular)} No. {number:02d}</span>
    <div class="script">{escape(drink["name"])}</div>
  </div>
  {build_shot(drink)}
  <div class="recipe">
    <div class="col-ingredients">
      <div class="caps col-label">Ingredients</div>
      <ul class="ing">{ing_html}</ul>
      <div class="caps serves">{escape(serves)}</div>
    </div>
    <div class="col-method">
      <div class="caps col-label">Method</div>
      <ol class="method">{method_html}</ol>
      <div class="note">{escape(note)}</div>
    </div>
  </div>
  <div class="drink-foot">
    <span class="mark">{escape(brand["scriptName"])}</span>
    <span class="caps">{escape(brand["footer"])}</span>
    <span class="caps">Page {page_no}</span>
  </div>
</section>
"""


def build_endcard(brand) -> str:
    slots = "".join(
        '<div class="slot">Next drink</div>' for _ in range(3)
    )
    return f"""
<section class="page endcard">
  <div class="endcard-inner">
    <div class="script">More to come</div>
    <div class="body">
      This chapter stays open. New seasonal drinks take their place here as they
      launch, each with its own page in the catalogue.
    </div>
    <hr class="rule">
    <div class="slots">{slots}</div>
  </div>
  <div class="caps endcard-mark">{escape(brand["footer"])}</div>
</section>
"""


# --------------------------------------------------------------------------
# document
# --------------------------------------------------------------------------

def build_document(catalog) -> str:
    brand = catalog["brand"]
    sections = catalog["sections"]
    defaults = catalog["placeholders"]
    logo = find_logo()

    # Pass 1 — assign page numbers (cover = 1, then divider + drink pages).
    page_map = {}
    page_no = 2
    for section in sections:
        page_no += 1  # divider
        for drink in section["drinks"]:
            page_map[id(drink)] = page_no
            page_no += 1
        if section.get("expandable"):
            page_no += 1  # end card

    # Pass 2 — render.
    pages = [build_cover(brand, sections, logo, page_map)]
    for section in sections:
        pages.append(build_divider(section, brand))
        for number, drink in enumerate(section["drinks"], start=1):
            pages.append(
                build_drink(drink, section, brand, defaults, number, page_map[id(drink)])
            )
        if section.get("expandable"):
            pages.append(build_endcard(brand))

    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(catalog['documentTitle'])}</title>"
        f"<style>{stylesheet()}</style>"
        "</head><body>"
        + "".join(pages)
        + "</body></html>\n"
    )


# --------------------------------------------------------------------------
# pdf
# --------------------------------------------------------------------------

def find_chromium() -> str:
    candidates = [
        "/opt/pw-browsers/chromium/chrome-linux/chrome",
        "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
        "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("chromium not found")


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = find_chromium()
    subprocess.run(
        [
            chrome,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--generate-pdf-document-outline=false",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    catalog = json.loads(DATA.read_text(encoding="utf-8"))
    DIST.mkdir(parents=True, exist_ok=True)

    HTML_OUT.write_text(build_document(catalog), encoding="utf-8")
    print(f"html  -> {HTML_OUT.relative_to(ROOT)}  ({HTML_OUT.stat().st_size // 1024} KB)")

    if "--html" in sys.argv:
        return

    render_pdf(HTML_OUT, PDF_OUT)
    print(f"pdf   -> {PDF_OUT.relative_to(ROOT)}  ({PDF_OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
