/// @file
/// Aster exterior prototype (SceneId_Aster). Not yet entered from world map.
/// The south exit temporarily leads to Vault's proven world-map arrival.
#include "types.h"
#include "field.h"
#include "scene_tables.h"
#include "actor.h"
#include "graphics.h"
#include "macros.h"

enum { ASTER_TO_WORLD_MAP = 1 };
enum AsterActorId {
  ACTOR_ASTER_ELDER = ACTOR_FIRST_PLACED,
  ACTOR_ASTER_INNKEEPER,
};

static struct SceneEntrance sAsterEntrances[] = {
    { ENTRANCE_DEFAULT, CONDITION_ALWAYS, 240, 0, 448,
      FACING_NORTH, 0, -1, -1, -1, -1, 0 },
    { SCENE_TABLE_END },
};
static u32 sAsterExits[] = {
    SCENE_EXITS(Aster),
    SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, WORLD_MAP_FROM_VAULT_SOUTH),
    SCENE_EXITS_END,
};
static struct ActorTemplate sAsterActors[] = {
    { SPRITE_OLD_MAN_WITH_CANE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
      PIXELS(192), 0, PIXELS(256), FACING_SOUTH, TALK_FACING_PARTY, 0 },
    { SPRITE_WOMAN_IN_BLUE_DRESS, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
      PIXELS(320), 0, PIXELS(272), FACING_SOUTH, TALK_FACING_PARTY, 0 },
    { SCENE_TABLE_END },
};
static struct Trigger sAsterTriggers[] = {
    { TRIGGER_EXIT, 1, CONDITION_ALWAYS, ASTER_TO_WORLD_MAP },
    { TRIGGERS_END },
};
s32 Scene_Initialize(void) { return 0; }
const struct SceneEntrance *Scene_GetEntrances(void) { return sAsterEntrances; }
const u32 *Scene_GetExits(void) { return sAsterExits; }
const struct ActorTemplate *Scene_GetActorTemplates(void) { return sAsterActors; }
const struct Trigger *Scene_GetTriggers(void) { return sAsterTriggers; }
const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }
