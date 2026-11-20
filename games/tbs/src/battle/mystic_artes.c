/// @file
/// Ashfall: the heroes' finishers and the special handling of Falling Wind.
/// Each finisher follows one of Tales of Destiny's Blast Calibers step by
/// step, a step to a blow, each drawn with the nearest animation the game
/// has, and nothing the Blast Caliber does not do:
/// - Isaac's Sol Ascension (Stahn's Zankuu Tenshouken): two slashes of one
///   colour and the rising leap.
/// - Garet's Last Ember (Mary's "ZAN!"): the overhead axe smash, the
///   one-handed slash, the shoulder charge and the uppercut.
/// - Ivan's Foresight (Philia's Rebirth Crusader): a wall of lightning, a
///   bolt into the sky and the great bolt's return.
/// - Mia's Last Tide (Garr's Sekkazan): she gathers her power and strikes,
///   and while foes remain the fallen rise and she falls.
/// The opening blow has its cry and the last calls out the name; the blows
/// between are silent.
///
/// Everything here runs from the spare ROM area (rom_tail_02); the battle
/// bank only calls in:
/// - BattleTurn_Build's cast line (MysticArte_CastMessage) and its targets
///   (MysticArte_AdjustPlan),
/// - BattleAbility_ApplyToTarget's power (MysticArte_Power),
/// - the round loop, after each action (MysticArte_RunAfterAction, through
///   PartyJoin_RunAfterAction).

#include "battle_internal.h"

