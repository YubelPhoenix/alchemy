#!/usr/bin/env python3
"""Static story-continuity guard for Ashfall's optional encounter logic.

This catches regressions in character field sprites, important actor speakers,
one-time encounter flags, and explicit choice-message cursor resets. It cannot
substitute for playing every branch in the built ROM.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORY = ROOT / "tools" / "dark_story"
SCENES = ROOT / "games" / "tbs" / "src" / "scene"

checks = 0


def require(condition: bool, explanation: str) -> None:
    global checks
    if not condition:
        raise SystemExit(f"ASHFALL STORY CONTRACT FAILURE: {explanation}")
    checks += 1


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def scene(name: str) -> str:
    return (SCENES / name).read_text(encoding="utf-8")


def function(source: str, name: str) -> str:
    """Get the function body, including nested if/else blocks, without a C parser."""
    match = re.search(
        r"\b(?:static\s+)?(?:void|s32|int|const\s+struct\s+(?:ActorTemplate|Trigger)\s*\*)\s*"
        + re.escape(name)
        + r"\s*\(\s*void\s*\)\s*\{",
        source,
    )
    require(match is not None, f"Missing expected scene function: {name}")
    start = match.end()
    depth = 1
    for index in range(start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index]
    raise SystemExit(f"ASHFALL STORY CONTRACT FAILURE: unclosed function {name}")


def template(source: str, name: str) -> str:
    match = re.search(
        r"\bstruct\s+ActorTemplate\s+" + re.escape(name)
        + r"\s*\[\s*\]\s*=\s*\{(.*?)\n\};",
        source,
        re.S,
    )
    require(match is not None, f"Missing template: {name}")
    return match.group(1)


def messages(filename: str) -> dict[str, str]:
    result = {}
    for line in (STORY / filename).read_text(encoding="utf-8").splitlines():
        if not re.match(r"^N\d+\t", line):
            continue
        parts = line.split("\t", 2)
        require(len(parts) == 3, f"Malformed message TSV: {filename} {line[:25]}")
        key, context, value = parts
        require(key not in result, f"Duplicate custom message in {filename}: {key}")
        require(bool(context), f"Missing context for {filename}: {key}")
        result[key] = value
    return result


def assert_speaker(body: str, message: str, actor: str) -> None:
    pattern = (
        r"Event_SetMessageId\(" + re.escape(message) + r"\);\s*"
        r"(?:GameFlag_Set\([^)]+\);\s*)?"
        r"Event_ShowMessage(?:ThenWait|AndWait)\("
        + re.escape(actor) + r"\s*,"
    )
    require(re.search(pattern, body) is not None, f"Speaker mismatch: {message} must be {actor}")


def check_visual_identity() -> None:
    """Ash Jenna uses the supplied sprite art in all five appearances."""
    for file, table in (
        ("lamakan_desert.c", "gLamakanDesertManticoreActorTemplates"),
        ("tolbi.c", "gTolbiActorTemplates"),
        ("suhalla_gate.c", "gSuhallaGateCheckpointActorTemplatesAfterAudience"),
        ("vale.c", "gVale_ActorTemplatesAfterKalay"),
        ("lalivero.c", "gLaliveroActorTemplatesAfterLighthouse"),
    ):
        require(re.search(r"\{\s*SPRITE_ASH_JENNA\s*,", template(scene(file), table)) is not None,
                f"{file}: Ash Jenna must use her supplied overworld sprite")
    lamakan = scene("lamakan_desert.c")
    require(re.search(r"ACTOR_LAMAKAN_ASH_JENNA\s*=\s*ACTOR_FIRST_PLACED\s*\+\s*2\b", lamakan) is not None,
            "Lamakan Ash Jenna must be third placed NPC (10), not party Jenna (5)")
    require("if (gSaveBlock.sceneId != (s32)&SceneId_LamakanDesertManticore)" in lamakan
            and "LamakanDesert_AshJennaWatches();" in lamakan,
            "Lamakan must keep Ash Jenna present and stage her before Manticore")
    ids = read("games/tbs/include/sprite_ids.h")
    sprites = read("games/tbs/src/graphics/sprite/sprites.tsv")
    layout = read("games/tbs/src/graphics/sprite/layout.tsv")
    workflow = read(".github/workflows/build-golden-sun-dialogue.yml")
    require("SPRITE_ASH_JENNA = 0x5e" in ids, "Ash Jenna sprite id is missing")
    require(re.search(r"^SPR_094\t32\t32\t", sprites, re.M) is not None,
            "SPR_094 must be a real field sprite")
    require("SPR_094" in layout.splitlines(), "SPR_094 must be packed into the ROM")
    require("python3 tools/dark_story/build_ash_jenna_overworld.py" in workflow,
            "CI must generate Ash Jenna's supplied overworld art")
    for n in range(1, 5):
        require((ROOT / f"assets/ash_jenna/overworld_{n}.png").exists(),
                f"Missing supplied Ash Jenna pose {n}")
    require(
        re.search(r"// Kegare impersonates Mia;.*?\{\s*SPRITE_WOMAN_IN_BLUE_DRESS\s*,\s*CONDITION_ALWAYS",
                  template(scene("vault_revisit.c"), "gVaultRevisit_ActorTemplates"), re.S) is not None,
        "Kegare must still visibly mimic Mia",
    )


def check_flags_and_quest_order() -> None:
    flags = read("games/tbs/include/flags.h")
    dark = re.findall(r"^\s*#define\s+(FLAG_DARK_\w+)\s+(0x[0-9a-fA-F]+)\b", flags, re.M)
    require(len(dark) >= 25, "Expected persistent Ashfall flags were removed")
    values = [int(v, 16) for _k, v in dark]
    require(len(set(values)) == len(values), "Two Ashfall flags share the same bit")
    required = {
        "FLAG_DARK_ASH_JENNA_LAMAKAN_MET", "FLAG_DARK_FINALE_DONE",
        "FLAG_DARK_ASH_JENNA_TOLBI", "FLAG_DARK_ASH_JENNA_LALIVERO",
        "FLAG_DARK_MANTICORE_RETURN_SEEN", "FLAG_DARK_ASH_GATE_FOUGHT",
        "FLAG_DARK_MINER_STAYED", "FLAG_DARK_HEART_BEATEN",
        "FLAG_DARK_KEGARE_BEATEN",
    }
    require(required.issubset({k for k, _v in dark}), "An Ashfall story flag is missing")

    lamakan = scene("lamakan_desert.c")
    finale = function(lamakan, "LamakanDesert_AshJennaFinale")
    check = function(lamakan, "LamakanDesert_ManticoreAftermath")
    require("GameFlag_Set(FLAG_DARK_MANTICORE_RETURN_SEEN)" in check and
            "Event_ShowMessage" not in check,
            "The Manticore aftermath must only record the return, without discarded dialogue")
    require("MsgDarkManticoreMiaGloat" not in lamakan,
            "The discarded Mia anger subplot must not play")
    require("Event_AskYesNo" not in finale and
            "FLAG_DARK_ASH_JENNA_ACCEPTED" not in finale and
            "FLAG_DARK_ASH_JENNA_REFUSED" not in finale,
            "Ash Jenna cannot recruit Isaac or trigger a Lamakan choice")
    assert_speaker(finale, "MsgDarkFinaleJenna2", "ACTOR_LAMAKAN_ASH_JENNA")
    require("MsgDarkFinaleJennaThreat" in finale and
            "GameFlag_Set(FLAG_DARK_FINALE_DONE)" in finale,
            "The linear Lamakan scene must end cleanly")

    tolbi = scene("tolbi.c")
    meeting = function(tolbi, "Tolbi_MeetAshJenna")
    require("MsgDarkTolbiJennaProtest" in meeting and
            "GameFlag_Set(FLAG_DARK_ASH_JENNA_TOLBI)" in meeting,
            "Tolbi's linear Ash Jenna encounter must complete")
    for obsolete in ("MsgDarkTolbiJennaAccepted", "MsgDarkTolbiJennaRefused",
                     "MsgDarkMiaTolbiConcern", "FLAG_DARK_ASH_JENNA_ACCEPTED",
                     "FLAG_DARK_ASH_JENNA_REFUSED"):
        require(obsolete not in meeting, f"Tolbi retained an obsolete branch: {obsolete}")

    lalivero = scene("lalivero.c")
    coda = function(lalivero, "Lalivero_TalkToAshJenna")
    init = function(lalivero, "Lalivero_Initialize")
    require("FLAG_DARK_ASH_JENNA_TOLBI" in init and
            "FLAG_DARK_ASH_JENNA_LALIVERO" in init,
            "Lalivero must remain an optional follow-up to Tolbi")
    require("MsgDarkLaliveroIsaacInnocents" in coda and
            "MsgDarkLaliveroAshStrangers" in coda and
            "GameFlag_Set(FLAG_DARK_ASH_JENNA_LALIVERO)" in coda,
            "Lalivero's linear coda must end once")
    require("FLAG_DARK_ASH_JENNA_ACCEPTED" not in coda and
            "FLAG_DARK_ASH_JENNA_REFUSED" not in coda,
            "Lalivero cannot assume a discarded choice")
    require("ACTOR_LALIVERO_ASH_JENNA" not in
            template(lalivero, "gLaliveroActorTemplates"),
            "Ash Jenna must not appear in pre-Venus Lalivero")

    vale = scene("vale.c")
    gate = scene("suhalla_gate.c")
    # Vale_Initialize contains #if/#else branches. The lightweight function()
    # extractor counts braces from both mutually exclusive C branches, so it
    # cannot reliably parse that function. Validate the exact gating block
    # instead, including both optional bosses being hidden before Colosso.
    require(
        re.search(
            r"if\s*\(\s*GameFlag_Get\(FLAG_KALAY_REACHED\)\s*!=\s*0\s*&&\s*"
            r"GameFlag_Get\(FLAG_COLOSSO_OVER\)\s*==\s*0\s*\)\s*\{\s*"
            r"Actor_SetPosition\(ACTOR_ASH_JENNA_AFTER_KALAY,\s*"
            r"PIXELS\(0\),\s*PIXELS\(0\)\);\s*"
            r"Actor_SetPosition\(ACTOR_MYSTERY_LEADER_AFTER_KALAY,\s*"
            r"PIXELS\(0\),\s*PIXELS\(0\)\);",
            vale, re.S,
        ) is not None,
        "Vale optional bosses must remain hidden until after Colosso",
    )
    require("SuhallaGate_AshJennaBlocksPassage" not in gate,
            "Suhalla's Ash Jenna boss must not trigger just by crossing")
    require("TRIGGER_TALK, ACTOR_ASH_JENNA" in gate,
            "Suhalla's Ash Jenna boss must remain talk-triggered")


def check_optional_battles() -> None:
    kolima = scene("kolima.c")
    heart = function(kolima, "Kolima_TalkToHeart")
    entry = function(kolima, "Kolima_Initialize")
    aftermath = function(kolima, "Kolima_HeartAftermath")
    require("Event_SetDefeatDestination" in heart
            and "Event_SetAfterBattleDestination" in heart,
            "Heart must send a defeat to the restart point (Sanctum), not back to Kolima")
    require("GameFlag_Clear(FLAG_DARK_HEART_FOUGHT)" in entry
            and "gSaveBlock.sequenceResult == -1" in entry,
            "A lost Heart battle must allow a retry")
    require("GameFlag_Set(FLAG_DARK_HEART_BEATEN)" in aftermath,
            "Only Heart's successful aftermath marks her defeated")

    tolbi = scene("tolbi.c")
    vault = scene("vault_revisit.c")
    kegare = function(vault, "VaultRevisit_TalkToKegare")
    require("Event_SetDefeatDestination" in kegare
            and "Event_SetAfterBattleDestination" in kegare,
            "Kegare must send a defeat to the restart point (Sanctum), not back to Vault")
    seq = (ROOT / "games/tbs/src/overworld/overworld/sequence_manager.c").read_text()
    require("Event_SetDefeatDestination(-1, -1)" in kegare
            and all(f in seq for f in ("FLAG_DARK_ASH_VALE_PENDING", "FLAG_DARK_ASH_GATE_PENDING",
                                       "FLAG_DARK_HEART_FOUGHT", "FLAG_DARK_KEGARE_PENDING")),
            "A superboss defeat must clear its fight flags")
    require("GameFlag_Clear(FLAG_DARK_KEGARE_FOUGHT)" in vault
            and "gSaveBlock.sequenceResult > 0" in vault,
            "A lost Kegare battle must allow retry")



def check_mystery_rescue_encounter() -> None:
    """Guard Isaac's solo opening, three companion rescues, and dialogue."""
    vale = scene("vale.c")
    approach = function(vale, "Vale_TalkToMysteryLeader")
    aftermath = function(vale, "Vale_MysteryLeaderAftermath")
    for name in ("GARET", "IVAN", "MIA"):
        require(f"Party_RemoveMember({name});" in approach,
                f"Mystery duel must bench {name}")
        require(f"Party_AddMember({name});" in aftermath,
                f"Mystery aftermath must restore {name}")
    # Garet, Ivan and Mia are not on the map (only the leader walks the
    # field), so her bind is shown as a screen-wide flash before their lines.
    require("PaletteFade_SetTarget(RGB(31, 31, 31), PALETTES_ALL);" in approach,
            "Missing the visible flash of her Psynergy bind")
    require(approach.index("PaletteFade_SetTarget(RGB(31, 31, 31), PALETTES_ALL);")
            < approach.index("Event_SetMessageId(MsgDarkMysteryGaretBound)"),
            "Her bind must flash before the companions speak")
    require(approach.index("Event_SetMessageId(MsgDarkMysteryGaretBound)")
            < approach.index("Party_RemoveMember(GARET)"),
            "Companions must respond before Isaac fights alone")
    require(aftermath.index("Party_AddMember(MIA);")
            < aftermath.index("Event_SetMessageId(MsgDarkMystery15)"),
            "Restore Mia before showing the victory sequence")
    require("Event_SetMessageId(MsgDarkMysteryMiaAfter)" in aftermath,
            "Mia's thirty-year foreshadowing is missing")
    require("Event_SetDefeatDestination(-1, -1);" in approach
            and "gSaveBlock.sequenceResult == -1" in aftermath,
            "Solo duel must retain the safe defeat/restart flow")
    sequence = read("games/tbs/src/overworld/overworld/sequence_manager.c")
    defeat = sequence.split("void Scene_ReturnFromSequence(s32 result)", 1)[1]
    defeat = defeat.split("} else {\n    // An after-battle destination", 1)[0]
    require("GameFlag_GetFar(FLAG_DARK_MYSTERY_PENDING)" in defeat
            and all(f"Party_AddMember({name});" in defeat
                    for name in ("GARET", "IVAN", "MIA"))
            and "GameFlag_ClearFar(FLAG_DARK_MYSTERY_PENDING);" in defeat,
            "Defeat must restore Garet, Ivan, and Mia before the Sanctum return")
    require(defeat.index("Party_AddMember(MIA);")
            < defeat.index("if (result == -1) {"),
            "Restore all companions before loading either destination scene")

    # Author-locked Vale exchange: pin both original Git blobs from a88d3ad.
    # Editing the reference and the live table together must not bypass this guard.
    # A new approved revision requires explicit authorization and updated pins.
    for filename, approved_blob in (
        ("phase118_mystery_leader.tsv", "1b4e886fa1178952b3bd1a463a7fbc0890728f77"),
        ("approved_mystery_prebattle.txt", "57c93bfb669016e5b635b2d63c0af05a23cb4109"),
    ):
        content = read("tools/dark_story/" + filename).encode("utf-8")
        header = f"blob {len(content)}\0".encode("ascii")
        require(hashlib.sha1(header + content).hexdigest() == approved_blob,
                f"Author-locked Vale dialogue changed without approval: {filename}")

    lines = messages("phase118_mystery_leader.tsv")
    require({f"N{i}" for i in range(356, 395)} == set(lines),
            "Mystery exchange requires N356-N394 without missing lines")
    require("Your friends are bound." not in lines["N369"],
            "Binding must not be announced before the screen flash")
    # Optional superbosses have no required defeat order. This pre-battle
    # exchange assumes previous sightings or attempts, not victories.
    # These approved lines must not be rewritten without explicit approval.
    approved_prebattle = {}
    for row in read("tools/dark_story/approved_mystery_prebattle.txt").splitlines():
        if not row.startswith("N"):
            continue
        parts = row.split("\t", 2)
        require(len(parts) == 3, "Malformed approved Isaac/??? dialogue")
        approved_prebattle[parts[0]] = parts[2]
    require(set(approved_prebattle) == {f"N{i}" for i in range(356, 370)} | {"N387"},
            "Approved Isaac/??? pre-battle reference is incomplete")
    for message_id, approved_text in approved_prebattle.items():
        require(lines[message_id] == approved_text,
                f"Isaac/??? pre-battle dialogue changed without approval: {message_id}")
    require("Event_SetMessageId(MsgDarkMysteryIsaacSuspects);" in approach
            and "Event_SetMessageId(MsgDarkMysteryGaretAfter);" in aftermath
            and "Event_SetMessageId(MsgDarkMysteryIsaacAfter);" in aftermath,
            "Isaac's discovery and full-party aftermath must be staged")
    for key, value in lines.items():
        for page in value.split("{page_break}"):
            visible = re.sub(r"\{[^{}]*\}", "", page)
            dialogue_lines = visible.split(r"\n")
            require(len(dialogue_lines) <= 3,
                    f"Mystery dialogue {key} exceeds three lines")
            for dialogue in dialogue_lines:
                require(len(dialogue) <= 27,
                        f"Mystery dialogue {key} exceeds 27 characters")

    enemies = read("games/tbs/src/game/enemies.c")
    boss = enemies.split("// ???, Heart's Dark Adept leader:", 1)[1]
    boss = boss.split("    },", 1)[0]
    require(".hp = 10000," in boss and ".turns = 1," in boss,
            "Mystery's four-person rescue battle HP/turn balance regressed")
    # She opens against Isaac alone, then faces Mia, Garet, and Ivan.
    # Her own attacks remain non-lethal/non-sealing in the scripted opener.
    # P-Storm uses the new summon presentation, with its original balance.
    require(".abilities = {ABILITY_GOTTERKANONE, ABILITY_P_STORM_SUMMON, ABILITY_P_VORTEX, "
            "ABILITY_PERFECTI_EXPLOSION, ABILITY_GLEPNIR, ABILITY_EX_GOTTERKANONE, "
            "ABILITY_STERNBRECHER, ABILITY_RANSNETZ}," in boss,
            "Solo duel must keep the Mystery Leader's own non-lethal, non-sealing moveset")
    # Validate the new story mechanics, not just the old solo setup.
    join = read("games/tbs/src/battle/party_join.c")
    boss_ai = read("games/tbs/src/battle/battle/boss_ai.c")
    require("#define PARTY_JOIN_ENABLED 1" in join
            and "#define RESCUE_ROUND 3" in join
            and "if (battle->joinRound >= RESCUE_ROUND)" in join,
            "Mia must arrive only after three solo rounds")
    # Each arrival names the friend first, then their element and the gloom
    # their light leaves.
    for name in ("MIA", "GARET", "IVAN"):
        require(f"PartyJoin_Arrive({name}," in join,
                f"Mystery battle must bring {name} into the live battle")
    require(join.index("PartyJoin_Arrive(MIA,") <
            join.index("PartyJoin_Arrive(GARET,") <
            join.index("PartyJoin_Arrive(IVAN,"),
            "Rescue companions must arrive Mia, Garet, then Ivan")
    require("#define GARET_BELOW_PERCENT 75" in join
            and "#define IVAN_LATEST_ROUNDS 5" in join
            and "mystery->hpMax * GARET_BELOW_PERCENT" in join,
            "Mystery's companion arrival thresholds changed unexpectedly")
    require("#define SAY_HOLD_FRAMES 150" in join
            and "#define SAY_KEY_LINE_FRAMES 180" in join
            and "#define SAY_QUIET_FRAMES 15" in join
            and "TextPrinter_AllFinishedFar()" in join
            and "gKeysHeld & (KEY_ADVANCE | KEY_B)" in join,
            "Rescue text must remain readable and resist held-button skipping")
    require("PartyJoin_SayKeyLine(MsgMysteryEnraged)" in boss_ai,
            "Mystery's awakened revelation needs protected reading time")
    battle_lines = messages("phase_fight_together.tsv")
    # The expanded fight includes each companion's answer to the leader's
    # prophecy; validate the complete set rather than the earlier 12-line cut.
    require(set(battle_lines) == {f"N{i}" for i in range(399, 418)},
            "Mystery rescue must retain all 19 indexed battle dialogue lines")
    for context in ("MsgPartyJoinMysteryProphecyMia", "MsgPartyJoinMiaForgotten",
                    "MsgPartyJoinMysteryProphecyGaret", "MsgPartyJoinGaretCount",
                    "MsgPartyJoinMysteryProphecyIvan", "MsgPartyJoinIvanForesee",
                    "MsgPartyJoinIvanNotToday"):
        require(f"PartyJoin_Say({context})" in join,
                f"Mystery rescue must actually play {context}")
    for key, value in battle_lines.items():
        require("{page_break}" not in value and "{end_" not in value,
                f"Mystery battle {key} must use plain battle text")
        short_lines = value.split(r"\n")
        require(len(short_lines) <= 2,
                f"Mystery battle {key} exceeds the two-line battle window")
        require(all(len(line) <= 27 for line in short_lines),
                f"Mystery battle {key} exceeds 27 characters per line")
    require("We couldn't do a thing" not in lines["N388"]
            and "I kept my word" not in lines["N371"],
            "Post-battle dialogue must reflect companions breaking free")

    table = read("games/tbs/src/game/abilities.c")
    own = table.split("// Gotterkanone: Mystery Leader (ability ID 519).", 1)[1]
    own = own.split("// Sarah's pike techniques", 1)[0]
    rows = re.findall(r"\{\s*\.targetMode.*?\}", own, re.S)
    require(len(rows) == 8, f"Mystery Leader needs 8 ability rows after Gotterkanone's, found {len(rows)}")
    for row in rows:
        require(".ppCost" not in row, "A Mystery Leader attack costs PP, so it would count as Psynergy")
        for banned in ("INSTANT_DEATH", "KILL", "SEAL", "STUN", "SLEEP", "HAUNT"):
            require(banned not in row, f"Mystery Leader attack has a forbidden effect: {banned}")


