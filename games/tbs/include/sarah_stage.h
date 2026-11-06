#ifndef ALCHEMY_SARAH_STAGE_H
#define ALCHEMY_SARAH_STAGE_H

/// @file
/// Sarah's four fights (Vault, Kalay, Tolbi, Lalivero): enemy row 135 holds the
/// strongest, and the earlier fights replace its numbers when the battle sets
/// the unit up (BattleUnit_Set) and when it pays out (BattleSpoils).

#include "flags.h"

#define ENEMY_ROW_SARAH 135

struct SarahStage {
  u8 level;
  u8 turns;
  u16 hp;
  u16 atk;
  u16 def;
  u16 agi;
  u16 luck;
  u16 coins;
  u16 experience;
  /// Her eight moves, the common ones first (her row's ACTION_STRATEGY_FALLING).
  u16 abilities[8];
};

static const struct SarahStage gSarahStages[4] = {
    // Vault: introduces her and tests basic combat; a party under level 5
    // struggles, one at 7 wins (party levels 5 to 7).
    {7, 1, 520, 68, 26, 42, 12, 150, 80,
     // Plain shots: Attack and Quick Strike, Shuriken to finish.
     {1, 1, 1, 163, 1, 163, 177, 163}},
    // Kalay: party coordination and Djinn management (14 to 16).
    {16, 2, 1500, 150, 58, 85, 20, 500, 260,
     // Adds Rapid Smash, Vorpal Slash and Barrage (her gun): focus and cover.
     {1, 163, 177, 234, 1, 228, 234, 225}},
    // Tolbi: defensive play and tactical decisions (19 to 22).
    {22, 2, 3000, 235, 90, 115, 28, 900, 520,
     // Adds Cyclone Slash, Sonic Smash and Helm Splitter: guard, wait, choose
     // the moment.
     {1, 163, 225, 228, 234, 232, 235, 162}},
    // Lalivero: the final, challenging duel (25 to 28).
    {28, 2, 6000, 335, 125, 160, 36, 1500, 900,
     // All of it, Annihilation last.
     {1, 225, 234, 228, 235, 232, 162, 178}},
};

#endif
