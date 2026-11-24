#!/usr/bin/env python3
"""Compose "Umbral Rift", the Rift's field music, as a Golden Sun MIDI.

An original piece written for Golden Sun: Ashfall. Nothing here is transcribed
from another game. It is written in code so the notes are reviewable in a
diff and the build regenerates the same bytes every time.

Mood: still and uneasy, a place where time has come apart. D minor, about
67 beats a minute, a 16-bar loop (about a minute):

  - low strings hold each chord; two more string voices move by step;
  - a harp arpeggio repeats a 5-note figure over 16-step bars, so it slips
    against the beat and never lines up the same way twice in a bar;
  - a bell motif marks every four bars;
  - the choir enters on bar 5, the flute sings the second half;
  - timpani mark the phrase starts.

Engine timing (as in the vanilla songs): 96 ticks are one bar of 4/4, so a
quarter note is 24 ticks; no note may last longer than 96 ticks.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "games/tbs/sound/songs/mus_umbral_rift.mid"

BAR = 96
# The engine's note lengths (tools/ags-music/sequence.c); others are rounded
# down to the nearest of these.
LENGTHS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
           20, 21, 22, 23, 24, 28, 30, 32, 36, 40, 42, 44, 48, 52, 54, 56, 60,
           64, 66, 68, 72, 76, 78, 80, 84, 88, 90, 92, 96)
Q = 24
BARS = 16
LOOP = BAR * BARS
# Microseconds per 96 ticks: about 67 quarter notes a minute.
TEMPO_US = 3_600_000

# Sound_BgmVoices programs, by their use in the vanilla songs.
STRINGS, CHOIR, HARP, BELL, FLUTE, TIMPANI = 48, 52, 46, 8, 73, 47

# One chord per two bars: i, VI, iv, bII (Neapolitan), i, VI, ii dim, V.
#        low root  mid  high  choir  harp tones (root, third, fifth)
CHORDS = [
    (50, 65, 69, None, (62, 65, 69)),  # D minor
    (46, 65, 70, None, (58, 62, 65)),  # B flat
    (43, 62, 67, 74, (55, 58, 62)),    # G minor
    (51, 63, 67, 75, (51, 55, 58)),    # E flat
    (50, 65, 69, 74, (62, 65, 69)),    # D minor
    (46, 65, 70, 74, (58, 62, 65)),    # B flat
    (52, 64, 67, 70, (52, 55, 58)),    # E diminished
    (45, 64, 69, 73, (57, 61, 64)),    # A major
]


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, 0x80 | (n & 0x7F))
        n >>= 7
    return bytes(out)


class Track:
    def __init__(self):
        self.events = []  # (tick, order, bytes)
        self.n = 0

    def add(self, tick, data):
        self.events.append((tick, self.n, data))
        self.n += 1

    def meta(self, tick, kind, payload):
        self.add(tick, bytes([0xFF, kind]) + vlq(len(payload)) + payload)

    def text(self, tick, kind, s):
        self.meta(tick, kind, s.encode("ascii"))

    def note(self, ch, tick, key, length, velocity):
        assert 0 < length <= BAR, length
        length = max(n for n in LENGTHS if n <= length)
        self.add(tick, bytes([0x90 | ch, key, velocity]))
        # Note-offs sort before a note-on at the same tick (order -1 below).
        self.events.append((tick + length, -1, bytes([0x80 | ch, key, 64])))

    def chunk(self):
        body = b""
        last = 0
        for tick, _, data in sorted(self.events, key=lambda e: (e[0], e[1])):
            body += vlq(tick - last) + data
            last = tick
        return b"MTrk" + len(body).to_bytes(4, "big") + body


def channel(n, program, volume, pan, tempo=False):
    """A track with the vanilla songs' preamble, opened for its loop."""
    t = Track()
    ch = n - 1
    for cc, v in ((0, 0), (91, 50), (101, 0), (100, 0), (6, 2), (38, 0)):
        t.add(0, bytes([0xB0 | ch, cc, v]))
    t.text(0, 6, "key_shift 0")
    t.add(0, bytes([0xC0 | ch, program]))
    t.add(0, bytes([0xB0 | ch, 7, volume]))
    t.add(0, bytes([0xB0 | ch, 10, pan]))
    t.add(0, bytes([0xE0 | ch, 0, 64]))
    if tempo:
        t.meta(0, 0x51, TEMPO_US.to_bytes(3, "big"))
    t.text(0, 6, f"label loop_{n}")
    t.text(0, 7, "loopStart")
    return t, ch


def close(t, n):
    t.text(LOOP, 7, "loopEnd")
    t.text(LOOP, 6, f"goto loop_{n}")
    t.text(LOOP, 6, "fine")
    t.meta(LOOP, 0x2F, b"")


