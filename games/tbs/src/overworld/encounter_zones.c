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
        .enemies = {10, 17, 24, 25},
        .weights = {4, 8, 8, 4},
    },
    // SolSanctumReliefs (entrances 1, 2)
    {
        .rate = 35,
        .level = 1,
        .enemies = {10, 14, 25, 21},
        .weights = {8, 4, 4, 8},
    },
    // SolSanctumReliefs (entrances 3, 6, 7)
    {
        .rate = 35,
        .level = 1,
        .enemies = {26, 25, 23, 22},
        .weights = {8, 8, 4, 4},
    },
    // Sol Sanctum Maze
    {
        .rate = 35,
        .level = 1,
        .enemies = {14, 7, 9, 10},
        .weights = {4, 4, 8, 8},
    },
    // SolSanctumReliefs (entrance 10)
    {
        .rate = 35,
        .level = 2,
        .enemies = {16, 37, 10, 22},
        .weights = {12, 8, 4, 4},
    },
    // Sol Sanctum Luna Sol Rooms
    {
        .rate = 35,
        .level = 2,
        .enemies = {7, 37, 32, 23},
        .weights = {4, 4, 12, 8},
    },
    // World Map: terrain kind 1, grassland and beach
    {
        .rate = 25,
        .level = 3,
        .enemies = {31, 21, 36, 24, 18, 52, 53, 55},
        .weights = {2, 2, 3, 3, 4, 4, 4, 3},
    },
    // World Map: terrain kind 1, forest
    {
        .rate = 9,
        .level = 3,
        .enemies = {35, 55, 11, 32, 9, 25, 52, 16},
        .weights = {2, 2, 2, 2, 3, 7, 2, 3},
    },
    // Goma Cave Pond
    {
        .rate = 30,
        .level = 4,
        .enemies = {26, 52, 16, 65, 60},
        .weights = {3, 3, 9, 3, 6},
    },
    // Goma Cave Pillar
    {
        .rate = 30,
        .level = 5,
        .enemies = {50, 16, 54, 73, 61, 59, 21},
        .weights = {2, 2, 2, 2, 8, 5, 2},
    },
    // GomaCaveStream
    {
        .rate = 30,
        .level = 5,
        .enemies = {56, 70, 68, 63, 23, 59, 64},
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
        .enemies = {90, 87, 75, 68, 61, 70, 51, 62},
        .weights = {4, 4, 4, 4, 4, 2, 2, 2},
    },
    // World Map: terrain kind 2, forest
    {
        .rate = 9,
        .level = 6,
        .enemies = {73, 66, 69, 70, 90, 21, 96, 37},
        .weights = {1, 1, 1, 1, 1, 2, 2, 2},
    },
    // KolimaTunnel
    {
        .rate = 35,
        .level = 6,
        .enemies = {88, 31, 92, 23, 83, 70, 80, 26},
        .weights = {1, 2, 2, 1, 1, 5, 5, 5},
    },
    // Kolima Forest Bridge
    {
        .rate = 40,
        .level = 6,
        .enemies = {83, 77, 63, 66, 32, 93, 37, 27},
        .weights = {10, 8, 6, 4, 2, 1, 1, 1},
    },
    // Kolima Forest Clearing
    {
        .rate = 40,
        .level = 7,
        .enemies = {87, 92, 74, 90, 75, 93, 80, 60},
        .weights = {4, 8, 6, 6, 4, 2, 1, 1},
    },
    // Kolima Forest River
    {
        .rate = 40,
        .level = 7,
        .enemies = {81, 70, 89, 63, 99, 88, 78, 92},
        .weights = {2, 4, 6, 6, 8, 6, 2, 1},
    },
    // Kolima Forest Tree
    {
        .rate = 40,
        .level = 7,
        .enemies = {75, 70, 72, 55, 62, 61, 31, 33},
        .weights = {1, 2, 4, 6, 8, 8, 4, 2},
    },
    // Tret Tree Branch (entrances 1 to 3)
    {
        .rate = 45,
        .level = 7,
        .enemies = {52, 88, 84, 74, 79, 77, 68, 55},
        .weights = {2, 2, 6, 2, 4, 6, 3, 1},
    },
    // Tret Tree Interiors (entrances 1, 11, 16, 21 to 29)
    {
        .rate = 45,
        .level = 7,
        .enemies = {60, 92, 77, 74, 78, 97, 72, 81},
        .weights = {1, 2, 6, 5, 5, 4, 2, 1},
    },
    // Tret Tree Interiors (entrances 2 to 5, 12, 13, 31, 32)
    {
        .rate = 45,
        .level = 8,
        .enemies = {95, 125, 50, 120, 68, 70, 80, 104},
        .weights = {1, 2, 4, 6, 6, 4, 3, 2},
    },
    // Tret Tree Branch (any entrance)
    {
        .rate = 45,
        .level = 8,
        .enemies = {54, 79, 97, 98, 103, 83, 65, 126},
        .weights = {1, 1, 4, 6, 3, 6, 4, 4},
    },
    // Tret Tree Interiors (entrances 6 to 9, 14, 51 to 59)
    {
        .rate = 45,
        .level = 8,
        .enemies = {126, 60, 78, 120, 99, 81, 52, 94},
        .weights = {1, 1, 2, 3, 4, 6, 10, 8},
    },
    // BilibinCaveRapier (any entrance)
    {
        .rate = 30,
        .level = 8,
        .enemies = {66, 124, 82, 73, 54, 61, 100, 77},
        .weights = {6, 6, 4, 4, 2, 2, 1, 1},
    },
    // BilibinCaveIce (any entrance)
    {
        .rate = 30,
        .level = 8,
        .enemies = {57, 79, 125, 36, 53, 124, 126, 89},
        .weights = {2, 2, 2, 4, 4, 5, 7, 7},
    },
    // BilibinCaveRapier (entrances 5, 6)
    {
        .rate = 30,
        .level = 9,
        .enemies = {143, 61, 78, 84, 66, 55, 88, 100},
        .weights = {1, 1, 1, 1, 1, 2, 2, 2},
    },
    // BilibinCaveIce (entrance 5)
    {
        .rate = 30,
        .level = 9,
        .enemies = {71, 50, 95, 132, 69, 81, 130, 68},
        .weights = {1, 1, 1, 1, 1, 2, 2, 2},
    },
    // World Map: terrain kind 21, snowfield (behavior 5)
    {
        .rate = 25,
        .level = 9,
        .enemies = {134, 92, 61, 122, 72},
        .weights = {3, 3, 5, 5, 5},
    },
    // World Map: terrain kind 21, snowfield (behavior 6)
    {
        .rate = 9,
        .level = 9,
        .enemies = {69, 94, 134, 121, 104},
        .weights = {2, 2, 4, 4, 4},
    },
    // Mercury Lighthouse Entrance, MercuryLighthouseLower
    {
        .rate = 40,
        .level = 9,
        .enemies = {71, 136, 78, 103, 51, 64, 104, 60},
        .weights = {6, 4, 2, 1, 4, 4, 2, 6},
    },
    // MercuryLighthouseLower and MercuryLighthouseMiddle
    {
        .rate = 40,
        .level = 9,
        .enemies = {56, 99, 100, 53, 143, 135, 130, 96},
        .weights = {2, 1, 2, 2, 4, 4, 6, 8},
    },
    // MercuryLighthouseMiddle and MercuryLighthouseUpper
    {
        .rate = 40,
        .level = 10,
        .enemies = {123, 148, 90, 149, 75, 102, 100, 121},
        .weights = {1, 1, 2, 2, 3, 4, 8, 8},
    },
    // MercuryLighthouseUpper and MercuryLighthouseExterior
    {
        .rate = 40,
        .level = 11,
        .enemies = {100, 98, 131, 126, 92, 120, 133, 167},
        .weights = {1, 2, 2, 1, 2, 4, 8, 8},
    },
    // MercuryLighthouseExterior (entrances 3, 4)
    {
        .rate = 40,
        .level = 11,
        .enemies = {161, 122, 141, 143, 81, 129, 104, 79},
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
        .enemies = {104, 101, 82, 83},
        .weights = {3, 3, 3, 3},
    },
    // World Map: terrain kind 31, forest
    {
        .rate = 9,
        .level = 11,
        .enemies = {160, 103, 164, 79},
        .weights = {1, 1, 1, 1},
    },
    // FuchinFallsCaveEntrance and FuchinFallsCaveZephyr
    {
        .rate = 38,
        .level = 11,
        .enemies = {95, 120, 149, 155, 126, 160, 86, 88},
        .weights = {4, 4, 4, 8, 6, 4, 2, 1},
    },
    // FuchinFallsCaveDragonsEye
    {
        .rate = 38,
        .level = 11,
        .enemies = {102, 148, 96, 120, 127, 106, 154, 82},
        .weights = {1, 2, 2, 3, 6, 6, 3, 2},
    },
    // FuchinFallsCaveDragonStatue
    {
        .rate = 38,
        .level = 11,
        .enemies = {148, 133, 89, 101, 165, 95, 122, 124},
        .weights = {1, 1, 2, 3, 4, 4, 6, 8},
    },
    // MogallForestSign
    {
        .rate = 42,
        .level = 11,
        .enemies = {152, 130, 122, 89, 99, 126, 123, 121},
        .weights = {6, 6, 6, 3, 2, 1, 1, 1},
    },
    // MogallForestQuartz
    {
        .rate = 42,
        .level = 12,
        .enemies = {102, 191, 195, 141, 99, 129, 131, 86},
        .weights = {1, 1, 3, 6, 6, 3, 1, 1},
    },
    // MogallForestKillerApe
    {
        .rate = 42,
        .level = 12,
        .enemies = {98, 181, 149, 163, 124, 89, 152, 121},
        .weights = {1, 1, 2, 2, 3, 4, 5, 5},
    },
    // World Map: terrain kind 3, grassland, desert and beach
    {
        .rate = 25,
        .level = 12,
        .enemies = {152, 195, 192, 129, 101, 141},
        .weights = {3, 3, 1, 3, 1, 1},
    },
    // World Map: terrain kind 3, forest
    {
        .rate = 9,
        .level = 12,
        .enemies = {195, 129, 143, 136, 103, 99},
        .weights = {1, 1, 2, 1, 2, 2},
    },
    // AltinPeakRailTunnel, AltinPeakSecondWaterBeast, AltinPeakSouthEntrance
    {
        .rate = 45,
        .level = 12,
        .enemies = {135, 99, 166, 122, 100, 94, 152, 124},
        .weights = {6, 6, 4, 2, 1, 1, 1, 1},
    },
    // AltinPeakThirdWaterBeast and AltinPeakPool
    {
        .rate = 45,
        .level = 13,
        .enemies = {125, 203, 162, 153, 120, 155, 206, 122},
        .weights = {1, 1, 2, 4, 3, 4, 2, 2},
    },
    // AltinPeakSpritz, AltinPeakJunction, AltinPeakFallingRocks and AltinPeakWestExit
    {
        .rate = 42,
        .level = 13,
        .enemies = {151, 150, 120, 99, 186, 207, 187, 196},
        .weights = {1, 1, 2, 3, 4, 4, 8, 8},
    },
    // LamakanDesertEast
    {
        .rate = 40,
        .level = 13,
        .enemies = {99, 106, 124, 148, 100, 161, 127, 104},
        .weights = {5, 5, 4, 3, 3, 2, 1, 1},
    },
    // LamakanDesertSmog
    {
        .rate = 40,
        .level = 14,
        .enemies = {184, 164, 165, 205, 196, 146, 144, 191},
        .weights = {1, 2, 3, 6, 6, 4, 2, 1},
    },
    // LamakanDesertManticore
    {
        .rate = 40,
        .level = 14,
        .enemies = {154, 167, 181, 182, 186, 180, 121, 150},
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
        .enemies = {166, 201, 155, 235, 187, 185, 206, 149},
        .weights = {4, 4, 4, 4, 4, 2, 2, 2},
    },
    // World Map: terrain kind 4, forest
    {
        .rate = 9,
        .level = 15,
        .enemies = {206, 181, 230, 191, 236, 162, 182, 164},
        .weights = {2, 2, 2, 2, 3, 4, 4, 4},
    },
    // ValeCaveKite (entrances 1 to 4)
    {
        .rate = 40,
        .level = 15,
        .enemies = {235, 226, 180, 144, 221, 208, 185, 142},
        .weights = {6, 6, 6, 4, 4, 1, 1, 1},
    },
    // ValeCaveKite (entrances 8 to 10)
    {
        .rate = 40,
        .level = 15,
        .enemies = {164, 207, 167, 236, 220, 223, 225, 149},
        .weights = {4, 4, 4, 6, 6, 2, 2, 2},
    },
    // ValeCaveLogs (entrances 1 to 3)
    {
        .rate = 40,
        .level = 15,
        .enemies = {165, 223, 184, 166, 196, 142, 193, 167},
        .weights = {2, 2, 2, 3, 3, 5, 5, 5},
    },
    // ValeCaveLogs (entrances 4, 5)
    {
        .rate = 40,
        .level = 15,
        .enemies = {154, 194, 144, 220, 149, 152, 202, 232},
        .weights = {1, 1, 1, 2, 2, 5, 5, 5},
    },
    // VaultCavePassage
    {
        .rate = 40,
        .level = 16,
        .enemies = {167, 162, 180, 221, 195, 226, 230, 192},
        .weights = {8, 8, 8, 4, 4, 4, 2, 2},
    },
    // VaultCaveVambrace and VaultCaveMouth
    {
        .rate = 40,
        .level = 16,
        .enemies = {161, 204, 225, 180, 195, 203, 201, 230},
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
        .enemies = {196, 260, 222, 252, 195, 189, 192, 231},
        .weights = {6, 6, 6, 6, 3, 3, 3, 3},
    },
    // World Map: terrain kind 5, forest
    {
        .rate = 9,
        .level = 18,
        .enemies = {181, 252, 255, 231, 253, 232, 221, 201},
        .weights = {3, 3, 3, 3, 6, 6, 6, 6},
    },
    // AltmillerCaveEntrance
    {
        .rate = 40,
        .level = 17,
        .enemies = {190, 195, 181, 255, 202, 231, 226, 222},
        .weights = {6, 6, 4, 4, 4, 2, 1, 1},
    },
    // AltmillerCaveBabi
    {
        .rate = 40,
        .level = 17,
        .enemies = {201, 205, 189, 250, 234, 185, 192, 232},
        .weights = {4, 4, 6, 6, 4, 4, 2, 1},
    },
    // AltmillerCaveVialChest
    {
        .rate = 40,
        .level = 18,
        .enemies = {182, 251, 229, 201, 206, 250, 230, 205},
        .weights = {3, 3, 4, 6, 6, 4, 2, 1},
    },
    // AltmillerCaveSquall
    {
        .rate = 40,
        .level = 18,
        .enemies = {183, 252, 180, 250, 196, 226, 262, 195},
        .weights = {2, 2, 4, 4, 6, 5, 5, 3},
    },
    // AltmillerCaveCookieChest
    {
        .rate = 40,
        .level = 18,
        .enemies = {253, 229, 190, 257, 221, 255, 208, 195},
        .weights = {2, 2, 3, 3, 4, 6, 6, 4},
    },
    // AltmillerCaveDraught (entrances 50, 51)
    {
        .rate = 40,
        .level = 18,
        .enemies = {232, 202, 206, 193, 208, 207, 225, 250},
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
        .enemies = {255, 262, 256, 275, 269, 232, 224, 222},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // GondowanCaveRiver (any entrance)
    {
        .rate = 30,
        .level = 20,
        .enemies = {281, 261, 230, 271, 220, 256, 273, 284},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // GondowanCaveRiver (entrances 1, 2)
    {
        .rate = 30,
        .level = 20,
        .enemies = {222, 281, 232, 225, 253, 257, 274, 250},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // GondowanCave (entrances 1 to 3)
    {
        .rate = 30,
        .level = 20,
        .enemies = {229, 226, 221, 274, 234, 278, 253, 277},
        .weights = {3, 3, 4, 4, 5, 5, 6, 6},
    },
    // LunpaFortressCave (entrances 1, 2)
    {
        .rate = 35,
        .level = 21,
        .enemies = {222, 273, 272, 284},
        .weights = {2, 2, 2, 2},
    },
    // LunpaFortressCave (any entrance)
    {
        .rate = 35,
        .level = 21,
        .enemies = {282, 315, 316, 252},
        .weights = {2, 2, 2, 2},
    },
    // LunpaFortressToadonpa (entrances 1, 2)
    {
        .rate = 35,
        .level = 21,
        .enemies = {281, 226, 225, 251},
        .weights = {2, 2, 2, 2},
    },
    // World Map: terrain kind 6, grassland, desert and beach
    {
        .rate = 25,
        .level = 22,
        .enemies = {281, 278, 317, 272, 275, 252, 268, 261},
        .weights = {4, 4, 3, 3, 3, 3, 3, 3},
    },
    // World Map: terrain kind 6, forest
    {
        .rate = 9,
        .level = 22,
        .enemies = {274, 323, 316, 322, 279, 259, 281, 268},
        .weights = {2, 2, 3, 3, 3, 4, 4, 4},
    },
    // SuhallaDesertNorth
    {
        .rate = 40,
        .level = 22,
        .enemies = {323, 250, 321, 312, 285, 279, 316, 261},
        .weights = {4, 4, 4, 5, 3, 4, 2, 2},
    },
    // SuhallaDesertSouth
    {
        .rate = 40,
        .level = 22,
        .enemies = {315, 251, 262, 277, 316, 260, 261, 322},
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
        .enemies = {271, 323, 259, 313, 268, 332, 285, 278},
        .weights = {6, 6, 6, 3, 3, 2, 2, 2},
    },
    // SuhallaGateDew (any entrance)
    {
        .rate = 30,
        .level = 24,
        .enemies = {329, 273, 333, 280, 272, 270, 310, 322},
        .weights = {2, 3, 3, 6, 6, 3, 3, 3},
    },
    // GatewayCave (entrances 1, 2)
    {
        .rate = 30,
        .level = 24,
        .enemies = {270, 268, 314, 281, 285, 271, 312, 321},
        .weights = {1, 1, 2, 2, 2, 3, 3, 3},
    },
    // GatewayCave (any entrance)
    {
        .rate = 30,
        .level = 24,
        .enemies = {322, 271, 330, 328, 280, 312, 320, 333},
        .weights = {2, 2, 3, 3, 3, 6, 6, 6},
    },
    // VenusLighthouseGroundFloor (any entrance)
    {
        .rate = 40,
        .level = 25,
        .enemies = {273, 272, 330, 313, 310},
        .weights = {4, 4, 4, 4, 4},
    },
    // VenusLighthouseGroundFloor (entrances 20 to 26, 30 to 32)
    {
        .rate = 40,
        .level = 25,
        .enemies = {284, 279, 314, 322, 331},
        .weights = {4, 4, 4, 4, 4},
    },
    // BabiLighthouseEntry, BabiLighthouseLuff, BabiLighthouseStoneDoor, TunnelRuinsLadyStatues (entrances 1 to 3)
    {
        .rate = 35,
        .level = 25,
        .enemies = {334, 315, 314, 330, 320, 333, 273, 274},
        .weights = {6, 6, 6, 4, 4, 4, 2, 2},
    },
    // TunnelRuinsGreatStatue, TunnelRuinsLadyStatues (entrances 8 to 11)
    {
        .rate = 35,
        .level = 25,
        .enemies = {328, 284, 316, 333, 321, 319, 274, 272},
        .weights = {3, 3, 4, 6, 6, 4, 3, 3},
    },
    // TunnelRuinsLadyStatues (entrances 12, 15 to 17)
    {
        .rate = 35,
        .level = 26,
        .enemies = {329, 339, 333, 337, 343, 314, 328, 319},
        .weights = {3, 3, 3, 4, 4, 4, 6, 6},
    },
    // VenusLighthouseFirstFloor (any entrance)
    {
        .rate = 34,
        .level = 27,
        .enemies = {333, 322, 344, 331, 338, 341, 321, 339},
        .weights = {4, 4, 3, 3, 3, 3, 2, 2},
    },
    // VenusLighthouseFirstFloor (entrances 19, 20), VenusLighthouseSecondFloor
    {
        .rate = 32,
        .level = 28,
        .enemies = {344, 331, 330, 333, 323, 322, 340, 338},
        .weights = {3, 3, 4, 4, 3, 3, 2, 2},
    },
    // VenusLighthouseThirdFloor
    {
        .rate = 30,
        .level = 29,
        .enemies = {344, 342, 340, 343, 337, 339, 338, 341},
        .weights = {2, 2, 3, 3, 4, 4, 3, 3},
    },
    // VenusLighthouseFourthFloor
    {
        .rate = 30,
        .level = 30,
        .enemies = {342, 337, 344, 340, 338, 341, 339, 343},
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
