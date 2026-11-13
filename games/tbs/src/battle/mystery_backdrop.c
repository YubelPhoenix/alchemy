/// @file
/// The Mystery Leader's backdrop (Ashfall): its crimson beacons pulse, its
/// stars twinkle and, once she is below half HP, the void and deck turn
/// toward crimson, by rewriting palette entries the picture reserves for them
/// (tools/dark_story/build_mystery_backdrop.py). This object sits at the start
/// of the ROM tail, beside battle_anim/perfecti.c, so the battle bank only
/// gains the two calls in BattleBackground_Load and BattleBackground_Free.

#include "battle_internal.h"
#include "unit/battle_anim/battle_anim.h"

/// The backdrop's own colours, as built from mystery_citadel.png: the first
/// entries of its resource (battle_bg.s), before any rage.
extern const u16 Battle_MysteryBackdrop[];

/// Each beacon's core, then its three halo rings, outermost last.
#define MYSTERY_BEACON_FIRST 112
#define MYSTERY_BEACON_ENTRIES 4
/// Eight groups of one-pixel stars, each twinkling on its own beat.
#define MYSTERY_STAR_FIRST 116
#define MYSTERY_STAR_GROUPS 8
/// Frames for one beacon pulse, dim to bright and back (1.6 seconds), and
/// once she is below half HP (0.8 seconds).
#define MYSTERY_BEACON_PERIOD 96
#define MYSTERY_BEACON_PERIOD_ENRAGED 48
/// Frames from one heartbeat to the next (about 1.1 seconds); each beat is
/// two flares, a lub and a dub, of MYSTERY_FLARE_FRAMES, the dub starting
/// MYSTERY_DUB_FRAMES after the lub.
#define MYSTERY_HEARTBEAT_PERIOD 64
#define MYSTERY_FLARE_FRAMES 5
#define MYSTERY_DUB_FRAMES 12
/// The entries the picture keeps, which her rage tints toward crimson.
#define MYSTERY_ART_ENTRIES 112
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

