/// @file
/// Tactical choices for the optional super bosses (Ashfall). Each boss has its
/// own switch, so one can be turned off without touching the others.
///
/// The rules every boss follows:
///  - A chooser only reads the battle. What a boss did is recorded by
///    BossAI_NoteTurn after its turn was really staged, so a move that was
///    refused, or a turn that failed, changes nothing.
///  - A boss's memory is bits 4..29 of its Unit.aiActionIndex; bits 0..3 are
///    the stock action cycle's and 30..31 Ash Jenna's rush (AI_RUSH,
///    AI_PUNISHED), which nothing here touches.
///  - The per-round bits are cleared by BossAI_BeginRound, once a round.
// Part of battle.c.

#include "../battle_internal.h"

/// Set a switch to 0 to give that boss back the stock AI.
#define BOSS_AI_KEGARE 1

/// Kegare's places in her action list (enemies.c).
enum KegareSlot {
  KEGARE_FREEZE_PRISM = 0,
  KEGARE_ICE_MISSILE = 1,
  KEGARE_FROTH_SPIRAL = 2,
  KEGARE_DELUGE = 3,
  KEGARE_HAIL_PRISM = 4,
  KEGARE_GLACIER = 5,
  KEGARE_ICE_BLESSING = 6,
  KEGARE_PLY_WELL = 7
};

/// Kegare's memory in Unit.aiActionIndex:
/// bits 15..13 the party place she last aimed at, plus one (0 none) |
/// 12..10 actions until she may heal again | 9..8 rounds in a row with a heavy
/// move | 7 a heavy move this round.
#define KEGARE_HEAVY_THIS_ROUND_BIT (1u << 7)
#define KEGARE_HEAVY_ROUNDS_SHIFT 8
#define KEGARE_HEAL_WAIT_SHIFT 10
#define KEGARE_LAST_AIM_SHIFT 13
/// After this many rounds in a row with a heavy move, one round has none.
#define KEGARE_HEAVY_ROUNDS_LIMIT 2
/// She may heal (Ply Well, her own pick or the stock cycle's) only below this
/// percent of her HP, and then not again for this many of her actions after a
/// heal that was really cast.
#define KEGARE_HEAL_BELOW_PERCENT 40
#define KEGARE_HEAL_WAIT 5
/// Out of 256: how often she keeps the stock choice instead of her own plan.
#define KEGARE_MISTAKE_CHANCE 51
/// Out of 256: how often she aims at the member who is most open.
#define KEGARE_AIM_CHANCE 102

/// Whether the ability id is one of the heavy moves in the row's action list.
static s32 BossAI_KegareIsHeavy(struct Unit *unit, s32 abilityId) {
  struct EnemyDefinition *enemy =
      (struct EnemyDefinition *)Enemy_GetDefinitionFar(unit->id);

  return abilityId == enemy->abilities[KEGARE_FREEZE_PRISM] ||
         abilityId == enemy->abilities[KEGARE_ICE_MISSILE] ||
         abilityId == enemy->abilities[KEGARE_FROTH_SPIRAL] ||
         abilityId == enemy->abilities[KEGARE_ICE_BLESSING];
}

/// Kegare's unit, or 0 when she is not in this battle.
static struct Unit *BossAI_FindKegare(void) {
  s32 index;
  s32 unitId;
  struct Unit *unit;

  for (index = 0; gBattleWork->enemyIds[index] != BATTLE_UNIT_LIST_END;
       index++) {
    unitId = gBattleWork->enemyIds[index];
    if (unitId == BATTLE_UNIT_REMOVED)
      continue;
    unit = Unit_GetFar(unitId);
    if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_KEGARE)
      return unit;
  }
  return 0;
}

