#ifndef ALCHEMY_WORLD_STATE_H
#define ALCHEMY_WORLD_STATE_H

/// @file
/// Golden Sun: Ashfall's slowly worsening world. Each lit lighthouse lets more
/// Alchemy back in, and the weather follows: rain that does not stop and a
/// duller, darker light. Scenes call WorldState_Apply when they load.

#include "event_layer.h"
#include "flags.h"
#include "speaker.h"
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

/// Dulls and darkens every colour in the palette fade's source palette to
/// the grey-olive of ash, then rebuilds the shown and target colours from it,
/// so the look holds across the scene's fades.
static inline void WorldState_TintPalettes(void) {
  struct PaletteFade *work = gPaletteFadeWork;
  s32 i;

  if (work == 0) {
    return;
  }
  for (i = 0; i < 0x1c0; i++) {
    s32 colour = work->palette[i];
    s32 r = colour & 31;
    s32 g = (colour >> 5) & 31;
    s32 b = (colour >> 10) & 31;
    s32 grey = (r + g + b) / 3;

    r = ((2 * r + 3 * grey) * 13) / 100 + 2;
    g = ((2 * g + 3 * grey) * 12) / 100 + 1;
    b = ((2 * b + 3 * grey) * 12) / 100;
    work->palette[i] = r | (g << 5) | (b << 10);
  }
  PaletteFade_SetSource(PALETTE_TINT_NONE, PALETTES_ALL);
  PaletteFade_SetTarget(PALETTE_TINT_NONE, PALETTES_ALL);
}

/// Like WorldState_Apply, but without rain, for scenes that already have
/// their own weather (Imil's snow).
static inline void WorldState_ApplyTintOnly(void) {
  if (WorldState_GetStage() >= 1) {
    WorldState_TintPalettes();
  }
}

/// Starts the world's current weather: from stage 1 on (the eruption), rain and the ash tint.
static inline void WorldState_Apply(void) {
  if (WorldState_GetStage() >= 1) {
    Weather_StartRain();
    WorldState_TintPalettes();
  }
}

#endif
