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
#include "engine_call.h"


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
  UMBRAL_MAZE_FROM_RITUAL = 2,
  /// Back out of Vale or Kolima, in the spur beside the statue.
  UMBRAL_MAZE_FROM_VIGIL = 3,
};
enum {
  UMBRAL_MAZE_TO_FOUNTAIN = 1,
  UMBRAL_MAZE_TO_TOP_DOOR = 2,
  /// The east door at the end of the middle corridor, into the Ritual Room.
  UMBRAL_MAZE_TO_RITUAL = 3,
  /// The end of the short spur off the west corridor, past the statue that
  /// stands there: on into Vale.
  UMBRAL_MAZE_TO_VIGIL = 4,
};

/// The Ritual Room (map row 0xc1): a small chamber of Mercury Lighthouse in
/// obsidian, off the maze's east door, with a pentagram burned into its floor
/// (new tiles in graphics/tileset/umbral_ritual) and a chest in its left
/// alcove: the first trace of whoever else has been using the Rift.
enum {
  /// Exit 1: the arch back to the maze.
  UMBRAL_RITUAL_TO_MAZE = 1,
};
/// Entrance 1: back under the arch after the fight with Karis.
enum { UMBRAL_RITUAL_FROM_KARIS_BATTLE = 1 };
/// The chest at the pentagram's heart, where the Wraith stood (treasure spot
/// and trigger subject 100).
enum { UMBRAL_RITUAL_CHEST = 100 };
/// The first row of the pentagram, just inside the arch.
enum { UMBRAL_RITUAL_STEP = 0x20 };
/// The Vengeful Wraith (Dark Dawn's Karis), standing black at the
/// pentagram's heart until she is beaten.
enum { ACTOR_RITUAL_KARIS = ACTOR_FIRST_PLACED };

/// Babi's statue room pulled into the Rift. The two dedicated statue sprites
/// use previously unused sprite slots; the original Lady Statue is untouched.
enum {
  UMBRAL_PALACE_FROM_MEMORY = 1,
  UMBRAL_PALACE_TO_MAZE = 1,
  UMBRAL_PALACE_TO_MEMORY = 6,
  SPRITE_UMBRAL_STATUE_TWO_FACE = 505,
  SPRITE_UMBRAL_STATUE_ELONGATED = 506,
};

/// The Vigil (map row 0xc3, map_194): Vale's plaza, cut from map_003, as the
/// Rift rebuilt it from the night of the storm. Every door is shut and the
/// pond is gone, grassed over. Five weeping statues stand round where it was.
/// They never move while the leader faces them; while his back is turned
/// they come for him (UmbralRift_WatchVigil). One that reaches him turns him
/// to stone for a moment, and the party is back at the cave mouth with the
/// statues where they began, and one more of them by the cave each time, up
/// to three. In at the cave mouth (from the maze), out by the arch at the
/// south.
enum {
  UMBRAL_VIGIL_FROM_GROVE = 1,
  /// Exit 1: the cave mouth under the cliff, back to the maze.
  UMBRAL_VIGIL_TO_MAZE = 1,
  /// Exit 2: the path through the arch at the south, on into Kolima.
  UMBRAL_VIGIL_TO_GROVE = 2,
  /// Exit 3: caught by a statue; back in at the cave mouth.
  UMBRAL_VIGIL_CAUGHT = 3,
  /// The wreathed maiden statue as weeping stone (spr_507,
  /// tools/dark_story/build_umbral_vigil_art.py).
  SPRITE_UMBRAL_VIGIL_STATUE = 507,
  /// SPRITE_UMBRAL_VIGIL_STATUE's animation once she has moved: sockets wide,
  /// mouth open.
  UMBRAL_VIGIL_STATUE_MOVED = 2,
  /// The five round the old pond, then the three by the cave for catches.
  UMBRAL_VIGIL_STATUES = 8,
  UMBRAL_VIGIL_EXTRA_FIRST = 5,
  /// A statue this close (in pixels) while unseen has caught the leader.
  UMBRAL_VIGIL_CATCH_DISTANCE = 16,
  /// Frames the leader stands as stone before the party is sent back.
  UMBRAL_VIGIL_STONE_FRAMES = 60,
};