def check_story_text() -> None:
    # This is a presentation check only; it does NOT certify whether writing
    # is good or whether a visible scene's meaning is earned.
    coda = messages("phase76_lalivero_ash_jenna_coda.tsv")
    require(set(coda) == {f"N{i}" for i in range(300, 319)},
            "Lalivero coda must have N300-N318 with no missing messages")
    for key, value in coda.items():
        pages = value.split("{page_break}")
        for page in pages:
            lines = page.split(r"\n")
            require(len(lines) <= 3, f"Coda {key} exceeds three lines per page")
            for line in lines:
                visible = re.sub(r"\{(?:actor_name:\d+|protagonist_name)\}",
                                 "XXXXXXXX", line)
                visible = re.sub(r"\{[^{}]*\}", "", visible)
                require(len(visible) <= 27,
                        f"Coda {key} overflows: {len(visible)} columns")
        require(re.search(r"\{end_(?:wait|now)\}$", value) is not None,
                f"Coda {key} must terminate explicitly")
    heart = messages("phase38_heart.tsv")
    require("We will meet again" not in heart["N132"],
            "Heart must not promise an unimplemented rematch")


def check_dormant_palette_cache_is_disabled() -> None:
    color = read("games/tbs/src/overworld/overworld/color.c")
    scene_manager = read("games/tbs/src/overworld/overworld/scene_manager.c")
    require("ASH_TINT_BYTES" not in color,
            "Dormant ash tint must not allocate unused EWRAM")
    require("work = AllocHeapSlotEwram(HEAP_SLOT_PALETTE_FADE, sizeof(*work));" in color,
            "Palette fade must use original heap allocation size")
    require("PaletteFade_KeepAshTint" not in scene_manager,
            "Disabled palette renderer must not be scheduled")


