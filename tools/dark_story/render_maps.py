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

from PIL import Image, ImageDraw, ImageFont

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
    # A cell holding 0xfff is a placeholder: the first time a picture shows up
    # the grid stores no number, and the pictures are numbered in order of
    # first appearance, row by row (map/README.md, "Placeholder metatiles").
    nxt = 0
    for row in grid:
        for c in row:
            if c[0] & 0xFFF == 0xFFF:
                c[0] = (c[0] & ~0xFFF) | nxt
                nxt += 1
    return grid


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def parse_actors(scenes):
    """Placed people and things in a scene's source: (label, x, z) in pixels."""
    found, seen = [], set()
    for scene in scenes:
        f = TBS / f"scene/{snake(scene)}.c"
        if not f.exists():
            continue
        text = f.read_text()
        for m in re.finditer(r"\{\s*(SPRITE_\w+),[^{}]*?MOVEMENT_TYPE_\w+,\s*PIXELS\((-?\d+)\),\s*[^,]+,\s*PIXELS\((-?\d+)\)", text):
            key = (m.group(1), m.group(2), m.group(3))
            if int(m.group(2)) < 0 or int(m.group(3)) < 0:
                continue  # parked off the map until an event brings it in
            if key in seen:
                continue
            seen.add(key)
            found.append((m.group(1)[7:].replace("_", " ").lower(), int(m.group(2)), int(m.group(3))))
    return found


def cell_heights(mapname):
    """Each shape row's rough ground height in pixels (the game works it out per pixel)."""
    rows = []
    f = TBS / f"map/{mapname}/shapes.tsv"
    if not f.exists():  # the map borrows another's table; treat the ground as level
        return rows
    for ln in f.read_text().splitlines()[1:]:
        if ln.strip():
            k, a, b, c = [int(x) for x in ln.split("\t")][:4]
            k &= 15
            rows.append(a if k == 0 else (a + b) / 2 if k in (1, 2) else max(a, b))
    return rows


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
                    # Pure magenta is the palette's "nothing here" colour.
                    if ci and ci < len(pal[bank]) and pal[bank][ci] != (248, 0, 248):
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