/// The Grove (map row 0xc4, map_195): Kolima, cut whole from map_037, where
/// wood and skin are one thing. Its great stumps are flesh; among their roots,
/// in the clearing and penned in the fold stand Kolima's people half become
/// trees, mouths open, breathing. They are silent, as is Vale. In from Vale
/// at the west edge, out at the east edge into the maze's spur again.
enum {
  UMBRAL_GROVE_FROM_VIGIL = 1,
  /// Exit 1: the west edge, back to Vale.
  UMBRAL_GROVE_TO_VIGIL = 1,
  /// Exit 2: the east edge, which comes out in the maze's spur.
  UMBRAL_GROVE_TO_MAZE = 2,
  /// Kolima's people half become trees: waist up a villager, crown and
  /// raised arms gone to dead wood, trunk and roots below (spr_508,
  /// tools/dark_story/build_umbral_grove_art.py).
  SPRITE_UMBRAL_GROVE_FIGURE = 508,
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

/// The Crossbone room (map row 0xc0): Crossbone Isle's room of spikes and ice
/// pillars in obsidian, between the Fountain Hall's left arch and the maze.
/// The party comes in at the left door and leaves by the right one, winding
/// between the spikes.
enum {
  UMBRAL_CROSSBONE_FROM_MAZE = 1,
};
enum {
  /// Exit 1: the left door, back to the Fountain Hall.
  UMBRAL_CROSSBONE_TO_FOUNTAIN = 1,
  /// Exit 2: the right door, on to the maze.
  UMBRAL_CROSSBONE_TO_MAZE = 2,
};
/// The floor just inside the left door.
enum { UMBRAL_CROSSBONE_STEP = 0x20 };

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
static void UmbralRift_KarisAftermath(void);
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
  if (UMBRAL_SCENE_IS(UmbralThrone) &&
      GameFlag_Get(FLAG_DARK_RIFT_BEATEN) == 0) {
    Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
    Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  }
  Event_SetMessageId(message);
  Event_ShowMessageThenWait(actor, 0, 20);
  if (UMBRAL_SCENE_IS(UmbralThrone) &&
      GameFlag_Get(FLAG_DARK_RIFT_BEATEN) == 0) {
    Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
    Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  }
  Portrait_CloseWindow(ACTOR_PARTY_LEADER);
  Portrait_CloseWindow(ACTOR_GARET);
  Portrait_CloseWindow(ACTOR_IVAN);
  Portrait_CloseWindow(ACTOR_MIA);
}

static void UmbralRift_FountainDialogue(void) {
  UmbralRift_Say(MsgDarkRiftFountain003, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftFountain007, ACTOR_GARET);
}

static void UmbralRift_MazeDialogue(void) {
  UmbralRift_Say(MsgDarkRiftMaze002, ACTOR_GARET);
}

static void UmbralRift_MemoryDialogue(void) {
  UmbralRift_Say(MsgDarkRiftMemory001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftMemory005, ACTOR_GARET);
}

static void UmbralRift_OrbDialogue(void) {
  UmbralRift_Say(MsgDarkRiftOrb003, ACTOR_IVAN);
}

// Called inside the gateway interaction, before changing rooms.
static void UmbralRift_GateEvent(void) {
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
  GameFlag_Set(FLAG_DARK_RIFT_CAUSEWAY_SEEN);
  Event_End();
}

static void UmbralRift_CloseAnchor(void) {
  UmbralRift_Say(MsgDarkRiftSeal003, ACTOR_IVAN);
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
  UmbralRift_Say(MsgDarkRiftSeal011, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftSeal015, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftSeal018, ACTOR_GARET);
  GameFlag_Set(FLAG_DARK_RIFT_ANCHOR_SEALED);
}


/// The Vigil's watch, kept for the frame task.
struct UmbralVigilWatch {
  u8 caught; ///< 1 once a statue has reached the leader
  u8 timer;  ///< frames he has stood as stone since
  u8 moved;  ///< bits: the statues that have moved
  u8 tick;   ///< counts frames; they step on every other one
};
struct UmbralVigilWatch gUmbralRift_VigilWatch;

/// The leader's eight facings as steps along x and z (east first, clockwise).
static const s8 sUmbralVigilFacingX[8] = {2, 1, 0, -1, -2, -1, 0, 1};
static const s8 sUmbralVigilFacingZ[8] = {0, 1, 2, 1, 0, -1, -2, -1};

/// Counts the Vigil's catches, up to three, in two flags.
static s32 UmbralRift_VigilCatches(void) {
  return GameFlag_Get(FLAG_DARK_RIFT_VIGIL_CAUGHT_1) +
         2 * GameFlag_Get(FLAG_DARK_RIFT_VIGIL_CAUGHT_2);
}

