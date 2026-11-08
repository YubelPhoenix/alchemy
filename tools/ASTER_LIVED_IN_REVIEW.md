# Aster — lived-in village acceptance review

**Working decision:** one ordinary-looking Golden Sun settlement, no ruined
alternate version. The settlement's contradictions emerge through people,
doors, records and dialogue, not visibly apocalyptic terrain.

## Why the original Aster failed

The user supplied the Ashfall city/town map archive as a visual standard.
The original 64x64 Aster had only six isolated buildings, three long
artificial road bars and broad meadow between them. Adding props did not
give the place a reason to exist.

The map comparisons establish these requirements:

- **Vault**: close homes, irregular rocky ledges, yards and practical
  objects turn even narrow walkable gaps into inhabited space.
- **Bilibin**: public space and built retaining boundaries establish an
  actual settlement center.
- **Xian**: cultivated land, working areas and approaches make everyday
  labor visible without explanatory dialogue.
- **Kalay/Tolbi**: buildings address streets and form blocks; the player
  can recognize commercial and civic areas.
- **Suhalla/Imil**: small settlements still have environmental limits,
  constrained routes and a specific relationship to their landscape.

Red collision overlays and blue event annotations from the user exports
are **not** texture assets. Only native Golden Sun set_02 layer art is
approved for the current Aster exterior.

## Two native-map compositional prototypes

1. `aster_lived_in_blockout.py`: clusters the six existing function
   buildings, makes short meandering routes and a shared commons, and
   assigns specific garden/work-yard uses. The first rendered image shows
   the roads are more natural, but there is **still too much open grass**.
   This study is **not approved** and does not update playable Map180.
2. `aster_lived_in_terrain.py`: wraps the same blockout with native
   cliff ridges and woodland strips chosen from the three-layer
   `aster_native_terrain_atlas.png`. **Visual result: REJECTED as a town.**
   Although source-accurate, the terrain sections read as isolated
   rectangular patches pasted into grass. Merely attaching more full
   source crops to an empty lawn repeats the original design error.
   The prototype is archived as a diagnostic; no terrain was incorporated
   into Map180 or scene collision.

The original single-town gameplay scene, eight triggers, seven actor slots,
and six facades remain untouched while these studies are evaluated.

## 2026-11-07: actual native water + forest synthesis comparison

A new source-only ecology pass is now staged under
`tools/aster_water_feature_study.py`, `tools/aster_lived_in_ecology.py`,
and `tools/aster_native_woodland_synthesis.py`.

**Positive result:** `aster_forest_synthesis.png` is meaningfully fuller
than the old grass prototype. Instead of rectangular source-terrain
cards or sparsely spaced 4x5 trees, the source program chooses authentic
Vale set_02 canopy metatiles according to neighboring rendered-pixel
edge compatibility and irregular forest-boundary coverage. This creates
a connected treeline around all four edges, plus smaller home-side
copses. No new pixel art or non-Golden-Sun assets were imported.

**Real water:** The eastern outskirts now include a source-only
nonmagical pond derived from original Vale water-bank and water-ripple
metatiles. The original Psynergy crystal/pedestal is deliberately
removed. Water and woodland are both native 16px source graphics.

**Everyday work:** One complete native Vale outbuilding appears on the
west service lane between occupied homes and the shop. There is a
working service approach, additional source-native flower beds and
small clusters of original wooden crates and water jars near trade and
homes. A source-only flood-fill confirms the eight planned event
coordinates and seven planned NPC anchor tiles remain reachable
after adding the forest, water and solid props.

**Remaining failures / release blockers:**
- Aster's central upper and middle lawns are STILL too empty. The
  forest boundary is successful but does not by itself make the market,
  memorial or commons a fully developed village.
- The pond still has a too-straight southern water edge; do not treat
  it as approved final coastline/bank geometry.
- The well remains an invisible solid place holder in these studies;
  a visible functional well must be developed without a Psynergy Stone.
- The western shed is VISUAL ONLY. Its door needs a sensible story/
  entrance policy before integration; do not add another fake door.
- No actual NPC walking routines or interiors are implemented.
- The compiled gameplay Map180 and `games/tbs/src/scene/aster.c`
  are still the previous old layout. Source-generated study images
  do NOT establish an emulator collision/priority/saving pass.

