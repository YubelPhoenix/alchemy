/// @file
/// Regenerate, finished (Ashfall): an ally wrapped in healing waters recovers
/// HP quietly at the end of every round, as Regen does in Final Fantasy IX.
///
/// The original game kept Regenerate unfinished and out of reach: casting it
/// set Unit.regenerate, which BattleUnit_TickRegenerate counts down over the
/// rounds, but nothing ever healed, and the move did its power as damage to
/// the ally it was cast on. Ashfall gives it to Mia (sSignatureMoves,
/// levels.c), takes its power away (abilities.c), names its messages
/// (MsgRefrain, MsgRefrainEnd, its description), shows it as a status icon
/// (ICON_REGENERATE, objects.c) and heals here.
///
/// As in Final Fantasy IX, the healing goes on in the background: no message
/// stops the battle and no sound plays (a sound every round soon grates), only
/// a blue shimmer on the unit and its HP rising. It comes at each round's end, whether or not the unit
/// acted, as Final Fantasy IX's Regen ticks on the battle's clock. There each
/// tick heals 1/16 of the maximum HP, and the Spirit stat makes the ticks
/// come more often; here the unit's Luck adds to the amount instead.
///
/// This object sits in the ROM tail beside party_join.c, because the battle
/// bank is full: Battle_ProcessRoundEnd only gains the call.

#include "battle_internal.h"

/// The heal, in 320ths of the maximum HP: REGEN_BASE (1/16) plus one for each
/// point of Luck up to REGEN_LUCK_CAP. Luck 5 heals about 8%, Luck 10 about
/// 9%, Luck 20 an eighth, and Luck 40 or more about 19%.
#define REGEN_BASE 20
#define REGEN_LUCK_CAP 40
#define REGEN_SCALE 320

/// The shimmer: this many flashes of blue, each this many frames on and off.
#define REGEN_SHIMMERS 2
#define REGEN_SHIMMER_FRAMES 4

/// At the end of a round, while Regenerate lasts and unitId stands short of
/// its maximum HP: restores its share of the maximum HP (at least 1), with
/// the recovery sound and a blue shimmer, and redraws its HP. Called by
/// Battle_ProcessRoundEnd for each unit, before Regenerate's turns are
/// counted down.
void Regenerate_RunRoundEnd(s32 unitId) {
  struct Unit *unit = Unit_GetFar(unitId);
  struct Actor *actor;
  s32 luck;
  s32 heal;
  s32 flash;

  if (unit->regenerate == 0 || unit->hp <= 0 || unit->hp >= unit->hpMax)
    return;
  luck = unit->luck;
  if (luck > REGEN_LUCK_CAP)
    luck = REGEN_LUCK_CAP;
  heal = unit->hpMax * (REGEN_BASE + luck) / REGEN_SCALE;
  if (heal < 1)
    heal = 1;
  if (heal > unit->hpMax - unit->hp)
    heal = unit->hpMax - unit->hp;

  Unit_AddHpFar(unitId, heal);
  actor = BattleObject_Get(unitId)->actor;
  if (actor != NULL) {
    for (flash = 0; flash < REGEN_SHIMMERS; flash++) {
      BattleObject_SetColorMode(actor, SPRITE_COLOR_BLUE_TINT);
      WaitFrames(REGEN_SHIMMER_FRAMES);
      BattleObject_SetColorMode(actor, BattleObject_GetPalette(unitId));
      WaitFrames(REGEN_SHIMMER_FRAMES);
    }
  }
  BattlePlayback_Reset();
  BattlePlayback_Push(PLAYBACK_REFRESH_UNIT, unitId);
  BattlePlayback_RunAll();
  BattlePlayback_Reset();
}
