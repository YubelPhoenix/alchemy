# Aster overworld placement — proposal, NOT APPROVED

Checked against `games/tbs/src/scene/world_map.c` on the isolated
`experiment/aster-v14-native-map-staging` branch, November 8, 2026.

## Geography and exact **candidate**

Place Aster as a small optional woodland settlement **west-northwest
of Vault, south of Vale, on the original Vale/Vault side of the damaged
Kalay passage**.

**Candidate world-coordinate (not yet validated): X=5696, Z=1504.**

The existing scene source explicitly places Vale at (5678,1200) and
Vault at (5848,1576). The candidate is about 168 world pixels from
the Vault icon and about 305 pixels from the Vale icon. Those are
static sprite-center distances, not verified accessible ground.

Source-only audit: `python3 tools/aster_overworld_site_audit.py`.

**Do not implement this coordinate until an in-emulator walkability check
shows a continuous traversable approach from Vault, a collision-safe
ground point for the party to emerge, and no existing event overlap.**
If the location is mountain, water, cliff, invisible impassable terrain
or off-route, choose the closest accessible clearing and rerun the audit
BEFORE committing source changes.

## Progression restrictions

- Keep Aster **optional**, reachable from the existing Vale/Vault
  overworld area only after checking that it does not interrupt Flint's
  introduction, the Vault thief sequence, Hammet's caravan, Goma Cave,
  or the broken southern bridge to Kalay. If required, gate its entrance
  using an existing story progression flag chosen by gameplay testing;
  do not invent a new permanent flag blindly.
- Preserve the current Aster map entrance at (32,61), its south
  interaction marker at (32,62), and sole open boundary at (32,63).
- On leaving the village, place Isaac just outside Aster's own icon,
  facing south, never at the present temporary Vault return.
- Test walking **from Vault to Aster and back**, then leaving Aster
  and re-entering without resetting the map or losing story flags.

## Engine wiring checks

The existing world-map uses `SPRITE_WORLD_MAP_VILLAGE` actor
templates for Vale, Vault and other villages. The active actor contact
scan uses `CONTACT_LAST_ACTOR = 65` and
`STEP_TRIGGER_AREA_BASE = 100`. Adding one more actor or exit can
shift actor IDs and invalidate existing trigger lookups. Review the
enum IDs, actor templates, alternate actor arrays, contact cutoff,
trigger table, world-map entrance table, world-map exit table,
destination scene and entrance direction **as one coordinated change**.

Do not simply append an actor to an array and assume the contact
handler sees it. Do not replace an existing world-map village actor.

## Aster overworld icon

For the FIRST smoke test, render using the existing native
`SPRITE_WORLD_MAP_VILLAGE = 0x105` sprite, not a painted static
symbol on the background.

The original file is
`games/tbs/src/graphics/sprite/spr_261.png`, **32×32 pixels,
8-bit indexed PNG** with animation data at `spr_261.tsv`.
It is shared by existing towns and must not be modified for Aster.

For the FINAL icon, add a **new registered sprite**, following the
source sprite's exact indexed palette, transparent index, animation,
layout/ID registration, drawing/collision dimensions and GBA
limitations. Recommended silhouette: a darker timber-roofed,
woodland-framed village, still recognizable as a settlement and
consistent with Golden Sun's native world-map art. Do not insert a
32×32 RGB PNG without indexing and linking it. The final sprite ID
is NOT allocated yet.

## Status

- Candidate site: **provisional**, source actor separation checked.
- World terrain/path from Vault: **untested**.
- Story progression conflicts: **untested**.
- New icon sprite: **not created or registered**.
- World-map actor/contact/exit/entrance: **not edited**.
- ROM build/emulator playtest: **not performed**.

Do not merge or call Aster release-ready on the basis of this report.
