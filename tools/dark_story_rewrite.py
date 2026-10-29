#!/usr/bin/env python3
"""Apply and validate the experimental dark Vale dialogue pass.

The script edits only the English text catalogue in the build workspace. It
preserves the PO compiler's display-line convention and validates the dialogue
before the ROM build is allowed to proceed.
"""
from pathlib import Path
import re

path = Path("games/tbs/text/en.po")
text = path.read_text(encoding="utf-8")

# Each literal \n is one displayed line. Keep lines within the original game's
# approximate 27-character text width and use {page_break} for a new page.
REPLACEMENTS = {
    "03675": r"{actor_name:1}, Dora!\nThe Boulder is slipping!\nMove! Now!{end_wait}",
    "03676": r"Dora, can they hold it?\nNot for long. Look at them.\nThey're almost spent.{end_wait}",
    "03685": r"You're old enough to run,\nIsaac. I hate that you must.\nGo. Please.{end_now}",
    "03686": r"Go to the plaza.\nDon't stop for anyone.\nIsaac... hurry.{end_wait}",
    "03687": r"Isaac? I didn't see you.\nAre you hurt? Tell me.{end_wait}",
    "03707": r"Don't go north.\nThat way leads to Mt. Aleph.\nGet back to the plaza.{end_wait}",
    "03709": r"The rock sealed the path.\nThere's no getting through.{end_wait}",
    "03723": r"I can't hold it!\nGet away from the river!\nGo!{end_wait}",
    "03724": r"Felix! No!\nSomebody, help him!\nPlease!{end_wait}",
    "03725": r"{actor_name:5}! Hold on!\nCan you hear me?\nPlease answer!{end_wait}",
    "03739": r"I'll search up north.\nGet help from the plaza.\nDon't come back alone.{end_wait}",
    "03749": r"We can't free him alone.\nOur Psynergy is gone.\nFind someone who can help.{end_wait}",
    "03755": r"My Psynergy is spent.\nI can't move another stone.{page_break}\nI'm sorry, child.\nI can't help you now.{end_wait}",
    "03756": r"{text_effect:4}My hands... they're shaking.\nI can't do it again.{reset_text_style}{page_break}\nThose stones took everything.\nI'm sorry.{end_wait}",
    "03766": r"Help the elders!\nThey're holding back the\nBoulder. They won't last!{end_wait}",
    "03781": r"Move! The elders are failing!\nWe have to reach them!{end_wait}",
    "03782": r"Mom? Dad? It's me.\nPlease, say something.{pause_20_skippable}{page_break}\nWe're home... we're home.{end_wait}",
    "03791": r"Mom...? Dad...?\n{actor_name:5}... where are you?{end_wait}",
    "03798": r"Only two survived.\nHow did we?{end_wait}",
    "03928": r"Those three travelers...\nSomething was wrong with them.\nThey watched us all night.{page_break}\nI thought they were rude.\nNow I'm not so sure.{end_wait}",
    "03929": r"The masked man hid his face.\nI thought he had a scar.{page_break}\nWhat else was he hiding?{end_wait}",
    "03930": r"They left while we were\nfighting for our lives.\nNot even a glance back.{page_break}\nWhat could be worth that?{end_wait}",
    "03975": r"Kraden...{pause_20_skippable}\nHe may know something.\nBut will he tell us?{end_wait}",
    "03976": r"Kraden knows too much.\nAnd he asks too many questions.\nWe must be careful.{end_wait}",
    "03977": r"Push him and he'll dig in.\nWe need another way.{end_wait}",
    "03978": r"He notices everything.\nDon't mistake his manners\nfor foolishness.{end_wait}",
    "03979": r"If he won't help us,\nwe'll manage without him.\nQuietly.{end_wait}",
    "03983": r"So, you heard us.{pause_20_skippable}\nThis needn't end badly.\nBut you can't leave now.{page_break}\nI'm sorry. You were warned.\nDon't make me ask again.{end_wait}",
    "03986": r"Sneaking around?\nYou have no idea what\nyou've stumbled into.{end_wait}",
    "03989": r"And we should drop everything\nfor your appointment?{end_now}",
    "03990": r"Pfeh. Your errand can wait.\nOurs cannot.{end_wait}",
    "03994": r"Saturos, are you sure?\nThose children may remember.{end_wait}",
    "03995": r"Menardi, let them go.\nKeeping them here gains us\nnothing.{page_break}\nFear will keep them quiet.\nIt always does.{end_wait}",
}


