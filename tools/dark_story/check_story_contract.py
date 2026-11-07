#!/usr/bin/env python3
"""Static story-continuity guard for Ashfall's optional encounter logic.

This catches regressions in character field sprites, important actor speakers,
one-time encounter flags, and explicit choice-message cursor resets. It cannot
substitute for playing every branch in the built ROM.
"""
from __future__ import annotations

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
    lamakan = scene("lamakan_desert.c")
    tolbi = scene("tolbi.c")
    lalivero = scene("lalivero.c")

    # Each antagonist uses a distinct ACTOR_ID but the correct existing
    # *character* sprite. Greyscale is applied at runtime; this is not the
    # user's animation's custom pixel artwork.
    require(
        re.search(r"\{\s*ACTOR_JENNA\s*,\s*IF_FLAG_SET\(FLAG_DARK_ASH_JENNA_LAMAKAN_HERE\)", 
                  template(lamakan, "gLamakanDesertManticoreActorTemplates")) is not None,
        "Lamakan Ash Jenna must use Jenna's recognizable field sprite",
    )
    require(
        re.search(r"\{\s*ACTOR_JENNA\s*,\s*CONDITION_ALWAYS", 
                  template(tolbi, "gTolbiActorTemplates")) is not None,
        "Tolbi Ash Jenna must use Jenna's recognizable field sprite",
    )
    require(
        re.search(r"\{\s*ACTOR_JENNA\s*,\s*CONDITION_ALWAYS", 
                  template(lalivero, "gLaliveroActorTemplatesAfterLighthouse")) is not None,
        "Post-Venus Ash Jenna must use Jenna's recognizable field sprite",
    )
    require(
        re.search(r"// Kegare impersonates Mia;.*?\{\s*SPRITE_WOMAN_IN_BLUE_DRESS\s*,\s*CONDITION_ALWAYS",
                  template(scene("vault_revisit.c"), "gVaultRevisit_ActorTemplates"), re.S) is not None,
        "Kegare must visibly mimic Mia with her own sprite (Mia is in the party)",
    )
    require(
        all(
            f"Actor_ConfigureSpriteColor({actor}, SPRITE_COLOR_ASH)" in source
            for actor, source in [
                ("ACTOR_LAMAKAN_ASH_JENNA", lamakan),
                ("ACTOR_TOLBI_ASH_JENNA", tolbi),
            ]
        ),
        "Alternate Jenna must retain her distinguishable recolor",
    )
    require("SPRITE_COLOR_ASH" in function(lalivero, "Lalivero_TalkToAshJenna")
            or "SPRITE_COLOR_ASH" in lalivero,
            "Alternate Jenna's Lalivero tint must remain configured")


