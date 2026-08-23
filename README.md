# Matcha On Ice Cafe — Documents

A4 portrait catalogue / technical-sheet PDFs for Matcha On Ice Cafe. Each document is its
own JSON file and build script. The three guest/recipe-facing documents share one brand
system — fonts, palette, cover, dividers, page furniture — defined once in
`build/common.py`. The Equipment & Bar Manual is a plain internal operational reference and
deliberately opts out of that brand system (see its section below) — it has its own small
stylesheet and page builder in `build/generate_equipment.py`.

| Document | Data | Build | Output | Status |
| --- | --- | --- | --- | --- |
| Matcha Catalogue | `data/catalog.json` | `build/generate.py` | [`dist/Matcha-On-Ice-Cafe-Catalog.pdf`](dist/Matcha-On-Ice-Cafe-Catalog.pdf) — 11 pages | Content complete |
| Syrups & Cold Foam | `data/syrups.json` | `build/generate_syrups.py` | [`dist/Matcha-On-Ice-Cafe-Syrups-Cold-Foam.pdf`](dist/Matcha-On-Ice-Cafe-Syrups-Cold-Foam.pdf) — 9 pages | Content complete |
| Coffee Bar Manual | `data/coffee-bar-manual.json` | `build/generate_coffee.py` | [`dist/Matcha-On-Ice-Cafe-Coffee-Bar-Manual.pdf`](dist/Matcha-On-Ice-Cafe-Coffee-Bar-Manual.pdf) — 19 pages | Draft — see note below |
| Equipment & Bar Manual | `data/equipment-manual.json` | `build/generate_equipment.py` | [`dist/Matcha-On-Ice-Cafe-Equipment-Bar-Manual.pdf`](dist/Matcha-On-Ice-Cafe-Equipment-Bar-Manual.pdf) — 8 pages | Mostly real content — see note below |

## Build

```bash
python3 build/generate.py                 # Matcha Catalogue: HTML + PDF
python3 build/generate_syrups.py           # Syrups & Cold Foam: HTML + PDF
python3 build/generate_coffee.py           # Coffee Bar Manual: HTML + PDF
python3 build/generate_equipment.py        # Equipment & Bar Manual: HTML + PDF
python3 build/generate.py --html           # any script: HTML only
```

Requires Python 3 and headless Chromium (auto-detected from `/opt/pw-browsers` or `PATH`).
No third-party Python packages. Fonts and logo artwork are embedded into the HTML, so the
generated `dist/*.html` files are self-contained and can be opened or shared on their own.

`build/extract_logo.py` is a separate one-off step that re-derives the logo artwork from
`assets/brand/logo-source.jpeg`. It only needs rerunning if the logo itself changes, and
it is the only thing here that needs `numpy` and `Pillow`.

## Structure

| Path | What it is |
| --- | --- |
| `build/common.py` | Shared brand system — stylesheet, page builders, PDF rendering |
| `build/generate.py` | Matcha Catalogue: loads `data/catalog.json` |
| `build/generate_syrups.py` | Syrups & Cold Foam: loads `data/syrups.json` |
| `build/generate_coffee.py` | Coffee Bar Manual: loads `data/coffee-bar-manual.json` |
| `build/generate_equipment.py` | Equipment & Bar Manual: loads `data/equipment-manual.json`; self-contained, does not use `build/common.py`'s brand system |
| `build/extract_logo.py` | Re-derives the logo artwork from the source file |
| `data/catalog.json` | Matcha Catalogue content |
| `data/syrups.json` | Syrups & Cold Foam content |
| `data/coffee-bar-manual.json` | Coffee Bar Manual content |
| `data/equipment-manual.json` | Equipment & Bar Manual content |
| `assets/fonts/` | Embedded brand fonts (SIL Open Font License, texts included) |
| `assets/photos/` | Drink photography — drop files here |
| `assets/brand/` | Source logo plus the transparent marks derived from it |
| `dist/` | Generated HTML and PDFs |

## Section shapes

