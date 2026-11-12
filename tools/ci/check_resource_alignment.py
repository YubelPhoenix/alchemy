#!/usr/bin/env python3
"""Fail when a resource-directory row is word-aligned in the baseline ROM but
not in the modified one.

Usage: check_resource_alignment.py BASELINE.gba MODIFIED.gba

Most of the game's packed assets have no alignment of their own: they copy
the original packer's padding and assume they start on a word. If an inserted
asset ends off-word, every asset after it shifts off-word too, and its u16/u32
offset tables read back as garbage (corrupted portraits, title icons, maps).
"""
import struct
import sys

ROM = 0x08000000


def directory_rows(path):
    rom = open(path, "rb").read()
    # Row 0 is Rom_Start; row 1 is the table's own address.
    for base in range(0, len(rom) - 8, 4):
        a, b = struct.unpack_from("<II", rom, base)
        if a == ROM and b == ROM + base:
            break
    else:
        raise SystemExit(f"{path}: resource directory not found")
    rows = []
    while base + 4 * len(rows) + 4 <= len(rom):
        (ptr,) = struct.unpack_from("<I", rom, base + 4 * len(rows))
        if ptr != 0 and not ROM <= ptr < ROM + 0x2000000:
            break
        rows.append(ptr)
    return rows


def main():
    baseline = directory_rows(sys.argv[1])
    modified = directory_rows(sys.argv[2])
    bad = [
        (row, ptr)
        for row, ptr in enumerate(modified)
        if ptr & 3 and (row >= len(baseline) or baseline[row] & 3 == 0)
    ]
    for row, ptr in bad:
        print(f"row 0x{row:03X}: 0x{ptr:08X} is off-word by {ptr & 3}")
    if bad:
        raise SystemExit(f"{len(bad)} resources lost word alignment")
    print(f"Resource alignment OK: {len(modified)} rows checked")


if __name__ == "__main__":
    main()