/// A party member Kegare can exploit: HP under half, Defense lowered (the
/// member's own, by anyone), or unable to act. Nobody who is down counts.
static s32 BossAI_MemberIsOpen(struct Unit *member) {
  return member->hp != 0 &&
         (member->hp * 2 < member->hpMax || member->defenseStage < 0 ||
          member->sleep != 0 || member->stun != 0);
}

/// Starts a round for the bosses: their per-round memory is cleared, and the
/// number of rounds in a row with a heavy move is brought up to date.
/// Called once a round by BattleTurnOrder_Sort, before anyone acts.
void BossAI_BeginRound(void) {
#if BOSS_AI_KEGARE
  struct Unit *kegare = BossAI_FindKegare();
  u32 memory;
  u32 rounds;

  if (kegare != 0) {
    memory = kegare->aiActionIndex;
    rounds = (memory >> KEGARE_HEAVY_ROUNDS_SHIFT) & 3;
    if (memory & KEGARE_HEAVY_THIS_ROUND_BIT) {
      if (rounds < 3)
        rounds++;
    } else {
      rounds = 0;
    }
    memory &= ~(KEGARE_HEAVY_THIS_ROUND_BIT | (3u << KEGARE_HEAVY_ROUNDS_SHIFT));
    kegare->aiActionIndex = memory | (rounds << KEGARE_HEAVY_ROUNDS_SHIFT);
  }
#endif
}

/// Records a turn that was really staged (result 0): which move a boss used,
/// and whom it aimed at. Called by BattleStaging_DispatchAction after the
/// turn, with the request it settled.
void BossAI_NoteTurn(struct BattleAction *request, s32 result) {
#if BOSS_AI_KEGARE
  struct Unit *unit;
  u32 memory;
  u32 wait;
  s32 abilityId;

  if (result != 0 || request->unitId == BATTLE_UNIT_LIST_END)
    return;
  unit = Unit_GetFar(request->unitId);
  if (unit->id != ENEMY_ID_FIRST + ENEMY_ROW_KEGARE)
    return;
  if (request->command != COMMAND_ENEMY_ABILITY &&
      request->command != COMMAND_PSYNERGY &&
      request->command != COMMAND_ATTACK)
    return;

  abilityId = request->parameter;
  if (request->command == COMMAND_ATTACK)
    abilityId = ABILITY_ATTACK;
  memory = unit->aiActionIndex;
  wait = (memory >> KEGARE_HEAL_WAIT_SHIFT) & 7;
  if (wait != 0)
    wait--;
  if (abilityId ==
      ((struct EnemyDefinition *)Enemy_GetDefinitionFar(unit->id))
          ->abilities[KEGARE_PLY_WELL])
    wait = KEGARE_HEAL_WAIT;
  if (BossAI_KegareIsHeavy(unit, abilityId))
    memory |= KEGARE_HEAVY_THIS_ROUND_BIT;
  memory &= ~((7u << KEGARE_HEAL_WAIT_SHIFT) | (7u << KEGARE_LAST_AIM_SHIFT));
  memory |= wait << KEGARE_HEAL_WAIT_SHIFT;
  if ((request->target & 0x180) == 0x100)
    memory |= (u32)(((request->target & 7) + 1) & 7) << KEGARE_LAST_AIM_SHIFT;
  unit->aiActionIndex = memory;
#endif
}