/// Runs every frame in the Vigil. A statue anywhere in front of the leader
/// (the half of the plaza he faces) never moves; any other comes a pixel
/// every other frame toward him, half his walking pace, wearing her moved
/// face from then on. One that reaches him
/// unseen turns him to stone, holds the field, and after
/// UMBRAL_VIGIL_STONE_FRAMES sends the party back in at the cave mouth.
static void UmbralRift_WatchVigil(void) {
  struct UmbralVigilWatch *watch = &gUmbralRift_VigilWatch;
  struct Actor *leader;
  s32 i;
  s32 fx;
  s32 fz;
  s32 lx;
  s32 lz;

  if (watch->caught) {
    if (++watch->timer == UMBRAL_VIGIL_STONE_FRAMES)
      Import_EventSetExitRequest(UMBRAL_VIGIL_CAUGHT);
    return;
  }
  leader = Actor_GetById(gSaveBlock.leaderActorId);
  lx = leader->x.fixed >> 16;
  lz = leader->z.fixed >> 16;
  watch->tick++;
  fx = sUmbralVigilFacingX[((leader->facing + 0x1000) >> 13) & 7];
  fz = sUmbralVigilFacingZ[((leader->facing + 0x1000) >> 13) & 7];
  for (i = 0; i < UMBRAL_VIGIL_STATUES; i++) {
    struct Actor *statue = Actor_Get(ACTOR_FIRST_PLACED + i);
    s32 dx;
    s32 dz;
    s32 far;
    s32 toward;

    if (statue == NULL || (statue->x.fixed == 0 && statue->z.fixed == 0))
      continue;
    dx = (statue->x.fixed >> 16) - lx;
    dz = (statue->z.fixed >> 16) - lz;
    far = dx * dx + dz * dz;
    toward = dx * fx + dz * fz;
    // Seen: anywhere in the half he faces.
    if (toward > 0)
      continue;
    if (far < UMBRAL_VIGIL_CATCH_DISTANCE * UMBRAL_VIGIL_CATCH_DISTANCE) {
      watch->caught = 1;
      Event_Start();
      Actor_ConfigureSpriteColor(ACTOR_PARTY_LEADER, SPRITE_COLOR_GREY);
      if (GameFlag_Get(FLAG_DARK_RIFT_VIGIL_CAUGHT_1) == 0)
        GameFlag_Set(FLAG_DARK_RIFT_VIGIL_CAUGHT_1);
      else if (GameFlag_Get(FLAG_DARK_RIFT_VIGIL_CAUGHT_2) == 0) {
        GameFlag_Clear(FLAG_DARK_RIFT_VIGIL_CAUGHT_1);
        GameFlag_Set(FLAG_DARK_RIFT_VIGIL_CAUGHT_2);
      } else
        GameFlag_Set(FLAG_DARK_RIFT_VIGIL_CAUGHT_1);
      return;
    }
    if (watch->tick & 1)
      continue;
    if (!(watch->moved & (1 << i))) {
      watch->moved |= 1 << i;
      Actor_SetAnimation(ACTOR_FIRST_PLACED + i, UMBRAL_VIGIL_STATUE_MOVED);
    }
    if ((dx < 0 ? -dx : dx) > (dz < 0 ? -dz : dz))
      statue->x.fixed += dx > 0 ? -0x10000 : 0x10000;
    else
      statue->z.fixed += dz > 0 ? -0x10000 : 0x10000;
  }
}

/// Sets up the Vigil: hides the statues by the cave beyond the number of
/// catches, clears the watch and starts it.
static void UmbralRift_StartVigil(void) {
  s32 i;

  for (i = UMBRAL_VIGIL_EXTRA_FIRST + UmbralRift_VigilCatches();
       i < UMBRAL_VIGIL_STATUES; i++)
    Import_ActorSetPosition(ACTOR_FIRST_PLACED + i, 0, 0);
  gUmbralRift_VigilWatch.caught = 0;
  gUmbralRift_VigilWatch.timer = 0;
  gUmbralRift_VigilWatch.moved = 0;
  gUmbralRift_VigilWatch.tick = 0;
  Task_AddFrame(UmbralRift_WatchVigil, TASK_PASS_FRAME);
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
  // Karis stands black in the Ritual Room's pentagram until beaten; back from
  // her fight (a win: a loss goes to the restart point), she fades.
  if (UMBRAL_SCENE_IS(UmbralRitual) &&
      GameFlag_Get(FLAG_DARK_RIFT_KARIS_BEATEN) == 0) {
    if (gSaveBlock.entrance == UMBRAL_RITUAL_FROM_KARIS_BATTLE &&
        GameFlag_Get(FLAG_DARK_RIFT_KARIS_FOUGHT) != 0 &&
        gSaveBlock.sequenceResult != -1)
      UmbralRift_KarisAftermath();
    else {
      // The chest at her feet is not there until she fades.
      TreasureSpot_SetPosition(UMBRAL_RITUAL_CHEST, 0, 0);
      UmbralRift_PairShow(ACTOR_RITUAL_KARIS, ACTOR_RITUAL_KARIS);
      // She stands on the pentagram, drawn above the floor's markings.
      Actor_SetSpritePriority(ACTOR_RITUAL_KARIS, 1);
    }
  }
  // Vale and Kolima are silent: no music, only the field's own sounds.
  if (UMBRAL_SCENE_IS(UmbralVigil) || UMBRAL_SCENE_IS(UmbralGrove))
    Sound_PlaySong(MUS_SILENCE);
  // Vale: the statues by the cave stand only for the times the party has been
  // caught; then the watch starts.
  if (UMBRAL_SCENE_IS(UmbralVigil))
    UmbralRift_StartVigil();
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
    UmbralRift_FountainDialogue();
  else if (flag == FLAG_DARK_RIFT_PAIR_MAZE)
    UmbralRift_MazeDialogue();
  else if (flag == FLAG_DARK_RIFT_PAIR_MEMORY)
    UmbralRift_MemoryDialogue();
  UmbralRift_FlickerOut(mystery, heart);
  Actor_ConfigureSpriteColor(mystery, SPRITE_COLOR_HIDDEN);
  Actor_ConfigureSpriteColor(heart, SPRITE_COLOR_HIDDEN);
  Actor_SetPosition(mystery, PIXELS(-9), PIXELS(488));
  Actor_SetPosition(heart, PIXELS(-9), PIXELS(488));
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
  UmbralRift_Say(MsgDarkRiftPost018, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftPost019, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost010, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPost011, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPost020, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPost021, ACTOR_RIFT_MYSTERY);
  Event_WaitFrames(20);
  UmbralRift_FlickerOut(ACTOR_RIFT_MYSTERY, ACTOR_RIFT_HEART);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_HIDDEN);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_HIDDEN);
  Actor_SetPosition(ACTOR_RIFT_MYSTERY, PIXELS(-9), PIXELS(488));
  Actor_SetPosition(ACTOR_RIFT_HEART, PIXELS(-9), PIXELS(488));
  GameFlag_Set(FLAG_DARK_RIFT_BEATEN);
  UmbralRift_Say(MsgDarkRiftPost025, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftPost026, ACTOR_PARTY_LEADER);
  Event_End();
}

