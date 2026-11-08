#!/usr/bin/env python3
"""Source-authored Aster dialogue polish, applied ONLY in disposable ROM builds.

The repository's games/tbs/text/en.po is deliberately left untouched to avoid
accidentally triggering the paid-capable dialogue GitHub Actions workflow.
--check: verify the 36 numbered Aster contexts, lengths and source TSV.
--apply: update Aster lines in the local disposable en.po + source TSV, so
         the actual locally compiled ROM contains these words. Idempotent.
This never adds message IDs, changes actors, or mutates a main project save.
"""
import argparse
import ast
import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PO=ROOT/"games/tbs/text/en.po"
TSV=ROOT/"tools/aster_dialogue.tsv"
# Two pages are shown as separate nested lists, each with 1–3 display lines.
UPDATES={
 "MsgAsterInnkeeperWelcome":[
     ["We don't get many guests.", "Not since the fire."],
     ["What fire? I don't know.", "I didn't say that."]],
 "MsgAsterArrivalHome":[["I lived near Vale once.", "I still hear the storm."]],
 "MsgAsterArrivalMemorial":[["FOR THOSE WHO RETURNED", "The names were scraped off."]],
 "MsgAsterArrivalElder":[["Aster's always been here.", "Ask anyone."]],
 "MsgAsterFractureElder":[["We laid the first stones.", "I wasn't alive back then."]],
 "MsgAsterFractureGreeter":[["You came back.", "No... you never left."]],
 "MsgAsterRevelationElder":[["Some remember the storm.", "Others remember the fire."]],
 "MsgAsterFractureBegin":[
     ["The wind suddenly stops.", "Someone calls your name.",
      "No one turns around."]],
 "MsgAsterOtherIsaacEarly":[["I know that face.", "I wish I didn't."]],
 "MsgAsterRevelationAshEcho":[
     ["I walked this road before.", "Those houses were ours."]],
}
# These are verbatim pre-polish source lines; unexpected changes abort the patch.
ORIGINAL={
 "MsgAsterInnkeeperWelcome":[
     ["Rooms are open tonight.", "Are you from Vale?"],
     ["No. Vale burned years ago.", "Forgive me. I feel ill."]],
 "MsgAsterArrivalHome":[["I remember Vale.", "Did you hear the rain?"]],
 "MsgAsterArrivalMemorial":[["FOR THOSE WHO RETURNED", "Names have been erased."]],
 "MsgAsterArrivalElder":[["Aster has always been here.", "Ask anyone."]],
 "MsgAsterFractureElder":[["We built this town", "before any of us were born."]],
 "MsgAsterFractureGreeter":[["You came back.", "No. You never left."]],
 "MsgAsterRevelationElder":[["The town isn't dying.", "It's remembering both."]],
 "MsgAsterFractureBegin":[
     ["The air folds in on itself.", "Someone calls your name.",
      "No one opens their mouth."]],
 "MsgAsterOtherIsaacEarly":[["Don't look at me yet.", "It isn't time."]],
 "MsgAsterRevelationAshEcho":[["I know this road.", "I know who lived here."]],
}
def require(ok,why):
    if not ok:raise AssertionError(why)
def decode(raw):
    quoted=[];started=False
    for line in raw.splitlines():
        if line=='msgstr ""':started=True;continue
        if started and line.startswith('"'):
            quoted.append(ast.literal_eval(line))
    require(quoted,"Missing compiled msgstr lines")
    data="".join(quoted)
    require(data.endswith("{end_wait}"),"Missing Aster msg terminator")
    return [page.split("\n") for page in data[:-len("{end_wait}")].split("{page_break}")]
def encode(pages):
    items=[]
    for pidx,page in enumerate(pages):
        for idx,line in enumerate(page):
            tail=("\n" if idx<len(page)-1 else
                  "{page_break}" if pidx<len(pages)-1 else "{end_wait}")
            items.append(json.dumps(line+tail,ensure_ascii=False))
    return 'msgstr ""\n'+"\n".join(items)
def title(stage,key):
    return "MsgAster"+"".join(part.capitalize()
                for seg in (stage,key) for part in seg.split("_"))
def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    require(UPDATES.keys()==ORIGINAL.keys(),"Original/new dialogue keys mismatch")
    for name,pages in UPDATES.items():
        require(1<=len(pages)<=4,f"{name}: invalid page count")
        for page in pages:
            require(1<=len(page)<=3,f"{name}: more than three display lines")
            for line in page:
                require(0<len(line)<=27,f"{name}: display line over 27 characters: {line}")
    po=PO.read_text(encoding="utf-8")
    blocks=re.split(r"(\n\s*\n)",po)
    occurrences={}
    changes=0
    for i,block in enumerate(blocks):
        match=re.search(r'^msgctxt "(MsgAster[^"]+)"$',block,re.M)
        if not match:continue
        name=match.group(1)
        occurrences[name]=occurrences.get(name,0)+1
        if name not in UPDATES:continue
        parsed=decode(block)
        require(parsed in (ORIGINAL[name],UPDATES[name]),
                f"{name}: source changed since review; refusing to overwrite")
        # Apply only to the local disposable clone; don't touch repository PO.
        if args.apply and parsed!=UPDATES[name]:
            before=re.search(r'(?m)^msgstr ""\n(?:^"[^"]*"\n?)+',block)
            require(before is not None,f"{name}: PO block format drift")
            blocks[i]=block[:before.start()]+encode(UPDATES[name])+block[before.end():]
            changes+=1
    require(len(occurrences)==36 and all(n==1 for n in occurrences.values()),
            f"Expected exactly 36 unique Aster contexts, got {len(occurrences)}")
    require(set(UPDATES).issubset(occurrences),"Missing protected Aster dialogue")
    with TSV.open(newline="",encoding="utf-8") as handle:
        reader=csv.DictReader(handle,delimiter="\t")
        fieldnames=reader.fieldnames
        rows=list(reader)
    require(fieldnames==["stage","key","speaker","line1","line2","line3"],
            "Aster TSV header drift")
    edits=0
    for row in rows:
        name=title(row["stage"],row["key"])
        if name not in UPDATES:continue
        require(len(UPDATES[name])==1,f"{name}: multi-page TSV unsupported")
        linekeys=["line1","line2","line3"]
        old=[row[k] for k in linekeys if row[k]]
        require(old in (ORIGINAL[name][0],UPDATES[name][0]),
                f"{name}: source TSV changed from approved baseline")
        if args.apply and old!=UPDATES[name][0]:
            for k,value in zip(linekeys,UPDATES[name][0]+[""]*3):
                row[k]=value
            edits+=1
    if args.apply:
        PO.write_text("".join(blocks),encoding="utf-8")
        with TSV.open("w",encoding="utf-8",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=fieldnames,delimiter="\t",
                                  lineterminator="\n")
            writer.writeheader();writer.writerows(rows)
        print(f"APPLIED {changes} local English PO dialogue replacements, {edits} TSV rows")
        print("No message IDs, scene events or permanent GitHub PO were edited.")
    else:
        print(f"PASS 36 Aster IDs, {len(UPDATES)} approved dialogue refinements")
        print("PASS all changed display lines at most 27 characters")
        print("READ-ONLY: local build will apply; original English PO stays unchanged")

if __name__=="__main__":main()
