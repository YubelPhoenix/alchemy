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

Aster now has a **new dedicated registered sprite**:
`SPRITE_WORLD_MAP_ASTER = 0x1f9` (decimal 505), at
`games/tbs/src/graphics/sprite/spr_505.png`.
This is an **actual 32×32, 8-bit indexed GBA-compatible source asset**,
drawn with 244 changed native-palette pixels, darker timber roofs and
stronger forest greens. It preserves the exact palette, 0-index transparency
silhouette and 32×32 draw/collision metadata of the unmodified original
`SPRITE_WORLD_MAP_VILLAGE = 0x105` sprite at `spr_261.png`.
The new icon's layout row, sprites.tsv metadata, animation table and ID
are registered on the isolated branch. A dedicated read-only source test:
`python3 tools/check_aster_world_icon.py`.

**Important**: Registered does not mean spawned into the world! We have
deliberately **NOT added an Aster world-map actor** at the unverified
candidate coordinates. Both final icon rendering and entry by proximity
must still be tested in a locally compiled experimental ROM. The existing
Vale, Vault and other village icons have not been changed.

For a safe coordinate check, the optional local build flag
`bash tools/aster_v14_local_smoke.sh --probe-world` temporarily
uses unused world-map entrance **98** to return from Aster to
`(5696,1536)` (32 pixels south of the Aster icon at `(5696,1504)`), without changing the story branch. The temporary edits
are restored automatically. The debug entrance was **not** used because
it disables map contacts and would hide progression failures.
The updated local-only probe also temporarily converts one unused world-map
signpost actor into Aster's icon and adds a test contact and exit at unused
exit kind 115. It does **not change the ID or position of any existing town,
Djinni, or story actor**. It lets the emulator tester approach Aster's icon,
enter the village, exit south, and walk back toward Vault. The original
source is restored after compilation. These coordinates and interactions
remain **unverified in the emulator**. Use only an experimental game save.

## Status

- Candidate site: **provisional**, source actor separation checked.
- World terrain/path from Vault: **untested**.
- Story progression conflicts: **untested**.
- New icon sprite: **created, source registered and source-audited**.
- Production world-map actor/contact/exit/entrance: **not edited**.
- Reversible local-only arrival probe: **implemented, not emulator-tested**.
- ROM build/emulator playtest: **not performed**.

Do not merge or call Aster release-ready on the basis of this report.
