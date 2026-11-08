# Aster — residential quarter visual reset (8 November 2026)

## What was actually built

`tools/aster_handbuilt_residential.py` is an isolated **source-only**
experiment. It intentionally places three cottages, 169 native dirt-road
cells, a 12×9 Vale-sourced pond, 14 complete native tree stamps, ten
2×2 flower beds, three wooden fence strips, seven supplies and 18
individual flowers. No item is skipped on collision. Source-level
checks confirmed the three doorways and shared lane remain connected.

The test image and exact counts are archived as
`tools/aster_handbuilt_residential_closeup.png` and
`tools/aster_handbuilt_residential_report.json`.

### Visual result: REJECTED

The neighborhood still looks like three scattered houses on an
undifferentiated grass plane. The large gap between homes and pond,
repeated same-looking thatch buildings, isolated trees and 16px prop
stamps all betray the fact that the terrain itself was not designed.
A stray source-building fragment remains next to the east pond shore.
The blue pond's lower edge looks unnatural. The narrow dirt streets,
garden patches and small household items are present in the *data*,
but do not read as a cohesive or convincing occupied village.

**No part of this rendering is approved to replace Map180 or the
Aster actor/event scene.** The passing footprint and connectivity
checks mean only that the source is internally consistent, not that
the map meets a professional Golden Sun visual standard.

## Mandatory change of asset strategy

Stop beginning with a 64×64 rectangle of Vale grass. Starting on an
unbroken grass plane and applying complete Vale tree/house/pond stamps
has been tried repeatedly and has failed visually even with manual
placements. Further prop-count increases cannot solve the problem.

The project can use **original Golden Sun** terrain and set graphics
from other towns when their *entire compatible metatile, layer,
tileset and palette setup* is respected. Do not paste unrelated
Vault or Xian image crops into Vale `set_02`; that repeats the
palette and clipping errors. Compare the authentic source maps/tilesets
for Vault (terrain and lived-in supplies), Xian (woodland, streams,
cultivation), and Kalay (domestic street structure), then choose
an Aster-compatible landscape vocabulary BEFORE placing any more
buildings.

## Hand-designed district requirement

Next deliverable is **one complete neighborhood**, not all of Aster.
The stage must show two or three homes, a connected landform, at least
one naturally banked water feature if the chosen set supports it, a
coherent work/storage area and substantive cultivated gardens.

Design the landscape first:
1. Use connected ground/rock/water/vegetation transitions, not
   detached square panels or floating upper layers.
2. Author the home footprints and thresholds as plots set into the
   environment; define each person's working garden or utility yard.
3. Draw paths that respond to slope, water and property frontage.
4. Use varied *complete* original game scenery within the SAME
   palette/layer system, including bushes, low grass, stone, fencing,
   woodpiles and supplies when the set actually has them.
5. Check both native 16px image and enlarged pixel-perfect view:
   shoreline continuity, roof/canopy occlusion, road edges, sprite
   silhouettes, position/scale and empty space.
6. Reject the entire district if it looks like an asset collage or
   garden stamps sprinkled on a green field.

Do not request visual approval based on counts or source audit results.
Once the residential quarter passes visual inspection, translate its
actual tile map to game Map180, update Aster's door/NPC/event positions
in one change, compile and test in an emulator. Keep the unfinished
ruined-state variant retired. The existing Aster story work is retained.
