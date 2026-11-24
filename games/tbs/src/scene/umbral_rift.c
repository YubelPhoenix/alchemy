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

/// The Beacon Chamber (map row 0xbf): Venus Lighthouse's beacon chamber in
/// obsidian, a place the party has never seen, between the Causeway and the
/// Throne Hall. The Causeway's door comes out at the arch in the lower room; a
/// bridge over the drop leads up to the beacon, whose violet flame opens on
/// the Throne Hall.
enum {
  UMBRAL_BEACON_FROM_THRONE = 1,
};
enum {
  /// Exit 1: the arch in the lower room, back to the Causeway.
  UMBRAL_BEACON_TO_CAUSEWAY = 1,
  /// Exit 2: through the beacon (requested by UmbralRift_EnterBeacon).
  UMBRAL_BEACON_TO_THRONE = 2,
};
/// The chamber floor halfway up (first sight of the beacon) and the cells
/// before the beacon.
enum { UMBRAL_BEACON_SIGHT_STEP = 0x20, UMBRAL_BEACON_STEP = 0x21 };

/// The one placed actor in each of the Fountain Hall (the rift light that
/// opens on the seal), the Memory Room (the dark orb) and the Causeway (the
/// light that restores the party).
enum { ACTOR_RIFT_FEATURE = ACTOR_FIRST_PLACED };
/// ??? and Heart where they are glimpsed: after the feature in the Fountain
/// Hall and Memory Room, the only actors in the Twin Maze.
enum { ACTOR_PAIR_MYSTERY = ACTOR_FIRST_PLACED + 1, ACTOR_PAIR_HEART };
enum { ACTOR_MAZE_MYSTERY = ACTOR_FIRST_PLACED, ACTOR_MAZE_HEART };

enum {
  ACTOR_RIFT_MYSTERY = ACTOR_FIRST_PLACED,
  ACTOR_RIFT_HEART,
};

/// A won fight returns here (UMBRAL_THRONE_FROM_RIFT_BATTLE); a lost one goes
/// to the last Sanctum and leaves the pair waiting for a rematch.
static void UmbralRift_Aftermath(void);
static void UmbralRift_PairEcho(s32 mystery, s32 heart, s32 flag, s32 facing);
static void UmbralRift_PairShow(s32 mystery, s32 heart);
static void UmbralRift_PairDark(void);

/// The floor cells before each echo of ??? and Heart.
enum { UMBRAL_ECHO_STEP = 0x20 };

#define UMBRAL_SCENE_IS(name) ((s16)gSaveBlock.sceneId == (s32)&SceneId_##name)

/// One line of dialogue. Each line closes the party's portraits after it, as
/// Kolima_HeartSays does: left up, a portrait outlives its event (it stayed
/// on screen into the field and the menu), and the next line by the same
/// speaker opened an empty frame beside it.
static void UmbralRift_Say(s32 message, s32 actor) {
  // Keep the throne pair silhouetted across facing and message transitions.
  if (UMBRAL_SCENE_IS(UmbralThrone)) {
    Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
    Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  }
  Event_SetMessageId(message);
  Event_ShowMessageThenWait(actor, 0, 20);
  if (UMBRAL_SCENE_IS(UmbralThrone)) {
    Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
    Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  }
  Portrait_CloseWindow(ACTOR_PARTY_LEADER);
  Portrait_CloseWindow(ACTOR_GARET);
  Portrait_CloseWindow(ACTOR_IVAN);
  Portrait_CloseWindow(ACTOR_MIA);
}

static void UmbralRift_FountainDialogue(s32 afterEcho) {
  if (afterEcho) {
  UmbralRift_Say(MsgDarkRiftFountain008, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftFountain009, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftFountain010, ACTOR_PARTY_LEADER);
  } else {
  UmbralRift_Say(MsgDarkRiftFountain001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftFountain002, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftFountain003, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftFountain004, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftFountain005, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftFountain006, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftFountain007, ACTOR_PARTY_LEADER);
  }
}