/// ??? remains a silhouette, and Heart never reveals her scarred face.
static void UmbralRift_TalkToMystery(void) {
  Event_Start();
  Actor_ConfigureSpriteColor(ACTOR_RIFT_MYSTERY, SPRITE_COLOR_BLACK);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  UmbralRift_Say(MsgDarkRiftPre001, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre002, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre007, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftPre008, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre005, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftPre006, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre009, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre010, ACTOR_RIFT_MYSTERY);
  if (GameFlag_Get(FLAG_DARK_RIFT_PAIR_FOUNTAIN) != 0 ||
      GameFlag_Get(FLAG_DARK_RIFT_PAIR_MAZE) != 0 ||
      GameFlag_Get(FLAG_DARK_RIFT_PAIR_MEMORY) != 0) {
    UmbralRift_Say(MsgDarkRiftPre021, ACTOR_IVAN);
    UmbralRift_Say(MsgDarkRiftPre022, ACTOR_RIFT_MYSTERY);
  }
  UmbralRift_Say(MsgDarkRiftPre023, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre024, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre025, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre028, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre029, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre030, ACTOR_RIFT_MYSTERY);

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
  UmbralRift_Say(MsgDarkRiftPre039, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre040, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre051, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre042, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre047, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre048, ACTOR_RIFT_MYSTERY);
  Event_WaitFrames(20);
  UmbralRift_Say(MsgDarkRiftPre067, ACTOR_RIFT_MYSTERY);
  Actor_ConfigureSpriteColor(ACTOR_RIFT_HEART, SPRITE_COLOR_BLACK);
  Actor_FaceDirection(ACTOR_RIFT_HEART, FACING_NORTH, 12);
  UmbralRift_Say(MsgDarkRiftPre070, ACTOR_RIFT_HEART);
  UmbralRift_Say(MsgDarkRiftPre080, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftPre081, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre011, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftPre012, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre013, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftPre014, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre015, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre016, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre090, ACTOR_PARTY_LEADER);
  UmbralRift_Say(MsgDarkRiftPre093, ACTOR_RIFT_MYSTERY);
  UmbralRift_Say(MsgDarkRiftPre094, ACTOR_RIFT_HEART);
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
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_LEFT_ARCH, UmbralCrossbone, ENTRANCE_DEFAULT),
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_RIGHT_ARCH, UmbralMemory, UMBRAL_MEMORY_FROM_STAIR),
    SCENE_EXIT(UMBRAL_FOUNTAIN_TO_CAUSEWAY, UmbralCauseway, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralMaze),
    SCENE_EXIT(UMBRAL_MAZE_TO_FOUNTAIN, UmbralCrossbone, UMBRAL_CROSSBONE_FROM_MAZE),
    SCENE_EXIT(UMBRAL_MAZE_TO_TOP_DOOR, UmbralPalace, ENTRANCE_DEFAULT),
    SCENE_EXIT(UMBRAL_MAZE_TO_RITUAL, UmbralRitual, ENTRANCE_DEFAULT),
    SCENE_EXIT(UMBRAL_MAZE_TO_VIGIL, UmbralVigil, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralMemory),
    SCENE_EXIT(UMBRAL_MEMORY_TO_MAZE, UmbralPalace, UMBRAL_PALACE_FROM_MEMORY),
    SCENE_EXIT(UMBRAL_MEMORY_TO_STAIR, UmbralFountain, UMBRAL_FOUNTAIN_FROM_RIGHT_ARCH),
    SCENE_EXITS(UmbralCauseway),
    SCENE_EXIT(UMBRAL_CAUSEWAY_TO_FOUNTAIN, UmbralFountain, UMBRAL_FOUNTAIN_FROM_CAUSEWAY),
    SCENE_EXIT(UMBRAL_CAUSEWAY_TO_THRONE, UmbralBeacon, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralRitual),
    SCENE_EXIT(UMBRAL_RITUAL_TO_MAZE, UmbralMaze, UMBRAL_MAZE_FROM_RITUAL),
    SCENE_EXITS(UmbralCrossbone),
    SCENE_EXIT(UMBRAL_CROSSBONE_TO_FOUNTAIN, UmbralFountain, UMBRAL_FOUNTAIN_FROM_LEFT_ARCH),
    SCENE_EXIT(UMBRAL_CROSSBONE_TO_MAZE, UmbralMaze, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralBeacon),
    SCENE_EXIT(UMBRAL_BEACON_TO_CAUSEWAY, UmbralCauseway, UMBRAL_CAUSEWAY_FROM_THRONE),
    SCENE_EXIT(UMBRAL_BEACON_TO_THRONE, UmbralThrone, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralPalace),
    SCENE_EXIT(UMBRAL_PALACE_TO_MAZE, UmbralMaze, UMBRAL_MAZE_FROM_TOP_DOOR),
    SCENE_EXIT(UMBRAL_PALACE_TO_MEMORY, UmbralMemory, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralVigil),
    SCENE_EXIT(UMBRAL_VIGIL_TO_MAZE, UmbralMaze, UMBRAL_MAZE_FROM_VIGIL),
    SCENE_EXIT(UMBRAL_VIGIL_TO_GROVE, UmbralGrove, ENTRANCE_DEFAULT),
    SCENE_EXIT(UMBRAL_VIGIL_CAUGHT, UmbralVigil, ENTRANCE_DEFAULT),
    SCENE_EXITS(UmbralGrove),
    SCENE_EXIT(UMBRAL_GROVE_TO_VIGIL, UmbralVigil, UMBRAL_VIGIL_FROM_GROVE),
    SCENE_EXIT(UMBRAL_GROVE_TO_MAZE, UmbralMaze, UMBRAL_MAZE_FROM_VIGIL),
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
    // A weeping statue at the end of the spur, where the way into Vale goes
    // through the wall.
    {SPRITE_UMBRAL_VIGIL_STATUE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
     PIXELS(296), 0, PIXELS(168), FACING_EAST, TALK_FACING_KEEP, 0},
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
    // Back out of the Ritual Room, below the east door.
    {UMBRAL_MAZE_FROM_RITUAL, CONDITION_ALWAYS, 424, 0, 280, FACING_SOUTH, 0,
     -1, -1, -1, -1, 0},
    // In the spur, beside the mother, walking away from her.
    {UMBRAL_MAZE_FROM_VIGIL, CONDITION_ALWAYS, 264, 0, 184, FACING_WEST, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralMazeTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_MAZE_TO_FOUNTAIN, CONDITION_ALWAYS,
     UMBRAL_MAZE_TO_FOUNTAIN},
    {TRIGGER_EXIT, UMBRAL_MAZE_TO_TOP_DOOR, CONDITION_ALWAYS,
     UMBRAL_MAZE_TO_TOP_DOOR},
    {TRIGGER_EXIT, UMBRAL_MAZE_TO_RITUAL, CONDITION_ALWAYS,
     UMBRAL_MAZE_TO_RITUAL},
    {TRIGGER_EXIT, UMBRAL_MAZE_TO_VIGIL, CONDITION_ALWAYS,
     UMBRAL_MAZE_TO_VIGIL},
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

