#!/usr/bin/env python3
"""Rebuild Heart's battle sheet from the original, unsquashed source poses."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "heart"
DEST = ROOT / "games/tbs/src/graphics/monster/purple_beast.png"

# Monster frames are 64x64, but Heart must remain at party scale.
# The first two animation slots are the resting loop; do not alternate
# a defensive stance into that loop. Other slots retain distinct poses.
POSES = [1, 1, 3, 4, 5, 6]
IDLE_HEIGHT = 36
ACTION_HEIGHT = {3: 36, 4: 36, 5: 36, 6: 36}
sheet = Image.new("RGBA", (64, 768), (0, 0, 0, 0))
for index, number in enumerate(POSES):
    src = Image.open(SOURCE / f"pose_128_{number}.png").convert("RGBA")
    bounds = src.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"Heart pose {number} is empty")
    art = src.crop(bounds)
    target_height = IDLE_HEIGHT if index < 2 else ACTION_HEIGHT[number]
    # Preserve the source pose's aspect ratio without arbitrary compression.
    target_width = max(1, round(art.width * target_height / art.height))
    if target_width > 60:
        target_width = 60
        target_height = max(1, round(art.height * target_width / art.width))
    art = art.resize((target_width, target_height), Image.Resampling.NEAREST)
    frame = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    # Feet sit on the bottom row above the battle shadow.
    frame.alpha_composite(art, ((64 - art.width) // 2, 64 - art.height))
    sheet.alpha_composite(frame, (0, index * 128))
    sheet.alpha_composite(frame, (0, index * 128 + 64))

# Build a single deterministic 4bpp palette from VISIBLE pixels only.
# The previous quantizer included the large transparent black background,
# wasting a colour and shifting the intended sprite indices.
visible = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
visible.alpha_composite(sheet)
opaque_pixels = [pixel[:3] for pixel in visible.getdata() if pixel[3] >= 128]
if not opaque_pixels:
    raise ValueError("Heart battle sheet has no visible pixels")
samples = Image.new("RGB", (len(opaque_pixels), 1))
samples.putdata(opaque_pixels)
reduced = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
source_palette = reduced.getpalette()[:45]
# Index zero is transparent; all six frames share indices 1..15.
palette = [0, 0, 0] + [(channel // 8) * 8 for channel in source_palette]
palette += [0] * (768 - len(palette))
indexed = Image.new("P", sheet.size, 0)
indexed.putpalette(palette)
# The quantizer only saw opaque pixels, so walk those pixels in the
# identical row-major order when mapping indices back into the sheet.
indices = iter(reduced.getdata())
alpha = visible.getchannel("A").load()
output = indexed.load()
for y in range(sheet.height):
    for x in range(sheet.width):
        if alpha[x, y] >= 128:
            output[x, y] = next(indices) + 1
# Transparent pixels must never consume one of the 15 visible colours.
assert max(indexed.getdata()) <= 15
assert sum(1 for index in indexed.getdata() if index) == len(opaque_pixels)
assert next(indices, None) is None
indexed.save(DEST)
print(f"Rebuilt {DEST.relative_to(ROOT)} at party scale with shared 16-colour palette")

# Claude's portrait hook already points at ICON_66. Replace that placeholder
# with the original 64x64 Heart mugshot; no changes to Mia or other portraits.
portrait = Image.open(SOURCE / "mugshot_64.png").convert("RGBA")
# This icon atlas requires each entry to be 32x32 with at most 16 colours.
# Preserve the original proportions rather than stretching the mugshot.
portrait.thumbnail((32, 32), Image.Resampling.NEAREST)
canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
canvas.alpha_composite(portrait, ((32 - portrait.width) // 2, (32 - portrait.height) // 2))
portrait_target = ROOT / "games/tbs/src/graphics/ui/icons/icon_66.png"
# GBA icon palettes require opaque RGB channels aligned to eight.
# Quantize first, then snap palette entries to valid GBA levels.
icon = canvas.convert("RGB").quantize(colors=16, method=Image.Quantize.MEDIANCUT)
palette = icon.getpalette()
for i in range(0, len(palette), 3):
    for channel in range(3):
        palette[i + channel] = (palette[i + channel] // 8) * 8
icon.putpalette(palette)
icon.save(portrait_target)
print(f"Rebuilt {portrait_target.relative_to(ROOT)} from original Heart mugshot")
