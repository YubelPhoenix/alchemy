/// @file
/// "???"'s Kaiserdammerung (Ashfall): Judgment's summon as she casts it, compiled
/// from parts/judgment.c again with JUDGMENT_DARK. Her figure
/// (SPRITE_MYSTERY_JUDGMENT) rises in Judgment's place, and every backdrop it
/// loads, the violet sky and the lands the blast sweeps over, is sunk in
/// darkness (Judgment_Darken). It sits in the ROM tail, as perfecti.c does,
/// since the battle-animation bank has no room; the bank's
/// BattleAnim_RunJudgment hands an enemy's call to it.

#define JUDGMENT_DARK
#define BattleAnim_RunJudgment BattleAnim_RunJudgmentDark
#include "parts/judgment.c"
