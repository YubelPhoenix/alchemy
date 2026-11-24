/// @file
/// The Mystery Leader's own attacks (Ashfall): eight canvas animations,
/// Gotterkanone's among them, drawn from the RLE frames of
/// parts/perfecti_frames.rle in a violet ramp. Each frame is 32x32 canvas
/// texels, 64x32 on screen, about a battler's size, centred on the middle of
/// the battler's sprite. This object sits at the start of the ROM tail rather than in the
/// battle-animation bank, which the original game left almost full; its calls
/// into that bank stay within a Thumb branch's 4 MB reach.

#include "battle_anim_internal.h"
#include "parts/perfecti_frames.h"

extern const u8 gPerfectiCompressedFrames[];

#define PERFECTI_FRAME_WIDTH 32
#define PERFECTI_FRAME_HEIGHT 32
/// The canvas is 128 texels across; a beam is this many frames side by side.
#define PERFECTI_BEAM_TILES (128 / PERFECTI_FRAME_WIDTH)
#define PERFECTI_FRAME_BYTES (PERFECTI_FRAME_WIDTH * PERFECTI_FRAME_HEIGHT)
/// Frames the canvas keeps fading after the last picture, so trails clear.
#define PERFECTI_FADE_FRAMES 8
/// Frames a struck battler flashes white.
#define PERFECTI_FLASH_FRAMES 6
/// Frames the battlefield darkens over for her heaviest attacks, to 60
/// percent, as the summons and beams darken it; the canvas's close
/// (BattleAnim_EndCanvasLayer) brings it back.
#define PERFECTI_DIM_FRAMES 24

/// What every attack draws with: the canvas, its blitter and the middle of
/// the user's and first target's sprites, in canvas texels (half the
/// screen's x).
struct PerfectiStage {
  struct BattleAnimArgs *args;
  struct BattleAnimWork *work;
  void *canvas;
  DrawRectangle draw;
  s32 userX, userY;
  s32 targetX, targetY;
  s32 decoded; ///< the frame now in work->sheet, or -1
  s32 burstX, burstY; ///< where the big impact burst plays
  s32 burstTick;      ///< frames into the burst, or -1 for none
};

/// The big impact burst: eight steps, two frames each, of four quarters.
#define PERFECTI_BURST_STEPS 8

/// Opens the canvas, writes the 64-step violet-to-white ramp and builds an
/// additive blitter, so overlapping light and fading trails build to white.
/// With `dim`, the battlefield darkens behind the attack.
static void Perfecti_Start(struct BattleAnimArgs *args,
                           struct PerfectiStage *stage, s32 dim) {
  void **slots;
  void **cursor;
  struct ScreenPoint point;
  u16 *palette;
  s32 level, red, green, blue;

  ANIM_GET_SLOTS(slots, cursor, stage->work, stage->canvas);
  stage->args = args;
  stage->work->args = args;
  stage->decoded = -1;
  stage->burstTick = -1;
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
  Projection_Sprite(args->user, &point);
  stage->userX = point.x / 2;
  stage->userY = point.y;
  Projection_Sprite(args->targets[0], &point);
  stage->targetX = point.x / 2;
  stage->targetY = point.y;
  ANIM_LOAD_BLITTER(HEAP_SLOT_RAM_CODE, ANIM_CLIP_BOUNDS, COMPOSITE_ADDITIVE);
  stage->draw = (DrawRectangle)ANIM_SLOT(slots, HEAP_SLOT_RAM_CODE);
  ANIM_START_TRANSFER(stage->work, CANVAS_COPY_AND_FADE,
                      CANVAS_FADE_THREE_QUARTERS);
  if (dim) {
    stage->work->fadeFrames = PERFECTI_DIM_FRAMES;
    stage->work->fadeStep = 0;
  }
}

