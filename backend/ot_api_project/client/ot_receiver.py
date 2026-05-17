"""Client-side OT receiver logic.

This file keeps choice_index and bits local to the client. It supports both:
1. old in-process demo flow, and
2. API-based flow where h0/h1 are sent to the server and c0/c1/gy come back.
"""

from core.ot_channel import OTChannel
from core.prf import PRF
from core.utils import int_to_bitlist, xor_bytes


class OTReceiver:
    """Client-side receiver for the 1-out-of-N OT construction."""

    def __init__(self, choice_index: int, level_count: int):
        if choice_index < 0:
            raise ValueError("choice_index must be non-negative")
        self.choice_index = choice_index
        self.bits = int_to_bitlist(choice_index, level_count)
        self.selected_keys: list[bytes] = []
        self._pending_x_by_level: dict[int, int] = {}

    def start_level(self, level: int) -> tuple[int, int]:
        """API-friendly step: generate h0/h1 for one OT level.

        Return h0/h1 to send to POST /api/ot/step. Keep x private locally.
        """
        bit = self.bits[level]
        h0, h1, x = OTChannel().receiver_step1(bit)
        self._pending_x_by_level[level] = x
        return h0, h1

    def finish_level(self, level: int, c0: bytes, c1: bytes, gy: int) -> bytes:
        """API-friendly step: decrypt the selected key for one OT level."""
        if level not in self._pending_x_by_level:
            raise ValueError("start_level must be called before finish_level")

        bit = self.bits[level]
        x = self._pending_x_by_level.pop(level)
        selected_key = OTChannel().receiver_step3(c0, c1, gy, x, bit)
        self.selected_keys.append(selected_key)
        return selected_key

    def obtain_keys_in_process(self, key_pairs, channel: OTChannel) -> None:
        """Old local demo flow. Do not use this in real API mode."""
        for level, bit in enumerate(self.bits):
            h0, h1, x = channel.receiver_step1(bit)
            m0, m1 = key_pairs[level]
            c0, c1, gy = channel.sender_step2(m0, m1, h0, h1)
            self.selected_keys.append(channel.receiver_step3(c0, c1, gy, x, bit))

    def recover_key(self, masked_keys: list[bytes]) -> bytes:
        """Recover the AES key for self.choice_index from public masked_keys."""
        if self.choice_index >= len(masked_keys):
            raise ValueError("choice_index is outside masked_keys")
        if len(self.selected_keys) != len(self.bits):
            raise ValueError("not all OT levels have been completed")

        y = masked_keys[self.choice_index]
        mask = bytes(len(y))

        for key in self.selected_keys:
            mask = xor_bytes(mask, PRF(key, len(y)).eval(self.choice_index))

        return xor_bytes(y, mask)