/// Karis speaks, kept black (a message window would redraw her in colour).
static void UmbralRift_KarisSay(s32 message, s32 actor) {
  Actor_ConfigureSpriteColor(ACTOR_RITUAL_KARIS, SPRITE_COLOR_BLACK);
  // Her own lines show her mugshot; the party's keep theirs.
  if (actor == ACTOR_RITUAL_KARIS)
    GameFlag_Set(FLAG_DARK_WRAITH_SPEAKING);
  UmbralRift_Say(message, actor);
  GameFlag_Clear(FLAG_DARK_WRAITH_SPEAKING);
  Actor_ConfigureSpriteColor(ACTOR_RITUAL_KARIS, SPRITE_COLOR_BLACK);
}

/// The Wraith recognizes Ivan, despises his companions, and attacks.
static void UmbralRift_SeeRitual(void) {
  Event_Start();
  UmbralRift_KarisSay(MsgDarkRiftKaris001, ACTOR_RITUAL_KARIS);
  UmbralRift_KarisSay(MsgDarkRiftKaris002, ACTOR_IVAN);
  UmbralRift_KarisSay(MsgDarkRiftKaris003, ACTOR_RITUAL_KARIS);
  UmbralRift_KarisSay(MsgDarkRiftKaris010, ACTOR_GARET);
  UmbralRift_KarisSay(MsgDarkRiftKaris011, ACTOR_RITUAL_KARIS);
  UmbralRift_KarisSay(MsgDarkRiftKaris012, ACTOR_MIA);
  UmbralRift_KarisSay(MsgDarkRiftKaris013, ACTOR_RITUAL_KARIS);
  UmbralRift_KarisSay(MsgDarkRiftKaris014, ACTOR_PARTY_LEADER);
  UmbralRift_KarisSay(MsgDarkRiftKaris006, ACTOR_RITUAL_KARIS);
  GameFlag_Set(FLAG_DARK_RIFT_KARIS_FOUGHT);
  Event_SetAfterBattleDestination((s32)&SceneId_UmbralRitual,
                                  UMBRAL_RITUAL_FROM_KARIS_BATTLE);
  Event_SetDefeatDestination(-1, -1);
  Battle_SetType(BATTLE_TYPE_SCRIPTED);
  Field_RequestBattleFromEncounterTable(ENCOUNTER_ZONE_UMBRAL_KARIS, 0);
  Event_End();
}