def walkability(mapname, x0, y0, x1, y1, scale, margin, top, size):
    """A see-through layer marking walls, steep edges and doors on the ground layer."""
    h, layers = parse_header(mapname)
    grid = parse_grid(TBS / f"map/{mapname}/map.txt")
    heights = cell_heights(mapname)
    lx, ly = layers[0][0] // 2, layers[0][1] // 2
    wc, hc = (h[2] - h[0]) // 2, (h[3] - h[1]) // 2
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cs = 16 * scale

    def at(cx, cy):
        if 0 <= cx < wc and 0 <= cy < hc and ly + cy < len(grid) and lx + cx < len(grid[0]):
            return grid[ly + cy][lx + cx]
        return None

    def height(c):
        return heights[c[2]] if c[2] < len(heights) else 0

    for cy in range(y0 // 16, -(-y1 // 16)):
        for cx in range(x0 // 16, -(-x1 // 16)):
            c = at(cx, cy)
            if c is None:
                continue
            px, py = margin + (cx * 16 - x0) * scale, top + (cy * 16 - y0) * scale
            beh = c[1]
            if beh == 255:
                d.rectangle([px, py, px + cs - 1, py + cs - 1], fill=(220, 30, 30, 120))
                continue
            if 1 <= beh <= 239:
                d.rectangle([px + 1, py + 1, px + cs - 2, py + cs - 2], outline=(40, 120, 255, 255), width=3)
            elif 252 <= beh <= 254:
                d.rectangle([px + 1, py + 1, px + cs - 2, py + cs - 2], outline=(255, 215, 0, 255), width=3)
            for nx, ny, edge in ((cx + 1, cy, (px + cs, py, px + cs, py + cs)),
                                 (cx, cy + 1, (px, py + cs, px + cs, py + cs))):
                n = at(nx, ny)
                if n is not None and n[1] != 255 and abs(height(n) - height(c)) > 8:
                    d.line(edge, fill=(255, 140, 0, 255), width=4)
    return ov


def render_map(mapname, layers, pal, sheets, behavior=False, marks=(), actors=()):
    h, _ = parse_header(mapname)
    wc, hc = (h[2] - h[0]) // 2, (h[3] - h[1]) // 2
    backdrop = (214, 208, 190)  # a plain floor colour; the game sets its own
    img = Image.new("RGB", (wc * 16, hc * 16), backdrop)
    # The back layer (priority 3) first, the front (priority 1) last.
    for L in sorted(layers, key=lambda l: -h[4 + l]):
        draw_layer(img, mapname, L, pal, sheets, behavior)
    # Crop to where something is drawn (plus the placed actors), keeping the
    # ruler in the map's own pixels.
    bg = Image.new("RGB", img.size, backdrop)
    from PIL import ImageChops
    box = ImageChops.difference(img, bg).getbbox() or (0, 0, img.width, img.height)
    pts = [(x, z) for _, x, z in list(actors) + list(marks)]
    x0 = min([box[0]] + [x - 24 for x, _ in pts])
    y0 = min([box[1]] + [z - 40 for _, z in pts])
    x1 = max([box[2]] + [x + 24 for x, _ in pts])
    y1 = max([box[3]] + [z + 24 for _, z in pts])
    x0, y0 = max(0, x0 // 32 * 32), max(0, y0 // 32 * 32)
    x1, y1 = min(img.width, -(-x1 // 32) * 32), min(img.height, -(-y1 // 32) * 32)
    img = img.crop((x0, y0, x1, y1))
    # Wash the picture out a little so the labels stand out from it.
    img = Image.blend(img, Image.new("RGB", img.size, (236, 232, 220)), 0.35)
    scale = 2
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    font = ImageFont.load_default(size=15)
    small = ImageFont.load_default(size=13)
    margin, banner = 44, 36
    legend = [f"{i + 1}. {n}  at {x}, {z}" for i, (n, x, z) in enumerate(actors)]
    legend += [f"*  {n}  at {x}, {z}" for x, z, n in marks]
    rows = max(1, -(-len(legend) // 2))
    foot = 16 + rows * 20 if legend else 8
    top = banner + margin
    out = Image.new("RGB", (img.width + margin, img.height + top + foot), (24, 24, 32))
    out.paste(img, (margin, top))
    out = out.convert("RGBA")
    out.alpha_composite(walkability(mapname, x0, y0, x1, y1, scale, margin, top, out.size))
    out = out.convert("RGB")
    d = ImageDraw.Draw(out)
    d.text((8, 4), "Numbers are pixels, written x, z: use them as PIXELS(x) and PIXELS(z).  Red circles: people already here.",
           fill=(255, 255, 255), font=small)
    d.text((8, 18), "Red cells: wall.   Orange line: too steep to step over.   Blue frame: door or event cell.   "
           "Yellow frame: ledge, climb or jump.   Plain: walkable.", fill=(255, 220, 150), font=small)

    def label(x, y, text):
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            d.text((x + ox, y + oy), text, fill=(0, 0, 0), font=small)
        d.text((x, y), text, fill=(255, 255, 255), font=small)

    gx0, gz0 = -(-x0 // 64) * 64, -(-y0 // 64) * 64
    for px in range(gx0, x1 + 1, 64):
        x = margin + (px - x0) * scale
        d.line([(x, top), (x, top + img.height)], fill=(60, 60, 90), width=1)
        d.text((x + 3, banner + 14), str(px), fill=(255, 230, 130), font=font)
    for pz in range(gz0, y1 + 1, 64):
        y = top + (pz - y0) * scale
        d.line([(margin, y), (margin + img.width, y)], fill=(60, 60, 90), width=1)
        d.text((2, y + 3), str(pz), fill=(255, 230, 130), font=font)
    # Every crossing says where it is, so no ruler reading is needed.
    for px in range(gx0, x1, 64):
        for pz in range(gz0, y1, 64):
            label(margin + (px - x0) * scale + 3, top + (pz - y0) * scale + 3, f"{px},{pz}")
    for i, (n, ax, az) in enumerate(actors):
        x, y = margin + (ax - x0) * scale, top + (az - y0) * scale
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(220, 30, 30), outline=(255, 255, 255), width=2)
        d.text((x, y), str(i + 1), fill=(255, 255, 255), font=font, anchor="mm")
    for mx, mz, label in marks:
        x, y = margin + (mx - x0) * scale, top + (mz - y0) * scale
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(30, 90, 220), outline=(255, 255, 255), width=2)
        d.text((x, y), "*", fill=(255, 255, 255), font=font, anchor="mm")
    for i, line in enumerate(legend):
        col, row = divmod(i, rows)
        d.text((margin + col * (out.width - margin) // 2, top + img.height + 10 + row * 20), line, fill=(255, 255, 255), font=small)
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
            im = render_map(mapname, [int(L) for L in a.layers], pal, sheets, a.behavior, marks, parse_actors(scenes))
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
