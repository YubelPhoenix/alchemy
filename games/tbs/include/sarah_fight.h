#ifndef ALCHEMY_SARAH_FIGHT_H
#define ALCHEMY_SARAH_FIGHT_H

/// @file
/// Sarah's field side, shared by the scenes she waits in (Vault, Tolbi and
/// Lalivero; Kalay has its own copy). Include after the scene's other headers.
/// Her strength per fight is in sarah_stage.h.

#include "flags.h"
#include "ash_warp.h"

/// Her next message, shown with her own mugshot.
#define SARAH_SAYS(actorId, message)                                           \
  do {                                                                         \
    Event_SetMessageId(message);                                               \
    GameFlag_Set(FLAG_DARK_SARAH_SPEAKING);                                    \
    Event_ShowMessageThenWait((actorId), 0, 20);                               \
    GameFlag_Clear(FLAG_DARK_SARAH_SPEAKING);                                  \
  } while (0)

/// Her next message, spoken by the party's leader (no mugshot of hers).
#define SARAH_ISAAC_SAYS(message)                                              \
  do {                                                                         \
    Event_SetMessageId(message);                                               \
    Event_ShowMessageThenWait(ACTOR_PARTY_LEADER, 0, 2);                       \
  } while (0)

/// Her battle at `stage` has been started here and not yet settled; a battle
/// begun in another town (and lost) does not answer in this one.
#define SARAH_PENDING_AT(stage)                                                \
  (GameFlag_Get(FLAG_DARK_SARAH_PENDING) != 0 &&                               \
   (((GameFlag_Get(FLAG_DARK_SARAH_STAGE_BIT0) != 0) |                         \
     ((GameFlag_Get(FLAG_DARK_SARAH_STAGE_BIT1) != 0) << 1)) == (stage)))

/// Starts her battle at `stage` (0 to 3); the party returns to `sceneId`.
#define SARAH_START_BATTLE(stage, sceneId)                                     \
  do {                                                                         \
    GameFlag_Set(FLAG_DARK_SARAH_PENDING);                                     \
    if ((stage) & 1)                                                           \
      GameFlag_Set(FLAG_DARK_SARAH_STAGE_BIT0);                                \
    else                                                                       \
      GameFlag_Clear(FLAG_DARK_SARAH_STAGE_BIT0);                              \
    if ((stage) & 2)                                                           \
      GameFlag_Set(FLAG_DARK_SARAH_STAGE_BIT1);                                \
    else                                                                       \
      GameFlag_Clear(FLAG_DARK_SARAH_STAGE_BIT1);                              \
    gFieldWork->transition =                                                   \
        SCENE_TRANSITION(TRANSITION_WINDOW, WINDOW_TRANSITION_BARS);           \
    Event_SetAfterBattleDestination((s32)&(sceneId), 0);                       \
    Event_SetDefeatDestination(-1, -1);                                        \
    Battle_SetType(BATTLE_TYPE_SCRIPTED);                                      \
    Field_RequestBattleFromEncounterTable(                                     \
        ENCOUNTER_ZONE_SCRIPTED_MIA_MENARDI, 1);                               \
  } while (0)

/// She turns and walks `dx` pixels east, then is gone (her place is parked
/// off the map); no warp flicker, she is a human.
#define SARAH_WALK_EAST(actorId, dx)                                           \
  do {                                                                         \
    Actor_FaceDirection((actorId), FACING_EAST, 10);                           \
    Actor_WalkByAndWait((actorId), (dx), 0);                                   \
    Actor_ConfigureSpriteColor((actorId), SPRITE_COLOR_HIDDEN);                \
  } while (0)

/// Kalay's road east, far enough to leave the screen.
#define SARAH_WALK_AWAY(actorId) SARAH_WALK_EAST((actorId), 112)

/// She steps `sideX` pixels east, clear of Isaac standing south of her, then
/// walks `dz` pixels south and is gone.
#define SARAH_WALK_SOUTH(actorId, sideX, dz)                                   \
  do {                                                                         \
    Actor_FaceDirection((actorId), FACING_EAST, 10);                           \
    Actor_WalkByAndWait((actorId), (sideX), 0);                                \
    Actor_FaceDirection((actorId), FACING_SOUTH, 6);                           \
    Actor_WalkByAndWait((actorId), 0, (dz));                                   \
    Actor_ConfigureSpriteColor((actorId), SPRITE_COLOR_HIDDEN);                \
  } while (0)

/// Back from her battle, in the scene she was fought in: the party stands
/// where it faced her; a defeat leaves her waiting, a win has her say her
/// last words, leave by `leave` (one of the walks above) and set
/// `foughtFlag`.
#define SARAH_AFTERMATH_BY(actorId, leaderX, leaderY, beatenMessage,           \
                           foughtFlag, leave)                                  \
  do {                                                                         \
    GameFlag_Clear(FLAG_DARK_SARAH_PENDING);                                   \
    Event_Start();                                                             \
    Actor_SetPosition(ACTOR_PARTY_LEADER, PIXELS(leaderX), PIXELS(leaderY));   \
    Actor_FaceDirection(ACTOR_PARTY_LEADER, FACING_NORTH, 0);                  \
    MapGrid_CenterOnFollowedPoint();                                           \
    WaitFrames(1);                                                             \
    Event_StartScreenTransition();                                             \
    Event_WaitTransitionFrames();                                              \
    if (gSaveBlock.sequenceResult == -1) {                                     \
      FieldCamera_MoveTo(-1, -1, -1, 0);                                       \
      Event_End();                                                             \
    } else {                                                                   \
      SARAH_SAYS((actorId), (beatenMessage));                                  \
      leave;                                                                   \
      Actor_SetPosition((actorId), PIXELS(0), PIXELS(0));                      \
      GameFlag_Set(foughtFlag);                                                \
      FieldCamera_MoveTo(-1, -1, -1, 0);                                       \
      Event_End();                                                             \
    }                                                                          \
  } while (0)

#endif