/// Unpacks frame `frame` into `out`: a control byte with bit 7 set repeats
/// the next byte, clear copies that many bytes; its low seven bits are the
/// count less one. Returns 0 unless the frame unpacks to exactly
/// PERFECTI_FRAME_BYTES.
static s32 Perfecti_Unpack(s32 frame, u8 *out) {
  const u8 *in = gPerfectiCompressedFrames + sPerfectiFrameOffsets[frame];
  const u8 *end = gPerfectiCompressedFrames + sPerfectiFrameOffsets[frame + 1];
  u32 written = 0;
  u32 count;
  u8 control;
  u8 value;

  while (in < end) {
    control = *in++;
    count = (control & 127) + 1;
    if (count > PERFECTI_FRAME_BYTES - written)
      return 0;
    if (control & 128) {
      value = *in++;
      while (count-- != 0)
        out[written++] = value;
    } else {
      while (count-- != 0)
        out[written++] = *in++;
    }
  }
  return written == PERFECTI_FRAME_BYTES;
}

/// Draws frame `frame` centred on (x, y). Only one frame is unpacked into
/// the sheet at a time, so each tick draws copies of a single frame.
static void Perfecti_Draw(struct PerfectiStage *stage, s32 frame, s32 x,
                          s32 y) {
  if (stage->decoded != frame) {
    if (!Perfecti_Unpack(frame, stage->work->sheet)) {
      stage->decoded = -1;
      return;
    }
    stage->decoded = frame;
  }
  stage->draw(stage->canvas, stage->work->sheet, x - PERFECTI_FRAME_WIDTH / 2,
              y - PERFECTI_FRAME_HEIGHT / 2, PERFECTI_FRAME_WIDTH,
              PERFECTI_FRAME_HEIGHT);
}

/// How hard a blow lands: knockback is an enum BattleKnockback variant, or
/// -1 for none; shake is camera-shake frames; flash, 0 or the brightness the
/// whole canvas jumps to after the blow, which the fade then takes down;
/// stop, the frames everything freezes as it lands (hit-stop); burst, 1 to
/// play the big impact burst on the target.
struct PerfectiImpact {
  s32 knockback;
  s32 shake;
  s32 flash;
  s32 stop;
  s32 burst;
};

/// Draws the big burst's current step, if one is playing: four 32x32
/// quarters around its centre.
static void Perfecti_DrawBurst(struct PerfectiStage *stage) {
  s32 step, quarter, first;

  if (stage->burstTick < 0)
    return;
  step = stage->burstTick / 2;
  if (step >= PERFECTI_BURST_STEPS) {
    stage->burstTick = -1;
    return;
  }
  first = PERFECTI_BURST_FIRST + step * 4;
  for (quarter = 0; quarter < 4; quarter++)
    Perfecti_Draw(stage, first + quarter,
                  stage->burstX + ((quarter & 1) ? PERFECTI_FRAME_WIDTH / 2
                                                 : -PERFECTI_FRAME_WIDTH / 2),
                  stage->burstY + ((quarter & 2) ? PERFECTI_FRAME_HEIGHT / 2
                                                 : -PERFECTI_FRAME_HEIGHT / 2));
}

/// Ends a frame: draws a playing burst and moves it on, then presents.
static void Perfecti_EndFrame(struct PerfectiStage *stage) {
  Perfecti_DrawBurst(stage);
  if (stage->burstTick >= 0)
    stage->burstTick++;
  ANIM_END_FRAME(stage->work);
}

/// Lands a blow on every target: white flash and damage pose, knockback and
/// camera shake.
static void Perfecti_Hit(struct PerfectiStage *stage, s32 knockback,
                         s32 shake) {
  s32 i;

  for (i = 0; i < stage->args->targetCount; i++) {
    BattleAnim_TintBattler(stage->args->targets[i], SPRITE_COLOR_WHITE,
                           POSE_DAMAGE, i, PERFECTI_FLASH_FRAMES);
    if (knockback >= 0)
      BattleMotion_ApplyKnockbackFar(stage->args->targets[i], knockback);
  }
  if (shake > stage->work->shakeFrames)
    stage->work->shakeFrames = shake;
}

