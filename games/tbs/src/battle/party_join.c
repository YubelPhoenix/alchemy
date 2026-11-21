/// @file
/// "You're not alone": the "???" commander's battle in Vale (Ashfall). She
/// binds Garet, Ivan and Mia before the fight (Vale_TalkToMysteryLeader), so
/// Isaac starts alone; during the battle his friends break free one by one
/// and join him, as Zidane's friends do in Final Fantasy IX's Pandemonium.
///
/// The fight:
///  1. Isaac fights her alone. While he is alone he cannot fall: a blow that
///     would fell him leaves him at 1 HP instead (PartyJoin_ClampDamage).
///  2. Her turn in RESCUE_ROUND is Kaiserdammerung: she speaks, and the blow leaves him at exactly 1 HP; the number shown is the
///     HP he lost (BossAI_MysteryChooseSlot asks PartyJoin_TakeBrinkTurn).
///  3. At the end of that round, or of any round that left Isaac alone at
///     1 HP, she speaks; Mia breaks free and runs in and casts Pure Ply on
///     Isaac. "???" and Mia speak.
///  Everything here plays at the end of a round, after the game's own round
///  end, or inside her own turn, so the screen is in the state the game
///  leaves it between rounds; the one extra action, Mia's Pure Ply, is
///  followed by PartyJoin_Settle.
///  4. Garet breaks free at the end of the first round that leaves "???" below
///     GARET_BELOW_PERCENT of her HP.
///  5. Ivan breaks free at the end of the round she awakens in, below half HP
///     (BossAI_MysteryAwaken sets MYSTERY_ENRAGED): with her full power turned
///     on Isaac she can no longer hold his Psynergy back. "???" has a last
///     word with the party whole.
///  The battle's own song plays from its start, FULL_PARTY_SONG from
///  Garet's arrival.
///  Each of 4 and 5 also happens after a few rounds regardless (the _LATEST_
///  counts), so every player sees all three arrive; one arrival a round.
///
/// How it looks: from the moment Kaiserdammerung lands the battlefield sinks
/// into darkness, and Isaac, slumped in the pose of a downed party member,
/// stands almost alone in it; each friend brings part of the light back, and
/// with all four the battlefield is lit again (the gloom: her backdrop,
/// mystery_backdrop.c, dims its colours by PartyJoin_StepGloom). Each
/// arrival breaks her bind with a crack, a white flash and a shake, runs in
/// from off the battlefield to their place, the way the party runs off when
/// it flees, but backwards, with a hop and the camera turned to the party,
/// and bursts with the light of their element. They come in at full HP and
/// PP. Getting a unit into
/// the battle copies what the engine does when an enemy calls for help
/// (BattleAbility_ApplyToTarget, target_exec.c): into the unit list, a
/// battle object at its spot, and BattleObject_Put for the sprite.
///
/// The party stays as it is when the battle ends; Vale's aftermath
/// (Vale_MysteryLeaderAftermath) puts it back in its usual order.
///
/// This object sits in the ROM tail beside mystery_backdrop.c, because the
/// battle bank is full: the bank only gains the calls into it (Battle_Run,
/// BossAI_MysteryChooseSlot and BattleAbility_ApplyToTarget).

#include "battle_internal.h"

/// Set to 0 to give the "???" battle back its plain solo fight.
#define PARTY_JOIN_ENABLED 1

/// The round at whose end she brings Isaac to 1 HP and Mia arrives.
#define RESCUE_ROUND 3
/// The song from Garet's arrival on. Until then the battle plays the song
/// Vale_TalkToMysteryLeader chooses for it, with no break: through Isaac
/// alone, her Kaiserdammerung and Mia's rescue. While that is this same song,
/// it plays on without starting again.
#define FULL_PARTY_SONG MUS_FUSION_DRAGON_BATTLE
/// Garet arrives once "???" is below this percent of her HP, or this many
/// rounds after Mia, whichever is first.
#define GARET_BELOW_PERCENT 75
#define GARET_LATEST_ROUNDS 4
/// Ivan arrives when she awakens, or this many rounds after Garet.
#define IVAN_LATEST_ROUNDS 5
/// Keep the four returning allies slightly wider than the stock 32-pixel
/// gaps, without pushing Ivan off the right edge of the battle camera.
/// Center four 36-pixel gaps at +54, +18, -18, -54 depth units.
#define MYSTERY_PARTY_SPACING 36
#define MYSTERY_PARTY_FRONT_Z 54
/// Frames an arrival takes to run in, and frames of the camera's turn first.
#define ARRIVAL_RUN_FRAMES 40
#define ARRIVAL_CAMERA_FRAMES 20

