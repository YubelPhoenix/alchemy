#ifndef ALCHEMY_WORLD_STATE_H
#define ALCHEMY_WORLD_STATE_H

/// @file
/// Golden Sun: Ashfall's slowly worsening world. Each lit lighthouse lets more
/// Alchemy back in, and the weather follows: rain that does not stop and a
/// duller, darker light. Scenes call WorldState_Apply when they load.

#include "event_layer.h"
#include "flags.h"
#include "speaker.h"
#include "scene_ids.h"
#include "save_block.h"
#include "graphics/palbuf.h"
#include "unit/overworld/event_commands.h"

/// How far Alchemy has returned: 0 until the Sol Sanctum erupts and the Stars
/// are taken, 1 from then on, 2 once Mercury Lighthouse is lit.
static inline s32 WorldState_GetStage(void) {
  if (GameFlag_Get(FLAG_MERCURY_LIGHTHOUSE_LIT) != 0) {
    return 2;
  }
  return GameFlag_Get(FLAG_SOL_SANCTUM_ERUPTED) != 0;
}

/// Compatibility hook for scenes written before the full-game review.
/// The global ash-tint renderer was disabled; this function intentionally
/// does nothing until a new visual design has been separately validated.
static inline void WorldState_ApplyTintOnly(void) {}

/// Starts the current weather effect: rain in scenes that opt in once the
/// Mercury Lighthouse has been lit. No global grey tint is enabled.
static inline void WorldState_Apply(void) {
  if (WorldState_GetStage() >= 2) {
    Weather_StartRain();
  }
}

#endif