These shapes apply to the three brand-system documents (Matcha Catalogue, Syrups & Cold
Foam, Coffee Bar Manual). The Equipment & Bar Manual uses its own, separate content model —
see its section below.

Every document is a `sections` array; each section is a chapter (cover index entry +
divider + its pages). A section's `"kind"` decides what its pages look like:

| `kind` | Pages | Used by |
| --- | --- | --- |
| *(default)* | One full page per item — photo (or a sage placeholder block), sized Measures (12oz/16oz), Method | Signature Matchas |
| `"foundation"` | Two fixed pages — a story/explanation page, then a proportions/recipe page (`measureBlocks` + one Method) | The Matcha Base, Cold Foam, Espresso Basics |
| `"simple"` | One plain recipe per item — name, one spec/ingredients list, Method. No photo; sized 12oz/16oz columns if the item sets `"sized": true`, one plain quantity column otherwise. A section can rename the two column headings via `specLabel` / `methodLabel` (default "Ingredients" / "Method") | Syrups, Espresso Classics, Barista Tools ("Specs" / "Use") |

A section can also be `"expandable": true` (independent of `kind`), which gives it the
"Open chapter" index treatment and a closing "More to come" card instead of ending flush —
the treatment Seasonal Add-Ons used before it split out of the Matcha Catalogue. The
machinery (`build_endcard`) stays in `build/common.py`, unused, ready for whichever
document picks up an open-ended chapter next.

See `build_drink`, `build_foundation_story` / `build_foundation_recipes`, and
`build_simple_recipe` in `build/common.py` for exactly what each shape renders.

## Brand system

The wordmark itself is never re-typeset — every appearance of it in any document is the
real logo artwork (see below). The three faces below are chosen to sit with it: Pinyon
Script for its high-contrast roundhand "Matcha", Playfair Display for the Didone of its
"On Ice", Jost for its spaced "CAFE".

| Role | Face | Used for |
| --- | --- | --- |
| Script | Pinyon Script | Drink/item names, section names, placeholder blocks |
| Serif | Playfair Display | Measures, method steps, blurbs, index, body copy |
| Caps | Jost, letterspaced | Category labels, step numbers, page furniture |

| Token | Hex | Role |
| --- | --- | --- |
| `--sage` | `#8a9b6e` | Primary — dividers, placeholder blocks |
| `--sage-deep` | `#5d6b45` | Item names, headings |
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
The block is portrait (83 × 90 mm) and images are cropped to fill, so **shoot vertical**.
(Only the default drink-page shape has a photo — `"simple"` and `"foundation"` pages don't.)

## The logo

The cover, the section dividers, the closing card and every page's footer use the actual
logo artwork rather than a typeset imitation, so the letterforms are exact.

`build/extract_logo.py` lifts the white artwork off the sage field in
`assets/brand/logo-source.jpeg` into transparent PNGs, in sage (for cream backgrounds) and
cream (for sage backgrounds):

| Mark | Contents | Used on |
| --- | --- | --- |
| `logo-lockup-*` | "Matcha On Ice" over "CAFE" | Cover |
| `logo-wordmark-*` | "Matcha On Ice" | Section dividers, closing card |
| `logo-script-*` | the "Matcha" script alone | Page footers |

To swap in a new logo, replace `logo-source.jpeg`, rerun `python3 build/extract_logo.py`,
then rebuild every document. If the new file has different proportions, the two crop
constants at the top of that script (`SCRIPT_END_X`, `BAND_SPLIT_Y`) need remeasuring. If
the marks are missing altogether, the cover falls back to a typeset lockup.

## Matcha Catalogue (`data/catalog.json`)

### Adding a drink

Add an entry to `signature-matchas` and rebuild. Page numbers, index rows and the "No. 0X"
labels are all derived, so nothing else needs updating.

There's no ingredients table. Things like ice, milk and cold foam aren't measured — they're
assembly steps, not a quantity — so they live in the Method text. **Measures** is reserved
for the few things worth calling out precisely: matcha, syrup.

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
syrup). A drink with no syrup (Coconut Cloud) just omits `measures`, and one whose method
departs from the section's `defaultMethod` overrides it in full, the way Coconut Cloud
drops the syrup step and Double Matcha's cold foam step is mandatory rather than optional.
`serves` and `note` are optional; a missing `note` renders no note at all rather than filler
text, since a placeholder note would read as real copy in a finished page.

