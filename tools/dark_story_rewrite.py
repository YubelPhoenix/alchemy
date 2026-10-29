#!/usr/bin/env python3
"""Apply the first scene-specific darker dialogue pass to the English PO file.

This runs only in the experimental build workspace. It does not rewrite the
tracked source file in GitHub; it produces the dialogue used for that build.
"""
from pathlib import Path
import re

path = Path("games/tbs/text/en.po")
text = path.read_text(encoding="utf-8")

REPLACEMENTS = {
    "03675": r"{actor_name:1}, Dora, hurry!\nThe Boulder is close to\nbreaking loose!{end_wait}",
    "03676": r"Kyle... Can they hold\nthe Boulder back?{end_wait}",
    "03685": r"You're a big boy now,\n{actor_name:1}. Go on ahead.\nPlease be careful!{end_now}",
    "03686": r"You know the way{em_dash}go\nsouth to the plaza.\nPlease, hurry!{end_wait}",
    "03687": r"Isaac? Sorry! I didn't\nsee you there!{end_wait}",
    "03707": r"We shouldn't go north...\nMt. Aleph is that way.\nWe need the plaza!{end_wait}",
    "03709": r"That rock blocks the way!\nWe can't get around it!{end_wait}",
    "03723": r"This is it... I can't hold on\nmuch longer! Please...\nget the others to safety!{end_wait}",
    "03724": r"Felix! No... please!\nSomeone, help my brother!\nI can't lose him too!{end_wait}",
    "03725": r"Hold on, {actor_name:5}!\nWe're coming for you!\nDon't let go!{end_wait}",
    "03739": r"I'll check the northern\npath. You get to the plaza\nand bring back help!{end_wait}",
    "03749": r"The two of you can't\nsave {actor_name:5} with so little\nPsynergy. Find help now!{end_wait}",
    "03755": r"Me? Use Psynergy?\nI'm an old woman! Don't\nask the impossible!{end_wait}",
    "03756": r"{text_effect:4}Ohhh... I'm exhausted.{page_break}\nI spent nearly everything\ndeflecting those rocks...{end_wait}",
    "03766": r"Go! Aid the elders! The\nBoulder is too heavy; they\ncan't hold it much longer!{end_wait}",
    "03781": r"There's no time! Hurry!\nEvery moment we waste,\nmore lives are at risk!{end_wait}",
    "03782": r"Mom! Dad! Please answer!\nFelix is slipping away!\nI can't reach him!{end_wait}",
    "03798": r"Only the two of us\nmade it out alive...\nThe others are gone...{end_wait}",
    "03928": r"Those three travelers\nmake me uneasy. They barely\nspeak to anyone.{page_break}\nThey watch the village\nas if searching for someone.\nI don't like it...{end_wait}",
    "03929": r"The masked man... I saw\nhim among that group. He\nnever showed his face.{page_break}\nMaybe he's hiding scars,\nbut something about them\nstill troubles me.{end_wait}",
    "03930": r"Two of those travelers\nhave gone out in this storm.\nI don't like the timing...{end_wait}",
    "03975": r"Kraden... Could he be\nuseful to us?{end_wait}",
    "03976": r"His knowledge is\nconsiderable...{page_break}\nIf he can be persuaded,\nhe may yet serve our\npurpose.{end_wait}",
    "03977": r"He is far more stubborn\nthan we anticipated.{end_wait}",
    "03978": r"And far more cunning.\nWe must not underestimate\nhim.{end_wait}",
    "03979": r"If he refuses to cooperate,\nwe may have to find\nanother way...{end_wait}",
    "03983": r"Oh ho! So you've been\nlistening...{pause_20_skippable}{page_break}\nI can't let you leave\nknowing what you've heard.{end_wait}",
    "03986": r"Sneaking? You dare\naccuse me of that? Who\ndo you think you are?{end_wait}",
    "03989": r"And this appointment is\nimportant enough to make\nus leave?{end_now}",
    "03990": r"Pfeh! You expect us to\nput your errand ahead\nof our own?{end_wait}",
    "03994": r"Are you certain,\nSaturos?{end_wait}",
    "03995": r"Menardi, there is no\nreason to keep these\nchildren here any longer.{end_wait}",
}

def main() -> None:
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
        # Preserve the project's physical-line PO convention. The game text
        # compiler treats each quoted continuation as a display line; keeping
        # one display line per PO string also makes the generated file auditable.
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
    print(f"Rewrote {len(found)} scene-specific dialogue entries.")

if __name__ == "__main__":
    main()
