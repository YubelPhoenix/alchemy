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
    "03675": r"{actor_name:1}, Dora!\nThe Boulder could fall!\nGet away from the mountain!{end_wait}",
    "03676": r"Kyle... Can they hold\nthe Boulder much longer?{end_wait}",
    "03685": r"You're a big boy now,\n{actor_name:1}. Go on ahead.\nPlease, be careful!{end_now}",
    "03686": r"You know the way{em_dash}go\nsouth to the plaza.\nPlease, hurry!{end_wait}",
    "03687": r"Huh? {actor_name:1}?\nSorry, I didn't see you.\nIs everyone safe?{end_wait}",
    "03707": r"We shouldn't go north...\nThat leads to Mt. Aleph.\nWe need the plaza!{end_wait}",
    "03709": r"We can't get around\nthis rock! It's too big!{end_wait}",
    "03723": r"I can't hold on much\nlonger. Get the others\nto safety... please!{end_wait}",
    "03724": r"Felix! No, please!\nSomeone, help my brother!\nI can't lose him too!{end_wait}",
    "03725": r"Hold on, {actor_name:5}!\nPlease, don't let go!\nWe're coming to help!{end_wait}",
    "03739": r"I'll search the north path.\nYou run to the plaza\nand bring back help!{end_wait}",
    "03749": r"You can't save {actor_name:5}\nwith so little Psynergy.\nGo and find help!{end_wait}",
    "03755": r"An old woman like me?\nYou expect me to use\nPsynergy now?{page_break}\nDon't ask the impossible!{end_wait}",
    "03756": r"{text_effect:4}Ohhh...{reset_text_style} I'm exhausted.{page_break}\nI used all my Psynergy\ndeflecting those rocks...{end_wait}",
    "03766": r"Go! Help the elders!\nThe Boulder is too heavy;\nthey can't hold it long!{end_wait}",
    "03781": r"There's no time! Hurry!\nEvery moment we waste,\nsomeone else may die!{end_wait}",
    "03782": r"Mom! Dad!{pause_20_skippable}\nWe're back! Please answer!{end_wait}",
    "03798": r"Only the two of us\nmade it out alive...{end_wait}",
    "03928": r"Those three travelers\nmake me uneasy. They\nbarely speak to us.{page_break}\nThey watch the village\nas if searching for someone.\nI wish they'd leave...{end_wait}",
    "03929": r"One man in that group\nwears a mask. He never\nshows his face.{page_break}\nMaybe he hides some scars,\nbut something about him\nstill troubles me...{end_wait}",
    "03930": r"Two of those travelers\nwent out into the storm.\nWhy leave now?{end_wait}",
    "03975": r"Kraden...{pause_20_skippable}\nCould he be of use?{end_wait}",
    "03976": r"He knows a great deal...{pause_20_skippable}\nIf he can be persuaded,\nhe may serve our purpose.{end_wait}",
    "03977": r"He is more stubborn\nthan we anticipated...{end_wait}",
    "03978": r"And more cunning, too.\nWe must not underestimate\nhim.{end_wait}",
    "03979": r"If he will not cooperate,\nwe'll need another way...{end_wait}",
    "03983": r"Oh ho!{pause_20_skippable}\nWell...{pause_20_skippable}{page_break}\nI can't let you leave\nknowing what you've heard.{end_wait}",
    "03986": r"Sneaking...{pause_20_skippable}\nWho are you to accuse me?{end_wait}",
    "03989": r"And this appointment\nmatters enough to make\nus leave?{end_now}",
    "03990": r"Pfeh! Your errand\nis more important than\nour own, is it?{end_wait}",
    "03994": r"Are you certain,\nSaturos?{end_wait}",
    "03995": r"Menardi, we needn't\nkeep these children\nany longer.{end_wait}",
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

def validate_replacements(entries: dict[str, str]) -> None:
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

        # Validate each page independently. The GBA dialogue UI is narrow;
        # reject overlong lines or more than three display lines per page.
        pages = re.split(r"\{page_break\}", replacement)
        for page_no, page in enumerate(pages, start=1):
            display_lines = page.split(r"\n")
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
    entries_by_id = parse_entries(text)
    validate_replacements(entries_by_id)

    # Keep all original metadata/context and replace only msgstr content.
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

        # Preserve the project's PO convention: each quoted continuation is
        # one displayed line; control codes stay in the text, not in Python's
        # source-line layout.
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
