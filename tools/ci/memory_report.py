#!/usr/bin/env python3
"""Prints how full the GBA's memory is, from the linker map, and what uses the
most of it: whole-region totals for fast memory (IWRAM), EWRAM and ROM, then the
biggest object files in each. Reporting only; it never fails the build.
Usage: memory_report.py out/tbs-en/tbs-en.map"""
import re
import sys
from collections import Counter

REGIONS = (("IWRAM", 0x03000000, 0x03008000),
           ("EWRAM", 0x02000000, 0x02040000),
           ("ROM", 0x08000000, 0x0A000000))

text = open(sys.argv[1], errors="replace").read()
start = text.find("Linker script and memory map")
lines = text[start:].splitlines()
usage = {name: Counter() for name, _, _ in REGIONS}
section = re.compile(r"^\s+(\S+)?\s*0x([0-9a-f]{8,16})\s+0x([0-9a-f]+)\s*(\S.*)?$")
pending = None
for line in lines:
    if re.match(r"^ \S+$", line) and not line.startswith("  "):
        pending = line.strip()        # a long section name wrapped onto its own line
        continue
    m = section.match(line)
    if not m:
        pending = None
        continue
    name, address, size, owner = m.group(1), int(m.group(2), 16), int(m.group(3), 16), m.group(4)
    if not owner and pending is None:
        continue
    if not size:
        continue
    owner = (owner or "?").strip().split("/")[-1]
    for region, low, high in REGIONS:
        if low <= address < high:
            usage[region][owner] += size
    pending = None

for region, low, high in REGIONS:
    total = sum(usage[region].values())
    capacity = high - low
    print(f"\n{region}: {total:,} of {capacity:,} bytes counted "
          f"({100.0 * total / capacity:.1f}%), {capacity - total:,} left")
    for owner, size in usage[region].most_common(12):
        print(f"  {size:>10,}  {owner}")
