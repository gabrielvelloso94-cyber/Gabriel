# Matcha On Ice Cafe — Drink Catalogue

A4 portrait catalogue / technical-sheet PDF for Matcha On Ice Cafe.

**Output:** [`dist/Matcha-On-Ice-Cafe-Catalog.pdf`](dist/Matcha-On-Ice-Cafe-Catalog.pdf) — 16 pages.

> **Status: layout test.** Ingredients and method steps are placeholder text on every
> drink page, for validating typography, colour and layout before the real recipes go in.
> Ingredients are quoted for two pour sizes, 12 oz and 16 oz.

## Build

```bash
python3 build/generate.py          # writes dist/catalog.html + the PDF
python3 build/generate.py --html   # HTML only
```

Requires Python 3 and headless Chromium (auto-detected from `/opt/pw-browsers` or `PATH`).
No third-party Python packages. Fonts and logo artwork are embedded into the HTML, so
`dist/catalog.html` is self-contained and can be opened or shared on its own.

`build/extract_logo.py` is a separate one-off step that re-derives the logo artwork from
`assets/brand/logo-source.jpeg`. It only needs rerunning if the logo itself changes, and
it is the only thing here that needs `numpy` and `Pillow`.

## Structure

| Path | What it is |
| --- | --- |
| `data/catalog.json` | All content — brand strings, sections, drinks, placeholder text |
| `build/generate.py` | Renders the HTML and prints it to PDF |
| `build/extract_logo.py` | Re-derives the logo artwork from the source file |
| `assets/fonts/` | Embedded brand fonts (SIL Open Font License, texts included) |
| `assets/photos/` | Drink photography — drop files here |
| `assets/brand/` | Source logo plus the transparent marks derived from it |
| `dist/` | Generated `catalog.html` and the PDF |

Pages: cover with the 3-block index → section divider + one page per drink, per section →
a closing "More to come" card at the end of Seasonal Add-Ons.

## Brand system

The wordmark itself is never re-typeset — every appearance of it in the catalogue is the
real logo artwork (see below). The three faces below are chosen to sit with it: Pinyon
Script for its high-contrast roundhand "Matcha", Playfair Display for the Didone of its
"On Ice", Jost for its spaced "CAFE".

| Role | Face | Used for |
| --- | --- | --- |
| Script | Pinyon Script | Drink names, section names, placeholder blocks |
| Serif | Playfair Display | Ingredients, method steps, blurbs, index |
| Caps | Jost, letterspaced | Category labels, step numbers, page furniture |

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

## The logo

The cover, the section dividers, the closing card and every drink-page footer use the
actual logo artwork rather than a typeset imitation, so the letterforms are exact.

`build/extract_logo.py` lifts the white artwork off the sage field in
`assets/brand/logo-source.jpeg` into transparent PNGs, in sage (for cream backgrounds) and
cream (for sage backgrounds):

| Mark | Contents | Used on |
| --- | --- | --- |
| `logo-lockup-*` | "Matcha On Ice" over "CAFE" | Cover |
| `logo-wordmark-*` | "Matcha On Ice" | Section dividers, closing card |
| `logo-script-*` | the "Matcha" script alone | Drink-page footers |

To swap in a new logo, replace `logo-source.jpeg`, rerun `python3 build/extract_logo.py`,
then rebuild. If the new file has different proportions, the two crop constants at the top
of that script (`SCRIPT_END_X`, `BAND_SPLIT_Y`) need remeasuring. If the marks are missing
altogether, the cover falls back to a typeset lockup.

## Adding a drink

Add an entry to the relevant section in `data/catalog.json` and rebuild. Page numbers,
index rows and the "No. 0X" labels are all derived, so nothing else needs updating.

```json
{
  "name": "Pumpkin Spice Matcha",
  "photo": "pumpkin-spice-matcha.jpg",
  "ingredients": [
    { "item": "Ceremonial matcha", "qty12": "1.5 tsp", "qty16": "2 tsp" },
    { "item": "Oat milk", "qty12": "140 ml", "qty16": "180 ml" }
  ],
  "method": [
    "Sift the matcha and whisk with hot water until smooth.",
    "Pour over ice and top with oat milk."
  ],
  "serves": "Serves 1",
  "note": "Barista note — keep the syrup under the ice line."
}
```

Every drink is served in two sizes, so each ingredient row carries two quantities —
`qty12` for the 12 oz pour, `qty16` for the 16 oz — printed as two right-aligned columns
under "12 OZ" / "16 OZ" headers. `ingredients`, `method`, `serves` and `note` are all
optional — anything omitted falls back to the placeholder text in `placeholders` at the
bottom of `catalog.json`. That is what every drink is using right now.

The **Seasonal Add-Ons** section is marked `"expandable": true`, which gives it the
"Open chapter" index treatment and the closing card. New seasonal drinks are just new
entries in its `drinks` array.
