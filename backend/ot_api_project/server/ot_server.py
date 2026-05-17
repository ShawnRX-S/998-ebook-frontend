"""Server-side 1-out-of-N OT masking logic from the old version."""

import os
from core.prf import PRF
from core.utils import int_to_bitlist, xor_bytes


class OTServer:
    """Prepare OT key pairs and masked book keys for a whole catalog group."""

    def __init__(self, book_keys: list[bytes]):
        if not book_keys:
            raise ValueError("book_keys cannot be empty")
        self.book_keys = book_keys
        self.N = len(book_keys)
        self.key_len = len(book_keys[0])
        if any(len(k) != self.key_len for k in book_keys):
            raise ValueError("all book keys must have the same length")

    def generate_key_pairs(self, level_count: int) -> list[tuple[bytes, bytes]]:
        """Generate (k0, k1) for each binary OT level."""
        return [
            (os.urandom(self.key_len), os.urandom(self.key_len))
            for _ in range(level_count)
        ]

    def compute_masked_keys(self, key_pairs: list[tuple[bytes, bytes]]) -> list[bytes]:
        """Compute Y_i = book_key_i XOR mask_i for every book index i."""
        level_count = len(key_pairs)
        masked_keys: list[bytes] = []

        for i in range(self.N):
            mask = bytes(self.key_len)
            bits = int_to_bitlist(i, level_count)

            for level, bit in enumerate(bits):
                level_key = key_pairs[level][bit]
                mask = xor_bytes(mask, PRF(level_key, self.key_len).eval(i))

            masked_keys.append(xor_bytes(self.book_keys[i], mask))

        return masked_keys