/// The line shown as `abilityId` is used, in place of "<unit> casts ...!";
/// MYSTIC_ARTE_SILENT for a blow in the middle of a finisher, which shows
/// none.
s32 MysticArte_CastMessage(s32 abilityId) {
  switch (abilityId) {
  case ABILITY_FALLING_WIND:
    return MsgFallingWindRemembered;
  case ABILITY_FALLING_WIND_REVIVE:
    return MsgFallingWindSettles;
  case ABILITY_SOL_ASCENSION:
    return MsgSolAscensionCry;
  case ABILITY_SOL_ASCENSION_RISE:
    return MsgSolAscensionName;
  case ABILITY_LAST_EMBER:
    return MsgLastEmberCry;
  case ABILITY_LAST_EMBER_UPPERCUT:
    return MsgLastEmberName;
  case ABILITY_FORESIGHT:
    return MsgForesightCry;
  case ABILITY_FORESIGHT_RETURN:
    return MsgForesightName;
  case ABILITY_LAST_TIDE:
    return MsgLastTideCry;
  case ABILITY_LAST_TIDE_STRIKE:
    return MsgLastTideName;
  case ABILITY_LAST_TIDE_REVIVE:
    return MsgLastTideRevive;
  case ABILITY_LAST_TIDE_COLLAPSE:
    return MsgLastTideCollapse;
  case ABILITY_SOL_ASCENSION_SLASH:
  case ABILITY_LAST_EMBER_SLASH:
  case ABILITY_LAST_EMBER_TACKLE:
  case ABILITY_FORESIGHT_SKY:
    return MYSTIC_ARTE_SILENT;
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

/// Trims the targets of the revives: Falling Wind's and Last Tide's raise
/// only the fallen, each certain to rise (no 60% roll by distance, no "no
/// effect" line for the living). Called by BattleTurn_Build for every
/// Psynergy.
void MysticArte_AdjustPlan(struct BattleTurn *plan, s32 abilityId) {
  switch (abilityId) {
  case ABILITY_FALLING_WIND_REVIVE:
  case ABILITY_LAST_TIDE_REVIVE:
    MysticArte_FilterTargets(plan, 1, 1);
    break;
  }
}

/// The power of `abilityId` as `actor` uses it. Last Ember's uppercut grows
/// as Garet's HP falls: its power, plus as much again times the share of HP
/// he has lost (twice as strong at the brink).
s32 MysticArte_Power(s32 abilityId, struct Unit *actor, s32 power) {
  if (abilityId == ABILITY_LAST_EMBER_UPPERCUT && actor->hpMax != 0)
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

/// The finishers' chains: the ability each hero learns, then the blows
/// that follow it, ended by 0.
enum { MYSTIC_ARTE_CHAIN_COUNT = 4, MYSTIC_ARTE_CHAIN_LENGTH = 4 };
static const s16 sMysticArte_Chains[MYSTIC_ARTE_CHAIN_COUNT]
                                   [MYSTIC_ARTE_CHAIN_LENGTH] = {
    {ABILITY_SOL_ASCENSION, ABILITY_SOL_ASCENSION_SLASH,
     ABILITY_SOL_ASCENSION_RISE},
    {ABILITY_LAST_EMBER, ABILITY_LAST_EMBER_SLASH, ABILITY_LAST_EMBER_TACKLE,
     ABILITY_LAST_EMBER_UPPERCUT},
    {ABILITY_FORESIGHT, ABILITY_FORESIGHT_SKY, ABILITY_FORESIGHT_RETURN},
    {ABILITY_LAST_TIDE, ABILITY_LAST_TIDE_STRIKE},
};

/// Plays `abilityId` at once as `unitId`'s follow-up, aimed at `target`.
static void MysticArte_Follow(s32 unitId, s32 abilityId, s32 target) {
  struct BattleAction request;

  Iwram_ClearWords(&request, sizeof(request));
  request.unitId = unitId;
  request.command = COMMAND_PSYNERGY;
  request.parameter = abilityId;
  request.target = target;
  request.range = Ability_Get(abilityId)->range;
  BattleStaging_DispatchAction(&request, 0);
}

/// The foe a chain's next blow aims at: the one it began on while it
/// stands, else the first foe standing; -1 when none stands.
static s32 MysticArte_NextFoe(s32 first) {
  u16 living[BATTLE_TARGET_CAPACITY + 1];

  if (first >= 0 && Unit_GetFar(first)->hp != 0)
    return first;
  if (BattleUnit_ListLiving(BATTLE_SIDE_MASK_ENEMIES, living) == 0)
    return -1;
  return living[0];
}

/// After a finisher's first blow, plays the rest of its chain, each blow
/// straight after the last, until the chain ends, its user falls or no foe
/// stands. Then, after Last Tide's strike while foes remain, Mia gives
/// everything: the fallen rise and she falls; if her strike ends the battle,
/// she is spared. Called after every action,
/// by PartyJoin_RunAfterAction.
void MysticArte_RunAfterAction(void) {
  struct BattleTurn *turn = &gBattleWork->turn;
  s32 chain, step, unitId, first, foe;

  if (turn->command != COMMAND_PSYNERGY ||
      turn->failure != TURN_FAILURE_NONE)
    return;
  for (chain = 0; chain < MYSTIC_ARTE_CHAIN_COUNT; chain++) {
    if (sMysticArte_Chains[chain][0] == turn->abilityId)
      break;
  }
  if (chain == MYSTIC_ARTE_CHAIN_COUNT)
    return;
  unitId = turn->unitId;
  first = turn->targetCount != 0 && turn->targetIds[0] > ALLY_MAX
              ? turn->targetIds[0]
              : -1;
  for (step = 1; step < MYSTIC_ARTE_CHAIN_LENGTH && sMysticArte_Chains[chain][step] != 0; step++) {
    foe = MysticArte_NextFoe(first);
    if (foe < 0 || Unit_GetFar(unitId)->hp == 0)
      return;
    MysticArte_Follow(unitId, sMysticArte_Chains[chain][step], foe);
  }
  if (sMysticArte_Chains[chain][0] != ABILITY_LAST_TIDE ||
      Unit_GetFar(unitId)->hp == 0 ||
      BattleUnit_ListLiving(BATTLE_SIDE_MASK_ENEMIES, 0) == 0)
    return;
  if (MysticArte_AnyAlly(unitId, 1))
    MysticArte_Follow(unitId, ABILITY_LAST_TIDE_REVIVE, unitId);
  MysticArte_Follow(unitId, ABILITY_LAST_TIDE_COLLAPSE, unitId);
}
