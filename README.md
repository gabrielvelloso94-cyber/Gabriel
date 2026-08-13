# Matcha On Ice Cafe — Drink Catalogue

A4 portrait catalogue / technical-sheet PDF for Matcha On Ice Cafe.

**Output:** [`dist/Matcha-On-Ice-Cafe-Catalog.pdf`](dist/Matcha-On-Ice-Cafe-Catalog.pdf) — 16 pages.

> **Status: in progress.** Signature Matchas are filled in with real measures and method.
> Signature Coffees and Seasonal Add-Ons are still placeholder, pending their recipes.

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
| Serif | Playfair Display | Measures, method steps, blurbs, index |
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
The block is portrait (87 × 94 mm) and images are cropped to fill, so **shoot vertical**.

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

There's no ingredients table. Things like ice, milk and cold foam aren't measured — they're
assembly steps, not a quantity — so they live in the Method text. **Measures** is reserved
for the few things worth calling out precisely: matcha, syrup, an espresso shot.

```json
{
  "name": "Pumpkin Spice Matcha",
  "photo": "pumpkin-spice-matcha.jpg",
  "measures": [
    { "item": "Pumpkin Spice Syrup", "qty12": "1 oz", "qty16": "1.5 oz" }
  ],
  "method": [
    "Fill the cup with ice.",
    "Weigh or measure the syrup for the cup size.",
    "Pour milk to about three-fifths of the cup, leaving room for the matcha and cold foam.",
    "Spoon the matcha over the milk.",
    "Top with cold foam, if requested.",
    "Garnish and serve."
  ],
  "note": "Barista note — keep the syrup under the ice line."
}
```

A drink's Measures list is its section's `defaultMeasures` (a section-wide constant, e.g.
every Signature Matcha pours the same matcha) followed by whatever the drink adds on top
(e.g. its syrup) — see `signature-matchas` and `signature-coffees` in `catalog.json`. A
drink with no syrup (Coconut Cloud) just omits `measures`, and one whose method departs
from the section's `defaultMethod` overrides it in full, the way Coconut Cloud drops the
syrup step. `serves` and `note` are optional; a missing `note` renders no note at all
rather than filler text, since a placeholder note would read as real copy in a finished
page.

The **Seasonal Add-Ons** section is marked `"expandable": true`, which gives it the
"Open chapter" index treatment and the closing card. New seasonal drinks are just new
entries in its `drinks` array.
