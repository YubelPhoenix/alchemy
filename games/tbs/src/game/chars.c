/// @file
/// The eight party members' growth curves, element bonuses, starting levels
/// and starting equipment.

#include "game.h"
#include "item_ids.h"

// clang-format off
const struct CharacterDefinition gCharacter_DefinitionTable[] = {
    // Isaac
    {
        .hp = {30, 193, 354, 515, 676, 837},
        .pp = {20, 74, 120, 156, 193, 230},
        .atk = {13, 98, 185, 270, 357, 442},
        .def = {6, 39, 70, 104, 137, 169},
        .agi = {8, 86, 163, 241, 318, 396},
        .luck = {3, 3, 3, 3, 3, 3},
        .elementBonus = {54, 3, 1, 2},
        .startingLevel = 1,
        .items = {ITEM_MACHETE, ITEM_COTTON_SHIRT, ITEM_PADDED_GLOVES, ITEM_HERB, ITEM_HERB, ITEM_HERB},
    },
    // Garet
    {
        .hp = {33, 222, 407, 592, 777, 963},
        .pp = {18, 72, 118, 154, 190, 226},
        .atk = {11, 83, 156, 228, 301, 373},
        .def = {8, 50, 92, 134, 176, 218},
        .agi = {6, 67, 127, 187, 247, 307},
        .luck = {2, 2, 2, 2, 2, 2},
        .elementBonus = {1, 2, 54, 3},
        .startingLevel = 1,
        .items = {ITEM_MACHETE, ITEM_COTTON_SHIRT, ITEM_PADDED_GLOVES, ITEM_HERB, ITEM_HERB},
    },
    // Ivan
    {
        .hp = {28, 153, 280, 407, 535, 661},
        .pp = {24, 110, 180, 235, 290, 346},
        .atk = {8, 68, 130, 190, 249, 310},
        .def = {4, 33, 62, 90, 118, 147},
        .agi = {11, 106, 201, 296, 391, 486},
        .luck = {4, 4, 4, 4, 4, 4},
        .elementBonus = {2, 1, 3, 54},
        .startingLevel = 4,
        .items = {55, 90, 136, 166, ITEM_HERB},
    },
    // Mia
    {
        .hp = {29, 182, 333, 485, 636, 789},
        .pp = {23, 104, 169, 220, 273, 325},
        .atk = {9, 71, 135, 198, 260, 323},
        .def = {5, 40, 73, 108, 141, 176},
        .agi = {7, 82, 155, 228, 302, 376},
        .luck = {5, 5, 5, 5, 5, 5},
        .elementBonus = {3, 54, 2, 1},
        .startingLevel = 10,
        .items = {57, 104, 128, 157, ITEM_HERB, ITEM_ANTIDOTE, ITEM_ELIXIR},
    },
    // Felix
    {},
    // Jenna
    {
        .hp = {29, 182, 334, 486, 638, 790},
        .pp = {19, 80, 130, 170, 210, 250},
        .atk = {10, 81, 153, 224, 295, 366},
        .def = {7, 37, 68, 100, 131, 163},
        .agi = {9, 84, 160, 236, 312, 388},
        .luck = {4, 4, 4, 4, 4, 4},
        .elementBonus = {1, 2, 54, 3},
        .startingLevel = 1,
        .items = {55, 103, ITEM_PADDED_GLOVES, ITEM_HERB},
    },
    // Sheba
    {},
    // Piers
    {},
};
// clang-format on
