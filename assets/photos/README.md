# Drink photography

Drop drink photos here and rebuild with `python3 build/generate.py`.

Filenames are reserved per drink in `data/catalog.json`. The extension in the JSON
does not have to match the file on disk — `.jpg`, `.jpeg`, `.png`, `.webp` and `.avif`
all resolve by name.

The frame is portrait (116 × 124 mm) and images are cropped to fill, so shoot vertical.
Any drink without a photo renders as a sage block with its name in the brand script.
