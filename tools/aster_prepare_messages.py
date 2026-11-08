#!/usr/bin/env python3
"""Protect Aster's already numbered messages during the Ashfall TSV rewrite.

This runs only in the disposable ROM-build checkout. In this branch the
original alchemy-null entry is 10722 but Aster's 36 messages follow it at
10723..10758. The existing dark_story_rewrite.py inserts Nxxx messages
wherever it sees the end marker; left alone that reuses Aster's message IDs.

Reposition the *marker*, not the existing Aster text: keep an empty row at
10722, move the null terminator to first unused ID, then run the existing
dark_story_rewrite.py. This preserves the battle's authored TSV dialogue.
"""
from pathlib import Path
import re
import sys

PATH = Path("games/tbs/text/en.po")
ROW = re.compile(r'^msgctxt "([^"]+)"\nmsgid "([0-9]{5})"$', re.MULTILINE)
NULL = re.compile(
    r'(?m)^#, alchemy-null\nmsgctxt "message"\nmsgid "([0-9]{5})"\nmsgstr ""(?=\n|$)'
)

def require(condition, message):
    if not condition:
        raise SystemExit("Aster message-build safeguard: " + message)

def inspect(text, strict):
    rows = [(m.group(1),int(m.group(2))) for m in ROW.finditer(text)]
    require(bool(rows),"No message rows in compiled English catalogue")
    ids=[n for _,n in rows]
    require(len(set(ids))==len(ids),"Duplicate numeric message IDs")
    require(ids==sorted(ids),"Message IDs are out of order")
    require(ids==list(range(ids[0],ids[-1]+1)),
            "Message IDs have a gap")
    markers=list(NULL.finditer(text))
    require(len(markers)==1,"Expected exactly one alchemy-null terminator")
    ast=[(c,n) for c,n in rows if c.startswith("MsgAster")]
    require(len(ast)==36,"Aster must retain all 36 authored messages")
    require([n for _,n in ast]==list(range(10723,10759)),
            "Aster's stable message IDs changed: 10723..10758 expected")
    if strict:
        require(markers[0].group(1)==str(ids[-1]).zfill(5),
                "Terminator is not at end of generated catalogue")
        names={c for c,n in rows}
        require("MsgDarkAshValePunish" in names,
                "Ash Jenna's authored combat dialogue was not generated")
        require("MsgDarkAshValePunished" in names,
                "Second Ash Jenna response was not generated")
        require(ids[-1]>10759,
                "No new Ashfall message rows were generated")
    return rows,markers[0]

def prepare():
    src=PATH.read_text(encoding="utf-8")
    rows,null=inspect(src,False)
    highest=rows[-1][1]
    previous=int(null.group(1))
    if highest==previous:
        print(f"Catalogue terminator already at {highest}; nothing to move")
        return
    require(previous<highest,"Unexpected null marker placed beyond last entry")
    # Replace comment only; the original numbered row remains as a harmless
    # empty message. Do not move, re-index, or rewrite any Aster dialogue.
    old="#, alchemy-null\n"
    require(src.count(old)==1,"Ambiguous null marker comment")
    src=src.replace(old,"",1)
    src=src.rstrip()+(
        f'\n\n#, alchemy-null\nmsgctxt "message"\n'
        f'msgid "{highest+1:05d}"\nmsgstr ""\n'
    )
    inspected,marker=inspect(src,False)
    require(int(marker.group(1))==highest+1,
            "Relocated null marker has wrong numeric ID")
    PATH.write_text(src,encoding="utf-8")
    print(f"Moved English null terminator {previous} -> {highest+1},"
          " preserving 36 Aster messages (10723..10758)")

def verify():
    src=PATH.read_text(encoding="utf-8")
    rows,null=inspect(src,True)
    dark=sum(c.startswith("MsgDark") for c,n in rows)
    print(f"PASS generated text catalogue: {len(rows)} unique numeric IDs,"
          f" {dark} authored dark-story contexts, 36 intact Aster contexts,"
          f" null entry {null.group(1)} last")

if __name__=="__main__":
    if sys.argv[1:]==["--verify"]:
        verify()
    elif not sys.argv[1:]:
        prepare()
    else:
        raise SystemExit("Usage: python3 tools/aster_prepare_messages.py [--verify]")
