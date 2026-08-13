# Matcha On Ice Cafe — Matcha Catalogue

A4 portrait catalogue / technical-sheet PDF for Matcha On Ice Cafe's matcha program: the
matcha base itself, then the Signature Matchas built on it.

**Output:** [`dist/Matcha-On-Ice-Cafe-Catalog.pdf`](dist/Matcha-On-Ice-Cafe-Catalog.pdf) — 14 pages.

> **Status: in progress.** The Matcha Base and Signature Matchas are filled in with real
> content. Seasonal Add-Ons is still a placeholder template, pending its first drink.

Signature Coffees split out of this document into a future **Coffee Bar Manual** (to
include the espresso classics too — cappuccino, latte, americano, etc.). Its
already-written content (the lattes, the espresso default measure) is seeded in
`data/coffee-bar-manual.json`, not yet wired into the generator.

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
| `data/catalog.json` | All content in this document — brand strings, sections, drinks |
| `data/coffee-bar-manual.json` | Seed content for the future Coffee Bar Manual (unused by the build) |
| `build/generate.py` | Renders the HTML and prints it to PDF |
| `build/extract_logo.py` | Re-derives the logo artwork from the source file |
| `assets/fonts/` | Embedded brand fonts (SIL Open Font License, texts included) |
| `assets/photos/` | Drink photography — drop files here |
| `assets/brand/` | Source logo plus the transparent marks derived from it |
| `dist/` | Generated `catalog.html` and the PDF |

Pages: cover with the 3-block index → section divider + its pages, per section → a closing
"More to come" card at the end of Seasonal Add-Ons. Two section shapes:
- **Drinks** (Signature Matchas, Seasonal Add-Ons) — divider, then one page per drink.
- **Foundation** (The Matcha Base) — divider, then two fixed pages: a sourcing/water-temperature
  page and a proportions/batch/method page. See `build_foundation_story` /
  `build_foundation_recipes` in `build/generate.py`.

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

A drink's Measures list is its section's `defaultMeasures` (a section-wide constant — every
Signature Matcha pours the same matcha) followed by whatever the drink adds on top (its
syrup) — see `signature-matchas` in `catalog.json`. A drink with no syrup (Coconut Cloud)
just omits `measures`, and one whose method departs from the section's `defaultMethod`
overrides it in full, the way Coconut Cloud drops the syrup step and Double Matcha's cold
foam step is mandatory rather than optional. `serves` and `note` are optional; a missing
`note` renders no note at all rather than filler text, since a placeholder note would read
as real copy in a finished page.

The **Seasonal Add-Ons** section is marked `"expandable": true`, which gives it the
"Open chapter" index treatment and the closing card. New seasonal drinks are just new
entries in its `drinks` array.

## The Matcha Base

Unlike the other two sections, `matcha-base` is marked `"kind": "foundation"` — it isn't a
list of drinks, it's the sourcing story, the water-temperature guidance, and the ratios
(individual and event-batch) every Signature Matcha is built from. Its two pages are fixed
rather than data-driven per entry (there's no "add a foundation page" the way there's "add a
drink"), so its content lives directly on the section object: `story` (the sourcing copy and
water-temperature callout), `individual` and `batch` (both rendered with the same `.ing`
measures-row styling drink pages use), and `method`. To change any of it, edit those keys in
`catalog.json` directly and rebuild.