/// After the fight the Wraith reveals her relationship to Ivan, then fades.
static void UmbralRift_KarisAftermath(void) {
  Event_Start();
  // The scene is still dark here: bring it in first, as the dais does.
  MapGrid_CenterOnFollowedPoint();
  WaitFrames(1);
  Event_StartScreenTransition();
  Event_WaitTransitionFrames();
  UmbralRift_KarisSay(MsgDarkRiftKaris004, ACTOR_RITUAL_KARIS);
  Event_WaitFrames(40);
  UmbralRift_KarisSay(MsgDarkRiftKaris015, ACTOR_RITUAL_KARIS);
  UmbralRift_KarisSay(MsgDarkRiftKaris016, ACTOR_RITUAL_KARIS);
  Event_WaitFrames(30);
  UmbralRift_FlickerOut(ACTOR_RITUAL_KARIS, ACTOR_RITUAL_KARIS);
  Actor_ConfigureSpriteColor(ACTOR_RITUAL_KARIS, SPRITE_COLOR_HIDDEN);
  Actor_SetPosition(ACTOR_RITUAL_KARIS, PIXELS(-9), PIXELS(488));
  // Where she stood, the chest she leaves behind.
  TreasureSpot_SetPosition(UMBRAL_RITUAL_CHEST, -1, -1);
  GameFlag_Set(FLAG_DARK_RIFT_KARIS_BEATEN);
  UmbralRift_Say(MsgDarkRiftKaris005, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftKaris017, ACTOR_GARET);
  UmbralRift_Say(MsgDarkRiftKaris018, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftKaris019, ACTOR_MIA);
  UmbralRift_Say(MsgDarkRiftKaris020, ACTOR_IVAN);
  UmbralRift_Say(MsgDarkRiftKaris021, ACTOR_PARTY_LEADER);
  GameFlag_Set(FLAG_DARK_RIFT_RITUAL_SEEN);
  Event_End();
}

static struct SceneEntrance sUmbralRitualEntrances[] = {
    // Through the maze's east door, under the arch.
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 136, 0, 72, FACING_SOUTH, 0, -1, -1,
     -1, -1, 0},
    {UMBRAL_RITUAL_FROM_KARIS_BATTLE, CONDITION_ALWAYS, 136, 0, 72,
     FACING_SOUTH, 0, -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralRitualActorTemplates[] = {
    // Karis at the pentagram's heart, drawn black, facing the arch: a young
    // woman's sprite with no portrait of its own (her lines show her mugshot,
    // FLAG_DARK_WRAITH_SPEAKING), and Mia's young woman's voice.
    {SPRITE_YOUNG_WOMAN_IN_GREEN, FLAG_DARK_RIFT_KARIS_BEATEN,
     MOVEMENT_TYPE_STAND, PIXELS(136), 0, PIXELS(120), FACING_NORTH,
     TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralRitualTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_RITUAL_TO_MAZE, CONDITION_ALWAYS,
     UMBRAL_RITUAL_TO_MAZE},
    {TRIGGER_STEP, UMBRAL_RITUAL_STEP, FLAG_DARK_RIFT_RITUAL_SEEN,
     EVENT(UmbralRift_SeeRitual)},
    {TRIGGER_TALK, ACTOR_RITUAL_KARIS, FLAG_DARK_RIFT_KARIS_BEATEN,
     EVENT(UmbralRift_SeeRitual)},
    // The chest in the left alcove (the map's treasure spot, subject 100).
    {EXAMINE_TRIGGER(EXAMINE_CHEST), 100, FLAG_CHEST_UMBRAL_RITUAL,
     FIND_ITEM(ITEM_MYSTERY_BLADE)},
    {TRIGGERS_END},
};

#define UMBRAL_IN_RITUAL() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralRitual)

/// The first steps into the Crossbone room.
static void UmbralRift_SeeCrossbone(void) {
  Event_Start();
  GameFlag_Set(FLAG_DARK_RIFT_CROSSBONE_SEEN);
  Event_End();
}

static struct SceneEntrance sUmbralCrossboneEntrances[] = {
    // Through the Fountain Hall's left arch, at the left door.
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 72, 0, 344, FACING_NORTH, 0, -1, -1,
     -1, -1, 0},
    // Back from the maze, at the right door.
    {UMBRAL_CROSSBONE_FROM_MAZE, CONDITION_ALWAYS, 184, 0, 344, FACING_NORTH, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralCrossboneActorTemplates[] = {
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralCrossboneTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_CROSSBONE_TO_FOUNTAIN, CONDITION_ALWAYS,
     UMBRAL_CROSSBONE_TO_FOUNTAIN},
    {TRIGGER_EXIT, UMBRAL_CROSSBONE_TO_MAZE, CONDITION_ALWAYS,
     UMBRAL_CROSSBONE_TO_MAZE},
    {TRIGGER_STEP, UMBRAL_CROSSBONE_STEP, FLAG_DARK_RIFT_CROSSBONE_SEEN,
     EVENT(UmbralRift_SeeCrossbone)},
    {TRIGGERS_END},
};

#define UMBRAL_IN_CROSSBONE() \
  ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralCrossbone)

