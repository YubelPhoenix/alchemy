#!/usr/bin/env python3
"""Reproduce Gotterkanone's 12 RLE frames exactly from the checked source asset."""
import base64
import bz2
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "games/tbs/src/battle_anim/parts"
SOURCE = PARTS / "gotterkanone.rle.bz2.b64"
TARGET = PARTS / "gotterkanone.rle"
EXPECTED_SHA256 = "81813d7996d6b91bb81efacc5d21654e077fb6d7078ac6f9d41f0bfafaeb8ad6"


def main():
    packed = base64.b64decode(SOURCE.read_text(encoding="ascii").strip(), validate=True)
    data = bz2.decompress(packed)
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != 16249 or digest != EXPECTED_SHA256:
        raise SystemExit("Gotterkanone asset failed checksum validation")
    if TARGET.exists() and TARGET.read_bytes() == data:
        print("Gotterkanone RLE frames already verified (12 images)")
        return
    TARGET.write_bytes(data)
    if hashlib.sha256(TARGET.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise SystemExit("Gotterkanone output failed readback validation")
    print("Gotterkanone RLE frames generated:", TARGET, "bytes:", len(data))


if __name__ == "__main__":
    main()
