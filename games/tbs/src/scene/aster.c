/// @file
/// Aster, an experimental town caught between two incompatible histories.
/// Experimental two-way overworld test only; no permanent flags or rewards.
#include "types.h"
#include "field.h"
#include "scene_tables.h"
#include "actor.h"
#include "graphics.h"
#include "ability_ids.h"
#include "flags.h"
#include "unit/overworld/event_commands.h"
#include "text/msg_ids.h"

enum { ASTER_TO_WORLD_MAP = 1, ASTER_MB_WELL = 0xe1,
       ASTER_MB_MEMORIAL = 0xe2, ASTER_MB_SEALED_DOOR = 0xe3,
       ASTER_MB_INN = 0xe4, ASTER_MB_WEST_HOME = 0xe5,
       ASTER_MB_EAST_HOME = 0xe6, ASTER_MB_SHOP = 0xe7,
       ASTER_MB_DUPLICATE_HOME = 0xe8 };
#define ASTER_SEEN_WELL FLAG_SCENE_TEMP_00
#define ASTER_SEEN_MEMORIAL FLAG_SCENE_TEMP_01
#define ASTER_HEARD_GREETER FLAG_SCENE_TEMP_02
#define ASTER_FRACTURED FLAG_SCENE_TEMP_03
#define ASTER_REVEALED FLAG_SCENE_TEMP_04
#define ASTER_REVISITED_WELL FLAG_SCENE_TEMP_05
#define ASTER_REVISITED_MEMORIAL FLAG_SCENE_TEMP_06
#define ASTER_SEEN_DOOR FLAG_SCENE_TEMP_07
#define ASTER_REVISITED_DOOR FLAG_SCENE_TEMP_08
#define ASTER_REVEALED_MEMORIAL FLAG_SCENE_TEMP_09
#define ASTER_GREETER_DUPLICATE_SEEN FLAG_SCENE_TEMP_0A
#define ASTER_ELDER_TALKED FLAG_SCENE_TEMP_0B
#define ASTER_ELDER_SECOND FLAG_SCENE_TEMP_0C
#define ASTER_INNKEEPER_TALKED FLAG_SCENE_TEMP_0D

/* Exterior thresholds are STEP triggers, so each line should play only once
 * per stage in a town visit. A changed history may still be heard after the
 * fracture; the duplicate house gets a third response after the revelation.
 * Scene_Arrive clears these flags on re-entry (no permanent save changes). */
#define ASTER_INN_THRESHOLD_ARRIVAL FLAG_SCENE_TEMP_0E
#define ASTER_INN_THRESHOLD_FRACTURE FLAG_SCENE_TEMP_0F
#define ASTER_WEST_HOME_THRESHOLD_ARRIVAL FLAG_SCENE_TEMP_10
#define ASTER_WEST_HOME_THRESHOLD_FRACTURE FLAG_SCENE_TEMP_11
#define ASTER_EAST_HOME_THRESHOLD_ARRIVAL FLAG_SCENE_TEMP_12
#define ASTER_EAST_HOME_THRESHOLD_FRACTURE FLAG_SCENE_TEMP_13
#define ASTER_SHOP_THRESHOLD_ARRIVAL FLAG_SCENE_TEMP_14
#define ASTER_SHOP_THRESHOLD_FRACTURE FLAG_SCENE_TEMP_15
#define ASTER_DUPLICATE_HOME_THRESHOLD_ARRIVAL FLAG_SCENE_TEMP_16
#define ASTER_DUPLICATE_HOME_THRESHOLD_FRACTURE FLAG_SCENE_TEMP_17
#define ASTER_DUPLICATE_HOME_THRESHOLD_REVELATION FLAG_SCENE_TEMP_18

enum AsterActorId {
  ACTOR_ASTER_ELDER = ACTOR_FIRST_PLACED,
  ACTOR_ASTER_INNKEEPER, ACTOR_ASTER_GREETER, ACTOR_ASTER_BOY,
  ACTOR_ASTER_RESIDENT, ACTOR_ASTER_OTHER, ACTOR_ASTER_MIRROR,
  // Four existing scenery actors follow the seven NPCs. Keep the sign last
  // so none of their established actor IDs changes.
  ACTOR_ASTER_GATE_SIGN = ACTOR_ASTER_MIRROR + 5
};

