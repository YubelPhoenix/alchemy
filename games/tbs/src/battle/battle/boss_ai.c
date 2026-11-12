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

/// The unit of the enemy in row `row` of enemies.c, or 0 when it is not in
/// this battle.
static struct Unit *BossAI_FindRow(s32 row) {
  s32 index;
  s32 unitId;
  struct Unit *unit;

  for (index = 0; gBattleWork->enemyIds[index] != BATTLE_UNIT_LIST_END;
       index++) {
    unitId = gBattleWork->enemyIds[index];
    if (unitId == BATTLE_UNIT_REMOVED)
      continue;
    unit = Unit_GetFar(unitId);
    if (unit->id == ENEMY_ID_FIRST + row)
      return unit;
  }
  return 0;
}

/// Where the enemy's staged request sits in its action list, or -1 when it is
/// not a move of its list. A plain Attack is looked up as ABILITY_ATTACK.
static s32 BossAI_RequestSlot(struct Unit *unit, struct BattleAction *request) {
  struct EnemyDefinition *enemy =
      (struct EnemyDefinition *)Enemy_GetDefinitionFar(unit->id);
  s32 abilityId = request->parameter;
  s32 slot;

  if (request->command == COMMAND_ATTACK)
    abilityId = ABILITY_ATTACK;
  else if (request->command != COMMAND_ENEMY_ABILITY &&
           request->command != COMMAND_PSYNERGY)
    return -1;
  for (slot = 0; slot < 8; slot++) {
    if (enemy->abilities[slot] == abilityId)
      return slot;
  }
  return -1;
}

/// Kegare's eight attacks and status effects, matching enemies.c.
enum KegareSlot {
  KEGARE_FREEZE_PRISM = 0,
  KEGARE_ICE_BLESSING = 1,
  KEGARE_STORM_BLESSING = 2,
  KEGARE_ANNIHILATION = 3,
  KEGARE_DEMON_NIGHT = 4,
  KEGARE_PSY_DRAIN = 5,
  KEGARE_BIND = 6,
  KEGARE_PURE_PLY = 7
};

/// Kegare only needs a heal cooldown and one Annihilation-per-round bit.
/// The old heavy-attack streak was recorded but never used to choose a move.
#define KEGARE_HEAL_WAIT_SHIFT 10
#define KEGARE_ANNIHILATION_THIS_ROUND_BIT (1u << 13)
#define KEGARE_DRAIN_USED_BIT (1u << 14)
#define KEGARE_BIND_USED_BIT (1u << 15)
#define KEGARE_BITS ((7u << KEGARE_HEAL_WAIT_SHIFT) | \
                     KEGARE_ANNIHILATION_THIS_ROUND_BIT | \
                     KEGARE_DRAIN_USED_BIT | KEGARE_BIND_USED_BIT)