/// Lands a blow as `impact` says. With a burst, its brightest step is drawn
/// over what this frame already holds; with hit-stop, the canvas then stops
/// fading and the frame is shown `stop` times, so everything freezes on the
/// impact; then the flash, and the burst plays on from its next step.
static void Perfecti_Land(struct PerfectiStage *stage,
                          struct PerfectiImpact *impact) {
  s32 frame;

  Perfecti_Hit(stage, impact->knockback, impact->shake);
  if (impact->burst) {
    stage->burstX = stage->targetX;
    stage->burstY = stage->targetY;
    stage->burstTick = 0;
    Perfecti_DrawBurst(stage);
  }
  if (impact->stop > 0) {
    ANIM_SET_TRANSFER(stage->work, CANVAS_COPY, 0);
    for (frame = 0; frame < impact->stop; frame++)
      ANIM_END_FRAME(stage->work);
    ANIM_SET_TRANSFER(stage->work, CANVAS_COPY_AND_FADE,
                      CANVAS_FADE_THREE_QUARTERS);
  }
  if (impact->flash != 0)
    Iwram_FillWords(stage->canvas, CANVAS_BYTES,
                    CANVAS_FILL_WORD(impact->flash));
  if (impact->burst)
    stage->burstTick = 2;
}

/// Lets the trails and any burst fade, then closes the canvas.
static void Perfecti_Finish(struct PerfectiStage *stage) {
  s32 tick;

  for (tick = 0; tick < PERFECTI_FADE_FRAMES ||
                 (stage->burstTick >= 0 && tick < 2 * PERFECTI_BURST_STEPS);
       tick++)
    Perfecti_EndFrame(stage);
  ANIM_FINISH_CANVAS_ONE_BLITTER();
}

/// Gathers light at the user for `ticks` frames (the charge frames of EX
/// Sternbrecher, four frames each, held on the brightest).
static void Perfecti_Charge(struct PerfectiStage *stage, s32 ticks) {
  s32 tick, frame;

  for (tick = 0; tick < ticks; tick++) {
    frame = (tick + 4 * 4 - ticks) / 4;
    if (frame < 0)
      frame = 0;
    Perfecti_Draw(stage, PERFECTI_STERNBRECHER_FIRST + frame, stage->userX,
                  stage->userY);
    Perfecti_EndFrame(stage);
  }
}

/// A volley: `copies` projectiles from the user to the first target, each
/// `stagger` frames after the last, over `travel` frames, bowing `bow`
/// texels apart. Each lands with a burst (the Explosion frames, two at a
/// time) and `each`; with `pulses`, the last then holds at the target and
/// strikes that many more times, five frames apart. `final` and `heavy`
/// (the damage sound) land with the last blow, which shows the damage.
struct PerfectiVolley {
  s32 first, count;
  s32 copies, stagger, travel, bow;
  s32 charge;  ///< frames of charge at the user first, 0 for none
  s32 launch;  ///< the sound as each projectile leaves, 0 for none
  s32 pulses;
  struct PerfectiImpact each, final;
  s32 heavy;
  s32 dim;     ///< darken the battlefield behind it
};

/// Frames a landing burst plays: the Explosion's twelve, two at a time.
#define PERFECTI_BURST_FRAMES 12

