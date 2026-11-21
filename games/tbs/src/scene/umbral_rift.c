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
  /// Exit 1: the cells at the hall's south end, back to the Fountain Hall.
  UMBRAL_THRONE_TO_FOUNTAIN = 1,
};

/// The Fountain Hall: the first room inside the monolith (map 0xbb), Mercury
/// Lighthouse's fountain room in obsidian. Its jewel is the rift's black
/// crystal, the seal on the way to the throne.
enum {
  UMBRAL_FOUNTAIN_FROM_LEFT_ARCH = 1,
  UMBRAL_FOUNTAIN_FROM_RIGHT_ARCH = 2,
  UMBRAL_FOUNTAIN_FROM_CAUSEWAY = 3,
};
enum {
  /// Exit 1: the stair at the south end, out to the monolith.
  UMBRAL_FOUNTAIN_TO_WORLD_MAP = 1,
  /// Exit 2: the left arch, into the Twin Maze.
  UMBRAL_FOUNTAIN_TO_LEFT_ARCH = 2,
  /// Exit 3: the right arch, the shortcut back from the Memory Room's stair.
  UMBRAL_FOUNTAIN_TO_RIGHT_ARCH = 3,
  /// Exit 4: through the rift light at the pool, once the seal is lit.
  UMBRAL_FOUNTAIN_TO_CAUSEWAY = 4,
};

/// The Twin Maze (map row 0xbc): Sol Sanctum's maze pieces rebuilt as
/// long parallel corridors in obsidian. In at the south-east door, out at the
/// north-east door into the Memory Room.
enum {
  UMBRAL_MAZE_FROM_TOP_DOOR = 1,
};
enum {
  UMBRAL_MAZE_TO_FOUNTAIN = 1,
  UMBRAL_MAZE_TO_TOP_DOOR = 2,
};

/// The Memory Room (map row 0xbd): Isaac's house in Vale, rebuilt in obsidian
/// inside the rift. In at the front door from the maze; the stair at the top
/// left comes out at the Fountain Hall's right arch: the shortcut back.
enum {
  UMBRAL_MEMORY_FROM_STAIR = 1,
};
enum {
  UMBRAL_MEMORY_TO_MAZE = 1,
  UMBRAL_MEMORY_TO_STAIR = 2,
};

/// The Causeway (map row 0xbe): Mercury Lighthouse's long hall in obsidian, a
/// walk between void pools up to the throne. A rift light at its foot restores
/// the party.
enum {
  UMBRAL_CAUSEWAY_FROM_THRONE = 1,
};
enum {
  UMBRAL_CAUSEWAY_TO_FOUNTAIN = 1,
  UMBRAL_CAUSEWAY_TO_THRONE = 2,
};

/// The one placed actor in each of the Fountain Hall (the rift light that
/// opens on the seal), the Memory Room (the dark orb) and the Causeway (the
/// light that restores the party).
enum { ACTOR_RIFT_FEATURE = ACTOR_FIRST_PLACED };

enum {
  ACTOR_RIFT_MYSTERY = ACTOR_FIRST_PLACED,
  ACTOR_RIFT_HEART,
};

/// A won fight returns here (UMBRAL_THRONE_FROM_RIFT_BATTLE); a lost one goes
/// to the last Sanctum and leaves the pair waiting for a rematch.
static void UmbralRift_Aftermath(void);

s32 UmbralRift_Initialize(void) {
  // Back from the fight on the dais. A loss is handled by the restart point
  // (the fight flag is cleared there), so only a win returns here.
  if ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralThrone &&
      gSaveBlock.entrance == UMBRAL_THRONE_FROM_RIFT_BATTLE &&
      GameFlag_Get(FLAG_DARK_RIFT_FOUGHT) != 0 &&
      GameFlag_Get(FLAG_DARK_RIFT_BEATEN) == 0 &&
      gSaveBlock.sequenceResult != -1)
    UmbralRift_Aftermath();
  return 0;
}