/// Pure Ply, two after Ply in abilities.c (ability_ids.h names only Ply).
#define ABILITY_PURE_PLY (ABILITY_PLY + 2)
/// Ice Missile, Mia's entrance: its row in abilities.c ("// Ice Missile"),
/// which ability_ids.h does not name.
#define ABILITY_ICE_MISSILE 0x1d

/// An action's target is a place on a side, not a unit id: bit 7 clear is
/// the party's side, and Isaac, who starts alone, is its place 0.
#define TARGET_ISAAC 0
/// "???", the battle's one enemy: the enemy side (bit 7) and its place 0.
#define TARGET_MYSTERY 0x80

/// The battle's state, kept in BattleWork's spare bytes, which Battle_Run
/// clears as every battle starts and no other code uses.
/// The rounds played so far.
#define joinRound unusedAfterEscapes
/// How far the story has gone (enum JoinStage).
#define joinStage unusedAfterChannels[0]
/// Her Kaiserdammerung turn (enum JoinBrink): it leaves Isaac 1 HP.
#define joinBrink unusedAfterChannels[1]
/// The round the last arrival came in.
#define joinLastArrival unusedAfterPlacement[0]
/// Set when Isaac reaches 1 HP alone: the gloom starts, but Mia waits
/// until the end of the third solo round.
#define joinEdge unusedAfterPlacement[1]
/// The gloom over the battlefield, 0 (lit) to 256 (black), as shown, the
/// gloom it is easing toward, and the gloom last written to the screen.
#define joinGloom unusedAfterBackground[0]
#define joinGloomTarget unusedAfterBackground[1]
#define joinGloomShown unusedAfterBackground[2]

/// The gloom while Isaac stands alone at 1 HP, with Mia, with Garet too, and
/// the change in it each frame (from lit to darkest in a little over a
/// second and a half).
#define GLOOM_ALONE 200
#define GLOOM_MIA 130
#define GLOOM_GARET 60
#define GLOOM_STEP 2

/// How each friend breaks the bind, rising one to the next: Mia gently, with
/// no crack, only her light; Garet with a crack, a white flash and a shake;
/// Ivan, who makes the party whole, with a louder crack, a longer flash and a
/// harder shake. Frames the screen stays white, frames it fades back (one
/// level of REG_BLDY each), and the shake in 1/65536 turns of yaw, as
/// BossAI_MysteryAwaken flashes.
enum JoinBreak {
  BREAK_GENTLE, ///< Mia: no crack, no flash
  BREAK_FORCE,  ///< Garet
  BREAK_WHOLE   ///< Ivan
};
#define BREAK_HOLD 4
#define BREAK_FADE 14
#define BREAK_SHAKE 0x180
#define BREAK_WHOLE_HOLD 8
#define BREAK_WHOLE_FADE 24
#define BREAK_WHOLE_SHAKE 0x280

/// The darkest moment: frames Isaac stands alone, slumped, before she speaks;
/// between each memory; and in the silence after them, before Mia comes.
#define ALONE_SILENCE_FRAMES 120
#define MEMORY_SILENCE_FRAMES 90

enum JoinBrink {
  BRINK_NONE = 0,    ///< not this round
  BRINK_PENDING = 1, ///< her next turn is Kaiserdammerung
  BRINK_STRIKING = 2 ///< her Kaiserdammerung is being played
};

enum JoinStage {
  JOIN_ALONE = 0, ///< Isaac alone
  JOIN_MIA = 1,   ///< Mia has come
  JOIN_GARET = 2, ///< Garet too
  JOIN_IVAN = 3   ///< all four
};

/// Returns the unit id of "???" if she is in this battle and still standing,
/// else -1.
static s32 PartyJoin_FindMystery(void) {
  s16 enemyIds[ENEMY_BATTLE_SIZE + 1];
  s32 count;
  s32 i;

  count = BattleEnemy_List(enemyIds);
  for (i = 0; i < count; i++) {
    struct Unit *unit = Unit_GetFar(enemyIds[i]);

    if (unit->id == ENEMY_ID_FIRST + ENEMY_ROW_MYSTERY_LEADER && unit->hp > 0)
      return enemyIds[i];
  }
  return -1;
}

