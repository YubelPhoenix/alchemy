#ifndef ALCHEMY_UNIT_SCENE_UMBRAL_RIFT_H
#define ALCHEMY_UNIT_SCENE_UMBRAL_RIFT_H

#include "types.h"
#include "scene_tables.h"

struct SceneExitRegion;
s32 UmbralRift_Initialize(void);
const struct SceneEntrance *Scene_GetEntrances(void);
const struct SceneExitRegion *Scene_GetExitRegions(void);
const u32 *Scene_GetExits(void);
const struct ActorTemplate *Scene_GetActorTemplates(void);
const struct Trigger *Scene_GetTriggers(void);

#endif