static void UmbralRift_MazeDialogue(s32 afterEcho) {
  if (afterEcho) {
  UmbralRift_Say(MsgDarkRiftMaze008, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftMaze009, ACTOR_PARTY_LEADER);
  } else {
  UmbralRift_Say(MsgDarkRiftMaze001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftMaze002, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftMaze003, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftMaze004, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftMaze005, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftMaze006, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftMaze007, ACTOR_PARTY_LEADER);
  }
}

static void UmbralRift_MemoryDialogue(void) {
  UmbralRift_Say(MsgDarkRiftMemory001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftMemory002, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftMemory003, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftMemory004, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftMemory005, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftMemory006, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftMemory007, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftMemory008, ACTOR_PARTY_LEADER);
}

static void UmbralRift_OrbDialogue(void) {
  UmbralRift_Say(MsgDarkRiftOrb001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftOrb002, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftOrb003, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftOrb004, ACTOR_PARTY_LEADER);
}

// Called inside the gateway interaction, before changing rooms.
static void UmbralRift_GateEvent(void) {
  UmbralRift_Say(MsgDarkRiftGate001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftGate002, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftGate003, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftGate004, ACTOR_PARTY_LEADER);
  GameFlag_Set(FLAG_DARK_RIFT_GATE_SEEN);
}

static void UmbralRift_CausewayEvent(void) {
  Event_Start();
  // Run from the scene's start-up: bring the picture in before anyone speaks,
  // or the lines would play over a black screen.
  MapGrid_CenterOnFollowedPoint();
  WaitFrames(1);
  Event_StartScreenTransition();
  Event_WaitTransitionFrames();
  UmbralRift_Say(MsgDarkRiftCauseway001, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftCauseway002, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftCauseway003, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftCauseway004, ACTOR_PARTY_LEADER);
  GameFlag_Set(FLAG_DARK_RIFT_CAUSEWAY_SEEN);
  Event_End();
}

static void UmbralRift_CloseAnchor(void) {
  UmbralRift_Say(MsgDarkRiftSeal001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftSeal002, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftSeal003, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftSeal005, ACTOR_MIA);
  Sound_PlaySong(SE_WARP);
  MapGrid_SetShake(PIXELS(3), PIXELS(3), Q16_ONE);
  PaletteFade_SetTarget(RGB(31, 31, 31), PALETTES_ALL);
  PaletteFade_StartInterpolation(2);
  Event_WaitFrames(10);
  PaletteFade_SetTarget(PALETTE_TINT_NONE, PALETTES_ALL);
  PaletteFade_StartInterpolation(16);
  MapGrid_SetShake(-1, -1, 9 * Q16_ONE / 10);
  MapGrid_WaitForShakeToSettle();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_BLACK);
  UmbralRift_Say(MsgDarkRiftSeal007, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftSeal008, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftSeal009, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftSeal010, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftSeal011, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftSeal013, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftSeal014, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftSeal015, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftSeal016, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftSeal018, ACTOR_PARTY_LEADER);
  GameFlag_Set(FLAG_DARK_RIFT_ANCHOR_SEALED);
}


