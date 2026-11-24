#!/usr/bin/env python3
"""Compose "Umbral Rift", the Rift's field music, as a Golden Sun MIDI.

An original piece written for Golden Sun: Ashfall. Nothing here is transcribed
from another game. It is written in code so the notes are reviewable in a
diff and the build regenerates the same bytes every time.

Mood: despair in a place where time has come apart. D minor, about 54 beats a
minute, a 16-bar loop (a little over a minute):

  - the bass falls by half steps, D, C sharp, C, B, B flat, A (a lament
    bass), so every chord sinks a little lower than the last;
  - strings hold the chords low; the choir sits close above them, and on
    the last chord holds the bare fifth with no third;
  - an oboe sings falling pairs of notes, each one a sigh, from bar 5;
  - a quiet harp figure of five notes against eight steps falls from the
    top of each chord, slipping against the beat;
  - a low bell tolls a falling half step every four bars;
  - timpani mark the phrases and roll into the loop's return.

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
# Microseconds per 96 ticks: about 54 quarter notes a minute.
TEMPO_US = 4_440_000

# Sound_BgmVoices programs, by their use in the vanilla songs.
STRINGS, CHOIR, HARP, BELL, OBOE, TIMPANI = 48, 52, 46, 8, 68, 47

# One chord per two bars over a falling bass: i, V6, i7/C, IV6 (G/B),
# iv6 (Gm/Bb), i64, VI, V.
#        bass  mid  high  choir  harp tones (low to high)
CHORDS = [
    (50, 57, 65, None, (50, 57, 62, 65, 69)),  # D minor
    (49, 57, 64, None, (49, 57, 61, 64, 69)),  # A over C sharp
    (48, 57, 65, 62, (48, 57, 62, 65, 69)),    # D minor over C
    (47, 55, 62, 62, (47, 55, 59, 62, 67)),    # G over B
    (46, 55, 62, 62, (46, 55, 58, 62, 67)),    # G minor over B flat
    (45, 57, 62, 65, (45, 57, 62, 65, 69)),    # D minor over A
    (46, 58, 62, 65, (46, 58, 62, 65, 70)),    # B flat
    (45, 52, 57, 64, (45, 52, 57, 64, 69)),    # A, the bare fifth
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

    # 1-3: strings, low. Each chord is struck once a bar, the second softer.
    for n, voice, vol, pan, vel in ((1, 0, 82, 64, 96), (2, 1, 60, 44, 78),
                                    (3, 2, 60, 84, 78)):
        t, ch = channel(n, STRINGS, vol, pan, tempo=(n == 1))
        for i, chord in enumerate(CHORDS):
            for b in range(2):
                t.note(ch, (2 * i + b) * BAR, chord[voice], BAR, vel - 16 * b)
        close(t, n)
        tracks.append(t)

    # 4: choir, from bar 5, close above the strings.
    t, ch = channel(4, CHOIR, 70, 64)
    for i, chord in enumerate(CHORDS):
        if chord[3] is None:
            continue
        for b in range(2):
            t.note(ch, (2 * i + b) * BAR, chord[3], BAR, 88 - 12 * b)
    close(t, 4)
    tracks.append(t)

    # 5: harp, quiet: five tones falling from the top of the chord, against
    # eight steps a bar, so the figure lands on a different beat each bar.
    t, ch = channel(5, HARP, 48, 36)
    step = 0
    for i, chord in enumerate(CHORDS):
        figure = tuple(reversed(chord[4]))
        for s in range(16):
            vel = 76 if step % 5 == 0 else 52 + 4 * (s % 2)
            t.note(ch, (2 * i) * BAR + s * 12, figure[step % 5], 12, vel)
            step += 1
    close(t, 5)
    tracks.append(t)

    # 6: a low bell tolls a falling half step every four bars.
    t, ch = channel(6, BELL, 46, 90)
    for bar, (a, b) in ((0, (70, 69)), (4, (70, 69)), (8, (70, 69)),
                        (12, (75, 74))):
        t.note(ch, bar * BAR, a, 2 * Q, 84)
        t.note(ch, bar * BAR + 2 * Q, b, 2 * Q, 70)
    close(t, 6)
    tracks.append(t)

    # 7: oboe, from bar 5: falling pairs, each a sigh, (bar, beat, key, beats).
    t, ch = channel(7, OBOE, 64, 70)
    line = [
        (4, 0, 77, 2), (4, 2, 76, 2), (5, 0, 74, 3),
        (6, 0, 74, 2), (6, 2, 71, 2), (7, 0, 67, 3),
        (8, 0, 70, 2), (8, 2, 69, 2), (9, 0, 67, 3),
        (10, 0, 77, 2), (10, 2, 76, 2), (11, 0, 74, 3),
        (12, 0, 74, 2), (12, 2, 72, 2), (13, 0, 70, 3),
        (14, 0, 69, 2), (14, 2, 68, 2), (15, 0, 69, 4),
    ]
    for bar, beat, key, q in line:
        t.note(ch, bar * BAR + beat * Q, key, q * Q - 2, 84 if beat else 92)
    close(t, 7)
    tracks.append(t)

    # 8: timpani at the phrases, low and soft; a roll back into the loop.
    t, ch = channel(8, TIMPANI, 64, 64)
    for bar, key in ((0, 50), (4, 48), (8, 46), (12, 46), (14, 45)):
        t.note(ch, bar * BAR, key, 2 * Q, 92)
    for k in range(8):
        t.note(ch, 15 * BAR + 2 * Q + k * 6, 45, 6, 44 + 8 * k)
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
