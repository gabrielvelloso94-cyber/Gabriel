# Matcha On Ice Cafe — Drink Catalogue

A4 portrait catalogue / technical-sheet PDF for Matcha On Ice Cafe.

**Output:** [`dist/Matcha-On-Ice-Cafe-Catalog.pdf`](dist/Matcha-On-Ice-Cafe-Catalog.pdf) — 16 pages.

> **Status: layout test.** Ingredients and method steps are placeholder text on every
> drink page, for validating typography, colour and layout before the real recipes go in.

## Build

```bash
python3 build/generate.py          # writes dist/catalog.html + the PDF
python3 build/generate.py --html   # HTML only
```

Requires Python 3 and headless Chromium (auto-detected from `/opt/pw-browsers` or `PATH`).
No third-party Python packages. Fonts are embedded into the HTML, so `dist/catalog.html`
is self-contained and can be opened or shared on its own.

## Structure

| Path | What it is |
| --- | --- |
| `data/catalog.json` | All content — brand strings, sections, drinks, placeholder text |
| `build/generate.py` | Renders the HTML and prints it to PDF |
| `assets/fonts/` | Embedded brand fonts (SIL Open Font License, texts included) |
| `assets/photos/` | Drink photography — drop files here |
| `assets/brand/` | Optional `logo.png` / `logo.svg` for the cover |
| `dist/` | Generated `catalog.html` and the PDF |

Pages: cover with the 3-block index → section divider + one page per drink, per section →
a closing "More to come" card at the end of Seasonal Add-Ons.

## Brand system

| Role | Face | Used for |
| --- | --- | --- |
| Script | Allura | Brand name, drink names, placeholder blocks, footer mark |
| Serif | Cormorant Garamond | "ON ICE", ingredients, method steps, blurbs |
| Caps | Jost, letterspaced | "CAFE", category labels, step numbers, page furniture |

| Token | Hex | Role |
| --- | --- | --- |
| `--sage` | `#8a9b6e` | Primary — dividers, placeholder blocks |
| `--sage-deep` | `#5d6b45` | Drink names, headings |
| `--sage-soft` | `#b6c19d` | Hairlines, keylines, dot leaders |
| `--cream` | `#f6f2e8` | Page background (off-white, not pure white) |
| `--ink` | `#2f3328` | Body text |

## Adding photos

Drop the image into `assets/photos/` and rebuild. Filenames are already reserved per drink
in `data/catalog.json` (`matcha-on-ice.jpg`, `mango-matcha.jpg`, …); the extension in the
JSON does not have to match the file on disk — `.jpg`, `.jpeg`, `.png`, `.webp` and `.avif`
all resolve by name.

Any drink without a photo falls back to a solid sage block with its name set in the brand
script, so the catalogue stays visually consistent while photography is outstanding.
The block is portrait (116 × 124 mm) and images are cropped to fill, so **shoot vertical**.

For the cover, add `assets/brand/logo.png` (or `.svg`) and it replaces the typographic
lockup automatically.

## Adding a drink

Add an entry to the relevant section in `data/catalog.json` and rebuild. Page numbers,
index rows and the "No. 0X" labels are all derived, so nothing else needs updating.

```json
{
  "name": "Pumpkin Spice Matcha",
  "photo": "pumpkin-spice-matcha.jpg",
  "ingredients": [
    { "item": "Ceremonial matcha", "qty": "2 tsp" },
    { "item": "Oat milk", "qty": "180 ml" }
  ],
  "method": [
    "Sift the matcha and whisk with hot water until smooth.",
    "Pour over ice and top with oat milk."
  ],
  "serves": "Serves 1  ·  16 oz",
  "note": "Barista note — keep the syrup under the ice line."
}
```

`ingredients`, `method`, `serves` and `note` are all optional — anything omitted falls back
to the placeholder text in `placeholders` at the bottom of `catalog.json`. That is what
every drink is using right now.

The **Seasonal Add-Ons** section is marked `"expandable": true`, which gives it the
"Open chapter" index treatment and the closing card. New seasonal drinks are just new
entries in its `drinks` array.
