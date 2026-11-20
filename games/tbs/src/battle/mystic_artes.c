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
/// between are silent. Isaac's and Garet's blows run up to the foe and strike,
/// as an attack does (STAGING_ATTACK). For each blow the hero is drawn in a
/// pose the author drew (the SPRITE_POSE_ sprites, the sword drawn in),
/// shown in place of their battle sprite and weapon until the finisher ends.
///
/// Everything here runs from the spare ROM area (rom_tail_02); the battle
/// bank only calls in:
/// - BattleTurn_Build's cast line (MysticArte_CastMessage) and its targets
///   (MysticArte_AdjustPlan),
/// - BattleAbility_ApplyToTarget's power (MysticArte_Power),
/// - the round loop, after each action (MysticArte_RunAfterAction, through
///   PartyJoin_RunAfterAction).

#include "battle_internal.h"

// While a finisher plays, its hero's own sprite and weapon, kept in the
// battle's spare bytes (zeroed with the rest of the battle's work) to be put
// back when it ends.
#define poseHero unusedAfterActions[0]   ///< the hero's unit id plus 1; 0 none
#define poseSprite unusedAfterActions[1] ///< two bytes: their sprite
#define poseWeapon unusedAfterActions[3] ///< two bytes: their weapon sprite

/// Each finisher blow's pose: the ability, the pose its hero is drawn in
/// while its line shows (0 for none) and while it strikes.
enum { POSE_ABILITY, POSE_FOR_LINE, POSE_FOR_BLOW, POSE_COLUMNS };
static const u16 sMysticArte_Poses[][POSE_COLUMNS] = {
    {ABILITY_SOL_ASCENSION, SPRITE_POSE_ISAAC_LOW_PROFILE,
     SPRITE_POSE_ISAAC_DASH},
    {ABILITY_SOL_ASCENSION_SLASH, 0, SPRITE_POSE_ISAAC_ATTACK_END},
    {ABILITY_SOL_ASCENSION_RISE, 0, SPRITE_POSE_ISAAC_SWORD_ATTACK},
    {ABILITY_LAST_EMBER, SPRITE_POSE_GARET_WINDUP, SPRITE_POSE_GARET_WINDUP},
    {ABILITY_LAST_EMBER_SLASH, 0, SPRITE_POSE_GARET_ATTACK_END},
    {ABILITY_LAST_EMBER_TACKLE, 0, SPRITE_POSE_GARET_DASH},
    {ABILITY_LAST_EMBER_UPPERCUT, 0, SPRITE_POSE_GARET_WINDUP},
    {ABILITY_FORESIGHT, SPRITE_POSE_IVAN_ATTACK_END,
     SPRITE_POSE_IVAN_ATTACK_END},
    {ABILITY_FORESIGHT_SKY, 0, SPRITE_POSE_IVAN_KARIS},
    {ABILITY_FORESIGHT_RETURN, 0, SPRITE_POSE_IVAN_KARIS},
    {ABILITY_LAST_TIDE, SPRITE_POSE_MIA_WINDUP, SPRITE_POSE_MIA_WINDUP},
    {ABILITY_LAST_TIDE_STRIKE, 0, SPRITE_POSE_MIA_YUGIZAN},
    {ABILITY_LAST_TIDE_REVIVE, 0, SPRITE_POSE_MIA_YUGIZAN},
    {ABILITY_LAST_TIDE_COLLAPSE, 0, SPRITE_POSE_MIA_FACEPLANT},
};
#define MYSTIC_ARTE_POSE_COUNT                                                 \
  (s32)(sizeof(sMysticArte_Poses) / sizeof(sMysticArte_Poses[0]))