STATIC_ASSERT((KEGARE_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((KEGARE_BITS & BOSS_LAST_AIM_BITS) == 0);
/// She may heal (Pure Ply) only below this
/// percent of her HP, and then not again for this many of her actions after a
/// heal that was really cast.
#define KEGARE_HEAL_BELOW_PERCENT 60
#define KEGARE_HEAL_WAIT 3
/// Out of 256: how often a turn of hers is Annihilation when one is allowed.
#define KEGARE_ANNIHILATION_CHANCE 170
/// Out of 256: how often she keeps the stock choice instead of her own plan.
#define KEGARE_MISTAKE_CHANCE 51
/// Out of 256: how often she aims at the member who is most open.
#define KEGARE_AIM_CHANCE 102

/// A party member Kegare can exploit: HP under half, Defense lowered (the
/// member's own, by anyone), or unable to act. Nobody who is down counts.
static s32 BossAI_MemberIsOpen(struct Unit *member) {
  return member->hp != 0 &&
         (member->hp * 2 < member->hpMax || member->defenseStage < 0 ||
          member->sleep != 0 || member->stun != 0);
}

/// Start Kegare's round; cooldown is already counted by staged actions.
static void BossAI_KegareBeginRound(void) {
#if BOSS_AI_KEGARE
  struct Unit *kegare = BossAI_FindRow(ENEMY_ROW_KEGARE);
  if (kegare != 0)
    kegare->aiActionIndex &= ~(KEGARE_ANNIHILATION_THIS_ROUND_BIT |
                               KEGARE_DRAIN_USED_BIT | KEGARE_BIND_USED_BIT);
#endif
}

/// Only staged actions affect Kegare's healing and once-a-round limits.
static void BossAI_KegareNoteTurn(struct BattleAction *request, s32 result) {
#if BOSS_AI_KEGARE
  struct Unit *unit;
  u32 memory;
  u32 wait;
  s32 slot;

  if (result != 0 || request->unitId == BATTLE_UNIT_LIST_END)
    return;
  unit = Unit_GetFar(request->unitId);
  if (unit->id != ENEMY_ID_FIRST + ENEMY_ROW_KEGARE)
    return;
  slot = BossAI_RequestSlot(unit, request);
  if (slot < 0)
    return;
  memory = unit->aiActionIndex;
  wait = (memory >> KEGARE_HEAL_WAIT_SHIFT) & 7;
  if (wait != 0)
    wait--;
  if (slot == KEGARE_PURE_PLY)
    wait = KEGARE_HEAL_WAIT;
  if (slot == KEGARE_ANNIHILATION)
    memory |= KEGARE_ANNIHILATION_THIS_ROUND_BIT;
  if (slot == KEGARE_PSY_DRAIN)
    memory |= KEGARE_DRAIN_USED_BIT;
  if (slot == KEGARE_BIND)
    memory |= KEGARE_BIND_USED_BIT;
  memory &= ~((7u << KEGARE_HEAL_WAIT_SHIFT) | BOSS_LAST_AIM_BITS);
  memory |= wait << KEGARE_HEAL_WAIT_SHIFT;
  if ((request->target & 0x180) == 0x100)
    memory |= (u32)(((request->target & 7) + 1) & 7)
              << BOSS_LAST_AIM_SHIFT;
  unit->aiActionIndex = memory;
#endif
}

/// Keep Pure Ply at critical HP, but break stalling with early offense.
static s32 BossAI_KegareChooseSlot(struct Unit *unit, s32 slot, s32 firstPick) {
#if BOSS_AI_KEGARE
  static const u8 pressure[4] = {KEGARE_FREEZE_PRISM, KEGARE_ICE_BLESSING,
                                 KEGARE_STORM_BLESSING, KEGARE_DEMON_NIGHT};
  u32 memory = unit->aiActionIndex;
  s32 roll = Battle_RandomFar() & 0xff;
  s32 roll2 = Battle_RandomFar() & 0xff;
  s32 mayHeal = ((memory >> KEGARE_HEAL_WAIT_SHIFT) & 7) == 0 &&
                unit->hp * 100 < unit->hpMax * KEGARE_HEAL_BELOW_PERCENT;
  if (firstPick) {
    if (mayHeal && (unit->hp * 100 < unit->hpMax * 35 || roll2 < 116))
      slot = KEGARE_PURE_PLY;
    else if ((memory & KEGARE_ANNIHILATION_THIS_ROUND_BIT) == 0 &&
             roll < KEGARE_ANNIHILATION_CHANCE)
      slot = KEGARE_ANNIHILATION;
    else if ((memory & KEGARE_DRAIN_USED_BIT) == 0 && roll2 < 24)
      slot = KEGARE_PSY_DRAIN;
    else if ((memory & KEGARE_BIND_USED_BIT) == 0 && roll2 < 48)
      slot = KEGARE_BIND;
    else
      slot = pressure[roll2 & 3];
  }
  if (slot == KEGARE_PURE_PLY && !mayHeal)
    slot = KEGARE_ICE_BLESSING;
  else if (slot == KEGARE_ANNIHILATION &&
           (memory & KEGARE_ANNIHILATION_THIS_ROUND_BIT))
    slot = KEGARE_STORM_BLESSING;
  else if (slot == KEGARE_PSY_DRAIN && (memory & KEGARE_DRAIN_USED_BIT))
    slot = KEGARE_ICE_BLESSING;
  else if (slot == KEGARE_BIND && (memory & KEGARE_BIND_USED_BIT))
    slot = KEGARE_DEMON_NIGHT;
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
  s32 pp;          ///< combined PP of living party members
  s32 sealed;      ///< living party members with Psynergy sealed
  s32 hp;          ///< all members' HP
  s32 hpMax;       ///< all members' maximum HP
};

/// Fills a view of the party from the battle's lists and units.
static void BossAI_ViewParty(struct BossPartyView *view) {
  struct BattleWork *work = gBattleWork;
  struct Unit *member;
  s32 index;

  view->alive = view->down = view->unavailable = view->haunted = 0;
  view->buffed = view->pp = view->sealed = view->hp = view->hpMax = 0;
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
    view->pp += member->pp;
    if (member->psySeal != 0)
      view->sealed++;
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

/// Select the living party member with the most PP. Bind skips sealed targets.
static s32 BossAI_AimAtPp(const s32 *unitIds, s32 count, s32 unsealed) {
  s32 index;
  s32 best = BOSS_AIM_STOCK;
  s32 value = 0;
  for (index = 0; index < count; index++) {
    struct Unit *member = Unit_GetFar(unitIds[index]);
    if (member->hp == 0 || member->pp <= 0 ||
        (unsealed && member->psySeal != 0))
      continue;
    if (member->pp > value) {
      value = member->pp;
      best = index;
    }
  }
  return best;
}

/// Records the party place a boss just aimed at, for the next aim.
static u32 BossAI_RememberAim(u32 memory, struct BattleAction *request) {
  memory &= ~BOSS_LAST_AIM_BITS;
  if ((request->target & 0x180) == 0x100)
    memory |= (u32)(((request->target & 7) + 1) & 7) << BOSS_LAST_AIM_SHIFT;
  return memory;
}

/// Vale Ash Jenna: destructive fire, a dangerous physical finish and PP theft.
enum AshSlot {
  ASH_MELTDOWN = 0,
  ASH_ACID_BLESSING = 1,
  ASH_PYROCLASM = 2,
  ASH_SUPERNOVA = 3,
  ASH_ANNIHILATION = 4,
  ASH_SEVERE_BLOW = 5,
  ASH_DEMON_FIRE = 6,
  ASH_PSY_DRAIN = 7
};
#define ASH_STARTED_BIT (1u << 4)
#define ASH_MELTDOWN_THIS_ROUND_BIT (1u << 5)
#define ASH_ANNIHILATION_SHIFT 6
#define ASH_BREAK_SHIFT 8
#define ASH_TURNS_SHIFT 10
#define ASH_DRAIN_USED_BIT (1u << 12)
#define ASH_SEVERE_USED_BIT (1u << 13)
#define ASH_BITS (0x3ff0u)
STATIC_ASSERT((ASH_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((ASH_BITS & BOSS_LAST_AIM_BITS) == 0);
#define ASH_ANNIHILATION_CHANCE 156
#define ASH_BREAK_AFTER_ROUNDS 2

/// Ash Jenna's memory brought up to date at the start of a round.
static void BossAI_AshBeginRound(void) {
#if BOSS_AI_ASH_JENNA
  struct Unit *ash = BossAI_FindRow(ENEMY_ASH_JENNA_VALE);
  u32 memory;
  u32 since;

  if (ash == 0)
    return;
  memory = ash->aiActionIndex;
  since = (memory >> ASH_BREAK_SHIFT) & 3;
  if ((memory & ASH_STARTED_BIT) && since < 3)
    since++;
  memory &= ~(ASH_MELTDOWN_THIS_ROUND_BIT | (3u << ASH_ANNIHILATION_SHIFT) |
              (3u << ASH_BREAK_SHIFT) | (3u << ASH_TURNS_SHIFT) |
              ASH_DRAIN_USED_BIT | ASH_SEVERE_USED_BIT);
  memory |= ASH_STARTED_BIT | (since << ASH_BREAK_SHIFT);
  ash->aiActionIndex = memory;
#endif
}

/// Records Ash Jenna's turn when it was really staged.
static void BossAI_AshNoteTurn(struct Unit *unit,
                               struct BattleAction *request) {
#if BOSS_AI_ASH_JENNA
  u32 memory = unit->aiActionIndex;
  u32 count = (memory >> ASH_TURNS_SHIFT) & 3;
  s32 slot = BossAI_RequestSlot(unit, request);

  if (slot < 0 && request->command != COMMAND_ENEMY_ABILITY &&
      request->command != COMMAND_PSYNERGY && request->command != COMMAND_ATTACK)
    return;
  if (count < 3)
    count++;
  memory &= ~(3u << ASH_TURNS_SHIFT);
  memory |= count << ASH_TURNS_SHIFT;
  if (slot == ASH_MELTDOWN || slot == ASH_ACID_BLESSING) {
    memory &= ~(3u << ASH_BREAK_SHIFT);
    if (slot == ASH_MELTDOWN)
      memory |= ASH_MELTDOWN_THIS_ROUND_BIT;
  } else if (slot == ASH_ANNIHILATION) {
    count = (memory >> ASH_ANNIHILATION_SHIFT) & 3;
    if (count < 3)
      count++;
    memory &= ~(3u << ASH_ANNIHILATION_SHIFT);
    memory |= count << ASH_ANNIHILATION_SHIFT;
  }
  if (slot == ASH_SEVERE_BLOW)
    memory |= ASH_SEVERE_USED_BIT;
  if (slot == ASH_PSY_DRAIN)
    memory |= ASH_DRAIN_USED_BIT;
  unit->aiActionIndex = BossAI_RememberAim(memory, request);
#endif
}

/// Attack from the opening turn, with a deadlier second phase.
static s32 BossAI_AshChooseSlot(struct Unit *unit, s32 slot, s32 firstPick) {
#if BOSS_AI_ASH_JENNA
  static const u8 pressure[4] = {ASH_PYROCLASM, ASH_ACID_BLESSING,
                                 ASH_SUPERNOVA, ASH_PYROCLASM};
  u32 memory = unit->aiActionIndex;
  u32 turns = (memory >> ASH_TURNS_SHIFT) & 3;
  u32 since = (memory >> ASH_BREAK_SHIFT) & 3;
  u32 done = (memory >> ASH_ANNIHILATION_SHIFT) & 3;
  s32 roll = Battle_RandomFar() & 0xff;
  s32 roll2 = Battle_RandomFar() & 0xff;
  struct BossPartyView view;
  s32 late = unit->hp * 2 < unit->hpMax;
  s32 limit = late ? 2 : 1;
  BossAI_ViewParty(&view);
  if (!firstPick)
    return ASH_ACID_BLESSING;
  if (view.alive > 1 && (s32)done < limit &&
      roll < (late ? 196 : ASH_ANNIHILATION_CHANCE))
    return ASH_ANNIHILATION;
  if (turns == 0 && (memory & ASH_MELTDOWN_THIS_ROUND_BIT) == 0 &&
      (!(memory & ASH_STARTED_BIT) || since >= ASH_BREAK_AFTER_ROUNDS) &&
      roll2 < 56)
    return ASH_MELTDOWN;
  if (view.alive > 0 && view.down <= 1 &&
      (memory & ASH_SEVERE_USED_BIT) == 0 && roll2 < 104)
    return ASH_SEVERE_BLOW;
  if (view.alive > 0 && view.haunted * 2 < view.alive && roll2 < 132)
    return ASH_DEMON_FIRE;
  if (view.pp > 0 && (memory & ASH_DRAIN_USED_BIT) == 0 && roll2 > 239)
    return ASH_PSY_DRAIN;
  slot = pressure[roll2 & 3];
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

/// Heart: immediate pressure, no warning or payoff rounds.
enum HeartSlot {
 HEART_DARK_BLESSING=0, HEART_AVALANCHE=1, HEART_DRAGON_DRIVER=2,
 HEART_DEATH_PLUNGE=3, HEART_HEARTRENDER=4, HEART_OUTER_SPACE=5,
 HEART_ANNIHILATION=6, HEART_SEVERE_BLOW=7
};
#define HEART_ANNIHILATION_USED_BIT (1u << 16)
#define HEART_HEARTRENDER_USED_BIT (1u << 17)
#define HEART_BITS (HEART_ANNIHILATION_USED_BIT | HEART_HEARTRENDER_USED_BIT)
STATIC_ASSERT((HEART_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((HEART_BITS & BOSS_LAST_AIM_BITS) == 0);
static void BossAI_HeartBeginRound(void) {
#if BOSS_AI_HEART
 struct Unit *heart=BossAI_FindRow(ENEMY_ROW_HEART);
 if (heart != 0) heart->aiActionIndex &= ~HEART_BITS;
#endif
}
static void BossAI_HeartNoteTurn(struct Unit *unit, struct BattleAction *request) {
#if BOSS_AI_HEART
 s32 slot=BossAI_RequestSlot(unit,request);
 u32 memory=unit->aiActionIndex;
 if (slot==HEART_ANNIHILATION) memory |= HEART_ANNIHILATION_USED_BIT;
 if (slot==HEART_HEARTRENDER) memory |= HEART_HEARTRENDER_USED_BIT;
 unit->aiActionIndex=BossAI_RememberAim(memory,request);
#endif
}
static s32 BossAI_HeartChooseSlot(struct Unit *unit,s32 slot,s32 firstPick) {
#if BOSS_AI_HEART
 u32 memory=unit->aiActionIndex;
 struct BossPartyView view;
 s32 roll=Battle_RandomFar() & 0xff;
 s32 late=unit->hp*2<=unit->hpMax;
 BossAI_ViewParty(&view);
 if (!firstPick) return HEART_AVALANCHE;
 if (view.alive>1 && !(memory & HEART_ANNIHILATION_USED_BIT) &&
     roll<(late?43:32)) return HEART_ANNIHILATION;
 if (roll<(late?112:99)) return HEART_OUTER_SPACE;
 if (roll<(late?161:148)) return HEART_DEATH_PLUNGE;
 if (roll<189) return HEART_DRAGON_DRIVER;
 if (roll<220) return HEART_AVALANCHE;
 if (!(memory & HEART_HEARTRENDER_USED_BIT) && roll<233) return HEART_HEARTRENDER;
 if (roll<245) return HEART_SEVERE_BLOW;
 return HEART_DARK_BLESSING;
#else
 return slot;
#endif
}

/// Heart's aim: avoid targets already asleep or stunned for disabling moves.
/// Otherwise rotate targets when possible.
static s32 BossAI_HeartChooseTarget(struct Unit *user,
                                    struct AbilityDefinition *action,
                                    const s32 *unitIds,
                                    const s32 *targetPositions, s32 count) {
#if BOSS_AI_HEART
  s32 last = (s32)((user->aiActionIndex >> BOSS_LAST_AIM_SHIFT) & 7) - 1;
  s32 allowed[6];
  s32 allowedCount = 0;
  s32 index;
  struct Unit *member;
  s32 hard = action->effect == ABILITY_EFFECT_STUN ||
             action->effect == ABILITY_EFFECT_INSTANT_DEATH;

  if (action->effect == ABILITY_EFFECT_DRAIN_PP)
    return BossAI_AimAtPp(unitIds, count, 0);
  if (!hard)
    return BossAI_AimAwayFromLast(user, targetPositions, count);
  for (index = 0; index < count && allowedCount < 6; index++) {
    member = Unit_GetFar(unitIds[index]);
    if (member->hp == 0 || member->sleep != 0 || member->stun != 0)
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

/// Heart's leader tests Isaac alone. The slots must match enemies.c row 164:
/// Gotterkanone, P-Storm, P-Vortex, Explosion, Glepnir, EX Gotterkanone,
/// EX Sternbrecher, Ransnetz. None is Psynergy, so nothing about her fighting
/// gives her away. All but P-Storm keep the numbers of the move they
/// replaced (Break, Grand Gaia, Psy Drain, Quick Strike, Avalanche,
/// Rockslide); P-Storm, in Demon Night's slot, is her late finisher.
/// No instant death or Psynergy seal in this solo fight.
enum MysterySlot {
  MYSTERY_GOTTERKANONE = 0,
  MYSTERY_P_STORM = 1,
  MYSTERY_P_VORTEX = 2,
  MYSTERY_EXPLOSION = 3,
  MYSTERY_GLEPNIR = 4,
  MYSTERY_EX_GOTTERKANONE = 5,
  MYSTERY_STERNBRECHER = 6,
  MYSTERY_RANSNETZ = 7
};
/// Two turns must pass between Glepnir's drains; P-Vortex also has a short
/// cooldown.
/// These bits are independent of the stock action cycle and other boss memory.
#define MYSTERY_GLEPNIR_WAIT_SHIFT 4
#define MYSTERY_VORTEX_WAIT_SHIFT 6
#define MYSTERY_BITS ((3u << MYSTERY_GLEPNIR_WAIT_SHIFT) | \
                      (3u << MYSTERY_VORTEX_WAIT_SHIFT))
STATIC_ASSERT((MYSTERY_BITS & BOSS_RESERVED_BITS) == 0);
STATIC_ASSERT((MYSTERY_BITS & BOSS_LAST_AIM_BITS) == 0);

/// Count down tactical-move cooldowns once per round, not once per re-pick.
static void BossAI_MysteryBeginRound(void) {
  struct Unit *unit = BossAI_FindRow(ENEMY_ROW_MYSTERY_LEADER);
  u32 memory;
  u32 glepnirWait;
  u32 vortexWait;
  if (unit == 0)
    return;
  memory = unit->aiActionIndex;
  glepnirWait = (memory >> MYSTERY_GLEPNIR_WAIT_SHIFT) & 3;
  vortexWait = (memory >> MYSTERY_VORTEX_WAIT_SHIFT) & 3;
  if (glepnirWait != 0)
    glepnirWait--;
  if (vortexWait != 0)
    vortexWait--;
  memory &= ~MYSTERY_BITS;
  memory |= (glepnirWait << MYSTERY_GLEPNIR_WAIT_SHIFT) |
            (vortexWait << MYSTERY_VORTEX_WAIT_SHIFT);
  unit->aiActionIndex = memory;
}

/// Only a move that actually executes starts its cooldown.
static void BossAI_MysteryNoteTurn(struct Unit *unit,
                                   struct BattleAction *request) {
  u32 memory = unit->aiActionIndex;
  s32 slot = BossAI_RequestSlot(unit, request);
  if (slot < 0 && request->command != COMMAND_ENEMY_ABILITY &&
      request->command != COMMAND_PSYNERGY && request->command != COMMAND_ATTACK)
    return;
  if (slot == MYSTERY_GLEPNIR) {
    memory &= ~(3u << MYSTERY_GLEPNIR_WAIT_SHIFT);
    memory |= 3u << MYSTERY_GLEPNIR_WAIT_SHIFT;
  } else if (slot == MYSTERY_P_VORTEX) {
    memory &= ~(3u << MYSTERY_VORTEX_WAIT_SHIFT);
    memory |= 2u << MYSTERY_VORTEX_WAIT_SHIFT;
  }
  unit->aiActionIndex = BossAI_RememberAim(memory, request);
}

/// Solo combat: spend most turns dealing damage, not draining an empty PP pool.
/// Below half HP the commander increases pressure rather than gaining a
/// chance to kill Isaac instantly: P-Storm, her finisher, comes only then. A rejected choice always becomes damage.
static s32 BossAI_MysteryChooseSlot(struct Unit *unit,s32 slot,s32 firstPick) {
 u32 memory=unit->aiActionIndex;
 s32 roll=Battle_RandomFar() & 0xff;
 s32 late=unit->hp*2<=unit->hpMax;
 struct BossPartyView view;
 BossAI_ViewParty(&view);
 if (!firstPick) return MYSTERY_RANSNETZ;
 if (view.buffed && ((memory>>MYSTERY_VORTEX_WAIT_SHIFT)&3)==0 && roll<24)
   return MYSTERY_P_VORTEX;
 if (view.pp>=16 && ((memory>>MYSTERY_GLEPNIR_WAIT_SHIFT)&3)==0 &&
     roll>=24 && roll<36) return MYSTERY_GLEPNIR;
 if (late) {
   if (roll<100) return MYSTERY_EXPLOSION;
   if (roll<169) return MYSTERY_STERNBRECHER;
   if (roll<210) return MYSTERY_GOTTERKANONE;
   if (roll<237) return MYSTERY_EX_GOTTERKANONE;
   return MYSTERY_P_STORM;
 }
 if (roll<75) return MYSTERY_EXPLOSION;
 if (roll<132) return MYSTERY_STERNBRECHER;
 if (roll<187) return MYSTERY_GOTTERKANONE;
 if (roll<225) return MYSTERY_RANSNETZ;
 if (roll<245) return MYSTERY_EX_GOTTERKANONE;
 return MYSTERY_RANSNETZ;
}

/// Starts a round for the bosses: their per-round memory is cleared and their
/// view of the party brought up to date. Called once a round by
/// BattleTurnOrder_Sort, before anyone acts.
void BossAI_BeginRound(void) {
  BossAI_KegareBeginRound();
  BossAI_AshBeginRound();
  BossAI_HeartBeginRound();
  BossAI_MysteryBeginRound();
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
  else if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_MYSTERY_LEADER)
    BossAI_MysteryNoteTurn(unit, request);
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
  if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_MYSTERY_LEADER)
    return BossAI_MysteryChooseSlot(unit, slot, firstPick);
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

  if (user->id == ENEMY_ID_FIRST + ENEMY_ROW_KEGARE) {
    if (action->effect == ABILITY_EFFECT_DRAIN_PP ||
        action->effect == ABILITY_EFFECT_SEAL)
      return BossAI_AimAtPp(unitIds, count,
                            action->effect == ABILITY_EFFECT_SEAL);
    return BossAI_KegareChooseTarget(unitIds, targetPositions, count, userId);
  }
  if (user->id == ENEMY_ID_FIRST + ENEMY_ASH_JENNA_VALE &&
      userId > ALLY_MAX) {
    if (action->effect == ABILITY_EFFECT_DRAIN_PP)
      return BossAI_AimAtPp(unitIds, count, 0);
    return BossAI_AshChooseTarget(user, targetPositions, count);
  }
  if (user->id == ENEMY_ID_FIRST + ENEMY_ROW_MYSTERY_LEADER &&
      userId > ALLY_MAX) {
    if (action->effect == ABILITY_EFFECT_DRAIN_PP ||
        action->effect == ABILITY_EFFECT_SEAL)
      return BossAI_AimAtPp(unitIds, count,
                            action->effect == ABILITY_EFFECT_SEAL);
    return BossAI_AimAwayFromLast(user, targetPositions, count);
  }
  if (user->id == ENEMY_ID_FIRST + ENEMY_ROW_HEART && userId > ALLY_MAX)
    return BossAI_HeartChooseTarget(user, action, unitIds, targetPositions,
                                    count);
  return BOSS_AIM_STOCK;
}
