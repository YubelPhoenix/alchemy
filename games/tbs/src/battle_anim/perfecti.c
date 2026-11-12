/// @file
/// The Mystery Leader's own attacks (Ashfall): seven canvas animations drawn
/// from the RLE frames of parts/perfecti_frames.rle, in Gotterkanone's violet
/// ramp. This object sits at the start of the ROM tail rather than in the
/// battle-animation bank, which the original game left almost full; its calls
/// into that bank stay within a Thumb branch's 4 MB reach.

#include "battle_anim_internal.h"
#include "parts/gotterkanone_stream.h"
#include "parts/perfecti_frames.h"

extern const u8 gPerfectiCompressedFrames[];

#define PERFECTI_FRAME_WIDTH 64
#define PERFECTI_FRAME_HEIGHT 48
#define PERFECTI_FRAME_BYTES (PERFECTI_FRAME_WIDTH * PERFECTI_FRAME_HEIGHT)
/// Frames the canvas keeps fading after the last picture, so trails clear.
#define PERFECTI_FADE_FRAMES 8
/// Frames a struck battler flashes white.
#define PERFECTI_FLASH_FRAMES 6

/// What every attack draws with: the canvas, its blitter and where the user
/// and first target stand, in canvas texels (half the screen's x).
struct PerfectiStage {
  struct BattleAnimArgs *args;
  struct BattleAnimWork *work;
  void *canvas;
  DrawRectangle draw;
  s32 userX, userY;
  s32 targetX, targetY;
  s32 decoded; ///< the frame now in work->sheet, or -1
};

/// Opens the canvas, writes the 64-step violet-to-white ramp and builds a
/// lightening blitter, as Gotterkanone does.
static void Perfecti_Start(struct BattleAnimArgs *args,
                           struct PerfectiStage *stage) {
  void **slots;
  void **cursor;
  struct ScreenPoint point;
  u16 *palette;
  s32 level, red, green, blue;

  ANIM_GET_SLOTS(slots, cursor, stage->work, stage->canvas);
  stage->args = args;
  stage->work->args = args;
  stage->decoded = -1;
  BattleAnim_StartCanvasLayer(BGCNT_PRIORITY(1));
  palette = (u16 *)BG_PLTT;
  for (level = 0; level < 64; level++) {
    if (level <= 31) {
      red = level * 24 / 31;
      green = level * 3 / 31;
      blue = level * 25 / 31;
    } else {
      red = 24 + (level - 31) * 7 / 32;
      green = 3 + (level - 31) * 28 / 32;
      blue = 25 + (level - 31) * 6 / 32;
    }
    palette[level] = RGB(red, green, blue);
  }
  Projection_Unit(args->user, &point);
  stage->userX = point.x / 2;
  stage->userY = point.y;
  Projection_Unit(args->targets[0], &point);
  stage->targetX = point.x / 2;
  stage->targetY = point.y;
  ANIM_LOAD_BLITTER(HEAP_SLOT_RAM_CODE, ANIM_CLIP_BOUNDS, COMPOSITE_LIGHTEN);
  stage->draw = (DrawRectangle)ANIM_SLOT(slots, HEAP_SLOT_RAM_CODE);
  ANIM_START_TRANSFER(stage->work, CANVAS_COPY_AND_FADE,
                      CANVAS_FADE_THREE_QUARTERS);
}

/// Draws frame `frame` centred on (x, y). Only one frame is unpacked into
/// the sheet at a time, so each tick draws copies of a single frame.
static void Perfecti_Draw(struct PerfectiStage *stage, s32 frame, s32 x,
                          s32 y) {
  const u8 *source;

  if (stage->decoded != frame) {
    source = gPerfectiCompressedFrames + sPerfectiFrameOffsets[frame];
    if (gotterkanone_decode_frame(source,
                                  sPerfectiFrameOffsets[frame + 1] -
                                      sPerfectiFrameOffsets[frame],
                                  stage->work->sheet, PERFECTI_FRAME_BYTES) != 0)
      return;
    stage->decoded = frame;
  }
  stage->draw(stage->canvas, stage->work->sheet, x - PERFECTI_FRAME_WIDTH / 2,
              y - PERFECTI_FRAME_HEIGHT / 2, PERFECTI_FRAME_WIDTH,
              PERFECTI_FRAME_HEIGHT);
}