/// Draws party member unitId as `sprite`, with no weapon, keeping their own
/// sprite and weapon the first time to put back (MysticArte_EndPose).
static void MysticArte_ShowPose(s32 unitId, s32 sprite) {
  struct BattleWork *battle = gBattleWork;
  struct BattleObject *battleObject;

  if (unitId < 0 || unitId > ALLY_MAX)
    return;
  battleObject = BattleObject_Get(unitId);
  if (battleObject == NULL || battleObject->actor == NULL)
    return;
  if (battle->poseHero == 0) {
    battle->poseHero = unitId + 1;
    (&battle->poseSprite)[0] = battleObject->resource;
    (&battle->poseSprite)[1] = battleObject->resource >> 8;
    (&battle->poseWeapon)[0] = battleObject->overlay;
    (&battle->poseWeapon)[1] = battleObject->overlay >> 8;
  }
  battleObject->resource = sprite;
  battleObject->overlay = 0;
  ReleaseBattleObjectRecords(unitId);
  BattleObject_Put();
}

/// Puts back the sprite and weapon of the hero a finisher drew in its poses.
static void MysticArte_EndPose(void) {
  struct BattleWork *battle = gBattleWork;
  struct BattleObject *battleObject;
  s32 unitId;

  if (battle->poseHero == 0)
    return;
  unitId = battle->poseHero - 1;
  battle->poseHero = 0;
  battleObject = BattleObject_Get(unitId);
  if (battleObject == NULL)
    return;
  battleObject->resource =
      (&battle->poseSprite)[0] | ((&battle->poseSprite)[1] << 8);
  battleObject->overlay =
      (&battle->poseWeapon)[0] | ((&battle->poseWeapon)[1] << 8);
  ReleaseBattleObjectRecords(unitId);
  BattleObject_Put();
}

/// Draws unitId in finisher blow abilityId's pose, `column` saying which:
/// POSE_FOR_LINE or POSE_FOR_BLOW. Nothing for any other ability.
static void MysticArte_Pose(s32 abilityId, s32 unitId, s32 column) {
  s32 i;

  for (i = 0; i < MYSTIC_ARTE_POSE_COUNT; i++) {
    if (sMysticArte_Poses[i][POSE_ABILITY] == abilityId) {
      if (sMysticArte_Poses[i][column] != 0)
        MysticArte_ShowPose(unitId, sMysticArte_Poses[i][column]);
      return;
    }
  }
}

/// The line shown as `abilityId` is used by unitId, in place of "<unit>
/// casts ...!"; MYSTIC_ARTE_SILENT for a blow in the middle of a finisher,
/// which shows none. A finisher's opening blow first draws its hero in the
/// pose for its cry.
s32 MysticArte_CastMessage(s32 abilityId, s32 unitId) {
  MysticArte_Pose(abilityId, unitId, POSE_FOR_LINE);
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
/// effect" line for the living). A finisher's blow draws its hero in the
/// blow's pose. Called by BattleTurn_Build for every Psynergy.
void MysticArte_AdjustPlan(struct BattleTurn *plan, s32 abilityId) {
  MysticArte_Pose(abilityId, plan->unitId, POSE_FOR_BLOW);
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
static const s16
    sMysticArte_Chains[MYSTIC_ARTE_CHAIN_COUNT][MYSTIC_ARTE_CHAIN_LENGTH] = {
        {ABILITY_SOL_ASCENSION, ABILITY_SOL_ASCENSION_SLASH,
         ABILITY_SOL_ASCENSION_RISE},
        {ABILITY_LAST_EMBER, ABILITY_LAST_EMBER_SLASH,
         ABILITY_LAST_EMBER_TACKLE, ABILITY_LAST_EMBER_UPPERCUT},
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
static void MysticArte_RunChain(void) {
  struct BattleTurn *turn = &gBattleWork->turn;
  s32 chain, step, unitId, first, foe;

  if (turn->command != COMMAND_PSYNERGY || turn->failure != TURN_FAILURE_NONE)
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
  for (step = 1;
       step < MYSTIC_ARTE_CHAIN_LENGTH && sMysticArte_Chains[chain][step] != 0;
       step++) {
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

/// After a finisher's first blow, plays the rest of it, then puts back its
/// hero's sprite. Called after every action, by PartyJoin_RunAfterAction.
void MysticArte_RunAfterAction(void) {
  MysticArte_RunChain();
  MysticArte_EndPose();
}
