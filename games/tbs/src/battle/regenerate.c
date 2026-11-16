/// @file
/// Regenerate, finished (Ashfall): an ally wrapped in healing waters recovers
/// a little HP after each of their turns, as regen does in Final Fantasy.
///
/// The original game kept Regenerate unfinished and out of reach: casting it
/// set Unit.regenerate, which BattleUnit_TickRegenerate counts down over the
/// rounds, but nothing ever healed, and the move did its power as damage to
/// the ally it was cast on. Ashfall gives it to Mia (sSignatureMoves,
/// levels.c), takes its power away (abilities.c), names its messages
/// (MsgRefrain, MsgRefrainEnd, its description) and heals here.
///
/// This object sits in the ROM tail beside party_join.c, because the battle
/// bank is full: BattleUnit_ProcessTurnEnd only gains the call.

#include "battle_internal.h"

/// The share of the maximum HP the healing waters restore after each turn.
#define REGENERATE_PERCENT 10

/// After unitId's turn, while Regenerate lasts and the unit stands short of
/// its maximum HP: restores REGENERATE_PERCENT of the maximum (at least 1),
/// with the recovery sound and "<unit> recovers <amount> HP!", as Ply shows
/// its heal. Called by BattleUnit_ProcessTurnEnd after poison.
void Regenerate_RunTurnEnd(s32 unitId) {
  struct Unit *unit = Unit_GetFar(unitId);
  s32 heal;

  if (unit->regenerate == 0 || unit->hp <= 0 || unit->hp >= unit->hpMax)
    return;
  heal = unit->hpMax * REGENERATE_PERCENT / 100;
  if (heal < 1)
    heal = 1;
  if (heal > unit->hpMax - unit->hp)
    heal = unit->hpMax - unit->hp;
  BattlePlayback_Reset();
  BattlePlayback_Push(PLAYBACK_UNIT_NAME, unitId);
  BattlePlayback_Push(PLAYBACK_NUMBER, heal);
  PUSH_MESSAGE(MsgHpRecover);
  Unit_AddHpFar(unitId, heal);
  BattlePlayback_Push(PLAYBACK_REFRESH_UNIT, unitId);
  Sound_PlaySongFar(SE_RECOVERY);
  BattlePlayback_RunAll();
  BattlePlayback_Reset();
}
