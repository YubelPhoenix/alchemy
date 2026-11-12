/* Gotterkanone: Heart's Mystery Leader, one-target violet blast.
 * RLE artwork and timing are built in to the ordinary Ashfall animation
 * dispatcher. Intended for in-game verification with Isaac's solo fight.
 */
#include "gotterkanone_offsets.h"
#include "gotterkanone_stream.h"

extern const u8 gGotterkanoneCompressedFrames[];

void BattleAnim_RunGotterkanone(struct BattleAnimArgs *args) {
  void **slots;
  void **cursor;
  struct BattleAnimWork *work;
  void *canvas;
  struct ScreenPoint source, destination;
  s32 tick;
  s32 x, y;
  s32 targetX, targetY;
  s32 startX, startY;
  s32 index;
  s32 level, red, green, blue;
  s32 paletteIndex;
  u16 *palette;
  u8 *decoded;
  DrawRectangle draw;

  ANIM_GET_SLOTS(slots, cursor, work, canvas);
  work->args = args;
  decoded = work->sheet;
  BattleAnim_StartCanvasLayer(BGCNT_PRIORITY(1));
  /* 64-step violet-to-white intensity ramp for the custom artwork. */
  palette = (u16 *)BG_PLTT;
  for (paletteIndex = 0; paletteIndex < 64; paletteIndex++) {
    level = paletteIndex;
    if (level <= 31) {
      red = level * 24 / 31;
      green = level * 3 / 31;
      blue = level * 25 / 31;
    } else {
      red = 24 + (level - 31) * 7 / 32;
      green = 3 + (level - 31) * 28 / 32;
      blue = 25 + (level - 31) * 6 / 32;
    }
    palette[paletteIndex] = RGB(red, green, blue);
  }
  Projection_Unit(args->user, &source);
  Projection_Unit(args->targets[0], &destination);
  startX = source.x / 2;
  startY = source.y;
  targetX = destination.x / 2;
  targetY = destination.y;
  ANIM_LOAD_BLITTER(HEAP_SLOT_RAM_CODE, ANIM_CLIP_BOUNDS, COMPOSITE_LIGHTEN);
  draw = (DrawRectangle)ANIM_SLOT(slots, HEAP_SLOT_RAM_CODE);
  ANIM_START_TRANSFER(work, CANVAS_COPY_AND_FADE, CANVAS_FADE_THREE_QUARTERS);

  for (tick = 0; tick < 36; ++tick) {
    index = tick % 12;
    if (gotterkanone_decode_frame(
            gGotterkanoneCompressedFrames + gotterkanone_frame_offsets[index],
            gotterkanone_frame_offsets[index + 1] - gotterkanone_frame_offsets[index],
            decoded, 3072) == 0) {
      x = startX + (targetX - startX) * tick / 35 - 32;
      y = startY + (targetY - startY) * tick / 35 - 24;
      draw(canvas, decoded, x, y, 64, 48);
    }
    if (tick == 30) {
      ANIM_SHOW_DAMAGE(SE_IMPACT);
      BattleAnim_TintBattler(args->targets[0], SPRITE_COLOR_WHITE,
                             POSE_DAMAGE, 0, 6);
    }
    ANIM_END_FRAME(work);
  }
  ANIM_FINISH_CANVAS_ONE_BLITTER();
}
