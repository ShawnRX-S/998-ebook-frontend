"""Book storage for the API prototype.

For this runnable coursework version, encrypted books and AES keys are prepared
in memory at server startup from files in storage/source_books.

Important privacy design:
- API exposes a public index inside a group.
- API never needs an internal book_id for OT.
- Download endpoint returns a whole encrypted group package, not a single book,
  so the request itself does not reveal the chosen index.
"""

import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_BOOK_DIR = PROJECT_ROOT / "storage" / "source_books"


def b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def b64_decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


@dataclass
class EncryptedBookRecord:
    index: int
    filename: str
    title: str
    author: str
    nonce: bytes
    ciphertext: bytes
    tag: bytes
    aes_key: bytes


class BookStorageService:
    """Load books, encrypt them with AES-GCM, and expose group-level data."""

    def __init__(self, group_id: str = "default"):
        self.group_id = group_id
        self.groups: dict[str, list[EncryptedBookRecord]] = {}
        self._ensure_demo_books_exist()
        self._load_default_group()

    def _ensure_demo_books_exist(self) -> None:
        SOURCE_BOOK_DIR.mkdir(parents=True, exist_ok=True)
        existing = list(SOURCE_BOOK_DIR.glob("*"))
        if existing:
            return

        demo_books = {
            "privacy_by_design.txt": "Privacy by Design demo ebook content.\n",
            "ot_for_ebook_platform.txt": "Oblivious Transfer for Ebook Platform demo ebook content.\n",
            "secure_download_demo.txt": "Secure Download Demo ebook content.\n",
            "private_catalog_example.txt": "Private Catalog Example ebook content.\n",
        }
        for filename, content in demo_books.items():
            (SOURCE_BOOK_DIR / filename).write_text(content, encoding="utf-8")

    def _load_default_group(self) -> None:
        records: list[EncryptedBookRecord] = []
        files = sorted(
            p for p in SOURCE_BOOK_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in {".pdf", ".txt", ".epub"}
        )
        if not files:
            raise RuntimeError(f"No source books found in {SOURCE_BOOK_DIR}")

        for idx, path in enumerate(files):
            data = path.read_bytes()
            aes_key = AESGCM.generate_key(bit_length=256)
            aesgcm = AESGCM(aes_key)
            nonce = os.urandom(12)
            encrypted = aesgcm.encrypt(nonce, data, None)
            ciphertext, tag = encrypted[:-16], encrypted[-16:]

            title = path.stem.replace("_", " ").title()
            records.append(
                EncryptedBookRecord(
                    index=idx,
                    filename=path.name,
                    title=title,
                    author="Demo Author",
                    nonce=nonce,
                    ciphertext=ciphertext,
                    tag=tag,
                    aes_key=aes_key,
                )
            )

        self.groups[self.group_id] = records

    def get_public_catalog(self, group_id: str = "default") -> dict[str, Any]:
        records = self._get_group(group_id)
        return {
            "group_id": group_id,
            "N": len(records),
            "books": [
                {
                    "index": r.index,
                    "title": r.title,
                    "author": r.author,
                    "filename": r.filename,
                }
                for r in records
            ],
            "privacy_note": "Use index only on the client side. Do not send choice_index to the server.",
        }

    def get_book_keys_for_group(self, group_id: str = "default") -> list[bytes]:
        return [r.aes_key for r in self._get_group(group_id)]

    def get_encrypted_group_package(self, group_id: str = "default") -> dict[str, Any]:
        records = self._get_group(group_id)
        return {
            "group_id": group_id,
            "N": len(records),
            "books": [
                {
                    "index": r.index,
                    "filename": r.filename,
                    "title": r.title,
                    "nonce": b64_encode(r.nonce),
                    "ciphertext": b64_encode(r.ciphertext),
                    "tag": b64_encode(r.tag),
                }
                for r in records
            ],
        }

    def _get_group(self, group_id: str) -> list[EncryptedBookRecord]:
        if group_id not in self.groups:
            raise ValueError(f"Unknown group_id: {group_id}")
        return self.groups[group_id]
