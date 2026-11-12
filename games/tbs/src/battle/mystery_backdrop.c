/// @file
/// The Mystery Leader's backdrop (Ashfall): its crimson beacons pulse and its
/// stars twinkle, by rewriting palette entries the picture reserves for them
/// (tools/dark_story/build_mystery_backdrop.py). This object sits at the start
/// of the ROM tail, beside battle_anim/perfecti.c, so the battle bank only
/// gains the two calls in BattleBackground_Load and BattleBackground_Free.

#include "battle_internal.h"

/// Each beacon's core, then its three halo rings, outermost last.
#define MYSTERY_BEACON_FIRST 112
#define MYSTERY_BEACON_ENTRIES 4
/// Eight groups of one-pixel stars, each twinkling on its own beat.
#define MYSTERY_STAR_FIRST 116
#define MYSTERY_STAR_GROUPS 8
/// Frames for one beacon pulse, dim to bright and back (1.6 seconds).
#define MYSTERY_BEACON_PERIOD 96
/// Frames for one star's twinkle cycle, before its group's own speed.
#define MYSTERY_STAR_PERIOD 256

/// Mixes RGB555 components from (r0, g0, b0) toward (r1, g1, b1) by `level`
/// (0 to 256), then scales by the battle's brightness (Q16).
static u16 Mystery_MixColor(s32 r0, s32 g0, s32 b0, s32 r1, s32 g1, s32 b1,
                            s32 level, s32 scale) {
  s32 red = r0 + ((r1 - r0) * level >> 8);
  s32 green = g0 + ((g1 - g0) * level >> 8);
  s32 blue = b0 + ((b1 - b0) * level >> 8);

  red = red * scale >> 16;
  green = green * scale >> 16;
  blue = blue * scale >> 16;
  return (blue << 10) | (green << 5) | red;
}

/// A triangle wave over `period` frames: 0 up to 256 and back.
static s32 Mystery_Triangle(u32 frame, u32 period) {
  u32 t = frame % period;
  u32 half = period / 2;

  if (t >= half)
    t = period - 1 - t;
  return (s32)(t * 256 / (half - 1));
}

/// The Mystery Leader's backdrop only: pulses the beacons and twinkles the
/// stars. Runs every VBlank while her battle lasts, reading only gVBlankCount,
/// and, as Heart_StepBackdropGlow does, writes only while the background is
/// zoomed, so battle animations that take the palette over are left alone.
/// Added by BattleBackground_Load, removed by BattleBackground_Free.
void Mystery_StepBackdropGlow(void) {
  struct BattleWork *battle = gBattleWork;
  struct BattleBackgroundWork *view =
      HEAP_SLOT_BLOCK(HEAP_SLOT_BATTLE_BACKGROUND);
  u32 frame = gVBlankCount;
  s32 scale, pulse, level, k;

  if (battle == NULL || view == NULL || view->mode != BATTLE_BACKGROUND_ZOOMED)
    return;
  scale = battle->brightness;
  if (scale > Q16_ONE)
    scale = Q16_ONE;

  // The core glows from a dim ember to bright crimson; each halo ring takes
  // half the light of the one inside it, over the void's violet.
  pulse = Mystery_Triangle(frame, MYSTERY_BEACON_PERIOD);
  BATTLE_BG_PALETTE[MYSTERY_BEACON_FIRST] =
      Mystery_MixColor(14, 2, 2, 31, 10, 8, pulse, scale);
  for (k = 1; k < MYSTERY_BEACON_ENTRIES; k++) {
    level = (64 + pulse * 3 / 4) >> (k - 1);
    BATTLE_BG_PALETTE[MYSTERY_BEACON_FIRST + k] =
        Mystery_MixColor(5, 3, 8, 31, 6, 5, level * 3 / 4, scale);
  }

  // Each group runs at its own speed and phase. A star is dim violet most of
  // the time and flares white only in the top quarter of its wave.
  for (k = 0; k < MYSTERY_STAR_GROUPS; k++) {
    level = Mystery_Triangle(frame * (4 + (k & 3)) / 4 + (u32)k * 97,
                             MYSTERY_STAR_PERIOD) * 4 - 768;
    if (level < 0)
      level = 0;
    BATTLE_BG_PALETTE[MYSTERY_STAR_FIRST + k] =
        Mystery_MixColor(12, 9, 18, 31, 29, 31, level, scale);
  }
}
