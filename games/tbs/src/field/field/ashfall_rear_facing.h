#ifndef ASHFALL_REAR_FACING_H
#define ASHFALL_REAR_FACING_H

/* Only approved pose pairs are directional. Unsupported poses retain the
 * legacy camera-flip behavior, including blank frames. Cache tags occupy
 * the upper bits of the animation id. */
static u32 AshfallRearFacing(u32 animationId, s32 frame, u32 nativeFacing,
                            u32 fallback) {
  if ((nativeFacing & 1) == 0)
    return fallback;
  switch (animationId & 0xfff) {
  case 477: /* Ash Jenna */
  case 487: /* Kegare */
    return frame == 4 ? nativeFacing : fallback;
  case 484: /* Heart */
    return (frame == 0 || frame == 10) ? nativeFacing : fallback;
  case 491: /* Vengeful Wraith */
    return frame == 6 ? nativeFacing : fallback;
  case 492: /* Menardi Atropos */
    return frame == 10 ? nativeFacing : fallback;
  default:
    return fallback;
  }
}

/* Align the rear slash's feet with the original pose without shortening
 * the weapon. Apply only to the projected image, before native mirroring. */
static s32 AshfallRearOffsetX(u32 animationId, s32 frame) {
  if (frame == 5) {
    if ((animationId & 0xfff) == 477)
      return 18;
    if ((animationId & 0xfff) == 487)
      return 8;
  }
  return 0;
}
#endif