s32 UmbralRift_Initialize(void) {
  // Reaching the Memory Room by its front door (from the maze) opens the
  // Fountain Hall's right arch as the way back to it.
  if (UMBRAL_SCENE_IS(UmbralMemory) && gSaveBlock.entrance == ENTRANCE_DEFAULT)
    GameFlag_Set(FLAG_DARK_RIFT_SHORTCUT_OPEN);
  // The Fountain Hall's right arch is drawn bricked up (and solid) in the map;
  // once the shortcut is open, copy the open doorway (stored off-screen at
  // cells 20,20 and 20,21) back into the arch.
  if (UMBRAL_SCENE_IS(UmbralFountain) &&
      GameFlag_Get(FLAG_DARK_RIFT_SHORTCUT_OPEN) != 0)
    MapGrid_CopyMetatileCellsRect(20, 20, 1, 2, 13, 3);
  // ??? and Heart, drawn in black, stand in each room on the way until the
  // party walks up to them (the step triggers below); then they speak of
  // nothing, flicker out, and are gone for good.
  if (UMBRAL_SCENE_IS(UmbralFountain) &&
      GameFlag_Get(FLAG_DARK_RIFT_PAIR_FOUNTAIN) == 0)
    UmbralRift_PairShow(ACTOR_PAIR_MYSTERY, ACTOR_PAIR_HEART);
  if (UMBRAL_SCENE_IS(UmbralMaze) && GameFlag_Get(FLAG_DARK_RIFT_PAIR_MAZE) == 0)
    UmbralRift_PairShow(ACTOR_MAZE_MYSTERY, ACTOR_MAZE_HEART);
  if (UMBRAL_SCENE_IS(UmbralMemory) &&
      GameFlag_Get(FLAG_DARK_RIFT_PAIR_MEMORY) == 0)
    UmbralRift_PairShow(ACTOR_PAIR_MYSTERY, ACTOR_PAIR_HEART);
  // Show each scene once and keep the closed anchor dark on later visits.
  if (UMBRAL_SCENE_IS(UmbralCauseway) &&
      gSaveBlock.entrance == ENTRANCE_DEFAULT &&
      GameFlag_Get(FLAG_DARK_RIFT_CAUSEWAY_SEEN) == 0)
    UmbralRift_CausewayEvent();
  if (UMBRAL_SCENE_IS(UmbralFountain) &&
      GameFlag_Get(FLAG_DARK_RIFT_ANCHOR_SEALED) != 0)
    Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_BLACK);
  // On the dais they are black too, until the fight.
  if (UMBRAL_SCENE_IS(UmbralThrone) && GameFlag_Get(FLAG_DARK_RIFT_BEATEN) == 0 &&
      !(gSaveBlock.entrance == UMBRAL_THRONE_FROM_RIFT_BATTLE &&
        GameFlag_Get(FLAG_DARK_RIFT_FOUGHT) != 0))
    UmbralRift_PairDark();
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

/// Flickers two actors between black and gone, staying black (a blink would
/// show their colours).
static void UmbralRift_FlickerOut(s32 a, s32 b) {
  s32 i;
  for (i = 0; i < 6; i++) {
    Actor_ConfigureSpriteColor(a, SPRITE_COLOR_HIDDEN);
    Actor_ConfigureSpriteColor(b, SPRITE_COLOR_HIDDEN);
    Event_WaitFrames(3 + i);
    Actor_ConfigureSpriteColor(a, SPRITE_COLOR_BLACK);
    Actor_ConfigureSpriteColor(b, SPRITE_COLOR_BLACK);
    Event_WaitFrames(6 - i);
  }
}

/// ??? and Heart stand in black as the room fades in, a moment, then flicker
/// and are gone; `flag` keeps them gone.
/// ??? and Heart, drawn in black, waiting where the party will find them.
/// Nothing is said here: the start-up must not open message windows while
/// the area's name is still on screen.
static void UmbralRift_PairShow(s32 mystery, s32 heart) {
  Event_Start();
  Actor_ConfigureSpriteColor(mystery, SPRITE_COLOR_BLACK);
  Actor_ConfigureSpriteColor(heart, SPRITE_COLOR_BLACK);
  Event_End();
}

/// The party walks up to the echo: the leader turns to face it, the party
/// reacts, it flickers out, and `flag` keeps it gone.
static void UmbralRift_PairEcho(s32 mystery, s32 heart, s32 flag, s32 facing) {
  Event_Start();
  Actor_FaceDirection(ACTOR_PARTY_LEADER, facing, 0);
  Event_WaitFrames(30);
  // The silhouettes are echoes of where they walked earlier.
  Sound_PlaySong(SE_WARP);
  if (flag == FLAG_DARK_RIFT_PAIR_FOUNTAIN)
    UmbralRift_FountainDialogue(0);
  else if (flag == FLAG_DARK_RIFT_PAIR_MAZE)
    UmbralRift_MazeDialogue(0);
  else if (flag == FLAG_DARK_RIFT_PAIR_MEMORY)
    UmbralRift_MemoryDialogue();
  UmbralRift_FlickerOut(mystery, heart);
  Actor_ConfigureSpriteColor(mystery, SPRITE_COLOR_HIDDEN);
  Actor_ConfigureSpriteColor(heart, SPRITE_COLOR_HIDDEN);
  Actor_SetPosition(mystery, PIXELS(-9), PIXELS(488));
  Actor_SetPosition(heart, PIXELS(-9), PIXELS(488));
  // Let the witnesses react once the images have disappeared.
  if (flag == FLAG_DARK_RIFT_PAIR_FOUNTAIN)
    UmbralRift_FountainDialogue(1);
  else if (flag == FLAG_DARK_RIFT_PAIR_MAZE)
    UmbralRift_MazeDialogue(1);
  GameFlag_Set(flag);
  Event_End();
}