/// Keep ordinary story lines visible for at least 2.5 seconds and the
/// commander's key lines for at least 3 seconds after text finishes.
/// Then require a quarter-second with no advance button held: the battle's
/// normal advance prompt accepts held B immediately and held A after 16
/// frames, so BOTH must be released before the prompt is allowed to open.
#define SAY_HOLD_FRAMES 150
#define SAY_KEY_LINE_FRAMES 180
#define SAY_QUIET_FRAMES 15

/// Show one story message as the battle's own two-line text. The minimum
/// display time cannot be skipped; afterward wait for a clean button release,
/// then let the usual battle advance prompt stay up until the player presses.
/// (A framed tutorial window needs a font only the tutorial battle loads.)
static void PartyJoin_SayWithHold(s32 message, s32 holdFrames) {
  s32 quiet;

  MessageArgument_ClearAllFar();
  BattleMessage_ShowAndWaitFar(message);
  // Start the minimum reading time only after every character is visible.
  while (!TextPrinter_AllFinishedFar())
    WaitFrames(1);
  WaitFrames(holdFrames);
  for (quiet = 0; quiet < SAY_QUIET_FRAMES; quiet++) {
    if (gKeysHeld & (KEY_ADVANCE | KEY_B))
      quiet = -1;
    WaitFrames(1);
  }
  BattleMessage_WaitForAdvance();
}

static void PartyJoin_Say(s32 message) {
  PartyJoin_SayWithHold(message, SAY_HOLD_FRAMES);
}

/// Important battle revelations, including her half-HP transformation.
/// Also called by the commander's boss AI, which runs in the battle bank.
void PartyJoin_SayKeyLine(s32 message) {
  PartyJoin_SayWithHold(message, SAY_KEY_LINE_FRAMES);
}

/// Turns the camera to the party over `frames` frames and waits for it.
static void PartyJoin_FaceParty(s32 frames) {
  struct BattleBackgroundWork *view =
      HEAP_SLOT_BLOCK(HEAP_SLOT_BATTLE_BACKGROUND);

  view->targetYaw = YAW_PARTY_TURN;
  view->frames = frames;
  WaitFrames(frames);
}

/// The party status window's column widths, in tiles, as
/// PartyStatus_BuildLayoutBounds lays it out (party_status.c keeps them
/// private).
#define STATUS_COLUMN_WIDTH 6
#define STATUS_DJINN_WIDTH 5

/// Widens the party status window for the party now fighting, keeping its
/// heap block. It must not be closed and opened again: freeing a heap slot
/// also frees every block taken after it (FreeHeapSlot), and the battle's
/// background, palette and sprite work were all taken after this one, so a
/// new block would be laid over them. Lays it out as
/// PartyStatus_BuildLayoutBounds does, a column for each party member at the
/// screen's right edge, then redraws it.
static void PartyJoin_WidenStatusWindow(void) {
  struct PartyStatusWindow *layout = HEAP_SLOT_BLOCK(HEAP_SLOT_PARTY_STATUS);
  s32 width;
  s32 height;

  height = 3;
  if (layout->flags & PARTY_STATUS_SHOW_PP)
    height++;
  width = BattleParty_PrepareMembers(0) * STATUS_COLUMN_WIDTH + 1;
  if (layout->flags & PARTY_STATUS_SHOW_DJINN)
    width += STATUS_DJINN_WIDTH;
  Window_CloseFar(layout->window, 1);
  layout->x = 30 - width;
  layout->width = width;
  layout->height = height;
  layout->window =
      Window_CreateFar(layout->x, layout->y, layout->width, layout->height, 6);
  PartyStatus_DrawFar(gBattleWork->partyStatus);
}

