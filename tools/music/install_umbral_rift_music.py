#!/usr/bin/env python3
"""Restore the experimental Umbral Rift MIDI used only by the music test branch.

The original source recording is user-provided "Opera House Massacre!"
(Golden Sun: Dark Dawn, heard during the Grave Eclipse). This MIDI is a rough
automated transcription, NOT a note-accurate extraction or final arrangement.
The committed data is compressed to stay reproducible without committing a
machine-generated binary and is checked before the converter uses it.
"""
from pathlib import Path
import base64
import hashlib
import zlib

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "games/tbs/sound/songs/mus_umbral_rift.mid"
SOURCE = OUT.with_name(OUT.name + ".zlib.b64")
EXPECTED_SHA256 = "566454f814d01bd28db0ae4b0ec28265b7b5b2dde46c370a4cbd09522f820900"

def main() -> None:
    packed = base64.b64decode(SOURCE.read_text(encoding="ascii").strip(), validate=True)
    midi = zlib.decompress(packed)
    digest = hashlib.sha256(midi).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"Refusing mismatched Umbral Rift music data: {digest}")
    if not midi.startswith(b"MThd"):
        raise SystemExit("Refusing invalid MIDI header")
    OUT.write_bytes(midi)
    print(f"Prepared test MIDI: {OUT} ({len(midi)} bytes)")

if __name__ == "__main__":
    main()