def check_mercury_lighthouse_chronology() -> None:
    sequence = read("games/tbs/src/overworld/overworld/sequence_manager.c")
    mercury = scene("mercury_lighthouse_aerie.c")
    state = read("games/tbs/include/world_state.h")
    require("GameFlag_GetFar(FLAG_AREA_VISITED(0x13))" not in sequence,
            "Merely visiting Mercury Lighthouse must not mark its beacon lit")
    require("GameFlag_ClearFar(FLAG_MERCURY_LIGHTHOUSE_LIT)" not in sequence,
            "The genuine Mercury beacon flag must survive area changes")
    require("GameFlag_Set(FLAG_MERCURY_LIGHTHOUSE_LIT);" in mercury,
            "Only Mercury's actual aerie/beacon scene sets its lit state")
    require("FLAG_MERCURY_LIGHTHOUSE_LIT" in state,
            "World-stage weather must read the genuine lit flag")


def check_lalivero_first_postvenus_entry() -> None:
    source = scene("lalivero.c")
    helper = function(source, "Lalivero_IsPostVenusState")
    for requirement in [
        "FLAG_VENUS_LIGHTHOUSE_PARTY_RETURNED",
        "ENTRANCE_FROM_AERIE",
        "ENTRANCE_FROM_AERIE_QUIETLY",
    ]:
        require(requirement in helper,
                "First post-Venus Lalivero must recognize " + requirement)
    require(
        "Lalivero_IsPostVenusState()" in
        function(source, "Lalivero_GetActorTemplates"),
        "Post-Venus actors must be selected before Lalivero_Initialize",
    )
    require(
        "Lalivero_IsPostVenusState()" in
        function(source, "Lalivero_GetTriggers"),
        "Post-Venus event triggers must load on the first return",
    )
    require(
        "GameFlag_Set(FLAG_VENUS_LIGHTHOUSE_PARTY_RETURNED)" in
        function(source, "Lalivero_Initialize"),
        "Post-Venus arrival must save its state after entering",
    )