static void Perfecti_RunVolley(struct BattleAnimArgs *args,
                               struct PerfectiVolley *v) {
  struct PerfectiStage stage;
  s32 tick, copy, local, x, y, spread, last, end, burst;

  Perfecti_Start(args, &stage, v->dim);
  Perfecti_Charge(&stage, v->charge);
  last = (v->copies - 1) * v->stagger + v->travel;
  end = last + v->pulses * 5 + PERFECTI_BURST_FRAMES;
  for (tick = 0; tick <= end; tick++) {
    for (copy = 0; copy < v->copies; copy++) {
      local = tick - copy * v->stagger;
      if (local == 0 && v->launch != 0)
        Sound_PlaySongFar(v->launch);
      if (local < 0)
        continue;
      if (local <= v->travel) {
        spread = (copy * 2 - (v->copies - 1)) * v->bow;
        x = stage.userX + (stage.targetX - stage.userX) * local / v->travel;
        y = stage.userY + (stage.targetY - stage.userY) * local / v->travel +
            spread * 4 * local * (v->travel - local) / (v->travel * v->travel);
        Perfecti_Draw(&stage, v->first + tick % v->count, x, y);
      }
      if (local == v->travel) {
        if (copy == v->copies - 1 && v->pulses == 0) {
          ANIM_SHOW_DAMAGE(v->heavy);
          Perfecti_Land(&stage, &v->final);
        } else
          Perfecti_Land(&stage, &v->each);
      }
      // The landing burst.
      burst = local - v->travel;
      if (copy == v->copies - 1)
        burst -= v->pulses * 5;
      if (burst > 0 && burst <= PERFECTI_BURST_FRAMES)
        Perfecti_Draw(&stage, PERFECTI_EXPLOSION_FIRST + (burst - 1) / 2 * 2,
                      stage.targetX, stage.targetY);
    }
    // The last projectile holding at the target, striking again and again.
    if (v->pulses > 0 && tick > last && tick <= last + v->pulses * 5) {
      Perfecti_Draw(&stage, v->first + tick % v->count, stage.targetX,
                    stage.targetY);
      if ((tick - last) % 5 == 0) {
        if (tick == last + v->pulses * 5) {
          ANIM_SHOW_DAMAGE(v->heavy);
          Perfecti_Land(&stage, &v->final);
        } else
          Perfecti_Land(&stage, &v->each);
      }
    }
    Perfecti_EndFrame(&stage);
  }
  Perfecti_Finish(&stage);
}

/// Plays frames at the first target for `ticks` frames, `rate` frames each,
/// once through or looping, with `sound` as it starts. The blow lands at
/// `hit` with `impact`, and every `every` frames after it again with a light
/// shake (0 for none).
static void Perfecti_RunAtTarget(struct BattleAnimArgs *args, s32 first,
                                 s32 count, s32 ticks, s32 rate, s32 loop,
                                 s32 sound, s32 hit, s32 every,
                                 struct PerfectiImpact *impact, s32 dim) {
  struct PerfectiStage stage;
  s32 tick, frame;

  Perfecti_Start(args, &stage, dim);
  Sound_PlaySongFar(sound);
  for (tick = 0; tick < ticks; tick++) {
    frame = tick / rate;
    if (loop)
      frame %= count;
    else if (frame >= count)
      frame = count - 1;
    // Drawn twice, slightly apart: the additive blitter makes the middle
    // burn white.
    Perfecti_Draw(&stage, first + frame, stage.targetX, stage.targetY);
    Perfecti_Draw(&stage, first + frame, stage.targetX, stage.targetY - 1);
    if (tick == hit) {
      ANIM_SHOW_DAMAGE(SE_HEAVY_IMPACT);
      Perfecti_Land(&stage, impact);
    } else if (every != 0 && tick > hit && (tick - hit) % every == 0)
      Perfecti_Hit(&stage, -1, 3);
    Perfecti_EndFrame(&stage);
  }
  Perfecti_Finish(&stage);
}

