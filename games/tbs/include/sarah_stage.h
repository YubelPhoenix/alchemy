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
};

static const struct SarahStage gSarahStages[4] = {
    // Vault: introduces her and tests basic combat (levels 5 to 7).
    {6, 1, 380, 58, 22, 36, 10, 150, 60},
    // Kalay: party coordination and Djinn management (14 to 16).
    {15, 1, 1100, 135, 52, 78, 18, 500, 200},
    // Tolbi: defensive play and tactical decisions (19 to 22).
    {21, 2, 2200, 215, 82, 108, 26, 900, 400},
    // Lalivero: the final, challenging duel (25 to 28).
    {27, 2, 4200, 310, 115, 150, 34, 1500, 700},
};

#endif