def check_named_scene_exit_wiring() -> None:
    # Only direct literal requests can be checked without evaluating the C
    # scene interpreter; dynamic, computed, and default exits remain manual.
    edited_scenes = [
        "altin.c", "altin_peak.c", "imil.c", "kolima.c",
        "lalivero.c", "lamakan_desert.c", "mercury_lighthouse_aerie.c",
        "mogall_forest.c", "sol_sanctum_corridor.c",
        "sol_sanctum_elemental_star_room.c", "sol_sanctum_eruption.c",
        "sol_sanctum_luna_sol_rooms.c", "sol_sanctum_statue.c",
        "tolbi.c", "vale.c", "vale_stormy_night.c", "vault.c",
        "vault_revisit.c", "world_map.c",
    ]
    inspected = 0
    for filename in edited_scenes:
        source = scene(filename)
        destinations = set(re.findall(
            r"Import_EventSetExitRequest\(\s*([A-Z_][A-Z0-9_]*)\s*\)",
            source,
        ))
        for destination in destinations:
            require(re.search(
                r"\bSCENE_EXIT\s*\(\s*" + re.escape(destination)
                + r"\s*,", source,
            ) is not None,
                    f"Unmapped named exit in {filename}: {destination}")
            inspected += 1
    require(inspected > 15, "Exit check did not inspect enough source exits")


