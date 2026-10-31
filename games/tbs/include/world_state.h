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

/// Which of the three haunted areas the scene is in, if any: Kolima Forest
/// (a sickly green rot), Tret Tree (the glow of embers) and Mercury Lighthouse
/// (a cold drowned blue). Each gives the ash tint its own cast.
static inline s32 WorldState_GetAreaLook(void) {
  s32 scene = (s32)gSaveBlock.sceneId;

  if (scene == (s32)&SceneId_KolimaForestEntrance ||
      scene == (s32)&SceneId_KolimaForestGlade ||
      scene == (s32)&SceneId_KolimaForestCliff ||
      scene == (s32)&SceneId_KolimaForestFloodgate ||
      scene == (s32)&SceneId_KolimaForestTree) {
    return 1;
  }
  if (scene == (s32)&SceneId_TreeRooms || scene == (s32)&SceneId_TretTreeBranch) {
    return 2;
  }
  if (scene == (s32)&SceneId_MercuryLighthouseEntrance ||
      scene == (s32)&SceneId_MercuryLighthouseLower ||
      scene == (s32)&SceneId_MercuryLighthouseMiddle ||
      scene == (s32)&SceneId_MercuryLighthouseUpper ||
      scene == (s32)&SceneId_MercuryLighthouseExterior) {
    return 3;
  }
  return 0;
}

/// Dulls and darkens one RGB555 colour to the grey-olive of ash, or, in one of
/// the three haunted areas, to that area's own cast.
static inline u16 WorldState_TintColour(u16 colour) {
  s32 r = colour & 31;
  s32 g = (colour >> 5) & 31;
  s32 b = (colour >> 10) & 31;
  s32 grey = (r + g + b) / 3;
  s32 look = WorldState_GetAreaLook();
  s32 kr = 17;
  s32 kg = 17;
  s32 kb = 15;

  if (look == 1) {
    kr = 13;
    kg = 21;
    kb = 10;
  } else if (look == 2) {
    kr = 23;
    kg = 16;
    kb = 8;
  } else if (look == 3) {
    kr = 11;
    kg = 16;
    kb = 25;
  }
  r = ((3 * r + 2 * grey) * kr) / 100 + 1;
  g = ((3 * g + 2 * grey) * kg) / 100 + 1;
  b = ((3 * b + 2 * grey) * kb) / 100;
  if (r > 31) {
    r = 31;
  }
  if (g > 31) {
    g = 31;
  }
  if (b > 31) {
    b = 31;
  }
  return r | (g << 5) | (b << 10);
}

/// Dulls and darkens every colour in the palette fade's source palette to
/// the grey-olive of ash, then rebuilds the shown and target colours from it,
/// so the look holds across the scene's fades. Colours put on the screen
/// after this are tinted by PaletteFade_KeepAshTint.
static inline void WorldState_TintPalettes(void) {
  struct PaletteFade *work = gPaletteFadeWork;
  s32 i;

  if (work == 0) {
    return;
  }
  for (i = 0; i < 0x1c0; i++) {
    work->palette[i] = WorldState_TintColour(work->palette[i]);
  }
  PaletteFade_SetSource(PALETTE_TINT_NONE, PALETTES_ALL);
  PaletteFade_SetTarget(PALETTE_TINT_NONE, PALETTES_ALL);
}

/// The task that keeps the ash tint on whatever a scene puts on the screen
/// after it has loaded (color.c).
void PaletteFade_KeepAshTint(void);

/// Kept for scenes that used to tint themselves: the ash tint is now applied
/// to every scene as it loads (SceneManager_Run), so this does nothing.
static inline void WorldState_ApplyTintOnly(void) {}

/// Starts the world's current weather: from stage 2 (Mercury Lighthouse lit)
/// the endless rain. The ash tint from stage 1 on is applied to every scene by
/// SceneManager_Run, so scenes no longer tint themselves.
static inline void WorldState_Apply(void) {
  if (WorldState_GetStage() >= 2) {
    Weather_StartRain();
  }
}

#endif
