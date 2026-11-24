/// @file
/// Sol Sanctum (SceneId_SolSanctumCorridor), a passage that joins two rooms of
/// SceneId_SolSanctumReliefs (sol_sanctum_entrance.c).
///
/// It places nobody and has no events but its two exits, one at each end:
/// SOL_SANCTUM_CORRIDOR_TO_SOL_SANCTUM_RELIEFS_WEST leads into the room
/// with the chest and SOL_SANCTUM_CORRIDOR_TO_SOL_SANCTUM_RELIEFS_EAST into
/// the room with the stepping stones. Its setup, SolSanctumRooms_Initialize
/// (common/sol_sanctum_init_zoom.h), is the one SceneId_SolSanctumMaze shares:
/// once Mt. Aleph has erupted (FLAG_SOL_SANCTUM_ERUPTED), the passage rumbles
/// and shakes.

#include "unit/scene/sol_sanctum_corridor.h"
#include "unit/scene/common/sol_sanctum_init_zoom.h"
#include "battle.h"
#include "debug.h"
#include "field.h"
#include "game.h"
#include "graphics.h"
#include "menu.h"
#include "minigame.h"
#include "sound.h"
#include "system.h"
#include "types.h"

#include "resource_37de_map.h"
#include "scene_tables.h"
#include "actor.h"

#include "event_layer.h"
#include "event_inline.h"
#include "flags.h"
#include "sprite_ids.h"
#include "unit/import.h"

const struct SceneEntrance *Scene_GetEntrances(void) {
  return gSolSanctumCorridorEntrances;
}

const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }

const u32 *Scene_GetExits(void) { return gSolSanctumCorridorExits; }

const struct ActorTemplate *Scene_GetActorTemplates(void) {
  return gSolSanctumCorridorActorTemplates;
}

/// Returns the passage's two exits, its only events.
const struct Trigger *Scene_GetTriggers(void) {
  return gSolSanctumCorridorTriggers;
}

#include "common/sol_sanctum_init_zoom.h"

struct SceneEntrance gSolSanctumCorridorEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 120, 0, 100, FACING_SOUTH, 0, -1, -1,
     -1, -1, 0},
    {SOL_SANCTUM_CORRIDOR_FROM_SOL_SANCTUM_RELIEFS_EAST, CONDITION_ALWAYS, 727,
     0, 92, FACING_NORTH, 0, -1, -1, -1, -1, 0},
    {SOL_SANCTUM_CORRIDOR_FROM_SOL_SANCTUM_RELIEFS_WEST, CONDITION_ALWAYS, 56,
     0, 616, FACING_SOUTH, 0, -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

u32 gSolSanctumCorridorExits[] = {
    SCENE_EXITS(SolSanctumCorridor),
    SCENE_EXIT(SOL_SANCTUM_CORRIDOR_TO_SOL_SANCTUM_RELIEFS_EAST,
               SolSanctumReliefs,
               SOL_SANCTUM_RELIEFS_FROM_SOL_SANCTUM_CORRIDOR_EAST),
    SCENE_EXIT(SOL_SANCTUM_CORRIDOR_TO_SOL_SANCTUM_RELIEFS_WEST,
               SolSanctumReliefs,
               SOL_SANCTUM_RELIEFS_FROM_SOL_SANCTUM_CORRIDOR_WEST),
    SCENE_EXITS_END,
};

/// The silent, cloaked watcher, placed off the map until her glimpse.
enum SolSanctumCorridorActorId {
  ACTOR_CORRIDOR_WATCHER = ACTOR_FIRST_PLACED,
};

struct ActorTemplate gSolSanctumCorridorActorTemplates[] = {
    {SPRITE_GAROH_HOODED_FIGURE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND, 0, 0, 0,
     FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

/// Stepping onto the middle of the long north-south hall: for a moment a
/// cloaked figure stands in the hall, a few steps ahead and just inside the
/// edge of the screen, watching the party. She says nothing and is gone. It
/// plays once (FLAG_DARK_WATCHER_SANCTUM_CORRIDOR).
static void SolSanctumCorridor_WatcherAppears(void) {
  Event_Start();
  GameFlag_Set(FLAG_DARK_WATCHER_SANCTUM_CORRIDOR);
  Actor_SetPosition(ACTOR_CORRIDOR_WATCHER, PIXELS(472), PIXELS(296));
  Actor_FaceDirection(ACTOR_CORRIDOR_WATCHER, FACING_SOUTH, 0);
  Import_ActorSetAnimation(ACTOR_CORRIDOR_WATCHER, ANIM_STAND);
  Event_WaitFrames(100);
  Actor_SetPosition(ACTOR_CORRIDOR_WATCHER, 0, 0);
  Event_End();
}

struct Trigger gSolSanctumCorridorTriggers[] = {
    {TRIGGER_EXIT, 1, CONDITION_ALWAYS,
     SOL_SANCTUM_CORRIDOR_TO_SOL_SANCTUM_RELIEFS_EAST},
    {TRIGGER_EXIT, 2, CONDITION_ALWAYS,
     SOL_SANCTUM_CORRIDOR_TO_SOL_SANCTUM_RELIEFS_WEST},
    {TRIGGER_STEP, 3, FLAG_DARK_WATCHER_SANCTUM_CORRIDOR,
     EVENT(SolSanctumCorridor_WatcherAppears)},
    {TRIGGERS_END},
};
