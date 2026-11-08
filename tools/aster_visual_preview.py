#!/usr/bin/env python3
"""Aster native-Golden-Sun tile preview (NOT an emulator screenshot).

Decode Golden Sun Vale's checked-in indexed tileset PNGs and metatile TSV into
an image of Map180's three layer windows. Draw no pixels from outside the
repo's original 'set_16' graphics. Explicitly highlight unpainted ground.
Generated PNGs are reproducible review artifacts, not proof of game collision,
sprite priority, palette animation or proper runtime camera placement.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "games/tbs/src/graphics/tileset/set_02"
METATILES = ROOT / "games/tbs/src/map/map_003/metatiles.tsv"
GRID = ROOT / "games/tbs/src/map/map_180/map.txt"
OUT = ROOT / "tools/aster_visual_review.png"
ANNOTATED = ROOT / "tools/aster_visual_review_events.png"
CELL = 16
SIDE = 64
IMAGE = SIDE * CELL
EMPTY_BG = (129, 0, 135, 255)  # visible missing-ground diagnostic
LOCATIONS = {
    "Sealed house": (3, 3),
    "Inn": (43, 3),
    "West home": (3, 24),
    "East home": (50, 24),
    "Shop": (3, 44),
    "Duplicate": (50, 44),
    "Memorial": (32, 14),
    "Well": (32, 35),
    "Gate": (32, 62),
}

def load_tiles():
    # These 256x128 PNGs encode 512 8x8 tiles each:
    # a -> GBA charblock 1, b -> charblock 2, c -> charblock 3.
    # d is in animation RAM and is not a fourth ordinary charblock.
    # See MapGrid_LoadMap in games/tbs/src/field/field/map_grid.c.
    blocks = {}
    source_sizes = {}
    for block, name in ((1, "tiles_a"), (2, "tiles_b"),
                        (3, "tiles_c")):
        path = BASE / (name + ".png")
        raw = Image.open(path)
        if raw.mode != "P":
            raise AssertionError(f"{name}: native indexed PNG required")
        if raw.size != (256,128):
            raise AssertionError(f"{name}: unexpected source size {raw.size}")
        tiles = []
        for y in range(0, raw.height, 8):
            for x in range(0, raw.width, 8):
                tiles.append(raw.crop((x,y,x+8,y+8)))
        assert len(tiles) == 512
        blocks[block] = tiles
        source_sizes[name] = raw.size
    # The fourth sheet is tiles for the game's animation script; its
    # imagery does not occupy a static background charblock.
    source_sizes["tiles_d_animation"] = Image.open(
        BASE / "tiles_d.png").size
    pal = Image.open(BASE / "palette.png").convert("RGB")
    if pal.width != 16:
        raise AssertionError("Expected 16 background palette pens")
    return blocks, pal, source_sizes

def load_metatiles():
    with METATILES.open(encoding="utf-8", newline="") as f:
        rows = csv.reader(f, delimiter="\t")
        header = next(rows)
        if header != ["top_left:u16", "top_right:u16",
                      "bottom_left:u16", "bottom_right:u16"]:
            raise AssertionError(f"Metatile columns changed: {header}")
        result = [[int(v, 0) for v in row] for row in rows if row]
    return result

def load_map():
    lines = GRID.read_text(encoding="utf-8").splitlines()
    if not lines[0].startswith("grid:128x128"):
        raise AssertionError("Unexpected map layout")
    rows = [line.split() for line in lines[1:]]
    if len(rows) != 128 or any(len(row) != 128 for row in rows):
        raise AssertionError("Expected full 128x128 source grid")
    return rows

def decode_tile(entry, blocks, pal, problems, cache, charbase):
    cache_key=(entry,charbase)
    if cache_key in cache:
        return cache[cache_key]
    idx = entry & 0x3ff
    hf = bool(entry & 0x400)
    vf = bool(entry & 0x800)
    bank = (entry >> 12) & 15
    # GBA BG CNT character base is in 16 KiB blocks. A 4bpp tile is
    # 32 bytes, giving 512 tile numbers per block. The game's three
    # imported static sheets occupy blocks 1,2,3. Block 0 is not
    # loaded from Map180 and is represented as transparent here.
    block=charbase+idx//512
    local=idx%512
    if block == 0:
        return Image.new("RGBA",(8,8),(0,0,0,0))
    if block not in blocks or bank >= pal.height:
        problems.add((block,local,bank))
        return Image.new("RGBA",(8,8),(255,0,80,220))
    tile=blocks[block][local]
    if hf:
        tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if vf:
        tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    colors=[pal.getpixel((c,bank)) for c in range(16)]
    image=Image.new("RGBA",(8,8),(0,0,0,0))
    source=tile.load()
    dest=image.load()
    for y in range(8):
        for x in range(8):
            n=source[x,y]
            if n:
                dest[x,y]=(*colors[n],255)
    cache[cache_key]=image
    return image

def render_metatile(value, metatiles, blocks, palette, problems,
                    cache, charbase):
    if value == 0xfff:
        return None
    if value < 0 or value >= len(metatiles):
        problems.add(("metatile",value))
        return Image.new("RGBA",(16,16),(255,0,80,220))
    cells=metatiles[value]
    output=Image.new("RGBA",(16,16),(0,0,0,0))
    for entry,(x,y) in zip(cells,[(0,0),(8,0),(0,8),(8,8)]):
        output.alpha_composite(
            decode_tile(entry,blocks,palette,problems,cache,charbase),
            (x,y))
    return output

def make(out=OUT, annotated=ANNOTATED):
    blocks, palette, sizes = load_tiles()
    meta = load_metatiles()
    cells = load_map()
    bad = set()
    cache = {}
    meta_cache = {}
    def draw_cell(canvas, token, x, y, charbase):
        # Only a 12-bit map metatile index is visible; behavior/shape go to
        # field movement and events rather than tile graphics.
        value = int(token.split(":")[0],16) & 0x0fff
        key=(value,charbase)
        if key not in meta_cache:
            meta_cache[key] = render_metatile(
                value,meta,blocks,palette,bad,cache,charbase)
        image = meta_cache[key]
        if image is not None:
            canvas.alpha_composite(image,(x*CELL,y*CELL))
    canvas = Image.new("RGBA",(IMAGE,IMAGE),EMPTY_BG)
    # Render only current Aster layer windows. The alpha mode is a basic
    # source preview and not a precise emulation of BG priority or blending.
    for delta_x,delta_y,charbase in ((0,0,0),(64,0,2),(0,64,2)):
        for y in range(SIDE):
            for x in range(SIDE):
                draw_cell(canvas,cells[y+delta_y][x+delta_x],x,y,charbase)
    canvas.convert("RGB").save(out,optimize=True)
    labels = canvas.copy()
    d = ImageDraw.Draw(labels,"RGBA")
    for name,(x,y) in LOCATIONS.items():
        x_px,y_px = x*CELL,y*CELL
        d.ellipse((x_px-4,y_px-4,x_px+4,y_px+4),fill=(255,240,20,235),
                  outline=(0,0,0,255),width=1)
        d.rectangle((max(0,x_px-2),max(0,y_px-21),
                     min(IMAGE,x_px+len(name)*7),y_px-6),
                     fill=(0,0,0,195))
        d.text((max(0,x_px),max(0,y_px-20)),name,fill=(255,255,255,255))
    labels.convert("RGB").save(annotated,optimize=True)
    print("Aster native source renderer.")
    print("NOT emulator output; does not verify compiled ROM or game collisions.")
    print(f"Tile source images: {sizes}")
    print(f"Image tiles in atlas: {sum(len(v) for v in blocks.values())}; metatile rows: {len(meta)}")
    print(f"Unmapped graphics indexes and palettes: {sorted(bad,key=str)[:40]}")
    print(f"Rendered: {out} | annotated: {annotated}")
    if bad:
        raise AssertionError(f"Unmapped graphic entries: {len(bad)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,default=OUT)
    ap.add_argument("--annotated",type=Path,default=ANNOTATED)
    args=ap.parse_args()
    make(args.output,args.annotated)
