#include "gotterkanone_stream.h"

s32 gotterkanone_decode_frame(const u8 *src, u32 src_len, u8 *dst, u32 dst_cap) {
  u32 i = 0;
  u32 j = 0;
  u32 k;
  u32 count;
  u8 control;
  u8 value;

  if (!src || !dst || dst_cap < 3072)
    return -1;
  while (i < src_len) {
    control = src[i++];
    count = (control & 127u) + 1u;
    if (count > 3072u - j)
      return -1;
    if (control & 128u) {
      if (i >= src_len)
        return -1;
      value = src[i++];
      for (k = 0; k < count; k++)
        dst[j++] = value;
    } else {
      if (count > src_len - i)
        return -1;
      for (k = 0; k < count; k++)
        dst[j++] = src[i++];
    }
  }
  return j == 3072 ? 0 : -1;
}