/// Puts the screen back as the game sets it before each action
/// (BattleStaging_DispatchAction) and between rounds: no highlight, full
/// brightness, the action camera's projection, and the zoomed background
/// with its saved palette. Called after an action this file plays itself.
static void PartyJoin_Settle(void) {
  struct BattleBackgroundWork *view =
      HEAP_SLOT_BLOCK(HEAP_SLOT_BATTLE_BACKGROUND);
  struct BattleCamera *camera = HEAP_SLOT_BLOCK(HEAP_SLOT_CAMERA);
  struct BattleWork *battle = gBattleWork;

  BattleHighlight_SetModes(0, HIGHLIGHT_OFF);
  view->flag = 0;
  battle->brightness = Q16_ONE;
  Transform_Reset();
  Transform_SetLookAt(camera->eye, camera->focus);
  Projection_Set(0x01fe0000, Iwram_RatioMulQ14(0x01fe0000, 0xc000), 0x7fff0000);
  BattleBackground_SetMode(BATTLE_BACKGROUND_ZOOMED, battle->background,
                           BATTLE_BACKGROUND_FADE_RESTORE);
  WaitFrames(1);
}

/// The bind breaking as a friend breaks free, in the friend's way
/// (enum JoinBreak): a crack, the whole screen white, and the white fading
/// while the camera shakes and settles, as her own awakening flashes
/// (BossAI_MysteryAwaken); nothing for BREAK_GENTLE. The yaw and the blend
/// registers are put back after.
static void PartyJoin_BreakFlash(s32 style) {
  struct BattleCamera *camera = HEAP_SLOT_BLOCK(HEAP_SLOT_CAMERA);
  u16 savedBlend = REG_BLDCNT;
  u16 baseYaw = camera->yaw;
  s32 frame;
  s32 shake;
  s32 hold;
  s32 fade;
  s32 strength;

  if (style == BREAK_GENTLE)
    return;
  hold = BREAK_HOLD;
  fade = BREAK_FADE;
  strength = BREAK_SHAKE;
  if (style == BREAK_WHOLE) {
    hold = BREAK_WHOLE_HOLD;
    fade = BREAK_WHOLE_FADE;
    strength = BREAK_WHOLE_SHAKE;
    Sound_PlaySongFar(SE_THUNDER_LOUD);
  }
  Sound_PlaySongFar(SE_ITEM_BREAK);
  REG_BLDCNT = BLDCNT_TGT1_ALL | BLDCNT_EFFECT_LIGHTEN;
  for (frame = 0; frame < hold + fade; frame++) {
    if (frame < hold)
      REG_BLDY = 16;
    else
      REG_BLDY = 16 - (frame - hold + 1) * 16 / fade;
    shake = strength * (hold + fade - frame) / (hold + fade);
    if (frame & 1)
      shake = -shake;
    camera->yaw = baseYaw + shake;
    WaitFrames(1);
  }
  camera->yaw = baseYaw;
  REG_BLDY = 0;
  REG_BLDCNT = savedBlend;
}

static void PartyJoin_Act(s32 unitId, s32 command, s32 abilityId,
                          s32 target);

/// Sets unitId's sprite off the battlefield, three times as far out as its
/// spot, where the party runs to when it flees (BattleMotion_SetupEscapeObject).
static void PartyJoin_PlaceOffstage(s32 unitId) {
  struct BattleObject *battleObject = BattleObject_Get(unitId);
  struct Actor *actor = battleObject->actor;

  if (actor == NULL)
    return;
  actor->x.fixed = battleObject->anchorX * 3;
  actor->y.fixed = 0;
  actor->z.fixed = battleObject->anchorZ;
}

