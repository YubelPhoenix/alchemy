/// @file
/// "You're not alone": the "???" commander's battle in Vale (Ashfall). She
/// binds Garet, Ivan and Mia before the fight (Vale_TalkToMysteryLeader), so
/// Isaac starts alone; during the battle his friends break free one by one
/// and join him, as Zidane's friends do in Final Fantasy IX's Pandemonium.
///
/// The fight:
///  1. Isaac fights her alone. While he is alone he cannot fall: a blow that
///     would fell him leaves him at 1 HP instead (PartyJoin_ClampDamage).
///  2. Her turn in RESCUE_ROUND is Gotterkanone: she speaks, and the blow leaves him at exactly 1 HP; the number shown is the
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
/// Each arrival runs in from off the battlefield to their place, the way the
/// party runs off when it flees, but backwards, with a hop and the camera
/// turned to the party. They come in at full HP and PP. Getting a unit into
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
#define RESCUE_ROUND 2
/// The song from Garet's arrival on. Until then the battle plays the song
/// Vale_TalkToMysteryLeader chooses for it, with no break: through Isaac
/// alone, her Gotterkanone and Mia's rescue. While that is this same song,
/// it plays on without starting again.
#define FULL_PARTY_SONG MUS_FUSION_DRAGON_BATTLE
/// Garet arrives once "???" is below this percent of her HP, or this many
/// rounds after Mia, whichever is first.
#define GARET_BELOW_PERCENT 75
#define GARET_LATEST_ROUNDS 4
/// Ivan arrives when she awakens, or this many rounds after Garet.
#define IVAN_LATEST_ROUNDS 5
/// Frames an arrival takes to run in, and frames of the camera's turn first.
#define ARRIVAL_RUN_FRAMES 40
#define ARRIVAL_CAMERA_FRAMES 20

/// Pure Ply, two after Ply in abilities.c (ability_ids.h names only Ply).
#define ABILITY_PURE_PLY (ABILITY_PLY + 2)

/// An action's target is a place on a side, not a unit id: bit 7 clear is
/// the party's side, and Isaac, who starts alone, is its place 0.
#define TARGET_ISAAC 0

/// The battle's state, kept in BattleWork's spare bytes, which Battle_Run
/// clears as every battle starts and no other code uses.
/// The rounds played so far.
#define joinRound unusedAfterEscapes
/// How far the story has gone (enum JoinStage).
#define joinStage unusedAfterChannels[0]
/// Her Gotterkanone turn (enum JoinBrink): it leaves Isaac 1 HP.
#define joinBrink unusedAfterChannels[1]
/// The round the last arrival came in.
#define joinLastArrival unusedAfterPlacement[0]
/// Set when a blow left Isaac, alone, at 1 HP: the rescue follows it.
#define joinEdge unusedAfterPlacement[1]

