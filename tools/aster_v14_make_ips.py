#!/usr/bin/env python3
"""Create a full experimental V14 ROM-difference IPS against a clean TBS ROM.

This is NOT an Aster-only/incremental patch for an existing Ashfall build:
all differences in the staged V14 compiled ROM are included, including any
older Ashfall game systems carried by this branch. No network or API calls.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

BASE_SHA1 = "5c4695205413df7db52b9a184815a07783999971"
EOF_OFFSET = 0x454F46
LIMIT = 0x1000000
MAX_RECORD = 65535

def sha(data, kind):
    return hashlib.new(kind, data).hexdigest()

def create_ips(base, changed):
    if len(changed) < len(base) or len(changed) > LIMIT:
        raise ValueError("Modified ROM has an unsupported size")
    if base == changed:
        raise ValueError("No differences; refusing an empty IPS")
    padded = base.ljust(len(changed), b"\x00")
    ips = bytearray(b"PATCH")
    changed_bytes = records = i = 0
    while i < len(changed):
        if padded[i] == changed[i]:
            i += 1
            continue
        start = i
        chunk = bytearray()
        if start == EOF_OFFSET:
            start -= 1
            chunk.append(changed[start])
        i = start + len(chunk)
        while i < len(changed) and len(chunk) < MAX_RECORD:
            if padded[i] == changed[i]:
                break
            chunk.append(changed[i])
            i += 1
        if not chunk or start >= LIMIT:
            raise ValueError("Invalid IPS record")
        ips.extend(start.to_bytes(3, "big"))
        ips.extend(len(chunk).to_bytes(2, "big"))
        ips.extend(chunk)
        changed_bytes += sum(padded[j] != changed[j]
                             for j in range(start, start+len(chunk)))
        records += 1
    ips.extend(b"EOF")
    if len(base) != len(changed):
        ips.extend(len(changed).to_bytes(3, "big"))
    return bytes(ips), changed_bytes, records

def apply_ips(base, ips):
    if not ips.startswith(b"PATCH"):
        raise ValueError("Invalid IPS header")
    out = bytearray(base)
    i = 5
    while True:
        if i + 3 > len(ips):
            raise ValueError("Truncated IPS")
        if ips[i:i+3] == b"EOF":
            i += 3
            break
        offset = int.from_bytes(ips[i:i+3], "big")
        i += 3
        if i + 2 > len(ips):
            raise ValueError("Truncated IPS record length")
        count = int.from_bytes(ips[i:i+2], "big")
        i += 2
        if count:
            if i + count > len(ips):
                raise ValueError("Truncated IPS data")
            payload = ips[i:i+count]
            i += count
        else:
            if i + 3 > len(ips):
                raise ValueError("Truncated IPS RLE data")
            payload = ips[i+2:i+3] * int.from_bytes(ips[i:i+2], "big")
            i += 3
        end = offset + len(payload)
        if end > LIMIT:
            raise ValueError("Out of range IPS payload")
        if end > len(out):
            out.extend(b"\x00"*(end-len(out)))
        out[offset:end] = payload
    if i + 3 == len(ips):
        size = int.from_bytes(ips[i:i+3], "big")
        if size > LIMIT:
            raise ValueError("Unsupported IPS resize")
        out.extend(b"\x00"*max(0,size-len(out)))
        del out[size:]
    elif i != len(ips):
        raise ValueError("Unexpected data after IPS EOF")
    return bytes(out)

def self_test():
    for clean, modified in (
        (b"abcdef", b"abcdZf"),
        (b"\0"*100, b"\1"*100),
        (b"\0"*250, b"\0"*250+b"END"),
        (b"\0"*70000, b"\1"*70000),
        (b"\0"*(EOF_OFFSET+10), b"\0"*EOF_OFFSET+b"X"+b"\0"*9),
    ):
        patch,_,_ = create_ips(clean, modified)
        assert apply_ips(clean, patch) == modified
    print("PASS IPS patch/replay test, long records, extended data and EOF edge")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--clean", type=Path)
    p.add_argument("--modified", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not (args.clean and args.modified and args.out):
        p.error("--clean, --modified, --out are required")
    if args.clean.resolve() == args.modified.resolve():
        raise SystemExit("Clean and modified ROM paths must differ")
    if args.out.suffix.lower() != ".ips":
        raise SystemExit("Output must end with .ips")
    base = args.clean.read_bytes()
    if sha(base, "sha1") != BASE_SHA1:
        raise SystemExit("Wrong clean ROM checksum: " + sha(base, "sha1")
                         + ". Required " + BASE_SHA1 + ". No patch produced.")
    compiled = args.modified.read_bytes()
    ips, changed_bytes, records = create_ips(base, compiled)
    if apply_ips(base, ips) != compiled:
        raise SystemExit("IPS does not reproduce compiled ROM; no patch produced")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(ips)
    try:
        commit = subprocess.check_output(["git","rev-parse","HEAD"],
                    text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):
        commit = "unknown"
    manifest = {
        "purpose": "Aster V14 isolated full-ROM test patch (not an incremental Ashfall update)",
        "branch": "experiment/aster-v14-native-map-staging",
        "source_commit": commit,
        "patch_scope": "complete compiled V14 ROM differences from clean original",
        "compatible_base": "clean English TBS ROM with exact checked SHA-1 only",
        "not_for": "existing Ashfall patched ROMs; stacking onto dark-story-rewrite builds",
        "clean_rom_sha1": BASE_SHA1,
        "compiled_rom_sha256": sha(compiled,"sha256"),
        "patch_sha256": sha(ips,"sha256"),
        "ips_size": len(ips),
        "changed_bytes": changed_bytes,
        "record_count": records,
        "warning": "Not emulator-verified. Apply ONLY to a copy of the verified clean ROM; do not layer onto an existing Ashfall patch. V14 may lack newer Ashfall boss AI/balance."
    }
    args.out.with_suffix(".manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("VERIFIED IPS:",args.out, "records:",records,"bytes:",len(ips))
    print("WARNING: FULL V14 TEST PATCH, not Aster-only or additive to Ashfall.")
    print("Apply ONLY to a copy of the verified CLEAN English TBS ROM.")
    print("Only the IPS and a manifest are saved; no ROM is uploaded")

if __name__ == "__main__":
    main()