/// Flashes every target white in its damage pose.
static void Perfecti_Strike(struct PerfectiStage *stage) {
  s32 i;

  for (i = 0; i < stage->args->targetCount; i++)
    BattleAnim_TintBattler(stage->args->targets[i], SPRITE_COLOR_WHITE,
                           POSE_DAMAGE, i, PERFECTI_FLASH_FRAMES);
}

/// Lets the trails fade, then closes the canvas.
static void Perfecti_Finish(struct PerfectiStage *stage) {
  s32 tick;

  for (tick = 0; tick < PERFECTI_FADE_FRAMES; tick++)
    ANIM_END_FRAME(stage->work);
  ANIM_FINISH_CANVAS_ONE_BLITTER();
}

/// Sends `copies` projectiles from the user to the first target, each
/// `stagger` frames after the last, over `travel` frames, bowing `bow`
/// texels apart; then holds the last at the target for `pulses` flashes.
/// The damage shows when the last copy lands, or on the last pulse.
static void Perfecti_RunVolley(struct BattleAnimArgs *args, s32 first,
                               s32 count, s32 copies, s32 stagger,
                               s32 travel, s32 bow, s32 pulses) {
  struct PerfectiStage stage;
  s32 tick, copy, local, x, y, spread, last;

  Perfecti_Start(args, &stage);
  last = (copies - 1) * stagger + travel;
  for (tick = 0; tick <= last + pulses * 5; tick++) {
    for (copy = 0; copy < copies; copy++) {
      local = tick - copy * stagger;
      if (local < 0)
        continue;
      if (local > travel) {
        if (copy == copies - 1 && pulses > 0)
          Perfecti_Draw(&stage, first + tick % count, stage.targetX,
                        stage.targetY);
        continue;
      }
      spread = (copy * 2 - (copies - 1)) * bow;
      x = stage.userX + (stage.targetX - stage.userX) * local / travel;
      y = stage.userY + (stage.targetY - stage.userY) * local / travel +
          spread * 4 * local * (travel - local) / (travel * travel);
      Perfecti_Draw(&stage, first + tick % count, x, y);
      if (local == travel) {
        Perfecti_Strike(&stage);
        if (copy == copies - 1 && pulses == 0)
          ANIM_SHOW_DAMAGE(SE_IMPACT);
      }
    }
    if (pulses > 0 && tick > last && (tick - last) % 5 == 0) {
      Perfecti_Strike(&stage);
      if (tick == last + pulses * 5)
        ANIM_SHOW_DAMAGE(SE_IMPACT);
    }
    ANIM_END_FRAME(stage.work);
  }
  Perfecti_Finish(&stage);
}

/// Plays frames at the first target for `ticks` frames, `rate` frames each,
/// once through or looping; strikes at `hit` and again at `hit2` (0 for
/// none), showing the damage at `hit`.
static void Perfecti_RunAtTarget(struct BattleAnimArgs *args, s32 first,
                                 s32 count, s32 ticks, s32 rate, s32 loop,
                                 s32 hit, s32 hit2) {
  struct PerfectiStage stage;
  s32 tick, frame;

  Perfecti_Start(args, &stage);
  for (tick = 0; tick < ticks; tick++) {
    frame = tick / rate;
    if (loop)
      frame %= count;
    else if (frame >= count)
      frame = count - 1;
    Perfecti_Draw(&stage, first + frame, stage.targetX, stage.targetY);
    if (tick == hit) {
      Perfecti_Strike(&stage);
      ANIM_SHOW_DAMAGE(SE_IMPACT);
    } else if (hit2 != 0 && tick == hit2)
      Perfecti_Strike(&stage);
    ANIM_END_FRAME(stage.work);
  }
  Perfecti_Finish(&stage);
}

