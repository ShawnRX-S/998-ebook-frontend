"""Pseudo-random function used to build the XOR mask for each book key."""

import hashlib


class PRF:
    """SHA-256 based PRF for the coursework OT prototype."""

    def __init__(self, key: bytes, length: int):
        self.key = key
        self.length = length

    def eval(self, x: int) -> bytes:
        """Return PRF(key, x) truncated to the requested byte length."""
        # 8 bytes supports very large catalog indexes and avoids the old 2-byte limit.
        x_bytes = x.to_bytes(8, "big", signed=False)
        return hashlib.sha256(self.key + x_bytes).digest()[: self.length]