static void Aster_Speak(s32 actor, s32 message) {
  Event_SetMessageId(message);
  Event_ShowMessageAndWait(actor, 0);
}
// Optional sign beside the south entrance, not on the exit marker.
// Re-read its text as Aster's story changes; no temporary sign flag needed.
static void Aster_ReadGateSign(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_REVEALED)) {
    FieldMessage_Show(MsgAsterRevelationGate, 1);
  } else if (GameFlag_Get(ASTER_FRACTURED)) {
    FieldMessage_Show(MsgAsterFractureGate, 1);
  } else {
    FieldMessage_Show(MsgAsterArrivalGate, 1);
  }
  Event_End();
}
static void Aster_CheckFracture(void) {
  if (GameFlag_Get(ASTER_FRACTURED) == 0 &&
      GameFlag_Get(ASTER_SEEN_WELL) != 0 &&
      GameFlag_Get(ASTER_SEEN_MEMORIAL) != 0 &&
      GameFlag_Get(ASTER_HEARD_GREETER) != 0) {
    GameFlag_Set(ASTER_FRACTURED);
    FieldMessage_Show(MsgAsterFractureBegin, 1);
  }
}
static void Aster_TalkElder(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_REVEALED)) {
    Aster_Speak(ACTOR_ASTER_ELDER, MsgAsterRevelationElder);
  } else if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_Speak(ACTOR_ASTER_ELDER, MsgAsterFractureElder);
  } else if (!GameFlag_Get(ASTER_ELDER_TALKED)) {
    Aster_Speak(ACTOR_ASTER_ELDER, MsgAsterElderWelcome);
    GameFlag_Set(ASTER_ELDER_TALKED);
  } else if (!GameFlag_Get(ASTER_ELDER_SECOND)) {
    Aster_Speak(ACTOR_ASTER_ELDER, MsgAsterArrivalElder);
    GameFlag_Set(ASTER_ELDER_SECOND);
  } else {
    Aster_Speak(ACTOR_ASTER_ELDER, MsgAsterArrivalElderSecond);
  }
  Event_End();
}
static void Aster_TalkInnkeeper(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_Speak(ACTOR_ASTER_INNKEEPER, MsgAsterFractureInn);
  } else if (!GameFlag_Get(ASTER_INNKEEPER_TALKED)) {
    Aster_Speak(ACTOR_ASTER_INNKEEPER, MsgAsterInnkeeperWelcome);
    GameFlag_Set(ASTER_INNKEEPER_TALKED);
  } else {
    Aster_Speak(ACTOR_ASTER_INNKEEPER, MsgAsterArrivalInn);
  }
  Event_End();
}
static void Aster_TalkGreeter(void) {
  Event_Start();
  // After the revelation, Isaac may return to the woman who welcomed him.
  // The farewell is optional TALK dialogue, never part of exit handling.
  if (GameFlag_Get(ASTER_REVEALED)) {
    Aster_Speak(ACTOR_ASTER_GREETER, MsgAsterRevelationExit);
  } else if (GameFlag_Get(ASTER_FRACTURED)) {
    if (!GameFlag_Get(ASTER_GREETER_DUPLICATE_SEEN)) {
      Aster_Speak(ACTOR_ASTER_GREETER, MsgAsterFractureGreeter);
      GameFlag_Set(ASTER_GREETER_DUPLICATE_SEEN);
    } else {
      Aster_Speak(ACTOR_ASTER_GREETER, MsgAsterFractureDuplicateA);
    }
  } else {
    Aster_Speak(ACTOR_ASTER_GREETER, MsgAsterArrivalGreeter);
    GameFlag_Set(ASTER_HEARD_GREETER);
    Aster_CheckFracture();
  }
  Event_End();
}
static void Aster_TalkBoy(void) {
  Event_Start();
  Aster_Speak(ACTOR_ASTER_BOY, GameFlag_Get(ASTER_FRACTURED)
      ? MsgAsterFractureWell : MsgAsterArrivalWell);
  Event_End();
}
static void Aster_TalkResident(void) {
  Event_Start();
  Aster_Speak(ACTOR_ASTER_RESIDENT, GameFlag_Get(ASTER_FRACTURED)
      ? MsgAsterFractureHome : MsgAsterArrivalHome);
  Event_End();
}
static void Aster_TalkMirror(void) {
  Event_Start();
  Aster_Speak(ACTOR_ASTER_MIRROR, GameFlag_Get(ASTER_FRACTURED)
      ? MsgAsterFractureDuplicateB : MsgAsterArrivalGreeterRepeat);
  Event_End();
}
static void Aster_TalkOther(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_FRACTURED) == 0) {
    Aster_Speak(ACTOR_ASTER_OTHER, MsgAsterOtherIsaacEarly);
  } else if (GameFlag_Get(ASTER_REVEALED) == 0) {
    Aster_Speak(ACTOR_ASTER_OTHER, MsgAsterFractureNorthernView);
    Aster_Speak(ACTOR_ASTER_OTHER, MsgAsterRevelationOtherIsaac);
    Aster_Speak(ACTOR_ASTER_OTHER, MsgAsterRevelationOtherIsaac2);
    GameFlag_Set(ASTER_REVEALED);
  } else {
    Aster_Speak(ACTOR_ASTER_OTHER, MsgAsterRevelationOtherIsaac2);
  }
  Event_End();
}
/// Step-on approach tiles surround solid scenery. Repeat visits without a
/// new stage do nothing, preventing a dialogue loop on the main walkway.
static void Aster_VisitWell(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_FRACTURED)) {
    if (!GameFlag_Get(ASTER_REVISITED_WELL)) {
      FieldMessage_Show(MsgAsterFractureWell, 1);
      GameFlag_Set(ASTER_REVISITED_WELL);
    }
  } else if (!GameFlag_Get(ASTER_SEEN_WELL)) {
    FieldMessage_Show(MsgAsterArrivalWell, 1);
    GameFlag_Set(ASTER_SEEN_WELL);
    Aster_CheckFracture();
  }
  Event_End();
}
static void Aster_VisitMemorial(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_REVEALED)) {
    if (!GameFlag_Get(ASTER_REVEALED_MEMORIAL)) {
      FieldMessage_Show(MsgAsterRevelationMemorial, 1);
      FieldMessage_Show(MsgAsterRevelationAshEcho, 1);
      FieldMessage_Show(MsgAsterRevelationAshEcho2, 1);
      GameFlag_Set(ASTER_REVEALED_MEMORIAL);
    }
  } else if (GameFlag_Get(ASTER_FRACTURED)) {
    if (!GameFlag_Get(ASTER_REVISITED_MEMORIAL)) {
      FieldMessage_Show(MsgAsterFractureMemorial, 1);
      GameFlag_Set(ASTER_REVISITED_MEMORIAL);
    }
  } else if (!GameFlag_Get(ASTER_SEEN_MEMORIAL)) {
    FieldMessage_Show(MsgAsterArrivalMemorial, 1);
    GameFlag_Set(ASTER_SEEN_MEMORIAL);
    Aster_CheckFracture();
  }
  Event_End();
}
static void Aster_VisitDoor(void) {
  Event_Start();
  if (GameFlag_Get(ASTER_FRACTURED)) {
    if (!GameFlag_Get(ASTER_REVISITED_DOOR)) {
      FieldMessage_Show(MsgAsterFractureSealedDoor, 1);
      GameFlag_Set(ASTER_REVISITED_DOOR);
    }
  } else if (!GameFlag_Get(ASTER_SEEN_DOOR)) {
    FieldMessage_Show(MsgAsterDoorClosed, 1);
    GameFlag_Set(ASTER_SEEN_DOOR);
  }
  Event_End();
}

