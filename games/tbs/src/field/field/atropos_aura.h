/* Ashfall: Atropos aura, generated from the approved ten-frame preview.
 * Sparse indexed changes: 12-bit pixel offset, expected palette index,
 * replacement palette index. The body sprite is 64 x 64, row-major.
 * Apply after the body and before higher-priority layers. No new OAM,
 * palette, hardware blend register or animation slot is allocated.
 * The table is tied to the approved 16-frame black-scythe sprite. */
#ifndef ASHFALL_ATROPOS_AURA_H
#define ASHFALL_ATROPOS_AURA_H

#define ATROPOS_AURA_PHASES 10
#define ATROPOS_AURA_POSES 8
extern const u16 sAtroposAuraOffsets[81];
extern const u32 sAtroposAuraChanges[52620];

static void AtroposAura_Apply(u8 *pixels, u32 frame, u32 phase) {
  u32 table, i, end, change, offset;
  if (frame >= 16 || phase >= ATROPOS_AURA_PHASES)
    return;
  table = (frame >> 1) * ATROPOS_AURA_PHASES + phase;
  i = sAtroposAuraOffsets[table];
  end = sAtroposAuraOffsets[table + 1];
  for (; i < end; i++) {
    change = sAtroposAuraChanges[i];
    offset = change & 0xfff;
    if (pixels[offset] == ((change >> 12) & 0xff))
      pixels[offset] = (u8)(change >> 20);
  }
}
#endif
