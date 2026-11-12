#ifndef GOTTERKANONE_STREAM_H
#define GOTTERKANONE_STREAM_H
#include "types.h"
/* RLE frame decoder. Destination must hold 3072 pixels. */
s32 gotterkanone_decode_frame(const u8 *src, u32 src_len, u8 *dst, u32 dst_cap);
#endif