/// Step triggers on the floor before each echo (metatile behavior
/// UMBRAL_ECHO_STEP): the leader turns toward them as the scene plays.
static void UmbralRift_ApproachFountainEcho(void) {
  UmbralRift_PairEcho(ACTOR_PAIR_MYSTERY, ACTOR_PAIR_HEART,
                      FLAG_DARK_RIFT_PAIR_FOUNTAIN, FACING_WEST);
}
static void UmbralRift_ApproachMazeEcho(void) {
  UmbralRift_PairEcho(ACTOR_MAZE_MYSTERY, ACTOR_MAZE_HEART,
                      FLAG_DARK_RIFT_PAIR_MAZE, FACING_WEST);
}
static void UmbralRift_ApproachMemoryEcho(void) {
  UmbralRift_PairEcho(ACTOR_PAIR_MYSTERY, ACTOR_PAIR_HEART,
                      FLAG_DARK_RIFT_PAIR_MEMORY, FACING_NORTH);
}

/// ??? and Heart on the dais, drawn in black.
static void UmbralRift_PairDark(void) {
  Event_Start();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  Event_End();
}

/// Post-battle dialogue comes before ??? and Heart leave. Isaac speaks first.
static void UmbralRift_Aftermath(void) {
  Event_Start();
  MapGrid_CenterOnFollowedPoint();
  WaitFrames(1);
  Event_StartScreenTransition();
  Event_WaitTransitionFrames();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  UmbralRift_Say(MsgDarkRiftPost001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost002, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost003, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost004, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost005, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPost006, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost010, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost011, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost012, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost013, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost014, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPost015, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost016, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPost017, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost018, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost019, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost020, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPost021, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost025, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost026, ACTOR_RIFT_MYSTERY);
  Event_WaitFrames(20);
  UmbralRift_FlickerOut(ACTOR_RIFT_MYSTERY, ACTOR_RIFT_HEART);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_HIDDEN);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_HIDDEN);
  Actor_SetPosition(ACTOR_RIFT_MYSTERY, PIXELS(-9), PIXELS(488));
  Actor_SetPosition(ACTOR_RIFT_HEART, PIXELS(-9), PIXELS(488));
  GameFlag_Set(FLAG_DARK_RIFT_BEATEN);
  Event_End();
}