/// Brings character unitId into the battle at the party's next place: the
/// bind breaks in the friend's way (PartyJoin_BreakFlash, enum JoinBreak),
/// they run in from off the battlefield with a hop, and their light breaks
/// through, easing the gloom to `gloom`: entranceAbility cast at "???" if
/// not 0, else a hand raised and the burst of their element. Returns 0 if they could not join (already
/// fighting, or no place left).
static s32 PartyJoin_Arrive(s32 unitId, s32 element, s32 gloom, s32 style,
                            s32 entranceAbility) {
  struct BattleWork *battle;
  struct BattleObject *battleObject;
  struct Actor *actor;
  struct Unit *unit;
  s32 place;

  battle = gBattleWork;
  if (GameFlag_GetFar(FLAG_IN_PARTY(unitId)) != 0)
    return 0;
  if (Party_CountMembersFar() >= PARTY_BATTLE_SIZE)
    return 0;

  // Into the party, fresh: full HP and PP, stats from their equipment.
  Party_AddMemberFar(unitId);
  Unit_CalculateFar(unitId);
  unit = Unit_GetFar(unitId);
  unit->hp = unit->hpMax;
  unit->pp = unit->ppMax;
  unit->side = BATTLE_SIDE_PARTY;
  Unit_RecalculateGaugesFar(unitId);

  // Into the battle's party list, with a battle object at the next of the
  // party's fixed spots (gBattlePlacement_StepPairs), as
  // BattleUnit_RefreshPlacement places everyone at the start.
  for (place = 0; battle->partyUnits[place] != BATTLE_UNIT_LIST_END; place++)
    ;
  battle->partyUnits[place] = unitId;
  battle->partyUnits[place + 1] = BATTLE_UNIT_LIST_END;
  battle->objectIndex[unitId] = place;
  battleObject = BattleObject_Get(unitId);
  BattleObject_Make(battleObject, unitId,
                    gBattlePlacement_StepPairs[place * 2],
                    gBattlePlacement_StepPairs[place * 2 + 1]);
  // The normal 32-pixel depth gaps crowd the 4-player battle sprites.
  // Expand the anchors only in this encounter, and ease existing allies
  // to their new spots as the next companion arrives.
  {
    s32 allyPlace;
    for (allyPlace = 0; allyPlace <= place; allyPlace++) {
      s32 allyId = battle->partyUnits[allyPlace];
      struct BattleObject *allyObject = BattleObject_Get(allyId);
      allyObject->anchorZ =
          (MYSTERY_PARTY_FRONT_Z - allyPlace * MYSTERY_PARTY_SPACING) * 65536;
      if (allyPlace != place)
        BattleMotion_ReturnToSpot(allyId);
    }
  }

  // Their Djinn on standby count toward summons, as at the battle's start,
  // and the party status window takes its width from the party size: both
  // before anything is staged with them in the party.
  DjinnRecovery_Reconcile();
  BattleSummon_UpdateAvailability();
  if (((struct BattleSummonState *)Djinn_GetRecoveryTableFar(
           DJINN_RECOVERY_PARTY))
          ->availableMask != 0)
    battle->partyStatus = PARTY_STATUS_SUMMONS;
  else
    battle->partyStatus = PARTY_STATUS_NO_SUMMONS;
  PartyJoin_WidenStatusWindow();

  // The camera on the party, the bind breaking, and the sprite made off
  // the battlefield, three times as far out as the spot (where the party
  // runs to when it flees, BattleMotion_SetupEscapeObject).
  PartyJoin_FaceParty(ARRIVAL_CAMERA_FRAMES);
  PartyJoin_BreakFlash(style);
  BattleObject_Put();
  PartyJoin_PlaceOffstage(unitId);

  // The run in to the spot, with a hop.
  battleObject = BattleObject_Get(unitId);
  actor = battleObject->actor;
  if (actor != NULL) {
    actor->acceleration = 0x20000;
    actor->speedLimit = 0x80000;
    actor->velocityY = 0x50000;
    actor->gravity = 0x7851;
    actor->bounce = 0;
    actor->steeringFlags = 0;
    actor->snapToTarget = 1;
    Actor_StartIdleFar(actor);
    Actor_SetMoveTargetFar(actor, battleObject->anchorX, 0,
                           battleObject->anchorZ);
    Actor_SelectAnimationFar(actor, POSE_STANDING);
    WaitFrames(ARRIVAL_RUN_FRAMES);
  }
  BattleMotion_ReturnToSpot(unitId);
  actor = BattleObject_Get(unitId)->actor;
  if (actor != NULL)
    Actor_SelectAnimationFar(actor, POSE_STANDING);

  // Their light breaks through, and the gloom eases with it: an entrance
  // attack on "???" (a cast's own glow is its light), or else a hand raised
  // and the burst of their element, as a Djinni set at a round's end bursts
  // (Battle_ProcessRoundEnd). Either puts the background in
  // BATTLE_BACKGROUND_FIXED, so the screen is settled after. ElementGlow_Play
  // returns when the glow is over; BattlePlayback_WaitForReady must not
  // follow it here, since it waits for a playback task only an action runs.
  battle->joinGloomTarget = gloom;
  // Garet and Ivan land without the burst; the gloom eases naturally.
  (void)element;
  if (entranceAbility != 0)
    PartyJoin_Act(unitId, COMMAND_PSYNERGY, entranceAbility, TARGET_MYSTERY);
  PartyJoin_Settle();
  BattleMotion_ReturnToSpot(unitId);

  battle->joinLastArrival = battle->joinRound;
  return 1;
}

