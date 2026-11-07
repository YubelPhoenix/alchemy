#!/usr/bin/env python3
"""Aster exterior blockout generator (design-stage, not an engine map).

Produces a deterministic 32x32 planning grid. No existing game files are
modified. Next step is to translate the blockout into a real map grid using
validated metatiles and register a scene and world-map entrance.
"""
from pathlib import Path

WIDTH = HEIGHT = 32
grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

def rect(x0, y0, x1, y1, char):
    assert 0 <= x0 <= x1 < WIDTH and 0 <= y0 <= y1 < HEIGHT
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grid[y][x] = char

# # impassable perimeter; paths must connect to south exit.
rect(0, 0, 31, 0, "#")
rect(0, 31, 31, 31, "#")
rect(0, 0, 0, 31, "#")
rect(31, 0, 31, 31, "#")
# Major plaza spine, overlook, and cross streets.
rect(14, 3, 17, 31, "=")
rect(3, 15, 28, 18, "=")
rect(10, 11, 21, 22, "=")
# Buildings: E elder, I inn, S shop, H homes, X sealed house.
for bounds, char in [
    ((11, 3, 20, 8), "E"),
    ((23, 8, 29, 14), "I"),
    ((2, 20, 9, 26), "S"),
    ((2, 7, 9, 13), "H"),
    ((22, 22, 29, 28), "H"),
    ((3, 2, 9, 5), "X"),
]:
    rect(*bounds, char)
# Open walkable approaches to building fronts.
for x, y in [(15, 9), (25, 15), (6, 19), (6, 14), (25, 21)]:
    grid[y][x] = "="
# Well at plaza center. Monument at northern approach.
grid[16][16] = "W"
grid[10][16] = "M"
# Southern entrance and explicit exit cell.
grid[31][15] = "G"
# Reserved NPC placement points; none block the main exit.
for x, y in [(12, 16), (20, 17), (15, 24), (8, 17), (18, 11), (24, 19)]:
    assert grid[y][x] in (".", "=")
    grid[y][x] = "n"

def main():
    out = Path(__file__).with_name("aster_blockout.txt")
    legend = (
        "ASTER EXTERIOR BLOCKOUT — NOT YET A PLAYABLE MAP\n"
        "32x32 planning cells; each represents one proposed 16px map cell.\n"
        "# boundary | . ground | = path | E elder | I inn | S shop\n"
        "H home | X sealed house | W well | M memorial | G exit | n NPC\n\n"
    )
    out.write_text(legend + "\n".join("".join(row) for row in grid) + "\n")
    print(out)
    # Prototype Alchemy map grid, not yet wired to a scene.
    # Uses metatile 1 from the selected reference tileset as placeholder ground.
    source = Path(__file__).with_name("aster_map.txt")
    cells = []
    for row in grid:
        encoded = []
        for symbol in row:
            if symbol in "#EISHX":
                encoded.append("fff:ff")
            elif symbol == "G":
                encoded.append("1:1")  # reserved exit behavior; requires scene trigger
            else:
                encoded.append("1")
        cells.append(" ".join(encoded))
    source.write_text(
        "grid:128x128\\tat:0,0\\tfill:fff:ff\\n"
        + "\\n".join(cells) + "\\n"
    )
    print(source)


if __name__ == "__main__":
    main()
