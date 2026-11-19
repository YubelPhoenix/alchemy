/// @file
/// Falling Wind (Ashfall), after the leaf-and-wind ability Mia uses in a
/// pre-release screenshot: two animations for its two parts. The storm, a
/// canvas animation: tumbling leaves (parts/falling_wind_leaves.h) sweep
/// across the enemies on a green ramp, leaving short trails, and strike them
/// three times. The revive, Dew's beams of light turned spring green
/// (parts/djinn_beams.c compiled again with DJINN_BEAMS_GREEN), as the leaves
/// settle on the fallen. It sits in the ROM tail, as perfecti.c does.

#define DJINN_BEAMS_GREEN
#define BattleAnim_RunRevive FallingWind_UnusedRevive
#define BattleAnim_RunDew FallingWind_UnusedDew
#define BattleAnim_RunDjinnBeams FallingWind_RunBeams
#include "parts/djinn_beams.c"
#include "parts/falling_wind_leaves.h"

/// Leaves in flight at once; each is a particle (PARTICLES).
#define FALLING_WIND_LEAVES 24
/// Frames new leaves are thrown in; the storm runs a little longer.
#define FALLING_WIND_SPAWN_TICKS 40
#define FALLING_WIND_TICKS 66
/// Frames the canvas keeps fading after the storm, so its trails clear.
#define FALLING_WIND_FADE_FRAMES 10
/// Frames a struck enemy flashes white.
#define FALLING_WIND_FLASH_FRAMES 5

/// Abilities: Falling Wind's revive (ABILITY_FALLING_WIND_REVIVE). Dew's
/// motes and column of light on each fallen ally, in spring green.
void BattleAnim_RunFallingWindRevive(struct BattleAnimArgs *args) {
  FallingWind_RunBeams(args, ELEMENT_MERCURY);
}

/// Abilities: Falling Wind (ABILITY_FALLING_WIND). Leaves blown from the
/// left tumble across the enemies, a band around their middle, two at a
/// time; the enemies are jolted twice and the damage lands with the third
/// blow. The leaves' places come from a private sequence, so the battle's
/// random numbers are left alone.
void BattleAnim_RunFallingWind(struct BattleAnimArgs *args) {
  void **slots;
  void **cursor;
  struct BattleAnimWork *work;
  void *canvas;
  DrawRectangle draw;
  struct ScreenPoint point;
  struct Particle *leaf;
  u16 *palette;
  u32 seed = 0x51ed2701;
  s32 tick, i, level, bandY, frame, size;
  const u16 *shape;

  ANIM_GET_SLOTS(slots, cursor, work, canvas);
  work->args = args;
  BattleAnim_StartCanvasLayer(BGCNT_PRIORITY(1));
  // The green ramp: dark leaf green to the vines' bright teal, then to a pale
  // spring white where trails and leaves overlap.
  palette = (u16 *)BG_PLTT;
  for (level = 0; level < 64; level++) {
    if (level <= 40)
      palette[level] = RGB(level * 3 / 40, level * 26 / 40, level * 18 / 40);
    else
      palette[level] = RGB(3 + (level - 40) * 22 / 23,
                           26 + (level - 40) * 5 / 23,
                           18 + (level - 40) * 10 / 23);
  }
  // The band the storm crosses: around the enemies' middle.
  bandY = 0;
  for (i = 0; i < args->targetCount; i++) {
    Projection_Sprite(args->targets[i], &point);
    bandY += point.y;
  }
  bandY = args->targetCount > 0 ? bandY / args->targetCount : 64;
  ANIM_LOAD_BLITTER(HEAP_SLOT_RAM_CODE, ANIM_CLIP_BOUNDS, COMPOSITE_ADDITIVE);
  draw = (DrawRectangle)ANIM_SLOT(slots, HEAP_SLOT_RAM_CODE);
  ANIM_START_TRANSFER(work, CANVAS_COPY_AND_FADE, CANVAS_FADE_THREE_QUARTERS);

  for (i = 0; i < FALLING_WIND_LEAVES; i++)
    PARTICLES[i].variant = 0;
  for (tick = 0; tick < FALLING_WIND_TICKS; tick++) {
    // Two new leaves a frame while the wind blows, in free places.
    if (tick < FALLING_WIND_SPAWN_TICKS) {
      s32 thrown = 0;
      for (i = 0; i < FALLING_WIND_LEAVES && thrown < 2; i++) {
        leaf = &PARTICLES[i];
        if (leaf->variant != 0)
          continue;
        seed = seed * 1103515245 + 12345;
        leaf->x = (-6 - (s32)((seed >> 16) % 10)) << 8;
        seed = seed * 1103515245 + 12345;
        leaf->y = (bandY - 36 + (s32)((seed >> 16) % 64)) << 8;
        seed = seed * 1103515245 + 12345;
        leaf->velocityX = 0x280 + (s32)((seed >> 16) % 0x180);
        leaf->velocityY = (seed & 0x100) ? 0x40 : -0x40;
        leaf->z = (s32)((seed >> 20) % 18); // size and first frame
        leaf->variant = 1;
        thrown++;
      }
    }
    for (i = 0; i < FALLING_WIND_LEAVES; i++) {
      leaf = &PARTICLES[i];
      if (leaf->variant == 0)
        continue;
      leaf->x += leaf->velocityX;
      leaf->y += leaf->velocityY;
      // Each leaf sways: its drift turns over every 12 frames.
      if ((leaf->variant++ % 12) == 0)
        leaf->velocityY = -leaf->velocityY;
      if ((leaf->x >> 8) > 136) {
        leaf->variant = 0;
        continue;
      }
      size = leaf->z / 6;
      frame = size * 6 + (leaf->z + leaf->variant / 3) % 6;
      shape = sFallingWindLeafFrames[frame];
      draw(canvas, (void *)(sFallingWindLeafLevels + shape[0]),
           (leaf->x >> 8) - shape[1] / 2, (leaf->y >> 8) - shape[2] / 2,
           shape[1], shape[2]);
    }
    if (tick == 0 || tick == 20)
      Sound_PlaySongFar(SE_WHOOSH);
    if (tick == 16 || tick == 28 || tick == 40) {
      if (tick == 40)
        ANIM_SHOW_DAMAGE(SE_IMPACT);
      for (i = 0; i < args->targetCount; i++) {
        BattleAnim_TintBattler(args->targets[i], SPRITE_COLOR_WHITE,
                               POSE_DAMAGE, i, FALLING_WIND_FLASH_FRAMES);
        BattleMotion_ApplyKnockbackFar(args->targets[i], KNOCKBACK_JOLT);
      }
    }
    ANIM_END_FRAME(work);
  }
  for (tick = 0; tick < FALLING_WIND_FADE_FRAMES; tick++)
    ANIM_END_FRAME(work);
  ANIM_FINISH_CANVAS_ONE_BLITTER();
}
