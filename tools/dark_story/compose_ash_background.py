#!/usr/bin/env python3
"""Gives Ash Jenna's moonlit-cliff background a ground the battlers can stand on.

assets/backgrounds/ash_original.png has its cliff in the lower right only; the
rest of the lower picture is forest. This extends the cliff's top level across
the whole width as a flat rocky platform (the cliff's own stone and moss,
as a smooth procedural ground in its colours (no tiling, no hard edge)) and writes assets/backgrounds/ash.png.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets/backgrounds/ash_original.png"
DEST = ROOT / "assets/backgrounds/ash.png"

PLATFORM_TOP = 612     # the cliff's own top level
DONOR = (1090, 640, 1500, 960)   # x0, y0, x1, y1: stone and moss of the cliff

img = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64)
h, w, _ = img.shape
x0, y0, x1, y1 = DONOR
base = img[y0:y1, x0:x1].reshape(-1, 3).mean(axis=0)   # the cliff's own colour
rng = np.random.default_rng(7)

def noise(scale, amp):
    n = rng.normal(0, 1, (h // scale + 2, w // scale + 2))
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    return n * amp

need = h - PLATFORM_TOP
rows = np.arange(h)[:, None]
depth = np.clip((rows - PLATFORM_TOP) / need, 0, 1)
# Ground gets slightly darker toward the bottom, with soft broad variation
# plus fine stone speckle.
lum = 2.1 - 0.5 * depth + noise(48, 0.05) + noise(12, 0.04) + noise(3, 0.03)
ground = np.clip(base[None, None, :] * lum[:, :, None], 0, 255)
ground[..., 1] *= 1.0 + 0.06 * np.clip(noise(64, 1.0), -1, 1)   # faint moss

# Soft blend from the forest line into the ground; no bright lip.
FADE = 44
alpha = np.clip((rows - (PLATFORM_TOP - FADE // 2)) / FADE, 0, 1)
alpha = alpha * alpha * (3 - 2 * alpha)
out = img * (1 - alpha[:, :, None]) + ground * alpha[:, :, None]
# Lift the whole picture so the battlers read against it on a GBA screen.
out = 255.0 * (np.clip(out, 0, 255) / 255.0) ** 0.78
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(DEST)
print(f"Wrote {DEST.relative_to(ROOT)}")