def check_live_sequential_dialogue() -> None:
    """Guard the sequential scenes the earlier named-message audit missed.

    These scripts start at one named ID and advance through unnamed messages.
    A named-context-only audit can pass while most of the on-screen exchange
    remains vanilla. These checks prove full table coverage, not prose quality.
    """
    imil = function(scene("imil.c"), "Imil_MiaSaysFarewellToApprentices")
    require("Event_SetMessageId(MSGNO(MsgImilMia))" in imil,
            "Mia's Imil farewell must still start at message 05723")
    spoken = re.findall(r"FieldEvent_ShowMessageThenWait\(\s*([^,]+)", imil)
    require(len(spoken) == 21,
            f"Mia's farewell changed: expected 21 spoken lines, got {len(spoken)}")

    farewell_rows = {}
    for line in (STORY / "phase17_imil_mercury_b.tsv").read_text(encoding="utf-8").splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3 and parts[0].isdigit():
            farewell_rows[parts[0]] = parts[2]
    missing = sorted(f"{n:05d}" for n in range(5723, 5744)
                     if f"{n:05d}" not in farewell_rows)
    require(not missing,
            "Live Imil farewell has unrewritten sequential IDs: " + ", ".join(missing))

    goma = function(scene("goma_cave_entrance.c"), "GomaCaveEntrance_IvanRejoins")
    require("Event_SetMessageId(MsgGomaNoUsePsynergy)" in goma,
            "Ivan's Goma Cave rejoin must start at message 05007")
    ivan_rows = {}
    for line in (STORY / "phase_goma_ivan_rejoin.tsv").read_text(encoding="utf-8").splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3 and parts[0].isdigit():
            ivan_rows[parts[0]] = parts[2]
    missing = sorted(f"{n:05d}" for n in range(5008, 5025)
                     if f"{n:05d}" not in ivan_rows)
    require(not missing,
            "Live Goma/Ivan rejoin has unrewritten sequential IDs: " + ", ".join(missing))


