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
#define BOSS_AI_ASH_JENNA 1
#define BOSS_AI_HEART 1

/// Unit.aiActionIndex bits no boss may use: the stock action cycle's
/// (BattleAIState) and Ash Jenna's rush flags (AI_PUNISHED, AI_RUSH).
#define BOSS_RESERVED_BITS (0xfu | AI_PUNISHED | AI_RUSH)
/// Every boss records the party place it last aimed at, plus one (0 none),
/// in bits 28..26.
#define BOSS_LAST_AIM_SHIFT 26
#define BOSS_LAST_AIM_BITS (7u << BOSS_LAST_AIM_SHIFT)

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
/// bits 12..10 actions until she may heal again | 9..8 rounds in a row with a
/// heavy move | 7 a heavy move this round (and the last-aim bits above).
#define KEGARE_HEAVY_THIS_ROUND_BIT (1u << 7)
#define KEGARE_HEAVY_ROUNDS_SHIFT 8
#define KEGARE_HEAL_WAIT_SHIFT 10
#define KEGARE_BITS                                                            \
  (KEGARE_HEAVY_THIS_ROUND_BIT | (3u << KEGARE_HEAVY_ROUNDS_SHIFT) |           \
   (7u << KEGARE_HEAL_WAIT_SHIFT))