/// After the win, ??? and Heart flicker black and are gone into the rift.
static void UmbralRift_Aftermath(void) {
  Event_Start();
  MapGrid_CenterOnFollowedPoint();
  WaitFrames(1);
  Event_StartScreenTransition();
  Event_WaitTransitionFrames();
  Event_WaitFrames(20);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK | SPRITE_COLOR_BLINK);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK | SPRITE_COLOR_BLINK);
  Event_WaitFrames(40);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_HIDDEN);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_HIDDEN);
  Actor_SetPosition(ACTOR_RIFT_MYSTERY, PIXELS(-9), PIXELS(488));
  Actor_SetPosition(ACTOR_RIFT_HEART, PIXELS(-9), PIXELS(488));
  GameFlag_Set(FLAG_DARK_RIFT_BEATEN);
  Event_End();
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
    SCENE_EXIT(UMBRAL_THRONE_TO_FOUNTAIN, UmbralCauseway, UMBRAL_CAUSEWAY_FROM_THRONE),
    SCENE_EXITS(UmbralFountain),
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_WORLD_MAP, WorldMap, WORLD_MAP_FROM_UMBRAL_RIFT),
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_LEFT_ARCH, UmbralMaze, ENTRANCE_DEFAULT),
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_RIGHT_ARCH, UmbralMemory, UMBRAL_MEMORY_FROM_STAIR),
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_CAUSEWAY, UmbralCauseway, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralMaze),
    SCENE_EXIT(UMBRAL_MAZE_TO_FOUNTAIN, UmbralFountain, UMBRAL_FOUNTAIN_FROM_LEFT_ARCH),
    SCENE_EXIT(UMBRAL_MAZE_TO_TOP_DOOR, UmbralMemory, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralMemory),
    SCENE_EXIT(UMBRAL_MEMORY_TO_MAZE, UmbralMaze, UMBRAL_MAZE_FROM_TOP_DOOR),
    SCENE_EXIT(UMBRAL_MEMORY_TO_STAIR, UmbralFountain, UMBRAL_FOUNTAIN_FROM_RIGHT_ARCH),
    SCENE_EXITS(UmbralCauseway),
    SCENE_EXIT(UMBRAL_CAUSEWAY_TO_FOUNTAIN, UmbralFountain, UMBRAL_FOUNTAIN_FROM_CAUSEWAY),
    SCENE_EXIT(UMBRAL_CAUSEWAY_TO_THRONE, UmbralThrone, ENTRANCE_DEFAULT),
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
    {TRIGGER_EXIT, UMBRAL_THRONE_TO_FOUNTAIN, CONDITION_ALWAYS,
     UMBRAL_THRONE_TO_FOUNTAIN},
    {TRIGGERS_END},
};

static struct SceneEntrance sUmbralFountainEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 136, 0, 232, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_FOUNTAIN_FROM_LEFT_ARCH, CONDITION_ALWAYS, 56, 0, 88, FACING_SOUTH,
     0, -1, -1, -1, -1, 0},
    {UMBRAL_FOUNTAIN_FROM_RIGHT_ARCH, CONDITION_ALWAYS, 216, 0, 88,
     FACING_SOUTH, 0, -1, -1, -1, -1, 0},
    {UMBRAL_FOUNTAIN_FROM_CAUSEWAY, CONDITION_ALWAYS, 136, 0, 232,
     FACING_SOUTH, 0, -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralFountainActorTemplates[] = {
    // The rift light at the pool's edge, before the statue: there once the
    // Memory Room's orb is lit.
    {SPRITE_FLOATING_LIGHT, IF_FLAG_SET(FLAG_DARK_RIFT_SEAL_LIT),
     MOVEMENT_TYPE_STAND, PIXELS(136), 0, PIXELS(200), FACING_SOUTH,
     TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralEmptyActorTemplates[] = {
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralMemoryActorTemplates[] = {
    // The dark orb, in the middle of the room.
    {SPRITE_FLOATING_LIGHT, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND, PIXELS(136), 0,
     PIXELS(168), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralCausewayActorTemplates[] = {
    // The rift light at the foot of the causeway, beside the walk.
    {SPRITE_FLOATING_LIGHT, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND, PIXELS(72),
     0, PIXELS(232), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

/// Through the rift light: on to the causeway.
static void UmbralRift_EnterRiftLight(void) {
  Event_Start();
  Import_EventSetExitRequest(UMBRAL_FOUNTAIN_TO_CAUSEWAY);
  Event_End();
}

/// The dark orb lights, and the seal in the Fountain Hall opens.
static void UmbralRift_LightOrb(void) {
  Event_Start();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_WHITE);
  Event_WaitFrames(20);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_NORMAL);
  GameFlag_Set(FLAG_DARK_RIFT_SEAL_LIT);
  Event_End();
}

/// The rest point: the party is restored.
static void UmbralRift_Rest(void) {
  Event_Start();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_WHITE);
  Party_RestoreHpPp(1);
  Event_WaitFrames(20);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_NORMAL);
  Event_End();
}

static struct Trigger sUmbralFountainTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_FOUNTAIN_TO_WORLD_MAP, CONDITION_ALWAYS,
     UMBRAL_FOUNTAIN_TO_WORLD_MAP},
    {TRIGGER_EXIT, UMBRAL_FOUNTAIN_TO_LEFT_ARCH, CONDITION_ALWAYS,
     UMBRAL_FOUNTAIN_TO_LEFT_ARCH},
    {TRIGGER_EXIT, UMBRAL_FOUNTAIN_TO_RIGHT_ARCH, CONDITION_ALWAYS,
     UMBRAL_FOUNTAIN_TO_RIGHT_ARCH},
    {TRIGGER_TALK, ACTOR_RIFT_FEATURE, IF_FLAG_SET(FLAG_DARK_RIFT_SEAL_LIT),
     EVENT(UmbralRift_EnterRiftLight)},
    {TRIGGERS_END},
};

static struct SceneEntrance sUmbralMazeEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 424, 0, 504, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_MAZE_FROM_TOP_DOOR, CONDITION_ALWAYS, 552, 0, 56, FACING_SOUTH, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralMazeTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_MAZE_TO_FOUNTAIN, CONDITION_ALWAYS,
     UMBRAL_MAZE_TO_FOUNTAIN},
    {TRIGGER_EXIT, UMBRAL_MAZE_TO_TOP_DOOR, CONDITION_ALWAYS,
     UMBRAL_MAZE_TO_TOP_DOOR},
    {TRIGGERS_END},
};

