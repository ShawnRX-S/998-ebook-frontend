# server/book_storage_db_service.py

import base64
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "bookstore.db"


def b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


class BookStorageDBService:
    """
    DB-backed replacement for BookStorageService.

    It keeps the old OT API contract:
    - get_public_catalog(group_id)
    - get_book_keys_for_group(group_id)
    - get_encrypted_group_package(group_id)

    Privacy rule:
    - Use group_id + book_index
    - Do not use order_items(book_id)
    - Do not receive choice_index
    """

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = str(db_path)

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_public_catalog(self, group_id: str = "default") -> dict[str, Any]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT
                    book_index,
                    title,
                    author,
                    filename
                FROM books
                WHERE group_id = ?
                  AND is_active = 1
                ORDER BY book_index ASC
                """,
                (group_id,),
            ).fetchall()

            if not rows:
                raise ValueError(f"No books found for group_id: {group_id}")

            return {
                "group_id": group_id,
                "N": len(rows),
                "books": [
                    {
                        "index": row["book_index"],
                        "title": row["title"],
                        "author": row["author"],
                        "filename": row["filename"],
                    }
                    for row in rows
                ],
                "privacy_note": "Use index only on the client side. Do not send choice_index to the server.",
            }

        finally:
            conn.close()

    def get_book_keys_for_group(self, group_id: str = "default") -> list[bytes]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT
                    book_index,
                    aes_key
                FROM book_keys
                WHERE group_id = ?
                ORDER BY book_index ASC
                """,
                (group_id,),
            ).fetchall()

            if not rows:
                raise ValueError(f"No AES keys found for group_id: {group_id}")

            keys = [row["aes_key"] for row in rows]

            if any(len(k) != len(keys[0]) for k in keys):
                raise ValueError("All AES keys must have the same length")

            return keys

        finally:
            conn.close()

    def get_encrypted_group_package(self, group_id: str = "default") -> dict[str, Any]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT
                    b.book_index,
                    b.filename,
                    b.title,
                    e.nonce,
                    e.ciphertext,
                    e.tag
                FROM books b
                JOIN encrypted_books e
                  ON b.group_id = e.group_id
                 AND b.book_index = e.book_index
                WHERE b.group_id = ?
                  AND b.is_active = 1
                ORDER BY b.book_index ASC
                """,
                (group_id,),
            ).fetchall()

            if not rows:
                raise ValueError(f"No encrypted books found for group_id: {group_id}")

            return {
                "group_id": group_id,
                "N": len(rows),
                "books": [
                    {
                        "index": row["book_index"],
                        "filename": row["filename"],
                        "title": row["title"],
                        "nonce": b64_encode(row["nonce"]),
                        "ciphertext": b64_encode(row["ciphertext"]),
                        "tag": b64_encode(row["tag"]),
                    }
                    for row in rows
                ],
            }

        finally:
            conn.close()