/// ??? remains a silhouette, and Heart never reveals her scarred face.
static void UmbralRift_TalkToMystery(void) {
  Event_Start();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  UmbralRift_Say(MsgDarkRiftPre001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre002, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre003, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre004, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre005, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre006, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre007, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre008, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre009, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre010, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre011, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre012, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre013, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre014, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre015, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre016, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre017, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre018, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre019, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre020, ACTOR_RIFT_MYSTERY);
  if (GameFlag_Get(FLAG_DARK_RIFT_PAIR_FOUNTAIN) != 0 ||
      GameFlag_Get(FLAG_DARK_RIFT_PAIR_MAZE) != 0 ||
      GameFlag_Get(FLAG_DARK_RIFT_PAIR_MEMORY) != 0) {
    UmbralRift_Say(MsgDarkRiftPre021, ACTOR_PARTY_LEADER);
    UmbralRift_Say(MsgDarkRiftPre022, ACTOR_RIFT_MYSTERY);
  }
  UmbralRift_Say(MsgDarkRiftPre023, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre024, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre025, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre026, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre028, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre029, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre030, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre032, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre033, ACTOR_RIFT_HEART);

  Sound_PlaySong(SE_THUNDER_LOUD);
  PaletteFade_SetTarget(RGB(31, 31, 31), PALETTES_ALL);
  PaletteFade_StartInterpolation(1);
  MapGrid_SetShake(PIXELS(4), PIXELS(4), Q16_ONE);
  Event_WaitFrames(8);
  PaletteFade_SetTarget(PALETTE_TINT_NONE, PALETTES_ALL);
  PaletteFade_StartInterpolation(16);
  MapGrid_SetShake(-1, -1, 9 * Q16_ONE / 10);
  MapGrid_WaitForShakeToSettle();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  Actor_FaceDirection(ACTOR_RIFT_HEART, FACING_NORTH, 12);
  UmbralRift_Say(MsgDarkRiftPre034, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre035, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre036, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre038, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre039, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre040, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre041, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre042, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre043, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre044, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre045, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre046, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftPre047, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre048, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre049, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre050, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre051, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre052, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre054, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre055, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre056, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre057, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre058, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre059, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre061, ACTOR_RIFT_MYSTERY);
  Event_WaitFrames(20);
  UmbralRift_Say(MsgDarkRiftPre065, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre067, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre069, ACTOR_RIFT_MYSTERY);

  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  Actor_FaceDirection(ACTOR_RIFT_HEART, FACING_NORTH, 12);
  UmbralRift_Say(MsgDarkRiftPre070, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre071, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre072, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre073, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre074, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftPre075, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre076, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre077, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre078, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre079, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre080, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre081, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre082, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre083, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre087, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre088, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre089, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre090, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre091, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre092, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre093, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre094, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre095, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre096, ACTOR_PARTY_LEADER);
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
    SCENE_EXIT(UMBRAL_THRONE_TO_FOUNTAIN, UmbralBeacon, UMBRAL_BEACON_FROM_THRONE),
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
    SCENE_EXIT(UMBRAL_CAUSEWAY_TO_THRONE, UmbralBeacon, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralBeacon),
    SCENE_EXIT(UMBRAL_BEACON_TO_CAUSEWAY, UmbralCauseway, UMBRAL_CAUSEWAY_FROM_THRONE),
    SCENE_EXIT(UMBRAL_BEACON_TO_THRONE, UmbralThrone, ENTRANCE_DEFAULT),
    SCENE_EXITS_END,
};