/// The first look at the beacon, halfway up the chamber.
static void UmbralRift_SeeBeacon(void) {
  Event_Start();
  Sound_PlaySong(SE_WARP);
  Event_WaitFrames(20);
  UmbralRift_Say(MsgDarkRiftBeacon003, ACTOR_PARTY_LEADER);
  GameFlag_Set(FLAG_DARK_RIFT_BEACON_SEEN);
  Event_End();
}

/// Through the beacon and out in the Throne Hall; the party talks it over the
/// first time.
static void UmbralRift_EnterBeacon(void) {
  Event_Start();
  if (GameFlag_Get(FLAG_DARK_RIFT_BEACON_CROSSED) == 0) {
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

static struct SceneEntrance sUmbralVigilEntrances[] = {
    // Out of the cave mouth under the cliff, from the maze.
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 184, 0, 120, FACING_SOUTH, 0, -1, -1,
     -1, -1, 0},
    // Back through the arch from Kolima.
    {UMBRAL_VIGIL_FROM_GROVE, CONDITION_ALWAYS, 216, 0, 488, FACING_NORTH, 0,
     -1, -1, -1, -1, 0},
    {SCENE_TABLE_END},
};

#define VIGIL_STATUE(x, z)                                                     \
  {SPRITE_UMBRAL_VIGIL_STATUE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,          \
   PIXELS(x), 0, PIXELS(z), FACING_SOUTH, TALK_FACING_KEEP, 0}
static struct ActorTemplate sUmbralVigilActorTemplates[] = {
    // Round where the pond was: one above, two each side.
    VIGIL_STATUE(216, 248),
    VIGIL_STATUE(136, 304),
    VIGIL_STATUE(136, 360),
    VIGIL_STATUE(296, 304),
    VIGIL_STATUE(296, 360),
    // By the cave mouth, one for each time the party has been caught
    // (hidden at start-up until then).
    VIGIL_STATUE(136, 136),
    VIGIL_STATUE(248, 120),
    VIGIL_STATUE(104, 200),
    {SCENE_TABLE_END},
};
#undef VIGIL_STATUE

static struct Trigger sUmbralVigilTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_VIGIL_TO_MAZE, CONDITION_ALWAYS, UMBRAL_VIGIL_TO_MAZE},
    {TRIGGER_EXIT, UMBRAL_VIGIL_TO_GROVE, CONDITION_ALWAYS,
     UMBRAL_VIGIL_TO_GROVE},
    {TRIGGERS_END},
};

static struct SceneEntrance sUmbralGroveEntrances[] = {
    // In at Kolima's west edge, from Vale.
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 44, 0, 267, FACING_EAST, 0, -1, -1,
     -1, -1, 0},
    {SCENE_TABLE_END},
};

#define GROVE_FIGURE(x, z, facing)                                             \
  {SPRITE_UMBRAL_GROVE_FIGURE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,          \
   PIXELS(x), 0, PIXELS(z), facing, TALK_FACING_KEEP, 0}
// Each figure's facing picks which of Kolima's people it is (spr_508): south
// the woman in the apron, east the young man, north the man in orange.
#define WOMAN FACING_SOUTH
#define YOUNG_MAN FACING_EAST
#define MAN FACING_NORTH
static struct ActorTemplate sUmbralGroveActorTemplates[] = {
    // Two grown out of the roots of each stump, either side of its door.
    GROVE_FIGURE(88, 184, WOMAN),
    GROVE_FIGURE(168, 184, MAN),
    GROVE_FIGURE(280, 232, YOUNG_MAN),
    GROVE_FIGURE(376, 232, WOMAN),
    GROVE_FIGURE(120, 312, MAN),
    GROVE_FIGURE(200, 312, YOUNG_MAN),
    GROVE_FIGURE(232, 376, WOMAN),
    GROVE_FIGURE(312, 376, MAN),
    // Three in the clearing, where the villagers would stand to talk, clear
    // of the one way between the roots (row 16).
    GROVE_FIGURE(184, 200, YOUNG_MAN),
    GROVE_FIGURE(232, 192, WOMAN),
    GROVE_FIGURE(264, 216, MAN),
    // Two penned in the fold like livestock.
    GROVE_FIGURE(344, 328, WOMAN),
    GROVE_FIGURE(360, 344, YOUNG_MAN),
    {SCENE_TABLE_END},
};
#undef WOMAN
#undef YOUNG_MAN
#undef MAN
#undef GROVE_FIGURE