static struct SceneEntrance sUmbralMemoryEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 80, 0, 256, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_MEMORY_FROM_STAIR, CONDITION_ALWAYS, 72, 0, 104, FACING_SOUTH, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralMemoryTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_MEMORY_TO_MAZE, CONDITION_ALWAYS,
     UMBRAL_MEMORY_TO_MAZE},
    {TRIGGER_EXIT, UMBRAL_MEMORY_TO_STAIR, CONDITION_ALWAYS,
     UMBRAL_MEMORY_TO_STAIR},
    {TRIGGER_TALK, ACTOR_RIFT_FEATURE, FLAG_DARK_RIFT_SEAL_LIT,
     EVENT(UmbralRift_LightOrb)},
    {TRIGGERS_END},
};

static struct SceneEntrance sUmbralCausewayEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 88, 0, 264, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_CAUSEWAY_FROM_THRONE, CONDITION_ALWAYS, 88, 0, 88, FACING_SOUTH, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralCausewayTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_CAUSEWAY_TO_FOUNTAIN, CONDITION_ALWAYS,
     UMBRAL_CAUSEWAY_TO_FOUNTAIN},
    {TRIGGER_EXIT, UMBRAL_CAUSEWAY_TO_THRONE, CONDITION_ALWAYS,
     UMBRAL_CAUSEWAY_TO_THRONE},
    {TRIGGER_TALK, ACTOR_RIFT_FEATURE, CONDITION_ALWAYS, EVENT(UmbralRift_Rest)},
    {TRIGGERS_END},
};

#define UMBRAL_IN_CAUSEWAY() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralCauseway)

#define UMBRAL_IN_MEMORY() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralMemory)
#define UMBRAL_IN_MAZE() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralMaze)
#define UMBRAL_IN_FOUNTAIN() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralFountain)

const struct SceneEntrance *Scene_GetEntrances(void) {
  return UMBRAL_IN_CAUSEWAY()   ? sUmbralCausewayEntrances
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryEntrances
         : UMBRAL_IN_MAZE()     ? sUmbralMazeEntrances
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainEntrances
                                : sUmbralThroneEntrances;
}
const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }
const u32 *Scene_GetExits(void) { return sUmbralThroneExits; }
const struct ActorTemplate *Scene_GetActorTemplates(void) {
  return UMBRAL_IN_CAUSEWAY()   ? sUmbralCausewayActorTemplates
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryActorTemplates
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainActorTemplates
         : UMBRAL_IN_MAZE()     ? sUmbralEmptyActorTemplates
                                : sUmbralThroneActorTemplates;
}
const struct Trigger *Scene_GetTriggers(void) {
  return UMBRAL_IN_CAUSEWAY()   ? sUmbralCausewayTriggers
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryTriggers
         : UMBRAL_IN_MAZE()     ? sUmbralMazeTriggers
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainTriggers
                                : sUmbralThroneTriggers;
}
