# Aster — one compact Golden Sun town (approved redesign direction)

**Decision: abandon the ruined-state variant.** Aster will have one authored
settlement. Its changing memories, mismatched houses and the Other Isaac echo
must create the narrative disturbance through the existing scene stages. The
unregistered damaged-map source and visual studies are preserved as **archive
only**, not built, maintained, verified, or counted in release acceptance.

## The issue with the old map

The problem is not insufficient flower decorations. Six widely separated
buildings sit on a nominal 64×64 walkable grass field. The three long parallel
east-west roads and lengthy north-south corridor leave large rectangular lawns
with no believable function. Even twelve trees, four flower plots and six
new domestic details cannot fix that underlying spatial composition.

**Do not iterate by sprinkling another layer of random objects over it.**
Change the street/block relationships and the amount of usable land first.

## New town footprint

Keep **Map180's existing three 64×64 layer windows in the 128×128 native
Golden Sun file format** to avoid needless map-encoder or engine rewrites.
Redesign the **visible/playable settlement** to approximately **46×46
metatile cells**, bounded by *irregular* compatible terrain and native
vegetation. The remaining border is environmental framing, **not** more
empty playable meadow. The 46×46 figure is a design target, not an
implemented map-size change.

The draft landmarks below are working placements, **NOT registered
coordinates or functioning story triggers**. Do not move them into
`aster_layout.py` without updating `aster.c`, entrances, NPC directions,
event tiles, and source contracts together.

| Area | Draft position in 64×64 map | Purpose |
| --- | --- | --- |
| Northwest | sealed house near (7,6) | An inhabited-looking facade with no legitimate entry |
| Northeast | duplicate home near (32,8) | A near-copy, offset rather than perfectly mirrored |
| North-center | memorial garden near (23,13) | Small ordinary memorial and legible approach |
| Mid-west | western home near (8,19) | Occupied domestic block: garden, laundry/working yard |
| Mid-east | eastern home near (32,22) | Slightly lower address, with a different-use yard |
| Central clearing | dry well near (24,27) | A compact *functional* meeting area; no spring/crystal |
| Southwest | shop near (7,34) | Trade frontage, crates, stall, short customer path |
| Southeast | inn near (30,34) | Lodging frontage and small guest/utility space |
| South | gate near (24,50) | Short, legible transition to the world map |

These positions deliberately *aren't* a rigid pair of columns.
The scene should feel like the buildings grew around roads and terrain.

## Three districts — not a grid of isolated houses

**1. North: remembrance and contradictions.** The northern lane is narrower
and quieter; the duplicate and sealed homes belong to an older, less-tended
block. Preserve the duplicated-home mystery, but do not deliberately make
both homes a mirrored corner in a symmetrical square.

**2. Middle: everyday life.** Put the two inhabited homes within view of
each other and the central well. Make a coherent commons with enough room
for the elder, boy and mirror woman to stand in meaningful positions. A
well must be legible at the native 16px scale before we wire collision.
If no compatible source prop exists, make a small purpose-built *Golden Sun
style* well asset from permitted/user-created original art, rather than
cropping a cave, house doorway or Psynergy object into a fake well.

**3. South: work and arrivals.** Bring the shop, inn, short fenced yards
and gate together so that the place visibly has a market frontage. Add a
single small utility shed or cart/stall only when its original Golden Sun
sprite/art and collision are confirmed; no imported Paradox tiles.

## Terrain and movement

- Shape the boundary with natural, compatible Golden Sun woods, earth edges,
  or cliffs. Use *complete* tile transitions and organic contours; do not
  paste repeating square tree rectangles. Leave clear visual exits.
- Connect short, uneven streets via a small central meeting area. Avoid
  long perfectly straight three-cell corridors and three identical
  crossroads. Roads follow building thresholds and the terrain.
- Give each home and commercial building a clear reason for its adjacent
  space. A pen, woodpile, garden, laundry, crates or enclosed yard should
  belong to something rather than floating in unused grass.
- Do not let props block any of the six doorstep approaches, seven NPC
  anchor positions, the eight narrative triggers, or the main gate.
- Preserve the actual original Golden Sun `set_02` metatiles and
  compatible three-layer rendering, not a visual imitation from another RPG.
- Explicitly exclude a Psynergy Stone, magic fountain, or borrowed monument.

## Development order / gates

1. **Layout before detail.** Draft and render the compact footprint,
   reshuffled six buildings and logical street connections. Compare it
   against the old 64×64 layout. No final props or dialogue rewrites yet.
2. **Integrate movement.** Update all eight triggers, seven NPC spots,
   entrances and Aster's scene source in the *same pass* as the approved
   new geometry. Source-level flood-fill and in-engine walking tests.
3. **Make the town inhabited.** Introduce *coherent* yards and proper
   landmark art, not hundreds of tiny repeated plant stamps. Validate
   scenery sizes, occlusion and source palette against real Golden Sun.
4. **Playtest narrative.** One physical Aster; arrival, fracture and
   revelation are dialogue/event states, not separate ruined town maps.
   Preserve each 27-character maximum dialogue line and three-line page.
5. **Before release.** Verify all entrances/thresholds, reciprocal
   world-map travel, proper well, engine sprite priority, event flag
   persistence, and no regressions to the rest of Ashfall.

Current live Map180 is still the **old broad layout** until the first
compact-layout source render passes. This document is a bounded rebuild
specification, not a claim that the geometry has already changed.