static struct Trigger sUmbralGroveTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_GROVE_TO_VIGIL, CONDITION_ALWAYS,
     UMBRAL_GROVE_TO_VIGIL},
    {TRIGGER_EXIT, UMBRAL_GROVE_TO_MAZE, CONDITION_ALWAYS, UMBRAL_GROVE_TO_MAZE},
    {TRIGGERS_END},
};

// Original Babi Palace camera bounds and door coordinates; no palace events.
static struct SceneEntrance sUmbralPalaceEntrances[] = {
    {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 768, 0, 200, FACING_NORTH, 0,
     512, 0, 1024, 224, 0},
    {UMBRAL_PALACE_FROM_MEMORY, CONDITION_ALWAYS, 584, 0, 72, FACING_SOUTH, 0,
     512, 0, 1024, 224, 0},
    {SCENE_TABLE_END},
};

static struct ActorTemplate sUmbralPalaceActorTemplates[] = {
    {SPRITE_UMBRAL_STATUE_ELONGATED, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
     PIXELS(680), 0, PIXELS(136), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SPRITE_UMBRAL_STATUE_TWO_FACE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
     PIXELS(768), 0, PIXELS(120), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SPRITE_UMBRAL_STATUE_ELONGATED, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
     PIXELS(856), 0, PIXELS(136), FACING_SOUTH, TALK_FACING_KEEP, 0},
    {SCENE_TABLE_END},
};

static struct Trigger sUmbralPalaceTriggers[] = {
    {TRIGGER_EXIT, UMBRAL_PALACE_TO_MAZE, CONDITION_ALWAYS,
     UMBRAL_PALACE_TO_MAZE},
    {TRIGGER_EXIT, UMBRAL_PALACE_TO_MEMORY, CONDITION_ALWAYS,
     UMBRAL_PALACE_TO_MEMORY},
    {TRIGGERS_END},
};

#define UMBRAL_IN_PALACE() ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralPalace)
#define UMBRAL_IN_VIGIL() ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralVigil)
#define UMBRAL_IN_GROVE() ((s16)gSaveBlock.sceneId == (s32)&SceneId_UmbralGrove)

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
  return UMBRAL_IN_VIGIL()       ? sUmbralVigilEntrances
         : UMBRAL_IN_GROVE()       ? sUmbralGroveEntrances
         : UMBRAL_IN_PALACE()      ? sUmbralPalaceEntrances
         : UMBRAL_IN_RITUAL()    ? sUmbralRitualEntrances
         : UMBRAL_IN_CROSSBONE() ? sUmbralCrossboneEntrances
         : UMBRAL_IN_BEACON()   ? sUmbralBeaconEntrances
         : UMBRAL_IN_CAUSEWAY() ? sUmbralCausewayEntrances
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryEntrances
         : UMBRAL_IN_MAZE()     ? sUmbralMazeEntrances
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainEntrances
                                : sUmbralThroneEntrances;
}
const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }
const u32 *Scene_GetExits(void) { return sUmbralThroneExits; }
const struct ActorTemplate *Scene_GetActorTemplates(void) {
  return UMBRAL_IN_VIGIL()       ? sUmbralVigilActorTemplates
         : UMBRAL_IN_GROVE()       ? sUmbralGroveActorTemplates
         : UMBRAL_IN_PALACE()      ? sUmbralPalaceActorTemplates
         : UMBRAL_IN_RITUAL()    ? sUmbralRitualActorTemplates
         : UMBRAL_IN_CROSSBONE() ? sUmbralCrossboneActorTemplates
         : UMBRAL_IN_BEACON()   ? sUmbralBeaconActorTemplates
         : UMBRAL_IN_CAUSEWAY() ? sUmbralCausewayActorTemplates
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryActorTemplates
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainActorTemplates
         : UMBRAL_IN_MAZE()     ? sUmbralMazeActorTemplates
                                : sUmbralThroneActorTemplates;
}
const struct Trigger *Scene_GetTriggers(void) {
  return UMBRAL_IN_VIGIL()       ? sUmbralVigilTriggers
         : UMBRAL_IN_GROVE()       ? sUmbralGroveTriggers
         : UMBRAL_IN_PALACE()      ? sUmbralPalaceTriggers
         : UMBRAL_IN_RITUAL()    ? sUmbralRitualTriggers
         : UMBRAL_IN_CROSSBONE() ? sUmbralCrossboneTriggers
         : UMBRAL_IN_BEACON()   ? sUmbralBeaconTriggers
         : UMBRAL_IN_CAUSEWAY() ? sUmbralCausewayTriggers
         : UMBRAL_IN_MEMORY()   ? sUmbralMemoryTriggers
         : UMBRAL_IN_MAZE()     ? sUmbralMazeTriggers
         : UMBRAL_IN_FOUNTAIN() ? sUmbralFountainTriggers
                                : sUmbralThroneTriggers;
}
