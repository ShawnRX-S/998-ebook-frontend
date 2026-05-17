"""FastAPI service layer wrapping the old OT design.

This is the key bridge you wanted:
- Old OTServer / OTChannel logic is preserved.
- API only handles session creation and per-level OT messages.
- choice_index, bit path, and selected book stay client-side only.
"""

import base64
import math
import secrets
import time
from typing import Any

from core.ot_channel import OTChannel
from core.utils import next_power_of_two
from server.book_storage_db_service import BookStorageDBService
from server.ot_server import OTServer


OT_SESSION_CACHE: dict[str, dict[str, Any]] = {}


def b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def b64_decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


class OTFlowService:
    """Coordinate catalog storage, OT sessions, and OT API steps."""

    def __init__(self):
        self.book_storage = BookStorageDBService()

    def get_public_catalog(self, group_id: str = "default") -> dict[str, Any]:
        return self.book_storage.get_public_catalog(group_id)

    def get_encrypted_group_package(self, group_id: str = "default") -> dict[str, Any]:
        return self.book_storage.get_encrypted_group_package(group_id)

    def create_ot_session(self, group_id: str = "default") -> dict[str, Any]:
        raw_keys = self.book_storage.get_book_keys_for_group(group_id)
        actual_n = len(raw_keys)
        padded_n = next_power_of_two(actual_n)

        padded_keys = list(raw_keys)
        while len(padded_keys) < padded_n:
            padded_keys.append(secrets.token_bytes(len(raw_keys[0])))

        level_count = 0 if padded_n <= 1 else int(math.log2(padded_n))
        ot_server = OTServer(padded_keys)
        key_pairs = ot_server.generate_key_pairs(level_count)
        masked_keys = ot_server.compute_masked_keys(key_pairs)

        session_id = secrets.token_urlsafe(24)
        OT_SESSION_CACHE[session_id] = {
            "group_id": group_id,
            "created_at": time.time(),
            "expires_at": time.time() + 1800,
            "actual_n": actual_n,
            "padded_n": padded_n,
            "level_count": level_count,
            "key_pairs": key_pairs,
        }

        return {
            "session_id": session_id,
            "group_id": group_id,
            "N": actual_n,
            "padded_N": padded_n,
            "l": level_count,
            # Only return real book masked keys. Dummy padding is internal.
            "masked_keys": [b64_encode(x) for x in masked_keys[:actual_n]],
            "privacy_note": "Server has not received choice_index, bit path, or selected book index.",
        }

    def perform_ot_step(self, session_id: str, level: int, h0: int, h1: int) -> dict[str, Any]:
        cached = OT_SESSION_CACHE.get(session_id)
        if not cached:
            raise ValueError("OT session not found or already cleared")

        if time.time() > cached["expires_at"]:
            OT_SESSION_CACHE.pop(session_id, None)
            raise ValueError("OT session expired")

        if level < 0 or level >= cached["level_count"]:
            raise ValueError("Invalid OT level")

        m0, m1 = cached["key_pairs"][level]
        c0, c1, gy = OTChannel().sender_step2(m0, m1, h0, h1)

        return {
            "session_id": session_id,
            "level": level,
            "c0": b64_encode(c0),
            "c1": b64_encode(c1),
            "gy": gy,
        }

    def clear_session(self, session_id: str) -> dict[str, str]:
        OT_SESSION_CACHE.pop(session_id, None)
        return {"message": "OT session cache cleared"}