/// Plays one action outside the round's list, as Battle_Run plays each of
/// its own. An enemy's ability is chosen at its turn (BattleAI_ChooseAction),
/// so abilityId only matters for a party member.
static void PartyJoin_Act(s32 unitId, s32 command, s32 abilityId,
                          s32 target) {
  struct BattleAction request;

  Iwram_ClearWords(&request, sizeof(request));
  request.unitId = unitId;
  request.command = command;
  request.parameter = abilityId;
  request.target = target;
  request.range = Ability_Get(abilityId)->range;
  BattleStaging_DispatchAction(&request, 10);
}

/// After the third solo round, she speaks; Mia breaks free, runs in and
/// heals him. Reaching 1 HP earlier does not skip the intended solo rounds.
static void PartyJoin_RunRescue(void) {
  struct BattleWork *battle = gBattleWork;

  struct Actor *isaac;

  battle->joinStage = JOIN_MIA;
  battle->joinEdge = 0;
  battle->joinBrink = BRINK_NONE;
  // Isaac slumps, as a downed party member does, until Mia's Pure Ply.
  BattleObject_Put();
  isaac = BattleObject_Get(battle->partyUnits[0])->actor;
  if (isaac != NULL)
    Actor_SelectAnimationFar(isaac, POSE_PARTY_HELD);
  WaitFrames(ALONE_SILENCE_FRAMES);
  PartyJoin_Say(MsgPartyJoinMysteryAlone);
  PartyJoin_Say(MsgPartyJoinMysteryAlone2);
  WaitFrames(MEMORY_SILENCE_FRAMES);

  if (PartyJoin_Arrive(MIA, ELEMENT_MERCURY, GLOOM_MIA, BREAK_GENTLE,
                       ABILITY_ICE_MISSILE) == 0)
    return;
  PartyJoin_Say(MsgPartyJoinMiaArrives);
  PartyJoin_Act(MIA, COMMAND_PSYNERGY, ABILITY_PURE_PLY, TARGET_ISAAC);
  PartyJoin_Settle();
  isaac = BattleObject_Get(battle->partyUnits[0])->actor;
  if (isaac != NULL)
    Actor_SelectAnimationFar(isaac, POSE_STANDING);
  PartyStatus_DrawFar(battle->partyStatus);
  PartyJoin_Say(MsgPartyJoinMysteryReacts);
  PartyJoin_Say(MsgPartyJoinMysteryProphecyMia);
  PartyJoin_Say(MsgPartyJoinMiaForgotten);
}

/// Her turn in RESCUE_ROUND: says her line and fades the music, and returns
/// 1 while the turn should be Kaiserdammerung. Called by
/// BossAI_MysteryChooseSlot at each of her picks; the line plays once.
s32 PartyJoin_TakeBrinkTurn(void) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle = gBattleWork;

  if (battle->joinBrink == BRINK_NONE || battle->joinStage != JOIN_ALONE)
    return 0;
  if (battle->joinBrink == BRINK_PENDING) {
    battle->joinBrink = BRINK_STRIKING;
    PartyJoin_SayKeyLine(MsgPartyJoinMysteryBrink);
    MessageArgument_ClearAllFar();
  }
  return 1;
#else
  return 0;
#endif
}

/// The party whole: all four raise their hands together, and Isaac, the one
/// she wanted alone, bursts with the light of Venus. Silent, as Isaac is;
/// what it says, it shows.
static void PartyJoin_RunUnison(void) {
  struct BattleWork *battle = gBattleWork;
  struct Actor *actor;
  s32 place;

  PartyJoin_FaceParty(ARRIVAL_CAMERA_FRAMES);
  for (place = 0; battle->partyUnits[place] != BATTLE_UNIT_LIST_END; place++) {
    actor = BattleObject_Get(battle->partyUnits[place])->actor;
    if (actor != NULL)
      Actor_SelectAnimationFar(actor, POSE_CAST);
  }
  WaitFrames(20);
  ElementGlow_Play(battle->partyUnits[0], ELEMENT_VENUS, GLOW_BURST, 0);
  PartyJoin_Settle();
  for (place = 0; battle->partyUnits[place] != BATTLE_UNIT_LIST_END; place++) {
    BattleMotion_ReturnToSpot(battle->partyUnits[place]);
    actor = BattleObject_Get(battle->partyUnits[place])->actor;
    if (actor != NULL)
      Actor_SelectAnimationFar(actor, POSE_STANDING);
  }
  WaitFrames(30);
  // The restraint ends here. From the next round onward the commander
  // gets two turns, so the final phase challenges a fully reunited party.
  {
    s32 mysteryId = PartyJoin_FindMystery();
    if (mysteryId >= 0)
      Unit_GetFar(mysteryId)->actionsPerRound = 2;
  }
}

