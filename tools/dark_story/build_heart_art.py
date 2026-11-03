#!/usr/bin/env python3
"""Rebuild Heart's battle sheet from the original, unsquashed source poses."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "heart"
DEST = ROOT / "games/tbs/src/graphics/monster/purple_beast.png"

# The sprite metadata defines 64x64 frames and the animation uses even
# frame indices 0, 2, 4, 6, 8, 10. Each pose occupies two frames.
POSES = [1, 2, 3, 4, 5, 6]
sheet = Image.new("RGBA", (64, 768), (0, 0, 0, 0))
for index, number in enumerate(POSES):
    src = Image.open(SOURCE / f"pose_128_{number}.png").convert("RGBA")
    bounds = src.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"Heart pose {number} is empty")
    art = src.crop(bounds)
    # Keep aspect ratio; never stretch width and height independently.
    art.thumbnail((60, 60), Image.Resampling.NEAREST)
    frame = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    frame.alpha_composite(art, ((64-art.width)//2, (64-art.height)//2))
    sheet.alpha_composite(frame, (0, index*128))
    sheet.alpha_composite(frame, (0, index*128+64))
# The GBA graphics packer expects indexed-color source art.
indexed = sheet.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
indexed.save(DEST)
print(f"Rebuilt {DEST.relative_to(ROOT)} from six original Heart poses")

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
