"""Simplified Diffie-Hellman based 1-out-of-2 OT channel.

This file intentionally keeps the same old-version teaching logic, but splits
it cleanly so the receiver step can run on the frontend/client and the sender
step can run behind FastAPI.
"""

import hashlib
import secrets
from core.config import G, P
from core.utils import xor_bytes


class OTChannel:
    """One layer of 1-out-of-2 Oblivious Transfer."""

    def receiver_step1(self, bit: int) -> tuple[int, int, int]:
        """Client-side step.

        The client keeps x private, sends only h0 and h1 to the server.
        The selected branch contains g^x; the other branch is random noise.
        """
        if bit not in (0, 1):
            raise ValueError("bit must be 0 or 1")

        x = secrets.randbelow(P - 3) + 2
        h = pow(G, x, P)
        fake = secrets.randbelow(P - 3) + 2

        if bit == 0:
            return h, fake, x
        return fake, h, x

    def sender_step2(self, m0: bytes, m1: bytes, h0: int, h1: int) -> tuple[bytes, bytes, int]:
        """Server-side step.

        The server encrypts both messages. The client can only decrypt the one
        corresponding to the branch where it knows x.
        """
        y = secrets.randbelow(P - 3) + 2

        k0 = pow(h0, y, P)
        k1 = pow(h1, y, P)

        k0_bytes = hashlib.sha256(str(k0).encode()).digest()[: len(m0)]
        k1_bytes = hashlib.sha256(str(k1).encode()).digest()[: len(m1)]

        c0 = xor_bytes(m0, k0_bytes)
        c1 = xor_bytes(m1, k1_bytes)
        gy = pow(G, y, P)

        return c0, c1, gy

    def receiver_step3(self, c0: bytes, c1: bytes, gy: int, x: int, bit: int) -> bytes:
        """Client-side final step. Recover only the chosen message."""
        if bit not in (0, 1):
            raise ValueError("bit must be 0 or 1")

        k = pow(gy, x, P)
        k_bytes = hashlib.sha256(str(k).encode()).digest()

        if bit == 0:
            return xor_bytes(c0, k_bytes[: len(c0)])
        return xor_bytes(c1, k_bytes[: len(c1)])
