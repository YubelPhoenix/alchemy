/// @file
/// The 104 encounter zones, by zone number: the zone names in the comments
/// say where each is used.

#include "field/encounter_zone.h"

// clang-format off
const struct EncounterZone gEncounterZones[] = {
    // No encounters
    {0},
    // Sol Sanctum Corridor
    {
        .rate = 37,
        .level = 1,
        .enemies = {10, 17, 24, 31},
        .weights = {4, 8, 8, 4},
    },
    // SolSanctumReliefs (entrances 1, 2)
    {
        .rate = 35,
        .level = 1,
        .enemies = {10, 14, 27, 25},
        .weights = {8, 4, 4, 8},
    },
    // SolSanctumReliefs (entrances 3, 6, 7)
    {
        .rate = 35,
        .level = 1,
        .enemies = {21, 36, 26, 25},
        .weights = {8, 8, 4, 4},
    },
    // Sol Sanctum Maze
    {
        .rate = 35,
        .level = 1,
        .enemies = {37, 34, 35, 23},
        .weights = {4, 4, 8, 8},
    },
    // SolSanctumReliefs (entrance 10)
    {
        .rate = 35,
        .level = 2,
        .enemies = {51, 23, 7, 12},
        .weights = {12, 8, 4, 4},
    },
    // Sol Sanctum Luna Sol Rooms
    {
        .rate = 35,
        .level = 2,
        .enemies = {14, 26, 13, 51},
        .weights = {4, 4, 12, 8},
    },
    // World Map: terrain kind 1, grassland and beach
    {
        .rate = 25,
        .level = 3,
        .enemies = {7, 54, 31, 21, 36, 24, 33, 60},
        .weights = {2, 2, 3, 3, 4, 4, 4, 3},
    },
    // World Map: terrain kind 1, forest
    {
        .rate = 9,
        .level = 3,
        .enemies = {35, 55, 64, 11, 32, 12, 59, 57},
        .weights = {2, 2, 2, 2, 3, 7, 2, 3},
    },
    // Goma Cave Pond
    {
        .rate = 30,
        .level = 4,
        .enemies = {26, 52, 16, 65, 70},
        .weights = {3, 3, 9, 3, 6},
    },
    // Goma Cave Pillar
    {
        .rate = 30,
        .level = 5,
        .enemies = {63, 10, 72, 71, 86, 80, 127},
        .weights = {2, 2, 2, 2, 8, 5, 2},
    },
    // GomaCaveStream
    {
        .rate = 30,
        .level = 5,
        .enemies = {90, 22, 80, 142, 89, 75, 84},
        .weights = {2, 2, 5, 2, 8, 8, 14},
    },
    // Event battles: Vale, Vault, World Map
    {
        .enemies = {1, 2, 3, 4, 5, 29, 28, 6},
        .weights = {10, 10, 10, 10, 10, 10, 1, 1},
    },
    // World Map: terrain kind 2, grassland and beach
    {
        .rate = 25,
        .level = 6,
        .enemies = {65, 89, 57, 69, 95, 62, 64, 100},
        .weights = {4, 4, 4, 4, 4, 2, 2, 2},
    },
    // World Map: terrain kind 2, forest
    {
        .rate = 9,
        .level = 6,
        .enemies = {60, 83, 24, 87, 164, 79, 65, 92},
        .weights = {1, 1, 1, 1, 1, 2, 2, 2},
    },
    // KolimaTunnel
    {
        .rate = 35,
        .level = 6,
        .enemies = {32, 79, 72, 59, 126, 25, 95, 92},
        .weights = {1, 2, 2, 1, 1, 5, 5, 5},
    },
    // Kolima Forest Bridge
    {
        .rate = 40,
        .level = 6,
        .enemies = {34, 73, 78, 61, 77, 62, 79, 129},
        .weights = {10, 8, 6, 4, 2, 1, 1, 1},
    },
    // Kolima Forest Clearing
    {
        .rate = 40,
        .level = 7,
        .enemies = {125, 90, 77, 124, 104, 101, 126, 135},
        .weights = {4, 8, 6, 6, 4, 2, 1, 1},
    },
    // Kolima Forest River
    {
        .rate = 40,
        .level = 7,
        .enemies = {74, 71, 21, 24, 54, 98, 120, 149},
        .weights = {2, 4, 6, 6, 8, 6, 2, 1},
    },
    // Kolima Forest Tree
    {
        .rate = 40,
        .level = 7,
        .enemies = {196, 70, 102, 99, 106, 103, 95, 24},
        .weights = {1, 2, 4, 6, 8, 8, 4, 2},
    },
    // Tret Tree Branch (entrances 1 to 3)
    {
        .rate = 45,
        .level = 7,
        .enemies = {74, 78, 98, 35, 96, 106, 70, 132},
        .weights = {2, 2, 6, 2, 4, 6, 3, 1},
    },
    // Tret Tree Interiors (entrances 1, 11, 16, 21 to 29)
    {
        .rate = 45,
        .level = 7,
        .enemies = {94, 101, 31, 71, 103, 86, 35, 189},
        .weights = {1, 2, 6, 5, 5, 4, 2, 1},
    },
    // Tret Tree Interiors (entrances 2 to 5, 12, 13, 31, 32)
    {
        .rate = 45,
        .level = 8,
        .enemies = {148, 62, 106, 32, 54, 31, 144, 132},
        .weights = {1, 2, 4, 6, 6, 4, 3, 2},
    },
    // Tret Tree Branch (any entrance)
    {
        .rate = 45,
        .level = 8,
        .enemies = {145, 152, 77, 59, 36, 132, 80, 93},
        .weights = {1, 1, 4, 6, 3, 6, 4, 4},
    },
    // Tret Tree Interiors (entrances 6 to 9, 14, 51 to 59)
    {
        .rate = 45,
        .level = 8,
        .enemies = {31, 190, 141, 136, 124, 61, 132, 73},
        .weights = {1, 1, 2, 3, 4, 6, 10, 8},
    },
    // BilibinCaveRapier (any entrance)
    {
        .rate = 30,
        .level = 8,
        .enemies = {142, 60, 143, 126, 83, 53, 101, 152},
        .weights = {6, 6, 4, 4, 2, 2, 1, 1},
    },
    // BilibinCaveIce (any entrance)
    {
        .rate = 30,
        .level = 8,
        .enemies = {142, 86, 183, 100, 97, 63, 129, 70},
        .weights = {2, 2, 2, 4, 4, 5, 7, 7},
    },
    // BilibinCaveRapier (entrances 5, 6)
    {
        .rate = 30,
        .level = 9,
        .enemies = {37, 62, 102, 57, 161, 97, 98, 51},
        .weights = {1, 1, 1, 1, 1, 2, 2, 2},
    },
    // BilibinCaveIce (entrance 5)
    {
        .rate = 30,
        .level = 9,
        .enemies = {133, 127, 94, 90, 206, 153, 64, 131},
        .weights = {1, 1, 1, 1, 1, 2, 2, 2},
    },
    // World Map: terrain kind 21, snowfield (behavior 5)
    {
        .rate = 25,
        .level = 9,
        .enemies = {145, 185, 71, 69, 148},
        .weights = {3, 3, 5, 5, 5},
    },
    // World Map: terrain kind 21, snowfield (behavior 6)
    {
        .rate = 9,
        .level = 9,
        .enemies = {122, 186, 96, 125, 149},
        .weights = {2, 2, 4, 4, 4},
    },
    // Mercury Lighthouse Entrance, MercuryLighthouseLower
    {
        .rate = 40,
        .level = 9,
        .enemies = {56, 142, 104, 163, 75, 72, 53, 141},
        .weights = {6, 4, 2, 1, 4, 4, 2, 6},
    },
    // MercuryLighthouseLower and MercuryLighthouseMiddle
    {
        .rate = 40,
        .level = 9,
        .enemies = {124, 180, 129, 50, 65, 135, 78, 134},
        .weights = {2, 1, 2, 2, 4, 4, 6, 8},
    },
    // MercuryLighthouseMiddle and MercuryLighthouseUpper
    {
        .rate = 40,
        .level = 10,
        .enemies = {72, 185, 75, 104, 88, 123, 142, 122},
        .weights = {1, 1, 2, 2, 3, 4, 8, 8},
    },
    // MercuryLighthouseUpper and MercuryLighthouseExterior
    {
        .rate = 40,
        .level = 11,
        .enemies = {135, 124, 94, 222, 93, 104, 150, 154},
        .weights = {1, 2, 2, 1, 2, 4, 8, 8},
    },
    // MercuryLighthouseExterior (entrances 3, 4)
    {
        .rate = 40,
        .level = 11,
        .enemies = {121, 150, 93, 230, 161, 152, 146, 84},
        .weights = {1, 2, 2, 1, 2, 4, 8, 8},
    },
    // Event battles: Tret Tree, Mercury Lighthouse
    {
        .enemies = {106, 107, 108},
        .weights = {10, 10, 10},
    },
    // World Map: terrain kind 31, grassland
    {
        .rate = 20,
        .level = 11,
        .enemies = {162, 120, 81, 195},
        .weights = {3, 3, 3, 3},
    },
    // World Map: terrain kind 31, forest
    {
        .rate = 9,
        .level = 11,
        .enemies = {68, 80, 149, 207},
        .weights = {1, 1, 1, 1},
    },
    // FuchinFallsCaveEntrance and FuchinFallsCaveZephyr
    {
        .rate = 38,
        .level = 11,
        .enemies = {142, 164, 193, 94, 71, 131, 90, 234},
        .weights = {4, 4, 4, 8, 6, 4, 2, 1},
    },
    // FuchinFallsCaveDragonsEye
    {
        .rate = 38,
        .level = 11,
        .enemies = {234, 98, 83, 186, 120, 166, 167, 122},
        .weights = {1, 2, 2, 3, 6, 6, 3, 2},
    },
    // FuchinFallsCaveDragonStatue
    {
        .rate = 38,
        .level = 11,
        .enemies = {106, 186, 166, 86, 81, 104, 145, 92},
        .weights = {1, 1, 2, 3, 4, 4, 6, 8},
    },
    // MogallForestSign
    {
        .rate = 42,
        .level = 11,
        .enemies = {195, 75, 131, 94, 190, 187, 82, 208},
        .weights = {6, 6, 6, 3, 2, 1, 1, 1},
    },
    // MogallForestQuartz
    {
        .rate = 42,
        .level = 12,
        .enemies = {129, 191, 86, 131, 134, 99, 126, 205},
        .weights = {1, 1, 3, 6, 6, 3, 1, 1},
    },
    // MogallForestKillerApe
    {
        .rate = 42,
        .level = 12,
        .enemies = {78, 232, 125, 152, 84, 90, 123, 79},
        .weights = {1, 1, 2, 2, 3, 4, 5, 5},
    },
    // World Map: terrain kind 3, grassland, desert and beach
    {
        .rate = 25,
        .level = 12,
        .enemies = {94, 90, 207, 186, 189, 223},
        .weights = {3, 3, 1, 3, 1, 1},
    },
    // World Map: terrain kind 3, forest
    {
        .rate = 9,
        .level = 12,
        .enemies = {161, 193, 196, 256, 194, 81},
        .weights = {1, 1, 2, 1, 2, 2},
    },
    // AltinPeakRailTunnel, AltinPeakSecondWaterBeast, AltinPeakSouthEntrance
    {
        .rate = 45,
        .level = 12,
        .enemies = {150, 134, 193, 120, 192, 162, 153, 255},
        .weights = {6, 6, 4, 2, 1, 1, 1, 1},
    },
    // AltinPeakThirdWaterBeast and AltinPeakPool
    {
        .rate = 45,
        .level = 13,
        .enemies = {102, 257, 187, 134, 160, 143, 152, 94},
        .weights = {1, 1, 2, 4, 3, 4, 2, 2},
    },
    // AltinPeakSpritz, AltinPeakJunction, AltinPeakFallingRocks and AltinPeakWestExit
    {
        .rate = 42,
        .level = 13,
        .enemies = {166, 231, 142, 149, 143, 102, 144, 164},
        .weights = {1, 1, 2, 3, 4, 4, 8, 8},
    },
    // LamakanDesertEast
    {
        .rate = 40,
        .level = 13,
        .enemies = {202, 88, 193, 150, 126, 195, 94, 225},
        .weights = {5, 5, 4, 3, 3, 2, 1, 1},
    },
    // LamakanDesertSmog
    {
        .rate = 40,
        .level = 14,
        .enemies = {230, 127, 102, 129, 205, 167, 226, 268},
        .weights = {1, 2, 3, 6, 6, 4, 2, 1},
    },
    // LamakanDesertManticore
    {
        .rate = 40,
        .level = 14,
        .enemies = {101, 189, 259, 129, 167, 187, 183, 182},
        .weights = {1, 1, 1, 2, 3, 4, 4, 5},
    },
    // Event battles: Mogall Forest, Altin Peak, Lamakan Desert
    {
        .enemies = {138, 139, 157, 158, 169, 170},
        .weights = {10, 10, 10, 10, 10, 10},
    },
    // World Map: terrain kind 4, grassland, desert and beach
    {
        .rate = 25,
        .level = 15,
        .enemies = {195, 153, 136, 148, 226, 122, 232, 268},
        .weights = {4, 4, 4, 4, 4, 2, 2, 2},
    },
    // World Map: terrain kind 4, forest
    {
        .rate = 9,
        .level = 15,
        .enemies = {161, 142, 154, 269, 233, 164, 226, 207},
        .weights = {2, 2, 2, 2, 3, 4, 4, 4},
    },
    // ValeCaveKite (entrances 1 to 4)
    {
        .rate = 40,
        .level = 15,
        .enemies = {162, 181, 141, 233, 131, 146, 227, 277},
        .weights = {6, 6, 6, 4, 4, 1, 1, 1},
    },
    // ValeCaveKite (entrances 8 to 10)
    {
        .rate = 40,
        .level = 15,
        .enemies = {222, 162, 184, 223, 181, 126, 120, 271},
        .weights = {4, 4, 4, 6, 6, 2, 2, 2},
    },
    // ValeCaveLogs (entrances 1 to 3)
    {
        .rate = 40,
        .level = 15,
        .enemies = {126, 153, 284, 143, 193, 187, 154, 229},
        .weights = {2, 2, 2, 3, 3, 5, 5, 5},
    },
    // ValeCaveLogs (entrances 4, 5)
    {
        .rate = 40,
        .level = 15,
        .enemies = {164, 184, 282, 189, 186, 204, 231, 227},
        .weights = {1, 1, 1, 2, 2, 5, 5, 5},
    },
    // VaultCavePassage
    {
        .rate = 40,
        .level = 16,
        .enemies = {235, 202, 182, 166, 226, 165, 250, 259},
        .weights = {8, 8, 8, 4, 4, 4, 2, 2},
    },
    // VaultCaveVambrace and VaultCaveMouth
    {
        .rate = 40,
        .level = 16,
        .enemies = {208, 254, 282, 145, 180, 152, 201, 181},
        .weights = {2, 2, 2, 4, 4, 4, 8, 8},
    },
    // Event battles: Tolbi ship
    {
        .level = 17,
        .enemies = {210, 211, 212, 213},
        .weights = {10, 10, 10, 10},
    },
    // Event battles: Crossbone Isle
    {
        .level = 17,
        .enemies = {291, 292, 293, 294},
        .weights = {10, 10, 10, 10},
    },
    // World Map: terrain kind 5, grassland, desert and beach
    {
        .rate = 25,
        .level = 18,
        .enemies = {230, 202, 193, 182, 223, 270, 279, 315},
        .weights = {6, 6, 6, 6, 3, 3, 3, 3},
    },
    // World Map: terrain kind 5, forest
    {
        .rate = 9,
        .level = 18,
        .enemies = {185, 261, 259, 320, 194, 285, 190, 256},
        .weights = {3, 3, 3, 3, 6, 6, 6, 6},
    },
    // AltmillerCaveEntrance
    {
        .rate = 40,
        .level = 17,
        .enemies = {194, 223, 189, 192, 162, 236, 225, 277},
        .weights = {6, 6, 4, 4, 4, 2, 1, 1},
    },
    // AltmillerCaveBabi
    {
        .rate = 40,
        .level = 17,
        .enemies = {182, 260, 191, 261, 222, 259, 195, 280},
        .weights = {4, 4, 6, 6, 4, 4, 2, 1},
    },
    // AltmillerCaveVialChest
    {
        .rate = 40,
        .level = 18,
        .enemies = {220, 181, 278, 270, 255, 262, 260, 282},
        .weights = {3, 3, 4, 6, 6, 4, 2, 1},
    },
    // AltmillerCaveSquall
    {
        .rate = 40,
        .level = 18,
        .enemies = {284, 277, 207, 250, 203, 191, 181, 272},
        .weights = {2, 2, 4, 4, 6, 5, 5, 3},
    },
    // AltmillerCaveCookieChest
    {
        .rate = 40,
        .level = 18,
        .enemies = {282, 278, 257, 189, 285, 204, 194, 231},
        .weights = {2, 2, 3, 3, 4, 6, 6, 4},
    },
    // AltmillerCaveDraught (entrances 50, 51)
    {
        .rate = 40,
        .level = 18,
        .enemies = {227, 201, 274, 251, 279, 186, 271, 269},
        .weights = {1, 1, 1, 2, 2, 4, 6, 6},
    },
    // Event battles: Colosso
    {
        .level = 19,
        .enemies = {238, 239, 240, 241, 242, 243},
        .weights = {10, 10, 10, 10, 10, 10},
    },
    // GondowanCave (any entrance)
    {
        .rate = 30,
        .level = 19,
        .enemies = {259, 313, 235, 196, 254, 226, 274, 227},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // GondowanCaveRiver (any entrance)
    {
        .rate = 30,
        .level = 20,
        .enemies = {262, 332, 227, 311, 235, 275, 310, 255},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // GondowanCaveRiver (entrances 1, 2)
    {
        .rate = 30,
        .level = 20,
        .enemies = {235, 323, 205, 282, 316, 285, 257, 314},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // GondowanCave (entrances 1 to 3)
    {
        .rate = 30,
        .level = 20,
        .enemies = {229, 331, 274, 226, 222, 233, 253, 259},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // LunpaFortressCave (entrances 1, 2)
    {
        .rate = 35,
        .level = 21,
        .enemies = {255, 254, 312, 339},
        .weights = {2, 2, 2, 2},
    },
    // LunpaFortressCave (any entrance)
    {
        .rate = 35,
        .level = 21,
        .enemies = {260, 254, 232, 338},
        .weights = {2, 2, 2, 2},
    },
    // LunpaFortressToadonpa (entrances 1, 2)
    {
        .rate = 35,
        .level = 21,
        .enemies = {235, 322, 310, 335},
        .weights = {2, 2, 2, 2},
    },
    // World Map: terrain kind 6, grassland, desert and beach
    {
        .rate = 25,
        .level = 22,
        .enemies = {274, 332, 330, 311, 272, 255, 251, 339},
        .weights = {4, 4, 3, 3, 3, 3, 3, 3},
    },
    // World Map: terrain kind 6, forest
    {
        .rate = 9,
        .level = 22,
        .enemies = {275, 341, 269, 332, 227, 268, 334, 277},
        .weights = {2, 2, 3, 3, 3, 4, 4, 4},
    },
    // SuhallaDesertNorth
    {
        .rate = 40,
        .level = 22,
        .enemies = {251, 284, 314, 260, 256, 269, 335, 338},
        .weights = {4, 4, 4, 5, 3, 4, 2, 2},
    },
    // SuhallaDesertSouth
    {
        .rate = 40,
        .level = 22,
        .enemies = {260, 261, 342, 278, 314, 273, 330, 221},
        .weights = {2, 2, 2, 4, 3, 4, 4, 4},
    },
    // Event battles: Crossbone Isle
    {
        .level = 17,
        .enemies = {296, 297, 298, 300, 301, 302},
        .weights = {10, 10, 10, 10, 10, 10},
    },
    // SuhallaGateDew (entrances 1, 2)
    {
        .rate = 30,
        .level = 23,
        .enemies = {330, 284, 278, 256, 335, 313, 323, 340},
        .weights = {6, 6, 6, 3, 3, 2, 2, 2},
    },
    // SuhallaGateDew (any entrance)
    {
        .rate = 30,
        .level = 24,
        .enemies = {341, 312, 311, 262, 315, 275, 259, 282},
        .weights = {2, 3, 3, 6, 6, 3, 3, 3},
    },
    // GatewayCave (entrances 1, 2)
    {
        .rate = 30,
        .level = 24,
        .enemies = {272, 337, 332, 316, 321, 331, 334, 259},
        .weights = {1, 1, 2, 2, 2, 3, 3, 3},
    },
    // GatewayCave (any entrance)
    {
        .rate = 30,
        .level = 24,
        .enemies = {279, 341, 282, 310, 260, 278, 320, 323},
        .weights = {2, 2, 3, 3, 3, 6, 6, 6},
    },
    // VenusLighthouseGroundFloor (any entrance)
    {
        .rate = 40,
        .level = 25,
        .enemies = {334, 335, 313, 269, 330},
        .weights = {4, 4, 4, 4, 4},
    },
    // VenusLighthouseGroundFloor (entrances 20 to 26, 30 to 32)
    {
        .rate = 40,
        .level = 25,
        .enemies = {340, 277, 329, 259, 270},
        .weights = {4, 4, 4, 4, 4},
    },
    // BabiLighthouseEntry, BabiLighthouseLuff, BabiLighthouseStoneDoor, TunnelRuinsLadyStatues (entrances 1 to 3)
    {
        .rate = 35,
        .level = 25,
        .enemies = {273, 311, 279, 320, 278, 333, 274, 285},
        .weights = {6, 6, 6, 4, 4, 4, 2, 2},
    },
    // TunnelRuinsGreatStatue, TunnelRuinsLadyStatues (entrances 8 to 11)
    {
        .rate = 35,
        .level = 25,
        .enemies = {269, 331, 316, 341, 328, 339, 332, 330},
        .weights = {3, 3, 4, 6, 6, 4, 3, 3},
    },
    // TunnelRuinsLadyStatues (entrances 12, 15 to 17)
    {
        .rate = 35,
        .level = 26,
        .enemies = {277, 274, 269, 311, 321, 270, 280, 334},
        .weights = {3, 3, 3, 4, 4, 4, 6, 6},
    },
    // VenusLighthouseFirstFloor (any entrance)
    {
        .rate = 34,
        .level = 27,
        .enemies = {339, 331, 317, 330, 337, 340, 321, 338},
        .weights = {4, 4, 3, 3, 3, 3, 2, 2},
    },
    // VenusLighthouseFirstFloor (entrances 19, 20), VenusLighthouseSecondFloor
    {
        .rate = 32,
        .level = 28,
        .enemies = {334, 333, 339, 331, 342, 343, 337, 323},
        .weights = {3, 3, 4, 4, 3, 3, 2, 2},
    },
    // VenusLighthouseThirdFloor
    {
        .rate = 30,
        .level = 29,
        .enemies = {320, 339, 323, 319, 343, 334, 342, 337},
        .weights = {2, 2, 3, 3, 4, 4, 3, 3},
    },
    // VenusLighthouseFourthFloor
    {
        .rate = 30,
        .level = 30,
        .enemies = {344, 338, 339, 342, 340, 343, 337, 341},
        .weights = {2, 2, 2, 3, 3, 3, 4, 4},
    },
    // Event battles: Suhalla Desert, Venus Lighthouse Aerie, World Map
    {
        .enemies = {347, 346, 264, 265, 266, 287, 288, 289},
        .weights = {10, 10, 30, 10, 10, 80, 10, 10},
    },
    // Mimic chests
    {
        .enemies = {350, 351, 352, 353, 354, 355, 356, 357},
        .weights = {10, 10, 10, 10, 10, 10, 10, 10},
    },
    // Venus Djinn battles
    {
        .enemies = {360, 360, 360, 361, 361, 361, 362},
        .weights = {10, 10, 10, 10, 10, 10, 10},
    },
    // Mercury Djinn battles
    {
        .enemies = {365, 365, 365, 366, 367, 367, 368},
        .weights = {10, 10, 10, 10, 10, 10, 10},
    },
    // Mars Djinn battles
    {
        .enemies = {371, 371, 372, 372, 372, 373, 373},
        .weights = {10, 10, 10, 10, 10, 10, 10},
    },
    // Jupiter Djinn battles
    {
        .enemies = {376, 376, 377, 377, 377, 378, 379},
        .weights = {10, 10, 10, 10, 10, 10, 10},
    },
    // Mia's first interlude near Imil (slot 0: three hired thieves, slot 1:
    // the Thief Chief and a hired thief)
    {
        .enemies = {380, 381, 380, 380, 380, 380, 380, 380},
        .weights = {10, 10, 10, 10, 10, 10, 10, 10},
    },
    // Mercury Lighthouse: slot 0 Mia alone against Menardi, slot 1 Isaac
    // alone against Mia, slot 2 Ondra in Tolbi, slot 3 Heart in Kolima, slot 4
    // Ash Jenna in Vale, slot 5 Ash Jenna at Suhalla Gate
    {
        .enemies = {382, 383, 384, 385, 386, 387, 382, 382},
        .weights = {10, 10, 10, 10, 10, 10, 10, 10},
    },
};
// clang-format on