/// Kegare's pick. Her plan, on the first pick of a turn: heal when low, else
/// press with a heavy move while a party member is open, else the stock cycle;
/// one time in five she keeps the stock choice. Her limits then apply to any
/// pick, plan or stock: a heavy move only if none was used this round and the
/// last two rounds did not both have one, and Ply Well only when she is low
/// and has not healed lately. A move the limits refuse becomes one of her
/// light moves. Returns her place in her action list.
s32 BossAI_ChooseKegareSlot(struct Unit *unit, s32 slot, s32 firstPick) {
#if BOSS_AI_KEGARE
  u32 memory = unit->aiActionIndex;
  u32 wait = (memory >> KEGARE_HEAL_WAIT_SHIFT) & 7;
  u32 heavyRounds = (memory >> KEGARE_HEAVY_ROUNDS_SHIFT) & 3;
  struct BattleWork *work = gBattleWork;
  struct Unit *member;
  s32 index;
  s32 roll = Battle_RandomFar() & 0xff;
  s32 mayHeal;
  s32 mayBeHeavy;
  s32 open = 0;

  mayHeal = wait == 0 &&
            unit->hp * 100 < unit->hpMax * KEGARE_HEAL_BELOW_PERCENT;
  mayBeHeavy = (memory & KEGARE_HEAVY_THIS_ROUND_BIT) == 0 &&
               heavyRounds < KEGARE_HEAVY_ROUNDS_LIMIT;

  if (firstPick) {
    for (index = 0; work->partyUnits[index] != BATTLE_UNIT_LIST_END; index++) {
      if (work->partyUnits[index] == BATTLE_UNIT_REMOVED)
        continue;
      member = Unit_GetFar(work->partyUnits[index]);
      if (BossAI_MemberIsOpen(member))
        open = 1;
    }
    if (mayHeal) {
      slot = KEGARE_PLY_WELL;
    } else if (roll >= KEGARE_MISTAKE_CHANCE && open && mayBeHeavy) {
      switch (roll & 3) {
      case 0:
        slot = KEGARE_FREEZE_PRISM;
        break;
      case 1:
        slot = KEGARE_ICE_MISSILE;
        break;
      case 2:
        slot = KEGARE_ICE_BLESSING;
        break;
      default:
        slot = KEGARE_FROTH_SPIRAL;
        break;
      }
    }
  }

  if (slot == KEGARE_PLY_WELL && !mayHeal)
    slot = KEGARE_DELUGE + (roll % 3);
  else if ((slot == KEGARE_FREEZE_PRISM || slot == KEGARE_ICE_MISSILE ||
            slot == KEGARE_FROTH_SPIRAL || slot == KEGARE_ICE_BLESSING) &&
           !mayBeHeavy)
    slot = KEGARE_DELUGE + (roll % 3);
#endif
  return slot;
}

/// Kegare's aim at foes: some of the time she goes for the most open of the
/// members her move can reach (low HP, low Mercury resistance, lowered
/// Defense), leaves one who is guarding alone, and never aims at the member
/// she aimed at last when another is there. Otherwise the stock random pick.
/// Returns the index in unitIds to aim at, or -1 for the stock pick. Only
/// reads the battle.
s32 BossAI_ChooseKegareTarget(const s32 *unitIds, const s32 *targetPositions,
                              s32 count, s32 userId) {
#if BOSS_AI_KEGARE
  struct Unit *user = Unit_GetFar(userId);
  struct Unit *member;
  s32 last;
  s32 index;
  s32 best = -1;
  s32 bestScore = -10000;
  s32 score;

  if (user->id != ENEMY_ID_FIRST + ENEMY_ROW_KEGARE || userId <= ALLY_MAX)
    return -1;
  if ((Battle_RandomFar() & 0xff) >= KEGARE_AIM_CHANCE)
    return -1;
  last = (s32)((user->aiActionIndex >> KEGARE_LAST_AIM_SHIFT) & 7) - 1;
  for (index = 0; index < count; index++) {
    member = Unit_GetFar(unitIds[index]);
    if (member->hp == 0 || member->hpMax <= 0)
      continue;
    if (count > 1 && last >= 0 && (targetPositions[index] & 7) == last)
      continue;
    score = 1000 - (member->hp * 1000) / member->hpMax;
    score += (100 - member->element[ELEMENT_MERCURY].resistance) * 2;
    if (member->defenseStage < 0)
      score += 200;
    if (member->defendLevel != 0)
      score -= 600;
    if (score > bestScore) {
      bestScore = score;
      best = index;
    }
  }
  return best;
#else
  return -1;
#endif
}