/// Counts the round that just ended and plays whatever the story has next.
/// Called by Battle_Run at the end of every round, outside a link battle.
void PartyJoin_RunRoundEnd(void) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle;
  struct Unit *mystery;
  s32 mysteryId;
  s32 sinceArrival;

  battle = gBattleWork;
  if (battle->isLink != 0)
    return;
  mysteryId = PartyJoin_FindMystery();
  if (mysteryId < 0)
    return;
  mystery = Unit_GetFar(mysteryId);
  if (battle->joinRound < 255)
    battle->joinRound++;
  sinceArrival = battle->joinRound - battle->joinLastArrival;

  switch (battle->joinStage) {
  case JOIN_ALONE:
    // Kaiserdammerung lands in the third solo round. An earlier close call can
    // darken the field, but never brings Mia in before that round ends.
    if (battle->joinRound >= RESCUE_ROUND)
      PartyJoin_RunRescue();
    else if (battle->joinRound == RESCUE_ROUND - 1)
      battle->joinBrink = BRINK_PENDING;
    break;
  case JOIN_MIA:
    if (mystery->hp * 100 < mystery->hpMax * GARET_BELOW_PERCENT ||
        sinceArrival >= GARET_LATEST_ROUNDS) {
      battle->joinStage = JOIN_GARET;
      if (PartyJoin_Arrive(GARET, ELEMENT_MARS, GLOOM_GARET, BREAK_FORCE, 0)) {
        if (gSaveBlock.battleMusic != FULL_PARTY_SONG)
          Sound_PlaySongFar(FULL_PARTY_SONG);
        PartyJoin_Say(MsgPartyJoinGaretArrives);
        PartyJoin_Say(MsgPartyJoinGaretArrives2);
        PartyJoin_Say(MsgPartyJoinGaretArrives3);
        PartyJoin_Say(MsgPartyJoinMysteryProphecyGaret);
        PartyJoin_Say(MsgPartyJoinGaretCount);
      }
    }
    break;
  case JOIN_GARET:
    if (sinceArrival > 0 && ((mystery->aiActionIndex & MYSTERY_ENRAGED) != 0 ||
                             sinceArrival >= IVAN_LATEST_ROUNDS)) {
      battle->joinStage = JOIN_IVAN;
      if (PartyJoin_Arrive(IVAN, ELEMENT_JUPITER, 0, BREAK_WHOLE, 0)) {
        PartyJoin_Say(MsgPartyJoinIvanArrives);
        PartyJoin_Say(MsgPartyJoinIvanArrives2);
        PartyJoin_Say(MsgPartyJoinMysteryProphecyIvan);
        PartyJoin_Say(MsgPartyJoinIvanForesee);
        PartyJoin_Say(MsgPartyJoinIvanNotToday);
        PartyJoin_SayKeyLine(MsgPartyJoinMysteryNotAlone);
        PartyJoin_SayKeyLine(MsgPartyJoinMysteryNotAlone2);
        PartyJoin_RunUnison();
      }
    }
    break;
  }
#endif
}

/// Ends her Kaiserdammerung turn once it has played, so only that blow leaves
/// Isaac at exactly 1 HP. Called by Battle_Run after every action.
/// Falling Wind's second part (Ashfall): after its storm, if the caster still
/// stands, an enemy remains and an ally is down, the leaves settle on the
/// fallen and every one rises at half HP (ABILITY_FALLING_WIND_REVIVE),
/// played at once as its own action. With nobody down it passes quietly.
/// Falling Wind's revive aims at every ally but lands only on the fallen:
/// the plan keeps the downed targets alone, each sure to rise, so the
/// living get no "no effect" line and no 60% roll by distance holds the
/// fallen down. Called by BattleTurn_Build for ABILITY_FALLING_WIND_REVIVE.
void FallingWind_KeepFallen(struct BattleTurn *plan) {
  s32 from, to = 0;

  for (from = 0; from < plan->targetCount; from++) {
    if (Unit_GetFar(plan->targetIds[from])->hp != 0)
      continue;
    plan->targetIds[to] = plan->targetIds[from];
    plan->targetOffset[to] = plan->targetOffset[from];
    plan->targetMultiplier[to] = plan->targetMultiplier[from];
    plan->targetCritical[to] = plan->targetCritical[from];
    plan->targetHit[to] = 1;
    to++;
  }
  plan->targetCount = to;
}

