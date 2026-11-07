/// @file
/// Tactical choices for the optional super bosses (Ashfall). Each boss has its
/// own switch, so one can be turned off without touching the others.
// Part of battle.c.

#include "../battle_internal.h"

/// Set a switch to 0 to give that boss back the stock AI.
#define BOSS_AI_KEGARE 1

/// The row of Kegare in gEnemy_Definitions (her unit id is ENEMY_ID_FIRST more).
#define ENEMY_ROW_KEGARE 104

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

/// Unit.aiActionIndex bits Kegare keeps here, among those BattleAIState and
/// the Ash Jenna rush leave unused: 9..7 turns until she may heal again |
/// 6..4 heavy moves in a row.
#define KEGARE_PRESSURE_SHIFT 4
#define KEGARE_HEAL_WAIT_SHIFT 7
#define KEGARE_FIELD_MASK 7u
/// After this many heavy moves in a row she takes a lighter one.
#define KEGARE_PRESSURE_LIMIT 3
/// Her own HP below this percent makes her heal, at most every 5 actions.
#define KEGARE_HEAL_BELOW_PERCENT 35
#define KEGARE_HEAL_WAIT 5
/// Out of 256: how often she ignores her plan and keeps the stock choice.
#define KEGARE_MISTAKE_CHANCE 51

/// Whether anyone in the party is hurt or exposed: HP under half, Defense
/// lowered, or unable to act. Nobody who is down counts.
static s32 BossAI_PartyIsOpen(void) {
  struct BattleWork *work = gBattleWork;
  s32 index;
  struct Unit *member;

  for (index = 0; work->partyUnits[index] != BATTLE_UNIT_LIST_END; index++) {
    if (work->partyUnits[index] == BATTLE_UNIT_REMOVED)
      continue;
    member = Unit_GetFar(work->partyUnits[index]);
    if (member->hp == 0)
      continue;
    if (member->hp * 2 < member->hpMax || member->defenseStage < 0 ||
        member->sleep != 0 || member->stun != 0)
      return 1;
  }
  return 0;
}

/// Kegare's pressure: when someone is hurt or exposed she presses with her
/// heavy moves, but after a few in a row she eases off, she heals herself
/// when low, and one time in five she keeps the stock choice. Only the first
/// pick of a turn is changed; a re-pick after a refused move is the stock
/// cycle's. Returns her place in her action list.
static s32 BossAI_ChooseKegareSlot(struct Unit *unit, s32 slot) {
#if BOSS_AI_KEGARE
  u32 state = unit->aiActionIndex;
  u32 pressure = (state >> KEGARE_PRESSURE_SHIFT) & KEGARE_FIELD_MASK;
  u32 healWait = (state >> KEGARE_HEAL_WAIT_SHIFT) & KEGARE_FIELD_MASK;
  s32 roll = Battle_RandomFar() & 0xff;
  s32 heavy;

  if (healWait != 0)
    healWait--;
  if (unit->hp * 100 < unit->hpMax * KEGARE_HEAL_BELOW_PERCENT &&
      healWait == 0) {
    slot = KEGARE_PLY_WELL;
    healWait = KEGARE_HEAL_WAIT;
  } else if (roll >= KEGARE_MISTAKE_CHANCE) {
    if (pressure >= KEGARE_PRESSURE_LIMIT) {
      slot = (roll & 1) ? KEGARE_HAIL_PRISM : KEGARE_GLACIER;
      if ((roll & 6) == 6)
        slot = KEGARE_DELUGE;
    } else if (BossAI_PartyIsOpen()) {
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

  heavy = slot == KEGARE_FREEZE_PRISM || slot == KEGARE_ICE_MISSILE ||
          slot == KEGARE_FROTH_SPIRAL || slot == KEGARE_ICE_BLESSING;
  if (heavy) {
    if (pressure < KEGARE_FIELD_MASK)
      pressure++;
  } else if (slot != KEGARE_PLY_WELL) {
    pressure = 0;
  }
  state &= ~((KEGARE_FIELD_MASK << KEGARE_PRESSURE_SHIFT) |
             (KEGARE_FIELD_MASK << KEGARE_HEAL_WAIT_SHIFT));
  unit->aiActionIndex = state | (pressure << KEGARE_PRESSURE_SHIFT) |
                        (healWait << KEGARE_HEAL_WAIT_SHIFT);
#endif
  return slot;
}

/// Kegare's aim: more than half the time she goes for the most hurt or
/// exposed of the targets a move can reach (low HP, lowered Defense), and
/// leaves a member who is guarding alone; otherwise the stock random pick.
/// Returns the index in unitIds to aim at, or -1 for the stock pick.
static s32 BossAI_ChooseKegareTarget(const s32 *unitIds, s32 count) {
#if BOSS_AI_KEGARE
  s32 index;
  s32 best = -1;
  s32 bestScore = -10000;
  s32 score;
  struct Unit *member;

  if ((Battle_RandomFar() & 0xff) >= 140)
    return -1;
  for (index = 0; index < count; index++) {
    member = Unit_GetFar(unitIds[index]);
    if (member->hp == 0 || member->hpMax <= 0)
      continue;
    score = 1000 - (member->hp * 1000) / member->hpMax;
    if (member->defenseStage < 0)
      score += 300;
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