static struct ActorTemplate sUmbralThroneActorTemplates[] = {
    // "???" and Heart side by side on the dais, until they are beaten.
    {SPRITE_MYSTERY_LEADER, FLAG_DARK_RIFT_BEATEN, MOVEMENT_TYPE_STAND,
     PIXELS(320), 0, PIXELS(104), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SPRITE_WOMAN_WITH_PURPLE_HAIR, FLAG_DARK_RIFT_BEATEN, MOVEMENT_TYPE_STAND,
     PIXELS(336), 0, PIXELS(104), FACING_SOUTH, TALK_FACING_KEEP, 0},
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
    // ??? and Heart on the ledge toward the left arch, the first time.
    {SPRITE_MYSTERY_LEADER, FLAG_DARK_RIFT_PAIR_FOUNTAIN, MOVEMENT_TYPE_STAND,
     PIXELS(56), 0, PIXELS(184), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SPRITE_WOMAN_WITH_PURPLE_HAIR, FLAG_DARK_RIFT_PAIR_FOUNTAIN,
     MOVEMENT_TYPE_STAND, PIXELS(80), 0, PIXELS(192), FACING_SOUTH,
     TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralMazeActorTemplates[] = {
    // ??? and Heart down the first corridor, watching, the first time.
    {SPRITE_MYSTERY_LEADER, FLAG_DARK_RIFT_PAIR_MAZE, MOVEMENT_TYPE_STAND,
     PIXELS(360), 0, PIXELS(500), FACING_EAST, TALK_FACING_KEEP, 0},
    {SPRITE_WOMAN_WITH_PURPLE_HAIR, FLAG_DARK_RIFT_PAIR_MAZE,
     MOVEMENT_TYPE_STAND, PIXELS(340), 0, PIXELS(512), FACING_EAST,
     TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralMemoryActorTemplates[] = {
    // The dark orb, against the back wall: out of the walkway (row 10) that
    // joins the two halves of the room, so it no longer blocks the stair.
    {SPRITE_FLOATING_LIGHT, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND, PIXELS(168), 0,
     PIXELS(98), FACING_SOUTH, TALK_FACING_KEEP, 0},
    // ??? and Heart in the middle of Isaac's home, the first time (gone after
    // the echo, so they never block the walkway).
    {SPRITE_MYSTERY_LEADER, FLAG_DARK_RIFT_PAIR_MEMORY, MOVEMENT_TYPE_STAND,
     PIXELS(104), 0, PIXELS(166), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SPRITE_WOMAN_WITH_PURPLE_HAIR, FLAG_DARK_RIFT_PAIR_MEMORY,
     MOVEMENT_TYPE_STAND, PIXELS(168), 0, PIXELS(166), FACING_SOUTH,
     TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralCausewayActorTemplates[] = {
    // The rift light at the foot of the causeway, beside the walk.
    {SPRITE_FLOATING_LIGHT, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND, PIXELS(104),
     0, PIXELS(232), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

/// The first interaction after the fight seals the anchor; later visits can
/// still use the gateway to explore the stabilized rooms.
static void UmbralRift_EnterRiftLight(void) {
  Event_Start();
  if (GameFlag_Get(FLAG_DARK_RIFT_BEATEN) != 0 &&
      GameFlag_Get(FLAG_DARK_RIFT_ANCHOR_SEALED) == 0)
    UmbralRift_CloseAnchor();
  else {
    if (GameFlag_Get(FLAG_DARK_RIFT_GATE_SEEN) == 0)
      UmbralRift_GateEvent();
    Import_EventSetExitRequest(UMBRAL_FOUNTAIN_TO_CAUSEWAY);
  }
  Event_End();
}

/// The dark orb lights, and the seal in the Fountain Hall opens.
static void UmbralRift_LightOrb(void) {
  Event_Start();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_WHITE);
  Event_WaitFrames(20);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_FEATURE, SPRITE_COLOR_NORMAL);
  Sound_PlaySong(SE_WARP);
  GameFlag_Set(FLAG_DARK_RIFT_SEAL_LIT);
  UmbralRift_OrbDialogue();
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
    // The right arch is a shortcut only once the Memory Room has been reached
    // through the maze; before that it leads nowhere.
    {TRIGGER_EXIT, UMBRAL_FOUNTAIN_TO_RIGHT_ARCH,
     IF_FLAG_SET(FLAG_DARK_RIFT_SHORTCUT_OPEN), UMBRAL_FOUNTAIN_TO_RIGHT_ARCH},
    {TRIGGER_TALK, ACTOR_RIFT_FEATURE, IF_FLAG_SET(FLAG_DARK_RIFT_SEAL_LIT),
     EVENT(UmbralRift_EnterRiftLight)},
    {TRIGGER_STEP, UMBRAL_ECHO_STEP, FLAG_DARK_RIFT_PAIR_FOUNTAIN,
     EVENT(UmbralRift_ApproachFountainEcho)},
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
    {TRIGGER_STEP, UMBRAL_ECHO_STEP, FLAG_DARK_RIFT_PAIR_MAZE,
     EVENT(UmbralRift_ApproachMazeEcho)},
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
    {TRIGGER_STEP, UMBRAL_ECHO_STEP, FLAG_DARK_RIFT_PAIR_MEMORY,
     EVENT(UmbralRift_ApproachMemoryEcho)},
    {TRIGGERS_END},
};

static struct SceneEntrance sUmbralCausewayEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 120, 0, 264, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_CAUSEWAY_FROM_THRONE, CONDITION_ALWAYS, 120, 0, 88, FACING_SOUTH, 0,
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

/// The first look at the beacon, halfway up the chamber.
static void UmbralRift_SeeBeacon(void) {
  Event_Start();
  Sound_PlaySong(SE_WARP);
  Event_WaitFrames(20);
  UmbralRift_Say(MsgDarkRiftBeacon001, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftBeacon002, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftBeacon003, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftBeacon004, ACTOR_IVAN);
  GameFlag_Set(FLAG_DARK_RIFT_BEACON_SEEN);
  Event_End();
}

/// Through the beacon and out in the Throne Hall; the party talks it over the
/// first time.
static void UmbralRift_EnterBeacon(void) {
  Event_Start();
  if (GameFlag_Get(FLAG_DARK_RIFT_BEACON_CROSSED) == 0) {
    UmbralRift_Say(MsgDarkRiftCross001, ACTOR_GARET);
    UmbralRift_Say(MsgDarkRiftCross002, ACTOR_IVAN);
    UmbralRift_Say(MsgDarkRiftCross003, ACTOR_MIA);
    UmbralRift_Say(MsgDarkRiftCross004, ACTOR_PARTY_LEADER);
    GameFlag_Set(FLAG_DARK_RIFT_BEACON_CROSSED);
  }
  Sound_PlaySong(SE_WARP);
  MapGrid_SetShake(PIXELS(2), PIXELS(2), Q16_ONE);
  Event_WaitFrames(16);
  Import_EventSetExitRequest(UMBRAL_BEACON_TO_THRONE);
  Event_End();
}

static struct SceneEntrance sUmbralBeaconEntrances[] = {
    // Through the Causeway's door, out of the arch in the lower room.
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 200, 0, 360, FACING_SOUTH, 0, -1, -1,
     -1, -1, 0},
    // Back out of the Throne Hall, below the beacon.
    {UMBRAL_BEACON_FROM_THRONE, CONDITION_ALWAYS, 168, 0, 152, FACING_SOUTH, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralBeaconActorTemplates[] = {
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralBeaconTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_BEACON_TO_CAUSEWAY, CONDITION_ALWAYS,
     UMBRAL_BEACON_TO_CAUSEWAY},
    {TRIGGER_STEP, UMBRAL_BEACON_SIGHT_STEP, FLAG_DARK_RIFT_BEACON_SEEN,
     EVENT(UmbralRift_SeeBeacon)},
    {TRIGGER_STEP, UMBRAL_BEACON_STEP, CONDITION_ALWAYS,
     EVENT(UmbralRift_EnterBeacon)},
    {TRIGGERS_END},
};

#define UMBRAL_IN_BEACON() ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralBeacon)

#define UMBRAL_IN_CAUSEWAY() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralCauseway)

#define UMBRAL_IN_MEMORY() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralMemory)
#define UMBRAL_IN_MAZE() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralMaze)
#define UMBRAL_IN_FOUNTAIN() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralFountain)

const struct SceneEntrance *Scene_GetEntrances(void) {
  return UMBRAL_IN_BEACON()      ? sUmbralBeaconEntrances
         : UMBRAL_IN_CAUSEWAY() ? sUmbralCausewayEntrances
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryEntrances
         : UMBRAL_IN_MAZE()     ? sUmbralMazeEntrances
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainEntrances
                                : sUmbralThroneEntrances;
}
const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }
const u32 *Scene_GetExits(void) { return sUmbralThroneExits; }
const struct ActorTemplate *Scene_GetActorTemplates(void) {
  return UMBRAL_IN_BEACON()      ? sUmbralBeaconActorTemplates
         : UMBRAL_IN_CAUSEWAY() ? sUmbralCausewayActorTemplates
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryActorTemplates
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainActorTemplates
         : UMBRAL_IN_MAZE()     ? sUmbralMazeActorTemplates
                                : sUmbralThroneActorTemplates;
}
const struct Trigger *Scene_GetTriggers(void) {
  return UMBRAL_IN_BEACON()      ? sUmbralBeaconTriggers
         : UMBRAL_IN_CAUSEWAY() ? sUmbralCausewayTriggers
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryTriggers
         : UMBRAL_IN_MAZE()     ? sUmbralMazeTriggers
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainTriggers
                                : sUmbralThroneTriggers;
}