/// How far toward crimson her rage turns the void and deck, 0 to 256: none
/// while she has more than half her HP or has yet to act below it (the
/// flash of BossAI_MysteryAwaken sets MYSTERY_ENRAGED), then 70 percent at once, so the
/// change is plain the moment she speaks, rising to full as her HP runs out.
static s32 Mystery_Rage(struct BattleWork *battle, s32 *mysteryId) {
  s32 index;
  s32 unitId;
  struct Unit *unit;
  s32 half;

  *mysteryId = -1;
  for (index = 0; battle->enemyIds[index] != BATTLE_UNIT_LIST_END; index++) {
    unitId = battle->enemyIds[index];
    if (unitId == BATTLE_UNIT_REMOVED)
      continue;
    unit = Unit_GetFar(unitId);
    if (unit->id != ENEMY_ID_FIRST + ENEMY_ROW_MYSTERY_LEADER)
      continue;
    if (unit->hp == 0)
      return 0;
    *mysteryId = unitId;
    half = unit->hpMax / 2;
    if (half <= 0 || unit->hp > half ||
        (unit->aiActionIndex & MYSTERY_ENRAGED) == 0)
      return 0;
    return 180 + 76 * (half - unit->hp) / half;
  }
  return 0;
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
  s32 scale, pulse, level, k, rage, zoomed, mysteryId, beat;
  const u16 *source;
  u16 colour;
  s32 red, green, blue, high, low;

  if (battle == NULL || view == NULL)
    return;
  zoomed = view->mode == BATTLE_BACKGROUND_ZOOMED;
  scale = battle->brightness;
  if (scale > Q16_ONE)
    scale = Q16_ONE;

  // Her rage: violet turns to crimson. Red rises to the larger of red and
  // blue (and a little past it), blue falls to a third of the smaller and
  // green to a third, so violet becomes deep red, the deck's red seams stay
  // red and its greys turn a dark, warm red. Worked out every frame from the
  // backdrop's own colours in ROM and kept in battle->palette, the colours
  // the battle repaints the background from, so the battlefield's darkening
  // under an attack and its return keep the crimson; written to the screen,
  // scaled by the battle's brightness, only while the background is zoomed,
  // as battle animations take the palette over otherwise.
  rage = Mystery_Rage(battle, &mysteryId);

  // Her heartbeat: in rage she flares violet (the blue raised to full,
  // SPRITE_COLOR_BLUE_TINT) twice a beat, a lub and a dub, then rests, and
  // takes her own colours back between (BattleAnim_TintBattler with palette
  // 0). Only the changes are written, so her sprite is redrawn four times a
  // beat. No flare starts while an attack plays (the background is not
  // zoomed then), so the heartbeat never doubles her afterimage flares
  // (battle_anim/perfecti.c); one already under way still ends on time.
  if (rage != 0 && mysteryId >= 0) {
    beat = frame % MYSTERY_HEARTBEAT_PERIOD;
    if (zoomed && (beat == 0 || beat == MYSTERY_DUB_FRAMES))
      BattleAnim_TintBattler(mysteryId, SPRITE_COLOR_BLUE_TINT, -1, -1, 0);
    else if (beat == MYSTERY_FLARE_FRAMES ||
             beat == MYSTERY_DUB_FRAMES + MYSTERY_FLARE_FRAMES)
      BattleAnim_TintBattler(mysteryId, 0, -1, -1, 0);
  }
  source = Battle_MysteryBackdrop;
  for (k = 0; k < MYSTERY_ART_ENTRIES; k++) {
    colour = source[k];
    if (rage != 0) {
      red = colour & 31;
      green = (colour >> 5) & 31;
      blue = (colour >> 10) & 31;
      high = red > blue ? red : blue;
      low = red < blue ? red : blue;
      high += high / 4;
      if (high > 31)
        high = 31;
      red += (high - red) * rage >> 8;
      blue -= (blue - low / 3) * rage >> 8;
      green -= green * 2 / 3 * rage >> 8;
      colour = (blue << 10) | (green << 5) | red;
    }
    battle->palette[k] = colour;
    if (zoomed && rage != 0)
      BATTLE_BG_PALETTE[k] =
          ((((colour >> 10) & 31) * scale >> 16) << 10) |
          ((((colour >> 5) & 31) * scale >> 16) << 5) |
          ((colour & 31) * scale >> 16);
  }
  if (!zoomed)
    return;

  // The core glows from a dim ember to bright crimson; each halo ring takes
  // half the light of the one inside it, over the void's violet. Enraged,
  // the beacons pulse twice as fast.
  pulse = Mystery_Triangle(frame, rage != 0 ? MYSTERY_BEACON_PERIOD_ENRAGED
                                            : MYSTERY_BEACON_PERIOD);
  BATTLE_BG_PALETTE[MYSTERY_BEACON_FIRST] =
      Mystery_MixColor(14, 2, 2, 31, 10, 8, pulse, scale);
  for (k = 1; k < MYSTERY_BEACON_ENTRIES; k++) {
    level = (64 + pulse * 3 / 4) >> (k - 1);
    // The rings start from the sky's own colour: violet, or crimson in rage.
    BATTLE_BG_PALETTE[MYSTERY_BEACON_FIRST + k] =
        rage != 0 ? Mystery_MixColor(9, 1, 2, 31, 8, 6, level * 3 / 4, scale)
                  : Mystery_MixColor(5, 3, 8, 31, 6, 5, level * 3 / 4, scale);
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

/// Her idle afterimages, kept in BattleWork.mysteryGhosts: the copies of her
/// sprite queued this frame, and REG_BLDCNT as it was before the first.
struct MysteryGhosts {
  struct AnimationSpritePart parts[4];
  u16 savedBlend;
  u16 blendSaved; ///< nonzero while savedBlend holds REG_BLDCNT
};
STATIC_ASSERT(sizeof(struct MysteryGhosts) <= 0x34);

/// Frames each pair of afterimages lasts, sliding back into her.
#define MYSTERY_GHOST_LIFE 24
/// How far out, in screen pixels, the lub's pair and the dub's pair start.
#define MYSTERY_GHOST_NEAR 10
#define MYSTERY_GHOST_FAR 18
/// Their opacity at the lub, in sixteenths; it falls to a third by the time
/// the dub's pair has gone back into her.
#define MYSTERY_GHOST_ALPHA 8
/// Under every battler (whose slots start at 1) and over the shadows (0):
/// the OAM list is built from slot 255 down, so a lower slot draws beneath.
#define MYSTERY_GHOST_DEPTH 1

/// Puts REG_BLDCNT back if the afterimages changed it.
static void Mystery_RestoreGhostBlend(struct MysteryGhosts *ghosts) {
  if (ghosts->blendSaved) {
    REG_BLDCNT = ghosts->savedBlend;
    ghosts->blendSaved = 0;
  }
}

/// In her rage, while she stands idle (the background zoomed, no unit
/// highlighted for a turn or a target), see-through copies of her sprite
/// split off left and right on each heartbeat flash, a near pair on the lub
/// and a far pair on the dub, and slide back into her as they fade. Each
/// copy is her own sprite's OAM entry again, moved sideways and made
/// semi-transparent, so it takes her pose and her colours (the flare's too)
/// and needs no VRAM. Semi-transparent sprites blend over the layers
/// REG_BLDCNT names second, at REG_BLDALPHA; both are set while copies show,
/// and REG_BLDCNT put back after. Runs in the main-loop pass after the
/// sprites are projected, so her entry and its affine matrix are this
/// frame's; added and removed with Mystery_StepBackdropGlow.
void Mystery_StepIdleGhosts(void) {
  struct BattleWork *battle = gBattleWork;
  struct BattleBackgroundWork *view =
      HEAP_SLOT_BLOCK(HEAP_SLOT_BATTLE_BACKGROUND);
  struct ActorSystemWork *actors = HEAP_SLOT_BLOCK(HEAP_SLOT_ACTOR_SYSTEM);
  struct MysteryGhosts *ghosts;
  struct BattleObject *object;
  struct Sprite *record;
  struct AnimationSpritePart *copy;
  s32 mysteryId, beat, age, pair, side, offset, alpha, count, x;

  if (battle == NULL || view == NULL)
    return;
  ghosts = (struct MysteryGhosts *)battle->mysteryGhosts;
  beat = gVBlankCount % MYSTERY_HEARTBEAT_PERIOD;
  if (view->mode != BATTLE_BACKGROUND_ZOOMED ||
      battle->highlightMode != HIGHLIGHT_OFF ||
      (actors != NULL && actors->suspended) ||
      Mystery_Rage(battle, &mysteryId) == 0 || mysteryId < 0 ||
      beat >= MYSTERY_DUB_FRAMES + MYSTERY_GHOST_LIFE) {
    Mystery_RestoreGhostBlend(ghosts);
    return;
  }
  object = BattleObject_Get(mysteryId);
  if (object == NULL || object->actor == NULL || object->fading) {
    Mystery_RestoreGhostBlend(ghosts);
    return;
  }
  record = GetMotionRecord(object->actor, 0);
  if (record == NULL || record->image.y >= DISPLAY_HEIGHT) {
    Mystery_RestoreGhostBlend(ghosts);
    return;
  }

  count = 0;
  for (pair = 0; pair < 2; pair++) {
    age = beat - (pair == 0 ? 0 : MYSTERY_DUB_FRAMES);
    if (age < 0 || age >= MYSTERY_GHOST_LIFE)
      continue;
    offset = (pair == 0 ? MYSTERY_GHOST_NEAR : MYSTERY_GHOST_FAR) *
             (MYSTERY_GHOST_LIFE - age) / MYSTERY_GHOST_LIFE;
    if (offset == 0)
      continue;
    for (side = -1; side <= 1; side += 2) {
      copy = &ghosts->parts[count++];
      *copy = record->image;
      x = record->image.x + side * offset;
      copy->x = x;
      copy->objectMode = OBJ_MODE_SEMI_TRANSPARENT;
      Oam_AddSpriteAtDepth(copy, MYSTERY_GHOST_DEPTH);
    }
  }
  if (count == 0) {
    Mystery_RestoreGhostBlend(ghosts);
    return;
  }
  if (!ghosts->blendSaved) {
    // Not while the screen is being lightened (BossAI_MysteryAwaken's
    // flash), whose REG_BLDCNT would be saved and put back after it.
    if ((REG_BLDCNT & BLDCNT_EFFECT_DARKEN) >= BLDCNT_EFFECT_LIGHTEN)
      return;
    ghosts->savedBlend = REG_BLDCNT;
    ghosts->blendSaved = 1;
  }
  alpha = MYSTERY_GHOST_ALPHA -
          MYSTERY_GHOST_ALPHA * 2 / 3 * beat /
              (MYSTERY_DUB_FRAMES + MYSTERY_GHOST_LIFE);
  REG_BLDCNT = ghosts->savedBlend | BLDCNT_TGT2_ALL;
  REG_BLDALPHA = BLEND_ALPHA(alpha, 16 - alpha);
}