def compose():
    tracks = []

    # 1-3: strings. The root re-strikes every bar, softer on the second.
    for n, voice, vol, pan, vel in ((1, 0, 74, 64, 92), (2, 1, 56, 48, 80),
                                    (3, 2, 56, 80, 80)):
        t, ch = channel(n, STRINGS, vol, pan, tempo=(n == 1))
        for i, chord in enumerate(CHORDS):
            for b in range(2):
                t.note(ch, (2 * i + b) * BAR, chord[voice], BAR - 4,
                       vel - 14 * b)
        close(t, n)
        tracks.append(t)

    # 4: choir, from bar 5 (chord 3).
    t, ch = channel(4, CHOIR, 58, 64)
    for i, chord in enumerate(CHORDS):
        if chord[3] is None:
            continue
        for b in range(2):
            t.note(ch, (2 * i + b) * BAR, chord[3], BAR - 4, 84 - 10 * b)
    close(t, 4)
    tracks.append(t)

    # 5: harp. Five tones over sixteen steps: the figure drifts each beat.
    t, ch = channel(5, HARP, 70, 40)
    step = 0
    for i, chord in enumerate(CHORDS):
        r, th, f = chord[4]
        figure = (r, f, r + 12, th + 12, f + 12)
        for s in range(32):
            k = figure[step % 5]
            vel = 96 if step % 5 == 0 else 68 + 6 * (s % 3)
            t.note(ch, (2 * i) * BAR + s * 6, k, 6, vel)
            step += 1
    close(t, 5)
    tracks.append(t)

    # 6: bells, every four bars.
    t, ch = channel(6, BELL, 60, 88)
    motifs = {0: (81, 79, 74), 4: (82, 81, 74), 8: (81, 79, 74),
              12: (82, 79, 76)}
    for bar, (a, b, c) in motifs.items():
        base = bar * BAR
        t.note(ch, base, a, Q, 90)
        t.note(ch, base + Q, b, Q, 82)
        t.note(ch, base + 2 * Q, c, 2 * Q, 86)
    # The last phrase rises on the dominant and is left hanging.
    t.note(ch, 14 * BAR, 76, Q, 84)
    t.note(ch, 14 * BAR + Q, 81, Q, 84)
    t.note(ch, 14 * BAR + 2 * Q, 85, 2 * Q, 90)
    close(t, 6)
    tracks.append(t)

    # 7: flute, the second half: (bar, beat, key, quarters).
    t, ch = channel(7, FLUTE, 62, 64)
    line = [
        (8, 0, 81, 3), (8, 3, 79, 1),
        (9, 0, 77, 2), (9, 2, 76, 1), (9, 3, 77, 1),
        (10, 0, 74, 4),
        (11, 2, 77, 1), (11, 3, 79, 1),
        (12, 0, 82, 3), (12, 3, 81, 1),
        (13, 0, 79, 2), (13, 2, 76, 2),
        (14, 0, 76, 2), (14, 2, 73, 2),
        (15, 0, 69, 4),
    ]
    for bar, beat, key, q in line:
        length = q * Q - (4 if q == 4 else 2)
        t.note(ch, bar * BAR + beat * Q, key, length, 88)
    close(t, 7)
    tracks.append(t)

    # 8: timpani at the phrase starts; the last bar pulls back to the top.
    t, ch = channel(8, TIMPANI, 76, 64)
    for bar, key in ((0, 50), (4, 43), (8, 50), (12, 52), (14, 45)):
        t.note(ch, bar * BAR, key, Q, 100)
    t.note(ch, 15 * BAR + 2 * Q, 45, 12, 70)
    t.note(ch, 15 * BAR + 3 * Q, 45, 12, 84)
    close(t, 8)
    tracks.append(t)

    names = ",".join(f"track_{i}" for i in range(1, len(tracks) + 1))
    conductor = Track()
    layout = "smsh-sequence 1\n"
    layout += "".join(f"stream track_{i}\n" for i in range(1, len(tracks) + 1))
    layout += "align 4 0\n"
    layout += ("header sound_012 block_count=0 priority=0 reverb=178 "
               f"tone_bank=Sound_BgmVoices tracks={names}\n")
    conductor.text(0, 1, layout)
    # One 96-tick bar per measure, matching the note grid above.
    conductor.meta(0, 0x58, bytes([1, 2, 24, 8]))
    conductor.meta(0, 0x2F, b"")

    header = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 1]) + \
        (len(tracks) + 1).to_bytes(2, "big") + BAR.to_bytes(2, "big")
    return header + conductor.chunk() + b"".join(t.chunk() for t in tracks)


def main():
    OUT.write_bytes(compose())
    print(f"Composed {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
