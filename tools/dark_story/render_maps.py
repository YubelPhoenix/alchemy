#!/usr/bin/env python3
"""Draws the game's maps as PNGs with a pixel ruler, to find where actors fit.

Coordinates on the ruler are the layer-local pixels that Actor_SetPosition and
PIXELS(x) use in the scene code (16-pixel cells, so cell = pixel / 16).

  render_maps.py OUT_DIR                  every scene, layer 0
  render_maps.py OUT_DIR Vale Tolbi       only these scenes
  --layers 012   draw these layers      --behavior   label cells' behaviours
  --mark X,Z,label   add a marker (pixels), repeatable
Also writes OUT_DIR/index.md listing which scenes use which map image.
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
TBS = ROOT / "games/tbs/src"


def parse_resources():
    """Offset from ResourceId_Map001 -> resource name, by replaying directory.s."""
    names, n, on = {}, 0, False
    for line in (TBS / "system/resource/directory.s").read_text().splitlines():
        line = line.split("@")[0].strip()
        if line.startswith("group Field, Map001"):
            on, names[0], n = True, "Field_Map001", 1
            continue
        if not on or not line:
            continue
        m = re.match(r"tileset (\w+), (\w+|-)(?:, (.*))?", line)
        if m:
            for i in re.findall(r"\d+", m.group(3) or ""):
                names[n] = "Field_Map" + i; n += 1
            names[n] = f"Tileset_{m.group(1)}Palette"; n += 1
            if m.group(2) != "-":
                for s in m.group(2):
                    names[n] = f"Tileset_{m.group(1)}Tiles{s}"; n += 1
            continue
        m = re.match(r"recolor (\d+)(?:, (.*))?", line)
        if m:
            for i in re.findall(r"\d+", m.group(2) or ""):
                names[n] = "Field_Map" + i; n += 1
            names[n] = f"Tileset_Palette{m.group(1)}"; n += 1
            continue
        m = re.match(r"resource ,? ?(\w+)?,?\s*(\w+)?$", line)
        if line.startswith("resource"):
            names[n] = line.split(",")[-1].strip(); n += 1
        elif line.startswith("unused"):
            n += int(line.split()[1])
        elif line.startswith("group"):
            n += len(line.split(",")) - 1
    return names


def parse_maps_table():
    rows = []
    for line in (TBS / "field/maps.c").read_text().splitlines():
        m = re.match(r"\s*\{\{([\d, ]+)\}\},?", line)
        if m:
            rows.append([int(x) for x in m.group(1).split(",")])
    return rows


def parse_scenes():
    out = []
    for line in (TBS / "field/scenes.s").read_text().splitlines():
        m = re.match(r"\s*scene (\w+), \w+, \w+, (\w+), (\w+)", line)
        if m:
            idx = m.group(3)
            out.append((m.group(1), 1 if idx == "MapIndex_World" else int(idx, 0)))
    return out


def read_palette(png):
    im = Image.open(png).convert("RGB")
    return [[im.getpixel((x, y)) for x in range(im.width)] for y in range(im.height)]


def tile_sheet(name):
    """resource name -> PIL image (indexed), or None."""
    m = re.match(r"Tileset_Set(\d+)Tiles([A-D])$", name)
    if not m:
        return None
    p = TBS / f"graphics/tileset/set_{m.group(1)}/tiles_{m.group(2).lower()}.png"
    return Image.open(p) if p.exists() else None


def palette_for(names, entry):
    m = re.match(r"Tileset_Set(\d+)Palette$", entry)
    if m:
        return read_palette(TBS / f"graphics/tileset/set_{m.group(1)}/palette.png")
    m = re.match(r"Tileset_Palette(\d+)$", entry)
    if m:
        return read_palette(TBS / f"graphics/tileset/palettes/pal_{m.group(1)}.png")
    return None


def parse_grid(path):
    lines = path.read_text().splitlines()
    head = lines[0]
    gw, gh = map(int, re.search(r"grid:(\d+)x(\d+)", head).groups())
    ax, ay = map(int, re.search(r"at:(\d+),(\d+)", head).groups())
    fill = re.search(r"fill:(\S+)", head).group(1).split(":")
    def cell(tok):
        p = tok.split(":")
        return [int(x, 16) if x else 0 for x in p] + [0] * (3 - len(p))
    fillc = cell(":".join(fill))
    grid = [[fillc] * gw for _ in range(gh)]
    for r, line in enumerate(lines[1:]):
        for c, tok in enumerate(line.split()):
            if ay + r < gh and ax + c < gw:
                grid[ay + r][ax + c] = cell(tok)
    return grid


def parse_header(mapname):
    s = (TBS / f"map/{mapname}/map.s").read_text()
    h = re.search(r"map_header ([^\n]+)", s).group(1).split(",")
    h = [int(x, 0) for x in h]
    layers = [[int(x, 0) for x in m.split(",")] for m in re.findall(r"map_layer ([^\n]+)", s)][:3]
    return h, layers


def draw_layer(img, mapname, layer, pal, sheets, behavior=False):
    h, layers = parse_header(mapname)
    left, top, right, bottom = h[:4]
    lx, ly = layers[layer][0], layers[layer][1]
    if h[4 + layer] == 0:
        return
    grid = parse_grid(TBS / f"map/{mapname}/map.txt")
    mt = [tuple(int(x, 16) for x in ln.split("\t")) for ln in
          (TBS / f"map/{mapname}/metatiles.tsv").read_text().splitlines()[1:] if ln.strip()]
    wc, hc = (right - left) // 2, (bottom - top) // 2
    # The header's chars value is where the layer's tiles start in video memory,
    # in 256-tile steps; each sheet holds 512 tiles, A to D in order.
    base = h[7 + layer] * 256
    cache = {}

    def tile(entry):
        key = entry
        if key in cache:
            return cache[key]
        idx, hf, vf, bank = entry & 0x3FF, entry >> 10 & 1, entry >> 11 & 1, entry >> 12
        g = base + idx
        sheet = sheets[g // 512] if g // 512 < len(sheets) else None
        idx = g
        t = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        if sheet is not None and pal is not None and bank < len(pal):
            i = idx % 512
            sx, sy = (i % 32) * 8, (i // 32) * 8
            crop = sheet.crop((sx, sy, sx + 8, sy + 8))
            px = crop.load()
            tp = t.load()
            for y in range(8):
                for x in range(8):
                    ci = px[x, y]
                    if ci:
                        tp[x, y] = pal[bank][ci] + (255,)
        if hf:
            t = t.transpose(Image.FLIP_LEFT_RIGHT)
        if vf:
            t = t.transpose(Image.FLIP_TOP_BOTTOM)
        cache[key] = t
        return t

    d = ImageDraw.Draw(img)
    for cy in range(hc):
        for cx in range(wc):
            gx, gy = lx // 2 + cx, ly // 2 + cy
            if gy >= len(grid) or gx >= len(grid[0]):
                continue
            m_idx, beh, shape = grid[gy][gx]
            m_idx &= 0xFFF  # the top four bits are flags nothing reads
            if m_idx != 0xfff and m_idx < len(mt):
                for q, ent in enumerate(mt[m_idx]):
                    img.paste(tile(ent), (cx * 16 + (q % 2) * 8, cy * 16 + (q // 2) * 8), tile(ent))
            if behavior and beh:
                d.text((cx * 16 + 1, cy * 16 + 3), f"{beh:x}", fill=(255, 255, 0))


def render_map(mapname, layers, pal, sheets, behavior=False, marks=()):
    h, _ = parse_header(mapname)
    wc, hc = (h[2] - h[0]) // 2, (h[3] - h[1]) // 2
    backdrop = (58, 58, 70)  # shows where every layer is clear (the game sets its own backdrop colour)
    img = Image.new("RGB", (wc * 16, hc * 16), backdrop)
    # The back layer (priority 3) first, the front (priority 1) last.
    for L in sorted(layers, key=lambda l: -h[4 + l]):
        draw_layer(img, mapname, L, pal, sheets, behavior)
    scale = 2
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    margin = 34
    out = Image.new("RGB", (img.width + margin, img.height + margin), (10, 10, 14))
    out.paste(img, (margin, margin))
    d = ImageDraw.Draw(out)
    for px in range(0, wc * 16 + 1, 16):
        major = px % 64 == 0
        x = margin + px * scale
        d.line([(x, margin if major else margin), (x, out.height)], fill=(255, 255, 255, 90) if major else (70, 70, 90), width=1)
        if major:
            d.text((x + 2, 4), str(px), fill=(255, 220, 120))
    for pz in range(0, hc * 16 + 1, 16):
        major = pz % 64 == 0
        y = margin + pz * scale
        d.line([(margin, y), (out.width, y)], fill=(255, 255, 255) if major else (70, 70, 90), width=1)
        if major:
            d.text((2, y + 2), str(pz), fill=(255, 220, 120))
    for mx, mz, label in marks:
        x, y = margin + mx * scale, margin + mz * scale
        d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2)
        d.text((x + 7, y - 6), f"{label} {mx},{mz}", fill=(255, 80, 80))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--layers", default="012")
    ap.add_argument("--behavior", action="store_true")
    ap.add_argument("--mark", action="append", default=[])
    a = ap.parse_args()
    marks = []
    for m in a.mark:
        x, z, label = (m.split(",", 2) + ["?"])[:3]
        marks.append((int(x), int(z), label))
    names = parse_resources()
    rows = parse_maps_table()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    by_map = {}
    for scene, idx in parse_scenes():
        if a.scenes and scene not in a.scenes:
            continue
        by_map.setdefault(idx, []).append(scene)
    index = []
    for idx, scenes in sorted(by_map.items()):
        row = rows[idx]
        mapres = names.get(row[0], "")
        m = re.match(r"Field_Map(\d+)$", mapres)
        if not m or not (TBS / f"map/map_{m.group(1)}/map.txt").exists():
            index.append(f"- map row {idx}: {', '.join(scenes)} (no drawable map: {mapres})")
            continue
        mapname = f"map_{m.group(1)}"
        pal = palette_for(names, names.get(row[1], ""))
        sheets = [tile_sheet(names.get(r, "")) for r in row[2:6]]
        files = []
        try:
            im = render_map(mapname, [int(L) for L in a.layers], pal, sheets, a.behavior, marks)
        except Exception as e:  # keep going; report
            print(f"{mapname}: {e}", file=sys.stderr)
            continue
        fn = f"{scenes[0]}.png"  # named for the first scene on the map
        im.save(out / fn)
        files.append(fn)
        index.append(f"- {', '.join(scenes)}: {', '.join(files)}")
    (out / "index.md").write_text("\n".join(index) + "\n")
    print("\n".join(index[:10]), f"... {len(index)} maps")


if __name__ == "__main__":
    main()