enum JoinBrink {
  BRINK_NONE = 0,    ///< not this round
  BRINK_PENDING = 1, ///< her next turn is Gotterkanone
  BRINK_STRIKING = 2 ///< her Gotterkanone is being played
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

/// Frames a line stays up, once typed, before a press can move on.
#define SAY_HOLD_FRAMES 30

/// Shows one line of the story as the battle's own text, at the bottom of the
/// screen with no window (two lines at most), and waits for the player. Once
/// typed it stays up SAY_HOLD_FRAMES, and only a fresh press moves on, so a
/// button held or mashed through the battle cannot skip the story. (A window
/// such as the Djinn tutorial's needs its font, which only that battle
/// loads: WindowSystem_InitBattleFar.)
static void PartyJoin_Say(s32 message) {
  MessageArgument_ClearAllFar();
  BattleMessage_ShowAndWaitFar(message);
  WaitFrames(SAY_HOLD_FRAMES);
  while (gKeysHeld & KEY_ADVANCE)
    WaitFrames(1);
  BattleMessage_WaitForAdvance();
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

/// Brings character unitId into the battle at the party's next place: they
/// run in from off the battlefield, with a hop, and turn to face the enemy.
/// Returns 0 if they could not join (already fighting, or no place left).
static s32 PartyJoin_Arrive(s32 unitId) {
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

  // The camera on the party; then the sprite is made, set three times as far
  // out as the spot (where the party runs to when it flees,
  // BattleMotion_SetupEscapeObject), and sent running in to it with a hop.
  PartyJoin_FaceParty(ARRIVAL_CAMERA_FRAMES);
  BattleObject_Put();
  actor = battleObject->actor;
  if (actor != NULL) {
    actor->x.fixed = battleObject->anchorX * 3;
    actor->z.fixed = battleObject->anchorZ;
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

  // Their Djinn on standby count toward summons, as at the battle's start.
  DjinnRecovery_Reconcile();
  BattleSummon_UpdateAvailability();
  if (((struct BattleSummonState *)Djinn_GetRecoveryTableFar(
           DJINN_RECOVERY_PARTY))
          ->availableMask != 0)
    battle->partyStatus = PARTY_STATUS_SUMMONS;
  else
    battle->partyStatus = PARTY_STATUS_NO_SUMMONS;

  // The party status window takes its width from the party size.
  PartyJoin_WidenStatusWindow();

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

/// End of a round that left Isaac, alone, at 1 HP (her Gotterkanone, or a
/// blow that would have felled him): she speaks; Mia breaks free, runs in
/// and heals him.
static void PartyJoin_RunRescue(void) {
  struct BattleWork *battle = gBattleWork;

  battle->joinStage = JOIN_MIA;
  battle->joinEdge = 0;
  battle->joinBrink = BRINK_NONE;
  WaitFrames(40);
  PartyJoin_Say(MsgPartyJoinMysteryAlone);
  PartyJoin_Say(MsgPartyJoinMysteryAlone2);
  WaitFrames(30);

  if (PartyJoin_Arrive(MIA) == 0)
    return;
  PartyJoin_Say(MsgPartyJoinMiaArrives);
  PartyJoin_Say(MsgPartyJoinMiaArrives2);
  PartyJoin_Act(MIA, COMMAND_PSYNERGY, ABILITY_PURE_PLY, TARGET_ISAAC);
  PartyJoin_Settle();
  PartyStatus_DrawFar(battle->partyStatus);
  PartyJoin_Say(MsgPartyJoinMysteryReacts);
  PartyJoin_Say(MsgPartyJoinMiaAnswers);
  PartyJoin_Say(MsgPartyJoinMiaAnswers2);
}

/// Her turn in RESCUE_ROUND: says her line and fades the music, and returns
/// 1 while the turn should be Gotterkanone. Called by
/// BossAI_MysteryChooseSlot at each of her picks; the line plays once.
s32 PartyJoin_TakeBrinkTurn(void) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle = gBattleWork;

  if (battle->joinBrink == BRINK_NONE || battle->joinStage != JOIN_ALONE)
    return 0;
  if (battle->joinBrink == BRINK_PENDING) {
    battle->joinBrink = BRINK_STRIKING;
    PartyJoin_Say(MsgPartyJoinMysteryBrink);
    MessageArgument_ClearAllFar();
  }
  return 1;
#else
  return 0;
#endif
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
    // Her next turn is the Gotterkanone; the round it lands in, or any
    // round that left Isaac at 1 HP, ends with Mia.
    if (battle->joinEdge != 0 || battle->joinRound >= RESCUE_ROUND)
      PartyJoin_RunRescue();
    else if (battle->joinRound == RESCUE_ROUND - 1)
      battle->joinBrink = BRINK_PENDING;
    break;
  case JOIN_MIA:
    if (mystery->hp * 100 < mystery->hpMax * GARET_BELOW_PERCENT ||
        sinceArrival >= GARET_LATEST_ROUNDS) {
      battle->joinStage = JOIN_GARET;
      if (PartyJoin_Arrive(GARET)) {
        if (gSaveBlock.battleMusic != FULL_PARTY_SONG)
          Sound_PlaySongFar(FULL_PARTY_SONG);
        PartyJoin_Say(MsgPartyJoinGaretArrives);
        PartyJoin_Say(MsgPartyJoinGaretArrives2);
        PartyJoin_Say(MsgPartyJoinGaretArrives3);
      }
    }
    break;
  case JOIN_GARET:
    if (sinceArrival > 0 && ((mystery->aiActionIndex & MYSTERY_ENRAGED) != 0 ||
                             sinceArrival >= IVAN_LATEST_ROUNDS)) {
      battle->joinStage = JOIN_IVAN;
      if (PartyJoin_Arrive(IVAN)) {
        PartyJoin_Say(MsgPartyJoinIvanArrives);
        PartyJoin_Say(MsgPartyJoinIvanArrives2);
        PartyJoin_Say(MsgPartyJoinMysteryNotAlone);
        PartyJoin_Say(MsgPartyJoinMysteryNotAlone2);
      }
    }
    break;
  }
#endif
}

/// Ends her Gotterkanone turn once it has played, so only that blow leaves
/// Isaac at exactly 1 HP. Called by Battle_Run after every action.
void PartyJoin_RunAfterAction(void) {
#if PARTY_JOIN_ENABLED
  struct BattleWork *battle = gBattleWork;

  if (battle->joinBrink == BRINK_STRIKING) {
    battle->joinBrink = BRINK_NONE;
    battle->joinEdge = 1;
  }
#endif
}

/// The HP damage a blow or an ability does to a unit at hp, as
/// BattleAbility_ApplyToTarget has worked it out, so the number shown is the
/// HP really lost. In the "???" battle: during her scripted Gotterkanone,
/// exactly enough to leave Isaac 1 HP; and while he is alone, never enough to
/// fell him (a blow that would sets joinEdge, and the rescue follows it).
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