def check_flags_and_quest_order() -> None:
    flags = read("games/tbs/include/flags.h")
    dark = re.findall(r"^\s*#define\s+(FLAG_DARK_\w+)\s+(0x[0-9a-fA-F]+)\b", flags, re.M)
    require(len(dark) >= 25, "Expected persistent Ashfall flags were removed")
    values = [int(v, 16) for _k, v in dark]
    require(len(set(values)) == len(values), "Two Ashfall flags share the same bit")
    required = {
        "FLAG_DARK_ASH_JENNA_LAMAKAN_MET",
        "FLAG_DARK_FINALE_DONE",
        "FLAG_DARK_ASH_JENNA_ACCEPTED",
        "FLAG_DARK_ASH_JENNA_REFUSED",
        "FLAG_DARK_ASH_JENNA_TOLBI",
        "FLAG_DARK_ASH_JENNA_LALIVERO",
        "FLAG_DARK_MINER_STAYED",
        "FLAG_DARK_HEART_BEATEN",
        "FLAG_DARK_KEGARE_BEATEN",
    }
    require(required.issubset({k for k, _v in dark}), "A story gate or choice flag is missing")

    lamakan = scene("lamakan_desert.c")
    finale = function(lamakan, "LamakanDesert_AshJennaFinale")
    require(
        re.search(r"if\s*\(GameFlag_Get\(FLAG_DARK_MINER_STAYED\).*?"
                  r"Event_SetMessageId\(MsgDarkEchoMiner\);\s*"
                  r"Event_ShowMessageThenWait\(ACTOR_GARET\s*,", finale, re.S) is not None,
        "Altin stay callback must be Garet's voice, conditional on staying",
    )
    assert_speaker(finale, "MsgDarkFinaleJenna2", "ACTOR_LAMAKAN_ASH_JENNA")
    require(
        "GameFlag_Set(FLAG_DARK_ASH_JENNA_ACCEPTED)" in finale
        and "GameFlag_Set(FLAG_DARK_ASH_JENNA_REFUSED)" in finale,
        "Lamakan must preserve both explicit Isaac choice outcomes",
    )
    require(
        "GameFlag_Set(FLAG_DARK_FINALE_DONE)" in finale,
        "Lamakan finale must record its completion",
    )

    tolbi = scene("tolbi.c")
    meeting = function(tolbi, "Tolbi_MeetAshJenna")
    for required_msg in [
        "MsgDarkTolbiJennaAccepted", "MsgDarkTolbiJennaRefused",
        "MsgDarkTolbiJennaAsh", "MsgDarkMiaTolbiConcern",
    ]:
        require(required_msg in meeting, f"Missing Tolbi choice/callback: {required_msg}")
    # New branch lines N240/N241 MUST NOT cause the fixed N76-N83
    # sequence to start from the wrong message ID.
    require(
        meeting.index("Event_SetMessageId(MsgDarkTolbiJennaAsh)")
        > meeting.index("Event_SetMessageId(MsgDarkTolbiJennaRefused)"),
        "Tolbi must explicitly reset the message cursor after both branches",
    )
    require("GameFlag_Set(FLAG_DARK_ASH_JENNA_TOLBI)" in meeting,
            "Tolbi completion must persist")

    lalivero = scene("lalivero.c")
    coda = function(lalivero, "Lalivero_TalkToAshJenna")
    init = function(lalivero, "Lalivero_Initialize")
    require(
        "FLAG_DARK_ASH_JENNA_TOLBI" in init
        and "FLAG_DARK_ASH_JENNA_LALIVERO" in init,
        "Lalivero actor should appear only after Tolbi and before coda completion",
    )
    require("MsgDarkLaliveroIsaacAccepted" in coda
            and "MsgDarkLaliveroIsaacRefused" in coda
            and "Event_SetMessageId(MsgDarkLaliveroAshJenna)" in coda,
            "Lalivero must honor each earlier choice and reconverge cleanly",
    )
    require("GameFlag_Set(FLAG_DARK_ASH_JENNA_LALIVERO)" in coda,
            "Lalivero meeting must be a one-time event")
    require(
        "ACTOR_LALIVERO_ASH_JENNA" not in template(lalivero, "gLaliveroActorTemplates"),
        "Post-Venus Ash Jenna actor must not be inserted into pre-Venus roster",
    )


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
    miner = messages("phase47_finale.tsv")
    require("miner" in miner["N203"].lower()
            and "generous" not in miner["N203"].lower(),
            "Garet's miner callback must not borrow Ash Jenna's contempt")


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
    spoken = re.findall(r"FieldEvent_ShowMessageThenWait\\(\\s*([^,]+)", imil)
    require(len(spoken) == 21,
            f"Mia's farewell changed: expected 21 spoken lines, got {len(spoken)}")

    farewell_rows = {}
    for line in (STORY / "phase17_imil_mercury_b.tsv").read_text(encoding="utf-8").splitlines():
        parts = line.split("\\t", 2)
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
        parts = line.split("\\t", 2)
        if len(parts) == 3 and parts[0].isdigit():
            ivan_rows[parts[0]] = parts[2]
    missing = sorted(f"{n:05d}" for n in range(5008, 5025)
                     if f"{n:05d}" not in ivan_rows)
    require(not missing,
            "Live Goma/Ivan rejoin has unrewritten sequential IDs: " + ", ".join(missing))


def main() -> None:
    check_live_sequential_dialogue()
    check_lalivero_first_postvenus_entry()
    check_named_scene_exit_wiring()
    check_mercury_lighthouse_chronology()
    check_dormant_palette_cache_is_disabled()
    check_visual_identity()
    check_flags_and_quest_order()
    check_optional_battles()
    check_story_text()
    print(f"Ashfall: {checks} static story contracts passed "
          "(visual/branch playthrough still required).")


if __name__ == "__main__":
    main()