**Acceptance criterion:** Preserve the new connected forest technique,
but continue the **functional district design**. The water should have
a proper native bank, homes their working yards, the marketplace a
visible reason to exist, and the common area a usable meeting point.
Only after those source renders pass visual QA may the source geometry,
scene actors, eight triggers and door approaches be moved into Map180
together. Do not prematurely merge a prettier but still incomplete
study into the live Ashfall field map.

## New hard rule after rendered prototypes

**Terrain must be authored continuously across the whole village.**
Do not use disconnected 7- or 10-cell cliff cards, even if every pixel
comes from Golden Sun. Build a connected ridge, graded transitions and
woodland enclosing the town, with pathways following its contours. A
proper tile-by-tile level plan must come before more scenery stamps.
Leave the rejected life-first and cliff-card PNGs as evidence of the
problem, not as templates for the actual playable map.

The native screenshot references show a second important issue: the
settlement needs enough ordinary building and working-yard density to
support a functioning population. Six facades, even grouped closer,
remain insufficient without interiors, supporting structures and
purposeful public spaces. The next map layout must solve both density
and topography at once.

## Functional neighborhoods required in the final map

### North — an old but still inhabited street
The sealed home and duplicate home sit along a narrow, sensible
residential passage, not on opposing corners of an empty square. A modest
wooden memorial has maintained garden edges, weathered signs, and a
reason someone would tend it. *Other Isaac* is part of a later story
encounter; don't turn the entire street into a haunted ruin on arrival.

### Middle — the village's ordinary daily life
The two occupied homes look onto a shared commons and usable water source,
not a giant dirt crossroads. One family has a visible cultivated yard;
another has baskets, materials, or a small working space. A child has room
to play and an elder has somewhere to sit or watch. **The well MUST be a
recognizable nonmagical dry well**, not an invisible solid metatile, cliff
cave, Psynergy Stone or water spring.

### South — a functioning trade stop
The shop and inn face connected foot traffic near the arrival road.
A short goods-unloading/work area and an inn guest/utility yard should
look like services someone actually uses. Native crates/wood fencing are
appropriate only when attached to the building that uses them. Avoid
detached repetitive prop patches floating in grass.

### Boundaries
Use terrain to define the settlement before deciding how many trees to
add. The village should feel protected by a broken ridge, stepped path
and wooded outskirts. Use intact native Golden Sun three-layer tile
transitions; cropped rectangles, visible roof fragments and arbitrary
cliff blocks fail visual QA. Keep the actual usable settlement compact
without changing the 64x64 engine window unless necessary.

## Villagers cannot be seven talking signposts

At first arrival, stage positions and eventual safe movement patterns
should suggest a village operating normally:

| Resident | Ordinary work/place | Narrative opportunity |
| --- | --- | --- |
| Elder | Between central commons and memorial | Has maintained the town's stories |
| Greeter | South gate and shop road | Knows who comes through Aster |
| Innkeeper | Inn entrance and service area | Recognizes travelers, room occupancy |
| Boy | Commons or household errand | Notices the dry well changing |
| Resident | Garden or home threshold | Gives conflicting family memories |
| Mirror woman | Between eastern home and commons | Contradicts another resident |
| Other Isaac | Northern lane at controlled story stage | Must feel unusual *after* ordinary life is established |

This is a **design plan**, not implemented patrol code. Assigning extra
sprites or making all actors wander randomly is not a substitute for
safe, collision-checked daily routines.

Add a few mundane supporting villagers only where genuine jobs and
dialogue justify them: a shop worker/vendor, someone handling supplies,
and a visitor outside the inn are stronger than a crowd of idle clones.

## Interior and gameplay gates

At least the shop, inn and occupied homes need real interiors or
a well-justified, limited entry policy. The sealed home may intentionally
remain inaccessible as a plot beat; ordinary homes should not all act
like fake doors.

To move a prototype into the game, update the single Map180 generator,
`aster.c` actor templates/entrance positions, all eight event coordinates,
door approaches and narrative checks **in one reviewed change**. Confirm
workability and 27-character-per-line dialogue rules. Then test real
in-game layering, collisions, playable thresholds, NPC motions, saving
and two-way overworld travel.

**Acceptance question:** If the player never spoke to a single NPC,
would this look like a believable, functioning Golden Sun village?
If not, do not ship it and do not cover the problem with more scattered
decorations.