# Guard against rewriting a numerically adjacent but semantically different line.
# In particular, 03782 is the return call to Mom and Dad; Jenna's post-boulder
# dialogue is 03791.
EXPECTED_CONTEXTS = {
    "03675": "MsgValeDoraHurryBoulder",
    "03676": "MsgValeKyleAbleStop",
    "03685": "MsgValeBigBoyWhy",
    "03686": "MsgValeKnowWayGo",
    "03687": "MsgValeHuh",
    "03707": "MsgValeNorthLeadsToMtAleph",
    "03709": "MsgValeCantGetAroundThisRock",
    "03723": "MsgValeSaveYourselves",
    "03724": "MsgValeNoBrother",
    "03725": "message",
    "03739": "MsgValeGoLookNorth",
    "03749": "MsgValeTwoDontEnough",
    "03755": "MsgValeOldWomanCannotUsePsynergy",
    "03756": "MsgValeExhaustedFromFallingRocks",
    "03766": "MsgValeGoAidElders",
    "03781": "MsgValeRaceAgainstTime",
    "03782": "MsgValeMomDadBack",
    "03791": "MsgValeMomDadFelixPleaseDontLeave",
    "03798": "MsgValeOnlyTwoSurvived",
    "03928": "MsgValeTheThreeTravelersSeemOdd",
    "03929": "MsgValeOneOfTheMenFromThat",
    "03930": "MsgValeTwoOfThoseThreeGuestsStaying",
    "03975": "message",
    "03976": "message",
    "03977": "message",
    "03978": "message",
    "03979": "message",
    "03983": "message",
    "03986": "message",
    "03989": "message",
    "03990": "message",
    "03994": "message",
    "03995": "message",
}

CONTROL_RE = re.compile(r"\{[^{}]+\}")
ACTOR_RE = re.compile(r"\{actor_name:\d+\}")

def parse_entries(source: str) -> dict[str, str]:
    """Return each numeric entry's complete decoded msgstr text."""
    entries: dict[str, str] = {}
    for entry in re.split(r"\n\s*\n", source):
        match = re.search(r'^msgid "([0-9]{5})"$', entry, re.MULTILINE)
        if not match:
            continue
        msgid = match.group(1)
        if msgid in entries:
            raise SystemExit(f"Duplicate dialogue ID {msgid} in PO catalogue.")
        lines = entry.splitlines()
        start = next((i for i, line in enumerate(lines)
                      if line.startswith("msgstr ")), None)
        if start is None:
            raise SystemExit(f"Missing msgstr for dialogue ID {msgid}.")
        encoded = []
        first = lines[start][len("msgstr "):]
        if first:
            encoded.append(first)
        for line in lines[start + 1:]:
            if not line.startswith('"'):
                break
            encoded.append(line)
        # Parse the PO string fragments without interpreting game control codes.
        raw = "".join(part[1:-1] for part in encoded if part.startswith('"'))
        raw = raw.replace(r"\n", "\n").replace(r"\\", "\\").replace(r'\"', '"')
        entries[msgid] = raw
    return entries

def visible_line_length(line: str) -> int:
    # Dynamic character names can be longer than their token; reserve eight
    # characters for them. Other control codes do not occupy dialogue width.
    line = ACTOR_RE.sub("XXXXXXXX", line)
    line = CONTROL_RE.sub("", line)
    return len(line)


def validate_contexts(source: str) -> None:
    for msgid, expected_context in EXPECTED_CONTEXTS.items():
        pattern = re.compile(
            rf'^msgctxt "{re.escape(expected_context)}"\nmsgid "{re.escape(msgid)}"$',
            re.MULTILINE,
        )
        if not pattern.search(source):
            raise SystemExit(
                f"Dialogue {msgid} has an unexpected context; "
                f"expected {expected_context}."
            )