// Exterior thresholds have no linked house interiors in this prototype.
// Avoid replaying the same automatic STEP-trigger text on every crossing, but
// let each door respond again when the town's history changes.
static void Aster_ShowThresholdOnce(s32 seenFlag, s32 message) {
  if (GameFlag_Get(seenFlag)) {
    return;
  }
  Event_Start();
  FieldMessage_Show(message, 1);
  GameFlag_Set(seenFlag);
  Event_End();
}
static void Aster_VisitInnThreshold(void) {
  if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_ShowThresholdOnce(ASTER_INN_THRESHOLD_FRACTURE, MsgAsterFractureInn);
  } else {
    Aster_ShowThresholdOnce(ASTER_INN_THRESHOLD_ARRIVAL, MsgAsterArrivalInn);
  }
}
static void Aster_VisitWestHomeThreshold(void) {
  if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_ShowThresholdOnce(ASTER_WEST_HOME_THRESHOLD_FRACTURE,
                            MsgAsterFractureHome);
  } else {
    Aster_ShowThresholdOnce(ASTER_WEST_HOME_THRESHOLD_ARRIVAL,
                            MsgAsterArrivalHome);
  }
}
static void Aster_VisitEastHomeThreshold(void) {
  if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_ShowThresholdOnce(ASTER_EAST_HOME_THRESHOLD_FRACTURE,
                            MsgAsterFractureDuplicateA);
  } else {
    Aster_ShowThresholdOnce(ASTER_EAST_HOME_THRESHOLD_ARRIVAL,
                            MsgAsterArrivalGreeterRepeat);
  }
}
static void Aster_VisitShopThreshold(void) {
  if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_ShowThresholdOnce(ASTER_SHOP_THRESHOLD_FRACTURE,
                            MsgAsterFractureHome);
  } else {
    Aster_ShowThresholdOnce(ASTER_SHOP_THRESHOLD_ARRIVAL, MsgAsterArrivalHome);
  }
}
static void Aster_VisitDuplicateHomeThreshold(void) {
  if (GameFlag_Get(ASTER_REVEALED)) {
    Aster_ShowThresholdOnce(ASTER_DUPLICATE_HOME_THRESHOLD_REVELATION,
                            MsgAsterRevelationOtherIsaac2);
  } else if (GameFlag_Get(ASTER_FRACTURED)) {
    Aster_ShowThresholdOnce(ASTER_DUPLICATE_HOME_THRESHOLD_FRACTURE,
                            MsgAsterFractureDuplicateB);
  } else {
    Aster_ShowThresholdOnce(ASTER_DUPLICATE_HOME_THRESHOLD_ARRIVAL,
                            MsgAsterArrivalGreeterRepeat);
  }
}

