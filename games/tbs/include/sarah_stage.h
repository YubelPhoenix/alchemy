#ifndef ALCHEMY_SARAH_STAGE_H
#define ALCHEMY_SARAH_STAGE_H

/// @file
/// Sarah's four fights (Vault, Kalay, Tolbi, Lalivero): enemy row 135 holds the
/// strongest, and the earlier fights replace its numbers when the battle sets
/// the unit up (BattleUnit_Set) and when it pays out (BattleSpoils).

#include "flags.h"
#include "ability_ids.h"

#define ENEMY_ROW_SARAH 135

struct SarahStage {
  u8 level;
  u8 turns;   ///< actions a round
  u16 hp;
  u16 atk;
  u16 def;
  u16 agi;
  u16 luck;
  u16 coins;
  u16 experience;
  /// Her eight moves, the common ones first (her row's ACTION_STRATEGY_FALLING).
  u16 abilities[8];
  u16 potions; ///< Potions she carries (BattleEnemy_ChooseAction drinks them)
};

/// She is only human, so she cannot match a party's Djinn, summons and
/// Psynergy; she out-fights and out-lasts them instead. Her pike techniques
/// break armour (Piercing Thrust), weapons (Disarm) and concentration (Haft
/// Strike), reach three foes (Sweeping Arc) and land one heavy blow
/// (Vaulting Strike); when badly hurt she drinks a Potion, which heals her a
/// share of her HP (target_exec.c); and summons take half their usual share of
/// her HP (target_exec.c). Every move here costs no PP: an enemy with none
/// skips Psynergy, which left Quick Strike, Helm Splitter, Death Plunge and
/// Annihilation unused in her old lists.
/// Tuned against a level-33 Warden Isaac (651 HP, Attack 408, Defense 236,
/// Agility 156) for the last fight, scaled back by level for the others.
static const struct SarahStage gSarahStages[4] = {
    // Vault: introduces her and tests basic combat; a party under level 5
    // struggles, one at 7 wins (party levels 5 to 7). Unchanged in play:
    // Attack where Quick Strike was, which she could never use.
    {7, 1, 520, 68, 26, 42, 12, 150, 80,
     {ABILITY_ATTACK, ABILITY_ATTACK, ABILITY_ATTACK, ABILITY_ATTACK,
      ABILITY_ATTACK, ABILITY_ATTACK, 228, ABILITY_ATTACK},
     0},
    // Kalay: three Adepts near level 15. About eight rounds; her blows take
    // near 30 percent of a member's HP.
    {16, 2, 1600, 220, 70, 90, 20, 500, 260,
     {ABILITY_ATTACK, ABILITY_PIERCING_THRUST, ABILITY_ATTACK,
      ABILITY_HAFT_STRIKE, ABILITY_SWEEPING_ARC, ABILITY_ATTACK,
      ABILITY_DISARM, ABILITY_VAULTING_STRIKE},
     1},
    // Tolbi: four Adepts near level 21. About nine rounds.
    {23, 2, 3400, 320, 110, 130, 28, 900, 520,
     {ABILITY_PIERCING_THRUST, ABILITY_ATTACK, ABILITY_SWEEPING_ARC,
      ABILITY_HAFT_STRIKE, ABILITY_DISARM, ABILITY_PIERCING_THRUST,
      ABILITY_VAULTING_STRIKE, ABILITY_SWEEPING_ARC},
     2},
    // Lalivero, after Venus Lighthouse: the final duel against a full party
    // near level 33. Three actions a round; about ten rounds.
    {34, 3, 7000, 500, 180, 200, 40, 1500, 900,
     {ABILITY_PIERCING_THRUST, ABILITY_SWEEPING_ARC, ABILITY_HAFT_STRIKE,
      ABILITY_DISARM, ABILITY_VAULTING_STRIKE, ABILITY_SWEEPING_ARC,
      ABILITY_PIERCING_THRUST, ABILITY_VAULTING_STRIKE},
     3},
};
#endif