### The Matcha Base

`matcha-base` is marked `"kind": "foundation"` — it isn't a list of drinks, it's the
sourcing story, the water-temperature guidance, and the ratios (individual and event-batch)
every Signature Matcha is built from. Its two pages are fixed rather than data-driven per
entry, so its content lives directly on the section object: `story` (the sourcing copy,
plus an optional `callout` — a labeled stat, e.g. water temperature or a component ratio),
`measureBlocks` (a list of `"sized"` — 12oz/16oz columns
— or `"single"` — one quantity column — measure lists), `recipesPage` (the second page's
heading), and `method`. To change any of it, edit those keys in `catalog.json` and rebuild.

## Syrups & Cold Foam (`data/syrups.json`)

Same brand system as the Matcha Catalogue, deliberately simpler pages: no photo, no
12oz/16oz split, since these are build components, not menu drinks.

**Syrups** (Vanilla, Banana Bread, Strawberry, Mango) are real recipes. **Cold Foam** is
filled in too — the 2:1:1 cream/milk/syrup ratio, the base batch, and the two-stage
whip-then-texture method.

### Adding a syrup

`syrups` is marked `"kind": "simple"`. Add an entry and rebuild:

```json
{
  "name": "Pumpkin Spice Syrup",
  "ingredients": [
    { "item": "Brown sugar", "qty": "1 cup" },
    { "item": "Water", "qty": "1 cup" },
    { "item": "Pumpkin spice blend", "qty": "1 tbsp" }
  ],
  "method": [
    "Combine the ingredients in a saucepan.",
    "Bring to a simmer, stirring until fully dissolved.",
    "Remove from heat and let cool completely.",
    "Strain, bottle and refrigerate."
  ],
  "yield": "Yield — 16 oz",
  "note": "Keeps refrigerated for 2 weeks."
}
```

`ingredients`, `yield` and `note` are all optional.

### Cold Foam

`cold-foam` is `"kind": "foundation"`, the same shape as The Matcha Base: a story page
(the three components, the whip-then-texture process, the 2:1:1 ratio callout) and a
recipe page (the batch, then Method). `measureBlocks` is a list, so a second block — a
flavor variant, say — is just another entry away.

## Coffee Bar Manual (`data/coffee-bar-manual.json`)

Same brand system again, three chapters:

- **Espresso Basics** (`"kind": "foundation"`) — what espresso is, the house double shot
  (dose, yield, extraction time), and the 25–30 sec extraction-time callout every classic
  and Signature Coffee is timed against.
- **Espresso Classics** (`"kind": "simple"`) — Espresso, Americano, Americano (Iced),
  Macchiato, Cortado, Flat White, Cappuccino, Latte, Latte (Iced). Each a spec sheet
  (shot / milk / foam) rather than a recipe — these are fixed drinks, not proprietary
  ones. Cappuccino and both Lattes are `"sized": true` (12oz/16oz columns, `yield` reads
  "Serves 1"); the rest are one plain quantity column with `yield` as a Cup-size caption.
- **Signature Coffees** (default `kind`, full drink page) — the four iced lattes, carried
  over from the Matcha Catalogue when it split out. Same shape as Signature Matchas: photo
  (or placeholder), sized Measures, Method.

> **Status: draft.** The house double shot (2 oz) is the number already confirmed for
> Signature Coffees. Everything built on top of it — Espresso Basics' dose (18 g) and
> extraction time (25–30 sec), and every Espresso Classic's milk/foam/cup spec — is a
> standard barista-training default, not this bar's confirmed number, and needs a pass to
> match your actual beans, machine and house pours. Signature Coffees is untouched
> placeholder, same starting point Signature Matchas had before its real syrups and method
> came in.

## Equipment & Bar Manual (`data/equipment-manual.json`)

