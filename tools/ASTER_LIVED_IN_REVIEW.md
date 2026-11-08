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
2. `aster_lived_in_terrain.py`: wraps the same blockout with contiguous,
   original Vale cliff ridges and woodland strips chosen from the
   three-layer `aster_native_terrain_atlas.png`. The prototype treats
   them as provisional solid boundaries, **not verified game collision**.
   Review the image critically for seams and clipped cliff faces before
   incorporating anything into Map180.

The original single-town gameplay scene, eight triggers, seven actor slots,
and six facades remain untouched while these studies are evaluated.

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
