"""Preserve approved Ashfall rear frames across battle-art regeneration.

All overlays are supplied-art conversions, indexed to the shared sprite palette.
Do not silently accept a changed pose layout or a resource over the cache limit.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets" / "rear_battle"


def packed_size(pixels):
    count = pixels.shape[0] // 64
    size = 4 * (count + 1)
    for frame in pixels.reshape(count, 4096):
        i = 0
        size += 1
        while i < 4096:
            if frame[i]:
                i += 1
            else:
                run = 1
                while run < 32 and i + run < 4096 and not frame[i + run]:
                    run += 1
                i += run
            size += 1
    return size


def apply_rear_frames(sheet, asset, slots):
    if sheet.mode != "P" or sheet.width != 64 or sheet.height % 64:
        raise ValueError("Expected a 64px-wide indexed battle sheet")
    palette = sheet.getpalette()
    rear = Image.open(ASSETS / (asset + ".png"))
    if rear.mode != "P" or rear.size != (64, 64):
        raise ValueError("Expected a 64x64 indexed rear frame")
    if rear.getpalette()[:672] != palette[:672]:
        raise ValueError("Rear frame palette differs from shared palette")
    pixels = np.array(sheet)
    original = pixels.copy()
    frame = np.array(rear)
    if not frame.any() or frame.max() > 223:
        raise ValueError("Rear frame has invalid palette indices")
    for slot in slots:
        if not 0 < slot < sheet.height // 64 or slot % 2 != 1:
            raise ValueError("Rear frame slot must be an existing odd frame")
        dest = pixels[slot * 64:(slot + 1) * 64]
        prior = pixels[(slot - 1) * 64:slot * 64]
        if not (np.array_equal(dest, prior) or np.array_equal(dest, frame)):
            raise ValueError("Rear frame would replace a nonduplicate pose")
        dest[:] = frame
    for i in range(sheet.height // 64):
        if i not in slots and not np.array_equal(
                pixels[i * 64:(i + 1) * 64], original[i * 64:(i + 1) * 64]):
            raise ValueError("Unexpected change to a nonreplacement pose")
    size = packed_size(pixels)
    if pixels.max() > 223 or size > 16384:
        raise ValueError(f"Invalid palette or sprite cache overflow: {size} bytes")
    result = Image.fromarray(pixels, "P")
    result.putpalette(palette)
    return result