/// A beam across the whole canvas at the target's height. `charge` frames
/// of gathering light at the user come first (four frames each, with
/// SE_POWER_UP), then `grow` frames of the beam swelling, `sustain` frames
/// of its loop of `loopCount` and `shrink` frames fading, two frames each.
/// It fires with `sound`; the blow lands `hit` frames into the loop, and the
/// beam keeps shaking the screen while it lasts.
static void Perfecti_RunBeam(struct BattleAnimArgs *args, s32 first,
                             s32 charge, s32 grow, s32 loopCount, s32 sustain,
                             s32 shrink, s32 sound, s32 hit,
                             struct PerfectiImpact *impact, s32 dim) {
  struct PerfectiStage stage;
  s32 tick, frame, beamTick, total, tile;

  Perfecti_Start(args, &stage, dim);
  if (charge != 0)
    Sound_PlaySongFar(SE_POWER_UP);
  total = charge * 4 + grow * 2 + sustain + shrink * 2;
  for (tick = 0; tick < total; tick++) {
    if (tick < charge * 4) {
      Perfecti_Draw(&stage, first + tick / 4, stage.userX, stage.userY);
      Perfecti_EndFrame(&stage);
      continue;
    }
    beamTick = tick - charge * 4;
    if (beamTick == 0)
      Sound_PlaySongFar(sound);
    if (beamTick < grow * 2)
      frame = charge + beamTick / 2;
    else if (beamTick < grow * 2 + sustain)
      frame = charge + grow + (beamTick - grow * 2) / 2 % loopCount;
    else
      frame = charge + grow + loopCount + (beamTick - grow * 2 - sustain) / 2;
    for (tile = 0; tile < PERFECTI_BEAM_TILES; tile++)
      Perfecti_Draw(&stage, first + frame,
                    PERFECTI_FRAME_WIDTH * tile + PERFECTI_FRAME_WIDTH / 2,
                    stage.targetY);
    if (beamTick == grow * 2 + hit) {
      ANIM_SHOW_DAMAGE(SE_HEAVY_IMPACT);
      Perfecti_Land(&stage, impact);
    } else if (beamTick > grow * 2 + hit && beamTick < grow * 2 + sustain &&
               stage.work->shakeFrames < 1)
      stage.work->shakeFrames = 1;
    Perfecti_EndFrame(&stage);
  }
  Perfecti_Finish(&stage);
}

/// Sets a struct PerfectiImpact.
#define PERFECTI_IMPACT(impact, k, s, f, st, b)                                \
  ((impact).knockback = (k), (impact).shake = (s), (impact).flash = (f),       \
   (impact).stop = (st), (impact).burst = (b))

/// Abilities: Gotterkanone. A short charge, then a violet bolt flies at the
/// target and bursts on it.
void BattleAnim_RunGotterkanone(struct BattleAnimArgs *args) {
  struct PerfectiVolley v;

  v.first = PERFECTI_GOTTERKANONE_FIRST;
  v.count = PERFECTI_GOTTERKANONE_COUNT;
  v.copies = 1, v.stagger = 0, v.travel = 24, v.bow = 0;
  v.charge = 10, v.launch = SE_WHOOSH, v.pulses = 0;
  PERFECTI_IMPACT(v.each, -1, 0, 0, 0, 0);
  PERFECTI_IMPACT(v.final, KNOCKBACK_HOP, 6, 24, 4, 1);
  v.heavy = SE_HEAVY_IMPACT;
  v.dim = 0;
  Perfecti_RunVolley(args, &v);
}

/// Abilities: EX Gotterkanone. A long charge, then a bigger orb flies at the
/// target, jolts it five times and bursts.
void BattleAnim_RunExGotterkanone(struct BattleAnimArgs *args) {
  struct PerfectiVolley v;

  Sound_PlaySongFar(SE_POWER_UP);
  v.first = PERFECTI_EX_GOTTERKANONE_FIRST;
  v.count = PERFECTI_EX_GOTTERKANONE_COUNT;
  v.copies = 1, v.stagger = 0, v.travel = 22, v.bow = 0;
  v.charge = 16, v.launch = SE_WHOOSH, v.pulses = 5;
  PERFECTI_IMPACT(v.each, KNOCKBACK_JOLT, 3, 10, 2, 0);
  PERFECTI_IMPACT(v.final, KNOCKBACK_LEAP, 12, 48, 8, 1);
  v.heavy = SE_HEAVY_IMPACT;
  v.dim = 1;
  Perfecti_RunVolley(args, &v);
}

/// Abilities: Ransnetz. Three homing missiles, launched a moment apart, bow
/// apart and close in, each bursting on the target.
void BattleAnim_RunRansnetz(struct BattleAnimArgs *args) {
  struct PerfectiVolley v;

  v.first = PERFECTI_RANSNETZ_FIRST;
  v.count = PERFECTI_RANSNETZ_COUNT;
  v.copies = 3, v.stagger = 6, v.travel = 22, v.bow = 10;
  v.charge = 0, v.launch = SE_WHOOSH, v.pulses = 0;
  PERFECTI_IMPACT(v.each, KNOCKBACK_JOLT, 3, 0, 1, 0);
  PERFECTI_IMPACT(v.final, KNOCKBACK_HOP, 6, 20, 3, 0);
  v.heavy = SE_IMPACT;
  v.dim = 0;
  Perfecti_RunVolley(args, &v);
}

