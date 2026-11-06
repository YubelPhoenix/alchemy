#!/usr/bin/env python3
"""Builds the exclusive boss battle backgrounds (assets/backgrounds/NAME.png)
into games/tbs/src/graphics/battle_bg/NAME.png.

A battle background is 256x120, indexed, with a 128-colour palette (indices 0
to 127), each channel a multiple of eight (GBA 5-bit colour). The artwork is
cropped to that shape (keeping the top, where the sky is) and dithered down.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/backgrounds"
DEST = ROOT / "games/tbs/src/graphics/battle_bg"
WIDTH, HEIGHT = 256, 120

# name -> vertical offset of the crop as a fraction of the spare height
BACKGROUNDS = {"heart": 0.12, "sarah": 1.0, "kegare": 0.9, "ash": 0.33}

for name, offset in BACKGROUNDS.items():
    art = Image.open(SOURCE / f"{name}.png").convert("RGB")
    crop_h = round(art.width * HEIGHT / WIDTH)
    if crop_h > art.height:
        raise ValueError(f"{name}: too short for a {WIDTH}x{HEIGHT} crop")
    top = round((art.height - crop_h) * offset)
    art = art.crop((0, top, art.width, top + crop_h))
    art = art.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    indexed = art.quantize(colors=128, method=Image.Quantize.MEDIANCUT, kmeans=4,
                           dither=Image.Dither.FLOYDSTEINBERG)
    palette = indexed.getpalette()[:128 * 3]
    palette += [0] * (128 * 3 - len(palette))
    palette = [(v // 8) * 8 for v in palette]
    indexed.putpalette(palette)
    assert indexed.size == (WIDTH, HEIGHT)
    assert max(indexed.getdata()) <= 127
    target = DEST / f"{name}.png"
    indexed.save(target, optimize=False)
    print(f"Rebuilt {target.relative_to(ROOT)} ({WIDTH}x{HEIGHT}, 128 colours)")