def check_integrated_gameplay() -> None:
    """Catch the omission of tested Claude AI, boss stats and sprite facing."""
    ai = read("games/tbs/src/battle/battle/boss_ai.c")
    battle = read("games/tbs/src/battle/battle.c")
    require('#include "battle/boss_ai.c"' in battle,
            "Tactical boss AI implementation not included in battle.c")
    for symbol in ("BOSS_AI_KEGARE", "BOSS_AI_ASH_JENNA", "BOSS_AI_HEART"):
        require(re.search(r"#define\s+" + symbol + r"\s+1\b", ai) is not None,
                f"Missing or disabled tactical boss AI: {symbol}")
    for symbol in ("BossAI_BeginRound", "BossAI_ChooseSlot",
                   "BossAI_ChooseTarget", "BossAI_NoteTurn"):
        require(symbol in ai, f"Missing boss AI lifecycle: {symbol}")
    enemies = read("games/tbs/src/game/enemies.c")
    for comment, hp, defense in (
        ("// Ash Jenna, the optional super boss of Vale", 11000, 90),
        ("// Heart (Chalice), the secret super boss of Kolima", 11500, 100),
        ("// Kegare, the otherworldly demon mimicking Mia", 9500, 80),
    ):
        require(comment in enemies, f"Boss balancing anchor missing: {comment}")
        row = enemies[enemies.index(comment):enemies.index(comment) + 300]
        require(f".hp = {hp}," in row and f".def = {defense}," in row,
                f"Missing balanced boss HP/Defense: {comment}")
    animation = read("games/tbs/src/battle_anim/battle_anim_internal.h")
    volcano = read("games/tbs/src/battle_anim/parts/volcano.c")
    plasma = read("games/tbs/src/battle_anim/parts/plasma.c")
    camera = read("games/tbs/src/battle/battle/setup.c")
    for label, source in (("helper", animation), ("volcano", volcano),
                          ("plasma", plasma)):
        require("BattleCamera_FlipBossesInFrontView" in source,
                f"Missing boss sprite-facing integration: {label}")
    require("flipCaster = 0" in camera,
            "Boss facing reset missing from battle camera")


def main() -> None:
    check_integrated_gameplay()
    check_live_sequential_dialogue()
    check_lalivero_first_postvenus_entry()
    check_named_scene_exit_wiring()
    check_mercury_lighthouse_chronology()
    check_dormant_palette_cache_is_disabled()
    check_visual_identity()
    check_flags_and_quest_order()
    check_optional_battles()
    check_mystery_rescue_encounter()
    check_story_text()
    print(f"Ashfall: {checks} static story contracts passed "
          "(visual/branch playthrough still required).")


if __name__ == "__main__":
    main()
