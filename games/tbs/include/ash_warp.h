#ifndef ASH_WARP_H
#define ASH_WARP_H

#include "songs.h"

// Ash Jenna's way of coming and going: a warp sound and a quick flicker of
// white and grey. Event scripts only (it waits frames). The scene sets her
// place and flags itself.

/// She flickers away. Leaves her hidden; the caller parks her.
static inline void AshWarp_Out(s32 actorId) {
  s32 beat;

  Event_PlaySong(SE_WARP);
  for (beat = 0; beat < 4; beat++) {
    Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_WHITE);
    Event_WaitFrames(3);
    Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_GREY);
    Event_WaitFrames(3);
  }
  Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_WHITE);
  Event_WaitFrames(4);
  Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_HIDDEN);
}

/// She flickers in at her place and settles grey.
static inline void AshWarp_In(s32 actorId) {
  s32 beat;

  Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_HIDDEN);
  Event_WaitFrames(8);
  Event_PlaySong(SE_WARP);
  Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_WHITE);
  Event_WaitFrames(4);
  for (beat = 0; beat < 3; beat++) {
    Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_GREY);
    Event_WaitFrames(3);
    Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_WHITE);
    Event_WaitFrames(3);
  }
  Actor_ConfigureSpriteColor(actorId, SPRITE_COLOR_GREY);
}

#endif
