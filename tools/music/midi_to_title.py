#!/usr/bin/env python3
"""Turns a plain one-track piano MIDI into the song format ags-music reads.

usage: midi_to_title.py INPUT.mid OUTPUT.mid SONG_NAME   (SONG_NAME: sound_070)

The engine counts time in clocks (one MIDI tick of the output is one clock), so
the source's ticks are kept one to one and the tempo is chosen to match.
Notes are capped in length and snapped to the engine's duration table, and
split across three tracks by pitch so the bass and treble get their own voice.
"""
import struct, sys

DUR = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,28,30,32,
       36,40,42,44,48,52,54,56,60,64,66,68,72,76,78,80,84,88,90,92,96]
MAX_LEN = 44          # clocks a note may ring; the piano sample decays anyway
MAX_POLY = 10         # keep the mixer from stealing every voice
WINDOW = 22          # ticks per thinning window (half a beat)


def vlq(d, i):
    v = 0
    while True:
        b = d[i]; i += 1; v = (v << 7) | (b & 127)
        if not b & 128:
            return v, i


def read_notes(path):
    d = open(path, 'rb').read()
    fmt, n, div = struct.unpack('>HHH', d[8:14])
    i = 14; notes = []; tempo = 500000
    for _ in range(n):
        ln = struct.unpack('>I', d[i + 4:i + 8])[0]; e = i + 8 + ln; j = i + 8
        tm = 0; rs = 0; open_ = {}
        while j < e:
            dt, j = vlq(d, j); tm += dt; s = d[j]
            if s == 0xff:
                ty = d[j + 1]; l, k = vlq(d, j + 2)
                if ty == 0x51 and tempo == 500000 and l == 3:
                    tempo = int.from_bytes(d[k:k + 3], 'big')
                j = k + l
            elif s in (0xf0, 0xf7):
                l, k = vlq(d, j + 1); j = k + l
            else:
                if s & 0x80: rs = s; j += 1
                ty = rs >> 4
                if ty in (0xc, 0xd):
                    j += 1; continue
                a, b = d[j], d[j + 1]; j += 2
                if ty == 9 and b > 0:
                    open_.setdefault(a, []).append((tm, b))
                elif ty == 8 or (ty == 9 and b == 0):
                    if open_.get(a):
                        t0, v = open_[a].pop(0)
                        notes.append((t0, tm, a, v))
        i = e
    return notes, div, tempo


def vl(n):
    out = [n & 127]; n >>= 7
    while n:
        out.append((n & 127) | 128); n >>= 7
    return bytes(reversed(out))


class Trk:
    def __init__(self): self.ev = []   # (tick, order, bytes)
    def add(self, tick, data): self.ev.append((tick, len(self.ev), data))
    def meta(self, tick, ty, data): self.add(tick, bytes([0xff, ty, *vl(len(data))]) + data)
    def bytes(self):
        out = b''; last = 0
        for t, _, d in sorted(self.ev):
            out += vl(t - last) + d; last = t
        out += vl(0) + b'\xff\x2f\x00'
        return b'MTrk' + struct.pack('>I', len(out)) + out


def thin(notes, keep_fraction):
    """Keeps the notes that carry the tune: per short window the highest
    (melody) and lowest (bass) note always stay, and the rest are ranked by
    loudness and length until keep_fraction of all notes remain."""
    win = {}
    for n in notes:
        win.setdefault(n[0] // WINDOW, []).append(n)
    must = set()
    for w in win.values():
        must.add(id(max(w, key=lambda a: (a[2], a[3]))))
        must.add(id(min(w, key=lambda a: (a[2], -a[3]))))
    rest = sorted((n for n in notes if id(n) not in must),
                  key=lambda a: -(a[3] * 2 + min(a[1], 40)))
    target = int(len(notes) * keep_fraction)
    keep = set(must)
    for n in rest:
        if len(keep) >= target: break
        keep.add(id(n))
    return [n for n in notes if id(n) in keep]


def main(src, dst, name, keep_fraction=1.0):
    notes, div, tempo = read_notes(src)
    import os
    if os.environ.get('MAX_TICKS'):
        notes = [n for n in notes if n[0] < int(os.environ['MAX_TICKS'])]
    # one source tick = one engine clock; engine tempo T plays 0.8*T clocks/s
    clocks_per_sec = div * 1e6 / tempo
    T = max(1, min(255, round(clocks_per_sec / 0.8)))
    micros = round(7200000000 * 280896 / (16777216 * T))
    out = []
    for t0, t1, k, v in notes:
        ln = max(1, min(MAX_LEN, t1 - t0))
        ln = max(x for x in DUR if x <= ln)
        out.append([t0 + 24, ln, k, max(40, min(127, v))])
    out.sort()
    if keep_fraction < 1.0:
        out = thin(out, keep_fraction)
    # thin out dense overlaps: drop the quietest notes above MAX_POLY
    kept = []; active = []
    for n in out:
        active = [a for a in active if a[0] + a[1] > n[0]]
        if len(active) >= MAX_POLY:
            weakest = min(active + [n], key=lambda a: a[3])
            if weakest is n:
                continue
            active.remove(weakest); kept.remove(weakest)
        active.append(n); kept.append(n)
    end = max(n[0] + n[1] for n in kept) + 24
    end = (end + 23) // 24 * 24
    bands = [(0, 47, 24, 100, 56), (48, 71, 47, 96, 64), (72, 127, 47, 84, 72)]
    tracks = []
    for lo, hi, prog, vol, pan in bands:
        t = Trk(); ch = len(tracks)
        for cc, val in ((0, 0), (91, 50), (101, 0), (100, 0), (6, 2), (38, 0)):
            t.add(0, bytes([0xb0 | ch, cc, val]))
        t.meta(0, 6, b'key_shift 0')
        t.add(0, bytes([0xc0 | ch, prog]))
        t.add(0, bytes([0xb0 | ch, 7, vol]))
        t.add(0, bytes([0xb0 | ch, 10, pan]))
        t.add(0, bytes([0xe0 | ch, 0, 64]))
        t.meta(24, 6, b'label loop_%d' % (len(tracks) + 1))
        t.meta(24, 7, b'loopStart')
        for t0, ln, k, v in kept:
            if lo <= k <= hi:
                t.add(t0, bytes([0x90 | ch, k, v]))
                t.add(t0 + ln, bytes([0x80 | ch, k, 64]))
        t.meta(end, 7, b'loopEnd')
        t.meta(end, 6, b'goto loop_%d' % (len(tracks) + 1))
        t.meta(end, 6, b'fine')
        tracks.append(t)
    tracks[0].meta(0, 0x51, micros.to_bytes(3, 'big'))
    cond = Trk()
    names = ','.join('track_%d' % (i + 1) for i in range(len(tracks)))
    skel = 'smsh-sequence 1\n' + ''.join('stream track_%d\n' % (i + 1) for i in range(len(tracks)))
    skel += 'align 4 0\nheader %s block_count=0 priority=0 reverb=178 tone_bank=Sound_BgmVoices tracks=%s\n' % (name, names)
    cond.meta(0, 1, skel.encode())
    cond.add(0, b'\xff\x58\x04\x01\x04\x18\x08')
    body = cond.bytes() + b''.join(t.bytes() for t in tracks)
    hdr = b'MThd' + struct.pack('>IHHH', 6, 1, 1 + len(tracks), 96)
    open(dst, 'wb').write(hdr + body)
    print('notes in', len(notes), 'kept', len(kept), 'engine tempo', T, 'clocks', end, 'seconds', end / (0.8 * T))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 1.0)
