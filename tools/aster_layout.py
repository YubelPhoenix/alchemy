#!/usr/bin/env python3
"""Reproducible Aster 32x32 Alchemy map source; --check validates tracked grid."""
from collections import deque
from pathlib import Path
import argparse
LAYOUT = (
    "################################",
    "#..............................#",
    "#..XXXXXXX....====.EEEEEEEEEE..#",
    "#..XXXXXXX....====.EEEEEEEEEE..#",
    "#..XXXXXXX....====.EEEEEEEEEE..#",
    "#..XXXXXXX....====.EEEEEEEEEE..#",
    "#.............====.EEEEEEEEEE..#",
    "#.HHHHHHHH....====.EEEEEEEEEE..#",
    "#.HHHHHHHH....====.EEEEEEEEEE..#",
    "#.HHHHHHHH....====.....IIIIIII.#",
    "#.HHHHHHHH....==M=.....IIIIIII.#",
    "#.HHHHHHHH========n===.IIIIIII.#",
    "#.HHHHHHHH============.IIIIIII.#",
    "#.HHHHHHHH============.IIIIIII.#",
    "#.....=...============.IIIIIII.#",
    "#..==========================..#",
    "#..=========n===W============..#",
    "#..=====n===========n========..#",
    "#..==========================..#",
    "#.....=...============..n......#",
    "#.SSSSSSSS============.........#",
    "#.SSSSSSSS============...=.....#",
    "#.SSSSSSSS============HHHHHHHH.#",
    "#.SSSSSSSS....====....HHHHHHHH.#",
    "#.SSSSSSSS....=n==....HHHHHHHH.#",
    "#.SSSSSSSS....====....HHHHHHHH.#",
    "#.SSSSSSSS....====....HHHHHHHH.#",
    "#.............====....HHHHHHHH.#",
    "#.............====....HHHHHHHH.#",
    "#.............====.............#",
    "#.............====.............#",
    "##############=G==##############",
)
TILES = {"#": "0:ff", ".": "0", "=": "14", "E": "56:ff", "I": "56:ff",
         "S": "56:ff", "H": "56:ff", "X": "56:ff", "W": "3e:ff",
         "M": "3e:ff", "G": "0:1", "n": "0"}
TARGETS = [(15, 31), (16, 16), (16, 10), (12, 16), (20, 17),
           (15, 24), (8, 17), (18, 11), (24, 19)]
DEST = Path(__file__).resolve().parents[1] / "games/tbs/src/map/map_180/map.txt"
def source():
    assert len(LAYOUT) == 32 and all(len(row) == 32 for row in LAYOUT)
    assert all(set(row) <= TILES.keys() for row in LAYOUT)
    assert sum(row.count("G") for row in LAYOUT) == 1
    assert LAYOUT[31][15] == "G"
    assert all(LAYOUT[0][i] == "#" for i in range(32))
    assert all(LAYOUT[31][i] == "#" for i in range(32) if i != 15)
    seen, queue = {(15, 28)}, deque([(15, 28)])
    while queue:
        x, y = queue.popleft()
        for X, Y in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= X < 32 and 0 <= Y < 32 and (X,Y) not in seen:
                if LAYOUT[Y][X] in ".=nMWG":
                    seen.add((X,Y))
                    queue.append((X,Y))
    assert all(point in seen for point in TARGETS), "Unreachable landmark"
    rows = [" ".join(TILES[c] for c in row) for row in LAYOUT]
    return "grid:128x128\tat:0,0\tfill:0:ff\n" + "\n".join(rows) + "\n"
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = source()
    if args.check:
        assert DEST.read_text() == text, "map.txt out of sync"
        print("Aster geometry and tracked map validated")
    else:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        DEST.write_text(text)
        print(f"Generated {DEST}")
if __name__ == "__main__":
    main()