/// Abilities: Explosion. A flash and a flattened shock ring burst on the
/// target, throwing it back.
void BattleAnim_RunPerfectiExplosion(struct BattleAnimArgs *args) {
  struct PerfectiImpact impact;

  PERFECTI_IMPACT(impact, KNOCKBACK_LAUNCH, 14, 56, 8, 1);
  Perfecti_RunAtTarget(args, PERFECTI_EXPLOSION_FIRST, PERFECTI_EXPLOSION_COUNT,
                       36, 3, 0, SE_BOOM, 4, 0, &impact, 1);
}

/// Abilities: P-Vortex. Three spiral arms wind around the target, wrenching
/// it in time with their turns.
void BattleAnim_RunPVortex(struct BattleAnimArgs *args) {
  struct PerfectiImpact impact;

  PERFECTI_IMPACT(impact, KNOCKBACK_JOLT, 6, 28, 4, 0);
  Perfecti_RunAtTarget(args, PERFECTI_P_VORTEX_FIRST, PERFECTI_P_VORTEX_COUNT,
                       48, 2, 1, SE_SWIRL, 20, 8, &impact, 0);
}

/// Abilities: Glepnir. A binding beam cracks across the screen at the
/// target, its chain knots running along it.
void BattleAnim_RunGlepnir(struct BattleAnimArgs *args) {
  struct PerfectiImpact impact;

  PERFECTI_IMPACT(impact, KNOCKBACK_SKID, 10, 40, 5, 1);
  Perfecti_RunBeam(args, PERFECTI_GLEPNIR_FIRST, 0, 3, 6, 30, 3, SE_THUNDER,
                   4, &impact, 0);
}

/// Abilities: EX Sternbrecher. Light gathers at the user, then a thick laser
/// tears across the screen at the target and hurls it back.
void BattleAnim_RunSternbrecher(struct BattleAnimArgs *args) {
  struct PerfectiImpact impact;

  PERFECTI_IMPACT(impact, KNOCKBACK_HURL, 20, 63, 10, 1);
  Perfecti_RunBeam(args, PERFECTI_STERNBRECHER_FIRST, 4, 0, 8, 40, 0,
                   SE_THUNDER_LOUD, 2, &impact, 1);
}

/// Abilities: P-Storm. Bolts rain down around the target, three a frame,
/// shaking the ground as they strike; the last wave throws it back. The
/// bolts' places come from a private sequence, so the battle's random
/// numbers are left alone.
void BattleAnim_RunPStorm(struct BattleAnimArgs *args) {
  struct PerfectiStage stage;
  struct PerfectiImpact impact;
  s32 tick, bolt, x, y;
  u32 seed = 0x2545f491;

  Perfecti_Start(args, &stage, 1);
  for (tick = 0; tick < 48; tick++) {
    for (bolt = 0; bolt < 3; bolt++) {
      seed = seed * 1103515245 + 12345;
      x = stage.targetX + (s32)((seed >> 16) % 64) - 32;
      seed = seed * 1103515245 + 12345;
      // Each bolt's flare lands near the target's feet.
      y = stage.targetY + 8 + (s32)((seed >> 16) % 8) - 4;
      Perfecti_Draw(&stage,
                    PERFECTI_P_STORM_FIRST + tick / 2 % PERFECTI_P_STORM_COUNT,
                    x, y);
    }
    if (tick % 12 == 0)
      Sound_PlaySongFar(SE_THUNDER);
    if (tick == 36) {
      ANIM_SHOW_DAMAGE(SE_HEAVY_IMPACT);
      PERFECTI_IMPACT(impact, KNOCKBACK_LAUNCH, 14, 56, 8, 1);
      Perfecti_Land(&stage, &impact);
    } else if (tick % 6 == 0 && tick != 0)
      Perfecti_Hit(&stage, KNOCKBACK_JOLT, 4);
    Perfecti_EndFrame(&stage);
  }
  Perfecti_Finish(&stage);
}