static struct SceneEntrance sAsterEntrances[] = {
  {ENTRANCE_DEFAULT, CONDITION_ALWAYS, 512, 0, 976, FACING_NORTH,
   0, -1, -1, -1, -1, 0},
  {SCENE_TABLE_END},
};
/// Experimental return entrance 98; walkability and arrival unverified.
static u32 sAsterExits[] = {
  SCENE_EXITS(Aster),
  SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, 98),
  SCENE_EXITS_END,
};
static struct ActorTemplate sAsterActors[] = {
  {SPRITE_OLD_MAN_WITH_CANE, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(432), 0, PIXELS(512), FACING_SOUTH, TALK_FACING_PARTY, 0},
  {SPRITE_WOMAN_IN_BLUE_DRESS, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(256), 0, PIXELS(576), FACING_NORTH, TALK_FACING_PARTY, 0},
  {SPRITE_WOMAN_IN_BLUE_DRESS, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(384), 0, PIXELS(576), FACING_SOUTH, TALK_FACING_PARTY, 0},
  {SPRITE_BOY_WITH_FAIR_HAIR, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(544), 0, PIXELS(608), FACING_SOUTH, TALK_FACING_PARTY, 0},
  {SPRITE_WOMAN_IN_GREEN_DRESS, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(672), 0, PIXELS(784), FACING_WEST, TALK_FACING_PARTY, 0},
  {SPRITE_YOUNG_MAN_WITH_BROWN_HAIR, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(448), 0, PIXELS(336), FACING_SOUTH, TALK_FACING_PARTY, 0},
  {SPRITE_WOMAN_IN_BLUE_DRESS, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(608), 0, PIXELS(576), FACING_WEST, TALK_FACING_PARTY, 0},
  // Native indexed scenery actors appended AFTER the seven talking NPCs.
  // No story actor ID is shifted; these locations remain collision-reserved.
  {SPRITE_ASTER_DRY_WELL, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(512), 0, PIXELS(544), FACING_SOUTH, TALK_FACING_KEEP, 0},
  {SPRITE_ASTER_MEMORIAL, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(464), 0, PIXELS(304), FACING_SOUTH, TALK_FACING_KEEP, 0},
  {SPRITE_ASTER_SANCTUM, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(672), 0, PIXELS(528), FACING_SOUTH, TALK_FACING_KEEP, 0},
  {SPRITE_ASTER_ADDITIONAL_HOME, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(208), 0, PIXELS(912), FACING_SOUTH, TALK_FACING_KEEP, 0},
  // Vanilla Golden Sun signpost, placed beside the safe main south approach.
  // Leave the (32,62) exit marker and (32,61) player spawn untouched.
  {SPRITE_SIGNPOST, CONDITION_ALWAYS, MOVEMENT_TYPE_STAND,
   PIXELS(480), 0, PIXELS(960), FACING_SOUTH, TALK_FACING_KEEP, 0},
  {SCENE_TABLE_END},
};
static struct Trigger sAsterTriggers[] = {
  {TRIGGER_EXIT, ASTER_TO_WORLD_MAP, CONDITION_ALWAYS, ASTER_TO_WORLD_MAP},
  {TRIGGER_STEP, ASTER_MB_WELL, CONDITION_ALWAYS, EVENT(Aster_VisitWell)},
  {TRIGGER_STEP, ASTER_MB_MEMORIAL, CONDITION_ALWAYS,
   EVENT(Aster_VisitMemorial)},
  {TRIGGER_STEP, ASTER_MB_SEALED_DOOR, CONDITION_ALWAYS,
   EVENT(Aster_VisitDoor)},
  {TRIGGER_STEP, ASTER_MB_INN, CONDITION_ALWAYS,
   EVENT(Aster_VisitInnThreshold)},
  {TRIGGER_STEP, ASTER_MB_WEST_HOME, CONDITION_ALWAYS,
   EVENT(Aster_VisitWestHomeThreshold)},
  {TRIGGER_STEP, ASTER_MB_EAST_HOME, CONDITION_ALWAYS,
   EVENT(Aster_VisitEastHomeThreshold)},
  {TRIGGER_STEP, ASTER_MB_SHOP, CONDITION_ALWAYS,
   EVENT(Aster_VisitShopThreshold)},
  {TRIGGER_STEP, ASTER_MB_DUPLICATE_HOME, CONDITION_ALWAYS,
   EVENT(Aster_VisitDuplicateHomeThreshold)},
  {TRIGGER_TALK, ACTOR_ASTER_ELDER, CONDITION_ALWAYS, EVENT(Aster_TalkElder)},
  {TRIGGER_TALK, ACTOR_ASTER_INNKEEPER, CONDITION_ALWAYS,
   EVENT(Aster_TalkInnkeeper)},
  {TRIGGER_TALK, ACTOR_ASTER_GREETER, CONDITION_ALWAYS,
   EVENT(Aster_TalkGreeter)},
  {TRIGGER_TALK, ACTOR_ASTER_BOY, CONDITION_ALWAYS, EVENT(Aster_TalkBoy)},
  {TRIGGER_TALK, ACTOR_ASTER_RESIDENT, CONDITION_ALWAYS,
   EVENT(Aster_TalkResident)},
  {TRIGGER_TALK, ACTOR_ASTER_OTHER, CONDITION_ALWAYS, EVENT(Aster_TalkOther)},
  {TRIGGER_TALK, ACTOR_ASTER_MIRROR, CONDITION_ALWAYS,
   EVENT(Aster_TalkMirror)},
  {TRIGGER_TALK, ACTOR_ASTER_GATE_SIGN, CONDITION_ALWAYS,
   EVENT(Aster_ReadGateSign)},
  {PSYNERGY_ON_ACTOR(ABILITY_MIND_READ), ACTOR_ASTER_INNKEEPER,
   CONDITION_ALWAYS, MSGNO(MsgAsterInnkeeperMindRead)},
  {PSYNERGY_ON_ACTOR(ABILITY_MIND_READ), ACTOR_ASTER_ELDER,
   CONDITION_ALWAYS, MSGNO(MsgAsterElderMindRead)},
  {PSYNERGY_ON_ACTOR(ABILITY_MIND_READ), ACTOR_ASTER_OTHER,
   CONDITION_ALWAYS, MSGNO(MsgAsterOtherIsaacMindRead)},
  {TRIGGERS_END},
};
s32 Scene_Initialize(void) { return 0; }
const struct SceneEntrance *Scene_GetEntrances(void) { return sAsterEntrances; }
const u32 *Scene_GetExits(void) { return sAsterExits; }
const struct ActorTemplate *Scene_GetActorTemplates(void) { return sAsterActors; }
const struct Trigger *Scene_GetTriggers(void) { return sAsterTriggers; }
const struct SceneExitRegion *Scene_GetExitRegions(void) { return NULL; }
