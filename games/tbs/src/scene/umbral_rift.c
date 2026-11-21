/// Umbral Rift: an optional dungeon added by Golden Sun: Ashfall.
///
/// A black monolith that appeared in the fields outside Vale after Colosso.
/// This first version holds only the throne hall (UmbralThrone, map 0xba),
/// rebuilt from the Hydros statue hall with its pillared approach doubled.
#include "unit/scene/umbral_rift.h"
#include "script_operands.h"
#include "djinn_ids.h"
#include "flags.h"
#include "character_ids.h"
#include "save_block.h"
#include "heap_slots.h"
#include "scene_ids.h"
#include "unit/overworld/overworld.h"
#include "unit/window/window.h"
#include "unit/overworld/event_commands.h"
#include "unit/field/field.h"
#include "unit/runtime/runtime.h"
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
#include "event_layer.h"
#include "event_inline.h"
#include "world_state.h"
#include "scene_tables.h"
#include "actor.h"
#include "call.h"
#include "text/msg_ids.h"
#include "ability_ids.h"
#include "actor_script.h"
#include "fixed_math.h"
#include "palbuf.h"
#include "scene.h"
#include "songs.h"
#include "io_reg.h"
#include "audio_engine_symbols.h"
#include "item_ids.h"
#include "common/actor_facing.h"


enum {
  UMBRAL_THRONE_FROM_RIFT_BATTLE = 1,
};

enum {
  ACTOR_RIFT_MYSTERY = ACTOR_FIRST_PLACED,
  ACTOR_RIFT_HEART,
};

/// A won fight returns here (UMBRAL_THRONE_FROM_RIFT_BATTLE); a lost one goes
/// to the last Sanctum and leaves the pair waiting for a rematch.
s32 UmbralRift_Initialize(void) {
  if (gSaveBlock.entrance == UMBRAL_THRONE_FROM_RIFT_BATTLE &&
      GameFlag_Get(FLAG_DARK_RIFT_FOUGHT) != 0)
    GameFlag_Set(FLAG_DARK_RIFT_BEATEN);
  return 0;
}

/// "???" and Heart, together on the dais. Dialogue comes in a later pass.
static void UmbralRift_TalkToMystery(void) {
  Event_Start();
  GameFlag_Set(FLAG_DARK_RIFT_FOUGHT);
  Event_SetAfterBattleDestination((s32)&SceneId_UmbralThrone,
                                  UMBRAL_THRONE_FROM_RIFT_BATTLE);
  Event_SetDefeatDestination(-1, -1);
  Battle_SetType(BATTLE_TYPE_SCRIPTED);
  Field_RequestBattleFromEncounterTable(ENCOUNTER_ZONE_SCRIPTED_MIA_MENARDI, 7);
  Event_End();
}

static struct SceneEntrance sUmbralThroneEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 328, 0, 616, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_THRONE_FROM_RIFT_BATTLE, CONDITION_ALWAYS, 328, 0, 200,
     FACING_NORTH, 0, -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static u32 sUmbralThroneExits[] = {
    SCENE_EXITS(UmbralThrone),
    SCENE_EXITS_END,
};

static struct ActorTemplate sUmbralThroneActorTemplates[] = {
    // "???" on the dais and Heart below her, until they are beaten.
    {SPRITE_MYSTERY_LEADER, FLAG_DARK_RIFT_BEATEN, MOVEMENT_TYPE_STAND,
     PIXELS(328), 0, PIXELS(104), FACING_SOUTH, TALK_FACING_PARTY, 0},
    {SPRITE_WOMAN_WITH_PURPLE_HAIR, FLAG_DARK_RIFT_BEATEN, MOVEMENT_TYPE_STAND,
     PIXELS(296), 0, PIXELS(168), FACING_SOUTH, TALK_FACING_PARTY, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralThroneTriggers[] = {
    {TRIGGER_TALK, ACTOR_RIFT_MYSTERY, FLAG_DARK_RIFT_BEATEN,
     EVENT(UmbralRift_TalkToMystery)},
    {TRIGGER_TALK, ACTOR_RIFT_HEART, FLAG_DARK_RIFT_BEATEN,
     EVENT(UmbralRift_TalkToMystery)},
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
