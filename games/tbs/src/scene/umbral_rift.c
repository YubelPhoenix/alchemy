/// Umbral Rift: an optional dungeon added by Golden Sun: Ashfall.
///
/// A black monolith that appeared in the fields outside Vale after Colosso.
/// This first version holds only the throne hall (UmbralThrone, map 0xba),
/// rebuilt from the Hydros statue hall with its pillared approach doubled.
#include "unit/scene/umbral_rift.h"
#include "field.h"
#include "game.h"
#include "system.h"
#include "types.h"
#include "scene_tables.h"
#include "actor.h"
#include "event_layer.h"
#include "flags.h"

s32 UmbralRift_Initialize(void) { return 0; }

static struct SceneEntrance sUmbralThroneEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 328, 0, 616, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {SCENE_TABLE_END},
};

static u32 sUmbralThroneExits[] = {
    SCENE_EXITS(UmbralThrone),
    SCENE_EXITS_END,
};

static struct ActorTemplate sUmbralThroneActorTemplates[] = {
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralThroneTriggers[] = {
    {TRIGGERS_END},
};

const struct SceneEntrance *Scene_GetEntrances(void) {
  return sUmbralThroneEntrances;
}
const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }
const u32 *Scene_GetExits(void) { return sUmbralThroneExits; }
const struct ActorTemplate *Scene_GetActorTemplates(void) {
  return sUmbralThroneActorTemplates;
}
const struct Trigger *Scene_GetTriggers(void) { return sUmbralThroneTriggers; }
