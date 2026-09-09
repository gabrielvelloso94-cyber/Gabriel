#!/usr/bin/env python3
"""Shared brand system for Matcha On Ice Cafe documents.

Every document (the matcha catalogue, the syrups & cold foam manual, and
whatever follows — a coffee bar manual, etc.) shares one visual language:
same fonts, same palette, same cover/divider/page furniture. This module
holds that shared system so each document's build script only has to state
its own content (a JSON file) and output paths — see build/generate.py and
build/generate_syrups.py for the thin per-document wrappers.

Section shapes a document's JSON can use:
    (default)     a plain list of drinks/items, one full page each
    "expandable"  same, plus an "Open chapter" cover-index label, a
                  trailing "More to come each season" filler row (only
                  that row is styled as pending — real items still read
                  as finished content), and a closing "More to come"
                  card (see build_endcard)
    "foundation"  two fixed pages — a story/explanation page and a
                  proportions/recipe page — for chapters that are reference
                  content rather than a list of items (e.g. The Matcha Base)
    "simple"      one plain recipe (ingredients + method, no photo, no
                  size split) per item — for straightforward build
                  components like syrups
"""

import base64
import mimetypes
import shutil
import subprocess
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
PHOTOS = ROOT / "assets" / "photos"
BRAND = ROOT / "assets" / "brand"

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


def brand_mark(stem: str, colour: str) -> Path | None:
    """Resolve a logo mark produced by build/extract_logo.py.

    `stem` is one of logo-lockup / logo-wordmark / logo-script; `colour` is
    sage (for cream backgrounds) or cream (for sage backgrounds).
    """
    path = BRAND / f"{stem}-{colour}.png"
    return path if path.exists() else None


def mark_img(stem: str, colour: str, css_class: str) -> str:
    mark = brand_mark(stem, colour)
    if not mark:
        return ""
    return f'<img class="{css_class}" src="{data_uri(mark)}" alt="Matcha On Ice Cafe">'


# --------------------------------------------------------------------------
# stylesheet
# --------------------------------------------------------------------------

def stylesheet() -> str:
    # Pinyon Script matches the high-contrast roundhand of the logo's "Matcha"; Playfair
    # Display matches the Didone of its "On Ice"; Jost matches its spaced "CAFE".
    faces = "".join([
        font_face("Brand Script", "PinyonScript-Regular.ttf", "400"),
        font_face("Brand Serif", "PlayfairDisplay-Variable.ttf", "400 700"),
        font_face("Brand Serif", "PlayfairDisplay-Italic-Variable.ttf", "400 700", "italic"),
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

.lockup{text-align:center;padding-top:7mm;}
.lockup-logo{width:122mm;margin:0 auto;display:block;}

/* fallback only — used if the extracted logo artwork is missing */
.lockup .script{font-size:56pt;color:var(--sage-deep);margin-bottom:-3mm;}
.lockup .on-ice{
  font-family:'Brand Serif',serif;
  font-weight:500;
  font-size:26pt;
  color:var(--ink);
}
.lockup-bar{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:5mm;
  margin-top:4mm;
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
  font-size:13pt;
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
  font-size:9pt;
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
  font-size:8.5pt;
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
  font-size:11.5pt;
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
  font-size:52pt;
  margin:7mm 0 9mm;
  color:var(--cream);
}
.divider .blurb{
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:11.5pt;
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
.divider-logo{width:46mm;margin:0 auto;display:block;}

/* ---------- drink / recipe page ---------- */

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

.drink-title{text-align:center;padding:6mm 0 5mm;}
.drink-title .eyebrow{
  font-size:6.8pt;
  color:var(--sage);
  display:block;
  margin-bottom:3.5mm;
}
.drink-title .script{
  font-size:44pt;
  color:var(--sage-deep);
  padding:0 4mm;
}

/* photo / placeholder block */

.shot{
  position:relative;
  width:83mm;
  height:90mm;
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
  font-size:31pt;
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

/* recipe */

.recipe{
  flex:1;
  display:flex;
  flex-direction:column;
  padding-top:6mm;
  margin-top:5mm;
  border-top:1px solid var(--sage-soft);
  min-height:0;
  overflow:hidden;
}
.measures{flex:0 0 auto;margin-bottom:5mm;}
.col-method{flex:1;min-height:0;display:flex;flex-direction:column;}

.col-label{
  display:block;
  font-size:7pt;
  color:var(--sage-deep);
  padding-bottom:2.5mm;
  margin-bottom:4mm;
  border-bottom:1px solid var(--sage);
}

.ing-head{
  display:flex;
  align-items:baseline;
  justify-content:space-between;
  padding-bottom:2.5mm;
  margin-bottom:4mm;
  border-bottom:1px solid var(--sage);
}
.ing-head .col-label{padding:0;margin:0;border:0;}
.ing-sizes{display:flex;gap:3mm;}
.ing-sizes span{
  font-family:'Brand Sans',sans-serif;
  font-weight:400;
  font-size:6.2pt;
  letter-spacing:.1em;
  color:var(--sage);
  width:14mm;
  text-align:right;
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
  font-size:10.5pt;
  color:var(--ink);
  white-space:nowrap;
}
.ing .dots{
  flex:1;
  min-width:4mm;
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
  width:14mm;
  flex-shrink:0;
  text-align:right;
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
  padding-bottom:2.4mm;
  font-family:'Brand Serif',serif;
  font-size:10.5pt;
  line-height:1.4;
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

.method-split{display:flex;flex-direction:row;gap:6mm;}
.method-split .method-col{flex:1;min-width:0;}
.method-split .method li{
  font-size:9pt;
  line-height:1.32;
  padding-left:7mm;
  padding-bottom:1.8mm;
}
.method-split .method li::before{font-size:6pt;}

.note{
  margin-top:auto;
  padding-top:3mm;
  border-top:1px solid var(--sage-soft);
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:8.8pt;
  line-height:1.5;
  color:var(--ink-soft);
}

/* ---------- foundation / simple pages (no photo, reference content) ---------- */

.foundation .drink-title{padding-top:8mm;padding-bottom:9mm;}

.story-body{
  flex:1;
  display:flex;
  flex-direction:column;
  min-height:0;
  overflow:hidden;
}

.foundation-copy{
  max-width:132mm;
  margin:0 auto;
  width:100%;
}

.foundation-recipe-body{max-width:132mm;margin:0 auto;width:100%;}
.foundation-method{margin-top:2mm;}
.foundation-copy p{
  font-family:'Brand Serif',serif;
  font-size:10.5pt;
  line-height:1.6;
  color:var(--ink);
  margin-bottom:5mm;
  text-align:left;
}
.foundation-copy p:last-child{margin-bottom:0;}

.callout{
  max-width:132mm;
  margin:10mm auto 0;
  padding-top:7mm;
  border-top:1px solid var(--sage-soft);
  text-align:center;
}
.callout-value{
  font-family:'Brand Serif',serif;
  font-weight:600;
  font-size:19pt;
  color:var(--sage-deep);
  margin:3mm 0;
}
.callout-sub{
  font-family:'Brand Sans',sans-serif;
  font-weight:400;
  font-size:9pt;
  color:var(--sage);
  letter-spacing:.04em;
}
.callout-note{
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:8.8pt;
  line-height:1.5;
  color:var(--ink-soft);
  max-width:108mm;
  margin:2mm auto 0;
}

.ing-batch .qty-single{
  font-family:'Brand Sans',sans-serif;
  font-weight:400;
  font-size:7.6pt;
  letter-spacing:.06em;
  color:var(--sage-deep);
  white-space:nowrap;
}
.ing-batch .qty-single i{
  font-style:italic;
  font-weight:400;
  color:var(--sage);
  margin-left:2mm;
  font-size:6.6pt;
  letter-spacing:0;
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
.drink-foot .mark{height:6mm;display:block;opacity:.85;}
.drink-foot .mark-text{
  font-family:'Brand Script',cursive;
  font-size:15pt;
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
.endcard-logo{width:44mm;margin:0 auto;display:block;opacity:.9;}
.endcard .script{font-size:42pt;color:var(--sage-deep);margin-bottom:7mm;}
.endcard .body{
  font-family:'Brand Serif',serif;
  font-style:italic;
  font-size:11.5pt;
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

def build_cover(brand, sections, page_map) -> str:
    lockup = mark_img("logo-lockup", "sage", "lockup-logo")
    if not lockup:
        lockup = (
            f'<div class="script">{escape(brand["scriptName"])}</div>'
            f'<div class="on-ice">{escape(brand["serifName"])}</div>'
            f'<div class="lockup-bar"><i></i>'
            f'<span class="caps">{escape(brand["capsName"])}</span><i></i></div>'
        )

    blocks = []
    for section in sections:
        rows = []
        for index, drink in enumerate(section["drinks"], start=1):
            page = page_map.get(id(drink))
            rows.append(
                f'<li class="index-row">'
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
        if section.get("expandable"):
            count_label = "Open chapter"
        elif section.get("kind") in ("foundation", "simple"):
            count_label = f"{count} pages"
        else:
            count_label = f"{count} drinks"
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
    <div class="lockup">{lockup}</div>
    <div class="cover-meta">
      <div class="tagline">{escape(brand["tagline"])}</div>
      <div class="caps edition">{escape(brand["year"])}</div>
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
    <div class="divider-mark">
      {mark_img("logo-wordmark", "cream", "divider-logo")
       or f'<span class="caps">{escape(brand["footer"])}</span>'}
    </div>
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
    # Measures are the few things worth calling out precisely (matcha, syrup,
    # espresso shot) — a section-wide default (e.g. every matcha uses the same
    # matcha pour) plus whatever this drink adds on top (e.g. its syrup).
    # Ice, milk and cold foam aren't measured, so they live in the Method text
    # instead of a fabricated "to taste" ingredients row.
    measures = [*section.get("defaultMeasures", []), *drink.get("measures", [])]
    method_hot = drink.get("methodHot") or section.get("defaultMethodHot")
    method_iced = drink.get("methodIced") or section.get("defaultMethodIced")
    method = drink.get("method") or section.get("defaultMethod") or defaults["method"]
    serves = drink.get("serves", defaults.get("serves", ""))
    note = drink.get("note")  # no fallback: an unfinished note would read as real copy

    measures_block = ""
    if measures:
        rows = "".join(
            '<li>'
            f'<span class="item">{escape(row["item"])}</span>'
            '<span class="dots"></span>'
            f'<span class="qty">{escape(row["qty12"])}</span>'
            f'<span class="qty">{escape(row["qty16"])}</span>'
            "</li>"
            for row in measures
        )
        serves_html = f'<div class="caps serves">{escape(serves)}</div>' if serves else ""
        measures_block = f"""
    <div class="measures">
      <div class="ing-head">
        <span class="caps col-label">Measures</span>
        <span class="ing-sizes"><span>12 oz</span><span>16 oz</span></span>
      </div>
      <ul class="ing">{rows}</ul>
      {serves_html}
    </div>"""

    note_html = f'<div class="note">{escape(note)}</div>' if note else ""

    if method_hot and method_iced:
        hot_html = "".join(f"<li>{escape(step)}</li>" for step in method_hot)
        iced_html = "".join(f"<li>{escape(step)}</li>" for step in method_iced)
        method_section = f"""
    <div class="col-method method-split">
      <div class="method-col">
        <div class="caps col-label">Method &mdash; Hot</div>
        <ol class="method">{hot_html}</ol>
      </div>
      <div class="method-col">
        <div class="caps col-label">Method &mdash; Iced</div>
        <ol class="method">{iced_html}</ol>
      </div>
    </div>
    {note_html}"""
    else:
        method_html = "".join(f"<li>{escape(step)}</li>" for step in method)
        method_section = f"""
    <div class="col-method">
      <div class="caps col-label">Method</div>
      <ol class="method">{method_html}</ol>
      {note_html}
    </div>"""

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
  <div class="recipe">{measures_block}{method_section}
  </div>
  <div class="drink-foot">
    {mark_img("logo-script", "sage", "mark") or f'<span class="mark-text script">{escape(brand["scriptName"])}</span>'}
    <span class="caps">{escape(brand["footer"])}</span>
    <span class="caps">Page {page_no}</span>
  </div>
</section>
"""


def build_simple_recipe(item, section, brand, number, page_no) -> str:
    """A plain recipe page: name, one spec/ingredients list, method. No
    photo — for build components (syrups), drink spec sheets (espresso
    classics), or reference items (barista tools). The list is one
    quantity column by default, or sized 12oz/16oz columns when the item
    sets "sized": true. A section can override the two column headings
    (default "Ingredients" / "Method") via specLabel / methodLabel — e.g.
    "Specs" / "Use" for a tools reference rather than a recipe."""
    ingredients = item.get("ingredients", [])
    method = item["method"]
    yield_ = item.get("yield", "")
    note = item.get("note")
    spec_label = section.get("specLabel", "Ingredients")
    method_label = section.get("methodLabel", "Method")

    block_html = _measure_block_html({
        "type": "sized" if item.get("sized") else "single",
        "label": spec_label,
        "rows": ingredients,
    })
    yield_html = f'<div class="caps serves">{escape(yield_)}</div>' if yield_ else ""
    method_html = "".join(f"<li>{escape(step)}</li>" for step in method)
    note_html = f'<p class="note" style="margin-top:6mm;">{escape(note)}</p>' if note else ""

    singular = section["label"].rstrip("s") if section["label"].endswith("s") else section["label"]

    return f"""
<section class="page drink foundation">
  <div class="drink-head">
    <span class="caps">{escape(section["label"])}</span>
    <span class="caps">{escape(section["numeral"])} &middot; {number:02d}</span>
  </div>
  <div class="drink-title">
    <span class="caps eyebrow">{escape(singular)} No. {number:02d}</span>
    <div class="script">{escape(item["name"])}</div>
  </div>
  <div class="story-body">
    <div class="foundation-recipe-body">{block_html}
      {yield_html}
      <div class="foundation-method">
        <div class="caps col-label">{escape(method_label)}</div>
        <ol class="method">{method_html}</ol>
      </div>
      {note_html}
    </div>
  </div>
  <div class="drink-foot">
    {mark_img("logo-script", "sage", "mark") or f'<span class="mark-text script">{escape(brand["scriptName"])}</span>'}
    <span class="caps">{escape(brand["footer"])}</span>
    <span class="caps">Page {page_no}</span>
  </div>
</section>
"""


def build_foundation_story(section, brand, page_no) -> str:
    story = section["story"]
    callout = story.get("callout")
    body_html = "".join(f"<p>{escape(p)}</p>" for p in story["body"])

    callout_html = ""
    if callout:
        callout_html = f"""
    <div class="callout">
      <span class="caps col-label">{escape(callout["label"])}</span>
      <div class="callout-value">{escape(callout["range"])} <span class="callout-sub">({escape(callout["sub"])})</span></div>
      <p class="callout-note">{escape(callout["note"])}</p>
    </div>"""

    return f"""
<section class="page drink foundation">
  <div class="drink-head">
    <span class="caps">{escape(section["label"])}</span>
    <span class="caps">{escape(section["numeral"])} &middot; {escape(story.get("shortLabel", "Story"))}</span>
  </div>
  <div class="drink-title">
    <span class="caps eyebrow">{escape(story["eyebrow"])}</span>
    <div class="script">{escape(story["heading"])}</div>
  </div>
  <div class="story-body">
    <div class="foundation-copy">{body_html}</div>{callout_html}
  </div>
  <div class="drink-foot">
    {mark_img("logo-script", "sage", "mark") or f'<span class="mark-text script">{escape(brand["scriptName"])}</span>'}
    <span class="caps">{escape(brand["footer"])}</span>
    <span class="caps">Page {page_no}</span>
  </div>
</section>
"""


def _measure_block_html(block: dict) -> str:
    """One .measures block: "sized" (12oz/16oz columns) or "single" (one qty)."""
    if block["type"] == "sized":
        rows = "".join(
            '<li>'
            f'<span class="item">{escape(row["item"])}</span>'
            '<span class="dots"></span>'
            f'<span class="qty">{escape(row["qty12"])}</span>'
            f'<span class="qty">{escape(row["qty16"])}</span>'
            "</li>"
            for row in block["rows"]
        )
        return f"""
      <div class="measures">
        <div class="ing-head">
          <span class="caps col-label">{escape(block["label"])}</span>
          <span class="ing-sizes"><span>12 oz</span><span>16 oz</span></span>
        </div>
        <ul class="ing">{rows}</ul>
      </div>"""

    rows = "".join(
        '<li>'
        f'<span class="item">{escape(row["item"])}</span>'
        '<span class="dots"></span>'
        f'<span class="qty-single">{escape(row["qty"])}'
        + (f' <i>{escape(row["note"])}</i>' if row.get("note") else "")
        + "</span></li>"
        for row in block["rows"]
    )
    return f"""
      <div class="measures">
        <span class="caps col-label">{escape(block["label"])}</span>
        <ul class="ing ing-batch">{rows}</ul>
      </div>"""


def build_foundation_recipes(section, brand, page_no) -> str:
    page = section.get("recipesPage", {})
    blocks_html = "".join(_measure_block_html(block) for block in section["measureBlocks"])
    method_html = "".join(f"<li>{escape(step)}</li>" for step in section["method"])

    return f"""
<section class="page drink foundation">
  <div class="drink-head">
    <span class="caps">{escape(section["label"])}</span>
    <span class="caps">{escape(section["numeral"])} &middot; {escape(page.get("shortLabel", "Recipe"))}</span>
  </div>
  <div class="drink-title">
    <span class="caps eyebrow">{escape(section["label"])}</span>
    <div class="script">{escape(page.get("heading", "Recipe"))}</div>
  </div>
  <div class="story-body">
    <div class="foundation-recipe-body">{blocks_html}
      <div class="foundation-method">
        <div class="caps col-label">Method</div>
        <ol class="method">{method_html}</ol>
      </div>
    </div>
  </div>
  <div class="drink-foot">
    {mark_img("logo-script", "sage", "mark") or f'<span class="mark-text script">{escape(brand["scriptName"])}</span>'}
    <span class="caps">{escape(brand["footer"])}</span>
    <span class="caps">Page {page_no}</span>
  </div>
</section>
"""


def build_endcard(brand, slot_label="Next drink", body=None) -> str:
    slots = "".join(
        f'<div class="slot">{escape(slot_label)}</div>' for _ in range(3)
    )
    body = body or (
        "This chapter stays open. New seasonal drinks take their place here as they "
        "launch, each with its own page in the catalogue."
    )
    return f"""
<section class="page endcard">
  <div class="endcard-inner">
    <div class="script">More to come</div>
    <div class="body">
      {escape(body)}
    </div>
    <hr class="rule">
    <div class="slots">{slots}</div>
  </div>
  <div class="endcard-mark">
    {mark_img("logo-wordmark", "sage", "endcard-logo")
     or f'<span class="caps">{escape(brand["footer"])}</span>'}
  </div>
</section>
"""


# --------------------------------------------------------------------------
# document
# --------------------------------------------------------------------------

def build_document(catalog) -> str:
    brand = catalog["brand"]
    sections = catalog["sections"]
    defaults = catalog.get("placeholders", {})

    # Pass 1 — assign page numbers (cover = 1, then divider + item pages).
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
    pages = [build_cover(brand, sections, page_map)]
    for section in sections:
        pages.append(build_divider(section, brand))
        kind = section.get("kind")
        if kind == "foundation":
            story_page, recipes_page = section["drinks"]
            pages.append(build_foundation_story(section, brand, page_map[id(story_page)]))
            pages.append(build_foundation_recipes(section, brand, page_map[id(recipes_page)]))
        elif kind == "simple":
            for number, item in enumerate(section["drinks"], start=1):
                pages.append(build_simple_recipe(item, section, brand, number, page_map[id(item)]))
        else:
            for number, drink in enumerate(section["drinks"], start=1):
                pages.append(
                    build_drink(drink, section, brand, defaults, number, page_map[id(drink)])
                )
        if section.get("expandable"):
            pages.append(build_endcard(
                brand,
                slot_label=section.get("endcardSlotLabel", "Next drink"),
                body=section.get("endcardBody"),
            ))

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


def build(data_path: Path, html_out: Path, pdf_out: Path, html_only: bool = False) -> None:
    import json

    catalog = json.loads(data_path.read_text(encoding="utf-8"))
    html_out.parent.mkdir(parents=True, exist_ok=True)

    html_out.write_text(build_document(catalog), encoding="utf-8")
    print(f"html  -> {html_out.relative_to(ROOT)}  ({html_out.stat().st_size // 1024} KB)")

    if html_only:
        return

    render_pdf(html_out, pdf_out)
    print(f"pdf   -> {pdf_out.relative_to(ROOT)}  ({pdf_out.stat().st_size // 1024} KB)")
