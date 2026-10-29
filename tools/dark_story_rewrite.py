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
    "03675": r"{actor_name:1}, Dora!\nThe Boulder is slipping!\nGet clear, now!{end_wait}",
    "03676": r"Kyle... can they hold it?\nThe Boulder is moving.\nThey're close to breaking.{end_wait}",
    "03685": r"You're old enough to run,\nIsaac. I wish you weren't.\nBut you must go.{end_now}",
    "03686": r"South, to the plaza.\nDon't stop along the way.\nPlease, Isaac. Hurry.{end_wait}",
    "03687": r"Isaac? Sorry, I didn't\nsee you there.\nAre you hurt?{end_wait}",
    "03707": r"Don't go north. That path\nleads to Mt. Aleph.\nGo back to the plaza.{end_wait}",
    "03709": r"The rock has sealed the\npath. There's no way\nthrough here.{end_wait}",
    "03723": r"I can't hold on much\nlonger. Save yourselves.\nGet away from the river.{end_wait}",
    "03724": r"Felix! No, please!\nSomeone, help my brother!\nDon't let him go!{end_wait}",
    "03725": r"{actor_name:5}, hold on!\nCan you hear me? Please!\nWe're coming!{end_wait}",
    "03739": r"I'll search the north path.\nRun to the plaza for help.\nDon't come back alone.{end_wait}",
    "03749": r"Two of us can't free him.\nOur Psynergy is spent.\nFind help. Quickly.{end_wait}",
    "03755": r"Psynergy? I can barely\nstand. I've used all I had\nkeeping those rocks away.{page_break}\nI'm sorry, child. I have\nnothing left to give.{end_wait}",
    "03756": r"{text_effect:4}My hands won't stop\nshaking... I pushed the\nstones aside,{reset_text_style}{page_break}\nnow I can barely stand.\nI can't do it again.{end_wait}",
    "03766": r"Go to the elders! They're\nholding the Boulder back.\nThey can't hold it forever.{end_wait}",
    "03781": r"Move! The elders are\nrunning out of strength.\nWe have no time to lose.{end_wait}",
    "03782": r"Mom? Dad? It's me!\nPlease, answer me!{pause_20_skippable}{page_break}\nWe're back. Please...{end_wait}",
    "03791": r"Mom...? Dad...?\n{actor_name:5}... please...\nDon't leave me here.{end_wait}",
    "03798": r"Only two of us survived.\nI still don't know how.{end_wait}",
    "03928": r"Those three travelers\ntroubled me from the start.\nThey watched everyone,{page_break}\nbut spoke to no one.\nI thought them rude.\nNow I wonder why.{end_wait}",
    "03929": r"The masked man never\nshowed his face. I thought\nhe was hiding a scar.{page_break}\nNow I wonder what he\nwas hiding from us.{end_wait}",
    "03930": r"Two of them left during\nthe storm. They didn't\nlook back once.{page_break}\nWhat could matter more\nthan the people here?{end_wait}",
    "03975": r"Kraden...{pause_20_skippable}\nHe knows more than he\nlets on. Could he help us?{end_wait}",
    "03976": r"He knows a great deal.\nBut he won't be led easily.\nWe need another approach.{end_wait}",
    "03977": r"He's more stubborn than\nwe expected. Push him,\nand he'll only resist.{end_wait}",
    "03978": r"And he notices too much.\nWe shouldn't mistake his\ncuriosity for naivety.{end_wait}",
    "03979": r"If he won't cooperate,\nwe'll find another way.\nQuietly, if possible.{end_wait}",
    "03983": r"So, you've been listening.{pause_20_skippable}\nI'd rather not hurt you.\nBut you can't leave knowing{page_break}\nwhat you heard. I'm sorry.\nI won't ask twice.{end_wait}",
    "03986": r"Sneaking? Careful.\nYou don't know what we're\ndoing, or why.{end_wait}",
    "03989": r"And this appointment is\nimportant enough to make\nus abandon our own work?{end_now}",
    "03990": r"Pfeh. You expect us to\nput your errand before\nour own?{end_wait}",
    "03994": r"Saturos... are you sure?\nThe children may remember\nmore than they should.{end_wait}",
    "03995": r"Menardi, there's no need\nto keep them here.\nLet them go.{page_break}\nFear will do the rest.\nPeople talk when they're\nafraid.{end_wait}",
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