/// A beam across the whole canvas at the target's height. `charge` frames
/// of gathering light at the user come first (four frames each), then
/// `grow` frames of the beam swelling, `sustain` frames of its loop of
/// `loopCount` and `shrink` frames fading, two frames each. The damage shows
/// `hit` frames into the loop.
static void Perfecti_RunBeam(struct BattleAnimArgs *args, s32 first,
                             s32 charge, s32 grow, s32 loopCount, s32 sustain,
                             s32 shrink, s32 hit) {
  struct PerfectiStage stage;
  s32 tick, frame, beamTick, total;

  Perfecti_Start(args, &stage);
  total = charge * 4 + grow * 2 + sustain + shrink * 2;
  for (tick = 0; tick < total; tick++) {
    if (tick < charge * 4) {
      Perfecti_Draw(&stage, first + tick / 4, stage.userX, stage.userY);
      ANIM_END_FRAME(stage.work);
      continue;
    }
    beamTick = tick - charge * 4;
    if (beamTick < grow * 2)
      frame = charge + beamTick / 2;
    else if (beamTick < grow * 2 + sustain)
      frame = charge + grow + (beamTick - grow * 2) / 2 % loopCount;
    else
      frame = charge + grow + loopCount + (beamTick - grow * 2 - sustain) / 2;
    Perfecti_Draw(&stage, first + frame, PERFECTI_FRAME_WIDTH / 2,
                  stage.targetY);
    Perfecti_Draw(&stage, first + frame, PERFECTI_FRAME_WIDTH * 3 / 2,
                  stage.targetY);
    if (beamTick == grow * 2 + hit) {
      Perfecti_Strike(&stage);
      ANIM_SHOW_DAMAGE(SE_IMPACT);
    }
    ANIM_END_FRAME(stage.work);
  }
  Perfecti_Finish(&stage);
}

/// Abilities: EX Gotterkanone. A bigger orb flies at the target and bursts
/// five times there.
void BattleAnim_RunExGotterkanone(struct BattleAnimArgs *args) {
  Perfecti_RunVolley(args, PERFECTI_EX_GOTTERKANONE_FIRST,
                     PERFECTI_EX_GOTTERKANONE_COUNT, 1, 0, 30, 0, 5);
}

/// Abilities: Ransnetz. Three homing motes, launched a moment apart, bow
/// apart and close in on the target.
void BattleAnim_RunRansnetz(struct BattleAnimArgs *args) {
  Perfecti_RunVolley(args, PERFECTI_RANSNETZ_FIRST, PERFECTI_RANSNETZ_COUNT, 3,
                     6, 24, 12, 0);
}

/// Abilities: Explosion. A flash and a flattened shock ring burst on the
/// target.
void BattleAnim_RunPerfectiExplosion(struct BattleAnimArgs *args) {
  Perfecti_RunAtTarget(args, PERFECTI_EXPLOSION_FIRST, PERFECTI_EXPLOSION_COUNT,
                       36, 3, 0, 6, 15);
}

/// Abilities: P-Vortex. Three spiral arms wind around the target.
void BattleAnim_RunPVortex(struct BattleAnimArgs *args) {
  Perfecti_RunAtTarget(args, PERFECTI_P_VORTEX_FIRST, PERFECTI_P_VORTEX_COUNT,
                       44, 2, 1, 24, 0);
}

/// Abilities: Glepnir. A binding beam crosses the screen at the target, its
/// chain knots running along it.
void BattleAnim_RunGlepnir(struct BattleAnimArgs *args) {
  Perfecti_RunBeam(args, PERFECTI_GLEPNIR_FIRST, 0, 3, 6, 30, 3, 10);
}

/// Abilities: EX Sternbrecher. Light gathers at the user, then a thick laser
/// crosses the screen at the target.
void BattleAnim_RunSternbrecher(struct BattleAnimArgs *args) {
  Perfecti_RunBeam(args, PERFECTI_STERNBRECHER_FIRST, 4, 0, 8, 36, 0, 8);
}

/// Abilities: P-Storm. Bolts rain down around the target, three a frame.
/// The bolts' places come from a private sequence, so the battle's random
/// numbers are left alone.
void BattleAnim_RunPStorm(struct BattleAnimArgs *args) {
  struct PerfectiStage stage;
  s32 tick, bolt, x, y;
  u32 seed = 0x2545f491;

  Perfecti_Start(args, &stage);
  for (tick = 0; tick < 48; tick++) {
    for (bolt = 0; bolt < 3; bolt++) {
      seed = seed * 1103515245 + 12345;
      x = stage.targetX + (s32)((seed >> 16) % 96) - 48;
      seed = seed * 1103515245 + 12345;
      y = stage.targetY - 20 + (s32)((seed >> 16) % 16) - 8;
      Perfecti_Draw(&stage, PERFECTI_P_STORM_FIRST + tick / 2 % PERFECTI_P_STORM_COUNT,
                    x, y);
    }
    if (tick % 8 == 0 && tick != 0)
      Perfecti_Strike(&stage);
    if (tick == 24)
      ANIM_SHOW_DAMAGE(SE_IMPACT);
    ANIM_END_FRAME(stage.work);
  }
  Perfecti_Finish(&stage);
}
