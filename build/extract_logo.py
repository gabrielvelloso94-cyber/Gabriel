#!/usr/bin/env python3
"""Derive transparent logo masks from the supplied brand artwork.

The source logo is white artwork on a sage field. This lifts the artwork off
that field into an alpha mask, so the catalogue can paint the *exact* logo
letterforms in any brand colour (sage on cream, cream on sage) via CSS
mask-image, rather than approximating them with a substitute script font.

Outputs, per mark, as transparent RGBA PNGs in each brand colour:
    assets/brand/logo-lockup-{sage,cream}.png    "Matcha On Ice" over "CAFE"
    assets/brand/logo-wordmark-{sage,cream}.png  "Matcha On Ice" without CAFE
    assets/brand/logo-script-{sage,cream}.png    the "Matcha" script alone

The colour is baked in rather than applied with a CSS mask: a CSS mask keys on
the alpha channel, and the print path is one less thing to go wrong.

Usage:
    python3 build/extract_logo.py [source-image]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand"
DEFAULT_SRC = BRAND / "logo-source.jpeg"

# Artwork geometry in the source file, measured from the luminance profile.
# The wordmark and CAFE sit in two horizontal bands; "Matcha" and "On Ice"
# are separated by a clean vertical gutter.
SCRIPT_END_X = 1032       # right edge of the "Matcha" script
BAND_SPLIT_Y = 1150       # between the wordmark band and the CAFE band

ARTWORK_LUM = 190.0       # above this a pixel is artwork, not field
BLOCK = 64                # background is sampled on this grid
EDGE_TRIM = 4             # the export carries faint border lines on all four sides


def estimate_background(rgb: np.ndarray, artwork: np.ndarray) -> np.ndarray:
    """Smooth per-pixel estimate of the sage field behind the artwork.

    The field carries a gentle gradient, so a single flat colour leaves halos.
    Sample a coarse grid of field-only medians, then interpolate back up.
    """
    h, w, _ = rgb.shape
    gh, gw = (h + BLOCK - 1) // BLOCK, (w + BLOCK - 1) // BLOCK
    coarse = np.zeros((gh, gw, 3), np.float32)
    filled = np.zeros((gh, gw), bool)

    for by in range(gh):
        for bx in range(gw):
            tile = rgb[by * BLOCK:(by + 1) * BLOCK, bx * BLOCK:(bx + 1) * BLOCK]
            keep = ~artwork[by * BLOCK:(by + 1) * BLOCK, bx * BLOCK:(bx + 1) * BLOCK]
            if keep.sum() >= 32:
                coarse[by, bx] = np.median(tile[keep], axis=0)
                filled[by, bx] = True

    # Blocks sitting entirely under artwork borrow from the nearest filled block.
    if not filled.all():
        ys, xs = np.where(filled)
        for by, bx in zip(*np.where(~filled)):
            d = (ys - by) ** 2 + (xs - bx) ** 2
            coarse[by, bx] = coarse[ys[d.argmin()], xs[d.argmin()]]

    smooth = Image.fromarray(coarse.astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(smooth).astype(np.float32)


def alpha_from(src: Path) -> np.ndarray:
    rgb = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)

    lum = rgb.mean(axis=2)
    core = Image.fromarray(((lum > ARTWORK_LUM) * 255).astype(np.uint8))
    artwork = np.asarray(core.filter(ImageFilter.MaxFilter(9))) > 127

    bg = estimate_background(rgb, artwork)

    # Artwork is white composited over the field: c = a*255 + (1-a)*bg
    alpha = np.clip(((rgb - bg) / np.maximum(255.0 - bg, 1.0)).mean(axis=2), 0, 1)
    alpha[alpha < 0.04] = 0.0          # clear JPEG noise out of the field

    # Drop the border lines so they cannot widen the crop.
    alpha[:EDGE_TRIM] = alpha[-EDGE_TRIM:] = 0.0
    alpha[:, :EDGE_TRIM] = alpha[:, -EDGE_TRIM:] = 0.0
    return alpha


# Brand colours the marks are rendered in, matching the catalogue palette.
IN_COLOURS = {
    "sage": (0x5d, 0x6b, 0x45),    # for cream backgrounds
    "cream": (0xf6, 0xf2, 0xe8),   # for sage backgrounds
}


def save_mark(alpha: np.ndarray, stem: str, pad: int = 6) -> None:
    ys, xs = np.where(alpha > 0.04)
    if len(xs) == 0:
        raise SystemExit(f"no artwork found for {stem}")
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, alpha.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, alpha.shape[1])
    crop = alpha[y0:y1, x0:x1]
    a8 = (crop * 255).round().astype(np.uint8)

    for name, rgb in IN_COLOURS.items():
        h, w = a8.shape
        out = np.empty((h, w, 4), np.uint8)
        out[..., 0], out[..., 1], out[..., 2] = rgb
        out[..., 3] = a8
        path = BRAND / f"{stem}-{name}.png"
        Image.fromarray(out, mode="RGBA").save(path, optimize=True)
        print(f"{path.name:26s} {w} x {h}")


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.exists():
        raise SystemExit(f"source artwork not found: {src}")

    BRAND.mkdir(parents=True, exist_ok=True)
    alpha = alpha_from(src)

    save_mark(alpha, "logo-lockup")

    wordmark = alpha.copy()
    wordmark[BAND_SPLIT_Y:] = 0.0
    save_mark(wordmark, "logo-wordmark")

    script = alpha.copy()
    script[BAND_SPLIT_Y:] = 0.0
    script[:, SCRIPT_END_X:] = 0.0
    save_mark(script, "logo-script")


if __name__ == "__main__":
    main()
