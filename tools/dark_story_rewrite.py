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
    "03675": r"{actor_name:1}, Dora!\nThe Boulder is breaking!\nGet clear of the mountain!{end_wait}",
    "03676": r"Kyle... tell me they're\nholding. Tell me we haven't\nsent them to die up there.{end_wait}",
    "03685": r"You're old enough to make\nthis run, Isaac. I hate\nsending you alone.{page_break}\nBut you must reach\nthe plaza alive.{end_now}",
    "03686": r"South. Straight to the\nplaza. If anyone sends you\nback toward Mt. Aleph,{page_break}\nkeep moving. Don't stop.\nUnderstand?{end_wait}",
    "03687": r"Isaac? What are you doing\nback here? The plaza is\nsouth!{end_wait}",
    "03707": r"Don't go north. That path\nleads back to Mt. Aleph.\nThe people who went that{page_break}\nway haven't returned.\nDon't follow them alone.{end_wait}",
    "03709": r"The rock buried the path.\nI heard someone beyond it,\nbut the stones are still{page_break}\nmoving. We can't get\nthrough yet.{end_wait}",
    "03723": r"I can't hold on... Please,\ndon't let them come back\nfor me.{page_break}\nGet the others away\nfrom the mountain.{end_wait}",
    "03724": r"My brother is still under\nthere! I heard him call\nmy name.{page_break}\nYou can't tell me he's\ngone when I haven't even\nseen him!{end_wait}",
    "03725": r"{actor_name:5}, keep\nbreathing! Can you hear me?\nStay with us.{page_break}\nWe're not leaving you\nin that rubble!{end_wait}",
    "03739": r"I'll search the north path\nand the houses. Run to the\nplaza and bring help.{page_break}\nIf I don't return, don't\nfollow me alone.{end_wait}",
    "03749": r"We have almost nothing\nleft. We cannot free\n{actor_name:5} alone.{page_break}\nFind help before the\nstones settle.{end_wait}",
    "03755": r"You want me to use\nPsynergy? I can barely\nstand, child.{page_break}\nI'm sorry. I've spent\nwhat strength I had\nkeeping others alive.{end_wait}",
    "03756": r"{text_effect:4}My hands\nwon't stop shaking... I\nturned the falling stones{page_break}\naside, but I have nothing\nleft. I cannot do it\nagain.{end_wait}",
    "03766": r"Go to the elders! They're\nholding the Boulder back\nwith their last strength.{page_break}\nIf they falter, Vale will\nbe buried alive!{end_wait}",
    "03781": r"Move! Every second we\nstand here, someone else\nmay be trapped beneath{page_break}\nthe mountain. We cannot\nafford another delay!{end_wait}",
    "03782": r"Mom! Dad! It's me!\nPlease answer!{pause_20_skippable}{page_break}\nWe came back!{end_wait}",
    "03791": r"Mom... Dad...\n{actor_name:5}... please,\ndon't leave me alone.{page_break}\nI don't know how to live\nin a world where everyone\nI love can vanish{page_break}\nin a single night.{end_wait}",
    "03798": r"We searched until the\ncries stopped. In the end,\nonly two of us came back{page_break}\ndown... and I don't know\nwhy we did.{end_wait}",
    "03928": r"Those three guests never\nacted like travelers.\nThey watched the roads{page_break}\nand counted who came and\nwent. They fell silent\nwhen anyone drew near.{page_break}\nI called it foolishness.\nNow I wonder if they were\nwaiting for the mountain.{end_wait}",
    "03929": r"The masked man never\nshowed his face. That\nshould have warned me.{page_break}\nHe watched the disaster\nas if he'd accepted it\nlong before it came.{end_wait}",
    "03930": r"Two of them left while\nthe mountain still shook.\nNo farewell. No reason.{page_break}\nWhat mattered more to\nthem than all those lives?{end_wait}",
    "03975": r"Kraden...{pause_20_skippable}\nHe knows more than he\nadmits.{page_break}\nCould he be useful to us?{end_wait}",
    "03976": r"He knows a great deal...{pause_20_skippable}\nBut knowledge doesn't\nmake him cooperative.{page_break}\nWe must learn what he\nwants before we act.{end_wait}",
    "03977": r"He's resisted every\nattempt to guide him.\nI expected curiosity,{page_break}\nnot this much defiance.{end_wait}",
    "03978": r"And he notices too much.\nDon't mistake his age or\nhis manners for weakness.{end_wait}",
    "03979": r"If he refuses to help,\nwe may have to show him\nwhat refusal will cost.{end_wait}",
    "03983": r"So you've been listening...{pause_20_skippable}{page_break}\nI'd rather leave this\nvillage without bloodshed.{page_break}\nBut I can't let you carry\nwhat you've heard to\nanyone else.{end_wait}",
    "03986": r"Sneaking? You know\nnothing of our purpose.\nThink carefully before{page_break}\nyou accuse me again.{end_wait}",
    "03989": r"And your appointment\nmatters enough to make us\nabandon our own work?{end_now}",
    "03990": r"Pfeh. You would have us\nplace your errand above\nours?{page_break}\nGive me one reason\nto agree.{end_wait}",
    "03994": r"Saturos... are you certain?\nThese children may remember\nmore than we expect.{end_wait}",
    "03995": r"Menardi, we needn't keep\nthem here. Let them go.{page_break}\nFear makes people careless.\nCareless people reveal\nwhat they know.{end_wait}",
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
