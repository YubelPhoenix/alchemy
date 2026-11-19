/// @file
/// Ashfall: the heroes' finishers, after the Tales series' mystic artes, and
/// the special handling of Falling Wind. Isaac's Sol Ascension (after
/// Zankuu Tenshouken), Garet's Last Ember (after Mary's "ZAN!"), Ivan's
/// Foresight (after Philia's Rebirth Crusader) and Mia's Last Tide (after
/// Garr's Sekkazan: she gives everything, the others rise, and she falls).
///
/// Everything here runs from the spare ROM area (rom_tail_02); the battle
/// bank only calls in:
/// - BattleTurn_Build's cast line (MysticArte_CastMessage) and its targets
///   (MysticArte_AdjustPlan),
/// - BattleAbility_ApplyToTarget's power (MysticArte_Power),
/// - the round loop, after each action (MysticArte_RunAfterAction, through
///   PartyJoin_RunAfterAction).

#include "battle_internal.h"

/// The line shown as `abilityId` is used, in place of "<unit> casts ...!".
s32 MysticArte_CastMessage(s32 abilityId) {
  switch (abilityId) {
  case ABILITY_FALLING_WIND:
    return MsgFallingWindRemembered;
  case ABILITY_FALLING_WIND_REVIVE:
    return MsgFallingWindSettles;
  case ABILITY_SOL_ASCENSION:
    return MsgSolAscensionCry;
  case ABILITY_LAST_EMBER:
    return MsgLastEmberCry;
  case ABILITY_FORESIGHT:
    return MsgForesightCry;
  case ABILITY_LAST_TIDE:
    return MsgLastTideCry;
  case ABILITY_LAST_TIDE_HEAL:
    return MsgLastTideHeal;
  case ABILITY_LAST_TIDE_REVIVE:
    return MsgLastTideRevive;
  case ABILITY_LAST_TIDE_COLLAPSE:
    return MsgLastTideCollapse;
  }
  return MsgActorCasts;
}

/// Keeps the plan's targets for which `keep` holds, each sure to be hit when
/// `sure` is set.
static void MysticArte_FilterTargets(struct BattleTurn *plan, s32 fallen,
                                     s32 sure) {
  s32 from, to = 0;

  for (from = 0; from < plan->targetCount; from++) {
    s32 id = plan->targetIds[from];
    s32 down = Unit_GetFar(id)->hp == 0;

    if (down != fallen || id == plan->unitId)
      continue;
    plan->targetIds[to] = plan->targetIds[from];
    plan->targetOffset[to] = plan->targetOffset[from];
    plan->targetMultiplier[to] = plan->targetMultiplier[from];
    plan->targetCritical[to] = plan->targetCritical[from];
    if (sure)
      plan->targetHit[to] = 1;
    else
      plan->targetHit[to] = plan->targetHit[from];
    to++;
  }
  plan->targetCount = to;
}

/// Trims the targets of the follow-ups: Falling Wind's revive and Last
/// Tide's raise only the fallen, each certain to rise (no 60% roll by
/// distance, no "no effect" line for the living); Last Tide's heal reaches
/// only the living. None of them touches the caster. Called by
/// BattleTurn_Build for every Psynergy.
void MysticArte_AdjustPlan(struct BattleTurn *plan, s32 abilityId) {
  switch (abilityId) {
  case ABILITY_FALLING_WIND_REVIVE:
  case ABILITY_LAST_TIDE_REVIVE:
    MysticArte_FilterTargets(plan, 1, 1);
    break;
  case ABILITY_LAST_TIDE_HEAL:
    MysticArte_FilterTargets(plan, 0, 0);
    break;
  }
}

/// The power of `abilityId` as `actor` uses it. Last Ember grows as Garet's
/// HP falls: its power, plus as much again times the share of HP he has
/// lost (twice as strong at the brink).
s32 MysticArte_Power(s32 abilityId, struct Unit *actor, s32 power) {
  if (abilityId == ABILITY_LAST_EMBER && actor->hpMax != 0)
    power += power * (actor->hpMax - actor->hp) / actor->hpMax;
  return power;
}

/// Whether Last Tide's collapse is being applied: the blow takes exactly the
/// HP Mia has left (PartyJoin_ClampDamage).
s32 MysticArte_IsCollapse(void) {
  return gBattleWork->turn.abilityId == ABILITY_LAST_TIDE_COLLAPSE;
}

/// Whether any party member but `unitId` is living (`fallen` 0) or down
/// (`fallen` 1).
static s32 MysticArte_AnyAlly(s32 unitId, s32 fallen) {
  struct BattleWork *battle = gBattleWork;
  s32 place;

  for (place = 0; battle->partyUnits[place] != BATTLE_UNIT_LIST_END; place++) {
    s32 id = battle->partyUnits[place];

    if (id != unitId && (Unit_GetFar(id)->hp == 0) == fallen)
      return 1;
  }
  return 0;
}

/// Plays `abilityId` at once as `unitId`'s follow-up.
static void MysticArte_Follow(s32 unitId, s32 abilityId) {
  struct BattleAction request;

  Iwram_ClearWords(&request, sizeof(request));
  request.unitId = unitId;
  request.command = COMMAND_PSYNERGY;
  request.parameter = abilityId;
  request.target = 0;
  request.range = Ability_Get(abilityId)->range;
  BattleStaging_DispatchAction(&request, 10);
}

/// After Last Tide's wave, while foes remain: her light heals the living,
/// raises the fallen, and she falls. If the wave ends the battle, she is
/// spared. Called after every action, by PartyJoin_RunAfterAction.
void MysticArte_RunAfterAction(void) {
  struct BattleTurn *turn = &gBattleWork->turn;
  s32 mia;

  if (turn->command != COMMAND_PSYNERGY ||
      turn->abilityId != ABILITY_LAST_TIDE ||
      turn->failure != TURN_FAILURE_NONE)
    return;
  mia = turn->unitId;
  if (Unit_GetFar(mia)->hp == 0 ||
      BattleUnit_ListLiving(BATTLE_SIDE_MASK_ENEMIES, 0) == 0)
    return;
  if (MysticArte_AnyAlly(mia, 0))
    MysticArte_Follow(mia, ABILITY_LAST_TIDE_HEAL);
  if (MysticArte_AnyAlly(mia, 1))
    MysticArte_Follow(mia, ABILITY_LAST_TIDE_REVIVE);
  MysticArte_Follow(mia, ABILITY_LAST_TIDE_COLLAPSE);
}