def validate_replacements(entries: dict[str, str]) -> None:
    # Jenna's post-Boulder line is a crash-regression target. Keep it on one
    # page until the in-game interaction has been verified; the general width
    # checks below still enforce the game's three-line, 27-character limits.
    jenna_aftermath = REPLACEMENTS["03791"]
    if "{page_break}" in jenna_aftermath:
        raise SystemExit("Dialogue 03791 must stay on one page during crash testing.")
    if "{end_wait}" not in jenna_aftermath:
        raise SystemExit("Dialogue 03791 is missing its required end_wait control.")
    if "{actor_name:5}" not in jenna_aftermath:
        raise SystemExit("Dialogue 03791 must preserve Jenna\'s dynamic actor-name reference.")

    missing = sorted(set(REPLACEMENTS) - set(entries))
    if missing:
        raise SystemExit("Missing expected dialogue IDs: " + ", ".join(missing))

    for msgid, replacement in REPLACEMENTS.items():
        original = entries[msgid]
        original_controls = [
            token for token in CONTROL_RE.findall(original)
            if token.startswith(("{end_", "{pause_", "{text_effect:", "{reset_text_style}"))
        ]
        new_controls = [
            token for token in CONTROL_RE.findall(replacement)
            if token.startswith(("{end_", "{pause_", "{text_effect:", "{reset_text_style}"))
        ]
        for token in original_controls:
            if token not in new_controls:
                raise SystemExit(
                    f"Dialogue {msgid} dropped required control code {token}."
                )

        pages = re.split(r"\{page_break\}", replacement)
        for page_no, page in enumerate(pages, start=1):
            display_lines = page.split(r"\n")
            while display_lines and not display_lines[0]:
                display_lines.pop(0)
            while display_lines and not display_lines[-1]:
                display_lines.pop()
            if not display_lines:
                continue
            if len(display_lines) > 3:
                raise SystemExit(
                    f"Dialogue {msgid}, page {page_no}: "
                    f"{len(display_lines)} display lines (maximum 3)."
                )
            for line_no, line in enumerate(display_lines, start=1):
                width = visible_line_length(line)
                if width > 27:
                    raise SystemExit(
                        f"Dialogue {msgid}, page {page_no}, line {line_no}: "
                        f"{width} visible characters (maximum 27): {line}"
                    )


def main() -> None:
    validate_contexts(text)
    entries_by_id = parse_entries(text)
    validate_replacements(entries_by_id)

    entries = re.split(r"(\n\s*\n)", text)
    found = set()
    for index, entry in enumerate(entries):
        match = re.search(r'^msgid "([0-9]{5})"$', entry, re.MULTILINE)
        if not match:
            continue
        msgid = match.group(1)
        if msgid not in REPLACEMENTS:
            continue
        if msgid in found:
            raise SystemExit(f"Duplicate dialogue ID {msgid}.")
        found.add(msgid)
        lines = entry.splitlines()
        msgstr_index = next(
            (i for i, line in enumerate(lines) if line.startswith("msgstr ")),
            None,
        )
        if msgstr_index is None:
            raise SystemExit(f"Missing msgstr for {msgid}.")

        display_lines = REPLACEMENTS[msgid].split(r"\n")
        encoded_lines = ['msgstr ""']
        for line_index, display_line in enumerate(display_lines):
            suffix = r"\n" if line_index < len(display_lines) - 1 else ""
            encoded_lines.append('"' + display_line + suffix + '"')
        lines = lines[:msgstr_index] + encoded_lines
        entries[index] = "\n".join(lines)

    missing = sorted(set(REPLACEMENTS) - found)
    if missing:
        raise SystemExit("Missing expected dialogue IDs: " + ", ".join(missing))
    path.write_text("".join(entries), encoding="utf-8")
    print(f"Rewrote and validated {len(found)} scene-specific dialogue entries.")


if __name__ == "__main__":
    main()