STATIC_ASSERT((KEGARE_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((KEGARE_BITS & BOSS_LAST_AIM_BITS) == 0);
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
static void BossAI_KegareBeginRound(void) {
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
    memory &=
        ~(KEGARE_HEAVY_THIS_ROUND_BIT | (3u << KEGARE_HEAVY_ROUNDS_SHIFT));
    kegare->aiActionIndex = memory | (rounds << KEGARE_HEAVY_ROUNDS_SHIFT);
  }
#endif
}

/// Records a turn that was really staged (result 0): which move a boss used,
/// and whom it aimed at. Called by BattleStaging_DispatchAction after the
/// turn, with the request it settled.
static void BossAI_KegareNoteTurn(struct BattleAction *request, s32 result) {
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
  if (abilityId == ((struct EnemyDefinition *)Enemy_GetDefinitionFar(unit->id))
                       ->abilities[KEGARE_PLY_WELL])
    wait = KEGARE_HEAL_WAIT;
  if (BossAI_KegareIsHeavy(unit, abilityId))
    memory |= KEGARE_HEAVY_THIS_ROUND_BIT;
  memory &= ~((7u << KEGARE_HEAL_WAIT_SHIFT) | BOSS_LAST_AIM_BITS);
  memory |= wait << KEGARE_HEAL_WAIT_SHIFT;
  if ((request->target & 0x180) == 0x100)
    memory |= (u32)(((request->target & 7) + 1) & 7) << BOSS_LAST_AIM_SHIFT;
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
static s32 BossAI_KegareChooseSlot(struct Unit *unit, s32 slot, s32 firstPick) {
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

  mayHeal =
      wait == 0 && unit->hp * 100 < unit->hpMax * KEGARE_HEAL_BELOW_PERCENT;
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
static s32 BossAI_KegareChooseTarget(const s32 *unitIds,
                                     const s32 *targetPositions, s32 count,
                                     s32 userId) {
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
  last = (s32)((user->aiActionIndex >> BOSS_LAST_AIM_SHIFT) & 7) - 1;
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

/// What a boss can see of the party at the start of a round, which is the
/// result of everything that has already happened.
struct BossPartyView {
  s32 alive;       ///< members not down
  s32 down;        ///< members down
  s32 unavailable; ///< members down, asleep or stunned
  s32 haunted;     ///< living members with an evil spirit on them
  s32 buffed;      ///< living members with a raised Attack, Defense or
                   ///< Resistance stage
  s32 hp;          ///< all members' HP
  s32 hpMax;       ///< all members' maximum HP
};

/// Fills a view of the party from the battle's lists and units.
static void BossAI_ViewParty(struct BossPartyView *view) {
  struct BattleWork *work = gBattleWork;
  struct Unit *member;
  s32 index;

  view->alive = view->down = view->unavailable = view->haunted = 0;
  view->buffed = view->hp = view->hpMax = 0;
  for (index = 0; work->partyUnits[index] != BATTLE_UNIT_LIST_END; index++) {
    if (work->partyUnits[index] == BATTLE_UNIT_REMOVED)
      continue;
    member = Unit_GetFar(work->partyUnits[index]);
    view->hp += member->hp;
    view->hpMax += member->hpMax;
    if (member->hp == 0) {
      view->down++;
      view->unavailable++;
      continue;
    }
    view->alive++;
    if (member->sleep != 0 || member->stun != 0)
      view->unavailable++;
    if (member->haunt != 0)
      view->haunted++;
    if (member->attackStage > 0 || member->defenseStage > 0 ||
        member->resistanceStage > 0)
      view->buffed++;
  }
}

/// Aims away from the party place the boss aimed at last, when it has a
/// choice: one of the other candidates, at random. Returns the index, or
/// BOSS_AIM_STOCK when there is nothing to avoid.
static s32 BossAI_AimAwayFromLast(struct Unit *user, const s32 *targetPositions,
                                  s32 count) {
  s32 last = (s32)((user->aiActionIndex >> BOSS_LAST_AIM_SHIFT) & 7) - 1;
  s32 others[6];
  s32 otherCount = 0;
  s32 index;

  if (last < 0 || count < 2)
    return BOSS_AIM_STOCK;
  for (index = 0; index < count && otherCount < 6; index++) {
    if ((targetPositions[index] & 7) != last)
      others[otherCount++] = index;
  }
  if (otherCount == 0)
    return BOSS_AIM_STOCK;
  return others[(Random16() * otherCount) >> 16];
}

/// Records the party place a boss just aimed at, for the next aim.
static u32 BossAI_RememberAim(u32 memory, struct BattleAction *request) {
  memory &= ~BOSS_LAST_AIM_BITS;
  if ((request->target & 0x180) == 0x100)
    memory |= (u32)(((request->target & 7) + 1) & 7) << BOSS_LAST_AIM_SHIFT;
  return memory;
}

/// Ash Jenna's places in her action list in Vale (enemies.c).
enum AshSlot {
  ASH_ERUPTION = 0,
  ASH_DEMON_FIRE = 1,
  ASH_FIRE_BLESSING = 2,
  ASH_MELTDOWN = 3,
  ASH_ATTACK = 4,
  ASH_INFERNO = 5,
  ASH_SUPERNOVA = 6,
  ASH_MAGMA_STORM = 7
};

/// Ash Jenna's memory in Unit.aiActionIndex, read at the start of each round
/// from what the party looks like then (never from commands chosen): bit
/// 15 a Meltdown this round | 14..13 rounds in a row with a big move | 12 a big
/// move this round | 11 the party is hurt | 10 the party has a raised stat |
/// 9 the party's HP rose since the last round | 8..5 the party's HP in
/// sixteenths at the last round | 4 the first round has passed.
/// Her rush flags (bits 30 and 31) and the stock cycle's bits are not here.
#define ASH_STARTED_BIT (1u << 4)
#define ASH_HP_SHIFT 5
#define ASH_RECOVERED_BIT (1u << 9)
#define ASH_BUFFED_BIT (1u << 10)
#define ASH_HURT_BIT (1u << 11)
#define ASH_BIG_THIS_ROUND_BIT (1u << 12)
#define ASH_BIG_ROUNDS_SHIFT 13
#define ASH_MELTDOWN_THIS_ROUND_BIT (1u << 15)
#define ASH_BITS (0xfff0u)
STATIC_ASSERT((ASH_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((ASH_BITS & BOSS_LAST_AIM_BITS) == 0);
/// The party's HP counts as risen when it gains this many sixteenths.
#define ASH_RECOVERY_STEP 3
/// Out of 256: how often she keeps the stock choice.
#define ASH_MISTAKE_CHANCE 32
/// Out of 256: how often she answers recovery or a buff with pressure.
#define ASH_REACT_CHANCE 210
/// After this many rounds in a row with a big move, one round has none.
#define ASH_BIG_ROUNDS_LIMIT 3
/// Out of 256: how often a plain pick (Eruption or her blade) becomes a big
/// move when one is allowed, so she presses instead of idling.
#define ASH_PRESS_CHANCE 150

/// Ash Jenna in Vale, or 0.
static struct Unit *BossAI_FindAsh(void) {
  s32 index;
  s32 unitId;
  struct Unit *unit;

  for (index = 0; gBattleWork->enemyIds[index] != BATTLE_UNIT_LIST_END;
       index++) {
    unitId = gBattleWork->enemyIds[index];
    if (unitId == BATTLE_UNIT_REMOVED)
      continue;
    unit = Unit_GetFar(unitId);
    if (unit->id == ENEMY_ID_FIRST + ENEMY_ASH_JENNA_VALE)
      return unit;
  }
  return 0;
}

/// Whether the slot is one of her big moves (power 120 and up).
static s32 BossAI_AshIsBig(s32 slot) {
  return slot == ASH_FIRE_BLESSING || slot == ASH_INFERNO ||
         slot == ASH_SUPERNOVA || slot == ASH_MAGMA_STORM;
}

/// Ash Jenna's view of the party at the start of a round, and her per-round
/// memory cleared.
static void BossAI_AshBeginRound(void) {
#if BOSS_AI_ASH_JENNA
  struct Unit *ash = BossAI_FindAsh();
  struct BossPartyView view;
  u32 memory;
  u32 bigRounds;
  s32 bucket;
  s32 previous;

  if (ash == 0)
    return;
  BossAI_ViewParty(&view);
  bucket = view.hpMax > 0 ? (view.hp * 15) / view.hpMax : 0;
  memory = ash->aiActionIndex;
  previous = (memory >> ASH_HP_SHIFT) & 15;
  bigRounds = (memory >> ASH_BIG_ROUNDS_SHIFT) & 3;
  if (memory & ASH_BIG_THIS_ROUND_BIT) {
    if (bigRounds < 3)
      bigRounds++;
  } else {
    bigRounds = 0;
  }
  memory &= ~ASH_BITS;
  memory |= ASH_STARTED_BIT | ((u32)bucket << ASH_HP_SHIFT) |
            (bigRounds << ASH_BIG_ROUNDS_SHIFT);
  if ((ash->aiActionIndex & ASH_STARTED_BIT) &&
      bucket >= previous + ASH_RECOVERY_STEP)
    memory |= ASH_RECOVERED_BIT;
  if (view.buffed != 0)
    memory |= ASH_BUFFED_BIT;
  if (view.hp * 2 < view.hpMax)
    memory |= ASH_HURT_BIT;
  ash->aiActionIndex = memory;
#endif
}

/// Records Ash Jenna's turn when it was really staged. The punish turn
/// (Annihilation, her summon-rush answer) is not recorded at all.
static void BossAI_AshNoteTurn(struct Unit *unit,
                               struct BattleAction *request) {
#if BOSS_AI_ASH_JENNA
  struct EnemyDefinition *enemy =
      (struct EnemyDefinition *)Enemy_GetDefinitionFar(unit->id);
  u32 memory;
  s32 abilityId;
  s32 slot;

  if (request->command != COMMAND_ENEMY_ABILITY &&
      request->command != COMMAND_PSYNERGY &&
      request->command != COMMAND_ATTACK)
    return;
  abilityId = request->parameter;
  if (request->command == COMMAND_ATTACK)
    abilityId = ABILITY_ATTACK;
  if (abilityId == ABILITY_ANNIHILATION)
    return;
  memory = unit->aiActionIndex;
  for (slot = 0; slot < 8; slot++) {
    if (enemy->abilities[slot] != abilityId)
      continue;
    if (BossAI_AshIsBig(slot))
      memory |= ASH_BIG_THIS_ROUND_BIT;
    if (slot == ASH_MELTDOWN)
      memory |= ASH_MELTDOWN_THIS_ROUND_BIT;
    break;
  }
  unit->aiActionIndex = BossAI_RememberAim(memory, request);
#endif
}

/// Ash Jenna's pick. On the first pick of a turn she answers what she has
/// seen: when the party's HP has risen or a stat is raised, she presses with
/// Meltdown (Defense down) or Demon Fire; a quarter of the time she keeps the
/// stock choice. Every pick then obeys her limits: one big move a round and a
/// calmer round after two with one, no Inferno or Supernova on a party under
/// half its HP, one Meltdown a round, and no Demon Fire once half the living
/// party is already haunted. A move the limits refuse becomes a lighter one.
/// Her punish pick (Annihilation) never reaches here.
static s32 BossAI_AshChooseSlot(struct Unit *unit, s32 slot, s32 firstPick) {
#if BOSS_AI_ASH_JENNA
  u32 memory = unit->aiActionIndex;
  u32 bigRounds = (memory >> ASH_BIG_ROUNDS_SHIFT) & 3;
  s32 roll = Battle_RandomFar() & 0xff;
  s32 react = Battle_RandomFar() & 0xff;
  struct BossPartyView view;
  s32 mayBeBig;

  BossAI_ViewParty(&view);
  mayBeBig = (memory & ASH_BIG_THIS_ROUND_BIT) == 0 &&
             bigRounds < ASH_BIG_ROUNDS_LIMIT;
  if (firstPick && roll >= ASH_MISTAKE_CHANCE &&
      (memory & (ASH_RECOVERED_BIT | ASH_BUFFED_BIT)) &&
      react < ASH_REACT_CHANCE)
    slot =
        (memory & ASH_MELTDOWN_THIS_ROUND_BIT) ? ASH_DEMON_FIRE : ASH_MELTDOWN;

  if (mayBeBig && (slot == ASH_ATTACK || slot == ASH_ERUPTION) &&
      (Battle_RandomFar() & 0xff) < ASH_PRESS_CHANCE) {
    static const u8 bigSlots[3] = {ASH_INFERNO, ASH_SUPERNOVA,
                                   ASH_MAGMA_STORM};
    slot = bigSlots[(Battle_RandomFar() & 0xff) % 3];
  }
  if (BossAI_AshIsBig(slot) && !mayBeBig)
    slot = ASH_ERUPTION;
  if (slot == ASH_MELTDOWN && (memory & ASH_MELTDOWN_THIS_ROUND_BIT))
    slot = ASH_ATTACK;
  if (slot == ASH_DEMON_FIRE && view.alive > 0 &&
      view.haunted * 2 >= view.alive)
    slot = ASH_ATTACK;
#endif
  return slot;
}

/// Ash Jenna's aim: never the party place she aimed at last when there is
/// another. She does not look at who is weak or at what was commanded.
static s32 BossAI_AshChooseTarget(struct Unit *user, const s32 *targetPositions,
                                  s32 count) {
#if BOSS_AI_ASH_JENNA
  return BossAI_AimAwayFromLast(user, targetPositions, count);
#else
  return BOSS_AIM_STOCK;
#endif
}

/// Heart's places in her action list (enemies.c).
enum HeartSlot {
  HEART_DEMON_NIGHT = 0,
  HEART_DARK_BLESSING = 1,
  HEART_DEMON_FIRE = 2,
  HEART_DEATH_PLUNGE = 3,
  HEART_HEARTRENDER = 4,
  HEART_OUTER_SPACE = 5,
  HEART_ANNIHILATION = 6,
  HEART_ATTACK = 7
};

/// Heart's memory in Unit.aiActionIndex: bits 25..20 the party places that
/// were down when the round began | 19 a payoff was used this round | 18 a
/// hard disable this round | 17 a big move this round | 16..14 rounds begun so
/// far, up to 7 | 13..10 rounds until Annihilation may be tried again |
/// 9..8 calm rounds before the next warning | 7..6 turns she has taken this
/// round | 5 the warning was given last round, so a payoff may come now |
/// 4 the warning was given this round.
/// A warning is Heartrender, which does no damage and is her only use of it.
/// A payoff is Outer Space, Death Plunge or Annihilation, and comes in the
/// round after the warning, never as her first turn of it, so what the party
/// chose after seeing the warning acts before it.
#define HEART_WARNED_BIT (1u << 4)
#define HEART_PAYOFF_READY_BIT (1u << 5)
#define HEART_TURNS_SHIFT 6
#define HEART_CALM_SHIFT 8
#define HEART_ANNIHILATION_WAIT_SHIFT 10
#define HEART_ROUNDS_SHIFT 14
#define HEART_BIG_BIT (1u << 17)
#define HEART_DISABLE_BIT (1u << 18)
#define HEART_PAYOFF_USED_BIT (1u << 19)
#define HEART_DOWN_SHIFT 20
#define HEART_BITS (0x03fffff0u)
STATIC_ASSERT((HEART_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((HEART_BITS & BOSS_LAST_AIM_BITS) == 0);
/// Rounds after an Annihilation before she may try it again: the next try is
/// seven rounds on, so six rounds pass between.
#define HEART_ANNIHILATION_WAIT 7
/// Annihilation is never tried until this round.
#define HEART_ANNIHILATION_FIRST_ROUND 4
/// Out of 256: how often she keeps the stock choice, and how often a round
/// that may begin with the warning does.
#define HEART_MISTAKE_CHANCE 51
#define HEART_WARNING_CHANCE 128
/// Calm rounds after a payoff round before the next warning may come.
#define HEART_CALM_ROUNDS 1
/// The party must have at least this percent of its HP for her to warn.
#define HEART_WARNING_ABOVE_PERCENT 40

/// Heart, or 0.
static struct Unit *BossAI_FindHeart(void) {
  s32 index;
  s32 unitId;
  struct Unit *unit;

  for (index = 0; gBattleWork->enemyIds[index] != BATTLE_UNIT_LIST_END;
       index++) {
    unitId = gBattleWork->enemyIds[index];
    if (unitId == BATTLE_UNIT_REMOVED)
      continue;
    unit = Unit_GetFar(unitId);
    if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_HEART)
      return unit;
  }
  return 0;
}

/// Starts a round for Heart: the warning of last round becomes this round's
/// permission for a payoff, her per-round memory is cleared, and the party
/// places that are down are noted, which is how a member revived during the
/// round is told from one who was standing.
static void BossAI_HeartBeginRound(void) {
#if BOSS_AI_HEART
  struct Unit *heart = BossAI_FindHeart();
  struct BattleWork *work = gBattleWork;
  u32 memory;
  u32 calm;
  u32 wait;
  u32 rounds;
  u32 down = 0;
  s32 index;
  s32 wasReady;

  if (heart == 0)
    return;
  memory = heart->aiActionIndex;
  wasReady = (memory & HEART_PAYOFF_READY_BIT) != 0;
  calm = (memory >> HEART_CALM_SHIFT) & 3;
  wait = (memory >> HEART_ANNIHILATION_WAIT_SHIFT) & 15;
  rounds = (memory >> HEART_ROUNDS_SHIFT) & 7;
  if (calm != 0)
    calm--;
  if (wasReady)
    calm = HEART_CALM_ROUNDS;
  if (wait != 0)
    wait--;
  if (rounds < 7)
    rounds++;
  for (index = 0; work->partyUnits[index] != BATTLE_UNIT_LIST_END && index < 6;
       index++) {
    if (work->partyUnits[index] != BATTLE_UNIT_REMOVED &&
        Unit_GetFar(work->partyUnits[index])->hp == 0)
      down |= 1u << index;
  }
  memory &= ~HEART_BITS;
  memory |=
      (heart->aiActionIndex & HEART_WARNED_BIT) ? HEART_PAYOFF_READY_BIT : 0;
  memory |= (calm << HEART_CALM_SHIFT) |
            (wait << HEART_ANNIHILATION_WAIT_SHIFT) |
            (rounds << HEART_ROUNDS_SHIFT) | (down << HEART_DOWN_SHIFT);
  heart->aiActionIndex = memory;
#endif
}

/// Records Heart's turn when it was really staged.
static void BossAI_HeartNoteTurn(struct Unit *unit,
                                 struct BattleAction *request) {
#if BOSS_AI_HEART
  struct EnemyDefinition *enemy =
      (struct EnemyDefinition *)Enemy_GetDefinitionFar(unit->id);
  u32 memory = unit->aiActionIndex;
  u32 turns = (memory >> HEART_TURNS_SHIFT) & 3;
  s32 abilityId;
  s32 slot;

  if (request->command != COMMAND_ENEMY_ABILITY &&
      request->command != COMMAND_PSYNERGY &&
      request->command != COMMAND_ATTACK)
    return;
  abilityId = request->parameter;
  if (request->command == COMMAND_ATTACK)
    abilityId = ABILITY_ATTACK;
  if (turns < 3)
    turns++;
  memory &= ~(3u << HEART_TURNS_SHIFT);
  memory |= turns << HEART_TURNS_SHIFT;
  for (slot = 0; slot < 8; slot++) {
    if (enemy->abilities[slot] != abilityId)
      continue;
    switch (slot) {
    case HEART_HEARTRENDER:
      memory |= HEART_WARNED_BIT;
      break;
    case HEART_DARK_BLESSING:
      memory |= HEART_BIG_BIT;
      break;
    case HEART_OUTER_SPACE:
      memory |= HEART_BIG_BIT | HEART_PAYOFF_USED_BIT;
      break;
    case HEART_DEATH_PLUNGE:
      memory |= HEART_DISABLE_BIT | HEART_PAYOFF_USED_BIT;
      break;
    case HEART_ANNIHILATION:
      memory |= HEART_DISABLE_BIT | HEART_PAYOFF_USED_BIT;
      memory &= ~(15u << HEART_ANNIHILATION_WAIT_SHIFT);
      memory |= (u32)HEART_ANNIHILATION_WAIT << HEART_ANNIHILATION_WAIT_SHIFT;
      break;
    }
    break;
  }
  unit->aiActionIndex = BossAI_RememberAim(memory, request);
#endif
}

/// Heart's pick. A round in which she may warn begins, some of the time, with
/// Heartrender; in the round after it she picks one payoff (Outer Space,
/// Death Plunge or Annihilation, weighted 40, 25 and 35 among those allowed)
/// as one of her later turns. Her limits apply to every pick, and a move they
/// refuse becomes Demon Night, Demon Fire or Attack: Heartrender only warns;
/// a payoff only follows a warning, not as her first turn, once a round, and
/// not on a re-pick; Annihilation needs round 4 or later, no one down, seven
/// rounds since the last try and at most one member unable to act, and
/// Death Plunge at most one unable to act; Outer Space at most one down; Dark
/// Blessing once a round and not in a warning or payoff round; and no Haunt
/// move once half the living party is haunted.
static s32 BossAI_HeartChooseSlot(struct Unit *unit, s32 slot, s32 firstPick) {
#if BOSS_AI_HEART
  u32 memory = unit->aiActionIndex;
  u32 turns = (memory >> HEART_TURNS_SHIFT) & 3;
  u32 rounds = (memory >> HEART_ROUNDS_SHIFT) & 7;
  u32 wait = (memory >> HEART_ANNIHILATION_WAIT_SHIFT) & 15;
  u32 calm = (memory >> HEART_CALM_SHIFT) & 3;
  struct BossPartyView view;
  s32 roll = Battle_RandomFar() & 0xff;
  s32 roll2 = Battle_RandomFar() & 0xff;
  s32 ready = (memory & HEART_PAYOFF_READY_BIT) != 0;
  s32 warned = (memory & HEART_WARNED_BIT) != 0;
  s32 payoffRound =
      ready && turns >= 1 && firstPick && (memory & HEART_PAYOFF_USED_BIT) == 0;
  s32 mayWarn;
  s32 mayAnnihilate;
  s32 mayDeathPlunge;
  s32 mayOuterSpace;
  s32 total;
  s32 light[3] = {HEART_DEMON_NIGHT, HEART_DEMON_FIRE, HEART_ATTACK};

  BossAI_ViewParty(&view);
  mayWarn = firstPick && turns == 0 && !ready && !warned && calm == 0 &&
            view.down <= 1 &&
            view.hp * 100 >= view.hpMax * HEART_WARNING_ABOVE_PERCENT;
  mayAnnihilate = payoffRound && rounds >= HEART_ANNIHILATION_FIRST_ROUND &&
                  wait == 0 && view.down == 0 && view.unavailable <= 1 &&
                  (memory & HEART_DISABLE_BIT) == 0;
  mayDeathPlunge =
      payoffRound && view.unavailable <= 1 && (memory & HEART_DISABLE_BIT) == 0;
  mayOuterSpace =
      payoffRound && view.down <= 1 && (memory & HEART_BIG_BIT) == 0;

  if (firstPick && roll >= HEART_MISTAKE_CHANCE) {
    if (mayWarn && roll2 < HEART_WARNING_CHANCE) {
      slot = HEART_HEARTRENDER;
    } else if (payoffRound) {
      total = (mayOuterSpace ? 40 : 0) + (mayDeathPlunge ? 25 : 0) +
              (mayAnnihilate ? 35 : 0);
      if (total > 0) {
        s32 pick = (roll2 * total) >> 8;

        if (mayOuterSpace && pick < 40) {
          slot = HEART_OUTER_SPACE;
        } else {
          pick -= mayOuterSpace ? 40 : 0;
          if (mayDeathPlunge && pick < 25)
            slot = HEART_DEATH_PLUNGE;
          else
            slot = HEART_ANNIHILATION;
        }
      }
    }
  }

  switch (slot) {
  case HEART_HEARTRENDER:
    if (!mayWarn)
      slot = light[roll % 3];
    break;
  case HEART_OUTER_SPACE:
    if (!mayOuterSpace)
      slot = light[roll % 3];
    break;
  case HEART_DEATH_PLUNGE:
    if (!mayDeathPlunge)
      slot = light[roll % 3];
    break;
  case HEART_ANNIHILATION:
    if (!mayAnnihilate)
      slot = light[roll % 3];
    break;
  case HEART_DARK_BLESSING:
    if ((memory & HEART_BIG_BIT) != 0 || warned || ready)
      slot = light[roll % 3];
    break;
  }
  if ((slot == HEART_DEMON_NIGHT || slot == HEART_DEMON_FIRE) &&
      view.alive > 0 && view.haunted * 2 >= view.alive)
    slot = HEART_ATTACK;
#endif
  return slot;
}

/// Heart's aim. A single-target disable or an instant death (Death Plunge,
/// Annihilation) skips a member who was down when the round began (so one
/// revived this round is safe from it), and one who is already asleep or
/// stunned; with no one left it picks again. Every other move aims at a
/// member other than the one she aimed at last, when there is another.
static s32 BossAI_HeartChooseTarget(struct Unit *user,
                                    struct AbilityDefinition *action,
                                    const s32 *unitIds,
                                    const s32 *targetPositions, s32 count) {
#if BOSS_AI_HEART
  u32 down = (user->aiActionIndex >> HEART_DOWN_SHIFT) & 0x3f;
  s32 last = (s32)((user->aiActionIndex >> BOSS_LAST_AIM_SHIFT) & 7) - 1;
  s32 allowed[6];
  s32 allowedCount = 0;
  s32 index;
  struct Unit *member;
  s32 place;
  s32 hard = action->effect == ABILITY_EFFECT_STUN ||
             action->effect == ABILITY_EFFECT_INSTANT_DEATH;

  if (!hard)
    return BossAI_AimAwayFromLast(user, targetPositions, count);
  for (index = 0; index < count && allowedCount < 6; index++) {
    member = Unit_GetFar(unitIds[index]);
    place = targetPositions[index] & 7;
    if (member->hp == 0 || member->sleep != 0 || member->stun != 0)
      continue;
    if (place < 6 && (down & (1u << place)) != 0)
      continue;
    allowed[allowedCount++] = index;
  }
  if (allowedCount == 0)
    return BOSS_AIM_NONE;
  if (allowedCount > 1 && last >= 0) {
    s32 kept[6];
    s32 keptCount = 0;

    for (index = 0; index < allowedCount; index++) {
      if ((targetPositions[allowed[index]] & 7) != last)
        kept[keptCount++] = allowed[index];
    }
    if (keptCount > 0) {
      s32 i;

      for (i = 0; i < keptCount; i++)
        allowed[i] = kept[i];
      allowedCount = keptCount;
    }
  }
  return allowed[(Random16() * allowedCount) >> 16];
#else
  return BOSS_AIM_STOCK;
#endif
}

/// Starts a round for the bosses: their per-round memory is cleared and their
/// view of the party brought up to date. Called once a round by
/// BattleTurnOrder_Sort, before anyone acts.
void BossAI_BeginRound(void) {
  BossAI_KegareBeginRound();
  BossAI_AshBeginRound();
  BossAI_HeartBeginRound();
}

/// Records a turn that was really staged (result 0). Called by
/// BattleStaging_DispatchAction after the turn, with the request it settled.
/// A turn that failed changes nothing.
void BossAI_NoteTurn(struct BattleAction *request, s32 result) {
  struct Unit *unit;

  BossAI_KegareNoteTurn(request, result);
  if (result != 0 || request->unitId == BATTLE_UNIT_LIST_END)
    return;
  unit = Unit_GetFar(request->unitId);
  if (unit->id == ENEMY_ID_FIRST + ENEMY_ASH_JENNA_VALE)
    BossAI_AshNoteTurn(unit, request);
  else if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_HEART)
    BossAI_HeartNoteTurn(unit, request);
}

/// A boss's pick of a place in its action list. Returns slot unchanged for
/// every other enemy, without drawing a random number. Called by
/// BattleAI_ChooseAction at an enemy's turn; firstPick is 0 on a re-pick after
/// a refused move.
s32 BossAI_ChooseSlot(struct Unit *unit, s32 slot, s32 firstPick) {
  if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_KEGARE)
    return BossAI_KegareChooseSlot(unit, slot, firstPick);
  if (unit->id == ENEMY_ID_FIRST + ENEMY_ASH_JENNA_VALE)
    return BossAI_AshChooseSlot(unit, slot, firstPick);
  if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_HEART)
    return BossAI_HeartChooseSlot(unit, slot, firstPick);
  return slot;
}

/// A boss's aim at foes, from the candidates BattleAI_ChooseTarget settled.
/// Returns the index to aim at, BOSS_AIM_STOCK for the stock random pick, or
/// BOSS_AIM_NONE when no candidate is fit. Other units get BOSS_AIM_STOCK
/// without drawing a random number.
s32 BossAI_ChooseTarget(s32 userId, struct AbilityDefinition *action,
                        const s32 *unitIds, const s32 *targetPositions,
                        s32 count) {
  struct Unit *user = Unit_GetFar(userId);

  if (user->id == ENEMY_ID_FIRST + ENEMY_ROW_KEGARE)
    return BossAI_KegareChooseTarget(unitIds, targetPositions, count, userId);
  if (user->id == ENEMY_ID_FIRST + ENEMY_ASH_JENNA_VALE && userId > ALLY_MAX)
    return BossAI_AshChooseTarget(user, targetPositions, count);
  if (user->id == ENEMY_ID_FIRST + ENEMY_ROW_HEART && userId > ALLY_MAX)
    return BossAI_HeartChooseTarget(user, action, unitIds, targetPositions,
                                    count);
  return BOSS_AIM_STOCK;
}