This is an internal operational reference, not a guest-facing piece, so it deliberately
opts out of the café's brand system — no script font, no sage/cream palette, no
one-item-per-page layout. It's plain sans-serif, black on white, dense tables and lists,
in the style of a straightforward SOP/training-manual page. Its stylesheet and HTML
builders live entirely in `build/generate_equipment.py` itself (it only borrows
`render_pdf`/`ROOT` from `build/common.py`), and pages flow naturally with normal CSS print
pagination (`page-break-before` / `break-inside: avoid`) rather than the fixed
297 mm `.page` divs the other documents use — there's no need for one/two-page-per-item
here.

Content model — `documentTitle`, `footer`, and a `chapters` array. Each chapter is
`{ numeral, title, subtitle, blocks }`, and each block in `blocks` is one of:

| `type` | Renders as | Fields |
| --- | --- | --- |
| `"prose"` | Paragraphs, with an optional heading | `heading?`, `paragraphs` |
| `"table"` | A spec table — 2-column (bold term / value, no header) by default, or any number of columns with a header row | `heading?`, `rows`, `headers?`, `columns?` |
| `"steps"` | A numbered list | `heading?`, `items` |
| `"deflist"` | A dense term/spec definition list, each entry with bulleted use-steps and an italic note | `heading?`, `items`: `{ term, spec, use[], note? }` |
| `"checklist"` | Two (or more) side-by-side checkbox lists, e.g. Opening / Closing | `heading?`, `groups`: `{ label, items }` |
| `"warning"` | A bordered callout — one bold all-caps line (`text`), or a bulleted list of cautions (`items`) | `heading?`, `text` or `items` |

A `paragraphs` entry (in `"prose"`) or an `items` entry (in `"steps"`) can be a plain string,
or `{ "lead": "...", "text": "..." }` for a bold inline lead-in — e.g. Steaming Milk's
"**Milk Temp.** The ideal range for dairy is 145°F–155°F…" and its "**Groom the milk.**
Tap the pitcher on the counter…" step both use this.

A `"table"` defaults to `columns: ["item", "value"]` with no header row (the plain spec-sheet
look). Pass `headers` (and matching `columns`, since row dicts can use any keys) for a wider
table with a header row — used for the Controls Reference and the Troubleshooting tables,
which run to 2–3 columns.

Four chapters, largely sourced from the equipment's own daily-operation guides rather than
general knowledge:

- **The Grinder** — the Fiorenzato F64 Evo Pro: what it is, a specs table, daily startup,
  the four dosing modes, adjusting grind size, daily cleaning (including the PRO
  quick-release chamber's deeper clean), monthly deep clean, burr replacement, a
  troubleshooting table, and a daily opening/closing checklist.
- **The Espresso Machine** — the Sanremo Zoe Compact 208V, 2 group: specs, a controls
  reference table (every lettered/numbered control), daily startup, pulling shots, steam
  and hot water, programming SED dose volumes, pre-infusion, daily backflush per group,
  periodic maintenance, a "Critical Don'ts" list, a troubleshooting table, and a daily
  checklist.
- **Steaming Milk** — drink size / milk temp / milk texture as the three things to know
  before starting, a setup/target table (145°F–155°F for dairy, lower max for standard
  dairy alternatives), the full 13-step technique including grooming the milk, and a
  "never re-steam milk" warning.
- **Barista Tools** — a `"deflist"` of seven tools (Tamper, WDT Tool, Digital Scale, Milk
  Pitchers, Knock Box, Puck Screen, Cleaning Kit), followed by a short "Workstation Setup"
  prose section on laying out the bar.

> **Status: mostly real content, one placeholder gap.** The Grinder and Espresso Machine
> chapters are transcribed from the equipment's own daily-operation guides (Fiorenzato F64
> Evo Pro, Sanremo Zoe Compact 208V) — startup sequences, control functions, dosing/
> programming steps, cleaning cadence and troubleshooting tables are the manufacturers'
> own, not general knowledge. Steaming Milk is likewise real, confirmed content. Barista
> Tools is standard technique/reference content, same confidence tier as Espresso Basics
> in the Coffee Bar Manual.