static void FallingWind_RunAfterAction(void) {
  struct BattleWork *battle = gBattleWork;
  struct BattleTurn *turn = &battle->turn;
  struct BattleAction request;
  s32 place, downed;

  if (turn->command != COMMAND_PSYNERGY ||
      turn->abilityId != ABILITY_FALLING_WIND ||
      turn->failure != TURN_FAILURE_NONE)
    return;
  if (Unit_GetFar(turn->unitId)->hp == 0 ||
      BattleUnit_ListLiving(BATTLE_SIDE_MASK_ENEMIES, 0) == 0)
    return;
  downed = -1;
  for (place = 0; battle->partyUnits[place] != BATTLE_UNIT_LIST_END; place++) {
    if (Unit_GetFar(battle->partyUnits[place])->hp == 0) {
      downed = place;
      break;
    }
  }
  if (downed < 0)
    return;
  Iwram_ClearWords(&request, sizeof(request));
  request.unitId = turn->unitId;
  request.command = COMMAND_PSYNERGY;
  request.parameter = ABILITY_FALLING_WIND_REVIVE;
  request.target = downed;
  request.range = Ability_Get(ABILITY_FALLING_WIND_REVIVE)->range;
  BattleStaging_DispatchAction(&request, 10);
}

void PartyJoin_RunAfterAction(void) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle = gBattleWork;

  if (battle->joinBrink == BRINK_STRIKING) {
    battle->joinBrink = BRINK_NONE;
    battle->joinEdge = 1;
  }
  // Isaac alone at 1 HP: the battlefield sinks into darkness.
  if (battle->joinEdge != 0 && battle->joinStage == JOIN_ALONE)
    battle->joinGloomTarget = GLOOM_ALONE;
#endif
  FallingWind_RunAfterAction();
}

/// Eases the gloom one frame toward where the story has it and returns it,
/// 0 (lit) to 256 (black). Sets *repaint while the backdrop must write its
/// colours to the screen: while there is gloom, and on the frame it lifts.
/// Called by Mystery_StepBackdropGlow every frame of her battle.
s32 PartyJoin_StepGloom(s32 *repaint) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle = gBattleWork;
  s32 gloom = battle->joinGloom;
  s32 target = battle->joinGloomTarget;

  if (gloom < target) {
    gloom += GLOOM_STEP;
    if (gloom > target)
      gloom = target;
  } else if (gloom > target) {
    gloom -= GLOOM_STEP;
    if (gloom < target)
      gloom = target;
  }
  battle->joinGloom = gloom;
  *repaint = gloom != 0 || battle->joinGloomShown != 0;
  battle->joinGloomShown = gloom;
  return gloom;
#else
  *repaint = 0;
  return 0;
#endif
}

/// The HP damage a blow or an ability does to a unit at hp, as
/// BattleAbility_ApplyToTarget has worked it out, so the number shown is the
/// HP really lost. In the "???" battle: during her scripted Kaiserdammerung,
/// exactly enough to leave Isaac 1 HP; and while he is alone, never enough to
/// fell him (a close call sets joinEdge for the darkened backdrop; it does
/// not bring Mia in before the third round).
/// Every other battle and unit keeps its damage.
s32 PartyJoin_ClampDamage(s32 targetId, s32 hp, s32 amount) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle = gBattleWork;

  if (targetId < 0 || targetId > ALLY_MAX || battle->isLink != 0)
    return amount;
  if (battle->joinBrink == BRINK_STRIKING) {
    amount = hp - 1;
  } else if (battle->joinStage == JOIN_ALONE && amount >= hp &&
             PartyJoin_FindMystery() >= 0) {
    amount = hp - 1;
    battle->joinEdge = 1;
  }
  if (amount < 0)
    amount = 0;
#endif
  return amount;
}
