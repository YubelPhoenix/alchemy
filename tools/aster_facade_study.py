#!/usr/bin/env python3
"""Non-destructive Golden Sun-only visual comparison of Vale house footprints.

Experimental render only. The tracked game map is NOT modified. Draw the
original Aster middle and overhead layers over seamless Vale grass instead
of retaining cliffs from the source houses' original surroundings.
"""
from pathlib import Path
import aster_layout as layout
import aster_visual_preview as render

ROWS=render.load_map()
for _, dx, dy, sx, sy, w, h, _ in layout.BUILDINGS:
    for y in range(dy,dy+h):
        for x in range(dx,dx+w):
            ROWS[y][x]="ba:ff"

render.load_map=lambda:ROWS
render.make(
  layout.ROOT/"tools/aster_facade_clean_study.png",
  layout.ROOT/"tools/aster_facade_clean_study_labeled.png"
)
print("STUDY ONLY; Golden Sun Vale base-grass underneath original roofs/walls.")
